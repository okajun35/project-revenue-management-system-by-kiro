#!/usr/bin/env python3
"""
プロジェクト作成機能のテスト
"""
import pytest
from app import create_app, db
from app.models import Project
from app.forms import ProjectForm
from decimal import Decimal

@pytest.fixture
def app():
    """テスト用アプリケーションを作成"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """テスト用クライアントを作成"""
    return app.test_client()

def test_project_creation_form_validation(app):
    """プロジェクト作成フォームのバリデーションテスト"""
    with app.app_context():
        # テスト用の支社を作成
        from app.models import Branch, FiscalYear
        test_branch = Branch.create_with_validation(
            branch_code='TEST001',
            branch_name='テスト支社',
            is_active=True
        )
        
        # テスト用の年度を作成
        test_fiscal_year = FiscalYear.create_with_validation(
            year=2024,
            year_name='2024年度'
        )
        
        # 有効なデータでフォームをテスト
        form_data = {
            'project_code': 'TEST-2024-001',
            'project_name': 'テストプロジェクト',
            'branch_id': test_branch.id,
            'fiscal_year': 2024,
            'order_probability': 100,
            'revenue': Decimal('1000000.00'),
            'expenses': Decimal('800000.00')
        }
        
        form = ProjectForm(data=form_data)
        # 支社の選択肢を設定
        form.branch_id.choices = [(test_branch.id, test_branch.branch_name)]
        # 年度の選択肢を設定
        form.fiscal_year.choices = [(test_fiscal_year.year, test_fiscal_year.year_name)]
        assert form.validate(), f"フォームバリデーションが失敗しました: {form.errors}"
        
        # 無効なデータでフォームをテスト
        invalid_form_data = {
            'project_code': '',  # 必須項目が空
            'project_name': 'テストプロジェクト',
            'branch_id': test_branch.id,
            'fiscal_year': 2024,
            'order_probability': 100,
            'revenue': Decimal('1000000.00'),
            'expenses': Decimal('800000.00')
        }
        
        invalid_form = ProjectForm(data=invalid_form_data)
        invalid_form.branch_id.choices = [(test_branch.id, test_branch.branch_name)]
        invalid_form.fiscal_year.choices = [(test_fiscal_year.year, test_fiscal_year.year_name)]
        assert not invalid_form.validate(), "無効なデータでバリデーションが通ってしまいました"
        assert 'project_code' in invalid_form.errors

def test_project_creation_model(app):
    """プロジェクト作成モデルのテスト"""
    with app.app_context():
        # テスト用の支社を作成
        from app.models import Branch, FiscalYear
        test_branch = Branch.create_with_validation(
            branch_code='TEST002',
            branch_name='テスト支社2',
            is_active=True
        )
        
        # テスト用の年度を作成
        FiscalYear.create_with_validation(
            year=2024,
            year_name='2024年度'
        )
        
        # プロジェクトを作成
        project = Project.create_with_validation(
            project_code='TEST-2024-001',
            project_name='テストプロジェクト',
            branch_id=test_branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=Decimal('1000000.00'),
            expenses=Decimal('800000.00')
        )
        
        # データベースに保存されているか確認
        assert project.id is not None
        assert project.project_code == 'TEST-2024-001'
        assert project.project_name == 'テストプロジェクト'
        assert project.fiscal_year == 2024
        assert project.order_probability == 100
        assert project.revenue == Decimal('1000000.00')
        assert project.expenses == Decimal('800000.00')
        
        # 粗利の自動計算を確認
        expected_gross_profit = 1000000.00 - 800000.00
        assert project.gross_profit == expected_gross_profit
        
        # データベースから取得できるか確認
        retrieved_project = Project.query.filter_by(project_code='TEST-2024-001').first()
        assert retrieved_project is not None
        assert retrieved_project.project_name == 'テストプロジェクト'

def test_project_creation_route(client, app):
    """プロジェクト作成ルートのテスト"""
    with app.app_context():
        # テスト用の支社を作成
        from app.models import Branch, FiscalYear
        test_branch = Branch.create_with_validation(
            branch_code='TEST003',
            branch_name='テスト支社3',
            is_active=True
        )
        
        # テスト用の年度を作成
        FiscalYear.create_with_validation(
            year=2024,
            year_name='2024年度'
        )
        
        # 新規作成フォーム画面のテスト
        response = client.get('/projects/new')
        assert response.status_code == 200
        assert 'プロジェクトコード' in response.get_data(as_text=True)
        
        # プロジェクト作成POSTリクエストのテスト
        form_data = {
            'project_code': 'TEST-2024-002',
            'project_name': 'テストプロジェクト2',
            'branch_id': test_branch.id,
            'fiscal_year': 2024,
            'order_probability': 50,
            'revenue': '1500000.00',
            'expenses': '1200000.00',
            'csrf_token': 'test_token'  # CSRFトークンは実際のテストでは適切に設定する必要があります
        }
        
        # CSRFを無効にしてテスト（テスト環境用）
        with app.test_request_context():
            app.config['WTF_CSRF_ENABLED'] = False
            response = client.post('/projects/', data=form_data, follow_redirects=True)
            
            # リダイレクトが成功したか確認
            assert response.status_code == 200
            
            # データベースに保存されているか確認
            project = Project.query.filter_by(project_code='TEST-2024-002').first()
            assert project is not None
            assert project.project_name == 'テストプロジェクト2'
            assert project.gross_profit == 300000.00  # 1500000 - 1200000

def test_gross_profit_calculation(app):
    """粗利計算のテスト"""
    with app.app_context():
        # テスト用の支社を作成
        from app.models import Branch, FiscalYear
        test_branch = Branch.create_with_validation(
            branch_code='TEST004',
            branch_name='テスト支社4',
            is_active=True
        )
        
        # テスト用の年度を作成
        FiscalYear.create_with_validation(
            year=2024,
            year_name='2024年度'
        )
        
        # 正の粗利のテスト
        project1 = Project.create_with_validation(
            project_code='PROFIT-001',
            project_name='利益プロジェクト',
            branch_id=test_branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=Decimal('2000000.00'),
            expenses=Decimal('1500000.00')
        )
        assert project1.gross_profit == 500000.00
        
        # 負の粗利のテスト
        project2 = Project.create_with_validation(
            project_code='LOSS-001',
            project_name='損失プロジェクト',
            branch_id=test_branch.id,
            fiscal_year=2024,
            order_probability=0,
            revenue=Decimal('1000000.00'),
            expenses=Decimal('1200000.00')
        )
        assert project2.gross_profit == -200000.00
        
        # ゼロ粗利のテスト
        project3 = Project.create_with_validation(
            project_code='BREAK-EVEN-001',
            project_name='損益分岐点プロジェクト',
            branch_id=test_branch.id,
            fiscal_year=2024,
            order_probability=50,
            revenue=Decimal('1000000.00'),
            expenses=Decimal('1000000.00')
        )
        assert project3.gross_profit == 0.00

def test_project_code_uniqueness(app):
    """プロジェクトコードの重複チェックテスト"""
    with app.app_context():
        # テスト用の支社を作成
        from app.models import Branch, FiscalYear
        test_branch = Branch.create_with_validation(
            branch_code='TEST005',
            branch_name='テスト支社5',
            is_active=True
        )
        
        # テスト用の年度を作成
        FiscalYear.create_with_validation(
            year=2024,
            year_name='2024年度'
        )
        
        # 最初のプロジェクトを作成
        project1 = Project.create_with_validation(
            project_code='UNIQUE-001',
            project_name='最初のプロジェクト',
            branch_id=test_branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=Decimal('1000000.00'),
            expenses=Decimal('800000.00')
        )
        assert project1.id is not None
        
        # 同じプロジェクトコードで作成を試行
        with pytest.raises(Exception):  # ValidationErrorまたはIntegrityError
            Project.create_with_validation(
                project_code='UNIQUE-001',  # 重複するコード
                project_name='重複プロジェクト',
                branch_id=test_branch.id,
                fiscal_year=2024,
                order_probability=50,
                revenue=Decimal('2000000.00'),
                expenses=Decimal('1500000.00')
            )

if __name__ == '__main__':
    pytest.main([__file__, '-v'])