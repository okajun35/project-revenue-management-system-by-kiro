from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Project, Branch, FiscalYear, ValidationError
from app.controllers.helpers import build_branch_choices, build_fiscal_year_choices
from app.forms import ProjectForm
from app import db

project_bp = Blueprint('projects', __name__, url_prefix='/projects')

@project_bp.route('/')
def index():
	"""プロジェクト一覧画面"""
	branches = Branch.get_active_branches()
	fiscal_years = FiscalYear.get_active_years()
	return render_template('projects/index.html', branches=branches, fiscal_years=fiscal_years)

@project_bp.route('/new')
def new():
	"""新規プロジェクト作成フォーム画面"""
	form = ProjectForm()
	form.branch_id.choices = build_branch_choices(include_placeholder=True)
	form.fiscal_year.choices = build_fiscal_year_choices(include_placeholder=True)
	return render_template('projects/form.html', form=form, title='新規プロジェクト作成')

@project_bp.route('/', methods=['POST'])
def create():
	"""プロジェクト作成処理"""
	form = ProjectForm()
	form.branch_id.choices = build_branch_choices(include_placeholder=True)
	form.fiscal_year.choices = build_fiscal_year_choices(include_placeholder=True)
	if form.validate_on_submit():
		try:
			project = Project.create_with_validation(
				project_code=form.project_code.data,
				project_name=form.project_name.data,
				branch_id=form.branch_id.data,
				fiscal_year=form.fiscal_year.data,
				order_probability=form.order_probability.data,
				revenue=form.revenue.data,
				expenses=form.expenses.data,
			)
			flash(f'✅ プロジェクト「{project.project_name}」（{project.project_code}）を正常に作成しました。', 'success')
			return redirect(url_for('projects.index'))
		except ValidationError as e:
			if hasattr(e, 'field') and e.field:
				if hasattr(form, e.field):
					getattr(form, e.field).errors.append(e.message)
				else:
					flash(e.message, 'error')
			else:
				flash(e.message, 'error')
		except Exception:
			flash('プロジェクトの作成中にエラーが発生しました。', 'error')
			db.session.rollback()
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
	form.branch_id.choices = build_branch_choices()
	form.fiscal_year.choices = build_fiscal_year_choices()
	return render_template('projects/form.html', form=form, project=project, title='プロジェクト編集')

@project_bp.route('/<int:project_id>/update', methods=['POST'])
def update(project_id):
	"""プロジェクト更新処理"""
	project = Project.query.get_or_404(project_id)
	form = ProjectForm(project_id=project.id)
	form.branch_id.choices = build_branch_choices()
	form.fiscal_year.choices = build_fiscal_year_choices()
	if form.validate_on_submit():
		try:
			project.update_with_validation(
				project_code=form.project_code.data,
				project_name=form.project_name.data,
				branch_id=form.branch_id.data,
				fiscal_year=form.fiscal_year.data,
				order_probability=form.order_probability.data,
				revenue=form.revenue.data,
				expenses=form.expenses.data,
			)
			flash(f'✅ プロジェクト「{project.project_name}」を正常に更新しました。', 'success')
			return redirect(url_for('projects.index'))
		except ValidationError as e:
			if hasattr(e, 'field') and e.field:
				if hasattr(form, e.field):
					getattr(form, e.field).errors.append(e.message)
				else:
					flash(e.message, 'error')
			else:
				flash(e.message, 'error')
		except Exception:
			flash('プロジェクトの更新中にエラーが発生しました。', 'error')
			db.session.rollback()
	return render_template('projects/form.html', form=form, project=project, title='プロジェクト編集')

@project_bp.route('/<int:project_id>/delete', methods=['POST'])
def delete(project_id):
	"""プロジェクト削除処理"""
	project = Project.query.get_or_404(project_id)
	try:
		result = project.delete_with_validation()
		if result['success']:
			flash(f'🗑️ プロジェクト「{result["project_name"]}」（{result["project_code"]}）を正常に削除しました。', 'success')
		else:
			flash('プロジェクトの削除に失敗しました。', 'error')
	except ValidationError as e:
		flash(f'削除エラー: {e.message}', 'error')
	except Exception:
		flash('プロジェクトの削除中に予期しないエラーが発生しました。システム管理者にお問い合わせください。', 'error')
	return redirect(url_for('projects.index'))

@project_bp.route('/api/list')
def api_list():
	"""プロジェクト一覧API（DataTables用）"""
	try:
		draw = request.args.get('draw', type=int, default=1)
		start = request.args.get('start', type=int, default=0)
		length = request.args.get('length', type=int, default=25)
		search_value = request.args.get('search[value]', default='')
		project_code_filter = request.args.get('project_code', default='')
		project_name_filter = request.args.get('project_name', default='')
		branch_id_filter = request.args.get('branch_id', type=int)
		fiscal_year_filter = request.args.get('fiscal_year', type=int)
		order_probability_min = request.args.get('order_probability_min', type=float)
		order_probability_max = request.args.get('order_probability_max', type=float)
		branch_filter = request.args.get('branch_filter', type=int)
		fiscal_year_filter_list = request.args.get('fiscal_year_filter', type=int)
		order_column = request.args.get('order[0][column]', type=int, default=7)
		order_dir = request.args.get('order[0][dir]', default='desc')
		columns = [
			'project_code', 'project_name', 'branch_name', 'fiscal_year',
			'order_probability', 'revenue', 'expenses', 'gross_profit',
			'created_at', 'actions',
		]
		query = Project.query.join(Branch)
		if search_value:
			query = query.filter(
				db.or_(
					Project.project_code.contains(search_value),
					Project.project_name.contains(search_value),
					Project.fiscal_year.like(f'%{search_value}%'),
					Branch.branch_name.contains(search_value),
				)
			)
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
		if branch_filter:
			query = query.filter(Project.branch_id == branch_filter)
		if fiscal_year_filter_list:
			query = query.filter(Project.fiscal_year == fiscal_year_filter_list)
		total_records = Project.query.count()
		filtered_records = query.count()
		if order_column < len(columns) and columns[order_column] != 'actions':
			column_name = columns[order_column]
			if column_name == 'gross_profit':
				query = query.order_by((Project.revenue - Project.expenses).desc() if order_dir == 'desc' else (Project.revenue - Project.expenses).asc())
			elif column_name == 'branch_name':
				query = query.order_by(Branch.branch_name.desc() if order_dir == 'desc' else Branch.branch_name.asc())
			else:
				column = getattr(Project, column_name)
				query = query.order_by(column.desc() if order_dir == 'desc' else column.asc())
		else:
			query = query.order_by(Project.created_at.desc())
		projects = query.offset(start).limit(length).all()
		data = []
		for project in projects:
			if project.order_probability == 100:
				badge_class = 'success'
			elif project.order_probability == 50:
				badge_class = 'warning'
			else:
				badge_class = 'danger'
			gross_profit_class = 'text-success' if project.gross_profit >= 0 else 'text-danger'
			# 小数を含まない整数パーセント表示に統一（例: 50% / 100%）
			order_percent_text = f"{int(project.order_probability)}%"
			data.append([
				project.project_code,
				project.project_name,
				project.branch.branch_name if project.branch else '未設定',
				project.fiscal_year,
				f'<span class="badge badge-{badge_class}">{project.order_probability_symbol} {order_percent_text}</span>',
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
		return jsonify({'draw': draw, 'recordsTotal': total_records, 'recordsFiltered': filtered_records, 'data': data})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@project_bp.route('/api/calculate-gross-profit')
def calculate_gross_profit():
	"""粗利計算API（Ajax用）"""
	try:
		revenue = float(request.args.get('revenue', 0))
		expenses = float(request.args.get('expenses', 0))
		gross_profit = revenue - expenses
		return jsonify({'success': True, 'gross_profit': gross_profit, 'formatted_gross_profit': f'{gross_profit:,.2f}'})
	except (ValueError, TypeError):
		return jsonify({'success': False, 'error': '無効な数値が入力されました'}), 400

@project_bp.route('/search')
def search():
	"""プロジェクト検索画面"""
	branches = Branch.get_active_branches()
	available_years = db.session.query(Project.fiscal_year).distinct().order_by(Project.fiscal_year.desc()).all()
	available_years = [year[0] for year in available_years] if available_years else []
	return render_template('projects/search.html', branches=branches, available_years=available_years)

@project_bp.route('/api/branches/search')
def api_branches_search():
	"""支社検索API（モーダル用）"""
	try:
		search_term = request.args.get('search', default='')
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
					'display_name': f'{branch.branch_code} - {branch.branch_name}',
				}
				for branch in branches
			],
		})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)}), 500

__all__ = ["project_bp"]
