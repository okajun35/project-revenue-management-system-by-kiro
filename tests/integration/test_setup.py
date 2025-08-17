#!/usr/bin/env python3
"""
簡単なセットアップテスト
"""
import os
import sys
from pathlib import Path

def test_basic_setup():
    """基本的なセットアップをテスト"""
    print("プロジェクト基盤のテストを開始...")
    
    # 必要なディレクトリを作成
    data_dir = Path('data')
    uploads_dir = Path('uploads')
    
    data_dir.mkdir(exist_ok=True)
    uploads_dir.mkdir(exist_ok=True)
    
    print(f"✓ データディレクトリを作成: {data_dir}")
    print(f"✓ アップロードディレクトリを作成: {uploads_dir}")
    
    # 設定ファイルの存在確認
    required_files = [
        'requirements.txt',
        'config.py',
        'app.py',
        'init_db.py',
        'app/__init__.py',
        'app/models.py',
        'app/routes.py'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ ファイル存在確認: {file_path}")
        else:
            print(f"✗ ファイルが見つかりません: {file_path}")
            return False
    
    print("\n基本的なセットアップテストが完了しました！")
    return True

if __name__ == '__main__':
    success = test_basic_setup()
    sys.exit(0 if success else 1)