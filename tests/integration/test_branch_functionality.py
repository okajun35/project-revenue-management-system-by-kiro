#!/usr/bin/env python3
"""
支社機能のテスト
"""
import pytest
import tempfile
import os
from app import create_app, db
from app.models import Branch, ValidationError
from app.services.branch_service import BranchService


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


class TestBranchModel:
    """支社モデルのテスト"""
    
    def test_branch_creation_success(self, app_context):
        """正常な支社作成のテスト"""
        branch_data = {
            'branch_code': 'TKY001',
            'branch_name': '東京支社',
            'is_active': True
        }
        
        branch = Branch.create_with_validation(**branch_data)
        
        assert branch.id is not None
        assert branch.branch_code == 'TKY001'
        assert branch.branch_name == '東京支社'
        assert branch.is_active is True
        assert branch.created_at is not None
        assert branch.updated_at is not None
    
    def test_branch_validation_required_fields(self, app_context):
        """必須項目の検証テスト"""
        # 支社コードが空の場合
        with pytest.raises(ValidationError) as exc_info:
            Branch.create_with_validation(branch_code='', branch_name='テスト支社')
        assert '支社コードは必須です' in str(exc_info.value)
        
        # 支社名が空の場合
        with pytest.raises(ValidationError) as exc_info:
            Branch.create_with_validation(branch_code='TEST001', branch_name='')
        assert '支社名は必須です' in str(exc_info.value)
    
    def test_branch_validation_length_limits(self, app_context):
        """文字数制限の検証テスト"""
        # 支社コードが20文字を超える場合
        long_code = 'A' * 21
        with pytest.raises(ValidationError) as exc_info:
            Branch.create_with_validation(branch_code=long_code, branch_name='テスト支社')
        assert '支社コードは20文字以内' in str(exc_info.value)
        
        # 支社名が100文字を超える場合
        long_name = 'あ' * 101
        with pytest.raises(ValidationError) as exc_info:
            Branch.create_with_validation(branch_code='TEST001', branch_name=long_name)
        assert '支社名は100文字以内' in str(exc_info.value)
    
    def test_branch_code_format_validation(self, app_context):
        """支社コード形式の検証テスト"""
        # 無効な文字を含む支社コード
        invalid_codes = ['TEST 001', 'TEST@001', 'TEST#001', 'テスト001']
        
        for invalid_code in invalid_codes:
            with pytest.raises(ValidationError) as exc_info:
                Branch.create_with_validation(branch_code=invalid_code, branch_name='テスト支社')
            assert '英数字、ハイフン、アンダースコアのみ使用可能' in str(exc_info.value)
    
    def test_branch_code_uniqueness(self, app_context):
        """支社コードの重複チェックテスト"""
        # 最初の支社を作成
        Branch.create_with_validation(branch_code='TKY001', branch_name='東京支社')
        
        # 同じ支社コードで作成を試行
        with pytest.raises(ValidationError) as exc_info:
            Branch.create_with_validation(branch_code='TKY001', branch_name='大阪支社')
        assert '支社コードは既に使用されています' in str(exc_info.value)
    
    def test_branch_name_uniqueness(self, app_context):
        """支社名の重複チェックテスト"""
        # 最初の支社を作成
        Branch.create_with_validation(branch_code='TKY001', branch_name='東京支社')
        
        # 同じ支社名で作成を試行
        with pytest.raises(ValidationError) as exc_info:
            Branch.create_with_validation(branch_code='TKY002', branch_name='東京支社')
        assert '支社名は既に使用されています' in str(exc_info.value)
    
    def test_branch_update_success(self, app_context):
        """支社更新の成功テスト"""
        # 支社を作成
        branch = Branch.create_with_validation(
            branch_code='TKY001', 
            branch_name='東京支社',
            is_active=True
        )
        original_updated_at = branch.updated_at
        
        # 支社を更新
        updated_branch = branch.update_with_validation(
            branch_name='東京本社',
            is_active=False
        )
        
        assert updated_branch.branch_name == '東京本社'
        assert updated_branch.is_active is False
        assert updated_branch.updated_at > original_updated_at
    
    def test_branch_toggle_status(self, app_context):
        """支社状態切り替えテスト"""
        # 支社を作成（有効状態）
        branch = Branch.create_with_validation(
            branch_code='TKY001', 
            branch_name='東京支社',
            is_active=True
        )
        
        # 無効に切り替え
        branch.toggle_active_status()
        assert branch.is_active is False
        
        # 有効に切り替え
        branch.toggle_active_status()
        assert branch.is_active is True
    
    def test_get_active_branches(self, app_context):
        """有効支社取得テスト"""
        # 有効な支社を作成
        Branch.create_with_validation(branch_code='TKY001', branch_name='東京支社', is_active=True)
        Branch.create_with_validation(branch_code='OSK001', branch_name='大阪支社', is_active=True)
        
        # 無効な支社を作成
        Branch.create_with_validation(branch_code='NGY001', branch_name='名古屋支社', is_active=False)
        
        # 有効な支社のみを取得
        active_branches = Branch.get_active_branches()
        
        assert len(active_branches) == 2
        assert all(branch.is_active for branch in active_branches)
    
    def test_branch_search(self, app_context):
        """支社検索テスト"""
        # テストデータを作成
        Branch.create_with_validation(branch_code='TKY001', branch_name='東京支社', is_active=True)
        Branch.create_with_validation(branch_code='OSK001', branch_name='大阪支社', is_active=True)
        Branch.create_with_validation(branch_code='NGY001', branch_name='名古屋支社', is_active=False)
        
        # 支社コードで検索
        results = Branch.search_branches(branch_code='TKY').all()
        assert len(results) == 1
        assert results[0].branch_code == 'TKY001'
        
        # 支社名で検索
        results = Branch.search_branches(branch_name='支社').all()
        assert len(results) == 3
        
        # 有効状態で検索
        results = Branch.search_branches(is_active=True).all()
        assert len(results) == 2
        assert all(branch.is_active for branch in results)


class TestBranchService:
    """支社サービスのテスト"""
    
    def test_create_branch_service(self, app_context):
        """支社作成サービスのテスト"""
        branch_data = {
            'branch_code': 'TKY001',
            'branch_name': '東京支社',
            'is_active': True
        }
        
        branch = BranchService.create_branch(branch_data)
        
        assert branch.branch_code == 'TKY001'
        assert branch.branch_name == '東京支社'
        assert branch.is_active is True
    
    def test_get_branch_by_id(self, app_context):
        """ID による支社取得テスト"""
        branch = Branch.create_with_validation(
            branch_code='TKY001', 
            branch_name='東京支社'
        )
        
        retrieved_branch = BranchService.get_branch_by_id(branch.id)
        
        assert retrieved_branch is not None
        assert retrieved_branch.id == branch.id
        assert retrieved_branch.branch_code == 'TKY001'
    
    def test_get_branch_by_code(self, app_context):
        """支社コードによる支社取得テスト"""
        Branch.create_with_validation(
            branch_code='TKY001', 
            branch_name='東京支社'
        )
        
        retrieved_branch = BranchService.get_branch_by_code('TKY001')
        
        assert retrieved_branch is not None
        assert retrieved_branch.branch_code == 'TKY001'
    
    def test_update_branch_service(self, app_context):
        """支社更新サービスのテスト"""
        branch = Branch.create_with_validation(
            branch_code='TKY001', 
            branch_name='東京支社'
        )
        
        update_data = {
            'branch_name': '東京本社',
            'is_active': False
        }
        
        updated_branch = BranchService.update_branch(branch.id, update_data)
        
        assert updated_branch.branch_name == '東京本社'
        assert updated_branch.is_active is False
    
    def test_delete_branch_service(self, app_context):
        """支社削除サービスのテスト"""
        branch = Branch.create_with_validation(
            branch_code='TKY001', 
            branch_name='東京支社'
        )
        branch_id = branch.id
        
        result = BranchService.delete_branch(branch_id)
        
        assert result is True
        assert BranchService.get_branch_by_id(branch_id) is None
    
    def test_validate_branch_data(self, app_context):
        """支社データ検証サービスのテスト"""
        # 有効なデータ
        valid_data = {
            'branch_code': 'TKY001',
            'branch_name': '東京支社',
            'is_active': True
        }
        
        errors = BranchService.validate_branch_data(valid_data)
        assert len(errors) == 0
        
        # 無効なデータ
        invalid_data = {
            'branch_code': '',
            'branch_name': '',
            'is_active': True
        }
        
        errors = BranchService.validate_branch_data(invalid_data)
        assert len(errors) == 2
        assert any('支社コードは必須です' in error.message for error in errors)
        assert any('支社名は必須です' in error.message for error in errors)
    
    def test_get_branch_statistics(self, app_context):
        """支社統計情報取得テスト"""
        # テストデータを作成
        Branch.create_with_validation(branch_code='TKY001', branch_name='東京支社', is_active=True)
        Branch.create_with_validation(branch_code='OSK001', branch_name='大阪支社', is_active=True)
        Branch.create_with_validation(branch_code='NGY001', branch_name='名古屋支社', is_active=False)
        
        stats = BranchService.get_branch_statistics()
        
        assert stats['total_branches'] == 3
        assert stats['active_branches'] == 2
        assert stats['inactive_branches'] == 1
    
    def test_get_branches_for_select(self, app_context):
        """選択リスト用支社データ取得テスト"""
        # 有効な支社を作成
        Branch.create_with_validation(branch_code='TKY001', branch_name='東京支社', is_active=True)
        Branch.create_with_validation(branch_code='OSK001', branch_name='大阪支社', is_active=True)
        
        # 無効な支社を作成（選択リストには含まれない）
        Branch.create_with_validation(branch_code='NGY001', branch_name='名古屋支社', is_active=False)
        
        select_data = BranchService.get_branches_for_select()
        
        assert len(select_data) == 2
        assert all('display_name' in item for item in select_data)
        assert select_data[0]['display_name'] == 'OSK001 - 大阪支社'  # アルファベット順
        assert select_data[1]['display_name'] == 'TKY001 - 東京支社'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])