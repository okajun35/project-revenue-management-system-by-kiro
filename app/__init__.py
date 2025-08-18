import os
from flask import Flask, request
from sqlalchemy import inspect as sa_inspect
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
    
    # Register blueprints (centralized)
    from app.controllers.blueprints import register_blueprints
    register_blueprints(app)

    # Register error handlers (centralized)
    from app.controllers.error_handlers import register_error_handlers
    register_error_handlers(app)
    
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
    
    # リクエスト毎に最低限のDB初期化を保証（初回起動時の500回避）
    @app.before_request
    def ensure_db_initialized():
        try:
            inspector = sa_inspect(db.engine)
            tables = set(inspector.get_table_names())
            required = {"projects", "branches", "fiscal_years"}
            if not required.issubset(tables):
                # モデル読み込み後に作成
                from app import models  # noqa: F401
                db.create_all()
        except Exception:
            # 初期化段階の例外は握りつぶしてハンドラ（OperationalError フォールバック）に委ねる
            pass

    # Create database tables
    with app.app_context():
        # Ensure models are imported so SQLAlchemy is aware of all tables
        try:
            from app import models  # noqa: F401
        except Exception:
            # 遅延インポート失敗時でもアプリの起動は継続する
            pass
        db.create_all()
    
    return app