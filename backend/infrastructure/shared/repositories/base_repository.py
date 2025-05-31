"""
Base repository for all systems.

Provides common database operations and patterns for all entities.
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.database import Base
from backend.infrastructure.shared.exceptions import (
    RepositoryError,
    EntityNotFoundError,
    EntityConflictError
)

logger = logging.getLogger(__name__)

# Type variables for generic repository
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType]):
    """
    Base repository class providing common CRUD operations.
    
    This class provides a consistent interface for database operations
    across all entities in the system.
    """
    
    def __init__(self, db_session: Session, model: Type[ModelType]):
        """
        Initialize repository with database session and model.
        
        Args:
            db_session: Database session
            model: SQLAlchemy model class
        """
        self.db = db_session
        self.model = model
        
    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        try:
            return self.db.query(self.model).filter(
                and_(
                    self.model.id == id,
                    getattr(self.model, 'is_active', True) == True
                )
            ).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} {id}: {str(e)}")
            raise RepositoryError(f"Failed to get {self.model.__name__}: {str(e)}")
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Tuple[List[ModelType], int]:
        """
        Get multiple entities with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field filters
            order_by: Field name to order by
            order_desc: Whether to order in descending order
            
        Returns:
            Tuple of (entities, total_count)
        """
        try:
            query = self.db.query(self.model)
            
            # Filter active records if the model has is_active field
            if hasattr(self.model, 'is_active'):
                query = query.filter(self.model.is_active == True)
            
            # Apply filters
            if filters:
                for field_name, field_value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        if isinstance(field_value, list):
                            query = query.filter(field.in_(field_value))
                        elif isinstance(field_value, str) and field_value.startswith('%') and field_value.endswith('%'):
                            query = query.filter(field.ilike(field_value))
                        else:
                            query = query.filter(field == field_value)
            
            # Get total count before pagination
            total = query.count()
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_field))
                else:
                    query = query.order_by(asc(order_field))
            elif hasattr(self.model, 'created_at'):
                query = query.order_by(desc(self.model.created_at))
            
            # Apply pagination
            entities = query.offset(skip).limit(limit).all()
            
            return entities, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to get multiple {self.model.__name__}: {str(e)}")
    
    def create(self, entity_data: Dict[str, Any]) -> ModelType:
        """
        Create a new entity.
        
        Args:
            entity_data: Data for entity creation
            
        Returns:
            Created entity
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            # Set timestamps if the model supports them
            now = datetime.utcnow()
            if hasattr(self.model, 'created_at'):
                entity_data['created_at'] = now
            if hasattr(self.model, 'updated_at'):
                entity_data['updated_at'] = now
            if hasattr(self.model, 'is_active') and 'is_active' not in entity_data:
                entity_data['is_active'] = True
            
            db_obj = self.model(**entity_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.debug(f"Created {self.model.__name__} with id {db_obj.id}")
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to create {self.model.__name__}: {str(e)}")
    
    def update(self, entity: ModelType, update_data: Dict[str, Any]) -> ModelType:
        """
        Update an existing entity.
        
        Args:
            entity: Existing entity from database
            update_data: Data to update
            
        Returns:
            Updated entity
        """
        try:
            # Set update timestamp if the model supports it
            if hasattr(self.model, 'updated_at'):
                update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
            
            self.db.commit()
            self.db.refresh(entity)
            
            logger.debug(f"Updated {self.model.__name__} {entity.id}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to update {self.model.__name__}: {str(e)}")
    
    def delete(self, id: UUID, soft_delete: bool = True) -> bool:
        """
        Delete entity (soft delete by default).
        
        Args:
            id: Entity ID to delete
            soft_delete: Whether to perform soft delete (set is_active=False)
            
        Returns:
            True if deleted successfully
        """
        try:
            entity = self.get_by_id(id)
            if not entity:
                return False
            
            if soft_delete and hasattr(entity, 'is_active'):
                entity.is_active = False
                if hasattr(entity, 'updated_at'):
                    entity.updated_at = datetime.utcnow()
                self.db.commit()
            else:
                self.db.delete(entity)
                self.db.commit()
            
            logger.debug(f"Deleted {self.model.__name__} {id} (soft={soft_delete})")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} {id}: {str(e)}")
            raise RepositoryError(f"Failed to delete {self.model.__name__}: {str(e)}")
    
    def exists(self, id: UUID) -> bool:
        """
        Check if entity exists.
        
        Args:
            id: Entity ID
            
        Returns:
            True if entity exists and is active
        """
        try:
            query = self.db.query(self.model.id).filter(self.model.id == id)
            if hasattr(self.model, 'is_active'):
                query = query.filter(self.model.is_active == True)
            return query.first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} {id}: {str(e)}")
            raise RepositoryError(f"Failed to check existence: {str(e)}")
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filters.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Count of entities matching filters
        """
        try:
            query = self.db.query(func.count(self.model.id))
            
            # Filter active records if the model has is_active field
            if hasattr(self.model, 'is_active'):
                query = query.filter(self.model.is_active == True)
            
            # Apply filters
            if filters:
                for field_name, field_value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        query = query.filter(field == field_value)
            
            return query.scalar()
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to count {self.model.__name__}: {str(e)}")
    
    def get_by_field(self, field_name: str, field_value: Any) -> Optional[ModelType]:
        """
        Get entity by a specific field.
        
        Args:
            field_name: Name of the field
            field_value: Value to search for
            
        Returns:
            Entity if found, None otherwise
        """
        try:
            query = self.db.query(self.model)
            
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                query = query.filter(field == field_value)
            else:
                raise ValueError(f"Field {field_name} not found on {self.model.__name__}")
            
            # Filter active records if the model has is_active field
            if hasattr(self.model, 'is_active'):
                query = query.filter(self.model.is_active == True)
            
            return query.first()
            
        except (AttributeError, SQLAlchemyError) as e:
            logger.error(f"Error getting {self.model.__name__} by {field_name}: {str(e)}")
            raise RepositoryError(f"Failed to get {self.model.__name__} by {field_name}: {str(e)}")
    
    def bulk_create(self, entities_data: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple entities in a single transaction.
        
        Args:
            entities_data: List of entity data dictionaries
            
        Returns:
            List of created entities
        """
        try:
            entities = []
            now = datetime.utcnow()
            
            for entity_data in entities_data:
                # Set timestamps if the model supports them
                if hasattr(self.model, 'created_at'):
                    entity_data['created_at'] = now
                if hasattr(self.model, 'updated_at'):
                    entity_data['updated_at'] = now
                if hasattr(self.model, 'is_active') and 'is_active' not in entity_data:
                    entity_data['is_active'] = True
                
                entities.append(self.model(**entity_data))
            
            self.db.add_all(entities)
            self.db.commit()
            
            # Refresh all entities
            for entity in entities:
                self.db.refresh(entity)
            
            logger.debug(f"Bulk created {len(entities)} {self.model.__name__} entities")
            return entities
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to bulk create {self.model.__name__}: {str(e)}") 