#!/usr/bin/env python3
"""
Task 19: インポート列マッピング機能のテスト

このテストファイルは、実装した列マッピング機能をテストします。
"""

import pytest
import tempfile
import os
import pandas as pd
from flask import session
from app import create_app, db
from app.models import Branch, Project
from app.services.import_service import ImportService


class TestImportMappingFunctionality:
    """インポート列マッピング機能のテストクラス"""
    
    @pytest.fixture
    def app(self):
        """テスト用のFlaskアプリケーションを作成"""
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
        
        with app.app_context():
            db.create_all()
            
            # 既存のデータをクリア
            db.session.query(Project).delete()
            db.session.query(Branch).delete()
            db.session.commit()
            
            # テスト用の支社データを作成
            branch1 = Branch.create_with_validation(
                branch_code='TKY',
                branch_name='東京支社',
                is_active=True
            )
            branch2 = Branch.create_with_validation(
                branch_code='OSK',
                branch_name='大阪支社',
                is_active=True
            )
            
            yield app
            
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """テスト用のクライアントを作成"""
        return app.test_client()
    
    @pytest.fixture
    def sample_csv_file(self):
        """テスト用のCSVファイルを作成"""
        # サンプルデータ
        data = {
            'プロジェクトコード': ['PRJ001', 'PRJ002', 'PRJ003'],
            'プロジェクト名': ['新システム開発', 'Webサイト構築', 'データ分析'],
            '支社名': ['東京支社', '大阪支社', '東京支社'],
            '売上の年度': [2024, 2024, 2025],
            '受注角度': ['〇', '△', '×'],
            '売上（契約金）': [1000000, 500000, 800000],
            '経費（トータル）': [800000, 300000, 600000]
        }
        
        df = pd.DataFrame(data)
        
        # 一時ファイルに保存
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig')
        df.to_csv(temp_file.name, index=False, encoding='utf-8-sig')
        temp_file.close()
        
        yield temp_file.name
        
        # クリーンアップ
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    def test_import_service_system_fields(self, app):
        """ImportServiceのシステムフィールド定義をテスト"""
        with app.app_context():
            service = ImportService()
            system_fields = service.get_system_fields()
            
            # 必須フィールドが含まれていることを確認
            required_fields = ['project_code', 'project_name', 'branch_name', 'fiscal_year', 'order_probability', 'revenue', 'expenses']
            for field in required_fields:
                assert field in system_fields
                assert 'label' in system_fields[field]
                assert 'required' in system_fields[field]
                assert 'description' in system_fields[field]
                assert 'example' in system_fields[field]
    
    def test_auto_mapping_generation(self, app, sample_csv_file):
        """自動マッピング生成機能をテスト"""
        with app.app_context():
            service = ImportService()
            
            # 日本語の列名でテスト（validate_fileは自動的に英語名に変換するため、元の列名を使用）
            japanese_columns = ['プロジェクトコード', 'プロジェクト名', '支社名', '売上の年度', '受注角度', '売上（契約金）', '経費（トータル）']
            
            # 自動マッピングを生成
            auto_mapping = service.get_auto_mapping(japanese_columns)
            
            # 期待されるマッピングが生成されることを確認
            expected_mappings = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクト名',
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上（契約金）',
                'expenses': '経費（トータル）'
            }
            
            for field, expected_column in expected_mappings.items():
                assert field in auto_mapping
                assert auto_mapping[field] == expected_column
    
    def test_branch_mapping_suggestions(self, app, sample_csv_file):
        """支社マッピング候補機能をテスト"""
        with app.app_context():
            service = ImportService()
            
            # ファイルを検証
            result = service.validate_file(sample_csv_file, 'csv')
            
            # 支社マッピング候補を取得
            branch_suggestions = service.get_branch_mapping_suggestions(result['columns'])
            
            # 既存の支社が含まれていることを確認
            assert 'existing_branches' in branch_suggestions
            assert len(branch_suggestions['existing_branches']) == 2
            
            # 支社名が正しく含まれていることを確認
            branch_names = [b['branch_name'] for b in branch_suggestions['existing_branches']]
            assert '東京支社' in branch_names
            assert '大阪支社' in branch_names
    
    def test_mapping_validation(self, app, sample_csv_file):
        """マッピング検証機能をテスト"""
        with app.app_context():
            service = ImportService()
            
            # 実際のファイル列名を使用（validate_fileで変換された後の英語名）
            result = service.validate_file(sample_csv_file, 'csv')
            columns = result['columns']
            
            # 正しいマッピング（英語列名を使用）
            valid_mapping = {
                'project_code': 'project_code',
                'project_name': 'project_name',
                'branch_name': 'branch_name',
                'fiscal_year': 'fiscal_year',
                'order_probability': 'order_probability',
                'revenue': 'revenue',
                'expenses': 'expenses'
            }
            
            validation_result = service.validate_mapping(valid_mapping, columns)
            assert validation_result['valid'] == True
            assert len(validation_result['errors']) == 0
            
            # 不正なマッピング（必須フィールド不足）
            invalid_mapping = {
                'project_code': 'project_code',
                'project_name': 'project_name'
                # 他の必須フィールドが不足
            }
            
            validation_result = service.validate_mapping(invalid_mapping, columns)
            assert validation_result['valid'] == False
            assert len(validation_result['errors']) > 0
            
            # 重複マッピング
            duplicate_mapping = {
                'project_code': 'プロジェクトコード',
                'project_name': 'プロジェクトコード',  # 重複
                'branch_name': '支社名',
                'fiscal_year': '売上の年度',
                'order_probability': '受注角度',
                'revenue': '売上（契約金）',
                'expenses': '経費（トータル）'
            }
            
            validation_result = service.validate_mapping(duplicate_mapping, columns)
            assert validation_result['valid'] == False
            assert len(validation_result['errors']) > 0
    
    def test_mapping_route_access(self, client, app, sample_csv_file):
        """マッピング画面へのアクセステスト"""
        with client.session_transaction() as sess:
            # セッションにファイル情報を設定（実際のファイルパスを使用）
            sess['import_file'] = sample_csv_file
            sess['import_columns'] = ['project_code', 'project_name', 'branch_name', 'fiscal_year', 'order_probability', 'revenue', 'expenses']
            sess['import_sample_data'] = [{'project_code': 'PRJ001', 'project_name': 'テスト', 'branch_name': '東京支社', 'fiscal_year': 2024, 'order_probability': '〇', 'revenue': 1000000, 'expenses': 800000}]
            sess['import_row_count'] = 3
        
        response = client.get('/import/mapping')
        assert response.status_code == 200
        assert 'マッピング設定' in response.get_data(as_text=True)
    
    def test_mapping_save_and_load_routes(self, client, app):
        """マッピング設定の保存・読み込みルートをテスト"""
        with client.session_transaction() as sess:
            sess['import_columns'] = ['project_code', 'project_name', 'branch_name', 'fiscal_year', 'order_probability', 'revenue', 'expenses']
        
        # マッピング設定を保存
        mapping_data = {
            'mapping_name': 'テスト設定',
            'mapping_project_code': 'project_code',
            'mapping_project_name': 'project_name',
            'mapping_branch_name': 'branch_name'
        }
        
        response = client.post('/import/save_mapping', 
                             json=mapping_data,
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        # 保存済みマッピング一覧を取得
        response = client.get('/import/get_saved_mappings')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'テスト設定' in data['mappings']
        
        # マッピング設定を読み込み
        response = client.post('/import/load_mapping',
                             json={'mapping_name': 'テスト設定'},
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert 'mapping' in data


def run_tests():
    """テストを実行"""
    print("Task 19: インポート列マッピング機能のテストを開始...")
    
    # pytest を使用してテストを実行
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    run_tests()