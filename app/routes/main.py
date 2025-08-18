from flask import Blueprint, render_template, jsonify, current_app, request
from app.services.dashboard_service import DashboardService
from app import db
import os
import shutil
import time

main_bp = Blueprint('main', __name__)
@main_bp.route('/')
def dashboard():
    """ダッシュボード画面"""
    available_years = DashboardService.get_available_years()
    current_year = available_years[0] if available_years else None
    stats = DashboardService.get_overall_stats(fiscal_year=current_year)
    stats['current_year'] = current_year
    recent_projects = DashboardService.get_recent_projects(limit=5)
    branch_stats = DashboardService.get_branch_stats(fiscal_year=current_year)
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_projects=recent_projects,
        available_years=available_years,
        branch_stats=branch_stats,
        current_year=current_year,
    )
@main_bp.route('/api/dashboard-data')
def dashboard_data():
    year = request.args.get('year', type=int)
    stats = DashboardService.get_overall_stats(fiscal_year=year)
    return jsonify(stats)


@main_bp.route('/api/chart-data')
def chart_data():
    trend_data = DashboardService.get_yearly_trend_data()
    return jsonify(trend_data)


@main_bp.route('/api/branch-stats')
def branch_stats():
    year = request.args.get('year', type=int)
    stats = DashboardService.get_branch_stats(fiscal_year=year)
    return jsonify({'branch_stats': stats, 'year': year})


@main_bp.route('/api/recent-projects')
def recent_projects():
    limit = request.args.get('limit', default=5, type=int)
    projects = DashboardService.get_recent_projects(limit=limit)
    return jsonify({'recent_projects': projects, 'count': len(projects)})


@main_bp.route('/api/top-projects')
def top_projects():
    year = request.args.get('year', type=int)
    limit = request.args.get('limit', default=10, type=int)
    projects = DashboardService.get_top_projects_by_revenue(fiscal_year=year, limit=limit)
    return jsonify({'top_projects': projects, 'year': year, 'count': len(projects)})

@main_bp.route('/health')
def health_check():
    """Comprehensive health check endpoint."""
    health_status = {
        'status': 'healthy',
        'checks': {}
    }

    # Database connectivity
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful',
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e),
        }

    # Disk space for data directory
    try:
        data_path = current_app.config.get('DATABASE_PATH', './data')
        data_dir = data_path.parent if hasattr(data_path, 'parent') else data_path
        if os.path.exists(data_dir):
            usage = shutil.disk_usage(str(data_dir))
            total_space = usage.total
            free_space = usage.free
            used_space = usage.used
            usage_percent = (used_space / total_space) * 100 if total_space else 0.0
            health_status['checks']['disk_space'] = {
                'status': 'healthy' if usage_percent < 90 else 'warning',
                'usage_percent': round(usage_percent, 2),
                'free_space_mb': round(free_space / (1024 * 1024), 2),
            }
        else:
            health_status['checks']['disk_space'] = {
                'status': 'unknown',
                'message': 'Data directory not found',
            }
    except Exception as e:
        health_status['checks']['disk_space'] = {
            'status': 'error',
            'error': str(e),
        }

    # Upload directory accessibility
    try:
        upload_dir = current_app.config.get('UPLOAD_FOLDER', './uploads')
        if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
            health_status['checks']['upload_directory'] = {
                'status': 'healthy',
                'message': 'Upload directory is writable',
            }
        else:
            health_status['status'] = 'unhealthy'
            health_status['checks']['upload_directory'] = {
                'status': 'unhealthy',
                'message': 'Upload directory not accessible',
            }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['upload_directory'] = {
            'status': 'error',
            'error': str(e),
        }

    health_status['response_time_ms'] = round(time.time() * 1000) % 1000
    return jsonify(health_status), (200 if health_status['status'] == 'healthy' else 503)


@main_bp.route('/ready')
def readiness_check():
    try:
        db.session.execute(db.text('SELECT COUNT(*) FROM projects LIMIT 1'))
        return jsonify({'status': 'ready', 'message': 'Application is ready to serve requests'}), 200
    except Exception as e:
        return jsonify({'status': 'not_ready', 'error': str(e)}), 503


@main_bp.route('/live')
def liveness_check():
    return jsonify({'status': 'alive', 'message': 'Application is running'}), 200


@main_bp.route('/api/monthly-revenue-trend')
def monthly_revenue_trend():
    fiscal_year = request.args.get('year', type=int)
    branch_ids = request.args.getlist('branch_ids', type=int)
    order_probabilities = request.args.getlist('order_probabilities', type=int)
    if not fiscal_year:
        available_years = DashboardService.get_available_years()
        fiscal_year = available_years[0] if available_years else 2024
    trend_data = DashboardService.get_monthly_revenue_trend(
        fiscal_year=fiscal_year,
        branch_ids=branch_ids if branch_ids else None,
        order_probabilities=order_probabilities if order_probabilities else None,
    )
    return jsonify(trend_data)


@main_bp.route('/api/filter-options')
def filter_options():
    return jsonify({
        'branches': DashboardService.get_available_branches(),
        'order_probabilities': DashboardService.get_available_order_probabilities(),
        'years': DashboardService.get_available_years(),
    })


@main_bp.route('/api/order-probability-distribution')
def order_probability_distribution():
    """受注角度別分布API"""
    year = request.args.get('year', type=int)
    distribution = DashboardService.get_order_probability_distribution(fiscal_year=year)
    return jsonify({'distribution': distribution, 'year': year})


@main_bp.route('/test-static')
def test_static():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>静的ファイルテスト</title>
        <link rel="stylesheet" href="/static/AdminLTE-3.2.0/dist/css/adminlte.min.css">
        <link rel="stylesheet" href="/static/AdminLTE-3.2.0/plugins/fontawesome-free/css/all.min.css">
    </head>
    <body>
        <div class="container mt-4">
            <h1 class="text-primary"><i class="fas fa-check"></i> 静的ファイルテスト</h1>
            <p>このページでCSSとアイコンが正しく表示されていれば、静的ファイルの配信は正常です。</p>
            <div class="alert alert-success">
                <i class="fas fa-info-circle"></i> AdminLTEのスタイルが適用されています
            </div>
        </div>
        <script src="/static/AdminLTE-3.2.0/plugins/jquery/jquery.min.js"></script>
        <script>
            $(document).ready(function() {
                console.log('jQuery loaded successfully');
            });
        </script>
    </body>
    </html>
    '''


@main_bp.route('/debug-dashboard')
def debug_dashboard():
    try:
        with open('test_dashboard_simple.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>ダッシュボードデバッグ</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/admin-lte/3.2.0/css/adminlte.min.css">
        </head>
        <body>
            <div class="container mt-4">
                <h1>ダッシュボード機能テスト</h1>
                <!-- content trimmed for brevity in debug page -->
            </div>
        </body>
        </html>
        '''
