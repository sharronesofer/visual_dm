"""
Base repository for the magic system.

This module contains the base repository class for database operations.
"""

from sqlalchemy.orm import Session

class BaseRepository:
    """Base repository for common operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the repository.
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    def commit(self):
        """Commit changes to the database."""
        self.db.commit()
    
    def rollback(self):
        """Rollback changes."""
        self.db.rollback() 