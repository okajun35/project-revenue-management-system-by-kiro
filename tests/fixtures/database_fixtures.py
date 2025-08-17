#!/usr/bin/env python3
"""
プロジェクト収支システム - データベースフィクスチャ
"""

import sqlite3
from pathlib import Path
from datetime import datetime
try:
    from .sample_data import SAMPLE_BRANCHES, SAMPLE_FISCAL_YEARS, SAMPLE_PROJECTS
except ImportError:
    from sample_data import SAMPLE_BRANCHES, SAMPLE_FISCAL_YEARS, SAMPLE_PROJECTS

class DatabaseFixtures:
    """テスト用データベースフィクスチャクラス"""
    
    def __init__(self, db_path=None):
        """
        初期化
        
        Args:
            db_path: データベースファイルパス（Noneの場合はメモリDB）
        """
        if db_path is None:
            self.db_path = ':memory:'
        else:
            self.db_path = str(db_path)
        
        self.connection = None
    
    def connect(self):
        """データベース接続"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def disconnect(self):
        """データベース切断"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def create_tables(self):
        """テーブル作成"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        
        # 支社テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                code VARCHAR(10) NOT NULL UNIQUE,
                address TEXT,
                phone VARCHAR(20),
                manager VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 年度テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fiscal_years (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL UNIQUE,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                is_active BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # プロジェクトテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(200) NOT NULL,
                branch_id INTEGER NOT NULL,
                fiscal_year INTEGER NOT NULL,
                order_probability VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'planning',
                revenue INTEGER DEFAULT 0,
                expenses INTEGER DEFAULT 0,
                gross_profit INTEGER DEFAULT 0,
                start_date DATE,
                end_date DATE,
                client_name VARCHAR(200),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (branch_id) REFERENCES branches (id),
                FOREIGN KEY (fiscal_year) REFERENCES fiscal_years (year)
            )
        ''')
        
        self.connection.commit()
    
    def insert_sample_data(self):
        """サンプルデータ挿入"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        
        # 支社データ挿入
        for branch in SAMPLE_BRANCHES:
            cursor.execute('''
                INSERT OR REPLACE INTO branches 
                (id, name, code, address, phone, manager, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                branch['id'], branch['name'], branch['code'], 
                branch['address'], branch['phone'], branch['manager'],
                branch['created_at'], branch['updated_at']
            ))
        
        # 年度データ挿入
        for fiscal_year in SAMPLE_FISCAL_YEARS:
            cursor.execute('''
                INSERT OR REPLACE INTO fiscal_years 
                (id, year, start_date, end_date, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                fiscal_year['id'], fiscal_year['year'], 
                fiscal_year['start_date'], fiscal_year['end_date'],
                fiscal_year['is_active'], fiscal_year['created_at'], 
                fiscal_year['updated_at']
            ))
        
        # プロジェクトデータ挿入
        for project in SAMPLE_PROJECTS:
            cursor.execute('''
                INSERT OR REPLACE INTO projects 
                (id, code, name, branch_id, fiscal_year, order_probability, status,
                 revenue, expenses, gross_profit, start_date, end_date, 
                 client_name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project['id'], project['code'], project['name'],
                project['branch_id'], project['fiscal_year'], 
                project['order_probability'], project['status'],
                project['revenue'], project['expenses'], project['gross_profit'],
                project['start_date'], project['end_date'],
                project['client_name'], project['description'],
                project['created_at'], project['updated_at']
            ))
        
        self.connection.commit()
    
    def clear_all_data(self):
        """全データ削除"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM projects')
        cursor.execute('DELETE FROM fiscal_years')
        cursor.execute('DELETE FROM branches')
        self.connection.commit()
    
    def setup_test_database(self):
        """テストデータベースセットアップ"""
        self.connect()
        self.create_tables()
        self.insert_sample_data()
        return self.connection
    
    def teardown_test_database(self):
        """テストデータベース後処理"""
        if self.connection:
            self.clear_all_data()
            self.disconnect()
    
    def get_project_count(self):
        """プロジェクト数取得"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM projects')
        return cursor.fetchone()[0]
    
    def get_branch_count(self):
        """支社数取得"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM branches')
        return cursor.fetchone()[0]
    
    def get_fiscal_year_count(self):
        """年度数取得"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM fiscal_years')
        return cursor.fetchone()[0]
    
    def get_projects_by_year(self, year):
        """年度別プロジェクト取得"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM projects WHERE fiscal_year = ?', (year,))
        return cursor.fetchall()
    
    def get_projects_by_branch(self, branch_id):
        """支社別プロジェクト取得"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM projects WHERE branch_id = ?', (branch_id,))
        return cursor.fetchall()
    
    def get_revenue_statistics(self):
        """売上統計取得"""
        if not self.connection:
            raise RuntimeError("Database not connected")
        
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as project_count,
                SUM(revenue) as total_revenue,
                SUM(expenses) as total_expenses,
                SUM(gross_profit) as total_gross_profit,
                AVG(revenue) as avg_revenue
            FROM projects
        ''')
        return cursor.fetchone()


def create_test_database(db_path=None):
    """テストデータベース作成ヘルパー関数"""
    fixtures = DatabaseFixtures(db_path)
    fixtures.setup_test_database()
    return fixtures


def create_sample_sqlite_file(file_path):
    """サンプルSQLiteファイル作成"""
    file_path = Path(file_path)
    
    # 既存ファイルがあれば削除
    if file_path.exists():
        file_path.unlink()
    
    # ディレクトリ作成
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # データベース作成
    fixtures = DatabaseFixtures(file_path)
    fixtures.setup_test_database()
    fixtures.disconnect()
    
    print(f"Sample database created: {file_path}")
    return file_path


if __name__ == '__main__':
    # サンプルデータベースファイル作成
    sample_db_path = Path(__file__).parent / 'data' / 'sample_test.db'
    create_sample_sqlite_file(sample_db_path)
    
    # 作成したデータベースの確認
    fixtures = DatabaseFixtures(sample_db_path)
    fixtures.connect()
    
    print(f"Projects: {fixtures.get_project_count()}")
    print(f"Branches: {fixtures.get_branch_count()}")
    print(f"Fiscal Years: {fixtures.get_fiscal_year_count()}")
    
    stats = fixtures.get_revenue_statistics()
    print(f"Revenue Statistics: {dict(stats)}")
    
    fixtures.disconnect()