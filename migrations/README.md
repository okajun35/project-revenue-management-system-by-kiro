# データベースマイグレーション

このディレクトリには、データベーススキーマの変更を行うマイグレーションスクリプトが含まれています。

## 📋 マイグレーションファイル

- `migrate.py` - 基本マイグレーション機能
- `migrate_add_branch_to_projects.py` - プロジェクトテーブルに支社関連カラム追加
- `migrate_add_fiscal_years.py` - 年度マスターテーブル追加

## 🚀 使用方法

### 新しいマイグレーション実行
```bash
# 支社関連カラム追加
python migrations/migrate_add_branch_to_projects.py

# 年度マスターテーブル追加
python migrations/migrate_add_fiscal_years.py
```

### マイグレーション作成ガイドライン

1. **ファイル命名規則**: `migrate_<変更内容>.py`
2. **実行順序**: ファイル名の日付順で実行
3. **ロールバック**: 可能な限りロールバック機能を実装
4. **テスト**: 本番適用前に開発環境でテスト

### マイグレーション例

```python
# migrations/migrate_example.py
from app import db
from app.models import YourModel

def upgrade():
    """マイグレーション実行"""
    # スキーマ変更処理
    pass

def downgrade():
    """ロールバック処理"""
    # 元に戻す処理
    pass

if __name__ == '__main__':
    upgrade()
```

## ⚠️ 注意事項

- **本番環境**: マイグレーション前に必ずバックアップを取得
- **データ整合性**: 既存データへの影響を十分検証
- **段階的実行**: 大きな変更は複数のマイグレーションに分割