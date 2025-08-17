#!/usr/bin/env python3
"""
pytest設定とフィクスチャ
"""
import pytest
import tempfile
import os
from app import create_app, db
from app.models import Branch, Project


@pytest.fixture(scope='function')
def app():
    """テスト用Flaskアプリケーション"""
    # テスト用の一時データベースファイル
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,  # テスト時はCSRFを無効化
    })
    
    with app.app_context():
        db.create_all()
        yield app
        
    # クリーンアップ
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """テスト用クライアント"""
    return app.test_client()


@pytest.fixture(scope='function')
def app_context(app):
    """アプリケーションコンテキスト"""
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def sample_branch(app_context):
    """テスト用支社データ"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    branch = Branch.create_with_validation(
        branch_code=f'TEST{unique_id}',
        branch_name=f'テスト支社{unique_id}'
    )
    db.session.commit()
    return branch


@pytest.fixture(scope='function')
def sample_branches(app_context):
    """複数のテスト用支社データ"""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    branches = []
    
    # 有効な支社
    branch1 = Branch.create_with_validation(
        branch_code=f'ACTIVE01{unique_id}',
        branch_name=f'アクティブ支社1{unique_id}'
    )
    branch2 = Branch.create_with_validation(
        branch_code=f'ACTIVE02{unique_id}', 
        branch_name=f'アクティブ支社2{unique_id}'
    )
    
    # 無効な支社
    branch3 = Branch.create_with_validation(
        branch_code=f'INACTIVE01{unique_id}',
        branch_name=f'非アクティブ支社{unique_id}'
    )
    branch3.is_active = False
    
    branches.extend([branch1, branch2, branch3])
    db.session.commit()
    
    return branches


@pytest.fixture(scope='function')
def sample_project(app_context, sample_branch):
    """テスト用プロジェクトデータ"""
    project = Project.create_with_validation(
        project_code='TEST-PROJ-001',
        project_name='テストプロジェクト',
        branch_id=sample_branch.id,
        fiscal_year=2024,
        order_probability=100,
        revenue=1500000.00,
        expenses=1200000.00
    )
    db.session.commit()
    return project


@pytest.fixture(scope='function')
def sample_projects(app_context, sample_branches):
    """複数のテスト用プロジェクトデータ"""
    projects = []
    
    for i, branch in enumerate(sample_branches[:2], 1):  # アクティブな支社のみ使用
        project = Project.create_with_validation(
            project_code=f'TEST-PROJ-{i:03d}',
            project_name=f'テストプロジェクト{i}',
            branch_id=branch.id,
            fiscal_year=2024,
            order_probability=100 if i % 2 == 1 else 50,
            revenue=1000000.00 * i,
            expenses=800000.00 * i
        )
        projects.append(project)
    
    db.session.commit()
    return projects