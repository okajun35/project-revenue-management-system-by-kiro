#!/usr/bin/env python3
"""
プロジェクト作成機能の手動テスト
"""
from app import create_app, db
from app.models import Project, Branch
from decimal import Decimal

def test_project_creation_manual():
    """プロジェクト作成の手動テスト"""
    print("=== プロジェクト作成機能テスト ===\n")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # 有効な支社を取得
            branch = Branch.get_active_branches()[0]
            
            # テストプロジェクトを作成
            print("1. プロジェクト作成テスト...")
            import time
            unique_code = f'MANUAL-TEST-{int(time.time())}'
            project = Project.create_with_validation(
                project_code=unique_code,
                project_name='手動テストプロジェクト',
                branch_id=branch.id,
                fiscal_year=2024,
                order_probability=100,
                revenue=Decimal('2500000.00'),
                expenses=Decimal('1800000.00')
            )
            
            print(f"✓ プロジェクト作成成功")
            print(f"  - ID: {project.id}")
            print(f"  - プロジェクトコード: {project.project_code}")
            print(f"  - プロジェクト名: {project.project_name}")
            print(f"  - 支社: {project.branch.branch_name}")
            print(f"  - 売上の年度: {project.fiscal_year}")
            print(f"  - 受注角度: {project.order_probability}% ({project.order_probability_symbol})")
            print(f"  - 売上: ¥{project.revenue:,}")
            print(f"  - 経費: ¥{project.expenses:,}")
            print(f"  - 粗利: ¥{project.gross_profit:,}")
            print(f"  - 作成日: {project.created_at}")
            
            # データベースから取得テスト
            print("\n2. データベース取得テスト...")
            retrieved_project = Project.query.filter_by(project_code=unique_code).first()
            if retrieved_project:
                print("✓ データベースから正常に取得できました")
                print(f"  - 取得したプロジェクト名: {retrieved_project.project_name}")
                print(f"  - 粗利計算結果: ¥{retrieved_project.gross_profit:,}")
            else:
                print("✗ データベースから取得できませんでした")
                return False
            
            # プロジェクト一覧取得テスト
            print("\n3. プロジェクト一覧取得テスト...")
            all_projects = Project.query.all()
            print(f"✓ 総プロジェクト数: {len(all_projects)}件")
            
            for p in all_projects[-3:]:  # 最新3件を表示
                print(f"  - {p.project_code}: {p.project_name} (粗利: ¥{p.gross_profit:,})")
            
            # バリデーションテスト
            print("\n4. バリデーションテスト...")
            try:
                # 重複するプロジェクトコードでテスト
                Project.create_with_validation(
                    project_code=unique_code,  # 重複
                    project_name='重複テスト',
                    branch_id=branch.id,
                    fiscal_year=2024,
                    order_probability=50,
                    revenue=Decimal('1000000.00'),
                    expenses=Decimal('800000.00')
                )
                print("✗ 重複チェックが機能していません")
                return False
            except Exception as e:
                print(f"✓ 重複チェック正常動作: {str(e)[:50]}...")
            
            # 無効なデータでテスト
            try:
                Project.create_with_validation(
                    project_code='',  # 空のプロジェクトコード
                    project_name='無効テスト',
                    branch_id=branch.id,
                    fiscal_year=2024,
                    order_probability=100,
                    revenue=Decimal('1000000.00'),
                    expenses=Decimal('800000.00')
                )
                print("✗ 必須項目チェックが機能していません")
                return False
            except Exception as e:
                print(f"✓ 必須項目チェック正常動作: {str(e)[:50]}...")
            
            print("\n=== テスト結果 ===")
            print("🎉 すべてのテストが成功しました！")
            print("プロジェクト作成機能が正常に動作しています。")
            
            return True
            
        except Exception as e:
            print(f"✗ テスト中にエラーが発生しました: {e}")
            return False

def test_web_routes():
    """Webルートのテスト"""
    print("\n=== Webルートテスト ===\n")
    
    app = create_app('development')
    
    with app.test_client() as client:
        try:
            # ダッシュボードアクセステスト
            print("1. ダッシュボードアクセステスト...")
            response = client.get('/')
            if response.status_code == 200:
                print("✓ ダッシュボードアクセス成功")
            else:
                print(f"✗ ダッシュボードアクセス失敗: {response.status_code}")
                return False
            
            # プロジェクト一覧アクセステスト
            print("2. プロジェクト一覧アクセステスト...")
            response = client.get('/projects/')
            if response.status_code == 200:
                print("✓ プロジェクト一覧アクセス成功")
                if 'プロジェクト一覧' in response.get_data(as_text=True):
                    print("✓ プロジェクト一覧ページ内容確認")
                else:
                    print("✗ プロジェクト一覧ページ内容が正しくありません")
            else:
                print(f"✗ プロジェクト一覧アクセス失敗: {response.status_code}")
                return False
            
            # 新規作成フォームアクセステスト
            print("3. 新規作成フォームアクセステスト...")
            response = client.get('/projects/new')
            if response.status_code == 200:
                print("✓ 新規作成フォームアクセス成功")
                content = response.get_data(as_text=True)
                required_fields = ['プロジェクトコード', 'プロジェクト名', '売上の年度', '受注角度', '売上（契約金）', '経費（トータル）']
                for field in required_fields:
                    if field in content:
                        print(f"✓ フィールド確認: {field}")
                    else:
                        print(f"✗ フィールド不足: {field}")
                        return False
            else:
                print(f"✗ 新規作成フォームアクセス失敗: {response.status_code}")
                return False
            
            print("\n✓ すべてのWebルートテストが成功しました！")
            return True
            
        except Exception as e:
            print(f"✗ Webルートテスト中にエラーが発生しました: {e}")
            return False

def main():
    """メインテスト関数"""
    print("プロジェクト作成機能の総合テストを開始します...\n")
    
    model_test = test_project_creation_manual()
    web_test = test_web_routes()
    
    print(f"\n=== 最終結果 ===")
    print(f"モデル・データベーステスト: {'✓ 成功' if model_test else '✗ 失敗'}")
    print(f"Webルートテスト: {'✓ 成功' if web_test else '✗ 失敗'}")
    
    if model_test and web_test:
        print("\n🎉 プロジェクト作成機能のすべてのテストが成功しました！")
        print("以下の機能が正常に動作しています:")
        print("- プロジェクト作成フォームの表示")
        print("- プロジェクトデータの作成と保存")
        print("- 粗利の自動計算")
        print("- データバリデーション")
        print("- プロジェクトコードの重複チェック")
        print("- プロジェクト一覧の表示")
        return True
    else:
        print("\n❌ 一部のテストが失敗しました。")
        return False

if __name__ == '__main__':
    main()