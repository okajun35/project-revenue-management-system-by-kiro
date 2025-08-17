#!/usr/bin/env python3
"""
プロジェクト収支システム - 初期サンプルデータセットアップ
本番環境での初回セットアップ時に実行するスクリプト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """メイン処理"""
    print("🚀 プロジェクト収支システム - 初期セットアップ")
    print("="*60)
    
    # 環境確認
    print("1. 環境確認中...")
    
    try:
        from app import create_app, db
        from app.models import Branch, FiscalYear, Project
        print("   ✅ アプリケーションモジュール読み込み成功")
    except ImportError as e:
        print(f"   ❌ アプリケーションモジュール読み込み失敗: {e}")
        return False
    
    # データベース接続確認
    print("2. データベース接続確認中...")
    
    try:
        app = create_app()
        with app.app_context():
            # データベース初期化
            db.create_all()
            
            # 接続テスト
            existing_projects = Project.query.count()
            existing_branches = Branch.query.count()
            existing_fiscal_years = FiscalYear.query.count()
            
            print(f"   ✅ データベース接続成功")
            print(f"   現在のデータ: プロジェクト{existing_projects}件, 支社{existing_branches}件, 年度{existing_fiscal_years}件")
            
    except Exception as e:
        print(f"   ❌ データベース接続失敗: {e}")
        return False
    
    # ユーザー確認
    print("\n" + "="*60)
    print("初期サンプルデータを作成します。")
    print("以下のデータが作成されます：")
    print("- 支社データ: 4件（東京本社、大阪支社、名古屋支社、福岡支社）")
    print("- 年度データ: 3件（2023年度、2024年度、2025年度）")
    print("- プロジェクトデータ: 8件（デモンストレーション用）")
    print("="*60)
    
    response = input("続行しますか？ (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("セットアップをキャンセルしました。")
        return False
    
    # サンプルデータ作成
    print("\n3. サンプルデータ作成中...")
    
    try:
        from create_sample_data import create_sample_data
        success = create_sample_data()
        
        if success:
            print("   ✅ サンプルデータ作成成功")
        else:
            print("   ❌ サンプルデータ作成失敗")
            return False
            
    except Exception as e:
        print(f"   ❌ サンプルデータ作成エラー: {e}")
        return False
    
    # 完了メッセージ
    print("\n" + "="*60)
    print("🎉 初期セットアップが完了しました！")
    print("="*60)
    print("\n次のステップ:")
    print("1. Webブラウザでシステムにアクセス")
    print("2. ダッシュボードでサンプルデータを確認")
    print("3. インポート機能をテスト（sample_data/demo_import.csv使用）")
    print("4. 各機能の動作確認")
    print("\nサンプルファイル:")
    print("- sample_data/demo_import.csv (CSVインポート用)")
    print("- sample_data/demo_import.xlsx (Excelインポート用)")
    print("\nサンプルデータ削除:")
    print("- python create_sample_data.py clear")
    
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ セットアップが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 予期しないエラー: {e}")
        sys.exit(1)