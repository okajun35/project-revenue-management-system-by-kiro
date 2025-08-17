# プロジェクト収支システム

[![CI](https://github.com/your-username/project-revenue-management-system/workflows/CI/badge.svg)](https://github.com/your-username/project-revenue-management-system/actions)
[![codecov](https://codecov.io/gh/your-username/project-revenue-management-system/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/project-revenue-management-system)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

## 概要
プロジェクトの売上、経費、粗利を管理するFlaskベースのWebアプリケーションです。
支社管理機能とプロジェクト管理機能を備えた本格的な業務システムです。

## 主な機能
- 📊 **ダッシュボード**: プロジェクト統計とグラフ表示、支社別統計の年度選択機能
- 🏢 **支社管理**: 支社の登録・編集・削除・有効/無効切り替え
- 📅 **年度管理**: 年度マスターの登録・編集・削除・有効/無効切り替え
- 📋 **プロジェクト管理**: プロジェクトの登録・編集・削除・一覧表示
- 🔍 **高度な検索・絞り込み**: 年度・支社による絞り込み、DataTablesによる高速検索・ソート・ページング
- 📱 **レスポンシブデザイン**: AdminLTEベースのモダンなUI
- ✅ **データ検証**: 包括的なバリデーション機能

## クイックスタート

### 🚀 最速で動作確認する場合
```bash
# 1. 依存関係をインストール
make install

# 2. デモ用データでアプリケーションを起動
make demo
```
ブラウザで http://localhost:5000 にアクセス

### 📋 利用可能なコマンド
```bash
make help          # 全コマンドの説明を表示
make install       # 依存関係をインストール
make setup         # データベースを初期化
make dev-data      # 開発用サンプルデータを作成
make demo-data     # 豊富なデモデータを作成
make run           # アプリケーションを起動
make demo          # デモ用データでアプリケーションを起動
make test          # 全テストを実行
make clean         # 一時ファイルを削除
```

## プロジェクト構造
```
project-revenue-system/
├── app/
│   ├── __init__.py              # アプリケーションファクトリ
│   ├── models.py                # データモデル（Project, Branch, FiscalYear）
│   ├── project_routes.py        # プロジェクト関連ルート
│   ├── branch_routes.py         # 支社関連ルート
│   ├── fiscal_year_routes.py    # 年度管理関連ルート
│   ├── forms.py                 # WTForms定義
│   ├── enums.py                 # 列挙型定義
│   ├── services/                # ビジネスロジック
│   │   ├── project_service.py   # プロジェクトサービス
│   │   ├── branch_service.py    # 支社サービス
│   │   └── validation_service.py # バリデーションサービス
│   └── templates/               # Jinjaテンプレート
│       ├── base.html            # ベーステンプレート
│       ├── dashboard.html       # ダッシュボード
│       ├── components/          # 共通コンポーネント
│       │   └── sidebar.html     # サイドバーメニュー
│       ├── projects/            # プロジェクト画面
│       │   ├── index.html       # 一覧画面（年度・支社絞り込み機能付き）
│       │   ├── form.html        # 作成・編集画面
│       │   └── show.html        # 詳細画面
│       ├── branches/            # 支社画面
│       │   ├── index.html       # 一覧画面
│       │   ├── form.html        # 作成・編集画面
│       │   └── show.html        # 詳細画面
│       └── fiscal_years/        # 年度管理画面
│           ├── index.html       # 一覧画面
│           ├── form.html        # 作成・編集画面
│           └── show.html        # 詳細画面
├── data/
│   └── projects.db              # SQLiteデータベース
├── static/                      # 静的ファイル（AdminLTE）
├── tests/                       # テストファイル群
│   ├── conftest.py              # pytest設定とフィクスチャ
│   ├── unit/                    # 単体テスト（テスト専用DB使用）
│   │   ├── dashboard/           # ダッシュボード機能テスト
│   │   ├── import/              # インポート機能テスト
│   │   └── backup/              # バックアップ機能テスト
│   ├── integration/             # 統合テスト
│   ├── frontend/                # フロントエンドテスト
│   └── manual/                  # 手動テスト・サンプルデータ作成
├── .kiro/specs/                 # 仕様書・設計書
│   ├── project-revenue-system/  # プロジェクト収支システム仕様
│   └── frontend-testing-automation/ # フロントエンドテスト自動化仕様
├── Makefile                     # 動作確認用コマンド集
├── app.py                       # メインアプリケーション
├── config.py                    # 設定ファイル
├── requirements.txt             # 依存関係
└── README.md                    # このファイル
```

## 詳細セットアップ

### 1. 依存関係のインストール
```bash
make install
# または
pip install -r requirements.txt
```

### 2. データベースの初期化
```bash
make setup
# または
python init_db.py
```

### 3. 開発用サンプルデータの作成

#### 基本的なサンプルデータ
```bash
# Windows環境（PowerShell）
python tests/manual/manual_test_branch_creation.py
python tests/manual/manual_test_project_creation.py

# Linux/Mac環境（makeが使える場合）
make dev-data
```

#### 豊富なデモデータ（推奨）
```bash
# 初期データベース作成
python init_db.py

# 基本マスターデータ（支社・年度）
python init_sample_data.py

# 豊富なプロジェクトデータ（複数年度・複数支社）
python create_sample_data.py

# 月別データの追加（ダッシュボード表示用）
python add_monthly_sample_data.py
```

#### ワンコマンドでデモ環境構築
```bash
# 全てを一括実行（最も簡単）
make demo
```

#### 作成されるデモデータ
- **支社**: 東京本社、大阪支社、名古屋支社、福岡支社など
- **年度**: 2023年度、2024年度、2025年度
- **プロジェクト**: 各支社・各年度に複数のプロジェクト
  - 受注角度: 〇（確実）、△（可能性あり）、×（困難）
  - 売上規模: 100万円〜5000万円の幅広いプロジェクト
  - 月別分散: 年度内の各月に分散配置

#### デモデータで確認できる機能
- **ダッシュボード統計**: 年度別・支社別の売上・粗利分析
- **支社別統計の年度選択**: 特定年度の支社パフォーマンス比較
- **プロジェクト一覧**: 年度・支社による絞り込み機能
- **受注角度分布**: 〇・△・×の割合とその売上貢献度
- **月別売上推移**: 年度内の売上トレンド分析

### 4. アプリケーションの起動
```bash
make run
# または
python app.py
```

## テスト

### 全テスト実行
```bash
# Windows環境（PowerShell）
python -m pytest tests/ -v

# Linux/Mac環境（makeが使える場合）
make test
```

### テストカテゴリ別実行
```bash
# 単体テスト（テスト専用データベース使用）
python -m pytest tests/unit/ -v

# 統合テスト
python -m pytest tests/integration/ -v

# フロントエンドテスト
python -m pytest tests/frontend/ -v

# 機能別テスト
python -m pytest tests/integration/test_branch_*.py -v  # 支社機能
python -m pytest tests/integration/test_project_*.py -v # プロジェクト機能
python -m pytest tests/unit/dashboard/ -v              # ダッシュボード機能

# クリーンなテスト（推奨）
python -m pytest tests/unit/test_validation_clean.py -v
```

### 個別テスト実行例
```bash
python -m pytest tests/integration/test_branch_functionality.py -v
python -m pytest tests/integration/test_project_creation.py -v
python -m pytest tests/integration/test_task9_branch_selection.py -v

# 新しいクリーンなテスト（推奨）
python -m pytest tests/unit/test_validation_clean.py -v
```

## テスト環境

### テスト専用データベース
単体テストでは**テスト専用の一時データベース**を使用し、実データに影響を与えません：

- **独立性**: 各テストが完全に独立して実行
- **安全性**: 実データベースに影響なし
- **並列実行**: 複数テストの同時実行が可能
- **再現性**: いつでも同じ結果が得られる

### フィクスチャ（テストデータ）
`tests/conftest.py`でテスト用データを自動生成：

```python
# テスト用支社データ
def test_example(sample_branch):
    # sample_branchは自動的に作成される

# 複数の支社データ
def test_example(sample_branches):
    # 複数の支社が自動作成される

# プロジェクトデータ
def test_example(sample_project):
    # プロジェクトと関連支社が自動作成される
```

### テストの種類
- **単体テスト**: モデル、サービス、バリデーションのテスト
- **統合テスト**: ルート、API、データベース連携のテスト
- **フロントエンドテスト**: テンプレート、JavaScript、UI のテスト

## データモデル

### Branch（支社）テーブル
- `id`: 主キー（自動増分）
- `branch_code`: 支社コード（一意、英数字・ハイフン・アンダースコア）
- `branch_name`: 支社名（一意）
- `is_active`: 有効フラグ（True/False）
- `created_at`: 作成日時
- `updated_at`: 更新日時

### FiscalYear（年度マスター）テーブル
- `id`: 主キー（自動増分）
- `year`: 年度（一意、数値）
- `year_name`: 年度名（一意、例：「2024年度」）
- `is_active`: 有効フラグ（True/False）
- `created_at`: 作成日時
- `updated_at`: 更新日時

### Project（プロジェクト）テーブル
- `id`: 主キー（自動増分）
- `project_code`: プロジェクトコード（一意、英数字・ハイフン・アンダースコア）
- `project_name`: プロジェクト名
- `branch_id`: 支社ID（外部キー）
- `fiscal_year`: 売上の年度（年度マスターと関連付け）
- `order_probability`: 受注角度（0, 50, 100のみ）
- `revenue`: 売上（契約金）
- `expenses`: 経費（トータル）
- `created_at`: 作成日時
- `updated_at`: 更新日時

### データ制約
- 受注角度: 0（×）, 50（△）, 100（〇）のみ
- 売上・経費: 0以上の数値
- 売上の年度: 1900-2100の範囲
- 支社: 有効な支社のみ選択可能

## 主要エンドポイント

### ダッシュボード
- `GET /` - ダッシュボード画面
- `GET /api/dashboard-data` - 年度別統計データAPI
- `GET /api/branch-stats` - 支社別統計API（年度フィルター対応）
- `GET /api/chart-data` - 年度別チャートデータAPI
- `GET /api/order-probability-distribution` - 受注角度分布API

### 支社管理
- `GET /branches` - 支社一覧
- `GET /branches/new` - 支社作成フォーム
- `POST /branches` - 支社作成
- `GET /branches/{id}` - 支社詳細
- `GET /branches/{id}/edit` - 支社編集フォーム
- `POST /branches/{id}/update` - 支社更新
- `POST /branches/{id}/delete` - 支社削除
- `POST /branches/{id}/toggle-status` - 有効/無効切り替え

### 年度管理
- `GET /fiscal-years` - 年度一覧
- `GET /fiscal-years/new` - 年度作成フォーム
- `POST /fiscal-years` - 年度作成
- `GET /fiscal-years/{id}` - 年度詳細
- `GET /fiscal-years/{id}/edit` - 年度編集フォーム
- `POST /fiscal-years/{id}/update` - 年度更新
- `POST /fiscal-years/{id}/delete` - 年度削除
- `POST /fiscal-years/{id}/toggle` - 有効/無効切り替え

### プロジェクト管理
- `GET /projects` - プロジェクト一覧
- `GET /projects/api/list` - DataTables用API
- `GET /projects/new` - プロジェクト作成フォーム
- `POST /projects` - プロジェクト作成
- `GET /projects/{id}` - プロジェクト詳細
- `GET /projects/{id}/edit` - プロジェクト編集フォーム
- `POST /projects/{id}/update` - プロジェクト更新
- `POST /projects/{id}/delete` - プロジェクト削除

## 技術仕様

### フレームワーク・ライブラリ
- **Flask**: Webアプリケーションフレームワーク
- **SQLAlchemy**: ORM（オブジェクトリレーショナルマッピング）
- **WTForms**: フォーム処理・バリデーション
- **AdminLTE**: レスポンシブ管理画面テンプレート
- **DataTables**: 高機能テーブル表示・検索・ソート
- **Chart.js**: グラフ表示
- **pytest**: テストフレームワーク

### 環境変数
- `FLASK_ENV`: 実行環境（development/production/testing）
- `SECRET_KEY`: セッション暗号化キー（本番環境では必須）
- `PORT`: サーバーポート（デフォルト: 5000）

### 設定クラス
- `DevelopmentConfig`: 開発環境用設定
- `ProductionConfig`: 本番環境用設定
- `TestingConfig`: テスト環境用設定

## 実装済み機能

### ✅ 基盤機能
- Flaskアプリケーションの基本構造
- SQLAlchemyによるデータモデル（Branch, Project）
- データベース初期化・マイグレーション
- 包括的なバリデーション機能
- エラーハンドリング

### ✅ 支社管理機能
- 支社の登録・編集・削除
- 有効/無効状態の切り替え
- 支社一覧表示・検索・ソート
- 関連プロジェクトの存在チェック

### ✅ 年度管理機能
- 年度マスターの登録・編集・削除
- 有効/無効状態の切り替え
- 年度一覧表示・検索・ソート
- 関連プロジェクトの存在チェック
- 年度の自動生成機能

### ✅ プロジェクト管理機能
- プロジェクトの登録・編集・削除
- 支社との関連付け
- 年度マスターとの関連付け
- 受注角度管理（〇・△・×）
- 粗利・粗利率の自動計算
- DataTablesによる高速一覧表示
- 年度・支社による絞り込み機能
- 高度な検索・ソート・ページング機能

### ✅ UI/UX機能
- AdminLTEベースのモダンなデザイン
- レスポンシブ対応
- ダッシュボード（統計情報・グラフ表示）
- 支社別統計の年度選択機能（年内プロジェクト管理重点）
- 直感的なナビゲーション
- フラッシュメッセージによるフィードバック

### ✅ テスト機能
- 単体テスト（モデル・サービス・ルート）
- 統合テスト（Web画面・API）
- バリデーションテスト
- エラーハンドリングテスト

## 動作確認手順

### 1. 基本動作確認
```bash
make quick-test    # 基本的な動作確認
make demo          # デモ用データで起動
```

### 2. 機能別動作確認
1. **ダッシュボード**: http://localhost:5000（支社別統計の年度選択機能付き）
2. **支社管理**: http://localhost:5000/branches
3. **年度管理**: http://localhost:5000/fiscal-years
4. **プロジェクト管理**: http://localhost:5000/projects（年度・支社絞り込み機能付き）

### 3. テスト実行
```bash
make test          # 全テスト実行
make test-branch   # 支社機能テスト
make test-project  # プロジェクト機能テスト
```

## トラブルシューティング

### よくある問題

**Q: `make` コマンドが認識されない**
A: Windows環境では以下の方法で解決：
- Git Bashを使用する
- WSL（Windows Subsystem for Linux）を使用する
- 個別にPythonコマンドを実行する

**Q: データベースエラーが発生する**
A: データベースをリセットしてください：
```bash
make reset
```

**Q: テストが失敗する**
A: 依存関係を再インストールしてください：
```bash
make clean
make install
```

## 開発者向け情報

### コード品質
- PEP 8準拠のコーディングスタイル
- 包括的なエラーハンドリング
- 詳細なコメント・ドキュメント
- 型ヒント（部分的）

### アーキテクチャ
- MVCパターンの採用
- サービス層による業務ロジックの分離
- バリデーション層による入力検証
- テンプレート継承による画面の統一

### 拡張性
- モジュラー設計による機能追加の容易さ
- 設定ベースの環境切り替え
- プラグイン可能なバリデーション
- RESTful APIの基盤