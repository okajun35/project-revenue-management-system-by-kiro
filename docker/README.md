# Docker設定

このディレクトリには、Docker関連の設定ファイルが含まれています。

## 📋 ディレクトリ構造

```
docker/
├── dev/                    # 開発環境用
│   └── docker-compose.dev.yml
├── prod/                   # 本番環境用
│   ├── docker-compose.prod.yml
│   └── Dockerfile.dev
└── README.md              # このファイル
```

## 🚀 使用方法

### 開発環境
```bash
# 開発環境起動
docker-compose -f docker/dev/docker-compose.dev.yml up -d

# または Makefile使用
make docker-dev
```

### 本番環境
```bash
# 本番環境起動
docker-compose -f docker/prod/docker-compose.prod.yml up -d

# または Makefile使用
make docker-prod
```

### プロジェクトルートのDocker設定

プロジェクトルートにある主要なDockerファイル：
- `Dockerfile` - メインのDockerイメージ定義
- `docker-compose.yml` - 基本のDocker Compose設定
- `.dockerignore` - Dockerビルド時の除外ファイル

## 🔧 設定詳細

### 開発環境の特徴
- ホットリロード対応
- デバッグモード有効
- 開発用ポート設定
- ボリュームマウントでコード変更反映

### 本番環境の特徴
- 最適化されたイメージ
- セキュリティ強化
- Nginx リバースプロキシ
- ログ管理
- ヘルスチェック

## 📊 監視・ログ

### ログ確認
```bash
# 開発環境
docker-compose -f docker/dev/docker-compose.dev.yml logs -f

# 本番環境
docker-compose -f docker/prod/docker-compose.prod.yml logs -f

# Makefile使用
make docker-logs
```

### ヘルスチェック
```bash
# アプリケーション状態確認
curl http://localhost:5000/health

# 本番環境（Nginx経由）
curl http://localhost/health
```

## 🛠️ トラブルシューティング

### よくある問題

**ポート競合**
```bash
# 使用中のポートを確認
netstat -tulpn | grep :5000

# コンテナ停止
docker-compose down
```

**イメージ更新**
```bash
# イメージ再ビルド
docker-compose build --no-cache

# 古いイメージ削除
docker image prune
```

**ボリューム問題**
```bash
# ボリューム確認
docker volume ls

# ボリューム削除
docker volume prune
```

## 🔒 セキュリティ

### 本番環境での注意点
- 環境変数でシークレット管理
- 非rootユーザーでの実行
- 最小権限の原則
- 定期的なイメージ更新

### セキュリティスキャン
```bash
# イメージの脆弱性スキャン
docker scan your-image:tag

# Dockerfileのベストプラクティスチェック
docker run --rm -i hadolint/hadolint < Dockerfile
```