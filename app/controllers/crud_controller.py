"""
CRUD操作の共通コントローラー

標準的なCRUD操作を提供
"""
from flask import render_template, redirect, url_for, flash, request
from app import db
from app.models import ValidationError
from .base_controller import BaseController


class CRUDController(BaseController):
    """CRUD操作の共通コントローラー"""
    
    def index(self):
        """一覧表示"""
        context = self.get_list_context()
        return render_template(self.get_template_path('index'), **context)
    
    def show(self, item_id):
        """詳細表示"""
        item = self.model_class.query.get_or_404(item_id)
        return render_template(self.get_template_path('show'), item=item)
    
    def new(self):
        """新規作成フォーム"""
        form = self.form_class()
        self.prepare_form_data(form)
        context = self.get_form_context(form, title=f'{self.template_prefix}新規作成')
        return render_template(self.get_template_path('form'), **context)
    
    def create(self):
        """新規作成処理"""
        form = self.form_class()
        self.prepare_form_data(form)
        
        if form.validate_on_submit():
            try:
                # フォームデータを辞書に変換
                form_data = {field.name: field.data for field in form if field.name != 'csrf_token'}
                
                # モデルの作成メソッドを呼び出し
                if hasattr(self.model_class, 'create_with_validation'):
                    item = self.model_class.create_with_validation(**form_data)
                else:
                    item = self.model_class(**form_data)
                    db.session.add(item)
                    db.session.commit()
                
                item_name = self.get_item_display_name(item)
                self.handle_success_message('create', item_name)
                return redirect(url_for(self.get_url_endpoint('index')))
                
            except ValidationError as e:
                self.handle_validation_error(form, e)
            except Exception as e:
                flash(f'{self.template_prefix}の作成中にエラーが発生しました。', 'error')
                db.session.rollback()
        
        context = self.get_form_context(form, title=f'{self.template_prefix}新規作成')
        return render_template(self.get_template_path('form'), **context)
    
    def edit(self, item_id):
        """編集フォーム"""
        item = self.model_class.query.get_or_404(item_id)
        form = self.form_class(obj=item)
        self.prepare_form_data(form, item=item)
        context = self.get_form_context(form, item=item, title=f'{self.template_prefix}編集')
        return render_template(self.get_template_path('form'), **context)
    
    def update(self, item_id):
        """更新処理"""
        item = self.model_class.query.get_or_404(item_id)
        form = self.form_class()
        self.prepare_form_data(form, item=item)
        
        if form.validate_on_submit():
            try:
                # フォームデータを辞書に変換
                form_data = {field.name: field.data for field in form if field.name != 'csrf_token'}
                
                # モデルの更新メソッドを呼び出し
                if hasattr(item, 'update_with_validation'):
                    item.update_with_validation(**form_data)
                else:
                    for key, value in form_data.items():
                        if hasattr(item, key):
                            setattr(item, key, value)
                    db.session.commit()
                
                item_name = self.get_item_display_name(item)
                self.handle_success_message('update', item_name)
                return redirect(url_for(self.get_url_endpoint('index')))
                
            except ValidationError as e:
                self.handle_validation_error(form, e)
            except Exception as e:
                flash(f'{self.template_prefix}の更新中にエラーが発生しました。', 'error')
                db.session.rollback()
        
        context = self.get_form_context(form, item=item, title=f'{self.template_prefix}編集')
        return render_template(self.get_template_path('form'), **context)
    
    def delete(self, item_id):
        """削除処理"""
        item = self.model_class.query.get_or_404(item_id)
        
        try:
            item_name = self.get_item_display_name(item)
            
            # モデルの削除メソッドを呼び出し
            if hasattr(item, 'delete_with_validation'):
                result = item.delete_with_validation()
                if isinstance(result, dict) and result.get('success'):
                    item_name = result.get('project_name', item_name)
            else:
                db.session.delete(item)
                db.session.commit()
            
            self.handle_success_message('delete', item_name)
            
        except ValidationError as e:
            flash(f'削除エラー: {e.message}', 'error')
        except Exception as e:
            flash(f'{self.template_prefix}の削除中にエラーが発生しました。', 'error')
            db.session.rollback()
        
        return redirect(url_for(self.get_url_endpoint('index')))
    
    def toggle_status(self, item_id):
        """状態切り替え処理（有効/無効など）"""
        item = self.model_class.query.get_or_404(item_id)
        
        try:
            if hasattr(item, 'toggle_active_status'):
                item.toggle_active_status()
            else:
                # デフォルトの状態切り替え
                if hasattr(item, 'is_active'):
                    item.is_active = not item.is_active
                    db.session.commit()
            
            item_name = self.get_item_display_name(item)
            self.handle_success_message('toggle', item_name)
            
        except ValidationError as e:
            flash(f'状態変更エラー: {e.message}', 'error')
        except Exception as e:
            flash(f'{self.template_prefix}の状態変更中にエラーが発生しました。', 'error')
            db.session.rollback()
        
        return redirect(url_for(self.get_url_endpoint('index')))
    
    def get_item_display_name(self, item):
        """アイテムの表示名を取得（サブクラスでオーバーライド）"""
        if hasattr(item, 'name'):
            return item.name
        elif hasattr(item, 'project_name'):
            return item.project_name
        elif hasattr(item, 'branch_name'):
            return item.branch_name
        elif hasattr(item, 'year_name'):
            return item.year_name
        else:
            return str(item)