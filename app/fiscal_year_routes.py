from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import FiscalYear, ValidationError
from app import db

fiscal_year_bp = Blueprint('fiscal_years', __name__, url_prefix='/fiscal-years')

@fiscal_year_bp.route('/')
def index():
    """年度一覧画面"""
    return render_template('fiscal_years/index.html')

@fiscal_year_bp.route('/new')
def new():
    """新規年度作成フォーム画面"""
    return render_template('fiscal_years/form.html', title='新規年度作成')

@fiscal_year_bp.route('/', methods=['POST'])
def create():
    """年度作成処理"""
    try:
        year = int(request.form.get('year'))
        year_name = request.form.get('year_name', f"{year}年度")
        
        fiscal_year = FiscalYear.create_with_validation(
            year=year,
            year_name=year_name
        )
        
        flash(f'✅ 年度「{fiscal_year.year_name}」を正常に作成しました。', 'success')
        return redirect(url_for('fiscal_years.index'))
        
    except ValidationError as e:
        flash(e.message, 'error')
    except ValueError:
        flash('年度は数値で入力してください。', 'error')
    except Exception as e:
        flash('年度の作成中にエラーが発生しました。', 'error')
        db.session.rollback()
    
    return render_template('fiscal_years/form.html', title='新規年度作成')

@fiscal_year_bp.route('/<int:fiscal_year_id>')
def show(fiscal_year_id):
    """年度詳細画面"""
    fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
    return render_template('fiscal_years/show.html', fiscal_year=fiscal_year)

@fiscal_year_bp.route('/<int:fiscal_year_id>/edit')
def edit(fiscal_year_id):
    """年度編集フォーム画面"""
    fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
    return render_template('fiscal_years/form.html', fiscal_year=fiscal_year, title='年度編集')

@fiscal_year_bp.route('/<int:fiscal_year_id>/update', methods=['POST'])
def update(fiscal_year_id):
    """年度更新処理"""
    fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
    
    try:
        year = int(request.form.get('year'))
        year_name = request.form.get('year_name')
        
        # 年度を更新
        fiscal_year.year = year
        fiscal_year.year_name = year_name
        
        # データ検証
        validation_errors = fiscal_year.validate_data()
        if validation_errors:
            raise validation_errors[0]
        
        # 重複チェック（自分自身を除外）
        fiscal_year.validate_unique_year(exclude_id=fiscal_year.id)
        fiscal_year.validate_unique_year_name(exclude_id=fiscal_year.id)
        
        db.session.commit()
        
        flash(f'✅ 年度「{fiscal_year.year_name}」を正常に更新しました。', 'success')
        return redirect(url_for('fiscal_years.index'))
        
    except ValidationError as e:
        flash(e.message, 'error')
    except ValueError:
        flash('年度は数値で入力してください。', 'error')
    except Exception as e:
        flash('年度の更新中にエラーが発生しました。', 'error')
        db.session.rollback()
    
    return render_template('fiscal_years/form.html', fiscal_year=fiscal_year, title='年度編集')

@fiscal_year_bp.route('/<int:fiscal_year_id>/delete', methods=['POST'])
def delete(fiscal_year_id):
    """年度削除処理"""
    fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
    
    try:
        # 関連プロジェクトの存在チェック
        if fiscal_year.projects:
            flash('この年度には関連するプロジェクトが存在するため削除できません。', 'error')
            return redirect(url_for('fiscal_years.index'))
        
        year_name = fiscal_year.year_name
        db.session.delete(fiscal_year)
        db.session.commit()
        flash(f'🗑️ 年度「{year_name}」を正常に削除しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash('年度の削除中にエラーが発生しました。', 'error')
    
    return redirect(url_for('fiscal_years.index'))

@fiscal_year_bp.route('/<int:fiscal_year_id>/toggle', methods=['POST'])
def toggle_active(fiscal_year_id):
    """年度の有効/無効切り替え"""
    fiscal_year = FiscalYear.query.get_or_404(fiscal_year_id)
    
    try:
        fiscal_year.is_active = not fiscal_year.is_active
        db.session.commit()
        
        status = "有効" if fiscal_year.is_active else "無効"
        flash(f'✅ 年度「{fiscal_year.year_name}」を{status}に変更しました。', 'success')
    except Exception as e:
        db.session.rollback()
        flash('年度の状態変更中にエラーが発生しました。', 'error')
    
    return redirect(url_for('fiscal_years.index'))

@fiscal_year_bp.route('/api/list')
def api_list():
    """年度一覧API（DataTables用）"""
    try:
        # DataTablesのパラメータを取得
        draw = request.args.get('draw', type=int, default=1)
        start = request.args.get('start', type=int, default=0)
        length = request.args.get('length', type=int, default=25)
        search_value = request.args.get('search[value]', default='')
        
        # ソート情報を取得
        order_column = request.args.get('order[0][column]', type=int, default=1)  # デフォルトは年度
        order_dir = request.args.get('order[0][dir]', default='desc')
        
        # 列のマッピング
        columns = [
            'year',        # 0
            'year_name',   # 1
            'is_active',   # 2
            'project_count', # 3
            'created_at',  # 4
            'actions'      # 5
        ]
        
        # ベースクエリ
        query = FiscalYear.query
        
        # 検索フィルタを適用
        if search_value:
            query = query.filter(
                db.or_(
                    FiscalYear.year.like(f'%{search_value}%'),
                    FiscalYear.year_name.contains(search_value)
                )
            )
        
        # 総レコード数を取得
        total_records = FiscalYear.query.count()
        filtered_records = query.count()
        
        # ソートを適用
        if order_column < len(columns) and columns[order_column] != 'actions':
            column_name = columns[order_column]
            if column_name == 'project_count':
                # プロジェクト数でソート（サブクエリ使用）
                from app.models import Project
                project_count_subquery = db.session.query(
                    Project.fiscal_year,
                    db.func.count(Project.id).label('count')
                ).group_by(Project.fiscal_year).subquery()
                
                query = query.outerjoin(
                    project_count_subquery,
                    FiscalYear.year == project_count_subquery.c.fiscal_year
                )
                
                if order_dir == 'desc':
                    query = query.order_by(db.func.coalesce(project_count_subquery.c.count, 0).desc())
                else:
                    query = query.order_by(db.func.coalesce(project_count_subquery.c.count, 0).asc())
            else:
                column = getattr(FiscalYear, column_name)
                if order_dir == 'desc':
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        else:
            # デフォルトソート（年度降順）
            query = query.order_by(FiscalYear.year.desc())
        
        # ページネーションを適用
        fiscal_years = query.offset(start).limit(length).all()
        
        # データを整形
        data = []
        for fiscal_year in fiscal_years:
            # プロジェクト数を取得
            project_count = len(fiscal_year.projects) if fiscal_year.projects else 0
            
            # 有効/無効のバッジ
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