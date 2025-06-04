"""
Memory System Services

This module provides business logic services for the memory system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.systems.memory.models.models import (
    MemoryEntity,
    MemoryModel,
    CreateMemoryRequest,
    UpdateMemoryRequest,
    MemoryResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    MemoryNotFoundError,
    MemoryValidationError,
    MemoryConflictError
)

logger = logging.getLogger(__name__)


class MemoryService(BaseService[MemoryEntity]):
    """Service class for memory business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, MemoryEntity)
        self.db = db_session

    async def create_memory(
        self, 
        request: CreateMemoryRequest,
        user_id: Optional[UUID] = None
    ) -> MemoryResponse:
        """Create a new memory"""
        try:
            logger.info(f"Creating memory: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise MemoryConflictError(f"Memory with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = MemoryEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created memory {entity.id} successfully")
            return MemoryResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating memory: {str(e)}")
            self.db.rollback()
            raise

    async def get_memory_by_id(self, memory_id: UUID) -> Optional[MemoryResponse]:
        """Get memory by ID"""
        try:
            entity = self.db.query(MemoryEntity).filter(
                MemoryEntity.id == memory_id,
                MemoryEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return MemoryResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting memory {_memory_id}: {str(e)}")
            raise

    async def update_memory(
        self, 
        memory_id: UUID, 
        request: UpdateMemoryRequest
    ) -> MemoryResponse:
        """Update existing memory"""
        try:
            entity = await self._get_entity_by_id(memory_id)
            if not entity:
                raise MemoryNotFoundError(f"Memory {_memory_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated memory {entity.id} successfully")
            return MemoryResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating memory {_memory_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_memory(self, memory_id: UUID) -> bool:
        """Soft delete memory"""
        try:
            entity = await self._get_entity_by_id(memory_id)
            if not entity:
                raise MemoryNotFoundError(f"Memory {_memory_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted memory {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory {_memory_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_memorys(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[MemoryResponse], int]:
        """List memorys with pagination and filters"""
        try:
            query = self.db.query(MemoryEntity).filter(
                MemoryEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(MemoryEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        MemoryEntity.name.ilike(f"%{search}%"),
                        MemoryEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(MemoryEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [MemoryResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing memorys: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[MemoryEntity]:
        """Get entity by name"""
        return self.db.query(MemoryEntity).filter(
            MemoryEntity.name == name,
            MemoryEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[MemoryEntity]:
        """Get entity by ID"""
        return self.db.query(MemoryEntity).filter(
            MemoryEntity.id == entity_id,
            MemoryEntity.is_active == True
        ).first()

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            total_count = self.db.query(func.count(MemoryEntity.id)).filter(
                MemoryEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(MemoryEntity.id)).filter(
                MemoryEntity.is_active == True,
                MemoryEntity.status == "active"
            ).scalar()
            
            return {
                "total_memorys": total_count,
                "active_memorys": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting memory statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_memory_service(db_session: Session) -> MemoryService:
    """Create memory service instance"""
    return MemoryService(db_session)


# Global memory service instance for LLM context manager compatibility
_memory_service_instance = None

async def get_memory_service() -> MemoryService:
    """Get memory service instance for LLM context manager compatibility"""
    global _memory_service_instance
    if _memory_service_instance is None:
        # For now, create a mock service - this should be properly initialized with a DB session
        from backend.infrastructure.database.connection import get_async_db
        db = next(get_async_db())
        _memory_service_instance = MemoryService(db)
    return _memory_service_instance
