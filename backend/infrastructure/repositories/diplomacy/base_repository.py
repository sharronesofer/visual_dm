"""
Base Repository for Diplomacy System

This module provides the base repository interface that all diplomacy
repositories inherit from. It abstracts the infrastructure layer and
provides common functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any, TypeVar, Generic
from uuid import UUID
from sqlalchemy.orm import Session

from backend.infrastructure.repositories.diplomacy_repository import DiplomacyRepository

T = TypeVar('T')

class BaseDiplomacyRepository(ABC, Generic[T]):
    """
    Base repository class for diplomacy entities.
    
    This class provides a common interface for all diplomacy repositories
    and delegates to the infrastructure DiplomacyRepository while adding
    diplomacy-specific abstractions.
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize the repository with an optional database session.
        
        Args:
            db_session: Optional SQLAlchemy session for database operations
        """
        self.db_session = db_session
        self._infrastructure_repo = DiplomacyRepository()
    
    @property
    def infrastructure_repo(self) -> DiplomacyRepository:
        """Get the underlying infrastructure repository."""
        return self._infrastructure_repo
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod 
    def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get an entity by its ID."""
        pass
    
    @abstractmethod
    def update(self, entity_id: UUID, updates: Dict[str, Any]) -> Optional[T]:
        """Update an entity with new values."""
        pass
    
    @abstractmethod
    def delete(self, entity_id: UUID) -> bool:
        """Delete an entity by its ID."""
        pass
    
    @abstractmethod
    def list_all(self, **filters) -> List[T]:
        """List all entities with optional filters."""
        pass
    
    def get_session(self) -> Optional[Session]:
        """Get the current database session."""
        return self.db_session
    
    def set_session(self, session: Session) -> None:
        """Set the database session for operations."""
        self.db_session = session 