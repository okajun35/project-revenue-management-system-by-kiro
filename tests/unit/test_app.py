#!/usr/bin/env python3
"""
アプリケーションの基本テスト
"""
import sqlite3
from pathlib import Path

def test_database_connection():
    """データベース接続をテスト"""
    print("データベース接続テストを開始...")
    
    db_path = Path('data/projects.db')
    
    if not db_path.exists():
        print("✗ データベースファイルが見つかりません")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # テーブル存在確認
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("✗ projectsテーブルが見つかりません")
            return False
        
        # データ確認
        cursor.execute("SELECT COUNT(*) FROM projects")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT project_code, project_name, revenue, expenses FROM projects LIMIT 3")
        projects = cursor.fetchall()
        
        print(f"✓ データベース接続成功")
        print(f"✓ projectsテーブル存在確認")
        print(f"✓ データ件数: {count}件")
        
        print("\nサンプルデータ:")
        for project in projects:
            code, name, revenue, expenses = project
            gross_profit = revenue - expenses
            print(f"  - {code}: {name} (売上: ¥{revenue:,}, 経費: ¥{expenses:,}, 粗利: ¥{gross_profit:,})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ データベース接続エラー: {e}")
        return False

def test_config():
    """設定ファイルをテスト"""
    print("\n設定ファイルテストを開始...")
    
    try:
        import config
        
        # 設定クラスの存在確認
        config_classes = ['Config', 'DevelopmentConfig', 'ProductionConfig', 'TestingConfig']
        for class_name in config_classes:
            if hasattr(config, class_name):
                print(f"✓ {class_name}クラス存在確認")
            else:
                print(f"✗ {class_name}クラスが見つかりません")
                return False
        
        # 開発設定のテスト
        dev_config = config.DevelopmentConfig()
        print(f"✓ データベースURI: {dev_config.SQLALCHEMY_DATABASE_URI}")
        print(f"✓ デバッグモード: {dev_config.DEBUG}")
        
        # テスト設定のテスト
        test_config = config.TestingConfig()
        print(f"✓ テスト用データベースURI: {test_config.SQLALCHEMY_DATABASE_URI}")
        
        # config辞書のテスト
        if hasattr(config, 'config') and isinstance(config.config, dict):
            print(f"✓ config辞書存在確認: {list(config.config.keys())}")
        else:
            print("✗ config辞書が見つかりません")
        
        return True
        
    except Exception as e:
        print(f"✗ 設定ファイルエラー: {e}")
        return False

def main():
    """メインテスト関数"""
    print("=== プロジェクト基盤テスト ===\n")
    
    db_test = test_database_connection()
    config_test = test_config()
    
    print(f"\n=== テスト結果 ===")
    print(f"データベーステスト: {'✓ 成功' if db_test else '✗ 失敗'}")
    print(f"設定ファイルテスト: {'✓ 成功' if config_test else '✗ 失敗'}")
    
    if db_test and config_test:
        print("\n🎉 すべてのテストが成功しました！")
        print("プロジェクト基盤とデータベース設定が完了しています。")
        return True
    else:
        print("\n❌ 一部のテストが失敗しました。")
        return False

if __name__ == '__main__':
    main()