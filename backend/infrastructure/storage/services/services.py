"""
Storage System Services

This module provides business logic services for the storage system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.storage.models import (
    StorageEntity,
    StorageModel,
    CreateStorageRequest,
    UpdateStorageRequest,
    StorageResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    StorageNotFoundError,
    StorageValidationError,
    StorageConflictError
)

logger = logging.getLogger(__name__)


class StorageService(BaseService[StorageEntity]):
    """Service class for storage business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, StorageEntity)
        self.db = db_session

    async def create_storage(
        self, 
        request: CreateStorageRequest,
        user_id: Optional[UUID] = None
    ) -> StorageResponse:
        """Create a new storage"""
        try:
            logger.info(f"Creating storage: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise StorageConflictError(f"Storage with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = StorageEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created storage {entity.id} successfully")
            return StorageResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating storage: {str(e)}")
            self.db.rollback()
            raise

    async def get_storage_by_id(self, storage_id: UUID) -> Optional[StorageResponse]:
        """Get storage by ID"""
        try:
            entity = self.db.query(StorageEntity).filter(
                StorageEntity.id == storage_id,
                StorageEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return StorageResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting storage {_storage_id}: {str(e)}")
            raise

    async def update_storage(
        self, 
        storage_id: UUID, 
        request: UpdateStorageRequest
    ) -> StorageResponse:
        """Update existing storage"""
        try:
            entity = await self._get_entity_by_id(storage_id)
            if not entity:
                raise StorageNotFoundError(f"Storage {_storage_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated storage {entity.id} successfully")
            return StorageResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating storage {_storage_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_storage(self, storage_id: UUID) -> bool:
        """Soft delete storage"""
        try:
            entity = await self._get_entity_by_id(storage_id)
            if not entity:
                raise StorageNotFoundError(f"Storage {_storage_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted storage {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting storage {_storage_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_storages(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[StorageResponse], int]:
        """List storages with pagination and filters"""
        try:
            query = self.db.query(StorageEntity).filter(
                StorageEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(StorageEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        StorageEntity.name.ilike(f"%{search}%"),
                        StorageEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(StorageEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [StorageResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing storages: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[StorageEntity]:
        """Get entity by name"""
        return self.db.query(StorageEntity).filter(
            StorageEntity.name == name,
            StorageEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[StorageEntity]:
        """Get entity by ID"""
        return self.db.query(StorageEntity).filter(
            StorageEntity.id == entity_id,
            StorageEntity.is_active == True
        ).first()

    async def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage system statistics"""
        try:
            total_count = self.db.query(func.count(StorageEntity.id)).filter(
                StorageEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(StorageEntity.id)).filter(
                StorageEntity.is_active == True,
                StorageEntity.status == "active"
            ).scalar()
            
            return {
                "total_storages": total_count,
                "active_storages": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting storage statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_storage_service(db_session: Session) -> StorageService:
    """Create storage service instance"""
    return StorageService(db_session)
