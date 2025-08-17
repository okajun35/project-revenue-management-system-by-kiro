import pytest
import json
import io
from datetime import datetime
from app import create_app, db
from app.models import Project, Branch, FiscalYear


class TestBackupRestore:
    """バックアップ・リストア機能のテスト"""
    
    @pytest.fixture
    def app(self):
        """テスト用アプリケーション"""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """テスト用クライアント"""
        return app.test_client()
    
    @pytest.fixture
    def sample_data(self, app):
        """テスト用サンプルデータ"""
        with app.app_context():
            # 年度データ
            fiscal_year = FiscalYear(year=2024, year_name="2024年度", is_active=True)
            db.session.add(fiscal_year)
            
            # 支社データ
            branch = Branch(branch_code="TKY", branch_name="東京本社", is_active=True)
            db.session.add(branch)
            db.session.flush()
            
            # プロジェクトデータ
            project = Project(
                project_code="PRJ001",
                project_name="テストプロジェクト",
                branch_id=branch.id,
                fiscal_year=2024,
                order_probability=100,
                revenue=1000000,
                expenses=800000
            )
            db.session.add(project)
            db.session.commit()
            
            return {
                'fiscal_year': fiscal_year,
                'branch': branch,
                'project': project
            }
    
    def test_backup_info_api(self, client, sample_data):
        """バックアップ情報API のテスト"""
        response = client.get('/backup/info')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert data['data']['projects_count'] == 1
        assert data['data']['branches_count'] == 1
        assert data['data']['fiscal_years_count'] == 1
        assert data['data']['total_records'] == 3
        assert data['data']['latest_update'] is not None
    
    def test_create_backup(self, client, sample_data):
        """バックアップ作成のテスト"""
        response = client.get('/backup/create')
        
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        # レスポンスヘッダーをチェック
        assert 'attachment' in response.headers.get('Content-Disposition', '')
        assert 'project_system_backup_' in response.headers.get('Content-Disposition', '')
        
        # JSONデータを解析
        backup_data = json.loads(response.data)
        
        # バックアップ情報をチェック
        assert 'backup_info' in backup_data
        assert 'data' in backup_data
        assert 'statistics' in backup_data
        
        # データ内容をチェック
        data_section = backup_data['data']
        assert len(data_section['projects']) == 1
        assert len(data_section['branches']) == 1
        assert len(data_section['fiscal_years']) == 1
        
        # プロジェクトデータの内容をチェック
        project_data = data_section['projects'][0]
        assert project_data['project_code'] == 'PRJ001'
        assert project_data['project_name'] == 'テストプロジェクト'
        assert project_data['fiscal_year'] == 2024
        assert project_data['order_probability'] == 100.0
        assert project_data['revenue'] == 1000000.0
        assert project_data['expenses'] == 800000.0
        
        # 支社データの内容をチェック
        branch_data = data_section['branches'][0]
        assert branch_data['branch_code'] == 'TKY'
        assert branch_data['branch_name'] == '東京本社'
        assert branch_data['is_active'] is True
        
        # 年度データの内容をチェック
        fiscal_year_data = data_section['fiscal_years'][0]
        assert fiscal_year_data['year'] == 2024
        assert fiscal_year_data['year_name'] == '2024年度'
        assert fiscal_year_data['is_active'] is True
    
    def test_upload_valid_backup_file(self, client, sample_data):
        """有効なバックアップファイルのアップロードテスト"""
        # バックアップファイルを作成
        backup_response = client.get('/backup/create')
        backup_data = json.loads(backup_response.data)
        
        # ファイルとしてアップロード
        backup_json = json.dumps(backup_data, ensure_ascii=False)
        file_data = io.BytesIO(backup_json.encode('utf-8'))
        
        response = client.post('/backup/upload', data={
            'backup_file': (file_data, 'test_backup.json')
        }, content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert data['success'] is True
        assert 'session_key' in data
        assert 'preview' in data
        
        # プレビュー情報をチェック
        preview = data['preview']
        assert 'backup_info' in preview
        assert 'current_data' in preview
        assert 'backup_data' in preview
        
        assert preview['current_data']['projects'] == 1
        assert preview['backup_data']['projects'] == 1
    
    def test_upload_invalid_json_file(self, client):
        """無効なJSONファイルのアップロードテスト"""
        # 無効なJSONファイル
        invalid_json = "{ invalid json content"
        file_data = io.BytesIO(invalid_json.encode('utf-8'))
        
        response = client.post('/backup/upload', data={
            'backup_file': (file_data, 'invalid.json')
        }, content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'ファイル形式が正しくありません' in data['error']
    
    def test_upload_invalid_backup_structure(self, client):
        """無効なバックアップ構造のファイルアップロードテスト"""
        # 構造が正しくないバックアップファイル
        invalid_backup = {
            "invalid_structure": True
        }
        
        backup_json = json.dumps(invalid_backup)
        file_data = io.BytesIO(backup_json.encode('utf-8'))
        
        response = client.post('/backup/upload', data={
            'backup_file': (file_data, 'invalid_backup.json')
        }, content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'バックアップファイルの形式が正しくありません' in data['error']
    
    def test_upload_non_json_file(self, client):
        """JSON以外のファイルアップロードテスト"""
        # テキストファイル
        text_content = "This is not a JSON file"
        file_data = io.BytesIO(text_content.encode('utf-8'))
        
        response = client.post('/backup/upload', data={
            'backup_file': (file_data, 'test.txt')
        }, content_type='multipart/form-data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'JSONファイルを選択してください' in data['error']
    
    def test_restore_execution(self, client, sample_data):
        """リストア実行のテスト"""
        # まず現在のデータをバックアップ
        backup_response = client.get('/backup/create')
        original_backup = json.loads(backup_response.data)
        
        # 新しいデータを追加
        with client.application.app_context():
            new_branch = Branch(branch_code="OSK", branch_name="大阪支社", is_active=True)
            db.session.add(new_branch)
            db.session.flush()
            
            new_project = Project(
                project_code="PRJ002",
                project_name="新規プロジェクト",
                branch_id=new_branch.id,
                fiscal_year=2024,
                order_probability=50,
                revenue=2000000,
                expenses=1500000
            )
            db.session.add(new_project)
            db.session.commit()
        
        # データが増えていることを確認
        info_response = client.get('/backup/info')
        info_data = json.loads(info_response.data)
        assert info_data['data']['projects_count'] == 2
        assert info_data['data']['branches_count'] == 2
        
        # 元のバックアップをアップロード
        backup_json = json.dumps(original_backup, ensure_ascii=False)
        file_data = io.BytesIO(backup_json.encode('utf-8'))
        
        upload_response = client.post('/backup/upload', data={
            'backup_file': (file_data, 'restore_test.json')
        }, content_type='multipart/form-data')
        
        upload_data = json.loads(upload_response.data)
        session_key = upload_data['session_key']
        
        # リストアを実行
        restore_response = client.post('/backup/restore', 
                                     json={
                                         'session_key': session_key,
                                         'confirm': True
                                     })
        
        assert restore_response.status_code == 200
        restore_data = json.loads(restore_response.data)
        
        assert restore_data['success'] is True
        assert 'statistics' in restore_data
        
        # データが元に戻っていることを確認
        final_info_response = client.get('/backup/info')
        final_info_data = json.loads(final_info_response.data)
        assert final_info_data['data']['projects_count'] == 1
        assert final_info_data['data']['branches_count'] == 1
        
        # 具体的なデータ内容を確認
        with client.application.app_context():
            projects = Project.query.all()
            assert len(projects) == 1
            assert projects[0].project_code == 'PRJ001'
            
            branches = Branch.query.all()
            assert len(branches) == 1
            assert branches[0].branch_code == 'TKY'
    
    def test_restore_without_session_key(self, client):
        """セッションキーなしでのリストア実行テスト"""
        response = client.post('/backup/restore', json={
            'confirm': True
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'セッションキーが指定されていません' in data['error']
    
    def test_restore_without_confirmation(self, client):
        """確認なしでのリストア実行テスト"""
        response = client.post('/backup/restore', json={
            'session_key': 'test_key',
            'confirm': False
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert data['success'] is False
        assert 'リストア実行の確認が必要です' in data['error']
    
    def test_backup_index_page(self, client):
        """バックアップ管理画面のテスト"""
        response = client.get('/backup/')
        
        assert response.status_code == 200
        assert 'バックアップ・リストア管理' in response.data.decode('utf-8')
        assert 'バックアップファイルを作成・ダウンロード' in response.data.decode('utf-8')
        assert 'データリストア' in response.data.decode('utf-8')