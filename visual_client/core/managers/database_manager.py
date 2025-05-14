"""
Database management system.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations."""
    
    def __init__(self, db_path: str = "data/app.db"):
        """Initialize database manager.
        
        Args:
            db_path: Path to database file
        """
        try:
            # Create database directory
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            self.db_path = db_path
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            
            # Create indexes
            self._create_indexes()
            
            logger.info("Database manager initialized")
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def _create_tables(self) -> None:
        """Create database tables."""
        try:
            cursor = self.conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    metadata TEXT
                )
            """)
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create game_states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_states (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Create achievements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    achievement_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            self.conn.commit()
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "_create_tables",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def _create_indexes(self) -> None:
        """Create database indexes."""
        try:
            cursor = self.conn.cursor()
            
            # Create indexes for users table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email
                ON users (email)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username
                ON users (username)
            """)
            
            # Create indexes for sessions table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id
                ON sessions (user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_token
                ON sessions (token)
            """)
            
            # Create indexes for game_states table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_game_states_user_id
                ON game_states (user_id)
            """)
            
            # Create indexes for settings table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_settings_user_id_category
                ON settings (user_id, category)
            """)
            
            # Create indexes for achievements table
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_achievements_user_id
                ON achievements (user_id)
            """)
            
            self.conn.commit()
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "_create_indexes",
                e,
                ErrorSeverity.ERROR
            )
            raise
            
    def execute(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> sqlite3.Cursor:
        """Execute SQL query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Database cursor
        """
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "execute",
                e,
                ErrorSeverity.ERROR,
                {"query": query}
            )
            raise
            
    def fetch_one(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> Optional[sqlite3.Row]:
        """Fetch single row from database.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Single row if found, None otherwise
        """
        try:
            cursor = self.execute(query, params)
            return cursor.fetchone()
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "fetch_one",
                e,
                ErrorSeverity.ERROR,
                {"query": query}
            )
            return None
            
    def fetch_all(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict[str, Any]]] = None
    ) -> List[sqlite3.Row]:
        """Fetch all rows from database.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of rows
        """
        try:
            cursor = self.execute(query, params)
            return cursor.fetchall()
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "fetch_all",
                e,
                ErrorSeverity.ERROR,
                {"query": query}
            )
            return []
            
    def insert(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Optional[str]:
        """Insert row into database.
        
        Args:
            table: Table name
            data: Row data
            
        Returns:
            Row ID if successful, None otherwise
        """
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            cursor = self.execute(query, list(data.values()))
            self.conn.commit()
            
            return cursor.lastrowid
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "insert",
                e,
                ErrorSeverity.ERROR,
                {"table": table}
            )
            return None
            
    def update(
        self,
        table: str,
        data: Dict[str, Any],
        where: Dict[str, Any]
    ) -> bool:
        """Update rows in database.
        
        Args:
            table: Table name
            data: Updated data
            where: Where clause conditions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
            where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            
            params = list(data.values()) + list(where.values())
            self.execute(query, params)
            self.conn.commit()
            
            return True
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "update",
                e,
                ErrorSeverity.ERROR,
                {"table": table}
            )
            return False
            
    def delete(
        self,
        table: str,
        where: Dict[str, Any]
    ) -> bool:
        """Delete rows from database.
        
        Args:
            table: Table name
            where: Where clause conditions
            
        Returns:
            True if successful, False otherwise
        """
        try:
            where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
            query = f"DELETE FROM {table} WHERE {where_clause}"
            
            self.execute(query, list(where.values()))
            self.conn.commit()
            
            return True
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "delete",
                e,
                ErrorSeverity.ERROR,
                {"table": table}
            )
            return False
            
    def begin_transaction(self) -> None:
        """Begin database transaction."""
        try:
            self.conn.execute("BEGIN TRANSACTION")
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "begin_transaction",
                e,
                ErrorSeverity.ERROR
            )
            
    def commit_transaction(self) -> None:
        """Commit database transaction."""
        try:
            self.conn.commit()
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "commit_transaction",
                e,
                ErrorSeverity.ERROR
            )
            
    def rollback_transaction(self) -> None:
        """Rollback database transaction."""
        try:
            self.conn.rollback()
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "rollback_transaction",
                e,
                ErrorSeverity.ERROR
            )
            
    def cleanup(self) -> None:
        """Clean up database resources."""
        try:
            self.conn.close()
            logger.info("Database manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "DatabaseManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 