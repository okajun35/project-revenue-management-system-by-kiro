from flask import jsonify
from app.models import ValidationError
import logging

logger = logging.getLogger(__name__)


class ValidationService:
    """データ検証とエラーハンドリングサービス"""
    
    @staticmethod
    def format_validation_errors(errors):
        """検証エラーを統一フォーマットに変換"""
        if isinstance(errors, list):
            # 複数のValidationErrorオブジェクトのリスト
            formatted_errors = []
            for error in errors:
                if isinstance(error, ValidationError):
                    formatted_errors.append({
                        'field': error.field,
                        'message': error.message
                    })
                else:
                    formatted_errors.append({
                        'field': 'general',
                        'message': str(error)
                    })
            return formatted_errors
        elif isinstance(errors, ValidationError):
            # 単一のValidationErrorオブジェクト
            if isinstance(errors.field, list):
                # fieldが検証エラーのリストの場合
                return ValidationService.format_validation_errors(errors.field)
            else:
                return [{
                    'field': errors.field or 'general',
                    'message': errors.message
                }]
        else:
            # その他のエラー
            return [{
                'field': 'general',
                'message': str(errors)
            }]
    
    @staticmethod
    def create_error_response(error_code, message, details=None, status_code=400):
        """統一されたエラーレスポンスを作成"""
        response_data = {
            'success': False,
            'error': {
                'code': error_code,
                'message': message
            }
        }
        
        if details:
            response_data['error']['details'] = ValidationService.format_validation_errors(details)
        
        return jsonify(response_data), status_code
    
    @staticmethod
    def create_success_response(data=None, message='操作が正常に完了しました'):
        """統一された成功レスポンスを作成"""
        response_data = {
            'success': True,
            'message': message
        }
        
        if data is not None:
            response_data['data'] = data
        
        return jsonify(response_data)
    
    @staticmethod
    def validate_project_data(data):
        """プロジェクトデータの基本検証"""
        errors = []
        
        # 必須フィールドチェック
        required_fields = ['project_code', 'project_name', 'fiscal_year', 
                          'order_probability', 'revenue', 'expenses']
        
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                field_names = {
                    'project_code': 'プロジェクトコード',
                    'project_name': 'プロジェクト名',
                    'fiscal_year': '売上の年度',
                    'order_probability': '受注角度',
                    'revenue': '売上（契約金）',
                    'expenses': '経費（トータル）'
                }
                errors.append(ValidationError(
                    f'{field_names[field]}は必須です', field
                ))
        
        # データ型と範囲チェック
        try:
            if 'fiscal_year' in data and data['fiscal_year'] is not None:
                fiscal_year = int(data['fiscal_year'])
                if not (1900 <= fiscal_year <= 2100):
                    errors.append(ValidationError(
                        '売上の年度は1900-2100の範囲で入力してください', 'fiscal_year'
                    ))
        except (ValueError, TypeError):
            errors.append(ValidationError(
                '売上の年度は有効な数値を入力してください', 'fiscal_year'
            ))
        
        try:
            if 'order_probability' in data and data['order_probability'] is not None:
                from app.enums import OrderProbability
                order_probability = int(data['order_probability'])
                valid_values = [item.numeric_value for item in OrderProbability]
                if order_probability not in valid_values:
                    errors.append(ValidationError(
                        '受注角度は有効な値（〇、△、×）を選択してください', 'order_probability'
                    ))
        except (ValueError, TypeError):
            errors.append(ValidationError(
                '受注角度は有効な値を選択してください', 'order_probability'
            ))
        
        try:
            if 'revenue' in data and data['revenue'] is not None:
                revenue = float(data['revenue'])
                if revenue < 0:
                    errors.append(ValidationError(
                        '売上（契約金）は0以上の値を入力してください', 'revenue'
                    ))
        except (ValueError, TypeError):
            errors.append(ValidationError(
                '売上（契約金）は有効な数値を入力してください', 'revenue'
            ))
        
        try:
            if 'expenses' in data and data['expenses'] is not None:
                expenses = float(data['expenses'])
                if expenses < 0:
                    errors.append(ValidationError(
                        '経費（トータル）は0以上の値を入力してください', 'expenses'
                    ))
        except (ValueError, TypeError):
            errors.append(ValidationError(
                '経費（トータル）は有効な数値を入力してください', 'expenses'
            ))
        
        return errors
    
    @staticmethod
    def handle_database_error(error):
        """データベースエラーのハンドリング"""
        logger.error(f"Database error: {str(error)}")
        
        error_message = str(error).lower()
        
        if 'unique constraint failed' in error_message:
            if 'project_code' in error_message:
                return ValidationService.create_error_response(
                    'DUPLICATE_PROJECT_CODE',
                    'このプロジェクトコードは既に使用されています',
                    [ValidationError('このプロジェクトコードは既に使用されています', 'project_code')]
                )
            else:
                return ValidationService.create_error_response(
                    'DUPLICATE_DATA',
                    '重複するデータが存在します'
                )
        elif 'check constraint failed' in error_message:
            return ValidationService.create_error_response(
                'CONSTRAINT_VIOLATION',
                'データの制約に違反しています'
            )
        else:
            return ValidationService.create_error_response(
                'DATABASE_ERROR',
                'データベースエラーが発生しました',
                status_code=500
            )
    
    @staticmethod
    def handle_validation_error(error):
        """検証エラーのハンドリング"""
        if isinstance(error, ValidationError):
            return ValidationService.create_error_response(
                'VALIDATION_ERROR',
                '入力データに問題があります',
                error
            )
        else:
            return ValidationService.create_error_response(
                'VALIDATION_ERROR',
                '入力データに問題があります',
                [ValidationError(str(error), 'general')]
            )
    
    @staticmethod
    def handle_generic_error(error):
        """一般的なエラーのハンドリング"""
        logger.error(f"Generic error: {str(error)}")
        return ValidationService.create_error_response(
            'INTERNAL_ERROR',
            'システムエラーが発生しました',
            status_code=500
        )