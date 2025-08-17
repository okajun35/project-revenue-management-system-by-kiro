# GitHub リポジトリセットアップガイド

このドキュメントでは、プロジェクト収支システムをGitHubにアップロードする手順を説明します。

## 🚀 推奨リポジトリ名

**`project-revenue-management-system`**

## 📋 セットアップ手順

### 1. GitHubでリポジトリを作成

1. [GitHub](https://github.com) にログイン
2. 右上の「+」→「New repository」をクリック
3. リポジトリ設定：
   - **Repository name**: `project-revenue-management-system`
   - **Description**: `Flask-based project revenue management system with dashboard, branch management, and comprehensive reporting features`
   - **Visibility**: Public（または Private）
   - **Initialize this repository with**: 何もチェックしない（既存プロジェクトのため）

### 2. ローカルでGitを初期化

```bash
# プロジェクトディレクトリで実行
git init
git add .
git commit -m "Initial commit: Project Revenue Management System

- Complete Flask-based web application
- Dashboard with branch statistics and year filtering
- Project, branch, and fiscal year management
- Comprehensive test suite
- Docker support
- Import/Export functionality
- Backup/Restore features"
```

### 3. リモートリポジトリを追加

```bash
# GitHubリポジトリのURLを設定（your-usernameを実際のユーザー名に変更）
git remote add origin https://github.com/your-username/project-revenue-management-system.git

# メインブランチを設定
git branch -M main

# 初回プッシュ
git push -u origin main
```

### 4. GitHubリポジトリの設定

#### 4.1 リポジトリ設定
1. リポジトリページの「Settings」タブ
2. 「General」→「Features」で以下を有効化：
   - ✅ Issues
   - ✅ Projects
   - ✅ Wiki
   - ✅ Discussions

#### 4.2 ブランチ保護ルール
1. 「Settings」→「Branches」
2. 「Add rule」をクリック
3. 設定：
   - **Branch name pattern**: `main`
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

#### 4.3 セキュリティ設定
1. 「Settings」→「Security & analysis」
2. 以下を有効化：
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ✅ Dependabot security updates

### 5. README.mdのバッジ更新

README.mdの以下の部分を実際のユーザー名に更新：

```markdown
[![CI](https://github.com/YOUR_USERNAME/project-revenue-management-system/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/project-revenue-management-system/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/project-revenue-management-system/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/project-revenue-management-system)
```

### 6. 追加の設定（オプション）

#### 6.1 Topics（タグ）の追加
リポジトリページの「About」セクションで以下のトピックを追加：
- `flask`
- `python`
- `dashboard`
- `project-management`
- `revenue-management`
- `business-application`
- `adminlte`
- `sqlite`
- `docker`

#### 6.2 ライセンスの確認
- ✅ MIT License が既に追加済み

#### 6.3 Codecov設定（オプション）
1. [Codecov](https://codecov.io/) にサインアップ
2. GitHubリポジトリを連携
3. カバレッジレポートの自動生成を有効化

## 🔧 継続的な開発ワークフロー

### ブランチ戦略
```bash
# 新機能開発
git checkout -b feature/new-feature-name
# 開発作業...
git add .
git commit -m "Add new feature: description"
git push origin feature/new-feature-name
# GitHubでPull Request作成

# バグ修正
git checkout -b bugfix/fix-description
# 修正作業...
git add .
git commit -m "Fix: description of the bug fix"
git push origin bugfix/fix-description
# GitHubでPull Request作成
```

### リリース管理
```bash
# リリースタグの作成
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHubでReleaseを作成
# 1. リポジトリページの「Releases」
# 2. 「Create a new release」
# 3. タグを選択してリリースノートを記述
```

## 📚 推奨する追加設定

### 1. GitHub Actions の活用
- ✅ CI/CD パイプライン（既に設定済み）
- 自動デプロイメント
- セキュリティスキャン
- 依存関係の自動更新

### 2. Issue テンプレート
- ✅ Bug Report（既に設定済み）
- ✅ Feature Request（既に設定済み）

### 3. プロジェクト管理
- GitHub Projects でタスク管理
- Milestones でリリース計画
- Labels でIssueの分類

### 4. コミュニティ機能
- ✅ Code of Conduct（既に設定済み）
- ✅ Contributing Guidelines（既に設定済み）
- ✅ Security Policy（既に設定済み）

## 🎯 公開後のチェックリスト

- [ ] リポジトリが正常に表示される
- [ ] README.md が適切にレンダリングされる
- [ ] CI/CD パイプラインが動作する
- [ ] Issue テンプレートが機能する
- [ ] Pull Request テンプレートが機能する
- [ ] ライセンスが表示される
- [ ] Topics が設定されている
- [ ] ブランチ保護ルールが有効

## 🔗 参考リンク

- [GitHub Docs](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**注意**: `your-username` を実際のGitHubユーザー名に置き換えることを忘れずに！