"""
Economy Database Service - Database session management and utilities for the economy system.

This service provides database session management, connection handling, and database
utilities specifically for the economy system.
"""

import logging
from typing import Optional, Generator, Any, Dict, List
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.pool import StaticPool

# Set up logging
logger = logging.getLogger(__name__)

class EconomyDatabaseService:
    """
    Database service for the economy system.
    
    Provides database session management, connection handling, and utilities
    for economy-related database operations.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize the database service.
        
        Args:
            database_url: Database connection URL. If None, uses in-memory SQLite for testing.
        """
        self.database_url = database_url or "sqlite:///:memory:"
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the database engine and session factory."""
        try:
            # Configure engine based on database type
            if self.database_url.startswith("sqlite"):
                # SQLite configuration
                self.engine = create_engine(
                    self.database_url,
                    poolclass=StaticPool,
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 20
                    },
                    echo=False  # Set to True for SQL debugging
                )
            else:
                # PostgreSQL or other database configuration
                self.engine = create_engine(
                    self.database_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,
                    echo=False  # Set to True for SQL debugging
                )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Economy database service initialized with {self.database_url}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
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
    
    def create_tables(self):
        """
        Create all economy system tables.
        
        Note: This should typically be done via migrations in production.
        """
        try:
            from backend.systems.economy.models import (
                Resource, Market, TradeRoute, CommodityFuture
            )
            from backend.infrastructure.database import Base
            
            Base.metadata.create_all(bind=self.engine)
            logger.info("Economy system tables created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    def drop_tables(self):
        """
        Drop all economy system tables.
        
        Warning: This will delete all data!
        """
        try:
            from backend.systems.economy.models import (
                Resource, Market, TradeRoute, CommodityFuture
            )
            from backend.infrastructure.database import Base
            
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("Economy system tables dropped")
            
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise
    
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
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a specific table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table information
        """
        try:
            with self.get_session() as session:
                # Get table schema information
                if self.database_url.startswith("sqlite"):
                    result = session.execute(text(f"PRAGMA table_info({table_name})"))
                    columns = [dict(zip(result.keys(), row)) for row in result.fetchall()]
                    
                    # Get row count
                    count_result = session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                    row_count = count_result.fetchone()[0]
                    
                else:
                    # PostgreSQL
                    result = session.execute(text("""
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns
                        WHERE table_name = :table_name
                        ORDER BY ordinal_position
                    """), {"table_name": table_name})
                    columns = [dict(zip(result.keys(), row)) for row in result.fetchall()]
                    
                    # Get row count
                    count_result = session.execute(text(f"SELECT COUNT(*) as count FROM {table_name}"))
                    row_count = count_result.fetchone()[0]
                
                return {
                    "table_name": table_name,
                    "columns": columns,
                    "row_count": row_count
                }
                
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            return {"error": str(e)}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get overall database statistics for economy tables.
        
        Returns:
            Dictionary with database statistics
        """
        economy_tables = [
            "resources", "markets", "trade_routes", "commodity_futures",
            "economic_transactions", "price_history", "economic_events"
        ]
        
        stats = {
            "connection_status": self.test_connection(),
            "database_url": self.database_url.split("@")[-1] if "@" in self.database_url else self.database_url,
            "tables": {}
        }
        
        for table in economy_tables:
            try:
                table_info = self.get_table_info(table)
                stats["tables"][table] = {
                    "exists": "error" not in table_info,
                    "row_count": table_info.get("row_count", 0),
                    "column_count": len(table_info.get("columns", []))
                }
            except Exception as e:
                stats["tables"][table] = {
                    "exists": False,
                    "error": str(e)
                }
        
        return stats
    
    def backup_data(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Backup data from a specific table.
        
        Args:
            table_name: Name of the table to backup
            
        Returns:
            List of all rows as dictionaries
        """
        try:
            return self.execute_raw_sql(f"SELECT * FROM {table_name}")
        except Exception as e:
            logger.error(f"Failed to backup table {table_name}: {e}")
            return []
    
    def restore_data(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """
        Restore data to a specific table.
        
        Args:
            table_name: Name of the table to restore to
            data: List of row dictionaries to insert
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_session() as session:
                # Clear existing data
                session.execute(text(f"DELETE FROM {table_name}"))
                
                # Insert new data
                for row in data:
                    columns = ", ".join(row.keys())
                    placeholders = ", ".join([f":{key}" for key in row.keys()])
                    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    session.execute(text(sql), row)
                
                session.commit()
                logger.info(f"Restored {len(data)} rows to {table_name}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to restore data to {table_name}: {e}")
            return False
    
    def optimize_database(self):
        """
        Optimize the database (vacuum, analyze, etc.).
        """
        try:
            with self.get_session() as session:
                if self.database_url.startswith("sqlite"):
                    session.execute(text("VACUUM"))
                    session.execute(text("ANALYZE"))
                else:
                    session.execute(text("VACUUM ANALYZE"))
                
                logger.info("Database optimization completed")
                
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
    
    def close(self):
        """Close the database engine and all connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Economy database service closed")

# Global database service instance
_db_service: Optional[EconomyDatabaseService] = None

def get_database_service(database_url: Optional[str] = None) -> EconomyDatabaseService:
    """
    Get the global database service instance.
    
    Args:
        database_url: Database connection URL (only used on first call)
        
    Returns:
        EconomyDatabaseService instance
    """
    global _db_service
    if _db_service is None:
        _db_service = EconomyDatabaseService(database_url)
    return _db_service

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