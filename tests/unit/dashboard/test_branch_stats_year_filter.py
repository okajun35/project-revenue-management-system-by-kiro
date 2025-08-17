"""
ダッシュボード支社別統計の年度フィルター機能のテスト
"""
import pytest
from flask import url_for
from app.services.dashboard_service import DashboardService
from app.models import Project, Branch
from app import db
import uuid


class TestBranchStatsYearFilter:
    """支社別統計年度フィルター機能のテストクラス"""
    
    def test_branch_stats_api_without_year(self, client, sample_branch):
        """年度指定なしでの支社別統計API取得テスト"""
        # テスト用プロジェクトを複数年度で作成
        project_2023 = Project.create_with_validation(
            project_code=f'TEST-2023-{uuid.uuid4().hex[:8].upper()}',
            project_name='2023年度テストプロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2023,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        
        project_2024 = Project.create_with_validation(
            project_code=f'TEST-2024-{uuid.uuid4().hex[:8].upper()}',
            project_name='2024年度テストプロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=50,
            revenue=1500000,
            expenses=1200000
        )
        
        # 年度指定なしでAPI呼び出し
        response = client.get(url_for('main.branch_stats'))
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'branch_stats' in data
        assert len(data['branch_stats']) > 0
        
        # 支社が含まれていることを確認
        branch_found = False
        for branch_stat in data['branch_stats']:
            if branch_stat['branch_id'] == sample_branch.id:
                branch_found = True
                # 全年度の合計が反映されていることを確認
                assert branch_stat['project_count'] == 2
                assert branch_stat['total_revenue'] == 2500000  # 1000000 + 1500000
                assert branch_stat['total_expenses'] == 2000000  # 800000 + 1200000
                break
        
        assert branch_found, "テスト支社が統計に含まれていません"
    
    def test_branch_stats_api_with_specific_year(self, client, sample_branch):
        """特定年度指定での支社別統計API取得テスト"""
        # テスト用プロジェクトを複数年度で作成
        project_2023 = Project.create_with_validation(
            project_code=f'TEST-2023-{uuid.uuid4().hex[:8].upper()}',
            project_name='2023年度テストプロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2023,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        
        project_2024 = Project.create_with_validation(
            project_code=f'TEST-2024-{uuid.uuid4().hex[:8].upper()}',
            project_name='2024年度テストプロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=50,
            revenue=1500000,
            expenses=1200000
        )
        
        # 2024年度のみ指定してAPI呼び出し
        response = client.get(url_for('main.branch_stats', year=2024))
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'branch_stats' in data
        assert data['year'] == 2024
        
        # 支社が含まれていることを確認
        branch_found = False
        for branch_stat in data['branch_stats']:
            if branch_stat['branch_id'] == sample_branch.id:
                branch_found = True
                # 2024年度のみの数値が反映されていることを確認
                assert branch_stat['project_count'] == 1
                assert branch_stat['total_revenue'] == 1500000
                assert branch_stat['total_expenses'] == 1200000
                assert branch_stat['total_gross_profit'] == 300000
                break
        
        assert branch_found, "テスト支社が統計に含まれていません"
    
    def test_dashboard_service_branch_stats_year_filter(self, sample_branch):
        """DashboardServiceの支社別統計年度フィルター機能テスト"""
        # テスト用プロジェクトを複数年度で作成
        project_2023 = Project.create_with_validation(
            project_code=f'TEST-2023-{uuid.uuid4().hex[:8].upper()}',
            project_name='2023年度テストプロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2023,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        
        project_2024 = Project.create_with_validation(
            project_code=f'TEST-2024-{uuid.uuid4().hex[:8].upper()}',
            project_name='2024年度テストプロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=50,
            revenue=1500000,
            expenses=1200000
        )
        
        # 全年度の統計を取得
        all_years_stats = DashboardService.get_branch_stats()
        
        # 2024年度のみの統計を取得
        year_2024_stats = DashboardService.get_branch_stats(fiscal_year=2024)
        
        # 2023年度のみの統計を取得
        year_2023_stats = DashboardService.get_branch_stats(fiscal_year=2023)
        
        # テスト支社の統計を検索
        def find_branch_stats(stats_list, branch_id):
            for stat in stats_list:
                if stat['branch_id'] == branch_id:
                    return stat
            return None
        
        all_years_branch = find_branch_stats(all_years_stats, sample_branch.id)
        year_2024_branch = find_branch_stats(year_2024_stats, sample_branch.id)
        year_2023_branch = find_branch_stats(year_2023_stats, sample_branch.id)
        
        # 全年度統計の確認
        assert all_years_branch is not None
        assert all_years_branch['project_count'] == 2
        assert all_years_branch['total_revenue'] == 2500000
        
        # 2024年度統計の確認
        assert year_2024_branch is not None
        assert year_2024_branch['project_count'] == 1
        assert year_2024_branch['total_revenue'] == 1500000
        
        # 2023年度統計の確認
        assert year_2023_branch is not None
        assert year_2023_branch['project_count'] == 1
        assert year_2023_branch['total_revenue'] == 1000000
    
    def test_dashboard_page_includes_year_selector(self, client):
        """ダッシュボードページに年度選択機能が含まれていることを確認"""
        response = client.get(url_for('main.dashboard'))
        
        assert response.status_code == 200
        html_content = response.get_data(as_text=True)
        
        # 支社別統計の年度選択要素が含まれていることを確認
        assert 'branch-stats-year-select' in html_content
        assert '支社別統計' in html_content
        assert '年度:' in html_content
    
    def test_branch_stats_with_no_projects(self, client, sample_branch):
        """プロジェクトが存在しない年度での支社別統計テスト"""
        # 存在しない年度（例：2030年）で統計を取得
        response = client.get(url_for('main.branch_stats', year=2030))
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'branch_stats' in data
        assert data['year'] == 2030
        
        # 支社は表示されるが、プロジェクト数は0であることを確認
        branch_found = False
        for branch_stat in data['branch_stats']:
            if branch_stat['branch_id'] == sample_branch.id:
                branch_found = True
                assert branch_stat['project_count'] == 0
                assert branch_stat['total_revenue'] == 0
                assert branch_stat['total_expenses'] == 0
                assert branch_stat['total_gross_profit'] == 0
                break
        
        assert branch_found, "支社が統計に含まれていません"
    
    def test_branch_stats_gross_profit_calculation(self, sample_branch):
        """支社別統計の粗利計算が正しく行われることを確認"""
        # 粗利がマイナスになるプロジェクトを作成
        project = Project.create_with_validation(
            project_code=f'TEST-LOSS-{uuid.uuid4().hex[:8].upper()}',
            project_name='赤字テストプロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=0,
            revenue=500000,
            expenses=800000  # 経費が売上を上回る
        )
        
        # 統計を取得
        stats = DashboardService.get_branch_stats(fiscal_year=2024)
        
        # テスト支社の統計を検索
        branch_stat = None
        for stat in stats:
            if stat['branch_id'] == sample_branch.id:
                branch_stat = stat
                break
        
        assert branch_stat is not None
        assert branch_stat['total_gross_profit'] == -300000  # 500000 - 800000
        assert branch_stat['gross_profit_rate'] == -60.0  # -300000 / 500000 * 100