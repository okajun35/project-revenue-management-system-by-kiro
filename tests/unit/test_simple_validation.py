#!/usr/bin/env python3
"""
簡単なバリデーションテスト
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Project, ValidationError


def test_simple_validation():
    """簡単なバリデーションテスト"""
    print("=== 簡単なバリデーションテスト ===")
    
    app = create_app()
    with app.app_context():
        # データベース初期化
        db.create_all()
        
        # 既存データをクリア
        Project.query.delete()
        db.session.commit()
        
        # 正常なプロジェクト作成テスト
        print("\n1. 正常なプロジェクト作成テスト")
        try:
            project = Project.create_with_validation(
                project_code='SIMPLE-2024-001',
                project_name='簡単テストプロジェクト',
                fiscal_year=2024,
                order_probability=50,  # △（中）
                revenue=1000000.00,
                expenses=800000.00
            )
            print(f"✓ プロジェクト作成成功: {project.project_name}")
            print(f"  粗利: {project.gross_profit}")
            
        except ValidationError as e:
            print(f"✗ プロジェクト作成失敗: {e.message}")
        
        # バリデーションエラーテスト
        print("\n2. バリデーションエラーテスト")
        try:
            invalid_project = Project.create_with_validation(
                project_code='',  # 空のコード
                project_name='エラーテスト',
                fiscal_year=1800,  # 範囲外
                order_probability=25,  # 無効な値（0, 50, 100以外）
                revenue=-1000,  # 負の値
                expenses=500000.00
            )
            print("✗ バリデーションエラーが検出されませんでした")
            
        except ValidationError as e:
            print(f"✓ バリデーションエラー正常検出: {e.message}")
        
        # 重複チェックテスト
        print("\n3. 重複チェックテスト")
        try:
            duplicate_project = Project.create_with_validation(
                project_code='SIMPLE-2024-001',  # 既存のコード
                project_name='重複テスト',
                fiscal_year=2024,
                order_probability=100,  # 〇（高）
                revenue=500000.00,
                expenses=400000.00
            )
            print("✗ 重複チェックが機能していません")
            
        except ValidationError as e:
            print(f"✓ 重複チェック正常動作: {e.message}")
        
        print("\n=== テスト完了 ===")


if __name__ == '__main__':
    test_simple_validation()