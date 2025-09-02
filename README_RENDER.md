# Render デプロイガイド（PostgreSQL版）

## デプロイ手順

### 1. 初回デプロイ

1. GitHubにコードをプッシュ
```bash
git add .
git commit -m "Add Render deployment configuration with SQLite"
git push origin main
```

2. Renderにログインして新しいプロジェクトを作成
   - https://render.com にアクセス
   - "New +" → "Web Service" を選択
   - GitHubリポジトリを接続

3. 環境変数を設定（Render Dashboard → Environment）
   - `CHANNEL_ACCESS_TOKEN`: LINE Botのチャンネルアクセストークン
   - `CHANNEL_SECRET`: LINE Botのチャンネルシークレット
   - `LIFF_ID`: LINE Front-end Framework ID
   - `OPENAI_API_KEY`: OpenAI APIキー
   - `SUPERUSER_NAME`: 管理者ユーザー名
   - `SUPERUSER_EMAIL`: 管理者メールアドレス
   - `SUPERUSER_PASSWORD`: 管理者パスワード

4. デプロイを開始

### 2. データベース設定

**重要**: デプロイ後、Render Shellから手動でマイグレーションを実行する必要があります。

1. Render Dashboardにアクセス
2. "Shell" タブを開く
3. 以下のコマンドを実行：

```bash
./migrate_manual.sh
```

または個別に実行：

```bash
# マイグレーション実行
python manage.py migrate

# スーパーユーザー作成
python manage.py createsuperuser
```

### 3. トラブルシューティング

#### マイグレーションを手動で実行する場合

Render Shellから：
```bash
python manage.py migrate
```

#### スーパーユーザーを手動で作成する場合

Render Shellから：
```bash
python manage.py createsuperuser
```

#### データベースをリセットする場合

Render Shellから：
```bash
rm /opt/render/project/data/db.sqlite3
python manage.py migrate
```

## ファイル構成

- `render.yaml`: Renderのサービス設定（永続ディスク付き）
- `build.sh`: ビルド時に実行されるスクリプト
- `runtime.txt`: Pythonバージョン指定
- `.env.example`: 環境変数のテンプレート

## 注意事項

- **重要**: PostgreSQLデータベースは無料プランで90日間保持されます
- 初回デプロイ後は必ず手動でマイグレーションを実行してください
- 無料プランではスリープ機能があるため、15分間アクセスがないとサービスが停止します
- 再起動には数十秒かかることがあります
- データベース接続の準備ができるまで時間がかかる場合があります