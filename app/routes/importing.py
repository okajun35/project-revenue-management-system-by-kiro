import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from app.services.import_service import ImportService
from app.forms import ImportForm

import_bp = Blueprint('import', __name__, url_prefix='/import')

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@import_bp.post('/suggest-mapping')
def suggest_mapping():
	payload = request.get_json(silent=True) or {}
	columns = payload.get('columns') or []
	keywords = {
		'project_code': ['プロジェクト', 'コード', 'project', 'code', 'id'],
		'project_name': ['プロジェクト', '名', 'project', 'name', 'title'],
		'branch_name': ['支社', '営業所', 'branch', 'office', '名'],
		'fiscal_year': ['年度', '年', 'year', 'fiscal'],
		'order_probability': ['受注', '角度', '確率', 'probability', 'order'],
		'revenue': ['売上', '契約', '金額', 'revenue', 'sales', 'amount'],
		'expenses': ['経費', '費用', 'expense', 'cost'],
	}
	def best_match(field: str):
		best = None
		best_score = 0
		for col in columns:
			col_l = str(col).lower()
			score = sum(1 for kw in keywords.get(field, []) if kw.lower() in col_l)
			if score > best_score:
				best_score = score
				best = col
		return best
	mapping = {field: best_match(field) for field in keywords.keys()}
	return jsonify(success=True, mapping=mapping)


@import_bp.route('/')
def index():
	form = ImportForm()
	return render_template('import/index.html', form=form)


@import_bp.route('/upload', methods=['POST'])
def upload_file():
	form = ImportForm()
	if not form.validate_on_submit():
		flash('入力内容に問題があります', 'error')
		return render_template('import/index.html', form=form)
	if 'file' not in request.files:
		flash('ファイルが選択されていません', 'error')
		return render_template('import/index.html', form=form)
	file = request.files['file']
	if file.filename == '':
		flash('ファイルが選択されていません', 'error')
		return render_template('import/index.html', form=form)
	if not allowed_file(file.filename):
		flash('サポートされていないファイル形式です', 'error')
		return render_template('import/index.html', form=form)
	try:
		filename = secure_filename(file.filename)
		filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
		file.save(filepath)
		import_service = ImportService()
		result = import_service.validate_file(filepath, form.file_type.data)
		if result['success']:
			from flask import session
			session['import_file'] = filepath
			session['import_type'] = form.file_type.data
			session['import_columns'] = result['columns']
			session['import_sample_data'] = result['sample_data']
			session['import_row_count'] = result['row_count']
			if form.file_type.data == 'excel' and 'excel_info' in result:
				session['excel_info'] = result['excel_info']
				session['selected_sheet'] = result.get('selected_sheet')
			flash(f'ファイルの読み込みが完了しました。{result["row_count"]}行のデータが見つかりました。', 'success')
			return redirect(url_for('import.mapping'))
		else:
			if os.path.exists(filepath):
				os.remove(filepath)
			flash(f'ファイルの検証に失敗しました: {result["error"]}', 'error')
			return render_template('import/index.html', form=form)
	except Exception as e:
		if 'filepath' in locals() and os.path.exists(filepath):
			os.remove(filepath)
		flash(f'ファイル処理中にエラーが発生しました: {str(e)}', 'error')
		return render_template('import/index.html', form=form)


@import_bp.route('/select_sheet')
def select_sheet():
	from flask import session
	if 'import_file' not in session or session.get('import_type') != 'excel':
		flash('Excelファイルが見つかりません', 'error')
		return redirect(url_for('import.index'))
	try:
		import_service = ImportService()
		excel_info = import_service.get_excel_sheets(session['import_file'])
		if not excel_info['success']:
			flash(f'Excelファイルの読み込みに失敗しました: {excel_info["error"]}', 'error')
			return redirect(url_for('import.index'))
		return render_template('import/select_sheet.html', filename=os.path.basename(session['import_file']), excel_info=excel_info)
	except Exception as e:
		flash(f'シート選択画面の表示中にエラーが発生しました: {str(e)}', 'error')
		return redirect(url_for('import.index'))


@import_bp.route('/set_sheet', methods=['POST'])
def set_sheet():
	from flask import session
	if 'import_file' not in session or session.get('import_type') != 'excel':
		flash('Excelファイルが見つかりません', 'error')
		return redirect(url_for('import.index'))
	sheet_name = request.form.get('sheet_name')
	if not sheet_name:
		flash('シートを選択してください', 'error')
		return redirect(url_for('import.select_sheet'))
	try:
		import_service = ImportService()
		sheet_result = import_service.validate_excel_sheet(session['import_file'], sheet_name)
		if not sheet_result['success']:
			flash(f'シートの検証に失敗しました: {sheet_result["error"]}', 'error')
			return redirect(url_for('import.select_sheet'))
		session['selected_sheet'] = sheet_name
		session['import_columns'] = sheet_result['columns']
		session['import_sample_data'] = sheet_result['sample_data']
		session['import_row_count'] = sheet_result['row_count']
		flash(f'シート「{sheet_name}」を選択しました。{sheet_result["row_count"]}行のデータが見つかりました。', 'success')
		return redirect(url_for('import.mapping'))
	except Exception as e:
		flash(f'シート設定中にエラーが発生しました: {str(e)}', 'error')
		return redirect(url_for('import.select_sheet'))


@import_bp.route('/mapping')
def mapping():
	from flask import session
	if 'import_file' not in session:
		flash('インポートするファイルが見つかりません', 'error')
		return redirect(url_for('import.index'))
	if session.get('import_type') == 'excel' and 'selected_sheet' not in session:
		return redirect(url_for('import.select_sheet'))
	try:
		import_service = ImportService()
		auto_mapping = import_service.get_auto_mapping(session['import_columns'])
		system_fields = import_service.get_system_fields()
		branch_suggestions = import_service.get_branch_mapping_suggestions(session['import_columns'])
		template_vars = {
			'filename': os.path.basename(session['import_file']),
			'columns': session['import_columns'],
			'sample_data': session['import_sample_data'],
			'row_count': session['import_row_count'],
			'auto_mapping': auto_mapping,
			'system_fields': system_fields,
			'branch_suggestions': branch_suggestions,
			'file_type': session.get('import_type'),
		}
		if session.get('import_type') == 'excel':
			template_vars['selected_sheet'] = session.get('selected_sheet')
			template_vars['excel_info'] = session.get('excel_info')
		return render_template('import/mapping.html', **template_vars)
	except Exception as e:
		flash(f'マッピング画面の表示中にエラーが発生しました: {str(e)}', 'error')
		return redirect(url_for('import.index'))


@import_bp.route('/set_mapping', methods=['POST'])
def set_mapping():
	from flask import session
	if 'import_file' not in session:
		flash('インポートするファイルが見つかりません', 'error')
		return redirect(url_for('import.index'))
	try:
		import_service = ImportService()
		column_mapping = {}
		for key, value in request.form.items():
			if key.startswith('mapping_') and value:
				field_name = key.replace('mapping_', '')
				column_mapping[field_name] = value
		validation_result = import_service.validate_mapping(column_mapping, session['import_columns'])
		if not validation_result['valid']:
			for error in validation_result['errors']:
				flash(error, 'error')
			return redirect(url_for('import.mapping'))
		for warning in validation_result['warnings']:
			flash(warning, 'warning')
		session['import_column_mapping'] = column_mapping
		flash('列マッピングが設定されました', 'success')
		return redirect(url_for('import.preview'))
	except Exception as e:
		flash(f'列マッピング設定中にエラーが発生しました: {str(e)}', 'error')
		return redirect(url_for('import.mapping'))


@import_bp.route('/preview')
def preview():
	from flask import session
	if 'import_file' not in session or 'import_column_mapping' not in session:
		flash('インポートするファイルまたは列マッピング情報が見つかりません', 'error')
		return redirect(url_for('import.index'))
	try:
		import_service = ImportService()
		preview_data = import_service.get_preview_data(
			session['import_file'], session['import_type'], session['import_column_mapping'], sheet_name=session.get('selected_sheet')
		)
		if preview_data['success']:
			return render_template('import/preview.html',
								   columns=session['import_columns'],
								   sample_data=session['import_sample_data'],
								   preview_data=preview_data['data'],
								   row_count=preview_data['row_count'],
								   validation_summary=preview_data.get('validation_summary'),
								   duplicates=preview_data.get('duplicates', []),
								   validation_errors=preview_data.get('validation_errors', []))
		else:
			flash(f'プレビューデータの取得に失敗しました: {preview_data["error"]}', 'error')
			return redirect(url_for('import.index'))
	except Exception as e:
		flash(f'プレビュー処理中にエラーが発生しました: {str(e)}', 'error')
		return redirect(url_for('import.index'))


@import_bp.route('/execute', methods=['POST'])
def execute_import():
	from flask import session
	if 'import_file' not in session or 'import_column_mapping' not in session:
		flash('インポートするファイルまたは列マッピング情報が見つかりません', 'error')
		return redirect(url_for('import.index'))
	try:
		import_service = ImportService()
		result = import_service.execute_import(
			session['import_file'], session['import_type'], session['import_column_mapping'], sheet_name=session.get('selected_sheet')
		)
		if os.path.exists(session['import_file']):
			os.remove(session['import_file'])
		if result.get('errors'):
			session['import_errors'] = result['errors']
		if result.get('duplicates'):
			session['import_duplicates'] = result['duplicates']
		if result.get('successful_projects'):
			session['import_successful_projects'] = result['successful_projects']
		session.pop('import_file', None)
		session.pop('import_type', None)
		session.pop('import_columns', None)
		session.pop('import_sample_data', None)
		session.pop('import_row_count', None)
		session.pop('import_column_mapping', None)
		session.pop('excel_info', None)
		session.pop('selected_sheet', None)
		if result['success']:
			flash(f'インポートが完了しました。成功: {result["success_count"]}件、エラー: {result["error_count"]}件', 'success')
			return render_template('import/result.html', result=result, errors=result.get('errors', []))
		else:
			flash(f'インポートに失敗しました: {result["error"]}', 'error')
			return redirect(url_for('import.index'))
	except Exception as e:
		from flask import session
		if 'import_file' in session and os.path.exists(session['import_file']):
			os.remove(session['import_file'])
		session.pop('import_file', None)
		session.pop('import_type', None)
		session.pop('import_columns', None)
		session.pop('import_sample_data', None)
		session.pop('import_row_count', None)
		session.pop('import_column_mapping', None)
		session.pop('excel_info', None)
		session.pop('selected_sheet', None)
		flash(f'インポート処理中にエラーが発生しました: {str(e)}', 'error')
		return redirect(url_for('import.index'))


@import_bp.route('/validate_mapping', methods=['POST'])
def validate_mapping():
	from flask import session
	if 'import_file' not in session:
		return jsonify({'success': False, 'error': 'セッション情報が見つかりません'})
	try:
		import_service = ImportService()
		column_mapping = {}
		for key, value in request.json.items():
			if key.startswith('mapping_') and value:
				field_name = key.replace('mapping_', '')
				column_mapping[field_name] = value
		validation_result = import_service.validate_mapping(column_mapping, session['import_columns'])
		return jsonify({'success': True, 'valid': validation_result['valid'], 'errors': validation_result['errors'], 'warnings': validation_result['warnings']})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})


@import_bp.route('/save_mapping', methods=['POST'])
def save_mapping():
	from flask import session
	try:
		column_mapping = {}
		mapping_name = request.json.get('mapping_name', 'デフォルト')
		for key, value in request.json.items():
			if key.startswith('mapping_') and value:
				field_name = key.replace('mapping_', '')
				column_mapping[field_name] = value
		if 'saved_mappings' not in session:
			session['saved_mappings'] = {}
		session['saved_mappings'][mapping_name] = column_mapping
		session.modified = True
		return jsonify({'success': True, 'message': f'マッピング設定「{mapping_name}」を保存しました'})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})


@import_bp.route('/load_mapping', methods=['POST'])
def load_mapping():
	from flask import session
	try:
		mapping_name = request.json.get('mapping_name')
		if 'saved_mappings' not in session or mapping_name not in session['saved_mappings']:
			return jsonify({'success': False, 'error': '指定されたマッピング設定が見つかりません'})
		column_mapping = session['saved_mappings'][mapping_name]
		return jsonify({'success': True, 'mapping': column_mapping})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})


@import_bp.route('/get_saved_mappings', methods=['GET'])
def get_saved_mappings():
	from flask import session
	try:
		saved_mappings = session.get('saved_mappings', {})
		return jsonify({'success': True, 'mappings': list(saved_mappings.keys())})
	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})


@import_bp.route('/download_error_report')
def download_error_report():
	from flask import session, make_response
	errors = session.get('import_errors', [])
	duplicates = session.get('import_duplicates', [])
	if not errors and not duplicates:
		flash('ダウンロード可能なエラーレポートがありません', 'warning')
		return redirect(url_for('import.index'))
	try:
		import_service = ImportService()
		csv_content = import_service.generate_error_report(errors, duplicates)
		response = make_response(csv_content)
		response.headers['Content-Type'] = 'text/csv; charset=utf-8'
		response.headers['Content-Disposition'] = 'attachment; filename=import_errors.csv'
		return response
	except Exception as e:
		flash(f'エラーレポートの生成に失敗しました: {str(e)}', 'error')
		return redirect(url_for('import.index'))


@import_bp.route('/download_success_report')
def download_success_report():
	from flask import session, make_response
	successful_projects = session.get('import_successful_projects', [])
	if not successful_projects:
		flash('ダウンロード可能な成功レポートがありません', 'warning')
		return redirect(url_for('import.index'))
	try:
		import_service = ImportService()
		csv_content = import_service.generate_success_report(successful_projects)
		response = make_response(csv_content)
		response.headers['Content-Type'] = 'text/csv; charset=utf-8'
		response.headers['Content-Disposition'] = 'attachment; filename=import_success.csv'
		return response
	except Exception as e:
		flash(f'成功レポートの生成に失敗しました: {str(e)}', 'error')
		return redirect(url_for('import.index'))


@import_bp.route('/cancel')
def cancel_import():
	from flask import session
	if 'import_file' in session and os.path.exists(session['import_file']):
		os.remove(session['import_file'])
	session.pop('import_file', None)
	session.pop('import_type', None)
	session.pop('import_columns', None)
	session.pop('import_sample_data', None)
	session.pop('import_row_count', None)
	session.pop('import_column_mapping', None)
	session.pop('excel_info', None)
	session.pop('selected_sheet', None)
	session.pop('import_errors', None)
	session.pop('import_duplicates', None)
	session.pop('import_successful_projects', None)
	flash('インポートをキャンセルしました', 'info')
	return redirect(url_for('import.index'))

__all__ = ["import_bp"]
