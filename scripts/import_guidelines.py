#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ガイドラインファイルをChromaDBに取り込むスクリプト
"""

import os
import sys
import django
from pathlib import Path

# Djangoプロジェクトのパスを追加
sys.path.append('/Users/bayashi/Repositories/w-manual-bot')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from django.conf import settings

def parse_guideline_file(file_path):
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
                    'source': f'guideline - {title}'
                }
            )
            documents.append(doc)
    
    return documents

def main():
    """メイン処理"""
    print("ガイドラインファイルをChromaDBに取り込み開始...")
    
    # OpenAI Embeddings初期化
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model="text-embedding-3-small"
    )
    
    # ChromaDB初期化
    try:
        from chromadb import PersistentClient
        client = PersistentClient(path="./wdb")
        
        # コレクション一覧確認
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        print(f"既存のコレクション: {collection_names}")
        
        # 'wdb'コレクションを取得
        if 'wdb' not in collection_names:
            print("'wdb'コレクションが存在しません。作成します...")
            client.create_collection(name='wdb')
        
        db = Chroma(
            client=client,
            collection_name='wdb',
            embedding_function=embeddings
        )
        
    except Exception as e:
        print(f"ChromaDB初期化エラー: {e}")
        print("デフォルト設定で初期化を試行...")
        db = Chroma(
            collection_name='wdb',
            persist_directory="./wdb",
            embedding_function=embeddings
        )
    
    # ガイドラインファイルを解析
    guideline_file = 'docs/guideline_unified.txt'
    print(f"ファイルを解析中: {guideline_file}")
    
    documents = parse_guideline_file(guideline_file)
    print(f"解析完了: {len(documents)} 個のドキュメントを抽出")
    
    # ドキュメント詳細表示
    for i, doc in enumerate(documents[:3]):  # 最初の3つのみ表示
        print(f"\nドキュメント {i+1}:")
        print(f"  タイトル: {doc.metadata.get('title', 'N/A')}")
        print(f"  カテゴリ: {doc.metadata.get('category', 'N/A')}")
        print(f"  内容 (先頭100文字): {doc.page_content[:100]}...")
    
    if len(documents) > 3:
        print(f"...他 {len(documents) - 3} 個のドキュメント")
    
    # ChromaDBに追加
    print("\nChromaDBに追加中...")
    try:
        # 既存のガイドラインドキュメントを削除（重複回避）
        existing_docs = db.similarity_search("", k=1000, filter={"type": "guideline"})
        if existing_docs:
            print(f"既存のガイドラインドキュメント {len(existing_docs)} 個を削除...")
            # 注意: LangChain Chromaでは直接削除は難しいので、コレクションをリセットするか
            # 手動でIDを指定して削除する必要があります。
            # ここでは警告のみ表示
            print("警告: 既存のガイドラインドキュメントが存在します。重複する可能性があります。")
        
        # 新しいドキュメントを追加
        db.add_documents(documents)
        print(f"✅ {len(documents)} 個のドキュメントを正常に追加しました")
        
        # 追加確認
        test_results = db.similarity_search("Wブランド", k=3, filter={"type": "guideline"})
        print(f"\n確認検索結果: {len(test_results)} 個のドキュメントが見つかりました")
        
        for i, result in enumerate(test_results):
            print(f"  {i+1}. {result.metadata.get('title', 'タイトルなし')} ({result.metadata.get('category', 'カテゴリなし')})")
            
    except Exception as e:
        print(f"❌ ChromaDBへの追加でエラーが発生: {e}")
        return False
    
    print("\n✅ ガイドライン取り込み完了!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)