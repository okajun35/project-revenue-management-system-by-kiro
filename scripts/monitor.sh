#!/bin/bash
# プロジェクト収支システム - 監視スクリプト

set -e

# 設定
HEALTH_URL="http://localhost/health"
LOG_FILE="./monitor.log"
ALERT_EMAIL=""  # アラート送信先メールアドレス（設定する場合）

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# アラート送信関数
send_alert() {
    local message="$1"
    log "ALERT: $message"
    
    # メール送信（mailコマンドが利用可能な場合）
    if [ -n "$ALERT_EMAIL" ] && command -v mail &> /dev/null; then
        echo "$message" | mail -s "プロジェクト収支システム アラート" "$ALERT_EMAIL"
    fi
}

# ヘルスチェック
check_health() {
    local response
    local http_code
    
    log "Performing health check..."
    
    # HTTPリクエスト実行
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$HEALTH_URL" 2>/dev/null || echo "HTTPSTATUS:000")
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]*$//')
    
    if [ "$http_code" = "200" ]; then
        log "Health check passed (HTTP $http_code)"
        return 0
    else
        log "Health check failed (HTTP $http_code)"
        send_alert "Health check failed with HTTP code: $http_code"
        return 1
    fi
}

# コンテナ状態チェック
check_containers() {
    log "Checking container status..."
    
    # Docker Composeサービス状態確認
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log "Some containers are not running"
        send_alert "One or more containers are not running"
        return 1
    fi
    
    log "All containers are running"
    return 0
}

# ディスク使用量チェック
check_disk_usage() {
    log "Checking disk usage..."
    
    local usage
    usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -gt 90 ]; then
        log "Disk usage is high: ${usage}%"
        send_alert "Disk usage is critically high: ${usage}%"
        return 1
    elif [ "$usage" -gt 80 ]; then
        log "Disk usage warning: ${usage}%"
        return 0
    fi
    
    log "Disk usage is normal: ${usage}%"
    return 0
}

# メモリ使用量チェック
check_memory_usage() {
    log "Checking memory usage..."
    
    local usage
    usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$usage" -gt 90 ]; then
        log "Memory usage is high: ${usage}%"
        send_alert "Memory usage is critically high: ${usage}%"
        return 1
    elif [ "$usage" -gt 80 ]; then
        log "Memory usage warning: ${usage}%"
        return 0
    fi
    
    log "Memory usage is normal: ${usage}%"
    return 0
}

# ログファイルサイズチェック
check_log_sizes() {
    log "Checking log file sizes..."
    
    local large_logs
    large_logs=$(find ./logs -name "*.log" -size +100M 2>/dev/null || true)
    
    if [ -n "$large_logs" ]; then
        log "Large log files detected:"
        echo "$large_logs" | while read -r logfile; do
            log "  - $logfile"
        done
        send_alert "Large log files detected, consider log rotation"
    fi
}

# メイン監視処理
main() {
    log "Starting system monitoring..."
    
    local exit_code=0
    
    # 各チェック実行
    check_health || exit_code=1
    check_containers || exit_code=1
    check_disk_usage || exit_code=1
    check_memory_usage || exit_code=1
    check_log_sizes
    
    if [ $exit_code -eq 0 ]; then
        log "All checks passed"
    else
        log "Some checks failed"
    fi
    
    log "Monitoring completed"
    return $exit_code
}

# 使用方法表示
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -c, --continuous    Run monitoring continuously (every 5 minutes)"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 Run monitoring once"
    echo "  $0 -c              Run monitoring continuously"
    exit 0
}

# 継続監視モード
continuous_monitoring() {
    log "Starting continuous monitoring mode..."
    
    while true; do
        main
        log "Waiting 5 minutes before next check..."
        sleep 300  # 5分待機
    done
}

# コマンドライン引数処理
case "${1:-}" in
    -c|--continuous)
        continuous_monitoring
        ;;
    -h|--help)
        usage
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        usage
        ;;
esac