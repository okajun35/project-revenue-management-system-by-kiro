# スクリプト

このディレクトリには、プロジェクトの初期化、データ作成、メンテナンス用のスクリプトが含まれています。

## 📋 スクリプト一覧

### 初期化スクリプト
- `init_db.py` - データベース初期化
- `init_sample_data.py` - 基本マスターデータ作成
- `simple_init.py` - 簡易初期化

### サンプルデータ作成
- `create_sample_data.py` - 豊富なサンプルデータ作成
- `add_monthly_sample_data.py` - 月別データ追加
- `create_test_excel.py` - テスト用Excelファイル作成

### メンテナンススクリプト
- `fix_osaka_branch.py` - 大阪支社データ修正（例）

### システム管理（`scripts/` サブディレクトリ）
- `backup.sh` - データベースバックアップ
- `restore.sh` - データベースリストア
- `deploy.sh` - デプロイメント
- `validate-setup.sh` - セットアップ検証
- `monitor.sh` - システム監視

## 🚀 使用方法

### 初回セットアップ
```bash
# 1. データベース初期化
python scripts/init_db.py

# 2. 基本マスターデータ作成
python scripts/init_sample_data.py

# 3. 豊富なサンプルデータ作成
python scripts/create_sample_data.py

# 4. 月別データ追加
python scripts/add_monthly_sample_data.py
```

### ワンコマンドセットアップ
```bash
# Makefileを使用（推奨）
make demo
```

### 個別スクリプト実行
```bash
# 特定のスクリプトのみ実行
python scripts/init_sample_data.py
```

## 📝 スクリプト作成ガイドライン

### 命名規則
- `init_*.py` - 初期化系
- `create_*.py` - データ作成系
- `fix_*.py` - データ修正系
- `backup_*.py` - バックアップ系

### 実装パターン
```python
#!/usr/bin/env python3
"""
スクリプトの説明
"""

from app import create_app, db
from app.models import YourModel

def main():
    """メイン処理"""
    app = create_app()
    
    with app.app_context():
        # 処理内容
        pass

if __name__ == '__main__':
    main()
```

### エラーハンドリング
- 適切な例外処理を実装
- ログ出力で進捗を表示
- 失敗時のロールバック処理

## 🔧 開発者向け

### 新しいスクリプト追加
1. 適切なディレクトリに配置
2. 実行権限を設定
3. READMEを更新
4. Makefileにコマンド追加（必要に応じて）

### テスト
- 開発環境で十分テスト
- 本番データに影響しないよう注意
- 可能な限り冪等性を保つ