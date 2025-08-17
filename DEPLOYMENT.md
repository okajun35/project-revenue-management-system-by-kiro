# プロジェクト収支システム - デプロイメントガイド

## 概要

このドキュメントでは、プロジェクト収支システムのDocker化とデプロイメント手順について説明します。

## 前提条件

- Docker Engine 20.10以上
- Docker Compose 2.0以上
- 本番環境では最低2GB RAM、2CPU推奨

## ファイル構成

```
project-revenue-system/
├── Dockerfile                 # 本番用Dockerファイル
├── Dockerfile.dev            # 開発用Dockerファイル
├── docker-compose.yml        # 基本Docker Compose設定
├── docker-compose.prod.yml   # 本番環境用設定
├── docker-compose.dev.yml    # 開発環境用設定
├── .env.production           # 本番環境変数テンプレート
├── nginx/                    # Nginx設定
│   ├── nginx.conf           # メイン設定
│   └── conf.d/
│       └── default.conf     # サイト設定
└── scripts/                  # デプロイメントスクリプト
    ├── deploy.sh            # デプロイスクリプト
    ├── backup.sh            # バックアップスクリプト
    ├── restore.sh           # リストアスクリプト
    └── logrotate.sh         # ログローテーション
```

## 開発環境での起動

### 1. 開発用コンテナの起動

```bash
# 開発環境用Docker Composeで起動
docker-compose -f docker-compose.dev.yml up -d

# ログ確認
docker-compose -f docker-compose.dev.yml logs -f web
```

### 2. アクセス確認

- アプリケーション: http://localhost:5000
- Nginx経由: http://localhost:8080
- ヘルスチェック: http://localhost:5000/health

### 3. 開発環境の停止

```bash
docker-compose -f docker-compose.dev.yml down
```

## 本番環境でのデプロイ

### 1. 環境設定

```bash
# 本番環境用の環境変数を設定
cp .env.production .env
# .envファイルを編集して本番用の値を設定
```

重要な環境変数:
- `SECRET_KEY`: ランダムな秘密鍵（必須）
- `FLASK_ENV=production`
- `DATABASE_URL`: データベース接続文字列

### 2. SSL証明書の配置（HTTPS用）

```bash
# SSL証明書ディレクトリを作成
mkdir -p nginx/ssl

# 証明書ファイルを配置
# nginx/ssl/cert.pem (証明書)
# nginx/ssl/key.pem (秘密鍵)
```

### 3. 本番環境の起動

#### 自動デプロイスクリプト使用（Linux/Mac）

```bash
# デプロイスクリプトに実行権限を付与
chmod +x scripts/*.sh

# デプロイ実行
./scripts/deploy.sh
```

#### 手動デプロイ（Windows/Linux/Mac）

```bash
# イメージビルド
docker-compose -f docker-compose.prod.yml build

# コンテナ起動
docker-compose -f docker-compose.prod.yml up -d

# ヘルスチェック
curl http://localhost/health
```

### 4. 本番環境の確認

- アプリケーション: http://localhost (または設定したドメイン)
- HTTPS: https://localhost (SSL証明書設定時)
- ヘルスチェック: http://localhost/health

## バックアップとリストア

### バックアップ作成

#### 自動バックアップ（Linux/Mac）

```bash
# バックアップスクリプト実行
./scripts/backup.sh
```

#### 手動バックアップ

```bash
# データディレクトリのバックアップ
mkdir -p backups
tar -czf backups/backup_$(date +%Y%m%d_%H%M%S).tar.gz data uploads
```

### リストア実行

#### 自動リストア（Linux/Mac）

```bash
# リストアスクリプト実行
./scripts/restore.sh backups/backup_20241212_120000.tar.gz
```

#### 手動リストア

```bash
# アプリケーション停止
docker-compose -f docker-compose.prod.yml down

# データリストア
tar -xzf backups/backup_20241212_120000.tar.gz

# アプリケーション再起動
docker-compose -f docker-compose.prod.yml up -d
```

## 監視とメンテナンス

### ログ確認

```bash
# アプリケーションログ
docker-compose -f docker-compose.prod.yml logs -f web

# Nginxログ
docker-compose -f docker-compose.prod.yml logs -f nginx

# 全サービスのログ
docker-compose -f docker-compose.prod.yml logs -f
```

### ヘルスチェック

```bash
# ヘルスチェックエンドポイント
curl -f http://localhost/health

# コンテナ状態確認
docker-compose -f docker-compose.prod.yml ps

# リソース使用量確認
docker stats
```

### アップデート手順

```bash
# 1. 現在のデータをバックアップ
./scripts/backup.sh

# 2. 新しいコードを取得
git pull origin main

# 3. 再デプロイ
./scripts/deploy.sh
```

## トラブルシューティング

### よくある問題

#### 1. コンテナが起動しない

```bash
# ログ確認
docker-compose -f docker-compose.prod.yml logs web

# 設定確認
docker-compose -f docker-compose.prod.yml config
```

#### 2. データベース接続エラー

```bash
# データディレクトリの権限確認
ls -la data/

# データベースファイル確認
docker-compose -f docker-compose.prod.yml exec web ls -la /app/data/
```

#### 3. 静的ファイルが表示されない

```bash
# 静的ファイルディレクトリ確認
ls -la static/

# Nginx設定確認
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

### パフォーマンス最適化

#### 1. リソース制限調整

`docker-compose.prod.yml`の`deploy.resources`セクションを調整:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # CPU制限
      memory: 2G       # メモリ制限
    reservations:
      cpus: '1.0'      # CPU予約
      memory: 1G       # メモリ予約
```

#### 2. ワーカープロセス数調整

Dockerfileの`CMD`を調整:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "--timeout", "120", "app:app"]
```

## セキュリティ設定

### 1. 環境変数の保護

```bash
# .envファイルの権限設定
chmod 600 .env.production
```

### 2. SSL/TLS設定

nginx/conf.d/default.confでSSL設定を有効化:

```nginx
# SSL設定を有効にする
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

### 3. ファイアウォール設定

```bash
# 必要なポートのみ開放
# HTTP: 80
# HTTPS: 443
# SSH: 22 (管理用)
```

## 定期メンテナンス

### 日次タスク

- ログローテーション（自動）
- ヘルスチェック確認
- バックアップ作成

### 週次タスク

- システムリソース確認
- ログ分析
- セキュリティアップデート確認

### 月次タスク

- 古いバックアップ削除
- パフォーマンス分析
- 容量使用量確認

## サポート

問題が発生した場合は、以下の情報を収集してください:

1. エラーログ
2. システム情報
3. 再現手順
4. 環境設定

```bash
# システム情報収集
docker version
docker-compose version
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs --tail=100
```