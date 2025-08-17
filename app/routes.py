from flask import Blueprint, render_template, jsonify, send_from_directory, current_app, request
from app.models import Project
from app.services.dashboard_service import DashboardService
from app import db
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    """ダッシュボード画面"""
    # 利用可能な年度一覧を取得
    available_years = DashboardService.get_available_years()
    
    # デフォルトは最新年度
    current_year = available_years[0] if available_years else None
    
    # 最新年度の統計情報を取得
    stats = DashboardService.get_overall_stats(fiscal_year=current_year)
    stats['current_year'] = current_year  # テンプレートで使用するために追加
    
    # 最近更新されたプロジェクト一覧を取得（最大5件）
    recent_projects = DashboardService.get_recent_projects(limit=5)
    
    # 支社別統計情報を取得
    branch_stats = DashboardService.get_branch_stats(fiscal_year=current_year)
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_projects=recent_projects,
                         available_years=available_years,
                         branch_stats=branch_stats,
                         current_year=current_year)

@main_bp.route('/api/dashboard-data')
def dashboard_data():
    """年度別ダッシュボードデータAPI"""
    year = request.args.get('year', type=int)
    
    # DashboardServiceを使用して統計情報を取得
    stats = DashboardService.get_overall_stats(fiscal_year=year)
    
    return jsonify(stats)

@main_bp.route('/api/chart-data')
def chart_data():
    """年度別チャートデータAPI"""
    # DashboardServiceを使用して年度別推移データを取得
    trend_data = DashboardService.get_yearly_trend_data()
    
    return jsonify(trend_data)

@main_bp.route('/api/branch-stats')
def branch_stats():
    """支社別統計情報API"""
    year = request.args.get('year', type=int)
    
    # DashboardServiceを使用して支社別統計を取得
    stats = DashboardService.get_branch_stats(fiscal_year=year)
    
    return jsonify({
        'branch_stats': stats,
        'year': year
    })

@main_bp.route('/api/recent-projects')
def recent_projects():
    """最近更新されたプロジェクトAPI"""
    limit = request.args.get('limit', default=5, type=int)
    
    # DashboardServiceを使用して最近のプロジェクトを取得
    projects = DashboardService.get_recent_projects(limit=limit)
    
    return jsonify({
        'recent_projects': projects,
        'count': len(projects)
    })

@main_bp.route('/api/top-projects')
def top_projects():
    """売上上位プロジェクトAPI"""
    year = request.args.get('year', type=int)
    limit = request.args.get('limit', default=10, type=int)
    
    # DashboardServiceを使用して売上上位プロジェクトを取得
    projects = DashboardService.get_top_projects_by_revenue(fiscal_year=year, limit=limit)
    
    return jsonify({
        'top_projects': projects,
        'year': year,
        'count': len(projects)
    })

@main_bp.route('/api/order-probability-distribution')
def order_probability_distribution():
    """受注角度別分布API"""
    year = request.args.get('year', type=int)
    
    # DashboardServiceを使用して受注角度別分布を取得
    distribution = DashboardService.get_order_probability_distribution(fiscal_year=year)
    
    return jsonify({
        'distribution': distribution,
        'year': year
    })

@main_bp.route('/health')
def health_check():
    """ヘルスチェックエンドポイント"""
    import os
    import time
    from datetime import datetime
    
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'checks': {}
    }
    
    # データベース接続テスト
    try:
        db.session.execute(db.text('SELECT 1'))
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
    
    # ディスク容量チェック
    try:
        data_dir = current_app.config.get('DATABASE_PATH', './data').parent
        if os.path.exists(data_dir):
            statvfs = os.statvfs(data_dir)
            free_space = statvfs.f_frsize * statvfs.f_bavail
            total_space = statvfs.f_frsize * statvfs.f_blocks
            usage_percent = ((total_space - free_space) / total_space) * 100
            
            health_status['checks']['disk_space'] = {
                'status': 'healthy' if usage_percent < 90 else 'warning',
                'usage_percent': round(usage_percent, 2),
                'free_space_mb': round(free_space / (1024 * 1024), 2)
            }
        else:
            health_status['checks']['disk_space'] = {
                'status': 'unknown',
                'message': 'Data directory not found'
            }
    except Exception as e:
        health_status['checks']['disk_space'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # アップロードディレクトリチェック
    try:
        upload_dir = current_app.config.get('UPLOAD_FOLDER', './uploads')
        if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
            health_status['checks']['upload_directory'] = {
                'status': 'healthy',
                'message': 'Upload directory is writable'
            }
        else:
            health_status['status'] = 'unhealthy'
            health_status['checks']['upload_directory'] = {
                'status': 'unhealthy',
                'message': 'Upload directory not accessible'
            }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['upload_directory'] = {
            'status': 'error',
            'error': str(e)
        }
    
    # レスポンス時間測定
    health_status['response_time_ms'] = round(time.time() * 1000) % 1000
    
    # 全体的なステータス判定
    if health_status['status'] == 'healthy':
        return jsonify(health_status), 200
    else:
        return jsonify(health_status), 503

@main_bp.route('/ready')
def readiness_check():
    """レディネスチェックエンドポイント（Kubernetes用）"""
    try:
        # 基本的なアプリケーション準備状態をチェック
        db.session.execute(db.text('SELECT COUNT(*) FROM projects LIMIT 1'))
        
        return jsonify({
            'status': 'ready',
            'message': 'Application is ready to serve requests'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'not_ready',
            'error': str(e)
        }), 503

@main_bp.route('/live')
def liveness_check():
    """ライブネスチェックエンドポイント（Kubernetes用）"""
    return jsonify({
        'status': 'alive',
        'message': 'Application is running'
    }), 200

@main_bp.route('/api/monthly-revenue-trend')
def monthly_revenue_trend():
    """月別売上推移データAPI"""
    fiscal_year = request.args.get('year', type=int)
    branch_ids = request.args.getlist('branch_ids', type=int)
    order_probabilities = request.args.getlist('order_probabilities', type=int)
    
    # デフォルト年度設定
    if not fiscal_year:
        available_years = DashboardService.get_available_years()
        fiscal_year = available_years[0] if available_years else 2024
    
    # 月別推移データを取得
    trend_data = DashboardService.get_monthly_revenue_trend(
        fiscal_year=fiscal_year,
        branch_ids=branch_ids if branch_ids else None,
        order_probabilities=order_probabilities if order_probabilities else None
    )
    
    return jsonify(trend_data)

@main_bp.route('/api/filter-options')
def filter_options():
    """フィルタオプションAPI"""
    return jsonify({
        'branches': DashboardService.get_available_branches(),
        'order_probabilities': DashboardService.get_available_order_probabilities(),
        'years': DashboardService.get_available_years()
    })

@main_bp.route('/test-static')
def test_static():
    """静的ファイルテスト用ページ"""
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
    """ダッシュボードデバッグページ"""
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
                
                <!-- 年度選択 -->
                <div class="form-group">
                    <label for="year-select">年度選択:</label>
                    <select id="year-select" class="form-control" style="width: 200px;">
                        <option value="">全年度</option>
                        <option value="2023">2023年度</option>
                        <option value="2024">2024年度</option>
                        <option value="2025">2025年度</option>
                    </select>
                </div>
                
                <!-- 統計表示 -->
                <div class="row">
                    <div class="col-3">
                        <div class="small-box bg-info">
                            <div class="inner">
                                <h3 id="total-projects">0</h3>
                                <p>総プロジェクト数</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="small-box bg-success">
                            <div class="inner">
                                <h3 id="total-revenue">¥0</h3>
                                <p>総売上</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="small-box bg-warning">
                            <div class="inner">
                                <h3 id="total-expenses">¥0</h3>
                                <p>総経費</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-3">
                        <div class="small-box bg-danger">
                            <div class="inner">
                                <h3 id="total-gross-profit">¥0</h3>
                                <p>総粗利</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- チャート -->
                <div class="card">
                    <div class="card-header">
                        <h3>年度別売上推移</h3>
                    </div>
                    <div class="card-body">
                        <canvas id="revenue-chart" width="400" height="200"></canvas>
                    </div>
                </div>
                
                <!-- ログ表示 -->
                <div class="card mt-3">
                    <div class="card-header">
                        <h3>デバッグログ</h3>
                    </div>
                    <div class="card-body">
                        <pre id="debug-log"></pre>
                    </div>
                </div>
            </div>

            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.4/Chart.min.js"></script>
            
            <script>
                $(document).ready(function() {
                    var log = $('#debug-log');
                    function addLog(message) {
                        log.append(new Date().toLocaleTimeString() + ': ' + message + '\\n');
                    }
                    
                    addLog('Page loaded');
                    addLog('jQuery available: ' + (typeof $ !== 'undefined'));
                    addLog('Chart.js available: ' + (typeof Chart !== 'undefined'));
                    
                    var chart;
                    
                    // 統計データを更新
                    function updateStats(year) {
                        var url = '/api/dashboard-data';
                        if (year) {
                            url += '?year=' + year;
                        }
                        
                        addLog('Fetching stats for year: ' + (year || 'all'));
                        
                        $.get(url)
                            .done(function(data) {
                                addLog('Stats received: ' + JSON.stringify(data));
                                $('#total-projects').text(data.total_projects);
                                $('#total-revenue').text('¥' + data.total_revenue.toLocaleString());
                                $('#total-expenses').text('¥' + data.total_expenses.toLocaleString());
                                $('#total-gross-profit').text('¥' + data.total_gross_profit.toLocaleString());
                            })
                            .fail(function(xhr, status, error) {
                                addLog('Stats error: ' + error);
                            });
                    }
                    
                    // チャートデータを読み込み
                    function loadChart() {
                        addLog('Loading chart data...');
                        
                        $.get('/api/chart-data')
                            .done(function(data) {
                                addLog('Chart data received: ' + JSON.stringify(data));
                                
                                if (chart) {
                                    chart.destroy();
                                }
                                
                                var ctx = document.getElementById('revenue-chart').getContext('2d');
                                chart = new Chart(ctx, {
                                    type: 'line',
                                    data: {
                                        labels: data.years,
                                        datasets: [{
                                            label: '売上',
                                            data: data.revenues,
                                            borderColor: 'rgb(75, 192, 192)',
                                            backgroundColor: 'rgba(75, 192, 192, 0.2)',
                                            tension: 0.1
                                        }]
                                    },
                                    options: {
                                        responsive: true,
                                        scales: {
                                            yAxes: [{
                                                ticks: {
                                                    callback: function(value) {
                                                        return '¥' + value.toLocaleString();
                                                    }
                                                }
                                            }]
                                        }
                                    }
                                });
                                
                                addLog('Chart created successfully');
                            })
                            .fail(function(xhr, status, error) {
                                addLog('Chart error: ' + error);
                            });
                    }
                    
                    // 年度選択イベント
                    $('#year-select').change(function() {
                        var selectedYear = $(this).val();
                        addLog('Year changed to: ' + selectedYear);
                        updateStats(selectedYear);
                    });
                    
                    // 初期データ読み込み
                    updateStats();
                    loadChart();
                });
            </script>
        </body>
        </html>
        '''