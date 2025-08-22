# Claude Code Commands Memo

## claude --init
プロジェクトの初期化コマンド

```bash
claude --init
```

このコマンドは新しいプロジェクトでClaude Codeの設定を初期化します。

## /permission
権限関連のコマンド

```bash
/permission
```

現在の権限設定を確認・管理するためのコマンドです。

## モデル設定
```bash
/model
```

使用するモデルを設定するコマンド。現在は「Default (Opus 4.1 for up to 20% of usage limits, then use Sonnet 4)」に設定されています。

## MCP (Model Context Protocol) サーバー設定

### claude --mcp-config
MCPサーバーを使用してClaude Codeの機能を拡張するコマンド

```bash
claude --mcp-config=.mcp.json
```

MCPサーバーの設定ファイル（.mcp.json）を指定してClaude Codeを起動します。

### .mcp.json 設定例
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
```

### Playwright MCP サーバー
Microsoft製のブラウザ自動化MCPサーバー

**特徴:**
- Playwrightを使用した高速・軽量なブラウザ自動化
- LLMフレンドリーな構造化データでの操作
- 決定論的なツール実行

**要件:**
- Node.js 18以上
- VS Code、Cursor、Claude Desktopと互換性あり

**主要機能:**
- 要素のクリック
- ページナビゲーション
- テキスト入力
- スクリーンショット撮影
- ダイアログ処理
- JavaScript実行

**インストール:**
```bash
npx @playwright/mcp@latest
```

**使用方法:**
1. .mcp.jsonファイルにplaywright設定を記述
2. `claude --mcp-config=.mcp.json`でClaude Codeを起動
3. ブラウザ自動化ツールがClaude Code内で利用可能になる

## claudeコマンドのエイリアス設定

### zsh（現在のシェル）の場合
~/.zshrcファイルに以下を追加:

```bash
# claudeコマンドのエイリアス
alias cl='claude'
alias clm='claude --mcp-config=.mcp.json'
alias clr='claude --resume'
```

設定を反映:
```bash
source ~/.zshrc
```

### 使用例
```bash
# 通常のclaude起動
cl

# MCP設定付きで起動
clm

# その他のオプション付き
cl --init
```


### 要件定義

```markdown
to gen AI
今から、私の作った動画をUdemyのような講座プラットフォームを作ってユーザーに閲覧してもらいたいと考えています。課金機能は後で作成し、早めにMVPを完成させたいです。

まだ要件が詰め切れていないので僕にヒアリングをしてください
```

```markdown
to gen AI
Claude codeで開発したいので今までの要件定義をマークダウン形式で書き直してください
```

```markdown
to claude code(opusで実施）
このサービスを作るので、CLAUDE.mdファイルに記載をしてください、
```

```markdown
to claude code(opusで実施）
Vue.jsのベストプラクティスを遵守してほしいので、そのルールをCLAUDE.mdに記載してください
```


```markdown
to claude code (opusで実施）
それでは、CLAUDE.mdファイルに書き出した機能を/docsはいかに連番でマークダウンファイルでチケット分割してください
各ファイルにはtodoも管理します。終わったら[]を[*]と管理できるようにします。
```

デザインと要件定義はopusで実施し、コードはSonnetで実施する

```markdown
タスクが終わったところは
[]を[*]に変更して、docs/に記載してください
```


## 便利コマンド

```
/hooks
```
通知機能を実装できる
STOPが便利そう



```
/clear
```

```
/agents
code-reviewerを使ってコードのレビューをお願いします
```
エージェントの管理コマンド
会話中のコンテキストを汚すことなく、エージェントを走らせることができる



### serena MCP
https://github.com/oraios/serena

- このコマンドでは、コードの解析などをSerenaが実行し、Serenaを利用できる状態にします。
/mcp__serena__initial_instructions


プション	説明	使用例	適用場面
-q	高速モード（3-5思考ステップ）	/serena "ボタン修正" -q	簡単なバグ、小さな機能追加
-d	深層モード（10-15思考ステップ）	/serena "アーキテクチャ設計" -d	複雑なシステム、重要な設計決定
-c	コード重視の分析	/serena "パフォーマンス最適化" -c	コードレビュー、リファクタリング
-s	ステップバイステップ実装	/serena "ダッシュボード構築" -s	フル機能開発
-v	詳細出力（プロセス表示）	/serena "バグデバッグ" -v	学習、プロセス理解
-r	リサーチフェーズ含む	/serena "フレームワーク選択" -r	技術決定
-t	実装TODO作成	/serena "新機能" -t	プロジェクト管理


## 使用パターン別解説

### 1. 基本的な使用方法
```bash
# シンプルな問題解決
/serena "ログインバグ修正"

# 高速な機能実装
/serena "検索フィルター追加" -q

# コード最適化
/serena "読み込み時間改善" -c
```

### 2. 高度な使用方法
```bash
# 複雑なシステム設計（リサーチ付き）
/serena "マイクロサービスアーキテクチャ設計" -d -r -v

# フル機能開発（TODO作成付き）
/serena "チャート付きユーザーダッシュボード実装" -s -t -c

# 深層分析（ドキュメント付き）
/serena "新フレームワークへの移行" -d -r -v --focus=frontend
```

## 問題タイプ別の自動選択

Serenaは**キーワードベース**で最適な思考パターンを自動選択します：

### デバッグパターン（5-8思考ステップ）
**キーワード**: error, bug, issue, broken, failing
```bash
/serena "APIエラーが発生している"
# → 症状分析 → 環境確認 → 原因仮説 → 検証 → 解決策 → 実装 → 検証戦略 → 予防措置
```

### 設計パターン（8-12思考ステップ）
**キーワード**: architecture, system, structure, plan
```bash
/serena "ユーザー認証システム設計"
# → 要件整理 → 制約確認 → 選択肢生成 → 評価 → 技術選定 → 設計決定 → 実装フェーズ → リスク軽減
```

### 実装パターン（6-10思考ステップ）
**キーワード**: build, create, add, feature
```bash
/serena "リアルタイムチャット機能追加"
# → 仕様確認 → 技術選定 → 設計 → 依存関係 → 実装順序 → テスト戦略 → エラーハンドリング
```

### 最適化パターン（4-7思考ステップ）
**キーワード**: performance, slow, improve, refactor
```bash
/serena "データベースクエリ最適化"
# → 現状分析 → ボトルネック特定 → 改善機会 → 解決選択肢 → 優先度 → 実装影響評価
```


### context7
Context7 MCPは、AIが参照するドキュメントのコンテキストを調整し、常に最新の情報をAIに提供することを目的としたMCP (Model Context Protocol) サーバーです。
これにより、AIはより新しく、より正確な情報に基づいて回答を生成できるようになります。
古い情報や誤った情報に基づく手戻りを減らし、開発の効率化に繋がることが期待されます。

```markdown
React 19の新機能Suspenseの使い方を教えて。use context7
```