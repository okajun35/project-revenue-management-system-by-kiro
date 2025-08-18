import os
from pathlib import Path

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    BASE_DIR = Path(__file__).parent
    DATABASE_PATH = BASE_DIR / 'data' / 'projects.db'
    # Windows でも安定して解決できるように、URI は POSIX 形式にする
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH.as_posix()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    
    # Pagination
    PROJECTS_PER_PAGE = 20
    
    # Static files configuration
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files
    
    # Debug toolbar configuration
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # セキュリティ設定
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ログ設定
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/app/logs/app.log')
    
    def __init__(self):
        super().__init__()
        self.SECRET_KEY = os.environ.get('SECRET_KEY')
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")
        
        # データベースURLの上書き（環境変数から）
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            self.SQLALCHEMY_DATABASE_URI = database_url

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # テスト専用のファイルベースDBを使用して、接続の跨りで状態を保持しつつ本番DBを保護
    TEST_DATABASE_PATH = Config.BASE_DIR / 'data' / 'test_sample.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + TEST_DATABASE_PATH.as_posix()
    WTF_CSRF_ENABLED = False

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}