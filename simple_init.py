#!/usr/bin/env python3
"""
シンプルなデータベース初期化スクリプト
"""
import sqlite3
from pathlib import Path

def create_database():
    """SQLiteデータベースを直接作成"""
    print("データベースを初期化中...")
    
    # データディレクトリを作成
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # データベースファイルのパス
    db_path = data_dir / 'projects.db'
    
    # データベース接続
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 支社テーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS branches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            branch_code VARCHAR(20) UNIQUE NOT NULL,
            branch_name VARCHAR(100) UNIQUE NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 年度マスターテーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_years (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER UNIQUE NOT NULL,
            year_name VARCHAR(20) UNIQUE NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # プロジェクトテーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_code VARCHAR(50) UNIQUE NOT NULL,
            project_name VARCHAR(200) NOT NULL,
            branch_id INTEGER NOT NULL,
            fiscal_year INTEGER NOT NULL,
            order_probability DECIMAL(5,2) NOT NULL,
            revenue DECIMAL(15,2) NOT NULL,
            expenses DECIMAL(15,2) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (branch_id) REFERENCES branches (id),
            CHECK (order_probability IN (0, 50, 100)),
            CHECK (revenue >= 0),
            CHECK (expenses >= 0),
            CHECK (fiscal_year >= 1900 AND fiscal_year <= 2100)
        )
    ''')
    
    # インデックスを作成
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_branches_branch_code ON branches(branch_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_branches_is_active ON branches(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fiscal_years_year ON fiscal_years(year)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fiscal_years_is_active ON fiscal_years(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_project_code ON projects(project_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_branch_id ON projects(branch_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_fiscal_year ON projects(fiscal_year)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at)')
    
    # 支社サンプルデータを挿入
    branch_data = [
        ('TKY', '東京本社'),
        ('OSK', '大阪支社'),
        ('NGY', '名古屋支社'),
        ('FKK', '福岡支社')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO branches 
        (branch_code, branch_name, is_active)
        VALUES (?, ?, 1)
    ''', branch_data)
    
    # 年度マスターサンプルデータを挿入
    fiscal_year_data = [
        (2023, '2023年度'),
        (2024, '2024年度'),
        (2025, '2025年度')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO fiscal_years 
        (year, year_name, is_active)
        VALUES (?, ?, 1)
    ''', fiscal_year_data)
    
    # プロジェクトサンプルデータを挿入（支社IDを参照）
    project_data = [
        ('PRJ-2024-001', 'Webシステム開発プロジェクト', 1, 2024, 100.0, 5000000, 3500000),  # 東京本社
        ('PRJ-2024-002', 'モバイルアプリ開発', 2, 2024, 50.0, 3000000, 2100000),   # 大阪支社
        ('PRJ-2023-015', 'データ分析システム', 1, 2023, 100.0, 8000000, 5200000),   # 東京本社
        ('PRJ-2024-003', 'ECサイト構築', 3, 2024, 100.0, 4500000, 3200000),        # 名古屋支社
        ('PRJ-2025-001', 'AI導入プロジェクト', 4, 2025, 50.0, 12000000, 8500000),  # 福岡支社
        ('PRJ-2024-004', 'インフラ更新', 2, 2024, 0.0, 2500000, 2800000),          # 大阪支社（赤字）
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO projects 
        (project_code, project_name, branch_id, fiscal_year, order_probability, revenue, expenses)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', project_data)
    
    # 変更をコミット
    conn.commit()
    
    # データ確認
    cursor.execute('SELECT COUNT(*) FROM branches')
    branch_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM fiscal_years')
    fiscal_year_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM projects')
    project_count = cursor.fetchone()[0]
    
    print(f"✓ データベースファイルを作成: {db_path}")
    print(f"✓ 支社テーブルを作成")
    print(f"✓ 年度マスターテーブルを作成")
    print(f"✓ プロジェクトテーブルを作成")
    print(f"✓ インデックスを作成")
    print(f"✓ 支社サンプルデータを挿入: {branch_count}件")
    print(f"✓ 年度マスターサンプルデータを挿入: {fiscal_year_count}件")
    print(f"✓ プロジェクトサンプルデータを挿入: {project_count}件")
    
    # 接続を閉じる
    conn.close()
    
    print("データベースの初期化が完了しました！")
    return True

if __name__ == '__main__':
    create_database()