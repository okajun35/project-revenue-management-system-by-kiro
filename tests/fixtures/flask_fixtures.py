#!/usr/bin/env python3
"""
プロジェクト収支システム - Flaskテスト用フィクスチャ
"""

import pytest
import tempfile
import os
from pathlib import Path
from app import create_app, db
from app.models import Branch, FiscalYear, Project
from .sample_data import SAMPLE_BRANCHES, SAMPLE_FISCAL_YEARS, SAMPLE_PROJECTS
from .database_fixtures import DatabaseFixtures

class FlaskTestFixtures:
    """Flaskアプリケーション用テストフィクスチャ"""
    
    def __init__(self):
        self.app = None
        self.app_context = None
        self.client = None
        self.temp_db = None
    
    def create_test_app(self, config_overrides=None):
        """テスト用Flaskアプリケーション作成"""
        # 一時データベースファイル作成
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # テスト設定
        test_config = {
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{self.temp_db.name}',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'test-secret-key',
            'UPLOAD_FOLDER': tempfile.gettempdir()
        }
        
        # 設定上書き
        if config_overrides:
            test_config.update(config_overrides)
        
        # アプリケーション作成
        self.app = create_app()
        
        # 設定適用
        for key, value in test_config.items():
            self.app.config[key] = value
        
        return self.app
    
    def setup_app_context(self):
        """アプリケーションコンテキストセットアップ"""
        if not self.app:
            raise RuntimeError("App not created. Call create_test_app() first.")
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # データベース初期化
        db.create_all()
        
        return self.app_context
    
    def create_test_client(self):
        """テストクライアント作成"""
        if not self.app:
            raise RuntimeError("App not created. Call create_test_app() first.")
        
        self.client = self.app.test_client()
        return self.client
    
    def load_sample_data(self):
        """サンプルデータ読み込み"""
        if not self.app_context:
            raise RuntimeError("App context not set up. Call setup_app_context() first.")
        
        # 支社データ
        for branch_data in SAMPLE_BRANCHES:
            branch = Branch(
                name=branch_data['name'],
                code=branch_data['code'],
                address=branch_data['address'],
                phone=branch_data['phone'],
                manager=branch_data['manager']
            )
            db.session.add(branch)
        
        # 年度データ
        for fy_data in SAMPLE_FISCAL_YEARS:
            fiscal_year = FiscalYear(
                year=fy_data['year'],
                start_date=fy_data['start_date'],
                end_date=fy_data['end_date'],
                is_active=fy_data['is_active']
            )
            db.session.add(fiscal_year)
        
        # プロジェクトデータ
        for project_data in SAMPLE_PROJECTS:
            project = Project(
                code=project_data['code'],
                name=project_data['name'],
                branch_id=project_data['branch_id'],
                fiscal_year=project_data['fiscal_year'],
                order_probability=project_data['order_probability'],
                status=project_data['status'],
                revenue=project_data['revenue'],
                expenses=project_data['expenses'],
                gross_profit=project_data['gross_profit'],
                start_date=project_data['start_date'],
                end_date=project_data['end_date'],
                client_name=project_data['client_name'],
                description=project_data['description']
            )
            db.session.add(project)
        
        db.session.commit()
    
    def clear_data(self):
        """データクリア"""
        if not self.app_context:
            return
        
        # 外部キー制約を考慮した順序で削除
        db.session.query(Project).delete()
        db.session.query(FiscalYear).delete()
        db.session.query(Branch).delete()
        db.session.commit()
    
    def teardown(self):
        """後処理"""
        if self.app_context:
            self.clear_data()
            db.session.remove()
            self.app_context.pop()
            self.app_context = None
        
        if self.temp_db:
            try:
                os.unlink(self.temp_db.name)
            except (OSError, FileNotFoundError):
                pass
            self.temp_db = None
        
        self.app = None
        self.client = None
    
    def setup_complete_test_environment(self, config_overrides=None):
        """完全なテスト環境セットアップ"""
        self.create_test_app(config_overrides)
        self.setup_app_context()
        self.create_test_client()
        self.load_sample_data()
        return self.app, self.client


# Pytestフィクスチャ
@pytest.fixture
def flask_fixtures():
    """Flaskテストフィクスチャ（pytest用）"""
    fixtures = FlaskTestFixtures()
    yield fixtures
    fixtures.teardown()


@pytest.fixture
def app():
    """Flaskアプリケーションフィクスチャ"""
    fixtures = FlaskTestFixtures()
    app = fixtures.create_test_app()
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
    
    fixtures.teardown()


@pytest.fixture
def client(app):
    """テストクライアントフィクスチャ"""
    return app.test_client()


@pytest.fixture
def app_with_data():
    """サンプルデータ付きFlaskアプリケーション"""
    fixtures = FlaskTestFixtures()
    app, client = fixtures.setup_complete_test_environment()
    
    yield app, client, fixtures
    
    fixtures.teardown()


# ヘルパー関数
def create_test_session_data():
    """テスト用セッションデータ作成"""
    return {
        'import_file': '/tmp/test_import.csv',
        'import_type': 'csv',
        'import_columns': ['プロジェクトコード', 'プロジェクト名', '支社名', '売上の年度', '受注角度', '売上', '経費'],
        'import_sample_data': [
            {
                'プロジェクトコード': 'TEST001',
                'プロジェクト名': 'テストプロジェクト',
                '支社名': 'テスト支社',
                '売上の年度': 2024,
                '受注角度': '〇',
                '売上': 1000000,
                '経費': 800000
            }
        ],
        'import_row_count': 1
    }


def create_test_form_data():
    """テスト用フォームデータ作成"""
    return {
        'code': 'TEST001',
        'name': 'テストプロジェクト',
        'branch_id': 1,
        'fiscal_year': 2024,
        'order_probability': 'high',
        'status': 'planning',
        'revenue': 1000000,
        'expenses': 800000,
        'gross_profit': 200000,
        'start_date': '2024-04-01',
        'end_date': '2024-12-31',
        'client_name': 'テストクライアント',
        'description': 'テスト用プロジェクトの説明'
    }


if __name__ == '__main__':
    # テスト実行例
    fixtures = FlaskTestFixtures()
    app, client = fixtures.setup_complete_test_environment()
    
    print("Test environment set up successfully!")
    
    # データ確認
    with app.app_context():
        branch_count = Branch.query.count()
        project_count = Project.query.count()
        fy_count = FiscalYear.query.count()
        
        print(f"Branches: {branch_count}")
        print(f"Projects: {project_count}")
        print(f"Fiscal Years: {fy_count}")
    
    fixtures.teardown()
    print("Test environment cleaned up!")