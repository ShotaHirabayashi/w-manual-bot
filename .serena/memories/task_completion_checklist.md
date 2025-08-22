# タスク完了時のチェックリスト

## コード変更後の確認事項

### 1. Django固有の確認
- [ ] マイグレーションが必要か確認
  ```bash
  python manage.py makemigrations --check --dry-run
  ```
- [ ] 必要に応じてマイグレーション作成と適用
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### 2. 構文とインポートの確認
- [ ] Pythonファイルの構文エラーチェック
  ```bash
  python -m py_compile <file.py>
  ```
- [ ] 未使用のインポートを削除
- [ ] 必要なインポートがすべて含まれているか確認

### 3. テスト実行
- [ ] 変更したアプリのテスト実行
  ```bash
  python manage.py test <app_name>
  ```
- [ ] 全体テスト実行（必要に応じて）
  ```bash
  python manage.py test
  ```

### 4. 開発サーバーでの動作確認
- [ ] runserverでエラーなく起動するか
  ```bash
  python manage.py runserver
  ```
- [ ] 関連するエンドポイントが正常に動作するか

### 5. セキュリティチェック
- [ ] 機密情報がコードに含まれていないか
- [ ] 環境変数で管理すべき値がハードコードされていないか
- [ ] SQL インジェクション対策（Django ORM使用）
- [ ] XSS/CSRF対策が適切か

### 6. コードスタイル
- [ ] Googleスタイルのdocstring追加（新規関数/クラス）
- [ ] snake_case命名規則の遵守
- [ ] 適切なコメント追加

### 7. Git確認
- [ ] 不要なファイルが含まれていないか
- [ ] .gitignoreの確認

## 注意事項
- 現在、自動フォーマッター/リンターは設定されていない
- 必要に応じてBlack, ruff等の導入を検討
- Claudeの一時ファイルは.claude/tmp/に保存すること