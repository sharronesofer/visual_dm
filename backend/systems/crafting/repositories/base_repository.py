"""
Base Repository

Provides common database operations for all crafting repositories.
"""

from typing import Type, TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_

from backend.infrastructure.database import BaseModel, SessionManager

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Base repository class providing common CRUD operations.
    """
    
    def __init__(self, model: Type[T]):
        """
        Initialize the repository with a specific model type.
        
        Args:
            model: The SQLAlchemy model class
        """
        self.model = model
        self._session_manager = SessionManager()
    
    def _get_session(self) -> Session:
        """Get a database session."""
        return self._session_manager.get_session()
    
    def create(self, **kwargs) -> T:
        """
        Create a new entity.
        
        Args:
            **kwargs: Fields for the new entity
            
        Returns:
            The created entity
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        session = self._get_session()
        try:
            entity = self.model(**kwargs)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        session = self._get_session()
        try:
            return session.query(self.model).filter(self.model.id == entity_id).first()
        finally:
            session.close()
    
    def find_by(self, **kwargs) -> List[T]:
        """
        Find entities by specific criteria.
        
        Args:
            **kwargs: Search criteria as field=value pairs
            
        Returns:
            List of matching entities
        """
        session = self._get_session()
        try:
            query = session.query(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.all()
        finally:
            session.close()
    
    def update(self, entity_id: str, **kwargs) -> Optional[T]:
        """
        Update an entity by ID.
        
        Args:
            entity_id: The ID of the entity to update
            **kwargs: Fields to update
            
        Returns:
            The updated entity if found, None otherwise
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        session = self._get_session()
        try:
            entity = session.query(self.model).filter(self.model.id == entity_id).first()
            if entity:
                for key, value in kwargs.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                session.commit()
                session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: The ID of the entity to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        session = self._get_session()
        try:
            entity = session.query(self.model).filter(self.model.id == entity_id).first()
            if entity:
                session.delete(entity)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close() 