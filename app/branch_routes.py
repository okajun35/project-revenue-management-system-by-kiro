"""
支社管理のルートとコントローラー
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services.branch_service import BranchService
from app.models import ValidationError
import logging

# ログ設定
logger = logging.getLogger(__name__)

# ブループリント作成
branch_bp = Blueprint('branches', __name__, url_prefix='/branches')


@branch_bp.route('/')
def index():
    """支社一覧画面"""
    try:
        branches = BranchService.get_all_branches()
        return render_template('branches/index.html', branches=branches)
    except Exception as e:
        logger.error(f"支社一覧取得エラー: {e}")
        flash('支社一覧の取得中にエラーが発生しました', 'error')
        return render_template('branches/index.html', branches=[])


@branch_bp.route('/new')
def new():
    """新規支社作成フォーム"""
    return render_template('branches/form.html', branch=None, action='create')


@branch_bp.route('/', methods=['POST'])
def create():
    """支社作成処理"""
    try:
        branch_data = {
            'branch_code': request.form.get('branch_code', '').strip(),
            'branch_name': request.form.get('branch_name', '').strip(),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        # データ検証
        validation_errors = BranchService.validate_branch_data(branch_data)
        if validation_errors:
            for error in validation_errors:
                flash(error.message, 'error')
            return render_template('branches/form.html', 
                                 branch=branch_data, 
                                 action='create')
        
        # 支社作成
        branch = BranchService.create_branch(branch_data)
        flash(f'支社「{branch.branch_name}」を作成しました', 'success')
        return redirect(url_for('branches.index'))
        
    except ValidationError as e:
        flash(e.message, 'error')
        return render_template('branches/form.html', 
                             branch=request.form.to_dict(), 
                             action='create')
    except Exception as e:
        logger.error(f"支社作成エラー: {e}")
        flash('支社作成中にエラーが発生しました', 'error')
        return render_template('branches/form.html', 
                             branch=request.form.to_dict(), 
                             action='create')


@branch_bp.route('/<int:branch_id>')
def show(branch_id):
    """支社詳細画面"""
    try:
        branch = BranchService.get_branch_by_id(branch_id)
        if not branch:
            flash('指定された支社が見つかりません', 'error')
            return redirect(url_for('branches.index'))
        
        return render_template('branches/show.html', branch=branch)
    except Exception as e:
        logger.error(f"支社詳細取得エラー: {e}")
        flash('支社詳細の取得中にエラーが発生しました', 'error')
        return redirect(url_for('branches.index'))


@branch_bp.route('/<int:branch_id>/edit')
def edit(branch_id):
    """支社編集フォーム"""
    try:
        branch = BranchService.get_branch_by_id(branch_id)
        if not branch:
            flash('指定された支社が見つかりません', 'error')
            return redirect(url_for('branches.index'))
        
        return render_template('branches/form.html', branch=branch, action='update')
    except Exception as e:
        logger.error(f"支社編集フォーム取得エラー: {e}")
        flash('支社編集フォームの取得中にエラーが発生しました', 'error')
        return redirect(url_for('branches.index'))


@branch_bp.route('/<int:branch_id>/update', methods=['POST'])
def update(branch_id):
    """支社更新処理"""
    try:
        branch = BranchService.get_branch_by_id(branch_id)
        if not branch:
            flash('指定された支社が見つかりません', 'error')
            return redirect(url_for('branches.index'))
        
        branch_data = {
            'branch_code': request.form.get('branch_code', '').strip(),
            'branch_name': request.form.get('branch_name', '').strip(),
            'is_active': request.form.get('is_active') == 'on'
        }
        
        # データ検証
        validation_errors = BranchService.validate_branch_data(branch_data, exclude_id=branch_id)
        if validation_errors:
            for error in validation_errors:
                flash(error.message, 'error')
            return render_template('branches/form.html', 
                                 branch=branch, 
                                 action='update')
        
        # 支社更新
        updated_branch = BranchService.update_branch(branch_id, branch_data)
        flash(f'支社「{updated_branch.branch_name}」を更新しました', 'success')
        return redirect(url_for('branches.index'))
        
    except ValidationError as e:
        flash(e.message, 'error')
        branch = BranchService.get_branch_by_id(branch_id)
        return render_template('branches/form.html', 
                             branch=branch, 
                             action='update')
    except Exception as e:
        logger.error(f"支社更新エラー: {e}")
        flash('支社更新中にエラーが発生しました', 'error')
        return redirect(url_for('branches.index'))


@branch_bp.route('/<int:branch_id>/delete', methods=['POST'])
def delete(branch_id):
    """支社削除処理"""
    try:
        branch = BranchService.get_branch_by_id(branch_id)
        if not branch:
            flash('指定された支社が見つかりません', 'error')
            return redirect(url_for('branches.index'))
        
        branch_name = branch.branch_name
        BranchService.delete_branch(branch_id)
        flash(f'支社「{branch_name}」を削除しました', 'success')
        
    except ValidationError as e:
        flash(e.message, 'error')
    except Exception as e:
        logger.error(f"支社削除エラー: {e}")
        flash('支社削除中にエラーが発生しました', 'error')
    
    return redirect(url_for('branches.index'))


@branch_bp.route('/<int:branch_id>/toggle', methods=['POST'])
def toggle_status(branch_id):
    """支社有効/無効切り替え"""
    try:
        branch = BranchService.toggle_branch_status(branch_id)
        status_text = '有効' if branch.is_active else '無効'
        flash(f'支社「{branch.branch_name}」を{status_text}に変更しました', 'success')
        
    except ValidationError as e:
        flash(e.message, 'error')
    except Exception as e:
        logger.error(f"支社状態変更エラー: {e}")
        flash('支社状態変更中にエラーが発生しました', 'error')
    
    return redirect(url_for('branches.index'))


# API エンドポイント

@branch_bp.route('/api/branches')
def api_branches():
    """支社一覧API（JSON）"""
    try:
        include_inactive = request.args.get('include_inactive', 'true').lower() == 'true'
        branches = BranchService.get_all_branches(include_inactive=include_inactive)
        
        return jsonify({
            'success': True,
            'data': [branch.to_dict() for branch in branches]
        })
    except Exception as e:
        logger.error(f"支社一覧API エラー: {e}")
        return jsonify({
            'success': False,
            'error': '支社一覧の取得中にエラーが発生しました'
        }), 500


@branch_bp.route('/api/branches/search')
def api_search_branches():
    """支社検索API（JSON）"""
    try:
        search_params = {
            'branch_code': request.args.get('branch_code'),
            'branch_name': request.args.get('branch_name'),
            'is_active': request.args.get('is_active')
        }
        
        # is_active パラメータの変換
        if search_params['is_active'] is not None:
            search_params['is_active'] = search_params['is_active'].lower() == 'true'
        
        branches = BranchService.search_branches(search_params)
        
        return jsonify({
            'success': True,
            'data': [branch.to_dict() for branch in branches]
        })
    except Exception as e:
        logger.error(f"支社検索API エラー: {e}")
        return jsonify({
            'success': False,
            'error': '支社検索中にエラーが発生しました'
        }), 500


@branch_bp.route('/api/branches/select')
def api_branches_for_select():
    """選択リスト用支社API（JSON）"""
    try:
        branches = BranchService.get_branches_for_select()
        
        return jsonify({
            'success': True,
            'data': branches
        })
    except Exception as e:
        logger.error(f"支社選択リストAPI エラー: {e}")
        return jsonify({
            'success': False,
            'error': '支社選択リストの取得中にエラーが発生しました'
        }), 500


@branch_bp.route('/api/branches/statistics')
def api_branch_statistics():
    """支社統計情報API（JSON）"""
    try:
        stats = BranchService.get_branch_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        logger.error(f"支社統計API エラー: {e}")
        return jsonify({
            'success': False,
            'error': '支社統計情報の取得中にエラーが発生しました'
        }), 500