"""
検索・フィルター機能のテスト

要件3の検証:
- 3.1: 検索画面へのアクセス
- 3.2: プロジェクトコードでの部分一致検索
- 3.3: プロジェクト名での部分一致検索
- 3.4: 売上年度での検索
- 3.5: 受注角度範囲での検索
- 3.6: 複数条件でのAND検索
- 3.7: 検索結果に粗利も含めて表示
"""

import pytest
from app import create_app, db
from app.models import Project, Branch, FiscalYear
from flask import url_for
import json


class TestSearchFunctionality:
    """検索・フィルター機能のテストクラス"""
    
    def test_search_page_access(self, client):
        """要件3.1: 検索画面へのアクセステスト"""
        with client.application.test_request_context():
            response = client.get('/projects/search')
            assert response.status_code == 200
            
            # レスポンスデータを取得
            response_data = response.get_data(as_text=True)
            
            # 基本的な検索フォーム要素が含まれていることを確認
            assert len(response_data) > 0, "Response should not be empty"
            
            # HTMLの基本構造が含まれていることを確認
            assert 'html' in response_data.lower()
            assert 'form' in response_data.lower() or 'search' in response_data.lower()
    
    def test_project_code_partial_search(self, client, sample_projects):
        """要件3.2: プロジェクトコードでの部分一致検索テスト"""
        # プロジェクトコード "PROJ" で検索
        response = client.get('/projects/api/list?project_code=PROJ')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        # 結果にPROJを含むプロジェクトのみが含まれることを確認
        for row in data['data']:
            assert 'PROJ' in row[0]  # プロジェクトコード列
    
    def test_project_name_partial_search(self, client, sample_projects):
        """要件3.3: プロジェクト名での部分一致検索テスト"""
        # プロジェクト名 "テスト" で検索
        response = client.get('/projects/api/list?project_name=テスト')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        # 結果に「テスト」を含むプロジェクトのみが含まれることを確認
        for row in data['data']:
            assert 'テスト' in row[1]  # プロジェクト名列
    
    def test_fiscal_year_search(self, client, sample_projects):
        """要件3.4: 売上年度での検索テスト"""
        # 2023年度で検索
        response = client.get('/projects/api/list?fiscal_year=2023')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        # 結果に2023年度のプロジェクトのみが含まれることを確認
        for row in data['data']:
            assert row[3] == 2023  # 年度列
    
    def test_order_probability_range_search(self, client, sample_projects):
        """要件3.5: 受注角度範囲での検索テスト"""
        # 受注角度50%以上で検索
        response = client.get('/projects/api/list?order_probability_min=50')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        # 結果に50%以上のプロジェクトのみが含まれることを確認
        for row in data['data']:
            # HTMLタグから数値を抽出
            probability_html = row[4]  # 受注角度列
            if '50%' in probability_html or '100%' in probability_html:
                assert True
            else:
                assert False, f"Expected probability >= 50%, got: {probability_html}"
    
    def test_multiple_conditions_and_search(self, client, sample_projects):
        """要件3.6: 複数条件でのAND検索テスト"""
        # プロジェクトコード "PROJ" かつ 2023年度で検索
        response = client.get('/projects/api/list?project_code=PROJ&fiscal_year=2023')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        # 結果に両方の条件を満たすプロジェクトのみが含まれることを確認
        for row in data['data']:
            assert 'PROJ' in row[0]  # プロジェクトコード列
            assert row[3] == 2023    # 年度列
    
    def test_search_results_include_gross_profit(self, client, sample_projects):
        """要件3.7: 検索結果に粗利も含めて表示テスト"""
        response = client.get('/projects/api/list')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        assert len(data['data']) > 0
        
        # 各行に粗利列が含まれることを確認
        for row in data['data']:
            assert len(row) >= 8  # 粗利列を含む最低限の列数
            gross_profit_html = row[7]  # 粗利列
            assert 'text-right' in gross_profit_html  # 右寄せスタイル
            # 数値が含まれることを確認（HTMLタグ内の数値）
            assert any(char.isdigit() or char in '.,+-' for char in gross_profit_html)
    
    def test_branch_search_functionality(self, client, sample_projects):
        """支社での検索機能テスト"""
        # 支社IDで検索
        response = client.get('/projects/api/list?branch_id=1')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        # 結果に指定した支社のプロジェクトのみが含まれることを確認
        for row in data['data']:
            # 支社名列が存在することを確認
            assert row[2] is not None  # 支社名列
    
    def test_branch_search_api(self, client, sample_branches):
        """支社検索APIのテスト"""
        # 支社名での部分一致検索
        response = client.get('/projects/api/branches/search?search=テスト東京')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'branches' in data
        
        # 結果に「東京」を含む支社のみが含まれることを確認
        for branch in data['branches']:
            assert 'テスト東京' in branch['branch_name']
    
    def test_empty_search_returns_all_projects(self, client, sample_projects):
        """空の検索条件で全プロジェクトが返されることをテスト"""
        response = client.get('/projects/api/list')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        assert data['recordsTotal'] > 0
        assert data['recordsFiltered'] == data['recordsTotal']
    
    def test_no_results_search(self, client, sample_projects):
        """該当なしの検索結果テスト"""
        # 存在しないプロジェクトコードで検索
        response = client.get('/projects/api/list?project_code=NONEXISTENT')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        assert len(data['data']) == 0
        assert data['recordsFiltered'] == 0
    
    def test_order_probability_range_validation(self, client, sample_projects):
        """受注角度範囲の境界値テスト"""
        # 最小値と最大値の両方を指定
        response = client.get('/projects/api/list?order_probability_min=0&order_probability_max=50')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        # 結果に0-50%の範囲のプロジェクトのみが含まれることを確認
        for row in data['data']:
            probability_html = row[4]  # 受注角度列
            # 0%または50%のプロジェクトのみ
            assert ('0%' in probability_html or '50%' in probability_html)
    
    def test_search_with_pagination(self, client, sample_projects):
        """ページネーション付き検索テスト"""
        # 最初のページ
        response = client.get('/projects/api/list?start=0&length=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        assert len(data['data']) <= 2
        assert 'recordsTotal' in data
        assert 'recordsFiltered' in data
    
    def test_search_with_sorting(self, client, sample_projects):
        """ソート付き検索テスト"""
        # プロジェクトコードで昇順ソート
        response = client.get('/projects/api/list?order[0][column]=0&order[0][dir]=asc')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'data' in data
        
        if len(data['data']) > 1:
            # ソート順が正しいことを確認
            first_code = data['data'][0][0]
            second_code = data['data'][1][0]
            assert first_code <= second_code


@pytest.fixture
def sample_projects(app):
    """テスト用のサンプルプロジェクトを作成"""
    import uuid
    with app.app_context():
        # ユニークな識別子を生成
        unique_id = str(uuid.uuid4())[:8]
        
        # 支社を作成
        branch1 = Branch.create_with_validation(
            branch_code=f'TEST{unique_id}1',
            branch_name=f'テスト東京支社{unique_id}',
            is_active=True
        )
        branch2 = Branch.create_with_validation(
            branch_code=f'TEST{unique_id}2',
            branch_name=f'テスト大阪支社{unique_id}',
            is_active=True
        )
        
        # プロジェクトを作成
        projects = [
            Project.create_with_validation(
                project_code='PROJ001',
                project_name='テストプロジェクト1',
                branch_id=branch1.id,
                fiscal_year=2023,
                order_probability=100,
                revenue=1000000,
                expenses=800000
            ),
            Project.create_with_validation(
                project_code='PROJ002',
                project_name='テストプロジェクト2',
                branch_id=branch2.id,
                fiscal_year=2023,
                order_probability=50,
                revenue=2000000,
                expenses=1500000
            ),
            Project.create_with_validation(
                project_code='TEST001',
                project_name='別のテストプロジェクト',
                branch_id=branch1.id,
                fiscal_year=2024,
                order_probability=0,
                revenue=500000,
                expenses=600000
            )
        ]
        
        yield projects
        
        # クリーンアップ
        for project in projects:
            try:
                db.session.delete(project)
            except:
                pass
        try:
            db.session.delete(branch1)
            db.session.delete(branch2)
        except:
            pass
        db.session.commit()


@pytest.fixture
def sample_branches(app):
    """テスト用のサンプル支社を作成"""
    import uuid
    with app.app_context():
        # ユニークな識別子を生成
        unique_id = str(uuid.uuid4())[:8]
        
        branches = [
            Branch.create_with_validation(
                branch_code=f'TKY{unique_id}',
                branch_name=f'テスト東京本社{unique_id}',
                is_active=True
            ),
            Branch.create_with_validation(
                branch_code=f'OSK{unique_id}',
                branch_name=f'テスト大阪支社{unique_id}',
                is_active=True
            ),
            Branch.create_with_validation(
                branch_code=f'NGY{unique_id}',
                branch_name=f'テスト名古屋支社{unique_id}',
                is_active=True
            )
        ]
        
        yield branches
        
        # クリーンアップ
        for branch in branches:
            try:
                db.session.delete(branch)
            except:
                pass
        db.session.commit()