#!/bin/bash
# プロジェクト収支システム - リストアスクリプト

set -e

# 設定
BACKUP_DIR="./backups"
LOG_FILE="./restore.log"

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# エラーハンドリング
error_exit() {
    log "ERROR: $1"
    exit 1
}

# 使用方法表示
usage() {
    echo "Usage: $0 <backup_file>"
    echo "Example: $0 ./backups/backup_20241212_120000.tar.gz"
    echo ""
    echo "Available backups:"
    ls -1 "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null || echo "No backup files found"
    exit 1
}

# 引数チェック
if [ $# -ne 1 ]; then
    usage
fi

BACKUP_FILE="$1"

# バックアップファイル存在チェック
if [ ! -f "$BACKUP_FILE" ]; then
    error_exit "Backup file not found: $BACKUP_FILE"
fi

log "Starting restore process from: $BACKUP_FILE"

# バックアップファイル検証
log "Verifying backup file integrity..."
if ! tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    error_exit "Backup file is corrupted or invalid"
fi
log "Backup file verification successful"

# 確認プロンプト
echo ""
echo "WARNING: This will overwrite existing data!"
echo "Backup file: $BACKUP_FILE"
echo "Current data will be backed up before restore."
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

# 現在のデータをバックアップ
log "Creating backup of current data before restore..."
CURRENT_BACKUP="./backups/pre_restore_$(date +%Y%m%d_%H%M%S).tar.gz"

if [ -d "./data" ] || [ -d "./uploads" ]; then
    BACKUP_TARGETS=""
    [ -d "./data" ] && BACKUP_TARGETS="$BACKUP_TARGETS ./data"
    [ -d "./uploads" ] && BACKUP_TARGETS="$BACKUP_TARGETS ./uploads"
    
    tar -czf "$CURRENT_BACKUP" $BACKUP_TARGETS 2>/dev/null || true
    log "Current data backed up to: $CURRENT_BACKUP"
fi

# アプリケーション停止
log "Stopping application..."
if docker-compose ps -q | grep -q .; then
    docker-compose down
    log "Application stopped"
fi

# 既存データの削除
log "Removing existing data..."
[ -d "./data" ] && rm -rf "./data"
[ -d "./uploads" ] && rm -rf "./uploads"

# バックアップからリストア
log "Restoring data from backup..."
tar -xzf "$BACKUP_FILE"
log "Data restored successfully"

# 権限設定
log "Setting proper permissions..."
[ -d "./data" ] && chmod -R 755 "./data"
[ -d "./uploads" ] && chmod -R 755 "./uploads"

# アプリケーション起動
log "Starting application..."
docker-compose up -d
log "Application started"

# ヘルスチェック
log "Performing health check..."
sleep 10

max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost/health &> /dev/null; then
        log "Health check passed - restore completed successfully"
        break
    fi
    
    log "Health check attempt $attempt/$max_attempts..."
    sleep 10
    attempt=$((attempt + 1))
done

if [ $attempt -gt $max_attempts ]; then
    log "WARNING: Health check failed, but restore process completed"
    log "Please check application logs: docker-compose logs"
fi

log "Restore process completed"

echo ""
echo "=== Restore Summary ==="
echo "Restored from: $BACKUP_FILE"
echo "Pre-restore backup: $CURRENT_BACKUP"
echo "Application URL: http://localhost"
echo "Health Check: http://localhost/health"
echo "===================="