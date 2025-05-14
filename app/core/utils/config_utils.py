"""
Configuration utilities for the application.
Provides configuration loading and management functions.
"""

import os
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig(BaseModel):
    """Database configuration settings."""
    host: str = Field("localhost", env="DB_HOST")
    port: int = Field(5432, env="DB_PORT")
    user: str = Field("postgres", env="DB_USER")
    password: str = Field("postgres", env="DB_PASSWORD")
    name: str = Field("visual_dm", env="DB_NAME")
    pool_size: int = Field(5, env="DB_POOL_SIZE")
    max_overflow: int = Field(10, env="DB_MAX_OVERFLOW")
    
    def get_database_url(self) -> str:
        """Get the database connection URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

class SecurityConfig(BaseModel):
    """Security configuration settings."""
    secret_key: str = Field("dev-secret-key", env="SECRET_KEY")
    algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    password_salt_rounds: int = Field(12, env="PASSWORD_SALT_ROUNDS")

class LoggingConfig(BaseModel):
    """Logging configuration settings."""
    level: str = Field("INFO", env="LOG_LEVEL")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    file_path: Optional[str] = Field(None, env="LOG_FILE_PATH")
    max_bytes: int = Field(10485760, env="LOG_MAX_BYTES")  # 10MB
    backup_count: int = Field(5, env="LOG_BACKUP_COUNT")

class APIConfig(BaseModel):
    """API configuration settings."""
    title: str = Field("Game API", env="API_TITLE")
    version: str = Field("1.0.0", env="API_VERSION")
    description: str = Field("Game API Documentation", env="API_DESCRIPTION")
    docs_url: str = Field("/docs", env="API_DOCS_URL")
    redoc_url: str = Field("/redoc", env="API_REDOC_URL")
    debug: bool = Field(False, env="API_DEBUG")
    port: int = Field(5050, env="API_PORT")

class Config(BaseModel):
    """Main configuration model."""
    database: DatabaseConfig
    security: SecurityConfig
    logging: LoggingConfig
    api: APIConfig

def load_config() -> Config:
    """Load and validate configuration from environment variables."""
    return Config(
        database=DatabaseConfig(),
        security=SecurityConfig(),
        logging=LoggingConfig(),
        api=APIConfig()
    )

def get_config() -> Config:
    """Get the application configuration."""
    if not hasattr(get_config, "config"):
        get_config.config = load_config()
    return get_config.config

def get_database_config() -> DatabaseConfig:
    """Get the database configuration."""
    return get_config().database

def get_security_config() -> SecurityConfig:
    """Get the security configuration."""
    return get_config().security

def get_logging_config() -> LoggingConfig:
    """Get the logging configuration."""
    return get_config().logging

def get_api_config() -> APIConfig:
    """Get the API configuration."""
    return get_config().api

def get_env_variable(name: str, default: Any = None) -> Any:
    """Get an environment variable with optional default value."""
    return os.getenv(name, default)

def is_debug_mode() -> bool:
    """Check if the application is in debug mode."""
    return get_api_config().debug

def get_secret_key() -> str:
    """Get the application secret key."""
    return get_security_config().secret_key

def get_database_url() -> str:
    """Get the database connection URL."""
    db_config = get_database_config()
    return f"postgresql://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.name}"

def validate_config(config: Dict[str, Any]) -> None:
    """Validate the application configuration"""
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = [var for var in required_vars if not config.get(var)]
    
    if missing_vars:
        raise ConfigError(f"Missing required environment variables: {missing_vars}")
    
    # Validate database URL format
    if not config['DATABASE_URL'].startswith(('postgresql://', 'sqlite://')):
        raise ConfigError("Invalid DATABASE_URL format")
    
    # Validate port number
    if not 0 <= config['FLASK_PORT'] <= 65535:
        raise ConfigError(f"Invalid port number: {config['FLASK_PORT']}")
    
    # Validate environment
    if config['FLASK_ENV'] not in ['development', 'production', 'testing']:
        raise ConfigError(f"Invalid FLASK_ENV: {config['FLASK_ENV']}")
    
    # Validate log level
    valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if config['LOG_LEVEL'] not in valid_log_levels:
        raise ConfigError(f"Invalid LOG_LEVEL: {config['LOG_LEVEL']}")
    
    # Validate database connection settings
    if config['MAX_DB_CONNECTIONS'] < 1:
        raise ConfigError("MAX_DB_CONNECTIONS must be at least 1")
    
    if config['DB_POOL_RECYCLE'] < 0:
        raise ConfigError("DB_POOL_RECYCLE must be non-negative")
    
    if config['DB_POOL_TIMEOUT'] < 0:
        raise ConfigError("DB_POOL_TIMEOUT must be non-negative")
    
    if config['DB_POOL_SIZE'] < 1:
        raise ConfigError("DB_POOL_SIZE must be at least 1")
    
    logger.info("Configuration validation successful")

# Create and export the config instance
config = get_config()

__all__ = [
    'Config',
    'config',
    'get_config',
    'get_database_config',
    'get_security_config',
    'get_logging_config',
    'get_api_config',
    'get_env_variable',
    'is_debug_mode',
    'get_secret_key',
    'get_database_url',
    'validate_config'
]

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///visual_dm.db'
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

# Configuration dictionary
Config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 