#!/bin/bash
# プロジェクト収支システム - バックアップスクリプト

set -e

# 設定
BACKUP_DIR="./backups"
DATA_DIR="./data"
UPLOADS_DIR="./uploads"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}
LOG_FILE="./backup.log"

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# バックアップディレクトリ作成
mkdir -p "$BACKUP_DIR"

# バックアップファイル名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

log "Starting backup process..."

# データベースとファイルのバックアップ
if [ -d "$DATA_DIR" ] || [ -d "$UPLOADS_DIR" ]; then
    log "Creating backup archive: $BACKUP_FILE"
    
    # バックアップ対象を確認
    BACKUP_TARGETS=""
    if [ -d "$DATA_DIR" ]; then
        BACKUP_TARGETS="$BACKUP_TARGETS $DATA_DIR"
        log "Including data directory: $DATA_DIR"
    fi
    
    if [ -d "$UPLOADS_DIR" ]; then
        BACKUP_TARGETS="$BACKUP_TARGETS $UPLOADS_DIR"
        log "Including uploads directory: $UPLOADS_DIR"
    fi
    
    # アーカイブ作成
    tar -czf "$BACKUP_FILE" $BACKUP_TARGETS
    
    # バックアップサイズ確認
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup created successfully: $BACKUP_FILE ($BACKUP_SIZE)"
    
else
    log "No data directories found to backup"
    exit 1
fi

# 古いバックアップの削除
log "Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null || true

# バックアップ一覧表示
log "Current backups:"
ls -lh "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null || log "No backup files found"

log "Backup process completed"

# バックアップ検証
if [ -f "$BACKUP_FILE" ]; then
    log "Verifying backup integrity..."
    if tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
        log "Backup verification successful"
        echo "$BACKUP_FILE"  # 成功時はファイルパスを出力
    else
        log "ERROR: Backup verification failed"
        exit 1
    fi
else
    log "ERROR: Backup file not created"
    exit 1
fi