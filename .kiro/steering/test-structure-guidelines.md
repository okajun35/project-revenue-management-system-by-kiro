---
inclusion: always
---

# テスト構造ガイドライン

このドキュメントは、プロジェクトでテストファイルを作成する際の構造とガイドラインを定義します。

## テストディレクトリ構造

```
tests/
├── unit/                    # ユニットテスト
│   ├── import/             # インポート機能のテスト
│   ├── export/             # エクスポート機能のテスト
│   ├── dashboard/          # ダッシュボード機能のテスト
│   ├── projects/           # プロジェクト機能のテスト
│   ├── branches/           # 支社機能のテスト
│   ├── fiscal_years/       # 年度機能のテスト
│   ├── services/           # サービスクラスのテスト
│   └── models/             # モデルのテスト
├── integration/            # 統合テスト
│   ├── api/               # API統合テスト
│   ├── database/          # データベース統合テスト
│   └── workflows/         # ワークフロー統合テスト
├── frontend/               # フロントエンドテスト
│   ├── e2e/               # E2Eテスト
│   ├── template/          # テンプレートテスト
│   └── syntax/            # 構文テスト
├── manual/                 # 手動テスト・デバッグ用
│   ├── performance/       # パフォーマンステスト
│   └── debug/             # デバッグスクリプト
└── fixtures/              # テストデータ・フィクスチャ
```

## テストファイル作成ルール

### 1. ファイル配置ルール

**ユニットテスト (`tests/unit/`)**
- **インポート機能**: `tests/unit/import/test_*.py`
- **エクスポート機能**: `tests/unit/export/test_*.py`
- **ダッシュボード機能**: `tests/unit/dashboard/test_*.py`
- **プロジェクト機能**: `tests/unit/projects/test_*.py`
- **支社機能**: `tests/unit/branches/test_*.py`
- **年度機能**: `tests/unit/fiscal_years/test_*.py`
- **サービスクラス**: `tests/unit/services/test_*_service.py`
- **モデル**: `tests/unit/models/test_*_model.py`

**統合テスト (`tests/integration/`)**
- **API統合**: `tests/integration/api/test_*_api.py`
- **データベース統合**: `tests/integration/database/test_*_db.py`
- **ワークフロー統合**: `tests/integration/workflows/test_*_workflow.py`

**フロントエンドテスト (`tests/frontend/`)**
- **E2Eテスト**: `tests/frontend/e2e/test_*_e2e.py`
- **テンプレートテスト**: `tests/frontend/template/test_*_template.py`
- **構文テスト**: `tests/frontend/syntax/test_*_syntax.py`

**手動テスト (`tests/manual/`)**
- **パフォーマンステスト**: `tests/manual/performance/perf_*.py`
- **デバッグスクリプト**: `tests/manual/debug/debug_*.py`

### 2. ファイル命名規則

- **通常のテスト**: `test_<機能名>.py`
- **特定タスクのテスト**: `test_task<番号>_<機能名>.py`
- **サービステスト**: `test_<サービス名>_service.py`
- **モデルテスト**: `test_<モデル名>_model.py`
- **APIテスト**: `test_<エンドポイント名>_api.py`
- **手動テスト**: `manual_test_<機能名>.py`
- **デバッグスクリプト**: `debug_<機能名>.py`
- **パフォーマンステスト**: `perf_<機能名>.py`

### 3. テストクラス命名規則

```python
# ユニットテスト
class TestImportService:
class TestProjectModel:
class TestBranchValidation:

# 統合テスト
class TestImportWorkflow:
class TestProjectAPIIntegration:
class TestDatabaseIntegration:

# フロントエンドテスト
class TestMappingTemplate:
class TestDashboardE2E:
```

## 実装時のガイドライン

### 新しいテストファイルを作成する際の手順

1. **機能を特定**: テストする機能がどのカテゴリに属するかを判断
2. **適切なディレクトリを選択**: 上記のルールに従ってディレクトリを選択
3. **ファイル名を決定**: 命名規則に従ってファイル名を決定
4. **必要な`__init__.py`を確認**: 新しいディレクトリの場合は`__init__.py`を作成

### 例：新しいテストファイルの作成

```python
# インポート機能の新しいテスト
# ファイル: tests/unit/import/test_excel_import.py

import pytest
from app.services.import_service import ImportService

class TestExcelImport:
    def test_excel_file_validation(self):
        # テスト実装
        pass
```

```python
# 支社機能の統合テスト
# ファイル: tests/integration/workflows/test_branch_workflow.py

import pytest
from app import create_app, db

class TestBranchWorkflow:
    def test_branch_creation_workflow(self):
        # テスト実装
        pass
```

### テストデータとフィクスチャ

- **共通フィクスチャ**: `tests/fixtures/`に配置
- **テストデータファイル**: `tests/fixtures/data/`に配置
- **モックデータ**: `tests/fixtures/mocks/`に配置

## 実行コマンド例

```bash
# 特定カテゴリのテスト実行
pytest tests/unit/import/          # インポート機能のユニットテスト
pytest tests/unit/export/          # エクスポート機能のユニットテスト
pytest tests/integration/api/      # API統合テスト
pytest tests/frontend/e2e/         # E2Eテスト

# 特定機能のテスト実行
pytest tests/unit/import/test_mapping_simple.py -v
pytest tests/integration/workflows/test_branch_workflow.py -v

# カバレッジ付きテスト実行
pytest --cov=app tests/unit/import/ --cov-report=html
```

## 注意事項

1. **プロジェクト直下にテストファイルを作成しない**
2. **適切なディレクトリ構造を維持する**
3. **`__init__.py`ファイルを忘れずに作成する**
4. **テストファイル名は必ず`test_`で始める**
5. **データベースを使用するテストでは適切なクリーンアップを行う**

## 自動適用ルール

Kiroでテストファイルを作成する際は、以下のルールが自動的に適用されます：

### 機能別ディレクトリマッピング

- **インポート機能のテスト** → `tests/unit/import/`
- **エクスポート機能のテスト** → `tests/unit/export/`
- **ダッシュボード機能のテスト** → `tests/unit/dashboard/`
- **プロジェクト機能のテスト** → `tests/unit/projects/`
- **支社機能のテスト** → `tests/unit/branches/`
- **年度機能のテスト** → `tests/unit/fiscal_years/`
- **サービスクラスのテスト** → `tests/unit/services/`
- **モデルのテスト** → `tests/unit/models/`
- **API統合テスト** → `tests/integration/api/`
- **ワークフロー統合テスト** → `tests/integration/workflows/`
- **E2Eテスト** → `tests/frontend/e2e/`
- **手動テスト・デバッグ** → `tests/manual/debug/`

### テスト作成時の自動判定

新しいテストファイルを作成する際、Kiroは以下の情報を基に適切なディレクトリを自動選択します：

1. **ファイル名のパターン**
2. **テスト対象の機能**
3. **テストの種類（ユニット/統合/E2E）**

### 例：自動配置の例

```python
# インポート機能のテスト → tests/unit/import/test_csv_validation.py
def test_csv_validation():
    pass

# 支社機能の統合テスト → tests/integration/workflows/test_branch_creation_workflow.py
def test_branch_creation_workflow():
    pass

# ダッシュボードのE2Eテスト → tests/frontend/e2e/test_dashboard_e2e.py
def test_dashboard_display():
    pass
```

このガイドラインに従うことで、テストファイルが整理され、保守しやすいプロジェクト構造を維持できます。