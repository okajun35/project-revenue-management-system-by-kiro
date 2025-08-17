#!/usr/bin/env python3
"""
プロジェクト収支システム - 本番環境用サンプルデータ作成スクリプト
"""

import sys
from pathlib import Path
from datetime import datetime, date

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import Branch, FiscalYear, Project

def create_sample_data():
    """本番環境用サンプルデータ作成"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Creating sample data for production environment...")
        
        # 既存データの確認
        existing_projects = Project.query.count()
        existing_branches = Branch.query.count()
        existing_fiscal_years = FiscalYear.query.count()
        
        print(f"Current data: {existing_projects} projects, {existing_branches} branches, {existing_fiscal_years} fiscal years")
        
        # 支社データ作成（存在しない場合のみ）
        branches_data = [
            {'branch_name': '東京本社', 'branch_code': 'TKY'},
            {'branch_name': '大阪支社', 'branch_code': 'OSK'},
            {'branch_name': '名古屋支社', 'branch_code': 'NGY'},
            {'branch_name': '福岡支社', 'branch_code': 'FKO'}
        ]
        
        created_branches = 0
        for branch_data in branches_data:
            existing_branch = Branch.query.filter_by(branch_code=branch_data['branch_code']).first()
            if not existing_branch:
                branch = Branch(**branch_data)
                db.session.add(branch)
                created_branches += 1
                print(f"✅ Created branch: {branch_data['branch_name']}")
            else:
                print(f"⚠️  Branch already exists: {branch_data['branch_name']}")
        
        # 年度データ作成（存在しない場合のみ）
        fiscal_years_data = [
            {'year': 2023, 'year_name': '2023年度', 'is_active': False},
            {'year': 2024, 'year_name': '2024年度', 'is_active': True},
            {'year': 2025, 'year_name': '2025年度', 'is_active': False}
        ]
        
        created_fiscal_years = 0
        for fy_data in fiscal_years_data:
            existing_fy = FiscalYear.query.filter_by(year=fy_data['year']).first()
            if not existing_fy:
                fiscal_year = FiscalYear(**fy_data)
                db.session.add(fiscal_year)
                created_fiscal_years += 1
                print(f"✅ Created fiscal year: {fy_data['year']}")
            else:
                print(f"⚠️  Fiscal year already exists: {fy_data['year']}")
        
        # 変更をコミット（支社と年度）
        db.session.commit()
        
        # 支社IDを取得
        tokyo_branch = Branch.query.filter_by(branch_code='TKY').first()
        osaka_branch = Branch.query.filter_by(branch_code='OSK').first()
        nagoya_branch = Branch.query.filter_by(branch_code='NGY').first()
        fukuoka_branch = Branch.query.filter_by(branch_code='FKO').first()
        
        if not all([tokyo_branch, osaka_branch, nagoya_branch, fukuoka_branch]):
            print("❌ Error: Could not find all required branches")
            return False
        
        # サンプルプロジェクトデータ（月別に分散）
        from datetime import datetime
        sample_projects = [
            {
                'project_code': 'DEMO001',
                'project_name': 'Webシステム開発プロジェクト（デモ）',
                'branch_id': tokyo_branch.id,
                'fiscal_year': 2024,
                'order_probability': 100,
                'revenue': 5000000,
                'expenses': 3500000
            },
            {
                'project_code': 'DEMO002',
                'project_name': 'モバイルアプリ開発（デモ）',
                'branch_id': osaka_branch.id,
                'fiscal_year': 2024,
                'order_probability': 50,
                'revenue': 3000000,
                'expenses': 2200000
            },
            {
                'project_code': 'DEMO003',
                'project_name': 'データ分析システム（デモ）',
                'branch_id': tokyo_branch.id,
                'fiscal_year': 2024,
                'order_probability': 100,
                'revenue': 8000000,
                'expenses': 5500000
            },
            {
                'project_code': 'DEMO004',
                'project_name': 'クラウド移行プロジェクト（デモ）',
                'branch_id': nagoya_branch.id,
                'fiscal_year': 2024,
                'order_probability': 0,
                'revenue': 12000000,
                'expenses': 8000000
            },
            {
                'project_code': 'DEMO005',
                'project_name': 'セキュリティ強化プロジェクト（デモ）',
                'branch_id': fukuoka_branch.id,
                'fiscal_year': 2024,
                'order_probability': 50,
                'revenue': 4500000,
                'expenses': 3200000
            },
            {
                'project_code': 'DEMO006',
                'project_name': 'AI導入支援プロジェクト（デモ）',
                'branch_id': tokyo_branch.id,
                'fiscal_year': 2025,
                'order_probability': 100,
                'revenue': 15000000,
                'expenses': 10000000
            },
            {
                'project_code': 'DEMO007',
                'project_name': 'レガシーシステム刷新（デモ）',
                'branch_id': osaka_branch.id,
                'fiscal_year': 2023,
                'order_probability': 100,
                'revenue': 20000000,
                'expenses': 14000000
            },
            {
                'project_code': 'DEMO008',
                'project_name': 'IoTプラットフォーム構築（デモ）',
                'branch_id': nagoya_branch.id,
                'fiscal_year': 2024,
                'order_probability': 50,
                'revenue': 7500000,
                'expenses': 5200000
            }
        ]
        
        # プロジェクトデータ作成（存在しない場合のみ）
        created_projects = 0
        for project_data in sample_projects:
            existing_project = Project.query.filter_by(project_code=project_data['project_code']).first()
            if not existing_project:
                project = Project(**project_data)
                db.session.add(project)
                created_projects += 1
                print(f"✅ Created project: {project_data['project_name']}")
            else:
                print(f"⚠️  Project already exists: {project_data['project_name']}")
        
        # 最終コミット
        db.session.commit()
        
        # 結果サマリー
        print("\n" + "="*60)
        print("           SAMPLE DATA CREATION SUMMARY")
        print("="*60)
        print(f"Created branches: {created_branches}")
        print(f"Created fiscal years: {created_fiscal_years}")
        print(f"Created projects: {created_projects}")
        
        # 現在のデータ統計
        total_projects = Project.query.count()
        total_branches = Branch.query.count()
        total_fiscal_years = FiscalYear.query.count()
        
        print(f"\nCurrent totals:")
        print(f"  Total branches: {total_branches}")
        print(f"  Total fiscal years: {total_fiscal_years}")
        print(f"  Total projects: {total_projects}")
        
        # 売上統計
        from sqlalchemy import func
        revenue_stats = db.session.query(
            func.count(Project.id).label('count'),
            func.sum(Project.revenue).label('total_revenue'),
            func.sum(Project.expenses).label('total_expenses')
        ).first()
        
        if revenue_stats.total_revenue:
            total_gross_profit = float(revenue_stats.total_revenue) - float(revenue_stats.total_expenses)
            print(f"\nRevenue statistics:")
            print(f"  Total revenue: ¥{float(revenue_stats.total_revenue):,.0f}")
            print(f"  Total expenses: ¥{float(revenue_stats.total_expenses):,.0f}")
            print(f"  Total gross profit: ¥{total_gross_profit:,.0f}")
        
        print("\n🎉 Sample data creation completed!")
        print("\nYou can now:")
        print("1. Access the dashboard to see sample data")
        print("2. Test import/export functionality")
        print("3. Explore branch and project management features")
        print("4. Test search and filtering capabilities")
        
        return True


def clear_demo_data():
    """デモデータのクリア"""
    app = create_app()
    
    with app.app_context():
        print("🧹 Clearing demo data...")
        
        # DEMOで始まるプロジェクトを削除
        demo_projects = Project.query.filter(Project.project_code.like('DEMO%')).all()
        for project in demo_projects:
            print(f"Deleting project: {project.project_name}")
            db.session.delete(project)
        
        db.session.commit()
        print(f"✅ Deleted {len(demo_projects)} demo projects")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage sample data for production environment')
    parser.add_argument('action', choices=['create', 'clear'], help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        success = create_sample_data()
        sys.exit(0 if success else 1)
    elif args.action == 'clear':
        clear_demo_data()
        sys.exit(0)