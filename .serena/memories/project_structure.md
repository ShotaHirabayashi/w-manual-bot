# プロジェクト構造

```
w-manual-bot/
├── .venv/              # Python仮想環境
├── .claude/            # Claude関連ファイル（一時ファイル、プロンプト等）
│   └── tmp/           # Claude一時ファイル保存先
├── config/             # Django設定
│   ├── settings.py    # Django設定ファイル
│   ├── urls.py        # ルートURLconf
│   └── wsgi.py        # WSGI設定
├── accounts/           # ユーザー管理アプリ
│   ├── models.py      # カスタムユーザーモデル (UserAccount)
│   ├── views.py       # ビュー
│   ├── migrations/    # データベースマイグレーション
│   └── tests.py       # テスト（未実装）
├── line/               # LINE Bot統合アプリ
│   ├── models.py      # モデル
│   ├── views.py       # LINE Bot Webhookハンドラー
│   ├── open_ai_views.py # OpenAI統合
│   ├── send_slack.py  # Slack送信機能
│   ├── line_messages.py # LINEメッセージ処理
│   ├── management/    
│   │   └── commands/
│   │       └── superuser.py # スーパーユーザー作成コマンド
│   └── templates/     # テンプレート
├── chat_ui/            # Webチャットインターフェース
│   ├── models.py      # モデル
│   ├── views.py       # ビュー
│   ├── management/
│   │   └── commands/
│   │       └── load_qa_data.py # Q&Aデータロードコマンド
│   └── templates/     # HTMLテンプレート
├── common/             # 共通モジュール
├── docs/               # ドキュメント
├── static/             # 静的ファイル（CSS, JS, 画像）
├── wdb/                # ChromaDB関連データ
│   └── chroma.sqlite3 # ChromaDBデータベース
├── manage.py           # Django管理スクリプト
├── requirements.txt    # Python依存関係
├── README.md          # プロジェクトREADME
├── CLAUDE.md          # Claude使用ガイドライン
└── .gitignore         # Git除外設定
```

## 主要ディレクトリの役割
- **config/**: Django全体の設定とURLルーティング
- **accounts/**: ユーザー認証と管理
- **line/**: LINE Bot機能とOpenAI統合
- **chat_ui/**: Web UIとRAGシステム
- **wdb/**: ベクトルデータベース（ChromaDB）のストレージ
- **.claude/**: Claude Code関連の作業ファイル