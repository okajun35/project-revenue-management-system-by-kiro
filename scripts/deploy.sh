#!/bin/bash
# プロジェクト収支システム - デプロイスクリプト

set -e

# 設定
PROJECT_NAME="project-revenue-system"
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
LOG_FILE="./deploy.log"

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# エラーハンドリング
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 前提条件チェック
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Docker確認
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed"
    fi
    
    # Docker Compose確認
    if ! command -v docker-compose &> /dev/null; then
        error_exit "Docker Compose is not installed"
    fi
    
    # 環境変数ファイル確認
    if [ ! -f ".env.production" ]; then
        error_exit ".env.production file not found"
    fi
    
    log "Prerequisites check passed"
}

# バックアップ作成
create_backup() {
    log "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    # データディレクトリのバックアップ
    if [ -d "./data" ]; then
        tar -czf "$BACKUP_FILE" ./data ./uploads 2>/dev/null || true
        log "Backup created: $BACKUP_FILE"
    else
        log "No data directory found, skipping backup"
    fi
}

# アプリケーションの停止
stop_application() {
    log "Stopping application..."
    
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q | grep -q .; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        log "Application stopped"
    else
        log "Application was not running"
    fi
}

# イメージのビルド
build_images() {
    log "Building Docker images..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    log "Docker images built successfully"
}

# アプリケーションの起動
start_application() {
    log "Starting application..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    log "Application started"
}

# ヘルスチェック
health_check() {
    log "Performing health check..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost/health &> /dev/null; then
            log "Health check passed"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, waiting..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    error_exit "Health check failed after $max_attempts attempts"
}

# クリーンアップ
cleanup() {
    log "Cleaning up old Docker images..."
    
    # 未使用のイメージを削除
    docker image prune -f
    
    # 古いバックアップを削除（30日以上古い）
    find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete 2>/dev/null || true
    
    log "Cleanup completed"
}

# メイン処理
main() {
    log "Starting deployment of $PROJECT_NAME"
    
    check_prerequisites
    create_backup
    stop_application
    build_images
    start_application
    health_check
    cleanup
    
    log "Deployment completed successfully"
    
    # デプロイ後の情報表示
    echo ""
    echo "=== Deployment Summary ==="
    echo "Project: $PROJECT_NAME"
    echo "Status: Running"
    echo "URL: http://localhost"
    echo "Health Check: http://localhost/health"
    echo "Logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "=========================="
}

# スクリプト実行
main "$@"