# -*- coding: utf-8 -*-
"""
ガイドラインファイルをChromaDBに取り込むDjango管理コマンド
"""

from django.core.management.base import BaseCommand
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from django.conf import settings
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'ガイドラインファイルをChromaDBに取り込む'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='docs/guideline_unified.txt',
            help='取り込むガイドラインファイルのパス（デフォルト: docs/guideline_unified.txt）'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='既存のガイドラインドキュメントを削除してから追加'
        )

    def handle(self, *args, **options):
        self.stdout.write("ガイドラインファイルをChromaDBに取り込み開始...")
        
        # ファイル存在確認
        file_path = options['file']
        if not os.path.exists(file_path):
            self.stderr.write(f"ファイルが見つかりません: {file_path}")
            return
        
        # OpenAI Embeddings初期化
        try:
            embeddings = OpenAIEmbeddings(
                api_key=settings.OPENAI_API_KEY,
                model="text-embedding-3-small"
            )
        except Exception as e:
            self.stderr.write(f"OpenAI Embeddings初期化エラー: {e}")
            return
        
        # ChromaDB初期化
        try:
            from chromadb import PersistentClient
            client = PersistentClient(path="./wdb")
            
            # コレクション一覧確認
            collections = client.list_collections()
            collection_names = [c.name for c in collections]
            self.stdout.write(f"既存のコレクション: {collection_names}")
            
            # 'wdb'コレクションを取得
            if 'wdb' not in collection_names:
                self.stdout.write("'wdb'コレクションが存在しません。作成します...")
                client.create_collection(name='wdb')
            
            db = Chroma(
                client=client,
                collection_name='wdb',
                embedding_function=embeddings
            )
            
        except Exception as e:
            self.stderr.write(f"ChromaDB初期化エラー: {e}")
            self.stdout.write("デフォルト設定で初期化を試行...")
            try:
                db = Chroma(
                    collection_name='wdb',
                    persist_directory="./wdb",
                    embedding_function=embeddings
                )
            except Exception as e2:
                self.stderr.write(f"デフォルト初期化も失敗: {e2}")
                return
        
        # ガイドラインファイルを解析
        self.stdout.write(f"ファイルを解析中: {file_path}")
        documents = self.parse_guideline_file(file_path)
        self.stdout.write(f"解析完了: {len(documents)} 個のドキュメントを抽出")
        
        if not documents:
            self.stderr.write("ドキュメントが抽出されませんでした")
            return
        
        # ドキュメント詳細表示
        for i, doc in enumerate(documents[:3]):  # 最初の3つのみ表示
            self.stdout.write(f"ドキュメント {i+1}:")
            self.stdout.write(f"  タイトル: {doc.metadata.get('title', 'N/A')}")
            self.stdout.write(f"  カテゴリ: {doc.metadata.get('category', 'N/A')}")
            self.stdout.write(f"  内容 (先頭100文字): {doc.page_content[:100]}...")
        
        if len(documents) > 3:
            self.stdout.write(f"...他 {len(documents) - 3} 個のドキュメント")
        
        # 既存のガイドラインドキュメント処理
        if options['clear']:
            self.stdout.write("既存のガイドラインドキュメント削除処理をスキップ（現在未実装）")
        else:
            try:
                existing_docs = db.similarity_search("", k=1000, filter={"type": "guideline"})
                if existing_docs:
                    self.stdout.write(
                        self.style.WARNING(
                            f"警告: 既存のガイドラインドキュメント {len(existing_docs)} 個が存在します。"
                            "重複する可能性があります。--clear オプションを使用してください。"
                        )
                    )
            except Exception as e:
                self.stdout.write(f"既存ドキュメント確認でエラー: {e}")
        
        # ChromaDBに追加
        self.stdout.write("ChromaDBに追加中...")
        try:
            db.add_documents(documents)
            self.stdout.write(
                self.style.SUCCESS(f"✅ {len(documents)} 個のドキュメントを正常に追加しました")
            )
            
            # 追加確認
            test_results = db.similarity_search("Wブランド", k=3, filter={"type": "guideline"})
            self.stdout.write(f"確認検索結果: {len(test_results)} 個のドキュメントが見つかりました")
            
            for i, result in enumerate(test_results):
                title = result.metadata.get('title', 'タイトルなし')
                category = result.metadata.get('category', 'カテゴリなし')
                self.stdout.write(f"  {i+1}. {title} ({category})")
                
        except Exception as e:
            self.stderr.write(f"❌ ChromaDBへの追加でエラーが発生: {e}")
            return
        
        self.stdout.write(self.style.SUCCESS("✅ ガイドライン取り込み完了!"))

    def parse_guideline_file(self, file_path):
        """統一形式のガイドラインファイルを解析してドキュメントリストを返す"""
        documents = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # '---'で分割
        sections = content.split('---\n')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            lines = section.split('\n')
            title = ""
            category = ""
            content_lines = []
            
            for line in lines:
                if line.startswith('タイトル: '):
                    title = line.replace('タイトル: ', '').strip()
                elif line.startswith('カテゴリ: '):
                    category = line.replace('カテゴリ: ', '').strip()
                elif line.startswith('内容: '):
                    content_lines.append(line.replace('内容: ', '').strip())
                elif content_lines:  # 内容の続き
                    content_lines.append(line.strip())
            
            if title and category and content_lines:
                content_text = '\n'.join(content_lines)
                
                doc = Document(
                    page_content=content_text,
                    metadata={
                        'title': title,
                        'type': 'guideline',
                        'category': category,
                        'source': f'ガイドライン - {title}'
                    }
                )
                documents.append(doc)
        
        return documents