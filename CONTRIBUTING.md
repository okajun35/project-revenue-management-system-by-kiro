# Contributing to Project Revenue Management System

このプロジェクトへの貢献を歓迎します！以下のガイドラインに従って、効果的な貢献をお願いします。

## 🚀 クイックスタート

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/your-username/project-revenue-management-system.git
cd project-revenue-management-system

# 開発環境をセットアップ
make setup-dev

# デモ環境で動作確認
make demo
```

## 📋 貢献の種類

### 🐛 バグ報告
- GitHubのIssuesを使用してバグを報告してください
- 再現手順、期待される動作、実際の動作を明記してください
- 可能であれば、スクリーンショットやエラーログを添付してください

### ✨ 機能提案
- 新機能のアイデアがある場合は、まずIssueで議論してください
- 機能の目的、使用例、実装方法を説明してください

### 🔧 コード貢献
- フォークしてプルリクエストを作成してください
- コーディング規約に従ってください
- テストを追加してください

## 🧪 テスト

### テスト実行
```bash
# 全テスト実行
make test

# 機能別テスト
python -m pytest tests/unit/dashboard/ -v      # ダッシュボード
python -m pytest tests/integration/ -v        # 統合テスト
python -m pytest tests/frontend/ -v           # フロントエンド
```

### 新しいテストの追加
- 新機能には必ずテストを追加してください
- テスト構造ガイドライン（`.kiro/steering/test-structure-guidelines.md`）に従ってください
- テストファイルは適切なディレクトリに配置してください：
  - `tests/unit/` - 単体テスト
  - `tests/integration/` - 統合テスト
  - `tests/frontend/` - フロントエンドテスト

## 📝 コーディング規約

### Python
- PEP 8に準拠
- 型ヒントの使用を推奨
- docstringの記述
- 適切なエラーハンドリング

### JavaScript
- ES6+の使用
- jQueryとの互換性維持
- コメントの記述

### HTML/CSS
- セマンティックなHTML
- AdminLTEクラスの活用
- レスポンシブデザインの考慮

## 🏗️ アーキテクチャ

### ディレクトリ構造
```
app/
├── models.py           # データモデル
├── routes.py          # メインルート
├── *_routes.py        # 機能別ルート
├── services/          # ビジネスロジック
├── forms.py           # フォーム定義
└── templates/         # テンプレート

tests/
├── unit/              # 単体テスト
├── integration/       # 統合テスト
├── frontend/          # フロントエンドテスト
└── fixtures/          # テストデータ
```

### 設計原則
- MVCパターンの採用
- サービス層による業務ロジックの分離
- 包括的なバリデーション
- RESTful API設計

## 🔄 プルリクエストプロセス

### 1. 準備
```bash
# 最新のmainブランチを取得
git checkout main
git pull origin main

# 機能ブランチを作成
git checkout -b feature/your-feature-name
```

### 2. 開発
- 小さな、論理的なコミットを作成
- 明確なコミットメッセージを記述
- テストを追加・更新

### 3. テスト
```bash
# テスト実行
make test

# コードフォーマット確認
python -m flake8 app/
```

### 4. プルリクエスト作成
- 変更内容の説明を記述
- 関連するIssueをリンク
- スクリーンショット（UI変更の場合）

### 5. レビュー対応
- フィードバックに対応
- 必要に応じて追加のテストを実装

## 📚 ドキュメント

### 更新が必要な場合
- `README.md` - 新機能の説明
- `DEPLOYMENT.md` - デプロイ手順の変更
- API仕様書 - 新しいエンドポイント

### ドキュメント作成ガイドライン
- 日本語での記述
- 具体的な例を含める
- スクリーンショットの活用

## 🐛 デバッグ

### ログ確認
```bash
# アプリケーションログ
tail -f app.log

# Dockerログ
make docker-logs
```

### デバッグツール
- Flask Debug Toolbar（開発環境）
- ブラウザ開発者ツール
- pytest デバッグ機能

## 📞 サポート

### 質問・相談
- GitHubのDiscussionsを使用
- Issueでの質問も歓迎

### 緊急の問題
- セキュリティ関連の問題は非公開で報告してください

## 🎯 優先度の高い貢献領域

### 現在募集中
- [ ] 多言語対応（国際化）
- [ ] パフォーマンス最適化
- [ ] セキュリティ強化
- [ ] モバイル対応の改善
- [ ] API仕様書の充実

### 将来的な機能
- [ ] プロジェクト予算管理
- [ ] タスク管理機能
- [ ] レポート機能の拡張
- [ ] 外部システム連携

## 🙏 謝辞

このプロジェクトに貢献していただき、ありがとうございます！
あなたの貢献により、より良いプロジェクト管理システムを構築できます。