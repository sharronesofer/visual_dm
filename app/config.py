"""
Application configuration.
"""

import os
from datetime import timedelta
from typing import Optional

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    PORT: int = int(os.environ.get('PORT', '5050'))
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///visual_dm.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Game Settings (non-sensitive configuration)
    MAX_PARTY_SIZE: int = 4
    MAX_INVENTORY_SLOTS: int = 20
    MAX_LEVEL: int = 20
    STARTING_GOLD: int = 100

    # Redis Cache
    REDIS_URL = "redis://localhost:6379/0"
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_KEY_PREFIX: str = 'visual_dm:'
    
    # API Configuration
    API_TITLE: str = 'Visual DM API'
    API_VERSION: str = '1.0'
    OPENAPI_VERSION: str = '3.0.2'
    
    # Performance
    SQLALCHEMY_POOL_SIZE: int = int(os.getenv('DB_POOL_SIZE', '10'))
    SQLALCHEMY_MAX_OVERFLOW: int = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600

    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_TYPE = 'filesystem'
    
    # Security
    REMEMBER_COOKIE_DURATION = timedelta(days=31)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    
    # Performance Monitoring
    SLOW_API_THRESHOLD = 0.5  # seconds
    ENABLE_PERFORMANCE_MONITORING = True
    
    # API Rate Limiting
    RATELIMIT_DEFAULT = "100 per minute"
    RATELIMIT_STORAGE_URL = REDIS_URL
    
    # Development vs Production
    DEBUG = False
    TESTING = False

    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    def __init__(self):
        """Validate required environment variables."""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required")
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL environment variable is required")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY environment variable is required")

class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'  # Use in-memory database
    PORT: int = 5050
    WTF_CSRF_ENABLED = False
    
    def __init__(self):
        """Override validation for test environment."""
        self.SECRET_KEY = 'test-secret-key'  # Safe for testing
        self.JWT_SECRET_KEY = 'test-jwt-secret'  # Safe for testing
        super().__init__()
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO: bool = True
    PORT: int = 5050
    ENABLE_QUERY_MONITORING: bool = True
    LOG_POOL_METRICS: bool = True
    REMEMBER_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    
class ProductionConfig(Config):
    """Production configuration."""
    # Ensure all required environment variables are set
    @classmethod
    def init_app(cls, app):
        """Initialize production application."""
        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)
        
        # Ensure secure configuration
        assert cls.SECRET_KEY != 'dev-key-please-change-in-production'
        assert cls.JWT_SECRET_KEY != 'jwt-dev-key-change-in-production'
        assert not cls.DEBUG
        assert not cls.TESTING
        
        # Additional production-specific initialization
        pass

config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 