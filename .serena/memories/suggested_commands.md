# 推奨コマンド一覧

## 開発環境
```bash
# 仮想環境のアクティベート
source .venv/bin/activate

# 依存関係のインストール
pip install -r requirements.txt
```

## Django管理コマンド
```bash
# 開発サーバーの起動
python manage.py runserver

# マイグレーション作成
python manage.py makemigrations

# マイグレーション適用
python manage.py migrate

# スーパーユーザー作成（カスタムコマンド）
python manage.py superuser

# 静的ファイル収集（本番用）
python manage.py collectstatic

# Q&Aデータのロード
python manage.py load_qa_data docs/rag-text.txt --doc-title "フロントマニュアル" --type qa --clear-db

# Djangoシェル
python manage.py shell

# データベースの確認
python manage.py dbshell
```

## テスト
```bash
# テスト実行
python manage.py test

# 特定アプリのテスト
python manage.py test accounts
python manage.py test line
python manage.py test chat_ui
```

## Git操作（macOS）
```bash
git status
git add .
git commit -m "メッセージ"
git push origin main
git pull origin main
```

## システムコマンド（macOS/Darwin）
```bash
ls -la  # ファイル一覧
find . -name "*.py"  # Pythonファイル検索
grep -r "検索文字列" .  # 文字列検索
```

## 注意事項
- フォーマッター/リンターの設定なし
- 必要に応じてBlack, ruff, flake8等の導入を検討