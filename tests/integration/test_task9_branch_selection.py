#!/usr/bin/env python3
"""
Task 9: プロジェクト作成・編集での支社選択機能のテスト
"""
import pytest
from app import create_app, db
from app.models import Project, Branch
from decimal import Decimal


@pytest.fixture
def app():
    """テスト用アプリケーション"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """テストクライアント"""
    return app.test_client()


@pytest.fixture
def sample_branches(app):
    """テスト用支社データ"""
    with app.app_context():
        # 年度マスターを作成
        from app.models import FiscalYear
        FiscalYear.create_with_validation(
            year=2024,
            year_name='2024年度'
        )
        
        # 有効な支社を作成
        branch1 = Branch.create_with_validation(
            branch_code='TKY',
            branch_name='東京本社',
            is_active=True
        )
        branch2 = Branch.create_with_validation(
            branch_code='OSK',
            branch_name='大阪支社',
            is_active=True
        )
        # 無効な支社を作成
        branch3 = Branch.create_with_validation(
            branch_code='NGY',
            branch_name='名古屋支社',
            is_active=False
        )
        
        # セッションをコミットしてIDを確定
        db.session.commit()
        
        # IDを取得してから返す
        branch_ids = [branch1.id, branch2.id, branch3.id]
        return branch_ids


def test_project_form_displays_active_branches_only(client, sample_branches):
    """プロジェクト作成フォームに有効な支社のみが表示されることをテスト"""
    response = client.get('/projects/new')
    assert response.status_code == 200
    
    content = response.get_data(as_text=True)
    
    # 有効な支社が表示されることを確認
    assert '東京本社' in content
    assert '大阪支社' in content
    
    # 無効な支社が表示されないことを確認
    assert '名古屋支社' not in content
    
    # 支社選択フィールドが存在することを確認
    assert 'name="branch_id"' in content
    assert '支社を選択してください' in content


def test_project_creation_with_branch_selection(client, sample_branches):
    """支社選択を含むプロジェクト作成のテスト"""
    branch_id = sample_branches[0]  # 東京本社のID
    
    # プロジェクト作成データ
    project_data = {
        'project_code': 'TEST-BRANCH-001',
        'project_name': '支社選択テストプロジェクト',
        'branch_id': branch_id,
        'fiscal_year': 2024,
        'order_probability': 100,
        'revenue': '1500000.00',
        'expenses': '1000000.00'
    }
    
    response = client.post('/projects/', data=project_data, follow_redirects=True)
    assert response.status_code == 200
    
    # プロジェクトが作成されたことを確認
    with client.application.app_context():
        project = Project.query.filter_by(project_code='TEST-BRANCH-001').first()
        assert project is not None
        assert project.branch_id == branch_id
        assert project.branch.branch_name == '東京本社'


def test_project_creation_without_branch_fails(client, sample_branches):
    """支社を選択しないプロジェクト作成が失敗することをテスト"""
    project_data = {
        'project_code': 'TEST-NO-BRANCH',
        'project_name': 'テストプロジェクト',
        'branch_id': 0,  # 支社未選択
        'fiscal_year': 2024,
        'order_probability': 100,
        'revenue': '1500000.00',
        'expenses': '1000000.00'
    }
    
    response = client.post('/projects/', data=project_data)
    assert response.status_code == 200  # フォームが再表示される
    
    content = response.get_data(as_text=True)
    # エラーメッセージが表示されることを確認
    assert '支社' in content and ('必須' in content or '選択' in content)
    
    # プロジェクトが作成されていないことを確認
    project = Project.query.filter_by(project_code='TEST-NO-BRANCH').first()
    assert project is None


def test_project_creation_with_inactive_branch_fails(client, sample_branches):
    """無効な支社でのプロジェクト作成が失敗することをテスト"""
    inactive_branch_id = sample_branches[2]  # 名古屋支社（無効）のID
    
    project_data = {
        'project_code': 'TEST-INACTIVE-BRANCH',
        'project_name': 'テストプロジェクト',
        'branch_id': inactive_branch_id,
        'fiscal_year': 2024,
        'order_probability': 100,
        'revenue': '1500000.00',
        'expenses': '1000000.00'
    }
    
    response = client.post('/projects/', data=project_data)
    assert response.status_code == 200  # フォームが再表示される
    
    content = response.get_data(as_text=True)
    # エラーメッセージが表示されることを確認
    assert '有効な支社' in content or '支社' in content
    
    # プロジェクトが作成されていないことを確認
    with client.application.app_context():
        project = Project.query.filter_by(project_code='TEST-INACTIVE-BRANCH').first()
        assert project is None


def test_project_edit_form_shows_current_branch(client, sample_branches):
    """プロジェクト編集フォームで現在選択されている支社が表示されることをテスト"""
    branch_id = sample_branches[0]  # 東京本社のID
    
    # テストプロジェクトを作成
    with client.application.app_context():
        project = Project.create_with_validation(
            project_code='TEST-EDIT-001',
            project_name='編集テストプロジェクト',
            branch_id=branch_id,
            fiscal_year=2024,
            order_probability=100,
            revenue=Decimal('1500000.00'),
            expenses=Decimal('1000000.00')
        )
        project_id = project.id
    
    # 編集フォームにアクセス
    response = client.get(f'/projects/{project_id}/edit')
    assert response.status_code == 200
    
    content = response.get_data(as_text=True)
    
    # 現在の支社が選択されていることを確認
    assert f'<option selected value="{branch_id}">' in content
    
    # 有効な支社がすべて表示されることを確認
    assert '東京本社' in content
    assert '大阪支社' in content
    assert '名古屋支社' not in content  # 無効な支社は表示されない


def test_project_edit_with_branch_change(client, sample_branches):
    """プロジェクト編集で支社を変更できることをテスト"""
    branch1_id = sample_branches[0]  # 東京本社のID
    branch2_id = sample_branches[1]  # 大阪支社のID
    
    # テストプロジェクトを作成（東京本社）
    with client.application.app_context():
        project = Project.create_with_validation(
            project_code='TEST-EDIT-BRANCH',
            project_name='支社変更テストプロジェクト',
            branch_id=branch1_id,
            fiscal_year=2024,
            order_probability=100,
            revenue=Decimal('1500000.00'),
            expenses=Decimal('1000000.00')
        )
        project_id = project.id
    
    # 支社を大阪支社に変更
    update_data = {
        'project_code': 'TEST-EDIT-BRANCH',
        'project_name': '支社変更テストプロジェクト',
        'branch_id': branch2_id,  # 大阪支社に変更
        'fiscal_year': 2024,
        'order_probability': 100,
        'revenue': '1500000.00',
        'expenses': '1000000.00'
    }
    
    response = client.post(f'/projects/{project_id}/update', data=update_data, follow_redirects=True)
    assert response.status_code == 200
    
    # プロジェクトの支社が変更されたことを確認
    with client.application.app_context():
        updated_project = Project.query.get(project_id)
        assert updated_project.branch_id == branch2_id
        assert updated_project.branch.branch_name == '大阪支社'


def test_branch_validation_in_form(client, sample_branches):
    """フォームでの支社バリデーションのテスト"""
    from app.forms import ProjectForm
    
    with client.application.app_context():
        # 有効な支社IDでのバリデーション
        form = ProjectForm()
        form.branch_id.choices = [(0, '支社を選択してください')] + [(branch.id, branch.branch_name) for branch in Branch.get_active_branches()]
        form.branch_id.data = sample_branches[0]  # 有効な支社ID
        
        # 支社フィールドのバリデーションが通ることを確認
        form.validate_branch_id(form.branch_id)  # エラーが発生しないことを確認
        
        # 無効な支社IDでのバリデーション
        form.branch_id.data = sample_branches[2]  # 無効な支社ID
        
        with pytest.raises(Exception):  # ValidationErrorが発生することを確認
            form.validate_branch_id(form.branch_id)


def test_branch_choices_populated_correctly(client, sample_branches):
    """支社選択肢が正しく設定されることをテスト"""
    from app.forms import ProjectForm
    
    with client.application.app_context():
        form = ProjectForm()
        # プロジェクトルートで設定されるのと同じ方法で選択肢を設定
        form.branch_id.choices = [(0, '支社を選択してください')] + [(branch.id, branch.branch_name) for branch in Branch.get_active_branches()]
        
        # 選択肢が正しく設定されていることを確認
        choices = dict(form.branch_id.choices)
        assert 0 in choices
        assert choices[0] == '支社を選択してください'
        
        # 有効な支社のみが含まれていることを確認
        active_branches = Branch.get_active_branches()
        for branch in active_branches:
            assert branch.id in choices
            assert choices[branch.id] == branch.branch_name
        
        # 無効な支社が含まれていないことを確認
        inactive_branch_id = sample_branches[2]  # 無効な支社のID
        assert inactive_branch_id not in choices


def test_project_list_shows_branch_names(client, sample_branches):
    """プロジェクト一覧で支社名が表示されることをテスト"""
    branch_id = sample_branches[0]  # 東京本社のID
    
    # テストプロジェクトを作成
    with client.application.app_context():
        project = Project.create_with_validation(
            project_code='TEST-LIST-BRANCH',
            project_name='一覧表示テストプロジェクト',
            branch_id=branch_id,
            fiscal_year=2024,
            order_probability=100,
            revenue=Decimal('1500000.00'),
            expenses=Decimal('1000000.00')
        )
    
    # プロジェクト一覧APIを呼び出し
    response = client.get('/projects/api/list?draw=1&start=0&length=25')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'data' in data
    
    # 作成したプロジェクトが含まれていることを確認
    project_found = False
    for row in data['data']:
        if row[0] == 'TEST-LIST-BRANCH':  # プロジェクトコード
            assert row[2] == '東京本社'  # 支社名
            project_found = True
            break
    
    assert project_found, "作成したプロジェクトが一覧に表示されていません"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])