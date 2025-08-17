"""
Task 20: インポートプレビューと実行機能のテスト
"""
import pytest
import pandas as pd
import os
import tempfile
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import Project, Branch
from app.services.import_service import ImportService


class TestTask20PreviewExecution:
    """Task 20: インポートプレビューと実行機能のテスト"""
    
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
        """テストクライアント"""
        return app.test_client()
    
    @pytest.fixture
    def import_service(self):
        """ImportServiceインスタンス"""
        return ImportService()
    
    @pytest.fixture
    def sample_csv_file(self):
        """サンプルCSVファイル"""
        csv_content = """プロジェクトコード,プロジェクト名,支社名,売上の年度,受注角度,売上,経費
PRJ001,テストプロジェクト1,東京支社,2024,〇,1000000,800000
PRJ002,テストプロジェクト2,大阪支社,2024,△,2000000,1500000
PRJ003,重複プロジェクト,東京支社,2024,×,500000,400000
PRJ003,重複プロジェクト,東京支社,2024,×,500000,400000
INVALID,エラープロジェクト,存在しない支社,2024,無効,abc,def"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
            f.write(csv_content)
            return f.name
    
    @pytest.fixture
    def existing_branch(self, app):
        """既存の支社データ"""
        with app.app_context():
            branch = Branch.create_with_validation(
                branch_code='TKY',
                branch_name='東京支社',
                is_active=True
            )
            return branch
    
    @pytest.fixture
    def existing_project(self, app):
        """既存のプロジェクトデータ"""
        with app.app_context():
            # 支社を作成
            branch = Branch.create_with_validation(
                branch_code='OSK',
                branch_name='大阪支社',
                is_active=True
            )
            # プロジェクトを作成
            project = Project.create_with_validation(
                project_code='EXISTING001',
                project_name='既存プロジェクト',
                branch_id=branch.id,
                fiscal_year=2024,
                order_probability=100,
                revenue=1000000,
                expenses=800000
            )
            return project
    
    def test_enhanced_preview_data_with_validation(self, app, import_service, sample_csv_file, existing_branch):
        """要件4.5, 4.6: プレビューデータの取得と検証機能"""
        with app.app_context():
            column_mapping = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクト名',
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上',
                'expenses': '経費'
            }
            
            result = import_service.get_preview_data(
                sample_csv_file, 
                'csv', 
                column_mapping
            )
            
            # 基本的な成功チェック
            assert result['success'] is True
            assert 'data' in result
            assert 'validation_summary' in result
            assert 'duplicates' in result
            assert 'validation_errors' in result
            
            # 検証サマリーのチェック
            summary = result['validation_summary']
            assert summary['total_rows'] == 5
            assert summary['duplicate_count'] > 0  # 重複があることを確認
            assert summary['error_rows'] > 0  # エラーがあることを確認
            
            # 重複データのチェック
            duplicates = result['duplicates']
            assert len(duplicates) > 0
            duplicate_found = False
            for duplicate in duplicates:
                if duplicate['code'] == 'PRJ003':
                    duplicate_found = True
                    assert len(duplicate['rows']) == 2  # 2行で重複
            assert duplicate_found
            
            # 検証エラーのチェック
            validation_errors = result['validation_errors']
            assert len(validation_errors) > 0
            
            # プレビューデータの検証状態チェック
            for row_data in result['data']:
                assert '_validation' in row_data
                validation = row_data['_validation']
                assert 'has_errors' in validation
                assert 'errors' in validation
    
    def test_duplicate_checking_functionality(self, app, import_service):
        """要件4.6: 重複チェック機能"""
        with app.app_context():
            # 既存プロジェクトを作成
            branch = Branch.create_with_validation(
                branch_code='TKY2',
                branch_name='東京支社2',
                is_active=True
            )
            existing_project = Project.create_with_validation(
                project_code='EXISTING002',
                project_name='既存プロジェクト2',
                branch_id=branch.id,
                fiscal_year=2024,
                order_probability=100,
                revenue=1000000,
                expenses=800000
            )
            
            # 既存プロジェクトと重複するデータを含むCSV
            csv_content = f"""プロジェクトコード,プロジェクト名,支社名,売上の年度,受注角度,売上,経費
{existing_project.project_code},重複プロジェクト,東京支社2,2024,〇,1000000,800000
NEW001,新規プロジェクト,東京支社2,2024,△,2000000,1500000"""
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
                f.write(csv_content)
                temp_file = f.name
            
            try:
                column_mapping = {
                    'project_code': 'プロジェクトコード',
                    'project_name': 'プロジェクト名',
                    'branch_name': '支社名',
                    'fiscal_year': '売上の年度',
                    'order_probability': '受注角度',
                    'revenue': '売上',
                    'expenses': '経費'
                }
                
                result = import_service.get_preview_data(temp_file, 'csv', column_mapping)
                
                # 既存データとの重複が検出されることを確認
                validation_errors = result['validation_errors']
                existing_duplicate_found = False
                
                for error in validation_errors:
                    for error_msg in error['errors']:
                        if f'プロジェクトコード「EXISTING002」は既に存在します' in error_msg:
                            existing_duplicate_found = True
                
                assert existing_duplicate_found
                
            finally:
                os.unlink(temp_file)
    
    def test_enhanced_import_execution(self, app, import_service, sample_csv_file, existing_branch):
        """要件4.7, 4.8: インポート実行と結果表示機能"""
        with app.app_context():
            column_mapping = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクト名',
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上',
                'expenses': '経費'
            }
            
            result = import_service.execute_import(
                sample_csv_file,
                'csv',
                column_mapping
            )
            
            # 基本的な成功チェック
            assert result['success'] is True
            assert 'success_count' in result
            assert 'error_count' in result
            assert 'total_rows' in result
            assert 'success_rate' in result
            assert 'errors' in result
            assert 'successful_projects' in result
            
            # 統計情報のチェック
            assert result['total_rows'] == 5
            assert result['success_count'] > 0  # 少なくとも1件は成功
            assert result['error_count'] > 0   # エラーもある
            assert 0 <= result['success_rate'] <= 100
            
            # エラー詳細のチェック
            errors = result['errors']
            assert len(errors) > 0
            for error in errors:
                assert 'row' in error
                assert 'error' in error
                assert 'type' in error
                assert 'data' in error
            
            # 成功したプロジェクトのチェック
            successful_projects = result['successful_projects']
            assert len(successful_projects) > 0
            for project in successful_projects:
                assert 'row' in project
                assert 'project_code' in project
                assert 'project_name' in project
    
    def test_error_report_generation(self, app, import_service):
        """要件4.9: エラー詳細のダウンロード機能"""
        with app.app_context():
            # サンプルエラーデータ
            errors = [
                {
                    'row': 1,
                    'error': 'プロジェクトコードが空です',
                    'type': 'validation_error',
                    'data': {'project_name': 'テストプロジェクト', 'branch_name': '東京支社'}
                },
                {
                    'row': 2,
                    'error': '受注角度の値が無効です',
                    'type': 'processing_error',
                    'data': {'project_code': 'PRJ002', 'order_probability': '無効値'}
                }
            ]
            
            duplicates = [
                {
                    'type': 'file_duplicate',
                    'code': 'PRJ003',
                    'rows': [3, 4],
                    'message': 'プロジェクトコード「PRJ003」がファイル内で重複しています'
                }
            ]
            
            # エラーレポート生成
            csv_content = import_service.generate_error_report(errors, duplicates)
            
            # CSVヘッダーの確認
            lines = csv_content.strip().split('\n')
            assert lines[0].strip() == '行番号,エラータイプ,エラー内容,データ'
            
            # エラーデータの確認
            assert len(lines) > 1  # ヘッダー以外にデータがある
            
            # 重複エラーが含まれていることを確認
            duplicate_found = False
            for line in lines[1:]:
                if 'PRJ003' in line and '重複エラー' in line:
                    duplicate_found = True
            assert duplicate_found
    
    def test_success_report_generation(self, app, import_service):
        """要件4.9: 成功レポートの生成機能"""
        with app.app_context():
            # サンプル成功データ
            successful_projects = [
                {
                    'row': 1,
                    'project_code': 'PRJ001',
                    'project_name': 'テストプロジェクト1'
                },
                {
                    'row': 2,
                    'project_code': 'PRJ002',
                    'project_name': 'テストプロジェクト2'
                }
            ]
            
            # 成功レポート生成
            csv_content = import_service.generate_success_report(successful_projects)
            
            # CSVヘッダーの確認
            lines = csv_content.strip().split('\n')
            assert lines[0].strip() == '行番号,プロジェクトコード,プロジェクト名'
            
            # 成功データの確認
            assert len(lines) == 3  # ヘッダー + 2行のデータ
            assert 'PRJ001' in lines[1]
            assert 'PRJ002' in lines[2]
    
    def test_preview_route_with_validation(self, app, client, existing_branch):
        """プレビュールートの検証機能テスト"""
        with app.app_context():
            with client.session_transaction() as sess:
                # セッションにテストデータを設定
                sess['import_file'] = '/tmp/test.csv'
                sess['import_type'] = 'csv'
                sess['import_columns'] = ['プロジェクトコード', 'プロジェクト名']
                sess['import_sample_data'] = [{'プロジェクトコード': 'PRJ001', 'プロジェクト名': 'テスト'}]
                sess['import_row_count'] = 1
                sess['import_column_mapping'] = {
                    'project_code': 'プロジェクトコード',
                    'project_name': 'プロジェクト名'
                }
            
            # ImportServiceをモック
            with patch('app.import_routes.ImportService') as mock_service:
                mock_instance = mock_service.return_value
                mock_instance.get_preview_data.return_value = {
                    'success': True,
                    'data': [{'project_code': 'PRJ001', '_validation': {'has_errors': False, 'errors': []}}],
                    'row_count': 1,
                    'validation_summary': {
                        'total_rows': 1,
                        'valid_rows': 1,
                        'error_rows': 0,
                        'duplicate_count': 0,
                        'success_rate': 100.0
                    },
                    'duplicates': [],
                    'validation_errors': []
                }
                
                response = client.get('/import/preview')
                
                assert response.status_code == 200
                assert b'validation_summary' in response.data or b'100.0' in response.data
    
    def test_error_download_routes(self, app, client):
        """エラーレポートダウンロードルートのテスト"""
        with app.app_context():
            with client.session_transaction() as sess:
                sess['import_errors'] = [
                    {
                        'row': 1,
                        'error': 'テストエラー',
                        'type': 'validation_error',
                        'data': {'project_code': 'PRJ001'}
                    }
                ]
                sess['import_duplicates'] = []
            
            response = client.get('/import/download_error_report')
            
            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
            assert 'attachment' in response.headers['Content-Disposition']
    
    def test_success_download_routes(self, app, client):
        """成功レポートダウンロードルートのテスト"""
        with app.app_context():
            with client.session_transaction() as sess:
                sess['import_successful_projects'] = [
                    {
                        'row': 1,
                        'project_code': 'PRJ001',
                        'project_name': 'テストプロジェクト'
                    }
                ]
            
            response = client.get('/import/download_success_report')
            
            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
            assert 'attachment' in response.headers['Content-Disposition']
    
    def cleanup_files(self, sample_csv_file):
        """テスト後のクリーンアップ"""
        if os.path.exists(sample_csv_file):
            os.unlink(sample_csv_file)