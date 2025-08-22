# W-Manual-Bot プロジェクト概要

## プロジェクトの目的
LINE BotとSlack Bot統合を備えたAIチャットボット/マニュアルボットシステム。
OpenAI APIとRAG（Retrieval-Augmented Generation）を使用して、文書ベースのQ&A機能を提供。

## 主な機能
- LINE Bot統合によるチャットインターフェース
- Slack Bot統合
- OpenAI APIを使用したAI応答生成
- ChromaDBを使用したベクトル検索
- RAGシステムによる文書ベースのQ&A
- Webベースの管理UIとチャットインターフェース

## テクノロジースタック
- **Framework**: Django 5.0.4
- **認証**: django-allauth
- **AI/ML**: 
  - langchain, langchain-openai, langchain-chroma
  - sentence-transformers (埋め込み生成)
  - OpenAI API
- **Bot統合**: 
  - line-bot-sdk (LINE Bot)
  - Slack Bot API
- **データベース**: PostgreSQL (psycopg2)
- **検索**: ChromaDB (ベクトルDB), rank-bm25
- **日本語処理**: mecab-python3, fugashi, unidic-lite
- **デプロイ**: gunicorn, whitenoise

## 環境変数
- SECRET_KEY: Django シークレットキー
- OPENAI_API_KEY: OpenAI API キー
- CHANNEL_ACCESS_TOKEN: LINE Bot アクセストークン
- CHANNEL_SECRET: LINE Bot チャンネルシークレット
- SLACK_BOT_TOKEN: Slack Bot トークン
- LIFF_ID: LINE Front-end Framework ID
- DATABASE_URL: データベース接続URL