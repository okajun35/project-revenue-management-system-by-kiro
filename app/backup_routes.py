from flask import Blueprint, request, jsonify, send_file, render_template, redirect, url_for, flash, current_app
from app.models import Project, Branch, FiscalYear, ValidationError
from app import db
import json
import io
from datetime import datetime
import os
import tempfile
from werkzeug.utils import secure_filename

backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

@backup_bp.route('/')
def index():
    """バックアップ・リストア管理画面"""
    return render_template('backup/index.html')

@backup_bp.route('/create')
def create_backup():
    """バックアップファイル作成"""
    try:
        # 全データを取得
        projects_data = []
        branches_data = []
        fiscal_years_data = []
        
        # プロジェクトデータを取得
        projects = Project.query.all()
        for project in projects:
            projects_data.append({
                'id': project.id,
                'project_code': project.project_code,
                'project_name': project.project_name,
                'branch_id': project.branch_id,
                'fiscal_year': project.fiscal_year,
                'order_probability': float(project.order_probability),
                'revenue': float(project.revenue),
                'expenses': float(project.expenses),
                'created_at': project.created_at.isoformat() if project.created_at else None,
                'updated_at': project.updated_at.isoformat() if project.updated_at else None
            })
        
        # 支社データを取得
        branches = Branch.query.all()
        for branch in branches:
            branches_data.append({
                'id': branch.id,
                'branch_code': branch.branch_code,
                'branch_name': branch.branch_name,
                'is_active': branch.is_active,
                'created_at': branch.created_at.isoformat() if branch.created_at else None,
                'updated_at': branch.updated_at.isoformat() if branch.updated_at else None
            })
        
        # 年度データを取得
        fiscal_years = FiscalYear.query.all()
        for fiscal_year in fiscal_years:
            fiscal_years_data.append({
                'id': fiscal_year.id,
                'year': fiscal_year.year,
                'year_name': fiscal_year.year_name,
                'is_active': fiscal_year.is_active,
                'created_at': fiscal_year.created_at.isoformat() if fiscal_year.created_at else None,
                'updated_at': fiscal_year.updated_at.isoformat() if fiscal_year.updated_at else None
            })
        
        # バックアップデータを作成
        backup_data = {
            'backup_info': {
                'created_at': datetime.now().isoformat(),
                'version': '1.0',
                'description': 'プロジェクト収支システム バックアップデータ'
            },
            'data': {
                'projects': projects_data,
                'branches': branches_data,
                'fiscal_years': fiscal_years_data
            },
            'statistics': {
                'projects_count': len(projects_data),
                'branches_count': len(branches_data),
                'fiscal_years_count': len(fiscal_years_data)
            }
        }
        
        # JSONファイルを生成
        json_str = json.dumps(backup_data, ensure_ascii=False, indent=2)
        json_bytes = io.BytesIO(json_str.encode('utf-8'))
        json_bytes.seek(0)
        
        # ファイル名を生成（現在日時を含む）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'project_system_backup_{timestamp}.json'
        
        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f'Backup creation error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'バックアップファイルの作成中にエラーが発生しました。'
        }), 500

@backup_bp.route('/info')
def backup_info():
    """バックアップ対象データの情報を取得"""
    try:
        # 各テーブルのレコード数を取得
        projects_count = Project.query.count()
        branches_count = Branch.query.count()
        fiscal_years_count = FiscalYear.query.count()
        
        # 最新更新日を取得
        latest_project = Project.query.order_by(Project.updated_at.desc()).first()
        latest_branch = Branch.query.order_by(Branch.updated_at.desc()).first()
        latest_fiscal_year = FiscalYear.query.order_by(FiscalYear.updated_at.desc()).first()
        
        latest_update = None
        for item in [latest_project, latest_branch, latest_fiscal_year]:
            if item and item.updated_at:
                if latest_update is None or item.updated_at > latest_update:
                    latest_update = item.updated_at
        
        return jsonify({
            'success': True,
            'data': {
                'projects_count': projects_count,
                'branches_count': branches_count,
                'fiscal_years_count': fiscal_years_count,
                'total_records': projects_count + branches_count + fiscal_years_count,
                'latest_update': latest_update.isoformat() if latest_update else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f'Backup info error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'バックアップ情報の取得中にエラーが発生しました。'
        }), 500

@backup_bp.route('/upload', methods=['POST'])
def upload_backup():
    """バックアップファイルのアップロード"""
    try:
        if 'backup_file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'ファイルが選択されていません。'
            }), 400
        
        file = request.files['backup_file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'ファイルが選択されていません。'
            }), 400
        
        # ファイル拡張子をチェック
        if not file.filename.lower().endswith('.json'):
            return jsonify({
                'success': False,
                'error': 'JSONファイルを選択してください。'
            }), 400
        
        # ファイル内容を読み込み
        try:
            file_content = file.read().decode('utf-8')
            backup_data = json.loads(file_content)
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'ファイル形式が正しくありません。有効なJSONファイルを選択してください。'
            }), 400
        except UnicodeDecodeError:
            return jsonify({
                'success': False,
                'error': 'ファイルの文字エンコーディングが正しくありません。'
            }), 400
        
        # バックアップファイルの構造を検証
        validation_result = validate_backup_file(backup_data)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'error': f'バックアップファイルの形式が正しくありません: {validation_result["error"]}'
            }), 400
        
        # プレビュー情報を生成
        preview_info = generate_restore_preview(backup_data)
        
        # セッションにバックアップデータを保存（実際の実装では一時ファイルを使用することを推奨）
        session_key = f"backup_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 一時ファイルに保存
        temp_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_filename = secure_filename(f"{session_key}.json")
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        with open(temp_filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'session_key': session_key,
            'preview': preview_info,
            'message': 'バックアップファイルが正常にアップロードされました。'
        })
        
    except Exception as e:
        current_app.logger.error(f'Backup upload error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'ファイルのアップロード中にエラーが発生しました。'
        }), 500

@backup_bp.route('/restore', methods=['POST'])
def restore_data():
    """データのリストア実行"""
    try:
        data = request.get_json()
        session_key = data.get('session_key')
        confirm = data.get('confirm', False)
        
        if not session_key:
            return jsonify({
                'success': False,
                'error': 'セッションキーが指定されていません。'
            }), 400
        
        if not confirm:
            return jsonify({
                'success': False,
                'error': 'リストア実行の確認が必要です。'
            }), 400
        
        # 一時ファイルからバックアップデータを読み込み
        temp_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        temp_filename = secure_filename(f"{session_key}.json")
        temp_filepath = os.path.join(temp_dir, temp_filename)
        
        if not os.path.exists(temp_filepath):
            return jsonify({
                'success': False,
                'error': 'バックアップデータが見つかりません。再度ファイルをアップロードしてください。'
            }), 400
        
        with open(temp_filepath, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # リストア実行
        restore_result = execute_restore(backup_data)
        
        # 一時ファイルを削除
        try:
            os.remove(temp_filepath)
        except:
            pass
        
        if restore_result['success']:
            return jsonify({
                'success': True,
                'message': 'データのリストアが正常に完了しました。',
                'statistics': restore_result['statistics']
            })
        else:
            return jsonify({
                'success': False,
                'error': restore_result['error']
            }), 500
        
    except Exception as e:
        current_app.logger.error(f'Restore execution error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'リストア実行中にエラーが発生しました。'
        }), 500

def validate_backup_file(backup_data):
    """バックアップファイルの構造を検証"""
    try:
        # 必須フィールドの存在確認
        if 'backup_info' not in backup_data:
            return {'valid': False, 'error': 'backup_info セクションが見つかりません'}
        
        if 'data' not in backup_data:
            return {'valid': False, 'error': 'data セクションが見つかりません'}
        
        data_section = backup_data['data']
        
        # 各テーブルデータの存在確認
        required_tables = ['projects', 'branches', 'fiscal_years']
        for table in required_tables:
            if table not in data_section:
                return {'valid': False, 'error': f'{table} データが見つかりません'}
            
            if not isinstance(data_section[table], list):
                return {'valid': False, 'error': f'{table} データの形式が正しくありません'}
        
        # プロジェクトデータの構造確認
        if data_section['projects']:
            project_sample = data_section['projects'][0]
            required_project_fields = ['project_code', 'project_name', 'branch_id', 'fiscal_year', 
                                     'order_probability', 'revenue', 'expenses']
            for field in required_project_fields:
                if field not in project_sample:
                    return {'valid': False, 'error': f'プロジェクトデータに {field} フィールドが見つかりません'}
        
        # 支社データの構造確認
        if data_section['branches']:
            branch_sample = data_section['branches'][0]
            required_branch_fields = ['branch_code', 'branch_name', 'is_active']
            for field in required_branch_fields:
                if field not in branch_sample:
                    return {'valid': False, 'error': f'支社データに {field} フィールドが見つかりません'}
        
        return {'valid': True, 'error': None}
        
    except Exception as e:
        return {'valid': False, 'error': f'ファイル検証中にエラーが発生しました: {str(e)}'}

def generate_restore_preview(backup_data):
    """リストアプレビュー情報を生成"""
    try:
        data_section = backup_data['data']
        
        # 現在のデータ件数
        current_projects = Project.query.count()
        current_branches = Branch.query.count()
        current_fiscal_years = FiscalYear.query.count()
        
        # バックアップデータ件数
        backup_projects = len(data_section['projects'])
        backup_branches = len(data_section['branches'])
        backup_fiscal_years = len(data_section['fiscal_years'])
        
        # バックアップ情報
        backup_info = backup_data.get('backup_info', {})
        
        return {
            'backup_info': {
                'created_at': backup_info.get('created_at'),
                'version': backup_info.get('version'),
                'description': backup_info.get('description')
            },
            'current_data': {
                'projects': current_projects,
                'branches': current_branches,
                'fiscal_years': current_fiscal_years,
                'total': current_projects + current_branches + current_fiscal_years
            },
            'backup_data': {
                'projects': backup_projects,
                'branches': backup_branches,
                'fiscal_years': backup_fiscal_years,
                'total': backup_projects + backup_branches + backup_fiscal_years
            },
            'warning': {
                'data_will_be_replaced': True,
                'current_data_will_be_lost': True
            }
        }
        
    except Exception as e:
        return {'error': f'プレビュー生成中にエラーが発生しました: {str(e)}'}

def execute_restore(backup_data):
    """リストア実行"""
    try:
        data_section = backup_data['data']
        
        try:
            # 既存データを削除（外部キー制約を考慮した順序）
            Project.query.delete()
            Branch.query.delete()
            FiscalYear.query.delete()
            
            # 年度データをリストア
            fiscal_years_created = 0
            for fy_data in data_section['fiscal_years']:
                fiscal_year = FiscalYear(
                    year=fy_data['year'],
                    year_name=fy_data['year_name'],
                    is_active=fy_data['is_active'],
                    created_at=datetime.fromisoformat(fy_data['created_at']) if fy_data.get('created_at') else datetime.now(),
                    updated_at=datetime.fromisoformat(fy_data['updated_at']) if fy_data.get('updated_at') else datetime.now()
                )
                db.session.add(fiscal_year)
                fiscal_years_created += 1
            
            # 支社データをリストア
            branches_created = 0
            branch_id_mapping = {}  # 旧ID -> 新IDのマッピング
            
            for branch_data in data_section['branches']:
                branch = Branch(
                    branch_code=branch_data['branch_code'],
                    branch_name=branch_data['branch_name'],
                    is_active=branch_data['is_active'],
                    created_at=datetime.fromisoformat(branch_data['created_at']) if branch_data.get('created_at') else datetime.now(),
                    updated_at=datetime.fromisoformat(branch_data['updated_at']) if branch_data.get('updated_at') else datetime.now()
                )
                db.session.add(branch)
                db.session.flush()  # IDを取得するためにflush
                
                # IDマッピングを保存
                old_id = branch_data.get('id')
                if old_id:
                    branch_id_mapping[old_id] = branch.id
                
                branches_created += 1
            
            # プロジェクトデータをリストア
            projects_created = 0
            for project_data in data_section['projects']:
                # 支社IDをマッピング
                old_branch_id = project_data['branch_id']
                new_branch_id = branch_id_mapping.get(old_branch_id)
                
                if not new_branch_id:
                    # マッピングが見つからない場合は最初の支社を使用
                    first_branch = Branch.query.first()
                    if first_branch:
                        new_branch_id = first_branch.id
                    else:
                        raise Exception('リストア用の支社データが見つかりません')
                
                project = Project(
                    project_code=project_data['project_code'],
                    project_name=project_data['project_name'],
                    branch_id=new_branch_id,
                    fiscal_year=project_data['fiscal_year'],
                    order_probability=project_data['order_probability'],
                    revenue=project_data['revenue'],
                    expenses=project_data['expenses'],
                    created_at=datetime.fromisoformat(project_data['created_at']) if project_data.get('created_at') else datetime.now(),
                    updated_at=datetime.fromisoformat(project_data['updated_at']) if project_data.get('updated_at') else datetime.now()
                )
                db.session.add(project)
                projects_created += 1
            
            # コミット
            db.session.commit()
            
            return {
                'success': True,
                'statistics': {
                    'projects_created': projects_created,
                    'branches_created': branches_created,
                    'fiscal_years_created': fiscal_years_created,
                    'total_created': projects_created + branches_created + fiscal_years_created
                }
            }
            
        except Exception as e:
            # ロールバック
            db.session.rollback()
            raise e
            
    except Exception as e:
        current_app.logger.error(f'Restore execution error: {str(e)}')
        return {
            'success': False,
            'error': f'リストア実行中にエラーが発生しました: {str(e)}'
        }