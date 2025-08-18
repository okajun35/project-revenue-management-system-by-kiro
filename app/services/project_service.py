from app.models import Project, ValidationError
from app.services.validation_service import ValidationService
from app import db
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class ProjectService:
    """プロジェクト管理のビジネスロジック"""
    _svc = BaseService[Project](Project)
    
    @staticmethod
    def create_project(data):
        """プロジェクトを作成"""
        try:
            # 基本データ検証
            validation_errors = ValidationService.validate_project_data(data)
            if validation_errors:
                return ValidationService.handle_validation_error(
                    ValidationError('入力データに問題があります', validation_errors)
                )
            
            # プロジェクト作成
            project = Project.create_with_validation(**data)
            
            return ValidationService.create_success_response(
                data=project.to_dict(),
                message='プロジェクトが正常に作成されました'
            )
            
        except ValidationError as e:
            return ValidationService.handle_validation_error(e)
        except IntegrityError as e:
            return ValidationService.handle_database_error(e)
        except SQLAlchemyError as e:
            return ValidationService.handle_database_error(e)
        except Exception as e:
            return ValidationService.handle_generic_error(e)
    
    @staticmethod
    def update_project(project_id, data):
        """プロジェクトを更新"""
        try:
            # プロジェクト存在チェック
            project = Project.query.get(project_id)
            if not project:
                return ValidationService.create_error_response(
                    'PROJECT_NOT_FOUND',
                    'プロジェクトが見つかりません',
                    status_code=404
                )
            
            # 基本データ検証
            validation_errors = ValidationService.validate_project_data(data)
            if validation_errors:
                return ValidationService.handle_validation_error(
                    ValidationError('入力データに問題があります', validation_errors)
                )
            
            # プロジェクト更新
            project.update_with_validation(**data)
            
            return ValidationService.create_success_response(
                data=project.to_dict(),
                message='プロジェクトが正常に更新されました'
            )
            
        except ValidationError as e:
            return ValidationService.handle_validation_error(e)
        except IntegrityError as e:
            return ValidationService.handle_database_error(e)
        except SQLAlchemyError as e:
            return ValidationService.handle_database_error(e)
        except Exception as e:
            return ValidationService.handle_generic_error(e)
    
    @staticmethod
    def delete_project(project_id):
        """プロジェクトを削除"""
        try:
            # プロジェクト存在チェック
            project = Project.query.get(project_id)
            if not project:
                return ValidationService.create_error_response(
                    'PROJECT_NOT_FOUND',
                    'プロジェクトが見つかりません',
                    status_code=404
                )
            
            # プロジェクト削除
            db.session.delete(project)
            db.session.commit()
            
            return ValidationService.create_success_response(
                message='プロジェクトが正常に削除されました'
            )
            
        except SQLAlchemyError as e:
            db.session.rollback()
            return ValidationService.handle_database_error(e)
        except Exception as e:
            db.session.rollback()
            return ValidationService.handle_generic_error(e)
    
    @staticmethod
    def get_project(project_id):
        """プロジェクトを取得"""
        try:
            project = ProjectService._svc.get(project_id)
            if not project:
                return ValidationService.create_error_response(
                    'PROJECT_NOT_FOUND',
                    'プロジェクトが見つかりません',
                    status_code=404
                )
            
            return ValidationService.create_success_response(
                data=project.to_dict()
            )
            
        except Exception as e:
            return ValidationService.handle_generic_error(e)
    
    @staticmethod
    def search_projects(search_params=None, page=1, per_page=20):
        """プロジェクトを検索"""
        try:
            if search_params is None:
                search_params = {}
            
            # 検索クエリ構築
            query = Project.search_projects(
                project_code=search_params.get('project_code'),
                project_name=search_params.get('project_name'),
                fiscal_year=search_params.get('fiscal_year'),
                order_probability_min=search_params.get('order_probability_min'),
                order_probability_max=search_params.get('order_probability_max')
            )
            
            # ページネーション
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # レスポンスデータ構築
            projects_data = [project.to_dict() for project in pagination.items]
            
            response_data = {
                'projects': projects_data,
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next,
                    'prev_num': pagination.prev_num,
                    'next_num': pagination.next_num
                }
            }
            
            return ValidationService.create_success_response(data=response_data)
            
        except Exception as e:
            return ValidationService.handle_generic_error(e)
    
    @staticmethod
    def get_all_projects():
        """全プロジェクトを取得"""
        try:
            projects = Project.query.order_by(Project.created_at.desc()).all()
            projects_data = [project.to_dict() for project in projects]
            
            return ValidationService.create_success_response(data=projects_data)
            
        except Exception as e:
            return ValidationService.handle_generic_error(e)
    
    @staticmethod
    def validate_project_code_unique(project_code, exclude_id=None):
        """プロジェクトコードの重複チェック"""
        try:
            query = Project.query.filter_by(project_code=project_code)
            if exclude_id:
                query = query.filter(Project.id != exclude_id)
            
            existing_project = query.first()
            
            if existing_project:
                return ValidationService.create_error_response(
                    'DUPLICATE_PROJECT_CODE',
                    'このプロジェクトコードは既に使用されています'
                )
            else:
                return ValidationService.create_success_response(
                    message='プロジェクトコードは使用可能です'
                )
                
        except Exception as e:
            return ValidationService.handle_generic_error(e)