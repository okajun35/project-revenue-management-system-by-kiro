"""
基底コントローラークラス

DRY原則に基づいて共通処理を提供
"""
from flask import render_template, redirect, url_for, flash, request, jsonify
from app import db
from app.models import ValidationError


class BaseController:
    """基底コントローラークラス"""
    
    def __init__(self, model_class, form_class, template_prefix, url_prefix):
        """
        Args:
            model_class: モデルクラス
            form_class: フォームクラス
            template_prefix: テンプレートのプレフィックス（例: 'projects'）
            url_prefix: URLのプレフィックス（例: 'projects'）
        """
        self.model_class = model_class
        self.form_class = form_class
        self.template_prefix = template_prefix
        self.url_prefix = url_prefix
    
    def get_template_path(self, template_name):
        """テンプレートパスを生成"""
        return f'{self.template_prefix}/{template_name}.html'
    
    def get_url_endpoint(self, action):
        """URLエンドポイントを生成"""
        return f'{self.url_prefix}.{action}'
    
    def handle_validation_error(self, form, error):
        """バリデーションエラーの共通処理"""
        if hasattr(error, 'field') and error.field and hasattr(form, error.field):
            getattr(form, error.field).errors.append(error.message)
        else:
            flash(error.message, 'error')
    
    def handle_success_message(self, action, item_name):
        """成功メッセージの共通処理"""
        messages = {
            'create': f'✅ {item_name}を正常に作成しました。',
            'update': f'✅ {item_name}を正常に更新しました。',
            'delete': f'🗑️ {item_name}を正常に削除しました。',
            'toggle': f'🔄 {item_name}の状態を変更しました。'
        }
        flash(messages.get(action, f'✅ 操作が完了しました。'), 'success')
    
    def get_form_choices(self):
        """フォームの選択肢を取得（サブクラスでオーバーライド）"""
        return {}
    
    def prepare_form_data(self, form, **kwargs):
        """フォームデータの準備（サブクラスでオーバーライド）"""
        choices = self.get_form_choices()
        for field_name, choice_list in choices.items():
            if hasattr(form, field_name):
                getattr(form, field_name).choices = choice_list
    
    def get_list_context(self):
        """一覧画面のコンテキスト取得（サブクラスでオーバーライド）"""
        return {}
    
    def get_form_context(self, form, item=None, title=None):
        """フォーム画面のコンテキスト取得"""
        context = {
            'form': form,
            'title': title or ('編集' if item else '新規作成')
        }
        if item:
            context['item'] = item
        return context