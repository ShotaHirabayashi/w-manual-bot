# ローカル開発環境セットアップガイド

このガイドでは、Django transcription アプリケーションをローカル環境で動作させるための手順を説明します。

## 前提条件

- Python 3.8以上
- pip (Python package installer)
- Git

## セットアップ手順

### 1. 仮想環境の作成と有効化

```bash
# 仮想環境作成
python3 -m venv .venv

# 仮想環境の有効化
source .venv/bin/activate
```

### 2. 依存関係のインストール

```bash
# 開発用パッケージのインストール
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
# ローカル開発用の環境変数ファイルをコピー
cp .env.local.example .env
```

### 4. データベース設定（オプション選択）

#### オプション 1: SQLite使用（推奨・最も簡単）

`.env` ファイルは何も変更する必要がありません。デフォルトでSQLiteが使用されます。

#### オプション 2: ローカルPostgreSQL使用

1. PostgreSQLをインストール（macOS）:
```bash
brew install postgresql
brew services start postgresql
```

2. データベースとユーザーを作成:
```bash
# PostgreSQLに接続
psql postgres

# データベース作成
CREATE DATABASE w_transcript_local;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE w_transcript_local TO postgres;
\q
```

3. `.env` ファイルで以下をアンコメント:
```bash
USE_LOCAL_POSTGRES=true
LOCAL_DB_NAME=w_transcript_local
LOCAL_DB_USER=postgres
LOCAL_DB_PASSWORD=postgres
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=5432
```

### 5. マイグレーション実行

```bash
# データベーステーブル作成
python manage.py migrate

# 管理者ユーザー作成（オプション）
python manage.py createsuperuser
```

### 6. 開発サーバーの起動

```bash
# 開発サーバー起動
python manage.py runserver
```

アプリケーションは http://127.0.0.1:8000 でアクセス可能になります。

## 設定の詳細

### データベース設定の仕組み

`config/settings.py` では以下の優先順位でデータベース設定が決定されます：

1. **DATABASE_URL** - 本番環境用（Cloud Run）
2. **CLOUD_SQL_CONNECTION_NAME** - Cloud SQL用設定
3. **USE_LOCAL_POSTGRES=true** - ローカルPostgreSQL
4. **デフォルト** - SQLite（最も簡単）

### ストレージ設定

ローカル開発では：
- `USE_CLOUD_STORAGE=false` (デフォルト)
- メディアファイルは `media/` ディレクトリに保存
- 静的ファイルは `static/` ディレクトリから配信

### TailwindCSS開発

スタイリングの変更を行う場合：

```bash
# 別ターミナルでTailwind監視モード起動
python manage.py tailwind start
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. `python manage.py runserver` でエラーが出る場合

```bash
# 環境変数を確認
python -c "import os; print('DEBUG:', os.getenv('DEBUG')); print('SECRET_KEY set:', bool(os.getenv('SECRET_KEY')))"

# データベース設定を確認
python manage.py dbshell --version
```

#### 2. SQLite接続エラー

```bash
# データベースファイルの権限を確認
ls -la db.sqlite3

# 必要に応じてマイグレーションを再実行
rm db.sqlite3
python manage.py migrate
```

#### 3. PostgreSQL接続エラー

```bash
# PostgreSQLサービスの状態確認
brew services list | grep postgresql

# 接続テスト
psql -h localhost -U postgres -d w_transcript_local
```

#### 4. 静的ファイルが表示されない

```bash
# 静的ファイルを収集
python manage.py collectstatic

# TailwindCSS設定を確認
python manage.py tailwind build
```

## 開発用機能

### デバッグツールバー

`.env` で以下を設定することでデバッグツールバーを有効化できます：

```bash
DEBUG=true
ENABLE_DEBUG_TOOLBAR=true
```

### 開発用API設定

複数アプリの連携テストを行う場合：

```bash
# 各アプリのローカルURL設定
APP1_API_URL=http://localhost:8080
APP2_API_URL=http://localhost:8081
APP3_API_URL=http://localhost:8082
```

## 本番デプロイとの違い

| 項目 | ローカル開発 | 本番環境（Cloud Run） |
|------|-------------|-------------------|
| データベース | SQLite/ローカルPostgreSQL | Cloud SQL |
| ストレージ | ローカルファイル | Google Cloud Storage |
| 認証 | 開発用シークレット | Workload Identity |
| SSL | HTTP | HTTPS（強制） |
| 静的ファイル | Django開発サーバー | WhiteNoise |

## 次のステップ

ローカル開発環境が正常に動作することを確認できたら：

1. Cloud Run用のコンテナ設定を確認
2. 本番環境用の環境変数を設定
3. デプロイスクリプトを実行

詳細は各デプロイメントガイドを参照してください。