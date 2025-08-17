"""
Task 21: Excelインポート機能のテスト
"""
import pytest
import pandas as pd
import os
import tempfile
from openpyxl import Workbook
from app.services.import_service import ImportService
from app.models import Project, Branch
from app import create_app, db


@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションを作成"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """テスト用のクライアントを作成"""
    return app.test_client()

class TestExcelImport:
    """Excelインポート機能のテスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される"""
        self.import_service = ImportService()
    
    def teardown_method(self):
        """各テストメソッドの後に実行される"""
        # テストデータをクリーンアップ
        try:
            Project.query.delete()
            Branch.query.filter_by(branch_code='TEST').delete()
            db.session.commit()
        except:
            pass
    
    def create_test_excel_file(self, data, sheet_names=None):
        """テスト用のExcelファイルを作成"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            if sheet_names is None:
                sheet_names = ['Sheet1']
            
            for i, sheet_name in enumerate(sheet_names):
                if i < len(data):
                    df = pd.DataFrame(data[i])
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    # 空のシート
                    pd.DataFrame().to_excel(writer, sheet_name=sheet_name, index=False)
        
        return temp_file.name
    
    def test_excel_file_validation_success(self, app):
        """正常なExcelファイルの検証テスト"""
        with app.app_context():
        # テストデータ
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'Excelテストプロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        filepath = self.create_test_excel_file([test_data])
        
        try:
            result = self.import_service.validate_file(filepath, 'excel')
            
            assert result['success'] is True
            assert result['row_count'] == 1
            assert 'project_code' in result['columns']
            assert 'excel_info' in result
            assert result['excel_info']['success'] is True
            assert len(result['excel_info']['sheets']) == 1
            
        finally:
            os.unlink(filepath)
    
    def test_excel_file_validation_multiple_sheets(self):
        """複数シートを持つExcelファイルの検証テスト"""
        # テストデータ
        sheet1_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'シート1プロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        sheet2_data = [{
            'プロジェクトコード': 'EXCEL002',
            'プロジェクト名': 'シート2プロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '△',
            '売上': 2000000,
            '経費': 1500000
        }]
        
        filepath = self.create_test_excel_file(
            [sheet1_data, sheet2_data], 
            ['データシート1', 'データシート2']
        )
        
        try:
            result = self.import_service.validate_file(filepath, 'excel')
            
            assert result['success'] is True
            assert result['excel_info']['sheet_count'] == 2
            assert result['excel_info']['sheets'][0]['name'] == 'データシート1'
            assert result['excel_info']['sheets'][1]['name'] == 'データシート2'
            assert result['excel_info']['sheets'][0]['has_data'] is True
            assert result['excel_info']['sheets'][1]['has_data'] is True
            
        finally:
            os.unlink(filepath)
    
    def test_excel_file_validation_with_sheet_selection(self):
        """特定シートを指定したExcelファイルの検証テスト"""
        # テストデータ
        sheet1_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'シート1プロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        sheet2_data = [{
            'プロジェクトコード': 'EXCEL002',
            'プロジェクト名': 'シート2プロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '△',
            '売上': 2000000,
            '経費': 1500000
        }]
        
        filepath = self.create_test_excel_file(
            [sheet1_data, sheet2_data], 
            ['Sheet1', 'Sheet2']
        )
        
        try:
            # Sheet2を指定して検証
            result = self.import_service.validate_file(filepath, 'excel', sheet_name='Sheet2')
            
            assert result['success'] is True
            assert result['row_count'] == 1
            assert result['selected_sheet'] == 'Sheet2'
            assert result['sample_data'][0]['project_code'] == 'EXCEL002'
            
        finally:
            os.unlink(filepath)
    
    def test_excel_file_validation_invalid_sheet(self):
        """存在しないシートを指定した場合のテスト"""
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'テストプロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        filepath = self.create_test_excel_file([test_data])
        
        try:
            result = self.import_service.validate_file(filepath, 'excel', sheet_name='NonExistentSheet')
            
            assert result['success'] is False
            assert '指定されたシート「NonExistentSheet」が見つかりません' in result['error']
            
        finally:
            os.unlink(filepath)
    
    def test_excel_sheets_info_retrieval(self):
        """Excelシート情報取得のテスト"""
        # テストデータ
        sheet1_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'シート1プロジェクト',
            '支社名': 'テスト支社'
        }]
        
        # 空のシート2
        sheet2_data = []
        
        filepath = self.create_test_excel_file(
            [sheet1_data, sheet2_data], 
            ['データあり', '空シート']
        )
        
        try:
            result = self.import_service.get_excel_sheets(filepath)
            
            assert result['success'] is True
            assert result['sheet_count'] == 2
            
            # データありシート
            data_sheet = result['sheets'][0]
            assert data_sheet['name'] == 'データあり'
            assert data_sheet['has_data'] is True
            assert len(data_sheet['headers']) > 0
            
            # 空シート
            empty_sheet = result['sheets'][1]
            assert empty_sheet['name'] == '空シート'
            assert empty_sheet['has_data'] is False
            
        finally:
            os.unlink(filepath)
    
    def test_excel_sheet_validation(self):
        """特定Excelシートの検証テスト"""
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'テストプロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        filepath = self.create_test_excel_file([test_data], ['TestSheet'])
        
        try:
            result = self.import_service.validate_excel_sheet(filepath, 'TestSheet')
            
            assert result['success'] is True
            assert result['row_count'] == 1
            assert 'project_code' in result['columns']
            assert len(result['sample_data']) == 1
            
        finally:
            os.unlink(filepath)
    
    def test_excel_preview_data_with_sheet(self):
        """Excelシート指定でのプレビューデータ取得テスト"""
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'テストプロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }, {
            'プロジェクトコード': 'EXCEL002',
            'プロジェクト名': 'テストプロジェクト2',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '△',
            '売上': 2000000,
            '経費': 1500000
        }]
        
        filepath = self.create_test_excel_file([test_data], ['TestSheet'])
        
        try:
            # 列マッピング
            column_mapping = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクト名',
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上',
                'expenses': '経費'
            }
            
            result = self.import_service.get_preview_data(
                filepath, 'excel', column_mapping, sheet_name='TestSheet'
            )
            
            assert result['success'] is True
            assert result['row_count'] == 2
            assert len(result['data']) == 2
            assert result['data'][0]['project_code'] == 'EXCEL001'
            assert result['data'][1]['project_code'] == 'EXCEL002'
            
        finally:
            os.unlink(filepath)
    
    def test_excel_import_execution_with_sheet(self):
        """Excelシート指定でのインポート実行テスト"""
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'Excelテストプロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        filepath = self.create_test_excel_file([test_data], ['ImportSheet'])
        
        try:
            # 列マッピング
            column_mapping = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクト名',
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上',
                'expenses': '経費'
            }
            
            result = self.import_service.execute_import(
                filepath, 'excel', column_mapping, sheet_name='ImportSheet'
            )
            
            assert result['success'] is True
            assert result['success_count'] == 1
            assert result['error_count'] == 0
            
            # データベースに保存されているかチェック
            project = Project.query.filter_by(project_code='EXCEL001').first()
            assert project is not None
            assert project.project_name == 'Excelテストプロジェクト'
            assert project.revenue == 1000000
            
        finally:
            os.unlink(filepath)
    
    def test_excel_file_validation_corrupted_file(self):
        """破損したExcelファイルの検証テスト"""
        # 無効なExcelファイルを作成
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        temp_file.write(b'invalid excel content')
        temp_file.close()
        
        try:
            result = self.import_service.validate_file(temp_file.name, 'excel')
            
            assert result['success'] is False
            assert 'Excelファイルが破損している' in result['error'] or 'ファイル読み込みエラー' in result['error']
            
        finally:
            os.unlink(temp_file.name)
    
    def test_excel_import_with_japanese_sheet_names(self):
        """日本語シート名を持つExcelファイルのテスト"""
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': '日本語シートテスト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }]
        
        filepath = self.create_test_excel_file([test_data], ['プロジェクトデータ'])
        
        try:
            result = self.import_service.validate_file(filepath, 'excel', sheet_name='プロジェクトデータ')
            
            assert result['success'] is True
            assert result['selected_sheet'] == 'プロジェクトデータ'
            assert result['row_count'] == 1
            
        finally:
            os.unlink(filepath)
    
    def test_excel_import_with_empty_cells(self):
        """空のセルを含むExcelファイルのテスト"""
        # 一部のセルが空のテストデータ
        test_data = [{
            'プロジェクトコード': 'EXCEL001',
            'プロジェクト名': 'テストプロジェクト',
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '〇',
            '売上': 1000000,
            '経費': 800000
        }, {
            'プロジェクトコード': 'EXCEL002',
            'プロジェクト名': '',  # 空のセル
            '支社名': 'テスト支社',
            '売上の年度': 2024,
            '受注角度': '△',
            '売上': None,  # 空のセル
            '経費': 1500000
        }]
        
        filepath = self.create_test_excel_file([test_data])
        
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
            
            result = self.import_service.get_preview_data(
                filepath, 'excel', column_mapping
            )
            
            assert result['success'] is True
            assert result['row_count'] == 2
            
            # 検証エラーがあることを確認
            assert result['validation_summary']['error_rows'] > 0
            assert len(result['validation_errors']) > 0
            
        finally:
            os.unlink(filepath)
    
    def test_excel_import_large_file_performance(self):
        """大きなExcelファイルのパフォーマンステスト"""
        # 100行のテストデータを作成
        test_data = []
        for i in range(100):
            test_data.append({
                'プロジェクトコード': f'EXCEL{i:03d}',
                'プロジェクト名': f'テストプロジェクト{i}',
                '支社名': 'テスト支社',
                '売上の年度': 2024,
                '受注角度': '〇' if i % 3 == 0 else '△' if i % 3 == 1 else '×',
                '売上': (i + 1) * 100000,
                '経費': (i + 1) * 80000
            })
        
        filepath = self.create_test_excel_file([test_data])
        
        try:
            import time
            start_time = time.time()
            
            result = self.import_service.validate_file(filepath, 'excel')
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            assert result['success'] is True
            assert result['row_count'] == 100
            # パフォーマンス要件: 100行の処理が5秒以内
            assert processing_time < 5.0, f"処理時間が長すぎます: {processing_time}秒"
            
        finally:
            os.unlink(filepath)


class TestExcelImportIntegration:
    """Excelインポート機能の統合テスト"""
    
    def setup_method(self):
        """各テストメソッドの前に実行される"""
        self.import_service = ImportService()
    
    def teardown_method(self):
        """各テストメソッドの後に実行される"""
        # テストデータをクリーンアップ
        Project.query.delete()
        Branch.query.filter(Branch.branch_name.like('%テスト%')).delete()
        db.session.commit()
    
    def create_complex_excel_file(self):
        """複雑なExcelファイルを作成"""
        # 複数シートを持つ複雑なExcelファイル
        sheet1_data = [
            {
                'プロジェクトコード': 'COMPLEX001',
                'プロジェクト名': '複雑なプロジェクト1',
                '支社名': '東京支社',
                '売上の年度': 2024,
                '受注角度': '〇',
                '売上': 5000000,
                '経費': 4000000
            },
            {
                'プロジェクトコード': 'COMPLEX002',
                'プロジェクト名': '複雑なプロジェクト2',
                '支社名': '大阪支社',
                '売上の年度': 2024,
                '受注角度': '△',
                '売上': 3000000,
                '経費': 2500000
            }
        ]
        
        sheet2_data = [
            {
                'プロジェクトコード': 'COMPLEX003',
                'プロジェクト名': '複雑なプロジェクト3',
                '支社名': '名古屋支社',
                '売上の年度': 2025,
                '受注角度': '×',
                '売上': 1000000,
                '経費': 1200000
            }
        ]
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            pd.DataFrame(sheet1_data).to_excel(writer, sheet_name='メインデータ', index=False)
            pd.DataFrame(sheet2_data).to_excel(writer, sheet_name='追加データ', index=False)
            # 空のシートも追加
            pd.DataFrame().to_excel(writer, sheet_name='空シート', index=False)
        
        return temp_file.name
    
    def test_complex_excel_import_workflow(self):
        """複雑なExcelファイルのインポートワークフローテスト"""
        filepath = self.create_complex_excel_file()
        
        try:
            # 1. ファイル検証
            validation_result = self.import_service.validate_file(filepath, 'excel')
            assert validation_result['success'] is True
            assert validation_result['excel_info']['sheet_count'] == 3
            
            # 2. シート情報取得
            sheets_info = self.import_service.get_excel_sheets(filepath)
            assert sheets_info['success'] is True
            
            # データありシートを確認
            data_sheets = [sheet for sheet in sheets_info['sheets'] if sheet['has_data']]
            assert len(data_sheets) == 2
            
            # 3. 特定シートでの検証
            sheet_result = self.import_service.validate_excel_sheet(filepath, 'メインデータ')
            assert sheet_result['success'] is True
            assert sheet_result['row_count'] == 2
            
            # 4. プレビューデータ取得
            column_mapping = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクト名',
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上',
                'expenses': '経費'
            }
            
            preview_result = self.import_service.get_preview_data(
                filepath, 'excel', column_mapping, sheet_name='メインデータ'
            )
            assert preview_result['success'] is True
            assert preview_result['row_count'] == 2
            
            # 5. インポート実行
            import_result = self.import_service.execute_import(
                filepath, 'excel', column_mapping, sheet_name='メインデータ'
            )
            assert import_result['success'] is True
            assert import_result['success_count'] == 2
            assert import_result['error_count'] == 0
            
            # 6. データベース確認
            projects = Project.query.filter(
                Project.project_code.in_(['COMPLEX001', 'COMPLEX002'])
            ).all()
            assert len(projects) == 2
            
            # 支社も自動作成されているか確認
            branches = Branch.query.filter(
                Branch.branch_name.in_(['東京支社', '大阪支社'])
            ).all()
            assert len(branches) == 2
            
        finally:
            os.unlink(filepath)