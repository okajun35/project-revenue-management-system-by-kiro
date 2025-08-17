#!/usr/bin/env python3
"""
月別売上推移テスト用の追加サンプルデータ作成
"""

import sys
from pathlib import Path
from datetime import datetime, date

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import Branch, Project

def add_monthly_sample_data():
    """月別推移テスト用のサンプルデータを追加"""
    
    app = create_app()
    
    with app.app_context():
        print("🚀 Adding monthly sample data...")
        
        # 支社を取得
        branches = Branch.query.all()
        if not branches:
            print("❌ No branches found. Please create sample data first.")
            return False
        
        # 月別プロジェクトデータ（2024年度）
        monthly_projects = [
            # 4月
            {'code': 'M2404001', 'name': '4月新規プロジェクト1', 'branch': 'TKY', 'revenue': 2000000, 'expenses': 1400000, 'prob': 100, 'month': 4},
            {'code': 'M2404002', 'name': '4月新規プロジェクト2', 'branch': 'OSK', 'revenue': 1500000, 'expenses': 1100000, 'prob': 50, 'month': 4},
            
            # 5月
            {'code': 'M2405001', 'name': '5月新規プロジェクト1', 'branch': 'TKY', 'revenue': 3000000, 'expenses': 2100000, 'prob': 100, 'month': 5},
            {'code': 'M2405002', 'name': '5月新規プロジェクト2', 'branch': 'NGY', 'revenue': 1800000, 'expenses': 1300000, 'prob': 50, 'month': 5},
            {'code': 'M2405003', 'name': '5月新規プロジェクト3', 'branch': 'FKO', 'revenue': 2200000, 'expenses': 1600000, 'prob': 0, 'month': 5},
            
            # 6月
            {'code': 'M2406001', 'name': '6月新規プロジェクト1', 'branch': 'OSK', 'revenue': 4000000, 'expenses': 2800000, 'prob': 100, 'month': 6},
            {'code': 'M2406002', 'name': '6月新規プロジェクト2', 'branch': 'TKY', 'revenue': 2500000, 'expenses': 1800000, 'prob': 50, 'month': 6},
            
            # 7月
            {'code': 'M2407001', 'name': '7月新規プロジェクト1', 'branch': 'NGY', 'revenue': 3500000, 'expenses': 2400000, 'prob': 100, 'month': 7},
            {'code': 'M2407002', 'name': '7月新規プロジェクト2', 'branch': 'FKO', 'revenue': 1600000, 'expenses': 1200000, 'prob': 50, 'month': 7},
            {'code': 'M2407003', 'name': '7月新規プロジェクト3', 'branch': 'TKY', 'revenue': 2800000, 'expenses': 2000000, 'prob': 0, 'month': 7},
            
            # 8月
            {'code': 'M2408001', 'name': '8月新規プロジェクト1', 'branch': 'OSK', 'revenue': 5000000, 'expenses': 3500000, 'prob': 100, 'month': 8},
            {'code': 'M2408002', 'name': '8月新規プロジェクト2', 'branch': 'TKY', 'revenue': 2200000, 'expenses': 1600000, 'prob': 50, 'month': 8},
            
            # 9月
            {'code': 'M2409001', 'name': '9月新規プロジェクト1', 'branch': 'NGY', 'revenue': 4200000, 'expenses': 2900000, 'prob': 100, 'month': 9},
            {'code': 'M2409002', 'name': '9月新規プロジェクト2', 'branch': 'FKO', 'revenue': 1900000, 'expenses': 1400000, 'prob': 50, 'month': 9},
            {'code': 'M2409003', 'name': '9月新規プロジェクト3', 'branch': 'OSK', 'revenue': 3100000, 'expenses': 2200000, 'prob': 0, 'month': 9},
            
            # 10月
            {'code': 'M2410001', 'name': '10月新規プロジェクト1', 'branch': 'TKY', 'revenue': 6000000, 'expenses': 4200000, 'prob': 100, 'month': 10},
            {'code': 'M2410002', 'name': '10月新規プロジェクト2', 'branch': 'NGY', 'revenue': 2400000, 'expenses': 1700000, 'prob': 50, 'month': 10},
            
            # 11月
            {'code': 'M2411001', 'name': '11月新規プロジェクト1', 'branch': 'OSK', 'revenue': 3800000, 'expenses': 2600000, 'prob': 100, 'month': 11},
            {'code': 'M2411002', 'name': '11月新規プロジェクト2', 'branch': 'FKO', 'revenue': 2100000, 'expenses': 1500000, 'prob': 50, 'month': 11},
            {'code': 'M2411003', 'name': '11月新規プロジェクト3', 'branch': 'TKY', 'revenue': 2700000, 'expenses': 1900000, 'prob': 0, 'month': 11},
            
            # 12月
            {'code': 'M2412001', 'name': '12月新規プロジェクト1', 'branch': 'NGY', 'revenue': 4500000, 'expenses': 3100000, 'prob': 100, 'month': 12},
            {'code': 'M2412002', 'name': '12月新規プロジェクト2', 'branch': 'OSK', 'revenue': 2600000, 'expenses': 1800000, 'prob': 50, 'month': 12},
            
            # 1月
            {'code': 'M2501001', 'name': '1月新規プロジェクト1', 'branch': 'TKY', 'revenue': 5500000, 'expenses': 3800000, 'prob': 100, 'month': 1},
            {'code': 'M2501002', 'name': '1月新規プロジェクト2', 'branch': 'FKO', 'revenue': 2300000, 'expenses': 1600000, 'prob': 50, 'month': 1},
            
            # 2月
            {'code': 'M2502001', 'name': '2月新規プロジェクト1', 'branch': 'OSK', 'revenue': 4100000, 'expenses': 2800000, 'prob': 100, 'month': 2},
            {'code': 'M2502002', 'name': '2月新規プロジェクト2', 'branch': 'NGY', 'revenue': 2800000, 'expenses': 2000000, 'prob': 50, 'month': 2},
            {'code': 'M2502003', 'name': '2月新規プロジェクト3', 'branch': 'TKY', 'revenue': 3200000, 'expenses': 2300000, 'prob': 0, 'month': 2},
            
            # 3月
            {'code': 'M2503001', 'name': '3月新規プロジェクト1', 'branch': 'FKO', 'revenue': 6500000, 'expenses': 4500000, 'prob': 100, 'month': 3},
            {'code': 'M2503002', 'name': '3月新規プロジェクト2', 'branch': 'OSK', 'revenue': 3000000, 'expenses': 2100000, 'prob': 50, 'month': 3},
            {'code': 'M2503003', 'name': '3月新規プロジェクト3', 'branch': 'NGY', 'revenue': 2400000, 'expenses': 1700000, 'prob': 0, 'month': 3},
        ]
        
        # 支社コードから支社IDのマッピングを作成
        branch_map = {branch.branch_code: branch.id for branch in branches}
        
        created_count = 0
        for project_data in monthly_projects:
            # 既存チェック
            existing = Project.query.filter_by(project_code=project_data['code']).first()
            if existing:
                print(f"⚠️  Project already exists: {project_data['code']}")
                continue
            
            # 支社IDを取得
            branch_id = branch_map.get(project_data['branch'])
            if not branch_id:
                print(f"❌ Branch not found: {project_data['branch']}")
                continue
            
            # 作成日を設定（年度に応じて）
            month = project_data['month']
            if month >= 4:  # 4-12月は2024年
                created_at = datetime(2024, month, 15, 10, 0, 0)
            else:  # 1-3月は2025年
                created_at = datetime(2025, month, 15, 10, 0, 0)
            
            # プロジェクト作成
            project = Project(
                project_code=project_data['code'],
                project_name=project_data['name'],
                branch_id=branch_id,
                fiscal_year=2024,
                order_probability=project_data['prob'],
                revenue=project_data['revenue'],
                expenses=project_data['expenses'],
                created_at=created_at,
                updated_at=created_at
            )
            
            db.session.add(project)
            created_count += 1
            print(f"✅ Created: {project_data['name']} ({month}月)")
        
        # コミット
        db.session.commit()
        
        print(f"\n🎉 Created {created_count} monthly projects!")
        
        # 統計表示
        total_projects = Project.query.count()
        print(f"Total projects in database: {total_projects}")
        
        return True


if __name__ == '__main__':
    success = add_monthly_sample_data()
    sys.exit(0 if success else 1)