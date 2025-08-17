#!/usr/bin/env python3
"""
プロジェクトテーブルに支社関連付けを追加するマイグレーションスクリプト
Task 8: プロジェクトモデルへの支社関連付け
"""

import sqlite3
import os
from datetime import datetime

def migrate_add_branch_to_projects():
    """既存のプロジェクトテーブルに支社関連付けを追加"""
    
    db_path = 'data/projects.db'
    
    if not os.path.exists(db_path):
        print(f"データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 既存のテーブル構造を確認
        cursor.execute("PRAGMA table_info(projects)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'branch_id' in columns:
            print("branch_idカラムは既に存在します。マイグレーションをスキップします。")
            conn.close()
            return True
        
        print("プロジェクトテーブルにbranch_idカラムを追加します...")
        
        # まず、デフォルトの支社が存在するかチェック
        cursor.execute("SELECT COUNT(*) FROM branches WHERE is_active = 1")
        active_branch_count = cursor.fetchone()[0]
        
        if active_branch_count == 0:
            print("有効な支社が存在しません。デフォルト支社を作成します...")
            cursor.execute("""
                INSERT INTO branches (branch_code, branch_name, is_active, created_at, updated_at)
                VALUES ('DEFAULT', 'デフォルト支社', 1, ?, ?)
            """, (datetime.utcnow(), datetime.utcnow()))
        
        # デフォルト支社のIDを取得
        cursor.execute("SELECT id FROM branches WHERE is_active = 1 ORDER BY id LIMIT 1")
        default_branch_id = cursor.fetchone()[0]
        
        # 既存のプロジェクト数を確認
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        
        print(f"既存のプロジェクト数: {project_count}")
        print(f"デフォルト支社ID: {default_branch_id}")
        
        # branch_idカラムを追加（一時的にNULL許可）
        cursor.execute("ALTER TABLE projects ADD COLUMN branch_id INTEGER")
        
        # 既存のプロジェクトにデフォルト支社を設定
        if project_count > 0:
            cursor.execute("UPDATE projects SET branch_id = ?", (default_branch_id,))
            print(f"{project_count}件のプロジェクトにデフォルト支社を設定しました。")
        
        # インデックスを作成
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_branch_id ON projects(branch_id)")
        
        conn.commit()
        print("マイグレーションが完了しました。")
        
        # 結果を確認
        cursor.execute("""
            SELECT p.project_code, p.project_name, b.branch_name 
            FROM projects p 
            JOIN branches b ON p.branch_id = b.id 
            LIMIT 5
        """)
        
        sample_projects = cursor.fetchall()
        if sample_projects:
            print("\n更新されたプロジェクトのサンプル:")
            for project in sample_projects:
                print(f"  - {project[0]}: {project[1]} ({project[2]})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def rollback_branch_migration():
    """マイグレーションをロールバック（開発用）"""
    
    db_path = 'data/projects.db'
    
    if not os.path.exists(db_path):
        print(f"データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 既存のテーブル構造を確認
        cursor.execute("PRAGMA table_info(projects)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'branch_id' not in columns:
            print("branch_idカラムが存在しません。ロールバックの必要はありません。")
            conn.close()
            return True
        
        print("警告: この操作はbranch_idカラムを削除します。")
        print("SQLiteではALTER TABLE DROP COLUMNがサポートされていないため、")
        print("テーブルを再作成する必要があります。")
        
        response = input("続行しますか？ (y/N): ")
        if response.lower() != 'y':
            print("ロールバックをキャンセルしました。")
            conn.close()
            return False
        
        # 既存データをバックアップ
        cursor.execute("""
            CREATE TABLE projects_backup AS 
            SELECT id, project_code, project_name, fiscal_year, order_probability, 
                   revenue, expenses, created_at, updated_at 
            FROM projects
        """)
        
        # 元のテーブルを削除
        cursor.execute("DROP TABLE projects")
        
        # 新しいテーブルを作成（branch_idなし）
        cursor.execute("""
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_code VARCHAR(50) UNIQUE NOT NULL,
                project_name VARCHAR(200) NOT NULL,
                fiscal_year INTEGER NOT NULL,
                order_probability NUMERIC(5, 2) NOT NULL,
                revenue NUMERIC(15, 2) NOT NULL,
                expenses NUMERIC(15, 2) NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT check_order_probability_values CHECK (order_probability IN (0, 50, 100)),
                CONSTRAINT check_revenue_positive CHECK (revenue >= 0),
                CONSTRAINT check_expenses_positive CHECK (expenses >= 0),
                CONSTRAINT check_fiscal_year_range CHECK (fiscal_year >= 1900 AND fiscal_year <= 2100)
            )
        """)
        
        # データを復元
        cursor.execute("""
            INSERT INTO projects (id, project_code, project_name, fiscal_year, order_probability, 
                                revenue, expenses, created_at, updated_at)
            SELECT id, project_code, project_name, fiscal_year, order_probability, 
                   revenue, expenses, created_at, updated_at 
            FROM projects_backup
        """)
        
        # インデックスを再作成
        cursor.execute("CREATE INDEX idx_projects_fiscal_year ON projects(fiscal_year)")
        cursor.execute("CREATE INDEX idx_projects_project_code ON projects(project_code)")
        cursor.execute("CREATE INDEX idx_projects_created_at ON projects(created_at)")
        
        # バックアップテーブルを削除
        cursor.execute("DROP TABLE projects_backup")
        
        conn.commit()
        print("ロールバックが完了しました。")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"データベースエラー: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False
    except Exception as e:
        print(f"予期しないエラー: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("=== プロジェクト支社関連付けマイグレーション ロールバック ===")
        success = rollback_branch_migration()
    else:
        print("=== プロジェクト支社関連付けマイグレーション ===")
        success = migrate_add_branch_to_projects()
    
    if success:
        print("処理が正常に完了しました。")
        sys.exit(0)
    else:
        print("処理中にエラーが発生しました。")
        sys.exit(1)