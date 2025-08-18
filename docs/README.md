# ドキュメント

## 変更履歴（テスト環境・ダッシュボード初期化関連）

- テスト実行時は `FLASK_ENV=testing` を使用し、テスト専用DB（`data/test_sample.db`）へ分離しました。
	- Makefileの `make test` と `make test-coverage` は自動的に `FLASK_ENV=testing` を設定します。
	- 直接pytestを実行する場合は、`FLASK_ENV=testing` を付与してください。
- 初回起動時にDBが未初期化でもダッシュボードが500にならないように、以下を導入しました。
	- `app/__init__.py` にて `@app.before_request` でテーブル存在チェックし、不足時に `db.create_all()` を実行
	- `DashboardService` 各メソッドで `OperationalError` を捕捉して空データを返すフォールバックを実装

これにより、開発/本番DBを保護しつつ、初回起動やデータ未投入時でもアプリが安定して表示されます。

このディレクトリには、プロジェクトの各種ドキュメントが含まれています。

## 📋 ファイル一覧

### 実装レポート
- `TASK*.md` - 各タスクの実装完了報告書
- `DASHBOARD_BRANCH_STATS_YEAR_FILTER_SUMMARY.md` - ダッシュボード支社別統計年度選択機能の実装報告

### セットアップ・デプロイ
- `DEPLOYMENT.md` - デプロイメント手順書
- `GITHUB_SETUP.md` - GitHubリポジトリセットアップガイド

## 📚 関連ドキュメント

プロジェクトルートにある主要ドキュメント：
- `README.md` - プロジェクト概要・使用方法
- `CONTRIBUTING.md` - 貢献ガイドライン
- `SECURITY.md` - セキュリティポリシー
- `CODE_OF_CONDUCT.md` - 行動規範

## 🔗 外部ドキュメント

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [AdminLTE Documentation](https://adminlte.io/docs/)