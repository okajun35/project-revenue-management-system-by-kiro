#!/usr/bin/env python3
"""
プロジェクト収支システム - Docker セットアップテスト
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def run_command(command, capture_output=True, timeout=60):
    """コマンド実行"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_docker_installation():
    """Docker インストール確認"""
    print("🔍 Checking Docker installation...")
    
    success, stdout, stderr = run_command("docker --version")
    if not success:
        print("❌ Docker is not installed or not accessible")
        return False
    
    print(f"✅ Docker found: {stdout.strip()}")
    
    # Docker daemon確認
    success, _, _ = run_command("docker info")
    if not success:
        print("❌ Docker daemon is not running")
        return False
    
    print("✅ Docker daemon is running")
    return True

def check_docker_compose():
    """Docker Compose確認"""
    print("🔍 Checking Docker Compose...")
    
    success, stdout, stderr = run_command("docker-compose --version")
    if not success:
        print("❌ Docker Compose is not installed")
        return False
    
    print(f"✅ Docker Compose found: {stdout.strip()}")
    return True

def check_required_files():
    """必要ファイル確認"""
    print("🔍 Checking required files...")
    
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.prod.yml",
        "docker-compose.dev.yml",
        "requirements.txt",
        "app.py",
        "config.py",
        "nginx/nginx.conf",
        "nginx/conf.d/default.conf",
        ".env.production"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ Found: {file_path}")
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    return True

def validate_docker_compose_configs():
    """Docker Compose設定検証"""
    print("🔍 Validating Docker Compose configurations...")
    
    configs = [
        "docker-compose.yml",
        "docker-compose.dev.yml", 
        "docker-compose.prod.yml"
    ]
    
    for config in configs:
        print(f"   Checking {config}...")
        success, _, stderr = run_command(f"docker-compose -f {config} config")
        if not success:
            print(f"❌ {config} has syntax errors: {stderr}")
            return False
        print(f"✅ {config} syntax is valid")
    
    return True

def test_development_build():
    """開発環境ビルドテスト"""
    print("🔍 Testing development environment build...")
    
    # 既存コンテナのクリーンアップ
    run_command("docker-compose -f docker-compose.dev.yml down", capture_output=False)
    
    # ビルド実行
    success, stdout, stderr = run_command(
        "docker-compose -f docker-compose.dev.yml build", 
        timeout=300
    )
    
    if not success:
        print(f"❌ Development build failed: {stderr}")
        return False
    
    print("✅ Development build successful")
    return True

def test_development_startup():
    """開発環境起動テスト"""
    print("🔍 Testing development environment startup...")
    
    # 起動
    success, _, stderr = run_command(
        "docker-compose -f docker-compose.dev.yml up -d",
        timeout=120
    )
    
    if not success:
        print(f"❌ Development startup failed: {stderr}")
        return False
    
    print("✅ Development environment started")
    
    # ヘルスチェック待機
    print("   Waiting for application to be ready...")
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed")
                health_data = response.json()
                print(f"   Status: {health_data.get('status')}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(2)
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
    
    print("❌ Health check failed after 30 attempts")
    
    # ログ出力
    print("📋 Container logs:")
    run_command("docker-compose -f docker-compose.dev.yml logs --tail=20", capture_output=False)
    
    return False

def cleanup_development():
    """開発環境クリーンアップ"""
    print("🧹 Cleaning up development environment...")
    run_command("docker-compose -f docker-compose.dev.yml down", capture_output=False)
    print("✅ Development environment cleaned up")

def test_production_build():
    """本番環境ビルドテスト"""
    print("🔍 Testing production environment build...")
    
    # 既存コンテナのクリーンアップ
    run_command("docker-compose -f docker-compose.prod.yml down", capture_output=False)
    
    # ビルド実行
    success, stdout, stderr = run_command(
        "docker-compose -f docker-compose.prod.yml build",
        timeout=300
    )
    
    if not success:
        print(f"❌ Production build failed: {stderr}")
        return False
    
    print("✅ Production build successful")
    return True

def show_summary(results):
    """結果サマリー表示"""
    print("\n" + "="*50)
    print("           TEST SUMMARY")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("-" * 50)
    print(f"Total: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! Your Docker setup is ready.")
        print("\nNext steps:")
        print("1. Review .env.production settings")
        print("2. Run: docker-compose -f docker-compose.dev.yml up -d")
        print("3. Access: http://localhost:5000")
        return True
    else:
        print(f"\n❌ {failed_tests} test(s) failed. Please fix the issues above.")
        return False

def main():
    """メイン処理"""
    print("🚀 プロジェクト収支システム - Docker セットアップテスト")
    print("="*60)
    
    results = {}
    
    # 基本チェック
    results["Docker Installation"] = check_docker_installation()
    results["Docker Compose"] = check_docker_compose()
    results["Required Files"] = check_required_files()
    results["Docker Compose Configs"] = validate_docker_compose_configs()
    
    # 基本チェックが失敗した場合は終了
    if not all([results["Docker Installation"], results["Docker Compose"], 
                results["Required Files"], results["Docker Compose Configs"]]):
        show_summary(results)
        return False
    
    # ビルドテスト
    results["Development Build"] = test_development_build()
    results["Production Build"] = test_production_build()
    
    # 起動テスト（開発環境のみ）
    if results["Development Build"]:
        results["Development Startup"] = test_development_startup()
        cleanup_development()
    else:
        results["Development Startup"] = False
    
    # 結果表示
    success = show_summary(results)
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        cleanup_development()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        cleanup_development()
        sys.exit(1)