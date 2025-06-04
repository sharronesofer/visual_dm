"""
Database Configuration

Centralized database configuration for all environments.
Handles SQLALCHEMY_DATABASE_URI and provides proper session setup.
"""

import os
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Environment variables for database configuration
DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    os.getenv("DATABASE_URL", "sqlite:///dreamforge.db")
)

# Development defaults
DEFAULT_SQLITE_DB = "sqlite:///dreamforge.db"
DEFAULT_POSTGRES_DB = "postgresql://user:password@localhost:5432/dreamforge"

def get_database_url() -> str:
    """
    Get the database URL with proper fallbacks.
    
    Priority:
    1. SQLALCHEMY_DATABASE_URI environment variable
    2. DATABASE_URL environment variable  
    3. Default SQLite database for development
    
    Returns:
        Database URL string
    """
    # Check environment variables
    db_url = os.getenv("SQLALCHEMY_DATABASE_URI")
    if db_url:
        logger.info("Using SQLALCHEMY_DATABASE_URI")
        return db_url
    
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        logger.info("Using DATABASE_URL")
        return db_url
    
    # Development environment detection
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment in ["production", "prod"]:
        logger.warning("Production environment detected but no DATABASE_URL configured!")
        # In production, require explicit database configuration
        raise ValueError(
            "Production environment requires SQLALCHEMY_DATABASE_URI or DATABASE_URL "
            "environment variable to be set"
        )
    
    elif environment in ["testing", "test"]:
        logger.info("Using in-memory SQLite for testing")
        return "sqlite:///:memory:"
    
    else:
        # Development environment
        logger.info("Using default SQLite database for development")
        return DEFAULT_SQLITE_DB

def get_database_config() -> dict:
    """
    Get database configuration parameters based on database type.
    
    Returns:
        Dictionary with database configuration parameters
    """
    db_url = get_database_url()
    parsed_url = urlparse(db_url)
    
    config = {
        "url": db_url,
        "echo": False,  # Set to True for SQL debugging
        "pool_pre_ping": True,
    }
    
    if parsed_url.scheme.startswith("sqlite"):
        # SQLite configuration
        config.update({
            "poolclass": "StaticPool",
            "connect_args": {
                "check_same_thread": False,
                "timeout": 30
            }
        })
        
        # Create directory for file-based SQLite if needed
        if not db_url.endswith(":memory:") and "/" in db_url:
            import pathlib
            db_path = pathlib.Path(db_url.replace("sqlite:///", ""))
            db_path.parent.mkdir(parents=True, exist_ok=True)
    
    elif parsed_url.scheme.startswith("postgresql"):
        # PostgreSQL configuration
        config.update({
            "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
            "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
            "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
        })
    
    # Enable SQL debugging in development
    if os.getenv("ENVIRONMENT", "development").lower() == "development":
        config["echo"] = os.getenv("DB_DEBUG", "false").lower() == "true"
    
    return config

def validate_database_url(db_url: str) -> bool:
    """
    Validate database URL format.
    
    Args:
        db_url: Database URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(db_url)
        
        # Check for required components
        if not parsed.scheme:
            logger.error("Database URL missing scheme")
            return False
        
        # Validate supported schemes
        if parsed.scheme not in ["sqlite", "postgresql", "postgresql+psycopg2", "mysql", "mysql+pymysql"]:
            logger.error(f"Unsupported database scheme: {parsed.scheme}")
            return False
        
        # For non-SQLite databases, require host
        if not parsed.scheme.startswith("sqlite") and not parsed.hostname:
            logger.error("Database URL missing hostname")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Invalid database URL format: {e}")
        return False

def get_alembic_database_url() -> str:
    """
    Get database URL for Alembic migrations.
    
    Some databases need special handling for migrations.
    
    Returns:
        Database URL for Alembic
    """
    db_url = get_database_url()
    
    # For SQLite, ensure we use absolute path for migrations
    if db_url.startswith("sqlite:///") and not db_url.endswith(":memory:"):
        # Convert relative path to absolute
        import pathlib
        db_path = pathlib.Path(db_url.replace("sqlite:///", ""))
        if not db_path.is_absolute():
            db_path = pathlib.Path.cwd() / db_path
        return f"sqlite:///{db_path.absolute()}"
    
    return db_url

def get_test_database_url() -> str:
    """
    Get database URL for testing.
    
    Uses in-memory SQLite by default for fast tests.
    Can be overridden with TEST_DATABASE_URL environment variable.
    
    Returns:
        Test database URL
    """
    return os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

class DatabaseConfig:
    """Database configuration class for easier access."""
    
    def __init__(self):
        self.url = get_database_url()
        self.config = get_database_config()
        self.is_sqlite = self.url.startswith("sqlite")
        self.is_postgresql = self.url.startswith("postgresql")
        self.is_memory = ":memory:" in self.url
        self.is_valid = validate_database_url(self.url)
    
    def __repr__(self):
        return f"DatabaseConfig(url='{self.url}', valid={self.is_valid})"

# Global database configuration instance
database_config = DatabaseConfig()

# Export commonly used values
__all__ = [
    "DATABASE_URL",
    "get_database_url",
    "get_database_config", 
    "validate_database_url",
    "get_alembic_database_url",
    "get_test_database_url",
    "DatabaseConfig",
    "database_config"
] 