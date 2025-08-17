#!/usr/bin/env python3
"""
プロジェクト削除機能の手動テストスクリプト
"""

from app import create_app, db
from app.models import Project, Branch
import uuid

def test_delete_functionality():
    """削除機能のテスト"""
    app = create_app()
    
    with app.app_context():
        # テスト用支社を作成
        branch = Branch.create_with_validation(
            branch_code=f'TEST-{uuid.uuid4().hex[:8].upper()}',
            branch_name=f'テスト支社-{uuid.uuid4().hex[:8]}',
            is_active=True
        )
        
        # テスト用プロジェクトを作成
        project = Project.create_with_validation(
            project_code=f'TEST-DELETE-{uuid.uuid4().hex[:8].upper()}',
            project_name='削除テスト用プロジェクト',
            branch_id=branch.id,
            fiscal_year=2024,
            order_probability=100,
            revenue=1000000,
            expenses=800000
        )
        
        print(f"作成されたプロジェクト: {project.project_code} - {project.project_name}")
        print(f"プロジェクトID: {project.id}")
        print(f"粗利: {project.gross_profit:,.2f}円")
        
        # 削除前の確認
        project_id = project.id
        assert Project.query.get(project_id) is not None
        print("✓ プロジェクトが正常に作成されました")
        
        # delete_with_validationメソッドのテスト
        result = project.delete_with_validation()
        
        print(f"削除結果: {result}")
        
        # 削除後の確認
        deleted_project = Project.query.get(project_id)
        assert deleted_project is None
        print("✓ プロジェクトが正常に削除されました")
        
        # 支社も削除
        branch.delete_with_validation()
        print("✓ テスト用支社も削除されました")
        
        print("\n🎉 すべてのテストが成功しました！")

if __name__ == '__main__':
    test_delete_functionality()