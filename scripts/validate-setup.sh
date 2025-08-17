#!/bin/bash
# プロジェクト収支システム - セットアップ検証スクリプト

set -e

# 色付きログ出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 検証結果
VALIDATION_ERRORS=0
VALIDATION_WARNINGS=0

# エラーカウント
increment_error() {
    VALIDATION_ERRORS=$((VALIDATION_ERRORS + 1))
}

increment_warning() {
    VALIDATION_WARNINGS=$((VALIDATION_WARNINGS + 1))
}

# Docker環境チェック
check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        increment_error
        return 1
    fi
    
    local docker_version
    docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    log_success "Docker version: $docker_version"
    
    # Docker daemon確認
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        increment_error
        return 1
    fi
    
    log_success "Docker daemon is running"
    return 0
}

# Docker Compose環境チェック
check_docker_compose() {
    log_info "Checking Docker Compose installation..."
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        increment_error
        return 1
    fi
    
    local compose_version
    compose_version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    log_success "Docker Compose version: $compose_version"
    
    return 0
}

# 必要ファイルの存在チェック
check_required_files() {
    log_info "Checking required files..."
    
    local required_files=(
        "Dockerfile"
        "docker-compose.yml"
        "docker-compose.prod.yml"
        "requirements.txt"
        "app.py"
        "config.py"
        "nginx/nginx.conf"
        "nginx/conf.d/default.conf"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "Found: $file"
        else
            log_error "Missing required file: $file"
            increment_error
        fi
    done
}

# 環境変数ファイルチェック
check_env_files() {
    log_info "Checking environment files..."
    
    if [ -f ".env.production" ]; then
        log_success "Found: .env.production"
        
        # 重要な環境変数の確認
        if grep -q "SECRET_KEY=change-this" .env.production; then
            log_warning "SECRET_KEY is still set to default value in .env.production"
            increment_warning
        fi
        
        if grep -q "FLASK_ENV=production" .env.production; then
            log_success "FLASK_ENV is set to production"
        else
            log_warning "FLASK_ENV is not set to production"
            increment_warning
        fi
    else
        log_warning "Missing .env.production file"
        increment_warning
    fi
}

# ディレクトリ構造チェック
check_directories() {
    log_info "Checking directory structure..."
    
    local required_dirs=(
        "app"
        "static"
        "nginx"
        "scripts"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "Found directory: $dir"
        else
            log_error "Missing directory: $dir"
            increment_error
        fi
    done
    
    # データディレクトリの作成
    if [ ! -d "data" ]; then
        log_info "Creating data directory..."
        mkdir -p data
        log_success "Created data directory"
    fi
    
    if [ ! -d "uploads" ]; then
        log_info "Creating uploads directory..."
        mkdir -p uploads
        log_success "Created uploads directory"
    fi
}

# Docker設定ファイルの構文チェック
check_docker_configs() {
    log_info "Validating Docker configuration files..."
    
    # docker-compose.yml構文チェック
    if docker-compose -f docker-compose.yml config &> /dev/null; then
        log_success "docker-compose.yml syntax is valid"
    else
        log_error "docker-compose.yml has syntax errors"
        increment_error
    fi
    
    # docker-compose.prod.yml構文チェック
    if docker-compose -f docker-compose.prod.yml config &> /dev/null; then
        log_success "docker-compose.prod.yml syntax is valid"
    else
        log_error "docker-compose.prod.yml has syntax errors"
        increment_error
    fi
}

# Nginx設定チェック
check_nginx_config() {
    log_info "Validating Nginx configuration..."
    
    # Nginx設定ファイルの構文チェック（Dockerコンテナ内で）
    if docker run --rm -v "$(pwd)/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" \
                       -v "$(pwd)/nginx/conf.d:/etc/nginx/conf.d:ro" \
                       nginx:alpine nginx -t &> /dev/null; then
        log_success "Nginx configuration is valid"
    else
        log_error "Nginx configuration has errors"
        increment_error
    fi
}

# ポート使用状況チェック
check_ports() {
    log_info "Checking port availability..."
    
    local ports=(80 443 5000)
    
    for port in "${ports[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            log_warning "Port $port is already in use"
            increment_warning
        else
            log_success "Port $port is available"
        fi
    done
}

# システムリソースチェック
check_system_resources() {
    log_info "Checking system resources..."
    
    # メモリチェック
    local total_mem
    total_mem=$(free -m | awk 'NR==2{print $2}')
    
    if [ "$total_mem" -lt 1024 ]; then
        log_warning "Low memory: ${total_mem}MB (recommended: 2GB+)"
        increment_warning
    else
        log_success "Memory: ${total_mem}MB"
    fi
    
    # ディスク容量チェック
    local disk_usage
    disk_usage=$(df . | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt 80 ]; then
        log_warning "High disk usage: ${disk_usage}%"
        increment_warning
    else
        log_success "Disk usage: ${disk_usage}%"
    fi
}

# 開発環境テスト
test_development_setup() {
    log_info "Testing development environment setup..."
    
    # 開発環境でのビルドテスト
    if docker-compose -f docker-compose.dev.yml build &> /dev/null; then
        log_success "Development build successful"
    else
        log_error "Development build failed"
        increment_error
        return 1
    fi
    
    # 開発環境での起動テスト（短時間）
    log_info "Testing development environment startup..."
    docker-compose -f docker-compose.dev.yml up -d &> /dev/null
    
    sleep 10
    
    # ヘルスチェック
    if curl -f http://localhost:5000/health &> /dev/null; then
        log_success "Development environment health check passed"
    else
        log_warning "Development environment health check failed"
        increment_warning
    fi
    
    # クリーンアップ
    docker-compose -f docker-compose.dev.yml down &> /dev/null
    log_info "Development environment test completed"
}

# 本番環境テスト
test_production_setup() {
    log_info "Testing production environment setup..."
    
    # 本番環境でのビルドテスト
    if docker-compose -f docker-compose.prod.yml build &> /dev/null; then
        log_success "Production build successful"
    else
        log_error "Production build failed"
        increment_error
        return 1
    fi
    
    log_success "Production environment validation completed"
}

# 結果サマリー表示
show_summary() {
    echo ""
    echo "=================================="
    echo "     VALIDATION SUMMARY"
    echo "=================================="
    
    if [ $VALIDATION_ERRORS -eq 0 ] && [ $VALIDATION_WARNINGS -eq 0 ]; then
        log_success "All validations passed! ✅"
        echo ""
        echo "Your Docker setup is ready for deployment."
        echo ""
        echo "Next steps:"
        echo "1. Review and update .env.production with your settings"
        echo "2. For development: docker-compose -f docker-compose.dev.yml up -d"
        echo "3. For production: ./scripts/deploy.sh"
        
    elif [ $VALIDATION_ERRORS -eq 0 ]; then
        log_warning "Validation completed with $VALIDATION_WARNINGS warning(s) ⚠️"
        echo ""
        echo "Your setup is functional but please review the warnings above."
        
    else
        log_error "Validation failed with $VALIDATION_ERRORS error(s) and $VALIDATION_WARNINGS warning(s) ❌"
        echo ""
        echo "Please fix the errors above before proceeding with deployment."
        exit 1
    fi
}

# メイン処理
main() {
    echo "=================================="
    echo "  Docker Setup Validation"
    echo "  プロジェクト収支システム"
    echo "=================================="
    echo ""
    
    check_docker
    check_docker_compose
    check_required_files
    check_env_files
    check_directories
    check_docker_configs
    check_nginx_config
    check_ports
    check_system_resources
    
    # テスト実行（オプション）
    if [ "${1:-}" = "--test" ]; then
        test_development_setup
        test_production_setup
    fi
    
    show_summary
}

# 使用方法
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --test    Run build and startup tests"
    echo "  --help    Show this help message"
    exit 0
}

# コマンドライン引数処理
case "${1:-}" in
    --help)
        usage
        ;;
    *)
        main "$@"
        ;;
esac