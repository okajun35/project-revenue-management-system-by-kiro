#!/usr/bin/env python3
"""
支社機能の手動テスト
"""
from app import create_app, db
from app.models import Branch, ValidationError
from app.services.branch_service import BranchService


def test_branch_functionality():
    """支社機能のテスト"""
    app = create_app()
    
    with app.app_context():
        print("=== 支社機能テスト開始 ===")
        
        # 1. 支社作成テスト
        print("\n1. 支社作成テスト")
        try:
            branch1 = Branch.create_with_validation(
                branch_code='TKY001',
                branch_name='東京支社',
                is_active=True
            )
            print(f"✓ 支社作成成功: {branch1}")
            
            branch2 = Branch.create_with_validation(
                branch_code='OSK001',
                branch_name='大阪支社',
                is_active=True
            )
            print(f"✓ 支社作成成功: {branch2}")
            
            branch3 = Branch.create_with_validation(
                branch_code='NGY001',
                branch_name='名古屋支社',
                is_active=False
            )
            print(f"✓ 支社作成成功: {branch3}")
            
        except ValidationError as e:
            print(f"✗ 支社作成エラー: {e.message}")
        
        # 2. 重複チェックテスト
        print("\n2. 重複チェックテスト")
        try:
            Branch.create_with_validation(
                branch_code='TKY001',  # 重複
                branch_name='東京本社',
                is_active=True
            )
            print("✗ 重複チェック失敗: エラーが発生しませんでした")
        except ValidationError as e:
            print(f"✓ 重複チェック成功: {e.message}")
        
        # 3. バリデーションテスト
        print("\n3. バリデーションテスト")
        try:
            Branch.create_with_validation(
                branch_code='',  # 空の支社コード
                branch_name='テスト支社',
                is_active=True
            )
            print("✗ バリデーション失敗: エラーが発生しませんでした")
        except ValidationError as e:
            print(f"✓ バリデーション成功: {e.message}")
        
        # 4. 支社一覧取得テスト
        print("\n4. 支社一覧取得テスト")
        all_branches = BranchService.get_all_branches()
        print(f"✓ 全支社数: {len(all_branches)}")
        for branch in all_branches:
            print(f"  - {branch.branch_code}: {branch.branch_name} ({'有効' if branch.is_active else '無効'})")
        
        # 5. 有効支社のみ取得テスト
        print("\n5. 有効支社のみ取得テスト")
        active_branches = BranchService.get_active_branches()
        print(f"✓ 有効支社数: {len(active_branches)}")
        for branch in active_branches:
            print(f"  - {branch.branch_code}: {branch.branch_name}")
        
        # 6. 支社検索テスト
        print("\n6. 支社検索テスト")
        search_results = BranchService.search_branches({'branch_code': 'TKY'})
        print(f"✓ 'TKY'で検索した結果: {len(search_results)}件")
        for branch in search_results:
            print(f"  - {branch.branch_code}: {branch.branch_name}")
        
        # 7. 支社更新テスト
        print("\n7. 支社更新テスト")
        try:
            updated_branch = BranchService.update_branch(branch1.id, {
                'branch_name': '東京本社',
                'is_active': True
            })
            print(f"✓ 支社更新成功: {updated_branch.branch_name}")
        except ValidationError as e:
            print(f"✗ 支社更新エラー: {e.message}")
        
        # 8. 支社状態切り替えテスト
        print("\n8. 支社状態切り替えテスト")
        try:
            toggled_branch = BranchService.toggle_branch_status(branch2.id)
            print(f"✓ 状態切り替え成功: {toggled_branch.branch_name} -> {'有効' if toggled_branch.is_active else '無効'}")
        except ValidationError as e:
            print(f"✗ 状態切り替えエラー: {e.message}")
        
        # 9. 統計情報取得テスト
        print("\n9. 統計情報取得テスト")
        try:
            stats = BranchService.get_branch_statistics()
            print(f"✓ 統計情報取得成功:")
            print(f"  - 総支社数: {stats['total_branches']}")
            print(f"  - 有効支社数: {stats['active_branches']}")
            print(f"  - 無効支社数: {stats['inactive_branches']}")
        except ValidationError as e:
            print(f"✗ 統計情報取得エラー: {e.message}")
        
        # 10. 選択リスト用データ取得テスト
        print("\n10. 選択リスト用データ取得テスト")
        try:
            select_data = BranchService.get_branches_for_select()
            print(f"✓ 選択リスト用データ取得成功: {len(select_data)}件")
            for item in select_data:
                print(f"  - {item['display_name']}")
        except ValidationError as e:
            print(f"✗ 選択リスト用データ取得エラー: {e.message}")
        
        # 11. 支社削除テスト
        print("\n11. 支社削除テスト")
        try:
            result = BranchService.delete_branch(branch3.id)
            print(f"✓ 支社削除成功: {result}")
        except ValidationError as e:
            print(f"✗ 支社削除エラー: {e.message}")
        
        print("\n=== 支社機能テスト完了 ===")


if __name__ == '__main__':
    test_branch_functionality()