# コーディングスタイルと規約

## Pythonコーディングスタイル
- **docstring**: Google-style docstringsを使用（日本語でのドキュメントも含む）
- **型ヒント**: 部分的に使用（完全ではない）
- **命名規則**: 
  - クラス: PascalCase (例: UserAccount, UserManager)
  - 関数/メソッド: snake_case (例: open_ai_chat, generate_random_user_uid)
  - 定数: UPPER_SNAKE_CASE (例: SECRET_KEY, CHANNEL_ACCESS_TOKEN)
- **インデント**: スペース4つ
- **行の長さ**: 明確な規約なし（88文字推奨 - Black標準）

## Djangoアプリ構造
- カスタムユーザーモデル使用 (accounts.UserAccount)
- django-allauthによる認証
- アプリごとにmodels, views, urls, forms, admin, testsファイルを配置
- 管理コマンドはmanagement/commands/ディレクトリに配置

## ファイル編成
- **設定**: config/ディレクトリ（settings.py, urls.py, wsgi.py）
- **アプリ**: 各機能ごとに分離
  - accounts: ユーザー管理
  - line: LINE Bot統合
  - chat_ui: Webチャットインターフェース
- **静的ファイル**: static/ディレクトリ
- **テンプレート**: 各アプリ内のtemplates/ディレクトリ

## セキュリティ
- 環境変数による機密情報管理（django-environ使用）
- CSRF保護有効
- django-allauthによる認証フロー

## 特記事項
- フォーマッター/リンターの設定ファイルなし
- テストファイルは存在するが実装されていない
- Claudeの一時ファイルは.claude/tmp/に保存