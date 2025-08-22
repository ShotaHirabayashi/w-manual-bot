#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django management command: RAG用データをベクトル化してChromaDBに保存

使い方:
    python manage.py load_qa_data docs/rag-text.txt --doc-title "フロントFAQ"
    python manage.py load_qa_data docs/rag-text.txt --type qa --update-existing
"""
import argparse
import re
import json
from datetime import datetime
from typing import List, Dict
from django.core.management.base import BaseCommand
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from django.conf import settings

SEP_PATTERN = re.compile(r"^\s*={3,}\s*$", re.MULTILINE)

class Command(BaseCommand):
    help = 'Load QA data into ChromaDB from text file'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str, help='Input text file path')
        parser.add_argument('--doc-title', default='フロントFAQ', help='Document title for metadata')
        parser.add_argument('--type', default='qa', help='Document type (qa, guideline, etc.)')
        parser.add_argument('--id-prefix', default='qa', help='ID prefix for documents')
        parser.add_argument('--start-id', type=int, default=1, help='Starting ID number')
        parser.add_argument('--update-existing', action='store_true', help='Update existing documents')
        parser.add_argument('--clear-db', action='store_true', help='Clear existing database before loading')

    def handle(self, *args, **options):
        input_file = options['input_file']
        doc_title = options['doc_title']
        doc_type = options['type']
        id_prefix = options['id_prefix']
        start_id = options['start_id']
        update_existing = options['update_existing']
        clear_db = options['clear_db']

        self.stdout.write(f"Loading data from: {input_file}")
        self.stdout.write(f"Document title: {doc_title}")
        self.stdout.write(f"Document type: {doc_type}")

        try:
            # ファイル読み込み
            with open(input_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # QAデータに変換
            records = self.to_records(text, doc_title, doc_type, id_prefix, start_id)
            self.stdout.write(f"Converted {len(records)} records")

            # ChromaDBに保存
            self.save_to_chromadb(records, update_existing, clear_db)
            
            self.stdout.write(self.style.SUCCESS(f"Successfully loaded {len(records)} records into ChromaDB"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {input_file}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

    def split_blocks(self, text: str) -> List[str]:
        """テキストを=====区切りでブロック分割"""
        parts = re.split(SEP_PATTERN, text)
        return [p.strip() for p in parts if p.strip()]

    def qa_from_block(self, block: str) -> tuple:
        """ブロックから質問と回答を抽出"""
        lines = block.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        
        # 先頭・末尾の空行を除去
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            return None, None
        
        q = lines[0].strip()
        a_lines = lines[1:]
        
        # 先頭に空行が1つ入っているケースに対応
        while a_lines and not a_lines[0].strip():
            a_lines.pop(0)
        
        a = "\n".join(a_lines).strip()
        return q, a

    def to_records(self, text: str, doc_title: str, rec_type: str, id_prefix: str, start: int) -> List[Dict]:
        """テキストをレコードのリストに変換"""
        blocks = self.split_blocks(text)
        records = []
        n = start
        today = datetime.now().strftime("%Y-%m-%d")
        
        for block in blocks:
            q, a = self.qa_from_block(block)
            if not q and not a:
                continue
            
            # 回答が空なら空文字として出力
            a = a if a is not None else ""
            
            # 質問と回答を結合してコンテンツとする
            if a:
                content = f"質問: {q}\n\n回答: {a}"
            else:
                content = f"質問: {q}"
            
            rec = {
                "id": f"{id_prefix}.{n:04d}",
                "type": rec_type,
                "doc_title": doc_title,
                "question": q,
                "answer": a,
                "content": content,
                "updated_at": today,
                "source": f"{doc_title} - {id_prefix}.{n:04d}"
            }
            records.append(rec)
            n += 1
            
        return records

    def save_to_chromadb(self, records: List[Dict], update_existing: bool, clear_db: bool):
        """ChromaDBにレコードを保存"""
        # OpenAI embeddings初期化
        embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        
        # ChromaDB初期化
        db = Chroma(
            collection_name='wdb',
            persist_directory="./wdb",
            embedding_function=embeddings
        )
        
        # 既存データをクリア
        if clear_db:
            self.stdout.write("Clearing existing database...")
            try:
                db.delete_collection()
                db = Chroma(
                    collection_name='wdb',
                    persist_directory="./wdb",
                    embedding_function=embeddings
                )
                self.stdout.write("Database cleared")
            except Exception as e:
                self.stdout.write(f"Warning: Could not clear database: {e}")
        
        # ドキュメント作成
        documents = []
        metadatas = []
        ids = []
        
        for record in records:
            # 既存チェック（update_existingがFalseの場合）
            if not update_existing:
                try:
                    existing = db.get(ids=[record['id']])
                    if existing['ids']:
                        self.stdout.write(f"Skipping existing document: {record['id']}")
                        continue
                except:
                    pass  # 存在チェックでエラーが出ても継続
            
            documents.append(Document(
                page_content=record['content'],
                metadata={
                    'id': record['id'],
                    'type': record['type'],
                    'doc_title': record['doc_title'],
                    'question': record['question'],
                    'answer': record['answer'],
                    'updated_at': record['updated_at'],
                    'source': record['source']
                }
            ))
            metadatas.append({
                'id': record['id'],
                'type': record['type'],
                'doc_title': record['doc_title'],
                'question': record['question'],
                'answer': record['answer'],
                'updated_at': record['updated_at'],
                'source': record['source']
            })
            ids.append(record['id'])
        
        if not documents:
            self.stdout.write("No documents to add")
            return
        
        # バッチでデータベースに追加
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            try:
                # 既存の場合は削除してから追加（更新）
                if update_existing:
                    try:
                        db.delete(ids=batch_ids)
                    except:
                        pass  # 削除エラーは無視
                
                db.add_documents(
                    documents=batch_docs,
                    ids=batch_ids
                )
                
                self.stdout.write(f"Added batch {i//batch_size + 1}: {len(batch_docs)} documents")
                
            except Exception as e:
                self.stdout.write(f"Error adding batch {i//batch_size + 1}: {e}")
                continue
        
        self.stdout.write(f"Successfully processed {len(documents)} documents")