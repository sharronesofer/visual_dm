"""
Crafting System Services

This module provides business logic services for the crafting system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.crafting.models import (
    CraftingEntity,
    CraftingModel,
    CreateCraftingRequest,
    UpdateCraftingRequest,
    CraftingResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    CraftingNotFoundError,
    CraftingValidationError,
    CraftingConflictError
)

logger = logging.getLogger(__name__)


class CraftingService(BaseService[CraftingEntity]):
    """Service class for crafting business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, CraftingEntity)
        self.db = db_session

    async def create_crafting(
        self, 
        request: CreateCraftingRequest,
        user_id: Optional[UUID] = None
    ) -> CraftingResponse:
        """Create a new crafting"""
        try:
            logger.info(f"Creating crafting: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise CraftingConflictError(f"Crafting with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = CraftingEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created crafting {entity.id} successfully")
            return CraftingResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating crafting: {str(e)}")
            self.db.rollback()
            raise

    async def get_crafting_by_id(self, crafting_id: UUID) -> Optional[CraftingResponse]:
        """Get crafting by ID"""
        try:
            entity = self.db.query(CraftingEntity).filter(
                CraftingEntity.id == crafting_id,
                CraftingEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return CraftingResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting crafting {_crafting_id}: {str(e)}")
            raise

    async def update_crafting(
        self, 
        crafting_id: UUID, 
        request: UpdateCraftingRequest
    ) -> CraftingResponse:
        """Update existing crafting"""
        try:
            entity = await self._get_entity_by_id(crafting_id)
            if not entity:
                raise CraftingNotFoundError(f"Crafting {_crafting_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated crafting {entity.id} successfully")
            return CraftingResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating crafting {_crafting_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_crafting(self, crafting_id: UUID) -> bool:
        """Soft delete crafting"""
        try:
            entity = await self._get_entity_by_id(crafting_id)
            if not entity:
                raise CraftingNotFoundError(f"Crafting {_crafting_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted crafting {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting crafting {_crafting_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_craftings(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[CraftingResponse], int]:
        """List craftings with pagination and filters"""
        try:
            query = self.db.query(CraftingEntity).filter(
                CraftingEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(CraftingEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        CraftingEntity.name.ilike(f"%{search}%"),
                        CraftingEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(CraftingEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [CraftingResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing craftings: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[CraftingEntity]:
        """Get entity by name"""
        return self.db.query(CraftingEntity).filter(
            CraftingEntity.name == name,
            CraftingEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[CraftingEntity]:
        """Get entity by ID"""
        return self.db.query(CraftingEntity).filter(
            CraftingEntity.id == entity_id,
            CraftingEntity.is_active == True
        ).first()

    async def get_crafting_statistics(self) -> Dict[str, Any]:
        """Get crafting system statistics"""
        try:
            total_count = self.db.query(func.count(CraftingEntity.id)).filter(
                CraftingEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(CraftingEntity.id)).filter(
                CraftingEntity.is_active == True,
                CraftingEntity.status == "active"
            ).scalar()
            
            return {
                "total_craftings": total_count,
                "active_craftings": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting crafting statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_crafting_service(db_session: Session) -> CraftingService:
    """Create crafting service instance"""
    return CraftingService(db_session)
