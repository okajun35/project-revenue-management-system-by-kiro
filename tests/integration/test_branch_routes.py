#!/usr/bin/env python3
"""
支社ルートのテスト
"""
import pytest
import tempfile
import os
import json
from app import create_app, db
from app.models import Branch


@pytest.fixture
def app():
    """テスト用アプリケーション"""
    # テスト用の一時データベースファイルを作成
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['DATABASE'] = db_path
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """アプリケーションコンテキスト"""
    with app.app_context():
        yield app


class TestBranchRoutes:
    """支社ルートのテスト"""
    
    def test_branch_index_route(self, client, app_context):
        """支社一覧ページのテスト"""
        # テストデータを作成
        Branch.create_with_validation(
            branch_code='TKY001',
            branch_name='東京支社',
            is_active=True
        )
        
        response = client.get('/branches/')
        assert response.status_code == 200
    
    def test_branch_new_route(self, client, app_context):
        """新規支社作成ページのテスト"""
        response = client.get('/branches/new')
        assert response.status_code == 200
    
    def test_branch_create_route(self, client, app_context):
        """支社作成処理のテスト"""
        response = client.post('/branches/', data={
            'branch_code': 'TKY001',
            'branch_name': '東京支社',
            'is_active': 'on'
        })
        
        # リダイレクトされることを確認
        assert response.status_code == 302
        
        # 支社が作成されたことを確認
        branch = Branch.query.filter_by(branch_code='TKY001').first()
        assert branch is not None
        assert branch.branch_name == '東京支社'
        assert branch.is_active is True
    
    def test_branch_api_branches_route(self, client, app_context):
        """支社一覧API のテスト"""
        # テストデータを作成
        Branch.create_with_validation(
            branch_code='TKY001',
            branch_name='東京支社',
            is_active=True
        )
        Branch.create_with_validation(
            branch_code='OSK001',
            branch_name='大阪支社',
            is_active=False
        )
        
        response = client.get('/branches/api/branches')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 2
    
    def test_branch_api_search_route(self, client, app_context):
        """支社検索API のテスト"""
        # テストデータを作成
        Branch.create_with_validation(
            branch_code='TKY001',
            branch_name='東京支社',
            is_active=True
        )
        
        response = client.get('/branches/api/branches/search?branch_code=TKY')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['branch_code'] == 'TKY001'
    
    def test_branch_api_select_route(self, client, app_context):
        """選択リスト用支社API のテスト"""
        # 有効な支社を作成
        Branch.create_with_validation(
            branch_code='TKY001',
            branch_name='東京支社',
            is_active=True
        )
        
        # 無効な支社を作成（選択リストには含まれない）
        Branch.create_with_validation(
            branch_code='OSK001',
            branch_name='大阪支社',
            is_active=False
        )
        
        response = client.get('/branches/api/branches/select')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['data']) == 1  # 有効な支社のみ
        assert data['data'][0]['branch_code'] == 'TKY001'
        assert 'display_name' in data['data'][0]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])