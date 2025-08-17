#!/usr/bin/env python3
"""
ダッシュボードサービスのテスト
"""

from app import create_app
from app.services.dashboard_service import DashboardService

def test_dashboard_service():
    app = create_app()
    with app.app_context():
        print('=== ダッシュボードサービステスト ===')
        
        # 利用可能な年度を取得
        years = DashboardService.get_available_years()
        print(f'利用可能な年度: {years}')
        
        # 全体統計を取得
        stats = DashboardService.get_overall_stats()
        print(f'全体統計: {stats}')
        
        # 年度別推移データを取得
        trend = DashboardService.get_yearly_trend_data()
        print(f'年度別推移: {trend}')
        
        # 支社別統計を取得
        branch_stats = DashboardService.get_branch_stats()
        print(f'支社別統計: {len(branch_stats)}件')
        for branch in branch_stats[:3]:  # 最初の3件のみ表示
            print(f'  - {branch["branch_name"]}: {branch["project_count"]}件, 売上¥{branch["total_revenue"]:,.0f}')
        
        # 最近のプロジェクトを取得
        recent = DashboardService.get_recent_projects(limit=3)
        print(f'最近のプロジェクト: {len(recent)}件')
        for project in recent:
            print(f'  - {project["project_name"]}: ¥{project["revenue"]:,.0f}')
        
        # 受注角度分布を取得
        distribution = DashboardService.get_order_probability_distribution()
        print(f'受注角度分布: {distribution}')
        
        print('テスト完了')

if __name__ == '__main__':
    test_dashboard_service()