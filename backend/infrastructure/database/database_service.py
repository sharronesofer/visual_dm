"""
Infrastructure Database Service

Centralized database session management, connection handling, and utilities
for all systems.
"""

import logging
from typing import Optional, Generator, Any, Dict, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.pool import StaticPool

from .config import get_database_url, get_database_config, validate_database_url

# Set up logging
logger = logging.getLogger(__name__)

class DatabaseService:
    """
    Database service for all systems.
    
    Provides database session management, connection handling, and utilities
    for all database operations across systems.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database service.
        
        Args:
            database_url: Database connection URL. If None, uses configured URL.
        """
        self.database_url = database_url or get_database_url()
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the database engine and session factory."""
        try:
            # Validate URL first
            if not validate_database_url(self.database_url):
                raise ValueError(f"Invalid database URL: {self.database_url}")
            
            # Get configuration for this database type
            config = get_database_config()
            
            # Create engine with appropriate configuration
            engine_kwargs = {
                "echo": config.get("echo", False),
                "pool_pre_ping": config.get("pool_pre_ping", True)
            }
            
            # Add database-specific configurations
            if "poolclass" in config:
                engine_kwargs["poolclass"] = getattr(__import__("sqlalchemy.pool"), config["poolclass"])
            
            if "connect_args" in config:
                engine_kwargs["connect_args"] = config["connect_args"]
            
            if "pool_size" in config:
                engine_kwargs["pool_size"] = config["pool_size"]
                
            if "max_overflow" in config:
                engine_kwargs["max_overflow"] = config["max_overflow"]
                
            if "pool_timeout" in config:
                engine_kwargs["pool_timeout"] = config["pool_timeout"]
                
            if "pool_recycle" in config:
                engine_kwargs["pool_recycle"] = config["pool_recycle"]
            
            self.engine = create_engine(self.database_url, **engine_kwargs)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Database service initialized successfully with {self._get_safe_url()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _get_safe_url(self) -> str:
        """Get database URL with password masked for logging."""
        try:
            from urllib.parse import urlparse, urlunparse
            parsed = urlparse(self.database_url)
            
            if parsed.password:
                # Replace password with asterisks
                netloc = f"{parsed.username}:***@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                
                safe_parsed = parsed._replace(netloc=netloc)
                return urlunparse(safe_parsed)
            
            return self.database_url
        except:
            return "database_url_parsing_failed"

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get a database session with automatic cleanup.
        
        Yields:
            SQLAlchemy session
            
        Example:
            with db_service.get_session() as session:
                resource = session.query(Resource).first()
        """
        if not self.SessionLocal:
            raise RuntimeError("Database service not properly initialized")
            
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def create_session(self) -> Session:
        """
        Create a new database session.
        
        Note: Caller is responsible for closing the session.
        
        Returns:
            SQLAlchemy session
        """
        if not self.SessionLocal:
            raise RuntimeError("Database service not properly initialized")
            
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """
        Test the database connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute raw SQL and return results.
        
        Args:
            sql: SQL query string
            params: Optional parameters for the query
            
        Returns:
            List of result dictionaries
        """
        try:
            with self.get_session() as session:
                result = session.execute(text(sql), params or {})
                
                # Handle different result types
                if result.returns_rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                else:
                    return [{"affected_rows": result.rowcount}]
                    
        except Exception as e:
            logger.error(f"Raw SQL execution failed: {e}")
            raise
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about the database engine.
        
        Returns:
            Dictionary with engine information
        """
        if not self.engine:
            return {"status": "not_initialized"}
        
        try:
            return {
                "status": "initialized",
                "url": self._get_safe_url(),
                "driver": self.engine.driver,
                "dialect": str(self.engine.dialect),
                "pool_size": getattr(self.engine.pool, 'size', 'unknown'),
                "checked_out": getattr(self.engine.pool, 'checkedout', 'unknown'),
                "overflow": getattr(self.engine.pool, 'overflow', 'unknown'),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def close(self):
        """Close the database engine and all connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database service closed")

# Global database service instance
_db_service: Optional[DatabaseService] = None

def get_database_service(database_url: Optional[str] = None) -> DatabaseService:
    """
    Get the global database service instance.
    
    Args:
        database_url: Database connection URL (only used on first call)
        
    Returns:
        DatabaseService instance
    """
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService(database_url)
    return _db_service

def reset_database_service():
    """Reset the global database service (useful for testing)."""
    global _db_service
    if _db_service:
        _db_service.close()
    _db_service = None

def get_db() -> Session:
    """
    Get a database session for dependency injection.
    
    Returns:
        SQLAlchemy session
    """
    db_service = get_database_service()
    return db_service.create_session()

# Context manager for database sessions
@contextmanager
def database_session(database_url: Optional[str] = None) -> Generator[Session, None, None]:
    """
    Context manager for database sessions.
    
    Args:
        database_url: Optional database URL
        
    Yields:
        SQLAlchemy session
    """
    db_service = get_database_service(database_url)
    with db_service.get_session() as session:
        yield session 