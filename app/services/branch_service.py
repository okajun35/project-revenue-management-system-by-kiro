"""
支社管理のビジネスロジック
"""
from typing import List, Optional, Dict, Any
from app.models import Branch, ValidationError
from app import db


class BranchService:
    """支社管理サービス"""
    
    @staticmethod
    def get_all_branches(include_inactive: bool = True) -> List[Branch]:
        """全支社を取得"""
        query = Branch.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(Branch.branch_name).all()
    
    @staticmethod
    def get_active_branches() -> List[Branch]:
        """有効な支社のみを取得"""
        return Branch.get_active_branches()
    
    @staticmethod
    def get_branch_by_id(branch_id: int) -> Optional[Branch]:
        """IDで支社を取得"""
        return Branch.query.get(branch_id)
    
    @staticmethod
    def get_branch_by_code(branch_code: str) -> Optional[Branch]:
        """支社コードで支社を取得"""
        return Branch.query.filter_by(branch_code=branch_code).first()
    
    @staticmethod
    def get_branch_by_name(branch_name: str) -> Optional[Branch]:
        """支社名で支社を取得"""
        return Branch.query.filter_by(branch_name=branch_name).first()
    
    @staticmethod
    def create_branch(branch_data: Dict[str, Any]) -> Branch:
        """新規支社を作成"""
        try:
            return Branch.create_with_validation(**branch_data)
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f'支社作成中にエラーが発生しました: {str(e)}', 'system')
    
    @staticmethod
    def update_branch(branch_id: int, branch_data: Dict[str, Any]) -> Branch:
        """支社を更新"""
        branch = BranchService.get_branch_by_id(branch_id)
        if not branch:
            raise ValidationError('指定された支社が見つかりません', 'branch_id')
        
        try:
            return branch.update_with_validation(**branch_data)
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f'支社更新中にエラーが発生しました: {str(e)}', 'system')
    
    @staticmethod
    def delete_branch(branch_id: int) -> bool:
        """支社を削除"""
        branch = BranchService.get_branch_by_id(branch_id)
        if not branch:
            raise ValidationError('指定された支社が見つかりません', 'branch_id')
        
        try:
            branch.delete_with_validation()
            return True
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f'支社削除中にエラーが発生しました: {str(e)}', 'system')
    
    @staticmethod
    def toggle_branch_status(branch_id: int) -> Branch:
        """支社の有効/無効状態を切り替え"""
        branch = BranchService.get_branch_by_id(branch_id)
        if not branch:
            raise ValidationError('指定された支社が見つかりません', 'branch_id')
        
        try:
            return branch.toggle_active_status()
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f'支社状態変更中にエラーが発生しました: {str(e)}', 'system')
    
    @staticmethod
    def search_branches(search_params: Dict[str, Any]) -> List[Branch]:
        """支社を検索"""
        try:
            query = Branch.search_branches(
                branch_code=search_params.get('branch_code'),
                branch_name=search_params.get('branch_name'),
                is_active=search_params.get('is_active')
            )
            return query.all()
        except Exception as e:
            raise ValidationError(f'支社検索中にエラーが発生しました: {str(e)}', 'system')
    
    @staticmethod
    def validate_branch_data(branch_data: Dict[str, Any], exclude_id: Optional[int] = None) -> List[ValidationError]:
        """支社データの検証"""
        errors = []
        
        # 必須項目チェック
        if not branch_data.get('branch_code'):
            errors.append(ValidationError('支社コードは必須です', 'branch_code'))
        
        if not branch_data.get('branch_name'):
            errors.append(ValidationError('支社名は必須です', 'branch_name'))
        
        # 重複チェック
        if branch_data.get('branch_code'):
            existing_branch = BranchService.get_branch_by_code(branch_data['branch_code'])
            if existing_branch and (not exclude_id or existing_branch.id != exclude_id):
                errors.append(ValidationError('この支社コードは既に使用されています', 'branch_code'))
        
        if branch_data.get('branch_name'):
            existing_branch = BranchService.get_branch_by_name(branch_data['branch_name'])
            if existing_branch and (not exclude_id or existing_branch.id != exclude_id):
                errors.append(ValidationError('この支社名は既に使用されています', 'branch_name'))
        
        return errors
    
    @staticmethod
    def get_branch_statistics() -> Dict[str, Any]:
        """支社統計情報を取得"""
        try:
            total_branches = Branch.query.count()
            active_branches = Branch.query.filter_by(is_active=True).count()
            inactive_branches = total_branches - active_branches
            
            return {
                'total_branches': total_branches,
                'active_branches': active_branches,
                'inactive_branches': inactive_branches
            }
        except Exception as e:
            raise ValidationError(f'統計情報取得中にエラーが発生しました: {str(e)}', 'system')
    
    @staticmethod
    def get_branches_for_select() -> List[Dict[str, Any]]:
        """選択リスト用の支社データを取得"""
        try:
            branches = BranchService.get_active_branches()
            return [
                {
                    'id': branch.id,
                    'branch_code': branch.branch_code,
                    'branch_name': branch.branch_name,
                    'display_name': f'{branch.branch_code} - {branch.branch_name}'
                }
                for branch in branches
            ]
        except Exception as e:
            raise ValidationError(f'支社選択リスト取得中にエラーが発生しました: {str(e)}', 'system')