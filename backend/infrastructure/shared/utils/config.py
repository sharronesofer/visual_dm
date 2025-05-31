"""
Shared configuration module for all backend systems.
Provides centralized configuration management.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    database_url: str = "sqlite:///./visual_dm.db"
    echo_sql: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600

@dataclass
class AppConfig:
    """Application configuration settings."""
    debug: bool = False
    testing: bool = False
    secret_key: str = "dev-secret-key"
    cors_origins: list = None
    
    # Database settings
    database_url: str = "sqlite:///./visual_dm.db"
    echo_sql: bool = False
    
    # SQLAlchemy pool settings
    SQLALCHEMY_POOL_SIZE: int = 5
    SQLALCHEMY_MAX_OVERFLOW: int = 10
    SQLALCHEMY_POOL_TIMEOUT: int = 30
    SQLALCHEMY_POOL_RECYCLE: int = 3600
    
    # API settings
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    # Security settings
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # External service settings
    openai_api_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:3000", "http://localhost:8080"]

def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        testing=os.getenv("TESTING", "false").lower() == "true",
        secret_key=os.getenv("SECRET_KEY", "dev-secret-key"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./visual_dm.db"),
        echo_sql=os.getenv("ECHO_SQL", "false").lower() == "true",
        SQLALCHEMY_POOL_SIZE=int(os.getenv("SQLALCHEMY_POOL_SIZE", "5")),
        SQLALCHEMY_MAX_OVERFLOW=int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", "10")),
        SQLALCHEMY_POOL_TIMEOUT=int(os.getenv("SQLALCHEMY_POOL_TIMEOUT", "30")),
        SQLALCHEMY_POOL_RECYCLE=int(os.getenv("SQLALCHEMY_POOL_RECYCLE", "3600")),
        api_prefix=os.getenv("API_PREFIX", "/api/v1"),
        docs_url=os.getenv("DOCS_URL", "/docs"),
        redoc_url=os.getenv("REDOC_URL", "/redoc"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
    )

# Global configuration instance
config = load_config()

# Backwards compatibility
DATABASE_URL = config.database_url
DEBUG = config.debug
SECRET_KEY = config.secret_key 