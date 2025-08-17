import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from config import config

# Initialize extensions
db = SQLAlchemy()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    # Flaskアプリケーションを作成（静的ファイルのパスを明示的に指定）
    app = Flask(__name__, 
                static_folder='../static',
                static_url_path='/static')
    app.config.from_object(config[config_name])
    
    # デバッグツールバーを無効化（静的ファイル配信の問題を回避）
    app.config['DEBUG_TB_ENABLED'] = False
    
    # Ensure data directory exists
    os.makedirs(app.config['DATABASE_PATH'].parent, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Register blueprints
    from app.routes import main_bp
    from app.project_routes import project_bp
    from app.branch_routes import branch_bp
    from app.fiscal_year_routes import fiscal_year_bp
    from app.export_routes import export_bp
    from app.import_routes import import_bp
    from app.backup_routes import backup_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(branch_bp)
    app.register_blueprint(fiscal_year_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(import_bp)
    app.register_blueprint(backup_bp)
    
    # 静的ファイル配信の改善
    @app.after_request
    def after_request(response):
        # 静的ファイルに適切なMIMEタイプを設定
        if response.mimetype == 'text/html' and request.path.startswith('/static/'):
            if request.path.endswith('.css'):
                response.mimetype = 'text/css'
            elif request.path.endswith('.js'):
                response.mimetype = 'application/javascript'
        return response
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app