# プロジェクト構造

整理後のプロジェクトディレクトリ構造です。

## 📁 ディレクトリ構造

```
project-revenue-management-system/
├── 📁 app/                          # メインアプリケーション
│   ├── 📁 services/                 # ビジネスロジック
│   ├── 📁 templates/                # Jinjaテンプレート
│   ├── 📄 models.py                 # データモデル
│   ├── 📄 routes.py                 # メインルート
│   ├── 📄 *_routes.py               # 機能別ルート
│   └── 📄 forms.py                  # フォーム定義
├── 📁 tests/                        # テストファイル群
│   ├── 📁 unit/                     # 単体テスト
│   ├── 📁 integration/              # 統合テスト
│   ├── 📁 frontend/                 # フロントエンドテスト
│   ├── 📁 fixtures/                 # テストデータ・フィクスチャ
│   └── 📁 manual/                   # 手動テスト
├── 📁 scripts/                      # 初期化・メンテナンススクリプト
│   ├── 📄 init_db.py                # データベース初期化
│   ├── 📄 init_sample_data.py       # 基本マスターデータ
│   ├── 📄 create_sample_data.py     # サンプルデータ作成
│   ├── 📄 add_monthly_sample_data.py # 月別データ追加
│   ├── 📄 backup.sh                 # バックアップスクリプト
│   ├── 📄 restore.sh                # リストアスクリプト
│   └── 📄 README.md                 # スクリプト説明
├── 📁 migrations/                   # データベースマイグレーション
│   ├── 📄 migrate.py                # 基本マイグレーション
│   ├── 📄 migrate_add_*.py          # 各種マイグレーション
│   └── 📄 README.md                 # マイグレーション説明
├── 📁 docker/                       # Docker設定
│   ├── 📁 dev/                      # 開発環境用
│   │   └── 📄 docker-compose.dev.yml
│   ├── 📁 prod/                     # 本番環境用
│   │   ├── 📄 docker-compose.prod.yml
│   │   └── 📄 Dockerfile.dev
│   └── 📄 README.md                 # Docker説明
├── 📁 docs/                         # ドキュメント
│   ├── 📄 TASK*.md                  # 実装レポート
│   ├── 📄 DEPLOYMENT.md             # デプロイ手順
│   ├── 📄 GITHUB_SETUP.md           # GitHub設定
│   └── 📄 README.md                 # ドキュメント説明
├── 📁 .github/                      # GitHub設定
│   ├── 📁 workflows/                # GitHub Actions
│   ├── 📁 ISSUE_TEMPLATE/           # Issueテンプレート
│   └── 📄 pull_request_template.md  # PRテンプレート
├── 📁 .kiro/                        # Kiro IDE設定
│   ├── 📁 specs/                    # 仕様書
│   └── 📁 steering/                 # ガイドライン
├── 📁 static/                       # 静的ファイル
├── 📁 data/                         # データベースファイル
├── 📁 uploads/                      # アップロードファイル
├── 📁 nginx/                        # Nginx設定
├── 📄 app.py                        # メインアプリケーション
├── 📄 config.py                     # 設定ファイル
├── 📄 requirements.txt              # 依存関係
├── 📄 Makefile                      # 便利コマンド
├── 📄 Dockerfile                    # Dockerイメージ定義
├── 📄 docker-compose.yml            # 基本Docker設定
├── 📄 README.md                     # プロジェクト説明
├── 📄 LICENSE                       # ライセンス
├── 📄 CONTRIBUTING.md               # 貢献ガイド
├── 📄 SECURITY.md                   # セキュリティポリシー
├── 📄 CODE_OF_CONDUCT.md            # 行動規範
└── 📄 .gitignore                    # Git除外設定
```

## 🎯 整理のメリット

### 1. **明確な責任分離**
- `scripts/` - 初期化・メンテナンス
- `migrations/` - データベース変更
- `docker/` - コンテナ設定
- `docs/` - ドキュメント

### 2. **開発効率向上**
- 目的別にファイルが整理されている
- 新しい開発者が理解しやすい
- メンテナンスが容易

### 3. **プロフェッショナルな構造**
- 企業レベルのプロジェクト構造
- GitHubでの見栄えが良い
- CI/CDとの親和性が高い

## 📝 ファイル移動履歴

### 移動したファイル

**`docs/` に移動**
- `TASK*.md` - 実装レポート
- `DASHBOARD_BRANCH_STATS_YEAR_FILTER_SUMMARY.md`
- `DEPLOYMENT.md`
- `GITHUB_SETUP.md`

**`scripts/` に移動**
- `init_*.py` - 初期化スクリプト
- `create_*.py` - データ作成スクリプト
- `add_*.py` - データ追加スクリプト
- `simple_init.py`
- `fix_*.py` - データ修正スクリプト

**`migrations/` に移動**
- `migrate*.py` - マイグレーションスクリプト

**`docker/` に移動**
- `docker-compose.dev.yml` → `docker/dev/`
- `docker-compose.prod.yml` → `docker/prod/`
- `Dockerfile.dev` → `docker/prod/`

**`tests/fixtures/` に移動**
- `test_*.csv` - テスト用CSVファイル

### 更新したファイル
- `Makefile` - パス更新
- `README.md` - パス更新
- 各ディレクトリに `README.md` 追加

## 🚀 使用方法

整理後も既存のコマンドはそのまま使用できます：

```bash
# デモ環境起動
make demo

# 開発環境起動
make dev

# テスト実行
make test

# Docker環境
make docker-dev
make docker-prod
```

パスが自動的に更新されているため、ユーザーは変更を意識する必要がありません。