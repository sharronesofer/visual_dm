"""
World_State System Services

This module provides business logic services for the world_state system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.world_state.models import (
    World_StateEntity,
    World_StateModel,
    CreateWorld_StateRequest,
    UpdateWorld_StateRequest,
    World_StateResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    World_StateNotFoundError,
    World_StateValidationError,
    World_StateConflictError
)

logger = logging.getLogger(__name__)


class World_StateService(BaseService[World_StateEntity]):
    """Service class for world_state business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, World_StateEntity)
        self.db = db_session

    async def create_world_state(
        self, 
        request: CreateWorld_StateRequest,
        user_id: Optional[UUID] = None
    ) -> World_StateResponse:
        """Create a new world_state"""
        try:
            logger.info(f"Creating world_state: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise World_StateConflictError(f"World_State with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = World_StateEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created world_state {entity.id} successfully")
            return World_StateResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating world_state: {str(e)}")
            self.db.rollback()
            raise

    async def get_world_state_by_id(self, world_state_id: UUID) -> Optional[World_StateResponse]:
        """Get world_state by ID"""
        try:
            entity = self.db.query(World_StateEntity).filter(
                World_StateEntity.id == world_state_id,
                World_StateEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return World_StateResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting world_state {_world_state_id}: {str(e)}")
            raise

    async def update_world_state(
        self, 
        world_state_id: UUID, 
        request: UpdateWorld_StateRequest
    ) -> World_StateResponse:
        """Update existing world_state"""
        try:
            entity = await self._get_entity_by_id(world_state_id)
            if not entity:
                raise World_StateNotFoundError(f"World_State {_world_state_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated world_state {entity.id} successfully")
            return World_StateResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating world_state {_world_state_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_world_state(self, world_state_id: UUID) -> bool:
        """Soft delete world_state"""
        try:
            entity = await self._get_entity_by_id(world_state_id)
            if not entity:
                raise World_StateNotFoundError(f"World_State {_world_state_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted world_state {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting world_state {_world_state_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_world_states(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[World_StateResponse], int]:
        """List world_states with pagination and filters"""
        try:
            query = self.db.query(World_StateEntity).filter(
                World_StateEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(World_StateEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        World_StateEntity.name.ilike(f"%{search}%"),
                        World_StateEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(World_StateEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [World_StateResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing world_states: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[World_StateEntity]:
        """Get entity by name"""
        return self.db.query(World_StateEntity).filter(
            World_StateEntity.name == name,
            World_StateEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[World_StateEntity]:
        """Get entity by ID"""
        return self.db.query(World_StateEntity).filter(
            World_StateEntity.id == entity_id,
            World_StateEntity.is_active == True
        ).first()

    async def get_world_state_statistics(self) -> Dict[str, Any]:
        """Get world_state system statistics"""
        try:
            total_count = self.db.query(func.count(World_StateEntity.id)).filter(
                World_StateEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(World_StateEntity.id)).filter(
                World_StateEntity.is_active == True,
                World_StateEntity.status == "active"
            ).scalar()
            
            return {
                "total_world_states": total_count,
                "active_world_states": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting world_state statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_world_state_service(db_session: Session) -> World_StateService:
    """Create world_state service instance"""
    return World_StateService(db_session)
