# テスト構造

このディレクトリには、プロジェクトのすべてのテストが整理されています。

## ディレクトリ構造

```
tests/
├── unit/                    # ユニットテスト
│   ├── import/             # インポート機能のテスト
│   │   ├── test_csv_import.py
│   │   ├── test_csv_import_mapping.py
│   │   ├── test_mapping_simple.py
│   │   └── test_task19_mapping.py
│   ├── export/             # エクスポート機能のテスト
│   │   ├── test_csv_export.py
│   │   ├── test_excel_export.py
│   │   └── test_excel_integration.py
│   ├── dashboard/          # ダッシュボード機能のテスト
│   │   ├── test_dashboard_api.py
│   │   └── test_dashboard_service.py
│   ├── test_app.py         # アプリケーション基本テスト
│   ├── test_order_probability.py
│   └── test_validation.py  # バリデーション機能テスト
├── integration/            # 統合テスト
│   ├── test_branch_*.py    # 支社機能の統合テスト
│   ├── test_project_*.py   # プロジェクト機能の統合テスト
│   └── test_search_*.py    # 検索機能の統合テスト
├── frontend/               # フロントエンドテスト
│   ├── syntax/            # テンプレート構文テスト
│   ├── template/          # テンプレートテスト
│   └── e2e/               # E2Eテスト
├── manual/                 # 手動テスト・デバッグ用
│   ├── debug_search.py
│   ├── test_search_manual.py
│   └── test_template_debug.py
└── conftest.py            # pytest設定
```

## テストの実行方法

### すべてのテストを実行
```bash
pytest
```

### 特定のカテゴリのテストを実行
```bash
# ユニットテストのみ
pytest tests/unit/

# 統合テストのみ
pytest tests/integration/

# インポート機能のテストのみ
pytest tests/unit/import/

# エクスポート機能のテストのみ
pytest tests/unit/export/
```

### 特定のテストファイルを実行
```bash
pytest tests/unit/import/test_mapping_simple.py -v
```

### カバレッジ付きでテストを実行
```bash
pytest --cov=app tests/
```

## テストファイルの命名規則

- `test_*.py`: 通常のテストファイル
- `*_test.py`: 代替の命名規則
- `test_task*.py`: 特定のタスク実装のテスト

## テストの種類

### ユニットテスト (tests/unit/)
- 個別の関数やクラスの動作をテスト
- 外部依存を最小限に抑制
- 高速で独立性が高い

### 統合テスト (tests/integration/)
- 複数のコンポーネント間の連携をテスト
- データベースやAPIエンドポイントを含む
- より現実的なシナリオをテスト

### フロントエンドテスト (tests/frontend/)
- テンプレートの構文チェック
- ブラウザベースのE2Eテスト
- UI/UXの動作確認

### 手動テスト (tests/manual/)
- 開発中のデバッグ用スクリプト
- 手動実行が必要なテスト
- パフォーマンステストなど