from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, Regexp
from wtforms.widgets import NumberInput
from app.models import Project, Branch
from app.enums import OrderProbability
from app import db
import re


class CustomNumberRange:
    """カスタム数値範囲バリデーター"""
    def __init__(self, min=None, max=None, message=None):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form, field):
        data = field.data
        if data is None:
            return

        if self.min is not None and data < self.min:
            raise ValidationError(self.message or f'値は{self.min}以上である必要があります')
        
        if self.max is not None and data > self.max:
            raise ValidationError(self.message or f'値は{self.max}以下である必要があります')


class ProjectForm(FlaskForm):
    """プロジェクト作成・編集フォーム"""
    
    project_code = StringField(
        'プロジェクトコード',
        validators=[
            DataRequired(message='プロジェクトコードは必須です'),
            Length(min=1, max=50, message='プロジェクトコードは1-50文字で入力してください'),
            Regexp(
                r'^[A-Za-z0-9\-_]+$',
                message='プロジェクトコードは英数字、ハイフン、アンダースコアのみ使用可能です'
            )
        ],
        render_kw={'class': 'form-control', 'placeholder': '例: PROJ-2024-001'}
    )
    
    project_name = StringField(
        'プロジェクト名',
        validators=[
            DataRequired(message='プロジェクト名は必須です'),
            Length(min=1, max=200, message='プロジェクト名は1-200文字で入力してください')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'プロジェクト名を入力してください'}
    )
    
    branch_id = SelectField(
        '支社',
        validators=[
            DataRequired(message='支社は必須です')
        ],
        coerce=int,
        render_kw={'class': 'form-control'}
    )
    
    fiscal_year = SelectField(
        '売上の年度',
        validators=[
            DataRequired(message='売上の年度は必須です')
        ],
        coerce=int,
        render_kw={'class': 'form-control'}
    )
    
    order_probability = SelectField(
        '受注角度',
        choices=OrderProbability.get_choices(),
        validators=[
            DataRequired(message='受注角度は必須です')
        ],
        coerce=int,
        render_kw={'class': 'form-control'}
    )
    
    revenue = DecimalField(
        '売上（契約金）',
        validators=[
            DataRequired(message='売上（契約金）は必須です'),
            CustomNumberRange(min=0, message='売上（契約金）は0以上の値を入力してください')
        ],
        places=2,
        render_kw={'class': 'form-control', 'placeholder': '1000000.00', 'step': '0.01'}
    )
    
    expenses = DecimalField(
        '経費（トータル）',
        validators=[
            DataRequired(message='経費（トータル）は必須です'),
            CustomNumberRange(min=0, message='経費（トータル）は0以上の値を入力してください')
        ],
        places=2,
        render_kw={'class': 'form-control', 'placeholder': '800000.00', 'step': '0.01'}
    )
    
    def __init__(self, project_id=None, *args, **kwargs):
        """フォーム初期化時にプロジェクトIDを設定（編集時の重複チェック用）"""
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.project_id = project_id
    
    def validate_project_code(self, field):
        """プロジェクトコードの重複チェック"""
        query = Project.query.filter_by(project_code=field.data)
        
        # 編集時は自分自身を除外
        if self.project_id:
            query = query.filter(Project.id != self.project_id)
        
        existing_project = query.first()
        if existing_project:
            raise ValidationError('このプロジェクトコードは既に使用されています')
    
    def validate_revenue(self, field):
        """売上の追加検証"""
        if field.data is not None and field.data < 0:
            raise ValidationError('売上は0以上の値を入力してください')
    
    def validate_expenses(self, field):
        """経費の追加検証"""
        if field.data is not None and field.data < 0:
            raise ValidationError('経費は0以上の値を入力してください')
    
    def validate_branch_id(self, field):
        """支社の追加検証"""
        if field.data == 0:
            raise ValidationError('支社を選択してください')
        
        # 有効な支社かチェック
        branch = Branch.query.filter_by(id=field.data, is_active=True).first()
        if not branch:
            raise ValidationError('有効な支社を選択してください')
    
    def validate_fiscal_year(self, field):
        """年度の追加検証"""
        if field.data == 0:
            raise ValidationError('年度を選択してください')
        
        # 有効な年度かチェック
        from app.models import FiscalYear
        fiscal_year = FiscalYear.query.filter_by(year=field.data, is_active=True).first()
        if not fiscal_year:
            raise ValidationError('有効な年度を選択してください')


class ProjectSearchForm(FlaskForm):
    """プロジェクト検索フォーム"""
    
    project_code = StringField(
        'プロジェクトコード',
        validators=[Length(max=50, message='プロジェクトコードは50文字以内で入力してください')],
        render_kw={'class': 'form-control', 'placeholder': 'プロジェクトコードで検索'}
    )
    
    project_name = StringField(
        'プロジェクト名',
        validators=[Length(max=200, message='プロジェクト名は200文字以内で入力してください')],
        render_kw={'class': 'form-control', 'placeholder': 'プロジェクト名で検索'}
    )
    
    fiscal_year = SelectField(
        '売上の年度',
        choices=[('', '全て')] + [(str(year), str(year)) for year in range(2020, 2031)],
        render_kw={'class': 'form-control'}
    )
    
    order_probability = SelectField(
        '受注角度',
        choices=[('', '全て')] + OrderProbability.get_choices(),
        render_kw={'class': 'form-control'}
    )
    



class ImportForm(FlaskForm):
    """ファイルインポートフォーム"""
    
    file_type = SelectField(
        'ファイル形式',
        choices=[
            ('csv', 'CSV形式'),
            ('excel', 'Excel形式')
        ],
        validators=[DataRequired(message='ファイル形式を選択してください')],
        render_kw={'class': 'form-control'}
    )
    
    def validate_file_upload(self, file):
        """アップロードファイルの検証"""
        if not file:
            raise ValidationError('ファイルを選択してください')
        
        filename = file.filename.lower()
        file_type = self.file_type.data
        
        if file_type == 'csv' and not filename.endswith('.csv'):
            raise ValidationError('CSV形式のファイルを選択してください')
        elif file_type == 'excel' and not (filename.endswith('.xlsx') or filename.endswith('.xls')):
            raise ValidationError('Excel形式のファイルを選択してください')