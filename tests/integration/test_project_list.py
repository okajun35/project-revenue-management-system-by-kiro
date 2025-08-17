#!/usr/bin/env python3
"""
プロジェクト一覧機能のテスト用データ作成スクリプト
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Project

def create_test_data():
    """テスト用のプロジェクトデータを作成"""
    app = create_app()
    
    with app.app_context():
        # 既存のデータをクリア
        Project.query.delete()
        db.session.commit()
        
        # テストデータを作成
        test_projects = [
            {
                'project_code': 'PRJ001',
                'project_name': 'Webシステム開発プロジェクト',
                'fiscal_year': 2024,
                'order_probability': 100,
                'revenue': 5000000,
                'expenses': 3500000
            },
            {
                'project_code': 'PRJ002',
                'project_name': 'モバイルアプリ開発',
                'fiscal_year': 2024,
                'order_probability': 50,
                'revenue': 3000000,
                'expenses': 2200000
            },
            {
                'project_code': 'PRJ003',
                'project_name': 'データ分析システム',
                'fiscal_year': 2023,
                'order_probability': 0,
                'revenue': 2500000,
                'expenses': 2800000
            },
            {
                'project_code': 'PRJ004',
                'project_name': 'ECサイト構築',
                'fiscal_year': 2024,
                'order_probability': 100,
                'revenue': 8000000,
                'expenses': 5500000
            },
            {
                'project_code': 'PRJ005',
                'project_name': 'AI機械学習プロジェクト',
                'fiscal_year': 2025,
                'order_probability': 50,
                'revenue': 12000000,
                'expenses': 8500000
            },
            {
                'project_code': 'PRJ006',
                'project_name': 'クラウド移行プロジェクト',
                'fiscal_year': 2024,
                'order_probability': 100,
                'revenue': 6500000,
                'expenses': 4200000
            },
            {
                'project_code': 'PRJ007',
                'project_name': 'セキュリティ強化プロジェクト',
                'fiscal_year': 2023,
                'order_probability': 0,
                'revenue': 1800000,
                'expenses': 1900000
            },
            {
                'project_code': 'PRJ008',
                'project_name': 'IoTシステム開発',
                'fiscal_year': 2025,
                'order_probability': 50,
                'revenue': 9500000,
                'expenses': 6800000
            },
            {
                'project_code': 'PRJ009',
                'project_name': 'ブロックチェーン研究',
                'fiscal_year': 2024,
                'order_probability': 0,
                'revenue': 4200000,
                'expenses': 4500000
            },
            {
                'project_code': 'PRJ010',
                'project_name': 'レガシーシステム更新',
                'fiscal_year': 2025,
                'order_probability': 100,
                'revenue': 15000000,
                'expenses': 11000000
            }
        ]
        
        for project_data in test_projects:
            try:
                project = Project.create_with_validation(**project_data)
                print(f"作成: {project.project_code} - {project.project_name}")
            except Exception as e:
                print(f"エラー: {project_data['project_code']} - {e}")
        
        print(f"\n合計 {Project.query.count()} 件のプロジェクトを作成しました。")

if __name__ == '__main__':
    create_test_data()