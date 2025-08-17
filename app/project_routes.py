from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Project, Branch, ValidationError
from app.forms import ProjectForm
from app import db

project_bp = Blueprint('projects', __name__, url_prefix='/projects')

@project_bp.route('/')
def index():
    """プロジェクト一覧画面"""
    # 有効な支社の選択肢を取得
    branches = Branch.get_active_branches()
    
    # 有効な年度の選択肢を取得
    from app.models import FiscalYear
    fiscal_years = FiscalYear.get_active_years()
    
    return render_template('projects/index.html', branches=branches, fiscal_years=fiscal_years)

@project_bp.route('/new')
def new():
    """新規プロジェクト作成フォーム画面"""
    form = ProjectForm()
    # 有効な支社の選択肢を設定
    form.branch_id.choices = [(0, '支社を選択してください')] + [(branch.id, branch.branch_name) for branch in Branch.get_active_branches()]
    
    # 有効な年度の選択肢を設定
    from app.models import FiscalYear
    form.fiscal_year.choices = [(0, '年度を選択してください')] + [(year.year, year.year_name) for year in FiscalYear.get_active_years()]
    
    return render_template('projects/form.html', form=form, title='新規プロジェクト作成')

@project_bp.route('/', methods=['POST'])
def create():
    """プロジェクト作成処理"""
    form = ProjectForm()
    # 有効な支社の選択肢を設定
    form.branch_id.choices = [(0, '支社を選択してください')] + [(branch.id, branch.branch_name) for branch in Branch.get_active_branches()]
    
    # 有効な年度の選択肢を設定
    from app.models import FiscalYear
    form.fiscal_year.choices = [(0, '年度を選択してください')] + [(year.year, year.year_name) for year in FiscalYear.get_active_years()]
    
    if form.validate_on_submit():
        try:
            # フォームデータからプロジェクトを作成
            project = Project.create_with_validation(
                project_code=form.project_code.data,
                project_name=form.project_name.data,
                branch_id=form.branch_id.data,
                fiscal_year=form.fiscal_year.data,
                order_probability=form.order_probability.data,
                revenue=form.revenue.data,
                expenses=form.expenses.data
            )
            
            flash(f'✅ プロジェクト「{project.project_name}」（{project.project_code}）を正常に作成しました。', 'success')
            return redirect(url_for('projects.index'))
            
        except ValidationError as e:
            if hasattr(e, 'field') and e.field:
                # 特定のフィールドエラーの場合
                if hasattr(form, e.field):
                    getattr(form, e.field).errors.append(e.message)
                else:
                    flash(e.message, 'error')
            else:
                # 一般的なエラーの場合
                flash(e.message, 'error')
        except Exception as e:
            flash('プロジェクトの作成中にエラーが発生しました。', 'error')
            db.session.rollback()
    
    # バリデーションエラーがある場合、フォームを再表示
    return render_template('projects/form.html', form=form, title='新規プロジェクト作成')

@project_bp.route('/<int:project_id>')
def show(project_id):
    """プロジェクト詳細画面"""
    project = Project.query.get_or_404(project_id)
    return render_template('projects/show.html', project=project)

@project_bp.route('/<int:project_id>/edit')
def edit(project_id):
    """プロジェクト編集フォーム画面"""
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(project_id=project.id, obj=project)
    # 有効な支社の選択肢を設定
    form.branch_id.choices = [(branch.id, branch.branch_name) for branch in Branch.get_active_branches()]
    
    # 有効な年度の選択肢を設定
    from app.models import FiscalYear
    form.fiscal_year.choices = [(year.year, year.year_name) for year in FiscalYear.get_active_years()]
    
    return render_template('projects/form.html', form=form, project=project, title='プロジェクト編集')

@project_bp.route('/<int:project_id>/update', methods=['POST'])
def update(project_id):
    """プロジェクト更新処理"""
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(project_id=project.id)
    # 有効な支社の選択肢を設定
    form.branch_id.choices = [(branch.id, branch.branch_name) for branch in Branch.get_active_branches()]
    
    # 有効な年度の選択肢を設定
    from app.models import FiscalYear
    form.fiscal_year.choices = [(year.year, year.year_name) for year in FiscalYear.get_active_years()]
    
    if form.validate_on_submit():
        try:
            # プロジェクトを更新
            project.update_with_validation(
                project_code=form.project_code.data,
                project_name=form.project_name.data,
                branch_id=form.branch_id.data,
                fiscal_year=form.fiscal_year.data,
                order_probability=form.order_probability.data,
                revenue=form.revenue.data,
                expenses=form.expenses.data
            )
            
            flash(f'✅ プロジェクト「{project.project_name}」を正常に更新しました。', 'success')
            return redirect(url_for('projects.index'))
            
        except ValidationError as e:
            if hasattr(e, 'field') and e.field:
                # 特定のフィールドエラーの場合
                if hasattr(form, e.field):
                    getattr(form, e.field).errors.append(e.message)
                else:
                    flash(e.message, 'error')
            else:
                # 一般的なエラーの場合
                flash(e.message, 'error')
        except Exception as e:
            flash('プロジェクトの更新中にエラーが発生しました。', 'error')
            db.session.rollback()
    
    # バリデーションエラーがある場合、フォームを再表示
    return render_template('projects/form.html', form=form, project=project, title='プロジェクト編集')

@project_bp.route('/<int:project_id>/delete', methods=['POST'])
def delete(project_id):
    """プロジェクト削除処理"""
    project = Project.query.get_or_404(project_id)
    
    try:
        # 削除実行（検証付き）
        result = project.delete_with_validation()
        
        if result['success']:
            flash(f'🗑️ プロジェクト「{result["project_name"]}」（{result["project_code"]}）を正常に削除しました。', 'success')
        else:
            flash('プロジェクトの削除に失敗しました。', 'error')
            
    except ValidationError as e:
        flash(f'削除エラー: {e.message}', 'error')
    except Exception as e:
        flash('プロジェクトの削除中に予期しないエラーが発生しました。システム管理者にお問い合わせください。', 'error')
    
    return redirect(url_for('projects.index'))

@project_bp.route('/api/list')
def api_list():
    """プロジェクト一覧API（DataTables用）"""
    try:
        # DataTablesのパラメータを取得
        draw = request.args.get('draw', type=int, default=1)
        start = request.args.get('start', type=int, default=0)
        length = request.args.get('length', type=int, default=25)
        search_value = request.args.get('search[value]', default='')
        
        # 高度な検索パラメータを取得
        project_code_filter = request.args.get('project_code', default='')
        project_name_filter = request.args.get('project_name', default='')
        branch_id_filter = request.args.get('branch_id', type=int)
        fiscal_year_filter = request.args.get('fiscal_year', type=int)
        order_probability_min = request.args.get('order_probability_min', type=float)
        order_probability_max = request.args.get('order_probability_max', type=float)
        
        # 一覧画面のフィルターパラメータを取得
        branch_filter = request.args.get('branch_filter', type=int)
        fiscal_year_filter_list = request.args.get('fiscal_year_filter', type=int)
        
        # ソート情報を取得
        order_column = request.args.get('order[0][column]', type=int, default=7)  # デフォルトは作成日
        order_dir = request.args.get('order[0][dir]', default='desc')
        
        # 列のマッピング
        columns = [
            'project_code',      # 0
            'project_name',      # 1
            'branch_name',       # 2
            'fiscal_year',       # 3
            'order_probability', # 4
            'revenue',           # 5
            'expenses',          # 6
            'gross_profit',      # 7 (計算列)
            'created_at',        # 8
            'actions'            # 9 (操作列)
        ]
        
        # ベースクエリ（支社情報を含む）
        query = Project.query.join(Branch)
        
        # 基本検索フィルタを適用
        if search_value:
            query = query.filter(
                db.or_(
                    Project.project_code.contains(search_value),
                    Project.project_name.contains(search_value),
                    Project.fiscal_year.like(f'%{search_value}%'),
                    Branch.branch_name.contains(search_value)
                )
            )
        
        # 高度な検索フィルタを適用（AND条件）
        if project_code_filter:
            query = query.filter(Project.project_code.contains(project_code_filter))
        
        if project_name_filter:
            query = query.filter(Project.project_name.contains(project_name_filter))
        
        if branch_id_filter:
            query = query.filter(Project.branch_id == branch_id_filter)
        
        if fiscal_year_filter:
            query = query.filter(Project.fiscal_year == fiscal_year_filter)
        
        if order_probability_min is not None:
            query = query.filter(Project.order_probability >= order_probability_min)
        
        if order_probability_max is not None:
            query = query.filter(Project.order_probability <= order_probability_max)
        
        # 一覧画面のフィルタを適用
        if branch_filter:
            query = query.filter(Project.branch_id == branch_filter)
        
        if fiscal_year_filter_list:
            query = query.filter(Project.fiscal_year == fiscal_year_filter_list)
        
        # 総レコード数を取得
        total_records = Project.query.count()
        filtered_records = query.count()
        
        # ソートを適用
        if order_column < len(columns) and columns[order_column] != 'actions':
            column_name = columns[order_column]
            if column_name == 'gross_profit':
                # 粗利は計算列なので、revenue - expenses でソート
                if order_dir == 'desc':
                    query = query.order_by((Project.revenue - Project.expenses).desc())
                else:
                    query = query.order_by((Project.revenue - Project.expenses).asc())
            elif column_name == 'branch_name':
                # 支社名でソート
                if order_dir == 'desc':
                    query = query.order_by(Branch.branch_name.desc())
                else:
                    query = query.order_by(Branch.branch_name.asc())
            else:
                column = getattr(Project, column_name)
                if order_dir == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        else:
            # デフォルトソート（作成日降順）
            query = query.order_by(Project.created_at.desc())
        
        # ページネーションを適用
        projects = query.offset(start).limit(length).all()
        
        # データを整形
        data = []
        for project in projects:
            # 受注角度のバッジクラスを決定
            if project.order_probability == 100:
                badge_class = 'success'
            elif project.order_probability == 50:
                badge_class = 'warning'
            else:
                badge_class = 'danger'
            
            # 粗利の色を決定
            gross_profit_class = 'text-success' if project.gross_profit >= 0 else 'text-danger'
            
            data.append([
                project.project_code,
                project.project_name,
                project.branch.branch_name if project.branch else '未設定',
                project.fiscal_year,
                f'<span class="badge badge-{badge_class}">{project.order_probability_symbol} {project.order_probability}%</span>',
                f'<span class="text-right">{project.revenue:,.2f}</span>',
                f'<span class="text-right">{project.expenses:,.2f}</span>',
                f'<span class="text-right {gross_profit_class}">{project.gross_profit:,.2f}</span>',
                project.created_at.strftime('%Y-%m-%d') if project.created_at else '',
                f'''
                <div class="btn-group" role="group">
                    <a href="{url_for('projects.show', project_id=project.id)}" 
                       class="btn btn-info btn-sm" title="詳細">
                        <i class="fas fa-eye"></i>
                    </a>
                    <a href="{url_for('projects.edit', project_id=project.id)}" 
                       class="btn btn-warning btn-sm" title="編集">
                        <i class="fas fa-edit"></i>
                    </a>
                    <button type="button" class="btn btn-danger btn-sm" 
                            onclick="confirmDelete({project.id}, '{project.project_name}')" 
                            title="削除">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
                '''
            ])
        
        return jsonify({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': filtered_records,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@project_bp.route('/api/calculate-gross-profit')
def calculate_gross_profit():
    """粗利計算API（Ajax用）"""
    try:
        revenue = float(request.args.get('revenue', 0))
        expenses = float(request.args.get('expenses', 0))
        gross_profit = revenue - expenses
        
        return jsonify({
            'success': True,
            'gross_profit': gross_profit,
            'formatted_gross_profit': f'{gross_profit:,.2f}'
        })
    except (ValueError, TypeError):
        return jsonify({
            'success': False,
            'error': '無効な数値が入力されました'
        }), 400

@project_bp.route('/search')
def search():
    """プロジェクト検索画面"""
    # 有効な支社の選択肢を取得
    branches = Branch.get_active_branches()
    
    # 利用可能な年度一覧を取得
    available_years = db.session.query(Project.fiscal_year).distinct().order_by(Project.fiscal_year.desc()).all()
    available_years = [year[0] for year in available_years] if available_years else []
    
    return render_template('projects/search.html', branches=branches, available_years=available_years)

@project_bp.route('/api/branches/search')
def api_branches_search():
    """支社検索API（モーダル用）"""
    try:
        search_term = request.args.get('search', default='')
        
        # 支社名での部分一致検索
        query = Branch.query.filter(Branch.is_active == True)
        if search_term:
            query = query.filter(Branch.branch_name.contains(search_term))
        
        branches = query.order_by(Branch.branch_name).all()
        
        return jsonify({
            'success': True,
            'branches': [
                {
                    'id': branch.id,
                    'branch_code': branch.branch_code,
                    'branch_name': branch.branch_name,
                    'display_name': f'{branch.branch_code} - {branch.branch_name}'
                }
                for branch in branches
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500