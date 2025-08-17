#!/usr/bin/env python3
"""
データベースマイグレーション機能
"""
import sqlite3
from pathlib import Path
from datetime import datetime

class DatabaseMigrator:
    """データベースマイグレーション管理クラス"""
    
    def __init__(self, db_path='data/projects.db'):
        self.db_path = Path(db_path)
        self.migrations_table = 'schema_migrations'
    
    def connect(self):
        """データベース接続"""
        return sqlite3.connect(self.db_path)
    
    def init_migrations_table(self):
        """マイグレーション管理テーブルを初期化"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version VARCHAR(50) UNIQUE NOT NULL,
                    description TEXT,
                    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def is_migration_applied(self, version):
        """マイグレーションが適用済みかチェック"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT COUNT(*) FROM {self.migrations_table} WHERE version = ?', (version,))
            return cursor.fetchone()[0] > 0
    
    def apply_migration(self, version, description, sql_commands):
        """マイグレーションを適用"""
        if self.is_migration_applied(version):
            print(f"マイグレーション {version} は既に適用済みです")
            return False
        
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                
                # マイグレーションSQLを実行
                for sql in sql_commands:
                    cursor.execute(sql)
                
                # マイグレーション記録を追加
                cursor.execute(f'''
                    INSERT INTO {self.migrations_table} (version, description)
                    VALUES (?, ?)
                ''', (version, description))
                
                conn.commit()
                print(f"✓ マイグレーション {version} を適用しました: {description}")
                return True
                
        except Exception as e:
            print(f"✗ マイグレーション {version} の適用に失敗しました: {e}")
            return False
    
    def get_applied_migrations(self):
        """適用済みマイグレーション一覧を取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                SELECT version, description, applied_at 
                FROM {self.migrations_table} 
                ORDER BY applied_at
            ''')
            return cursor.fetchall()

def run_migrations():
    """マイグレーションを実行"""
    print("データベースマイグレーションを開始...")
    
    migrator = DatabaseMigrator()
    migrator.init_migrations_table()
    
    # マイグレーション定義
    migrations = [
        {
            'version': '001_initial_schema',
            'description': 'プロジェクトテーブルの初期作成',
            'sql': [
                '''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_code VARCHAR(50) UNIQUE NOT NULL,
                    project_name VARCHAR(200) NOT NULL,
                    fiscal_year INTEGER NOT NULL,
                    order_probability DECIMAL(5,2) NOT NULL,
                    revenue DECIMAL(15,2) NOT NULL,
                    expenses DECIMAL(15,2) NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CHECK (order_probability >= 0 AND order_probability <= 100),
                    CHECK (revenue >= 0),
                    CHECK (expenses >= 0),
                    CHECK (fiscal_year >= 1900 AND fiscal_year <= 2100)
                )'''
            ]
        },
        {
            'version': '002_add_indexes',
            'description': 'インデックスの追加',
            'sql': [
                'CREATE INDEX IF NOT EXISTS idx_project_code ON projects(project_code)',
                'CREATE INDEX IF NOT EXISTS idx_fiscal_year ON projects(fiscal_year)',
                'CREATE INDEX IF NOT EXISTS idx_created_at ON projects(created_at)'
            ]
        },
        {
            'version': '003_create_branches_table',
            'description': '支社テーブルの作成',
            'sql': [
                '''CREATE TABLE IF NOT EXISTS branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    branch_code VARCHAR(20) UNIQUE NOT NULL,
                    branch_name VARCHAR(100) UNIQUE NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )'''
            ]
        },
        {
            'version': '004_add_branch_indexes',
            'description': '支社テーブルのインデックス追加',
            'sql': [
                'CREATE INDEX IF NOT EXISTS idx_branches_branch_code ON branches(branch_code)',
                'CREATE INDEX IF NOT EXISTS idx_branches_is_active ON branches(is_active)'
            ]
        }
    ]
    
    # マイグレーションを順次適用
    applied_count = 0
    for migration in migrations:
        if migrator.apply_migration(
            migration['version'],
            migration['description'],
            migration['sql']
        ):
            applied_count += 1
    
    # 適用済みマイグレーション一覧を表示
    print(f"\n適用済みマイグレーション一覧:")
    applied_migrations = migrator.get_applied_migrations()
    for version, description, applied_at in applied_migrations:
        print(f"  - {version}: {description} (適用日時: {applied_at})")
    
    print(f"\nマイグレーション完了: {applied_count}件の新しいマイグレーションを適用しました")

if __name__ == '__main__':
    run_migrations()