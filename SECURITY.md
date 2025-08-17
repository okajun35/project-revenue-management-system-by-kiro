# Security Policy

## サポートされているバージョン

現在、以下のバージョンでセキュリティアップデートを提供しています：

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## セキュリティ脆弱性の報告

セキュリティ脆弱性を発見した場合は、以下の手順で報告してください：

### 🔒 非公開での報告

**公開のIssueやPull Requestでセキュリティ問題を報告しないでください。**

代わりに、以下の方法で非公開で報告してください：

1. **GitHub Security Advisory**を使用（推奨）
   - リポジトリの「Security」タブから「Report a vulnerability」を選択
   
2. **メールでの報告**
   - 件名：`[SECURITY] Project Revenue Management System - 脆弱性報告`
   - 内容：詳細な脆弱性情報

### 📋 報告に含めるべき情報

以下の情報を可能な限り含めてください：

- **脆弱性の種類**（例：SQL Injection, XSS, CSRF等）
- **影響範囲**（どの機能・データが影響を受けるか）
- **再現手順**（詳細なステップ）
- **概念実証コード**（可能であれば）
- **推奨される修正方法**（あれば）

### 🕐 対応タイムライン

- **24時間以内**: 報告の受領確認
- **72時間以内**: 初期評価と重要度の判定
- **7日以内**: 修正計画の策定
- **30日以内**: 修正版のリリース（重要度による）

## 🛡️ セキュリティ対策

### 実装済みの対策

- **入力検証**: SQLAlchemyによるSQLインジェクション対策
- **CSRF保護**: Flask-WTFによるCSRF トークン
- **XSS対策**: Jinjaテンプレートの自動エスケープ
- **セッション管理**: Flaskの安全なセッション管理
- **パスワードハッシュ化**: 将来の認証機能に向けた準備

### 推奨される運用

#### 本番環境
```bash
# 環境変数の設定
export FLASK_ENV=production
export SECRET_KEY="your-secure-random-key"

# HTTPSの使用
# リバースプロキシ（Nginx）でSSL終端を推奨
```

#### データベース
```bash
# SQLiteファイルの権限設定
chmod 600 data/projects.db

# バックアップの暗号化
# 機密データを含む場合は暗号化バックアップを推奨
```

#### Docker環境
```bash
# 非rootユーザーでの実行
# セキュリティスキャンの実行
docker scan your-image:tag
```

## 🔍 セキュリティチェックリスト

### 開発者向け

- [ ] 新機能にはセキュリティレビューを実施
- [ ] 入力値の検証を適切に実装
- [ ] 機密情報をログに出力しない
- [ ] 依存関係の脆弱性を定期的にチェック

### 運用者向け

- [ ] 定期的なセキュリティアップデート
- [ ] アクセスログの監視
- [ ] バックアップの暗号化
- [ ] ネットワークセキュリティの設定

## 📚 セキュリティリソース

### 参考資料
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/en/2.0.x/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/core/security.html)

### ツール
```bash
# 依存関係の脆弱性チェック
pip install safety
safety check

# コード品質チェック
pip install bandit
bandit -r app/
```

## 🏆 セキュリティ貢献者

セキュリティ脆弱性を責任を持って報告してくださった方々に感謝いたします。

<!-- 将来的に貢献者リストを追加 -->

## 📞 連絡先

セキュリティに関する質問や懸念がある場合：

- **一般的な質問**: GitHubのDiscussions
- **脆弱性報告**: GitHub Security Advisory（推奨）
- **緊急事態**: 上記の非公開報告方法を使用

---

**注意**: このセキュリティポリシーは定期的に更新されます。最新版を確認してください。