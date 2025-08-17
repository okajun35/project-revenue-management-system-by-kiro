"""
プロジェクト削除機能の統合テスト
"""
import pytest
from flask import url_for
from app.models import Project, Branch
from app import db
import uuid


class TestProjectDeletion:
    """プロジェクト削除機能のテストクラス"""
    
    def test_delete_project_success(self, client, sample_branch):
        """プロジェクト削除成功のテスト"""
        # ユニークなプロジェクトコードを生成
        unique_code = f'TEST-DELETE-{uuid.uuid4().hex[:8].upper()}'
        
        # テスト用プロジェクトを作成
        project = Project.create_with_validation(
            project_code=unique_code,
            project_name='削除テスト用プロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        project_id = project.id
        project_name = project.project_name
        
        # 削除前にプロジェクトが存在することを確認
        assert Project.query.get(project_id) is not None
        
        # 削除リクエストを送信
        response = client.post(
            url_for('projects.delete', project_id=project_id),
            follow_redirects=True
        )
        
        # レスポンスの確認
        assert response.status_code == 200
        
        # プロジェクトが削除されていることを確認
        deleted_project = Project.query.get(project_id)
        assert deleted_project is None
        
        # 成功メッセージが表示されていることを確認
        assert '正常に削除しました' in response.get_data(as_text=True)
        assert project_name in response.get_data(as_text=True)
    
    def test_delete_nonexistent_project(self, client):
        """存在しないプロジェクトの削除テスト"""
        # 存在しないプロジェクトIDで削除リクエスト
        response = client.post(
            url_for('projects.delete', project_id=99999),
            follow_redirects=True
        )
        
        # 404エラーが返されることを確認
        assert response.status_code == 404
    
    def test_delete_project_get_method_not_allowed(self, client, sample_project):
        """GETメソッドでの削除リクエストが拒否されることのテスト"""
        response = client.get(
            url_for('projects.delete', project_id=sample_project.id)
        )
        
        # 405 Method Not Allowedが返されることを確認
        assert response.status_code == 405
    
    def test_delete_project_database_error_handling(self, client, sample_branch, monkeypatch):
        """データベースエラー時のハンドリングテスト"""
        # ユニークなプロジェクトコードを生成
        unique_code = f'TEST-ERROR-{uuid.uuid4().hex[:8].upper()}'
        
        # テスト用プロジェクトを作成
        project = Project.create_with_validation(
            project_code=unique_code,
            project_name='エラーテスト用プロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        
        # データベースエラーをシミュレート
        def mock_commit():
            raise Exception("Database error")
        
        monkeypatch.setattr(db.session, 'commit', mock_commit)
        
        # 削除リクエストを送信
        response = client.post(
            url_for('projects.delete', project_id=project.id),
            follow_redirects=True
        )
        
        # レスポンスの確認
        assert response.status_code == 200
        
        # エラーメッセージが表示されていることを確認
        assert 'エラーが発生しました' in response.get_data(as_text=True)
        
        # プロジェクトが削除されていないことを確認（rollbackされるため）
        # 新しいセッションで確認
        db.session.rollback()
        project = Project.query.get(project.id)
        assert project is not None
    
    def test_delete_project_model_method(self, sample_branch):
        """Projectモデルのdelete_with_validationメソッドのテスト"""
        # ユニークなプロジェクトコードを生成
        unique_code = f'TEST-MODEL-{uuid.uuid4().hex[:8].upper()}'
        
        # テスト用プロジェクトを作成
        project = Project.create_with_validation(
            project_code=unique_code,
            project_name='モデルテスト用プロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        
        project_id = project.id
        project_name = project.project_name
        project_code = project.project_code
        
        # 削除前にプロジェクトが存在することを確認
        assert Project.query.get(project_id) is not None
        
        # delete_with_validationメソッドを実行
        result = project.delete_with_validation()
        
        # 結果の確認
        assert result['success'] is True
        assert result['project_name'] == project_name
        assert result['project_code'] == project_code
        
        # プロジェクトが削除されていることを確認
        deleted_project = Project.query.get(project_id)
        assert deleted_project is None
    
    def test_delete_project_model_method_database_error(self, sample_branch, monkeypatch):
        """Projectモデルのdelete_with_validationメソッドでのデータベースエラーテスト"""
        # ユニークなプロジェクトコードを生成
        unique_code = f'TEST-DB-ERR-{uuid.uuid4().hex[:8].upper()}'
        
        # テスト用プロジェクトを作成
        project = Project.create_with_validation(
            project_code=unique_code,
            project_name='DBエラーテスト用プロジェクト',
            branch_id=sample_branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        
        # データベースエラーをシミュレート
        def mock_commit():
            raise Exception("Database error")
        
        monkeypatch.setattr(db.session, 'commit', mock_commit)
        
        # delete_with_validationメソッドを実行してエラーが発生することを確認
        with pytest.raises(Exception) as exc_info:
            project.delete_with_validation()
        
        assert 'プロジェクトの削除中にエラーが発生しました' in str(exc_info.value)
        
        # プロジェクトが削除されていないことを確認（rollbackされるため）
        db.session.rollback()
        project_check = Project.query.get(project.id)
        assert project_check is not None