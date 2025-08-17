# フロントエンドテスト自動化システム

このディレクトリには、Webアプリケーションのフロントエンド機能を自動的にテストするためのシステムが含まれています。

## 概要

フロントエンドテスト自動化システムは以下の機能を提供します：

- **テンプレート統合テスト**: Jinjaテンプレートの正しいレンダリングを検証
- **API統合テスト**: DataTables APIなどのエンドポイントをテスト
- **E2Eテスト**: Playwrightを使用した実際のブラウザでのテスト
- **構文チェック**: テンプレートの構文エラーを検出
- **レポート生成**: 詳細なHTMLレポートとスクリーンショット

## ディレクトリ構造

```
tests/frontend/
├── template/           # テンプレート統合テスト
├── api/               # API統合テスト
├── e2e/               # E2Eテスト（Playwright）
├── syntax/            # テンプレート構文チェック
├── utils/             # テストユーティリティ
├── config/            # 設定ファイル
│   ├── test_config.py      # Python テスト設定
│   ├── playwright.config.js # Playwright設定
│   ├── global-setup.js     # グローバルセットアップ
│   └── global-teardown.js  # グローバルクリーンアップ
├── reports/           # テスト結果レポート
│   ├── html/          # HTMLレポート
│   ├── screenshots/   # スクリーンショット
│   ├── json/          # JSONレポート
│   ├── junit/         # JUnitレポート
│   ├── videos/        # テスト実行動画
│   └── coverage/      # カバレッジレポート
├── conftest.py        # pytest設定とフィクスチャ
├── pytest.ini        # pytest設定ファイル
└── README.md          # このファイル
```

## セットアップ

### 1. 依存関係のインストール

```bash
# Python依存関係
pip install -r requirements.txt

# Playwrightブラウザ
make install-playwright
# または
python -m playwright install
```

### 2. テスト環境のセットアップ

```bash
make setup-frontend-tests
```

## テストの実行

### 全フロントエンドテストの実行

```bash
# 従来のフロントエンドテスト
make test-frontend

# 新しい自動化システム
make test-frontend-automation
```

### 特定のテストタイプの実行

```bash
# テンプレートテストのみ
python -m pytest tests/frontend/template/ -v

# APIテストのみ
python -m pytest tests/frontend/api/ -v

# E2Eテストのみ（Playwright）
make test-playwright

# 構文チェックのみ
python -m pytest tests/frontend/syntax/ -v
```

### マーカーを使用したテスト実行

```bash
# スモークテストのみ
python -m pytest tests/frontend/ -m smoke -v

# 遅いテストを除外
python -m pytest tests/frontend/ -m "not slow" -v

# パフォーマンステストのみ
python -m pytest tests/frontend/ -m performance -v
```

## 設定

### テスト設定の変更

`tests/frontend/config/test_config.py` でテスト設定を変更できます：

```python
# ベースURL
BASE_URL = "http://localhost:5000"

# ブラウザ設定
BROWSER_TYPES = ["chromium", "firefox", "webkit"]
HEADLESS = True

# タイムアウト設定
PAGE_LOAD_TIMEOUT = 10000  # ミリ秒
API_RESPONSE_TIMEOUT = 5000  # ミリ秒
```

### 環境変数での設定

```bash
# CI環境での実行
export CI=true

# ローカル開発環境
export TEST_ENV=local

# 特定のブラウザのみ使用
export TEST_BROWSER=chromium

# ベースURLの変更
export BASE_URL=http://localhost:8000
```

## レポート

### HTMLレポート

テスト実行後、以下の場所でレポートを確認できます：

- **pytest レポート**: `tests/frontend/reports/html/pytest-report.html`
- **Playwright レポート**: `tests/frontend/reports/html/playwright-report/index.html`

### スクリーンショット

失敗したテストのスクリーンショットは `tests/frontend/reports/screenshots/` に保存されます。

### カバレッジレポート

コードカバレッジレポートは `tests/frontend/reports/coverage/` で確認できます。

## トラブルシューティング

### よくある問題

1. **Playwrightブラウザが見つからない**
   ```bash
   make install-playwright
   ```

2. **テストデータベースの問題**
   ```bash
   # データベースをリセット
   make reset
   ```

3. **ポート5000が使用中**
   ```bash
   # 別のポートを使用
   export BASE_URL=http://localhost:8000
   python app.py --port 8000
   ```

### ログの確認

テスト実行時の詳細ログは以下で確認できます：

```bash
# 詳細ログ付きでテスト実行
python -m pytest tests/frontend/ -v -s --log-cli-level=DEBUG
```

## 新しいテストの追加

### テンプレートテストの追加

```python
# tests/frontend/template/test_new_page.py
import pytest

@pytest.mark.template
def test_new_page_rendering(client):
    response = client.get('/new-page/')
    assert response.status_code == 200
    assert b'Expected Content' in response.data
```

### E2Eテストの追加

```python
# tests/frontend/e2e/test_new_feature.py
import pytest
from playwright.async_api import Page

@pytest.mark.e2e
async def test_new_feature(page: Page):
    await page.goto('/new-feature/')
    await page.click('#submit-button')
    await expect(page.locator('#success-message')).to_be_visible()
```

## ベストプラクティス

1. **テストの独立性**: 各テストは他のテストに依存しないようにする
2. **適切なマーカー**: テストに適切なマーカーを付ける
3. **明確なアサーション**: 何をテストしているかが明確になるようにする
4. **エラーハンドリング**: 予期される失敗に対する適切な処理
5. **パフォーマンス**: 不要に遅いテストは避ける

## CI/CD統合

GitHub Actionsでの実行例：

```yaml
name: Frontend Tests
on: [push, pull_request]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m playwright install
      - name: Run Frontend Tests
        run: make test-frontend-automation
      - name: Upload Test Results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/frontend/reports/
```