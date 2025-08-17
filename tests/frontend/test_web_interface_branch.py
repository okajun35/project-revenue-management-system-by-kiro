#!/usr/bin/env python3
"""
Task 8: プロジェクトモデルへの支社関連付けのWebインターフェーステスト
"""

from app import create_app
from app.models import Project, Branch

def test_web_interface():
    """Webインターフェースでの支社関連付けテスト"""
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("=== Webインターフェース支社関連付けテスト ===")
            
            # 1. プロジェクト一覧画面のテスト
            print("\n1. プロジェクト一覧画面のテスト:")
            response = client.get('/projects/')
            print(f"  ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                content = response.get_data(as_text=True)
                if '支社' in content:
                    print("  ✓ 支社列がプロジェクト一覧に表示されています")
                else:
                    print("  ✗ 支社列が見つかりません")
            
            # 2. プロジェクト作成フォームのテスト
            print("\n2. プロジェクト作成フォームのテスト:")
            response = client.get('/projects/new')
            print(f"  ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                content = response.get_data(as_text=True)
                if '支社' in content and 'branch_id' in content:
                    print("  ✓ 支社選択フィールドが表示されています")
                else:
                    print("  ✗ 支社選択フィールドが見つかりません")
            
            # 3. プロジェクト詳細画面のテスト
            print("\n3. プロジェクト詳細画面のテスト:")
            project = Project.query.first()
            if project:
                response = client.get(f'/projects/{project.id}')
                print(f"  ステータスコード: {response.status_code}")
                
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    if '支社' in content and project.branch.branch_name in content:
                        print(f"  ✓ 支社情報が表示されています: {project.branch.branch_name}")
                    else:
                        print("  ✗ 支社情報が見つかりません")
            else:
                print("  テスト用プロジェクトが見つかりません")
            
            # 4. API一覧のテスト
            print("\n4. プロジェクト一覧API（DataTables）のテスト:")
            response = client.get('/projects/api/list')
            print(f"  ステータスコード: {response.status_code}")
            
            if response.status_code == 200:
                import json
                data = json.loads(response.get_data(as_text=True))
                if 'data' in data and len(data['data']) > 0:
                    # 最初のプロジェクトデータをチェック
                    first_project = data['data'][0]
                    if len(first_project) >= 3:  # プロジェクトコード、名前、支社の順
                        print(f"  ✓ API応答に支社情報が含まれています: {first_project[2]}")
                    else:
                        print("  ✗ API応答の形式が正しくありません")
                else:
                    print("  ✗ APIからデータが取得できませんでした")

if __name__ == "__main__":
    test_web_interface()