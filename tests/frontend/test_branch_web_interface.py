#!/usr/bin/env python3
"""
支社管理画面のWebインターフェーステスト
"""
import pytest
from app import create_app, db
from app.models import Branch


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


def test_branch_management_workflow(client):
    """支社管理の基本ワークフローテスト"""
    
    # 1. 支社一覧画面にアクセス
    response = client.get('/branches/')
    assert response.status_code == 200
    assert '支社管理' in response.get_data(as_text=True)
    
    # 2. 新規支社作成画面にアクセス
    response = client.get('/branches/new')
    assert response.status_code == 200
    assert '新規支社作成' in response.get_data(as_text=True)
    
    # 3. 支社を作成
    response = client.post('/branches/', data={
        'branch_code': 'TEST001',
        'branch_name': 'テスト支社',
        'is_active': 'on'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'テスト支社' in response.get_data(as_text=True)
    
    # 4. 作成した支社の詳細画面にアクセス
    with client.application.app_context():
        branch = Branch.query.filter_by(branch_code='TEST001').first()
        assert branch is not None
        
        response = client.get(f'/branches/{branch.id}')
        assert response.status_code == 200
        assert 'テスト支社' in response.get_data(as_text=True)
        
        # 5. 支社編集画面にアクセス
        response = client.get(f'/branches/{branch.id}/edit')
        assert response.status_code == 200
        assert 'TEST001' in response.get_data(as_text=True)
        
        # 6. 支社を更新
        response = client.post(f'/branches/{branch.id}/update', data={
            'branch_code': 'TEST001',
            'branch_name': 'テスト支社（更新済み）',
            'is_active': 'on'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert 'テスト支社（更新済み）' in response.get_data(as_text=True)
        
        # 7. 支社の状態を切り替え
        response = client.post(f'/branches/{branch.id}/toggle', follow_redirects=True)
        assert response.status_code == 200
        
        # 8. 支社を削除
        response = client.post(f'/branches/{branch.id}/delete', follow_redirects=True)
        assert response.status_code == 200


def test_branch_api_endpoints(client):
    """支社API エンドポイントのテスト"""
    
    # テスト用支社を作成
    client.post('/branches/', data={
        'branch_code': 'API001',
        'branch_name': 'API テスト支社',
        'is_active': 'on'
    })
    
    # 1. 支社一覧API
    response = client.get('/branches/api/branches')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['data']) > 0
    
    # 2. 支社検索API
    response = client.get('/branches/api/branches/search?branch_name=API')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    
    # 3. 支社選択リストAPI
    response = client.get('/branches/api/branches/select')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])