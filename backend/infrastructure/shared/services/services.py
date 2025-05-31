"""
Shared System Services

This module provides business logic services for the shared system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple, Generic, TypeVar, Type
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from sqlalchemy.ext.declarative import DeclarativeMeta

from backend.infrastructure.shared.models import (
    SharedEntity,
    SharedModel,
    CreateSharedRequest,
    UpdateSharedRequest,
    SharedResponse
)
# Import BaseService from parent module to avoid circular import
# from .. import BaseService
from backend.infrastructure.shared.exceptions import (
    SharedNotFoundError,
    SharedValidationError,
    SharedConflictError
)

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=DeclarativeMeta)

# Define BaseService locally to avoid circular import
class BaseService(Generic[T]):
    """Base service class for all system services"""
    
    def __init__(self, db_session: Session, entity_class: Type[T]):
        self.db = db_session
        self.entity_class = entity_class

    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID"""
        return self.db.query(self.entity_class).filter(
            self.entity_class.id == entity_id
        ).first()

    async def create(self, **kwargs) -> T:
        """Create new entity"""
        entity = self.entity_class(**kwargs)
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    async def update(self, entity_id: UUID, **kwargs) -> Optional[T]:
        """Update entity"""
        entity = await self.get_by_id(entity_id)
        if entity:
            for key, value in kwargs.items():
                setattr(entity, key, value)
            self.db.commit()
            self.db.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity"""
        entity = await self.get_by_id(entity_id)
        if entity:
            self.db.delete(entity)
            self.db.commit()
            return True
        return False

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List all entities with pagination"""
        return self.db.query(self.entity_class).offset(offset).limit(limit).all()


class SharedService(BaseService[SharedEntity]):
    """Service class for shared business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, SharedEntity)
        self.db = db_session

    async def create_shared(
        self, 
        request: CreateSharedRequest,
        user_id: Optional[UUID] = None
    ) -> SharedResponse:
        """Create a new shared"""
        try:
            logger.info(f"Creating shared: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise SharedConflictError(f"Shared with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = SharedEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created shared {entity.id} successfully")
            return SharedResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating shared: {str(e)}")
            self.db.rollback()
            raise

    async def get_shared_by_id(self, shared_id: UUID) -> Optional[SharedResponse]:
        """Get shared by ID"""
        try:
            entity = self.db.query(SharedEntity).filter(
                SharedEntity.id == shared_id,
                SharedEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return SharedResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting shared {shared_id}: {str(e)}")
            raise

    async def update_shared(
        self, 
        shared_id: UUID, 
        request: UpdateSharedRequest
    ) -> SharedResponse:
        """Update existing shared"""
        try:
            entity = await self._get_entity_by_id(shared_id)
            if not entity:
                raise SharedNotFoundError(f"Shared {shared_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated shared {entity.id} successfully")
            return SharedResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating shared {shared_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_shared(self, shared_id: UUID) -> bool:
        """Soft delete shared"""
        try:
            entity = await self._get_entity_by_id(shared_id)
            if not entity:
                raise SharedNotFoundError(f"Shared {shared_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted shared {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting shared {shared_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_shareds(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[SharedResponse], int]:
        """List shareds with pagination and filters"""
        try:
            query = self.db.query(SharedEntity).filter(
                SharedEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(SharedEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        SharedEntity.name.ilike(f"%{search}%"),
                        SharedEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(SharedEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [SharedResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing shareds: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[SharedEntity]:
        """Get entity by name"""
        return self.db.query(SharedEntity).filter(
            SharedEntity.name == name,
            SharedEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[SharedEntity]:
        """Get entity by ID"""
        return self.db.query(SharedEntity).filter(
            SharedEntity.id == entity_id,
            SharedEntity.is_active == True
        ).first()

    async def get_shared_statistics(self) -> Dict[str, Any]:
        """Get shared system statistics"""
        try:
            total_count = self.db.query(func.count(SharedEntity.id)).filter(
                SharedEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(SharedEntity.id)).filter(
                SharedEntity.is_active == True,
                SharedEntity.status == "active"
            ).scalar()
            
            return {
                "total_shareds": total_count,
                "active_shareds": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting shared statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_shared_service(db_session: Session) -> SharedService:
    """Create shared service instance"""
    return SharedService(db_session)
