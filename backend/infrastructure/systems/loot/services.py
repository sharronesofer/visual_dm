"""
Loot System Services

This module provides business logic services for the loot system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.systems.loot.models import (
    LootEntity,
    LootModel,
    CreateLootRequest,
    UpdateLootRequest,
    LootResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    LootNotFoundError,
    LootValidationError,
    LootConflictError
)

logger = logging.getLogger(__name__)


class LootService(BaseService[LootEntity]):
    """Service class for loot business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, LootEntity)
        self.db = db_session

    async def create_loot(
        self, 
        request: CreateLootRequest,
        user_id: Optional[UUID] = None
    ) -> LootResponse:
        """Create a new loot"""
        try:
            logger.info(f"Creating loot: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise LootConflictError(f"Loot with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = LootEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created loot {entity.id} successfully")
            return LootResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating loot: {str(e)}")
            self.db.rollback()
            raise

    async def get_loot_by_id(self, loot_id: UUID) -> Optional[LootResponse]:
        """Get loot by ID"""
        try:
            entity = self.db.query(LootEntity).filter(
                LootEntity.id == loot_id,
                LootEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return LootResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting loot {_loot_id}: {str(e)}")
            raise

    async def update_loot(
        self, 
        loot_id: UUID, 
        request: UpdateLootRequest
    ) -> LootResponse:
        """Update existing loot"""
        try:
            entity = await self._get_entity_by_id(loot_id)
            if not entity:
                raise LootNotFoundError(f"Loot {_loot_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated loot {entity.id} successfully")
            return LootResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating loot {_loot_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_loot(self, loot_id: UUID) -> bool:
        """Soft delete loot"""
        try:
            entity = await self._get_entity_by_id(loot_id)
            if not entity:
                raise LootNotFoundError(f"Loot {_loot_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted loot {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting loot {_loot_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_loots(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[LootResponse], int]:
        """List loots with pagination and filters"""
        try:
            query = self.db.query(LootEntity).filter(
                LootEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(LootEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        LootEntity.name.ilike(f"%{search}%"),
                        LootEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(LootEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [LootResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing loots: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[LootEntity]:
        """Get entity by name"""
        return self.db.query(LootEntity).filter(
            LootEntity.name == name,
            LootEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[LootEntity]:
        """Get entity by ID"""
        return self.db.query(LootEntity).filter(
            LootEntity.id == entity_id,
            LootEntity.is_active == True
        ).first()

    async def get_loot_statistics(self) -> Dict[str, Any]:
        """Get loot system statistics"""
        try:
            total_count = self.db.query(func.count(LootEntity.id)).filter(
                LootEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(LootEntity.id)).filter(
                LootEntity.is_active == True,
                LootEntity.status == "active"
            ).scalar()
            
            return {
                "total_loots": total_count,
                "active_loots": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting loot statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_loot_service(db_session: Session) -> LootService:
    """Create loot service instance"""
    return LootService(db_session)
