"""
World_Generation System Services

This module provides business logic services for the world_generation system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.world_generation.models import (
    World_GenerationEntity,
    World_GenerationModel,
    CreateWorld_GenerationRequest,
    UpdateWorld_GenerationRequest,
    World_GenerationResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    World_GenerationNotFoundError,
    World_GenerationValidationError,
    World_GenerationConflictError
)

logger = logging.getLogger(__name__)


class World_GenerationService(BaseService[World_GenerationEntity]):
    """Service class for world_generation business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, World_GenerationEntity)
        self.db = db_session

    async def create_world_generation(
        self, 
        request: CreateWorld_GenerationRequest,
        user_id: Optional[UUID] = None
    ) -> World_GenerationResponse:
        """Create a new world_generation"""
        try:
            logger.info(f"Creating world_generation: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise World_GenerationConflictError(f"World_Generation with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = World_GenerationEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created world_generation {entity.id} successfully")
            return World_GenerationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating world_generation: {str(e)}")
            self.db.rollback()
            raise

    async def get_world_generation_by_id(self, world_generation_id: UUID) -> Optional[World_GenerationResponse]:
        """Get world_generation by ID"""
        try:
            entity = self.db.query(World_GenerationEntity).filter(
                World_GenerationEntity.id == world_generation_id,
                World_GenerationEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return World_GenerationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting world_generation {_world_generation_id}: {str(e)}")
            raise

    async def update_world_generation(
        self, 
        world_generation_id: UUID, 
        request: UpdateWorld_GenerationRequest
    ) -> World_GenerationResponse:
        """Update existing world_generation"""
        try:
            entity = await self._get_entity_by_id(world_generation_id)
            if not entity:
                raise World_GenerationNotFoundError(f"World_Generation {_world_generation_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated world_generation {entity.id} successfully")
            return World_GenerationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating world_generation {_world_generation_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_world_generation(self, world_generation_id: UUID) -> bool:
        """Soft delete world_generation"""
        try:
            entity = await self._get_entity_by_id(world_generation_id)
            if not entity:
                raise World_GenerationNotFoundError(f"World_Generation {_world_generation_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted world_generation {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting world_generation {_world_generation_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_world_generations(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[World_GenerationResponse], int]:
        """List world_generations with pagination and filters"""
        try:
            query = self.db.query(World_GenerationEntity).filter(
                World_GenerationEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(World_GenerationEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        World_GenerationEntity.name.ilike(f"%{search}%"),
                        World_GenerationEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(World_GenerationEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [World_GenerationResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing world_generations: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[World_GenerationEntity]:
        """Get entity by name"""
        return self.db.query(World_GenerationEntity).filter(
            World_GenerationEntity.name == name,
            World_GenerationEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[World_GenerationEntity]:
        """Get entity by ID"""
        return self.db.query(World_GenerationEntity).filter(
            World_GenerationEntity.id == entity_id,
            World_GenerationEntity.is_active == True
        ).first()

    async def get_world_generation_statistics(self) -> Dict[str, Any]:
        """Get world_generation system statistics"""
        try:
            total_count = self.db.query(func.count(World_GenerationEntity.id)).filter(
                World_GenerationEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(World_GenerationEntity.id)).filter(
                World_GenerationEntity.is_active == True,
                World_GenerationEntity.status == "active"
            ).scalar()
            
            return {
                "total_world_generations": total_count,
                "active_world_generations": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting world_generation statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_world_generation_service(db_session: Session) -> World_GenerationService:
    """Create world_generation service instance"""
    return World_GenerationService(db_session)
