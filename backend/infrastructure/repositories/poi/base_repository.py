"""
Base repository for POI system.

Provides common database operations and patterns for POI-related entities.
"""

import logging
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy import and_, or_, desc, asc, func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.infrastructure.database import Base, get_db
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


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository class providing common CRUD operations.
    
    This class provides a consistent interface for database operations
    across all POI-related entities.
    """
    
    def __init__(self, model: Type[ModelType], db_session: Session):
        """
        Initialize repository with model and database session.
        
        Args:
            model: SQLAlchemy model class
            db_session: Database session
        """
        self.model = model
        self.db = db_session
        
    def create(self, *, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """
        Create a new entity.
        
        Args:
            obj_in: Creation schema/data
            **kwargs: Additional fields to set
            
        Returns:
            Created entity
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict()
            else:
                obj_data = obj_in
                
            # Add any additional kwargs
            obj_data.update(kwargs)
            
            # Set timestamps
            obj_data['created_at'] = datetime.utcnow()
            obj_data['updated_at'] = datetime.utcnow()
            
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.debug(f"Created {self.model.__name__} with id {db_obj.id}")
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to create {self.model.__name__}: {str(e)}")
    
    def get(self, id: UUID) -> Optional[ModelType]:
        """
        Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} {id}: {str(e)}")
            raise RepositoryError(f"Failed to get {self.model.__name__}: {str(e)}")
    
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
            field = getattr(self.model, field_name)
            return self.db.query(self.model).filter(field == field_value).first()
        except (AttributeError, SQLAlchemyError) as e:
            logger.error(f"Error getting {self.model.__name__} by {field_name}: {str(e)}")
            raise RepositoryError(f"Failed to get {self.model.__name__} by {field_name}: {str(e)}")
    
    def get_multiple(
        self,
        *,
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
            
            # Apply pagination
            entities = query.offset(skip).limit(limit).all()
            
            return entities, total
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting multiple {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to get multiple {self.model.__name__}: {str(e)}")
    
    def update(self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Update an existing entity.
        
        Args:
            db_obj: Existing entity from database
            obj_in: Update schema/data
            
        Returns:
            Updated entity
        """
        try:
            if hasattr(obj_in, 'dict'):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in
            
            # Set update timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.debug(f"Updated {self.model.__name__} with id {db_obj.id}")
            return db_obj
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to update {self.model.__name__}: {str(e)}")
    
    def delete(self, *, id: UUID, soft_delete: bool = True) -> bool:
        """
        Delete an entity (soft or hard delete).
        
        Args:
            id: Entity ID
            soft_delete: Whether to perform soft delete (set is_active=False)
            
        Returns:
            True if deleted successfully
        """
        try:
            db_obj = self.get(id)
            if not db_obj:
                raise EntityNotFoundError(f"{self.model.__name__} with id {id} not found")
            
            if soft_delete and hasattr(db_obj, 'is_active'):
                db_obj.is_active = False
                db_obj.updated_at = datetime.utcnow()
                self.db.commit()
            else:
                self.db.delete(db_obj)
                self.db.commit()
            
            logger.debug(f"Deleted {self.model.__name__} with id {id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to delete {self.model.__name__}: {str(e)}")
    
    def exists(self, id: UUID) -> bool:
        """
        Check if entity exists.
        
        Args:
            id: Entity ID
            
        Returns:
            True if entity exists
        """
        try:
            return self.db.query(self.model.id).filter(self.model.id == id).first() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to check existence: {str(e)}")
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count entities with optional filters.
        
        Args:
            filters: Dictionary of field filters
            
        Returns:
            Count of entities
        """
        try:
            query = self.db.query(self.model)
            
            if filters:
                for field_name, field_value in filters.items():
                    if hasattr(self.model, field_name):
                        field = getattr(self.model, field_name)
                        query = query.filter(field == field_value)
            
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to count {self.model.__name__}: {str(e)}")
    
    def bulk_create(self, *, objects: List[CreateSchemaType]) -> List[ModelType]:
        """
        Create multiple entities in bulk.
        
        Args:
            objects: List of creation schemas/data
            
        Returns:
            List of created entities
        """
        try:
            db_objects = []
            for obj_in in objects:
                if hasattr(obj_in, 'dict'):
                    obj_data = obj_in.dict()
                else:
                    obj_data = obj_in
                    
                obj_data['created_at'] = datetime.utcnow()
                obj_data['updated_at'] = datetime.utcnow()
                
                db_objects.append(self.model(**obj_data))
            
            self.db.add_all(db_objects)
            self.db.commit()
            
            for db_obj in db_objects:
                self.db.refresh(db_obj)
            
            logger.debug(f"Bulk created {len(db_objects)} {self.model.__name__} entities")
            return db_objects
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to bulk create {self.model.__name__}: {str(e)}")


class PoiBaseRepository(BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Extended base repository for POI-specific operations.
    
    Adds POI-specific query methods and utilities.
    """
    
    def get_active(self, id: UUID) -> Optional[ModelType]:
        """
        Get active entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Active entity if found, None otherwise
        """
        try:
            query = self.db.query(self.model).filter(self.model.id == id)
            if hasattr(self.model, 'is_active'):
                query = query.filter(self.model.is_active == True)
            return query.first()
        except SQLAlchemyError as e:
            logger.error(f"Error getting active {self.model.__name__}: {str(e)}")
            raise RepositoryError(f"Failed to get active {self.model.__name__}: {str(e)}")
    
    def get_by_location(
        self, 
        *, 
        x: float, 
        y: float, 
        radius: Optional[float] = None
    ) -> List[ModelType]:
        """
        Get entities by location (if model has location fields).
        
        Args:
            x: X coordinate
            y: Y coordinate
            radius: Search radius (optional)
            
        Returns:
            List of entities within location criteria
        """
        try:
            if not (hasattr(self.model, 'location_x') and hasattr(self.model, 'location_y')):
                return []
            
            query = self.db.query(self.model)
            
            if radius:
                # Use distance calculation for radius search
                distance_expr = func.sqrt(
                    func.pow(self.model.location_x - x, 2) + 
                    func.pow(self.model.location_y - y, 2)
                )
                query = query.filter(distance_expr <= radius)
            else:
                # Exact location match
                query = query.filter(
                    and_(
                        self.model.location_x == x,
                        self.model.location_y == y
                    )
                )
            
            if hasattr(self.model, 'is_active'):
                query = query.filter(self.model.is_active == True)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by location: {str(e)}")
            raise RepositoryError(f"Failed to get {self.model.__name__} by location: {str(e)}")
    
    def search_by_name(self, name_pattern: str) -> List[ModelType]:
        """
        Search entities by name pattern.
        
        Args:
            name_pattern: Name pattern to search for
            
        Returns:
            List of matching entities
        """
        try:
            if not hasattr(self.model, 'name'):
                return []
            
            query = self.db.query(self.model).filter(
                self.model.name.ilike(f"%{name_pattern}%")
            )
            
            if hasattr(self.model, 'is_active'):
                query = query.filter(self.model.is_active == True)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error searching {self.model.__name__} by name: {str(e)}")
            raise RepositoryError(f"Failed to search {self.model.__name__} by name: {str(e)}") 