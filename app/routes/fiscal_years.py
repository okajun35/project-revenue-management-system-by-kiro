from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import FiscalYear, ValidationError
from app import db

fiscal_year_bp = Blueprint('fiscal_years', __name__, url_prefix='/fiscal-years')

@fiscal_year_bp.route('/')
def index():
	return render_template('fiscal_years/index.html')

@fiscal_year_bp.route('/new')
def new():
	return render_template('fiscal_years/form.html', title='新規年度作成')

@fiscal_year_bp.route('/', methods=['POST'])
def create():
	try:
		year = int(request.form.get('year'))
		year_name = request.form.get('year_name', f"{year}年度")
		fiscal_year = FiscalYear.create_with_validation(year=year, year_name=year_name)
		flash(f'✅ 年度「{fiscal_year.year_name}」を正常に作成しました。', 'success')
		return redirect(url_for('fiscal_years.index'))
	except ValidationError as e:
		flash(e.message, 'error')
	except ValueError:
		flash('年度は数値で入力してください。', 'error')
	except Exception:
		flash('年度の作成中にエラーが発生しました。', 'error')
		db.session.rollback()
	return render_template('fiscal_years/form.html', title='新規年度作成')

@fiscal_year_bp.route('/<int:fiscal_year_id>')
def show(fiscal_year_id):
	fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
	return render_template('fiscal_years/show.html', fiscal_year=fiscal_year)

@fiscal_year_bp.route('/<int:fiscal_year_id>/edit')
def edit(fiscal_year_id):
	fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
	return render_template('fiscal_years/form.html', fiscal_year=fiscal_year, title='年度編集')

@fiscal_year_bp.route('/<int:fiscal_year_id>/update', methods=['POST'])
def update(fiscal_year_id):
	fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
	try:
		year = int(request.form.get('year'))
		year_name = request.form.get('year_name')
		fiscal_year.year = year
		fiscal_year.year_name = year_name
		validation_errors = fiscal_year.validate_data()
		if validation_errors:
			raise validation_errors[0]
		fiscal_year.validate_unique_year(exclude_id=fiscal_year.id)
		fiscal_year.validate_unique_year_name(exclude_id=fiscal_year.id)
		db.session.commit()
		flash(f'✅ 年度「{fiscal_year.year_name}」を正常に更新しました。', 'success')
		return redirect(url_for('fiscal_years.index'))
	except ValidationError as e:
		flash(e.message, 'error')
	except ValueError:
		flash('年度は数値で入力してください。', 'error')
	except Exception:
		flash('年度の更新中にエラーが発生しました。', 'error')
		db.session.rollback()
	return render_template('fiscal_years/form.html', fiscal_year=fiscal_year, title='年度編集')

@fiscal_year_bp.route('/<int:fiscal_year_id>/delete', methods=['POST'])
def delete(fiscal_year_id):
	fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
	try:
		if fiscal_year.projects:
			flash('この年度には関連するプロジェクトが存在するため削除できません。', 'error')
			return redirect(url_for('fiscal_years.index'))
		year_name = fiscal_year.year_name
		db.session.delete(fiscal_year)
		db.session.commit()
		flash(f'🗑️ 年度「{year_name}」を正常に削除しました。', 'success')
	except Exception:
		db.session.rollback()
		flash('年度の削除中にエラーが発生しました。', 'error')
	return redirect(url_for('fiscal_years.index'))

@fiscal_year_bp.route('/<int:fiscal_year_id>/toggle', methods=['POST'])
def toggle_active(fiscal_year_id):
	fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
	try:
		fiscal_year.is_active = not fiscal_year.is_active
		db.session.commit()
		status = "有効" if fiscal_year.is_active else "無効"
		flash(f'✅ 年度「{fiscal_year.year_name}」を{status}に変更しました。', 'success')
	except Exception:
		db.session.rollback()
		flash('年度の状態変更中にエラーが発生しました。', 'error')
	return redirect(url_for('fiscal_years.index'))

@fiscal_year_bp.route('/api/list')
def api_list():
	try:
		draw = request.args.get('draw', type=int, default=1)
		start = request.args.get('start', type=int, default=0)
		length = request.args.get('length', type=int, default=25)
		search_value = request.args.get('search[value]', default='')
		order_column = request.args.get('order[0][column]', type=int, default=1)
		order_dir = request.args.get('order[0][dir]', default='desc')
		columns = ['year', 'year_name', 'is_active', 'project_count', 'created_at', 'actions']
		query = FiscalYear.query
		if search_value:
			query = query.filter(
				db.or_(FiscalYear.year.like(f'%{search_value}%'), FiscalYear.year_name.contains(search_value))
			)
		total_records = FiscalYear.query.count()
		filtered_records = query.count()
		if order_column < len(columns) and columns[order_column] != 'actions':
			column_name = columns[order_column]
			if column_name == 'project_count':
				from app.models import Project
				project_count_subquery = db.session.query(
					Project.fiscal_year, db.func.count(Project.id).label('count')
				).group_by(Project.fiscal_year).subquery()
				query = query.outerjoin(project_count_subquery, FiscalYear.year == project_count_subquery.c.fiscal_year)
				order_col = db.func.coalesce(project_count_subquery.c.count, 0)
				query = query.order_by(order_col.desc() if order_dir == 'desc' else order_col.asc())
			else:
				column = getattr(FiscalYear, column_name)
				query = query.order_by(column.desc() if order_dir == 'desc' else column.asc())
		else:
			query = query.order_by(FiscalYear.year.desc())
		fiscal_years = query.offset(start).limit(length).all()
		data = []
		for fiscal_year in fiscal_years:
			project_count = len(fiscal_year.projects) if fiscal_year.projects else 0
			status_badge = '<span class="badge badge-success">有効</span>' if fiscal_year.is_active else '<span class="badge badge-secondary">無効</span>'
			data.append([
				fiscal_year.year,
				fiscal_year.year_name,
				status_badge,
				project_count,
				fiscal_year.created_at.strftime('%Y-%m-%d') if fiscal_year.created_at else '',
				f'''
				<div class="btn-group" role="group">
					<a href="{url_for('fiscal_years.show', fiscal_year_id=fiscal_year.id)}" 
					   class="btn btn-info btn-sm" title="詳細">
						<i class="fas fa-eye"></i>
					</a>
					<a href="{url_for('fiscal_years.edit', fiscal_year_id=fiscal_year.id)}" 
					   class="btn btn-warning btn-sm" title="編集">
						<i class="fas fa-edit"></i>
					</a>
					<button type="button" class="btn btn-{'secondary' if fiscal_year.is_active else 'success'} btn-sm" 
							onclick="toggleActive({fiscal_year.id}, '{fiscal_year.year_name}', {'true' if fiscal_year.is_active else 'false'})" 
							title="{'無効化' if fiscal_year.is_active else '有効化'}">
						<i class="fas fa-{'toggle-off' if fiscal_year.is_active else 'toggle-on'}"></i>
					</button>
					<button type="button" class="btn btn-danger btn-sm" 
							onclick="confirmDelete({fiscal_year.id}, '{fiscal_year.year_name}', {project_count})" 
							title="削除">
						<i class="fas fa-trash"></i>
					</button>
				</div>
				'''
			])
		return jsonify({'draw': draw, 'recordsTotal': total_records, 'recordsFiltered': filtered_records, 'data': data})
	except Exception as e:
		return jsonify({'error': str(e)}), 500

__all__ = ["fiscal_year_bp"]
