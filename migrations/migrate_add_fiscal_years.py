#!/usr/bin/env python3
"""
年度マスターテーブルを追加するマイグレーションスクリプト
"""

import sqlite3
from datetime import datetime
import os

def migrate_add_fiscal_years():
    """年度マスターテーブルを追加し、既存の年度データを移行"""
    
    # データベースファイルのパス
    db_path = 'data/projects.db'
    
    if not os.path.exists(db_path):
        print(f"データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("年度マスターテーブルのマイグレーションを開始します...")
        
        # 1. 年度マスターテーブルを作成
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
        
        # インデックスを作成
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fiscal_years_year ON fiscal_years(year)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fiscal_years_is_active ON fiscal_years(is_active)')
        
        print("✅ 年度マスターテーブルを作成しました")
        
        # 2. 既存のプロジェクトから年度データを抽出
        cursor.execute('SELECT DISTINCT fiscal_year FROM projects WHERE fiscal_year IS NOT NULL ORDER BY fiscal_year')
        existing_years = cursor.fetchall()
        
        if existing_years:
            print(f"既存のプロジェクトから {len(existing_years)} 個の年度を発見しました")
            
            # 3. 年度マスターにデータを挿入
            for (year,) in existing_years:
                year_name = f"{year}年度"
                
                # 既に存在するかチェック
                cursor.execute('SELECT id FROM fiscal_years WHERE year = ?', (year,))
                if cursor.fetchone() is None:
                    cursor.execute('''
                        INSERT INTO fiscal_years (year, year_name, is_active, created_at, updated_at)
                        VALUES (?, ?, 1, ?, ?)
                    ''', (year, year_name, datetime.now(), datetime.now()))
                    print(f"  ✅ {year_name} を追加しました")
                else:
                    print(f"  ⚠️  {year_name} は既に存在します")
        else:
            print("既存のプロジェクトに年度データが見つかりませんでした")
            
            # デフォルトの年度を追加
            default_years = [2023, 2024, 2025]
            for year in default_years:
                year_name = f"{year}年度"
                cursor.execute('''
                    INSERT OR IGNORE INTO fiscal_years (year, year_name, is_active, created_at, updated_at)
                    VALUES (?, ?, 1, ?, ?)
                ''', (year, year_name, datetime.now(), datetime.now()))
                print(f"  ✅ デフォルト年度 {year_name} を追加しました")
        
        # 4. 変更をコミット
        conn.commit()
        
        # 5. 結果を確認
        cursor.execute('SELECT year, year_name, is_active FROM fiscal_years ORDER BY year DESC')
        fiscal_years = cursor.fetchall()
        
        print("\n📊 年度マスター一覧:")
        print("年度 | 年度名 | 有効")
        print("-" * 25)
        for year, year_name, is_active in fiscal_years:
            status = "有効" if is_active else "無効"
            print(f"{year} | {year_name} | {status}")
        
        print(f"\n✅ マイグレーションが正常に完了しました！")
        print(f"   - 年度マスターテーブルを作成")
        print(f"   - {len(fiscal_years)} 個の年度データを登録")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ データベースエラー: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def rollback_fiscal_years():
    """年度マスターテーブルを削除（ロールバック）"""
    
    db_path = 'data/projects.db'
    
    if not os.path.exists(db_path):
        print(f"データベースファイルが見つかりません: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("年度マスターテーブルのロールバックを開始します...")
        
        # テーブルを削除
        cursor.execute('DROP TABLE IF EXISTS fiscal_years')
        
        conn.commit()
        print("✅ 年度マスターテーブルを削除しました")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ データベースエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_fiscal_years()
    else:
        migrate_add_fiscal_years()