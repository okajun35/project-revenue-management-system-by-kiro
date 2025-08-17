#!/bin/sh
# プロジェクト収支システム - ログローテーションスクリプト

LOG_DIR="/app/logs"
NGINX_LOG_DIR="/var/log/nginx"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

echo "$(date): Starting log rotation..."

# アプリケーションログのローテーション
if [ -d "$LOG_DIR" ]; then
    find "$LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS -delete
    echo "$(date): Rotated application logs older than $RETENTION_DAYS days"
fi

# Nginxログのローテーション
if [ -d "$NGINX_LOG_DIR" ]; then
    find "$NGINX_LOG_DIR" -name "*.log" -type f -mtime +$RETENTION_DAYS -delete
    echo "$(date): Rotated nginx logs older than $RETENTION_DAYS days"
fi

# ログファイルの圧縮
find "$LOG_DIR" -name "*.log" -type f -mtime +1 -exec gzip {} \;
find "$NGINX_LOG_DIR" -name "*.log" -type f -mtime +1 -exec gzip {} \;

echo "$(date): Log rotation completed"