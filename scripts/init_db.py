#!/usr/bin/env python3
"""
データベース初期化スクリプト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加（scripts の親ディレクトリ）
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import Project, Branch, FiscalYear

def init_database():
    """データベースを初期化"""
    app = create_app()
    
    with app.app_context():
        print("データベースを初期化中...")
        
        # 既存のテーブルを削除（開発環境のみ）
        if os.environ.get('FLASK_ENV') == 'development':
            db.drop_all()
            print("既存のテーブルを削除しました")
        
        # テーブルを作成
        db.create_all()
        print("テーブルを作成しました")
        
        # サンプルデータを挿入（開発環境のみ）
        if os.environ.get('FLASK_ENV') == 'development':
            create_sample_data()
        
        print("データベースの初期化が完了しました")

def create_sample_data():
    """サンプルデータを作成"""
    try:
        # 支社サンプルデータを作成
        sample_branches = [
            {'branch_code': 'TKY', 'branch_name': '東京本社'},
            {'branch_code': 'OSK', 'branch_name': '大阪支社'},
            {'branch_code': 'NGY', 'branch_name': '名古屋支社'},
            {'branch_code': 'FKK', 'branch_name': '福岡支社'}
        ]
        
        branches = {}
        for branch_data in sample_branches:
            branch = Branch.create_with_validation(**branch_data)
            branches[branch_data['branch_code']] = branch
            print(f"支社を作成: {branch.branch_name}")
        
        # 年度マスターサンプルデータを作成
        sample_fiscal_years = [
            {'year': 2023, 'year_name': '2023年度'},
            {'year': 2024, 'year_name': '2024年度'},
            {'year': 2025, 'year_name': '2025年度'}
        ]
        
        fiscal_years = {}
        for fiscal_year_data in sample_fiscal_years:
            fiscal_year = FiscalYear.create_with_validation(**fiscal_year_data)
            fiscal_years[fiscal_year_data['year']] = fiscal_year
            print(f"年度を作成: {fiscal_year.year_name}")
        
        # プロジェクトサンプルデータを作成
        sample_projects = [
            {
                'project_code': 'PRJ-2024-001',
                'project_name': 'Webシステム開発プロジェクト',
                'branch_id': branches['TKY'].id,
                'fiscal_year': 2024,
                'order_probability': 100.0,
                'revenue': 5000000,
                'expenses': 3500000
            },
            {
                'project_code': 'PRJ-2024-002',
                'project_name': 'モバイルアプリ開発',
                'branch_id': branches['OSK'].id,
                'fiscal_year': 2024,
                'order_probability': 50.0,
                'revenue': 3000000,
                'expenses': 2100000
            },
            {
                'project_code': 'PRJ-2023-015',
                'project_name': 'データ分析システム',
                'branch_id': branches['TKY'].id,
                'fiscal_year': 2023,
                'order_probability': 100.0,
                'revenue': 8000000,
                'expenses': 5200000
            },
            {
                'project_code': 'PRJ-2024-003',
                'project_name': 'ECサイト構築',
                'branch_id': branches['NGY'].id,
                'fiscal_year': 2024,
                'order_probability': 100.0,
                'revenue': 4500000,
                'expenses': 3200000
            },
            {
                'project_code': 'PRJ-2025-001',
                'project_name': 'AI導入プロジェクト',
                'branch_id': branches['FKK'].id,
                'fiscal_year': 2025,
                'order_probability': 50.0,
                'revenue': 12000000,
                'expenses': 8500000
            },
            {
                'project_code': 'PRJ-2024-004',
                'project_name': 'インフラ更新',
                'branch_id': branches['OSK'].id,
                'fiscal_year': 2024,
                'order_probability': 0.0,
                'revenue': 2500000,
                'expenses': 2800000
            }
        ]
        
        for project_data in sample_projects:
            project = Project.create_with_validation(**project_data)
            print(f"プロジェクトを作成: {project.project_name} ({project.project_code})")
        
        print(f"✓ 支社サンプルデータを作成: {len(sample_branches)}件")
        print(f"✓ 年度マスターサンプルデータを作成: {len(sample_fiscal_years)}件")
        print(f"✓ プロジェクトサンプルデータを作成: {len(sample_projects)}件")
        
    except Exception as e:
        db.session.rollback()
        print(f"サンプルデータの作成に失敗しました: {e}")
        raise

if __name__ == '__main__':
    init_database()