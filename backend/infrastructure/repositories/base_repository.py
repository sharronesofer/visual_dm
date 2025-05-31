"""Base repository pattern implementation for data access."""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from sqlalchemy import and_, or_, desc, asc

from backend.infrastructure.models import BaseModel

T = TypeVar('T', bound=BaseModel)  # Type must be BaseModel or subclass

logger = logging.getLogger(__name__)

class BaseRepository(Generic[T]):
    """Base repository for CRUD operations on a model.
    
    Generic repository pattern implementation that provides common
    database operations for any model type.
    """
    
    def __init__(self, model_class: Type[T], db: Session):
        """Initialize repository with model class and db session.
        
        Args:
            model_class: Model class (must be a subclass of BaseModel)
            db: SQLAlchemy database session
        """
        self.model_class = model_class
        self.db = db
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity instance if found, None otherwise
        """
        try:
            return self.db.query(self.model_class).filter(self.model_class.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model_class.__name__} by ID {id}: {e}")
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        """Get all entities with optional filtering, pagination, and sorting.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Filter conditions as keyword arguments
            
        Returns:
            List of entities matching the criteria
        """
        try:
            query = self.db.query(self.model_class)
            
            # Apply filters if provided
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        # Handle special case for list values (OR condition)
                        if isinstance(value, list):
                            filter_conditions.append(getattr(self.model_class, key).in_(value))
                        else:
                            filter_conditions.append(getattr(self.model_class, key) == value)
                
                if filter_conditions:
                    query = query.filter(and_(*filter_conditions))
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {e}")
            return []
    
    def create(self, obj_data: Dict[str, Any]) -> Optional[T]:
        """Create a new entity.
        
        Args:
            obj_data: Entity data as dictionary
            
        Returns:
            Created entity if successful, None otherwise
        """
        try:
            db_obj = self.model_class(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            return None
    
    def update(self, id: Any, obj_data: Dict[str, Any]) -> Optional[T]:
        """Update an entity by ID.
        
        Args:
            id: Entity ID
            obj_data: Updated entity data as dictionary
            
        Returns:
            Updated entity if successful, None otherwise
        """
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return None
            
            # Update entity attributes
            for key, value in obj_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model_class.__name__} with ID {id}: {e}")
            return None
    
    def delete(self, id: Any) -> bool:
        """Delete an entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            True if entity was deleted, False otherwise
        """
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model_class.__name__} with ID {id}: {e}")
            return False
    
    def count(self, **filters) -> int:
        """Count entities matching the filter criteria.
        
        Args:
            **filters: Filter conditions as keyword arguments
            
        Returns:
            Number of entities matching the criteria
        """
        try:
            query = self.db.query(self.model_class)
            
            # Apply filters if provided
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    if hasattr(self.model_class, key):
                        filter_conditions.append(getattr(self.model_class, key) == value)
                
                if filter_conditions:
                    query = query.filter(and_(*filter_conditions))
            
            return query.count()
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            return 0
    
    def exists(self, id: Any) -> bool:
        """Check if an entity with the given ID exists.
        
        Args:
            id: Entity ID
            
        Returns:
            True if entity exists, False otherwise
        """
        try:
            return self.db.query(self.model_class).filter(self.model_class.id == id).count() > 0
        except SQLAlchemyError as e:
            logger.error(f"Error checking if {self.model_class.__name__} with ID {id} exists: {e}")
            return False 