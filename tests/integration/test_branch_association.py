#!/usr/bin/env python3
"""
Task 8: プロジェクトモデルへの支社関連付けのテスト
"""

from app import create_app
from app.models import Project, Branch, ValidationError

def test_branch_association():
    """支社関連付けのテストを実行"""
    
    app = create_app()
    
    with app.app_context():
        print("=== プロジェクトと支社の関連付けテスト ===")
        
        # 1. 既存のプロジェクトと支社の関連付けを確認
        print("\n1. 既存のプロジェクトと支社の関連付けを確認:")
        projects = Project.query.limit(5).all()
        for project in projects:
            branch_name = project.branch.branch_name if project.branch else "関連付けなし"
            print(f"  {project.project_code}: {project.project_name} -> {branch_name}")
        
        # 2. 有効な支社一覧を確認
        print("\n2. 有効な支社一覧:")
        active_branches = Branch.get_active_branches()
        for branch in active_branches:
            project_count = len(branch.projects)
            print(f"  {branch.branch_code}: {branch.branch_name} (プロジェクト数: {project_count})")
        
        # 3. 支社バリデーションのテスト
        print("\n3. 支社バリデーションのテスト:")
        
        # 有効な支社でプロジェクト作成テスト
        if active_branches:
            test_branch = active_branches[0]
            print(f"  有効な支社 ({test_branch.branch_name}) でプロジェクト作成テスト...")
            
            try:
                test_project = Project(
                    project_code="TEST_BRANCH_001",
                    project_name="支社関連付けテストプロジェクト",
                    branch_id=test_branch.id,
                    fiscal_year=2024,
                    order_probability=100,
                    revenue=1000000,
                    expenses=800000
                )
                
                validation_errors = test_project.validate_data()
                if validation_errors:
                    print(f"    バリデーションエラー: {[error.message for error in validation_errors]}")
                else:
                    print("    ✓ 有効な支社でのバリデーション成功")
                
            except Exception as e:
                print(f"    エラー: {e}")
        
        # 無効な支社IDでのテスト
        print("  無効な支社IDでプロジェクト作成テスト...")
        try:
            invalid_project = Project(
                project_code="TEST_INVALID_001",
                project_name="無効支社テストプロジェクト",
                branch_id=99999,  # 存在しない支社ID
                fiscal_year=2024,
                order_probability=100,
                revenue=1000000,
                expenses=800000
            )
            
            validation_errors = invalid_project.validate_data()
            if validation_errors:
                error_messages = [error.message for error in validation_errors if error.field == 'branch_id']
                if error_messages:
                    print(f"    ✓ 無効な支社IDでのバリデーションエラー: {error_messages[0]}")
                else:
                    print("    ✗ 支社バリデーションが機能していません")
            else:
                print("    ✗ 無効な支社IDでもバリデーションが通ってしまいました")
                
        except Exception as e:
            print(f"    エラー: {e}")
        
        # 4. 支社による検索テスト
        print("\n4. 支社による検索テスト:")
        if active_branches:
            test_branch = active_branches[0]
            branch_projects = Project.search_projects(branch_id=test_branch.id).all()
            print(f"  支社 '{test_branch.branch_name}' のプロジェクト数: {len(branch_projects)}")
            
            for project in branch_projects[:3]:  # 最初の3件を表示
                print(f"    - {project.project_code}: {project.project_name}")
        
        # 5. プロジェクトのto_dict()メソッドで支社情報が含まれるかテスト
        print("\n5. プロジェクトのto_dict()メソッドテスト:")
        if projects:
            test_project = projects[0]
            project_dict = test_project.to_dict()
            
            required_branch_fields = ['branch_id', 'branch_name', 'branch_code']
            missing_fields = [field for field in required_branch_fields if field not in project_dict]
            
            if missing_fields:
                print(f"    ✗ 不足している支社関連フィールド: {missing_fields}")
            else:
                print("    ✓ 支社関連フィールドが正しく含まれています")
                print(f"      支社ID: {project_dict['branch_id']}")
                print(f"      支社名: {project_dict['branch_name']}")
                print(f"      支社コード: {project_dict['branch_code']}")

if __name__ == "__main__":
    test_branch_association()