from datetime import datetime
from sqlalchemy import CheckConstraint, Index
from sqlalchemy.exc import IntegrityError
from app import db
from app.enums import OrderProbability
import re


class ValidationError(Exception):
    """カスタム検証エラー"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class FiscalYear(db.Model):
    """年度マスターデータモデル"""
    __tablename__ = 'fiscal_years'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Integer, unique=True, nullable=False, index=True)
    year_name = db.Column(db.String(20), unique=True, nullable=False)  # "2023年度"
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ（プロジェクトとの関連付け）
    # 注意: fiscal_yearは外部キーではなく、年度の数値での関連付け
    projects = db.relationship('Project', 
                              primaryjoin='FiscalYear.year == Project.fiscal_year',
                              foreign_keys='Project.fiscal_year',
                              backref='fiscal_year_master', 
                              lazy=True)
    
    def validate_data(self):
        """データ検証を実行"""
        errors = []
        
        # 年度検証
        if not self.year:
            errors.append(ValidationError('年度は必須です', 'year'))
        elif not (1900 <= self.year <= 2100):
            errors.append(ValidationError('年度は1900-2100の範囲で入力してください', 'year'))
        
        # 年度名検証
        if not self.year_name:
            errors.append(ValidationError('年度名は必須です', 'year_name'))
        elif len(self.year_name) > 20:
            errors.append(ValidationError('年度名は20文字以内で入力してください', 'year_name'))
        
        return errors
    
    def validate_unique_year(self, exclude_id=None):
        """年度の重複チェック"""
        query = FiscalYear.query.filter_by(year=self.year)
        if exclude_id:
            query = query.filter(FiscalYear.id != exclude_id)
        
        existing_year = query.first()
        if existing_year:
            raise ValidationError('この年度は既に登録されています', 'year')
    
    def validate_unique_year_name(self, exclude_id=None):
        """年度名の重複チェック"""
        query = FiscalYear.query.filter_by(year_name=self.year_name)
        if exclude_id:
            query = query.filter(FiscalYear.id != exclude_id)
        
        existing_year = query.first()
        if existing_year:
            raise ValidationError('この年度名は既に使用されています', 'year_name')
    
    @classmethod
    def create_with_validation(cls, **kwargs):
        """検証付きで年度を作成"""
        fiscal_year = cls(**kwargs)
        
        # 年度名が指定されていない場合は自動生成
        if not fiscal_year.year_name and fiscal_year.year:
            fiscal_year.year_name = f"{fiscal_year.year}年度"
        
        # データ検証
        validation_errors = fiscal_year.validate_data()
        if validation_errors:
            raise validation_errors[0]
        
        # 重複チェック
        fiscal_year.validate_unique_year()
        fiscal_year.validate_unique_year_name()
        
        try:
            db.session.add(fiscal_year)
            db.session.commit()
            return fiscal_year
        except IntegrityError as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                if 'year' in str(e):
                    raise ValidationError('この年度は既に登録されています', 'year')
                elif 'year_name' in str(e):
                    raise ValidationError('この年度名は既に使用されています', 'year_name')
            raise ValidationError('データベースエラーが発生しました', 'database')
    
    @classmethod
    def get_active_years(cls):
        """有効な年度一覧を取得"""
        return cls.query.filter_by(is_active=True).order_by(cls.year.desc()).all()
    
    @classmethod
    def get_or_create_year(cls, year):
        """年度を取得または作成"""
        existing_year = cls.query.filter_by(year=year).first()
        if existing_year:
            return existing_year
        
        return cls.create_with_validation(year=year, year_name=f"{year}年度")
    
    def to_dict(self):
        """辞書形式でデータを返す"""
        return {
            'id': self.id,
            'year': self.year,
            'year_name': self.year_name,
            'is_active': self.is_active,
            'project_count': len(self.projects) if self.projects else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<FiscalYear {self.year}: {self.year_name}>'


class Branch(db.Model):
    """支社データモデル"""
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    branch_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    branch_name = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーションシップ（プロジェクトとの関連付け）
    projects = db.relationship('Project', backref='branch', lazy=True)
    
    def validate_data(self):
        """データ検証を実行"""
        errors = []
        
        # 支社コード検証
        if not self.branch_code:
            errors.append(ValidationError('支社コードは必須です', 'branch_code'))
        elif len(self.branch_code) > 20:
            errors.append(ValidationError('支社コードは20文字以内で入力してください', 'branch_code'))
        elif not re.match(r'^[A-Za-z0-9\-_]+$', self.branch_code):
            errors.append(ValidationError('支社コードは英数字、ハイフン、アンダースコアのみ使用可能です', 'branch_code'))
        
        # 支社名検証
        if not self.branch_name:
            errors.append(ValidationError('支社名は必須です', 'branch_name'))
        elif len(self.branch_name) > 100:
            errors.append(ValidationError('支社名は100文字以内で入力してください', 'branch_name'))
        
        # 有効フラグ検証（デフォルト値があるので、Noneの場合のみエラー）
        if self.is_active is None:
            # デフォルト値を設定
            self.is_active = True
        
        return errors
    
    def validate_unique_branch_code(self, exclude_id=None):
        """支社コードの重複チェック"""
        query = Branch.query.filter_by(branch_code=self.branch_code)
        if exclude_id:
            query = query.filter(Branch.id != exclude_id)
        
        existing_branch = query.first()
        if existing_branch:
            raise ValidationError('この支社コードは既に使用されています', 'branch_code')
    
    def validate_unique_branch_name(self, exclude_id=None):
        """支社名の重複チェック"""
        query = Branch.query.filter_by(branch_name=self.branch_name)
        if exclude_id:
            query = query.filter(Branch.id != exclude_id)
        
        existing_branch = query.first()
        if existing_branch:
            raise ValidationError('この支社名は既に使用されています', 'branch_name')
    
    def validate_deletion(self):
        """削除可能かチェック（関連プロジェクトの存在確認）"""
        if self.projects:
            raise ValidationError('この支社には関連するプロジェクトが存在するため削除できません', 'branch')
    
    @classmethod
    def create_with_validation(cls, **kwargs):
        """検証付きで支社を作成"""
        branch = cls(**kwargs)
        
        # データ検証
        validation_errors = branch.validate_data()
        if validation_errors:
            # 最初のエラーメッセージを使用
            raise validation_errors[0]
        
        # 重複チェック
        branch.validate_unique_branch_code()
        branch.validate_unique_branch_name()
        
        try:
            db.session.add(branch)
            db.session.commit()
            return branch
        except IntegrityError as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                if 'branch_code' in str(e):
                    raise ValidationError('この支社コードは既に使用されています', 'branch_code')
                elif 'branch_name' in str(e):
                    raise ValidationError('この支社名は既に使用されています', 'branch_name')
            raise ValidationError('データベースエラーが発生しました', 'database')
    
    def update_with_validation(self, **kwargs):
        """検証付きで支社を更新"""
        # 更新データを設定
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 更新日を設定
        self.updated_at = datetime.utcnow()
        
        # データ検証
        validation_errors = self.validate_data()
        if validation_errors:
            # 最初のエラーメッセージを使用
            raise validation_errors[0]
        
        # 重複チェック（自分自身を除外）
        self.validate_unique_branch_code(exclude_id=self.id)
        self.validate_unique_branch_name(exclude_id=self.id)
        
        try:
            db.session.commit()
            return self
        except IntegrityError as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                if 'branch_code' in str(e):
                    raise ValidationError('この支社コードは既に使用されています', 'branch_code')
                elif 'branch_name' in str(e):
                    raise ValidationError('この支社名は既に使用されています', 'branch_name')
            raise ValidationError('データベースエラーが発生しました', 'database')
    
    def delete_with_validation(self):
        """検証付きで支社を削除"""
        # 削除可能かチェック
        self.validate_deletion()
        
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValidationError('削除処理中にエラーが発生しました', 'database')
    
    def toggle_active_status(self):
        """有効/無効状態を切り替え"""
        self.is_active = not self.is_active
        self.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            raise ValidationError('状態変更中にエラーが発生しました', 'database')
    
    @classmethod
    def get_active_branches(cls):
        """有効な支社一覧を取得"""
        return cls.query.filter_by(is_active=True).order_by(cls.branch_name).all()
    
    @classmethod
    def search_branches(cls, branch_code=None, branch_name=None, is_active=None):
        """支社検索"""
        query = cls.query
        
        if branch_code:
            query = query.filter(cls.branch_code.contains(branch_code))
        
        if branch_name:
            query = query.filter(cls.branch_name.contains(branch_name))
        
        if is_active is not None:
            query = query.filter(cls.is_active == is_active)
        
        return query.order_by(cls.branch_name)
    
    def to_dict(self):
        """辞書形式でデータを返す"""
        return {
            'id': self.id,
            'branch_code': self.branch_code,
            'branch_name': self.branch_name,
            'is_active': self.is_active,
            'project_count': len(self.projects) if self.projects else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Branch {self.branch_code}: {self.branch_name}>'


class Project(db.Model):
    """プロジェクトデータモデル"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    project_name = db.Column(db.String(200), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    fiscal_year = db.Column(db.Integer, nullable=False, index=True)
    order_probability = db.Column(db.Numeric(5, 2), nullable=False)
    revenue = db.Column(db.Numeric(15, 2), nullable=False)
    expenses = db.Column(db.Numeric(15, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table constraints
    __table_args__ = (
        CheckConstraint('order_probability IN (0, 50, 100)', 
                       name='check_order_probability_values'),
        CheckConstraint('revenue >= 0', name='check_revenue_positive'),
        CheckConstraint('expenses >= 0', name='check_expenses_positive'),
        CheckConstraint('fiscal_year >= 1900 AND fiscal_year <= 2100', 
                       name='check_fiscal_year_range'),
    )
    
    @property
    def gross_profit(self):
        """粗利を計算（売上 - 経費）"""
        return float(self.revenue) - float(self.expenses)
    
    @property
    def gross_profit_rate(self):
        """粗利率を計算（粗利 / 売上 * 100）"""
        if float(self.revenue) > 0:
            return (self.gross_profit / float(self.revenue)) * 100
        return 0.0
    
    @property
    def order_probability_enum(self):
        """受注角度のEnum表現を取得"""
        try:
            return OrderProbability.from_value(int(self.order_probability))
        except (ValueError, TypeError):
            return OrderProbability.LOW
    
    @property
    def order_probability_symbol(self):
        """受注角度の記号を取得"""
        return self.order_probability_enum.symbol
    
    @property
    def order_probability_description(self):
        """受注角度の説明を取得"""
        return self.order_probability_enum.description
    
    def validate_data(self):
        """データ検証を実行"""
        errors = []
        
        # プロジェクトコード検証
        if not self.project_code:
            errors.append(ValidationError('プロジェクトコードは必須です', 'project_code'))
        elif len(self.project_code) > 50:
            errors.append(ValidationError('プロジェクトコードは50文字以内で入力してください', 'project_code'))
        elif not re.match(r'^[A-Za-z0-9\-_]+$', self.project_code):
            errors.append(ValidationError('プロジェクトコードは英数字、ハイフン、アンダースコアのみ使用可能です', 'project_code'))
        
        # プロジェクト名検証
        if not self.project_name:
            errors.append(ValidationError('プロジェクト名は必須です', 'project_name'))
        elif len(self.project_name) > 200:
            errors.append(ValidationError('プロジェクト名は200文字以内で入力してください', 'project_name'))
        
        # 支社検証
        if not self.branch_id:
            errors.append(ValidationError('支社は必須です', 'branch_id'))
        else:
            # 有効な支社IDかチェック
            branch = Branch.query.filter_by(id=self.branch_id, is_active=True).first()
            if not branch:
                errors.append(ValidationError('有効な支社を選択してください', 'branch_id'))
        
        # 売上の年度検証
        if not self.fiscal_year:
            errors.append(ValidationError('売上の年度は必須です', 'fiscal_year'))
        elif not (1900 <= self.fiscal_year <= 2100):
            errors.append(ValidationError('売上の年度は1900-2100の範囲で入力してください', 'fiscal_year'))
        
        # 受注角度検証
        if self.order_probability is None:
            errors.append(ValidationError('受注角度は必須です', 'order_probability'))
        else:
            try:
                prob_value = int(self.order_probability)
                if prob_value not in [item.numeric_value for item in OrderProbability]:
                    errors.append(ValidationError('受注角度は有効な値（〇、△、×）を選択してください', 'order_probability'))
            except (ValueError, TypeError):
                errors.append(ValidationError('受注角度は有効な値を選択してください', 'order_probability'))
        
        # 売上検証
        if self.revenue is None:
            errors.append(ValidationError('売上（契約金）は必須です', 'revenue'))
        elif float(self.revenue) < 0:
            errors.append(ValidationError('売上（契約金）は0以上の値を入力してください', 'revenue'))
        
        # 経費検証
        if self.expenses is None:
            errors.append(ValidationError('経費（トータル）は必須です', 'expenses'))
        elif float(self.expenses) < 0:
            errors.append(ValidationError('経費（トータル）は0以上の値を入力してください', 'expenses'))
        
        return errors
    
    def validate_unique_project_code(self, exclude_id=None):
        """プロジェクトコードの重複チェック"""
        query = Project.query.filter_by(project_code=self.project_code)
        if exclude_id:
            query = query.filter(Project.id != exclude_id)
        
        existing_project = query.first()
        if existing_project:
            raise ValidationError('このプロジェクトコードは既に使用されています', 'project_code')
    
    @classmethod
    def create_with_validation(cls, **kwargs):
        """検証付きでプロジェクトを作成"""
        project = cls(**kwargs)
        
        # データ検証
        validation_errors = project.validate_data()
        if validation_errors:
            raise ValidationError('入力データに問題があります', validation_errors)
        
        # 重複チェック
        project.validate_unique_project_code()
        
        try:
            db.session.add(project)
            db.session.commit()
            return project
        except IntegrityError as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                raise ValidationError('このプロジェクトコードは既に使用されています', 'project_code')
            else:
                raise ValidationError('データベースエラーが発生しました', 'database')
    
    def update_with_validation(self, **kwargs):
        """検証付きでプロジェクトを更新"""
        # 更新データを設定
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # 更新日を設定
        self.updated_at = datetime.utcnow()
        
        # データ検証
        validation_errors = self.validate_data()
        if validation_errors:
            raise ValidationError('入力データに問題があります', validation_errors)
        
        # 重複チェック（自分自身を除外）
        self.validate_unique_project_code(exclude_id=self.id)
        
        try:
            db.session.commit()
            return self
        except IntegrityError as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                raise ValidationError('このプロジェクトコードは既に使用されています', 'project_code')
            else:
                raise ValidationError('データベースエラーが発生しました', 'database')
    
    def delete_with_validation(self):
        """検証付きでプロジェクトを削除"""
        try:
            project_name = self.project_name
            project_code = self.project_code
            
            db.session.delete(self)
            db.session.commit()
            
            return {
                'success': True,
                'project_name': project_name,
                'project_code': project_code
            }
        except Exception as e:
            db.session.rollback()
            raise ValidationError('プロジェクトの削除中にエラーが発生しました', 'database')
    
    @classmethod
    def search_projects(cls, project_code=None, project_name=None, fiscal_year=None, 
                       order_probability_min=None, order_probability_max=None, branch_id=None):
        """プロジェクト検索"""
        query = cls.query
        
        if project_code:
            query = query.filter(cls.project_code.contains(project_code))
        
        if project_name:
            query = query.filter(cls.project_name.contains(project_name))
        
        if fiscal_year:
            query = query.filter(cls.fiscal_year == fiscal_year)
        
        if order_probability_min is not None:
            query = query.filter(cls.order_probability >= order_probability_min)
        
        if order_probability_max is not None:
            query = query.filter(cls.order_probability <= order_probability_max)
        
        if branch_id:
            query = query.filter(cls.branch_id == branch_id)
        
        return query.order_by(cls.created_at.desc())
    
    def to_dict(self):
        """辞書形式でデータを返す"""
        return {
            'id': self.id,
            'project_code': self.project_code,
            'project_name': self.project_name,
            'branch_id': self.branch_id,
            'branch_name': self.branch.branch_name if self.branch else None,
            'branch_code': self.branch.branch_code if self.branch else None,
            'fiscal_year': self.fiscal_year,
            'order_probability': int(self.order_probability),
            'order_probability_symbol': self.order_probability_symbol,
            'order_probability_description': self.order_probability_description,
            'revenue': float(self.revenue),
            'expenses': float(self.expenses),
            'gross_profit': self.gross_profit,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Project {self.project_code}: {self.project_name}>'