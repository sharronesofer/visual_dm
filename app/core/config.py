"""
Application configuration management.
"""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path
import logging
from dotenv import load_dotenv
from datetime import timedelta

logger = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    """Redis configuration settings."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    timeout: int = 5

    @property
    def url(self) -> str:
        """Get Redis URL."""
        protocol = "rediss" if self.ssl else "redis"
        auth = f":{self.password}@" if self.password else ""
        return f"{protocol}://{auth}{self.host}:{self.port}/{self.db}"


@dataclass
class JWTConfig:
    """JWT configuration settings."""

    secret_key: str
    access_token_expires: int = 3600  # 1 hour
    refresh_token_expires: int = 2592000  # 30 days
    algorithm: str = "HS256"
    token_location: str = "headers"
    blacklist_enabled: bool = True
    blacklist_token_checks: tuple = ("access", "refresh")


@dataclass
class APIConfig:
    """API configuration settings."""

    version: str = "v1"
    title: str = "Visual DM API"
    description: str = "Game Master's Digital Assistant API"
    prefix: str = "/api"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    cors_origins: list = None
    rate_limit_default: int = 100
    rate_limit_period: int = 3600
    default_page_size: int = 20
    max_page_size: int = 100


@dataclass
class Config:
    """Main application configuration."""

    # Environment
    env: str = os.getenv("FLASK_ENV", "development")
    debug: bool = env == "development"
    testing: bool = env == "testing"

    # Application
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    project_root: Path = Path(__file__).parent.parent.parent

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5000"))
    workers: int = int(os.getenv("WORKERS", "1"))

    # Database
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{project_root}/app.db")
    echo_sql: bool = debug

    # Redis
    redis: RedisConfig = RedisConfig(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        password=os.getenv("REDIS_PASSWORD"),
        ssl=os.getenv("REDIS_SSL", "").lower() == "true",
        timeout=int(os.getenv("REDIS_TIMEOUT", "5")),
    )

    # JWT
    jwt: JWTConfig = JWTConfig(
        secret_key=os.getenv("JWT_SECRET_KEY", secret_key),
        access_token_expires=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600")),
        refresh_token_expires=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")),
        algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        blacklist_enabled=os.getenv("JWT_BLACKLIST_ENABLED", "true").lower() == "true",
    )

    # API
    api: APIConfig = APIConfig(
        version=os.getenv("API_VERSION", "v1"),
        title=os.getenv("API_TITLE", "Visual DM API"),
        description=os.getenv("API_DESCRIPTION", "Game Master's Digital Assistant API"),
        prefix=os.getenv("API_PREFIX", "/api"),
        docs_url=os.getenv("API_DOCS_URL", "/docs"),
        openapi_url=os.getenv("API_OPENAPI_URL", "/openapi.json"),
        redoc_url=os.getenv("API_REDOC_URL", "/redoc"),
        cors_origins=os.getenv("API_CORS_ORIGINS", "*").split(","),
        rate_limit_default=int(os.getenv("API_RATE_LIMIT_DEFAULT", "100")),
        rate_limit_period=int(os.getenv("API_RATE_LIMIT_PERIOD", "3600")),
        default_page_size=int(os.getenv("API_DEFAULT_PAGE_SIZE", "20")),
        max_page_size=int(os.getenv("API_MAX_PAGE_SIZE", "100")),
    )

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Mail settings
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")

    # Add admin email for scheduled reports
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", MAIL_USERNAME)

    @property
    def is_production(self) -> bool:
        """Check if environment is production."""
        return self.env == "production"

    @property
    def is_development(self) -> bool:
        """Check if environment is development."""
        return self.env == "development"

    @property
    def is_testing(self) -> bool:
        """Check if environment is testing."""
        return self.env == "testing"


# Create default configuration instance
config = Config()

# Load environment variables
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Application settings
APP_NAME: str = "Visual_DM"
DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

# Security settings
SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")

# Database settings
SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///visual_dm.db")
SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
SQLALCHEMY_ECHO: bool = DEBUG

# CORS settings
CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Rate limiting
RATE_LIMIT: str = os.getenv("RATE_LIMIT", "200 per day, 50 per hour")

# Cache settings
CACHE_TYPE: str = os.getenv("CACHE_TYPE", "simple")
CACHE_DEFAULT_TIMEOUT: int = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))

# Mail settings
MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
MAIL_USE_TLS: bool = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")

# Database Pool Configuration
SQLALCHEMY_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
SQLALCHEMY_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))
SQLALCHEMY_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
SQLALCHEMY_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))

# Redis Cache
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_KEY_PREFIX = "visual_dm:"

# HTTP Cache Configuration
HTTP_CACHE_MAX_AGE = int(os.getenv("HTTP_CACHE_MAX_AGE", "300"))  # 5 minutes default
HTTP_CACHE_COMPRESSION_MIN_SIZE = int(
    os.getenv("HTTP_CACHE_COMPRESSION_MIN_SIZE", "1024")
)  # 1KB
HTTP_CACHE_COMPRESSION_TYPES = ["gzip", "br"]  # Supported compression algorithms

# Cache Timeouts by Resource Type
HTTP_CACHE_TIMEOUTS = {
    "list": int(timedelta(minutes=5).total_seconds()),
    "detail": int(timedelta(minutes=10).total_seconds()),
    "static": int(timedelta(hours=24).total_seconds()),
    "metadata": int(timedelta(hours=1).total_seconds()),
}

# Security
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-key-please-change")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

# API Configuration
API_TITLE = "Visual DM API"
API_VERSION = "1.0"
OPENAPI_VERSION = "3.0.2"


@staticmethod
def get_config() -> Dict[str, Any]:
    """Get the current configuration as a dictionary."""
    return {
        key: value
        for key, value in Config.__dict__.items()
        if not key.startswith("_")
        and isinstance(value, (str, int, float, bool, list, dict))
    }


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    SQLALCHEMY_ECHO = True
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


class TestingConfig(Config):
    """Testing environment configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CACHE_TYPE = "simple"
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    SQLALCHEMY_ECHO = False


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(env: Optional[str] = None) -> Config:
    """Get the appropriate configuration class based on environment."""
    if env is None:
        env = os.getenv("FLASK_ENV", "development")

    return config.get(env, config["default"])


# Initialize configuration
Config.validate_config()
Config.setup_logging()

# Log configuration (with sensitive data masked)
logger.info("Application configuration loaded: %s", Config.get_sensitive_config())
