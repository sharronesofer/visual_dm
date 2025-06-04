"""
Npc System Services

This module provides business logic services for the npc system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

# Use canonical imports from infrastructure
from backend.infrastructure.systems.npc.models.models import (
    NpcEntity,
    NpcModel,
    CreateNpcRequest,
    UpdateNpcRequest,
    NpcResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    NpcNotFoundError,
    NpcValidationError,
    NpcConflictError
)

logger = logging.getLogger(__name__)


class NpcService(BaseService[NpcEntity]):
    """Service class for npc business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, NpcEntity)
        self.db = db_session

    async def create_npc(
        self, 
        request: CreateNpcRequest,
        user_id: Optional[UUID] = None
    ) -> NpcResponse:
        """Create a new npc"""
        try:
            logger.info(f"Creating npc: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise NpcConflictError(f"Npc with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = NpcEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created npc {entity.id} successfully")
            return NpcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating npc: {str(e)}")
            self.db.rollback()
            raise

    async def get_npc_by_id(self, npc_id: UUID) -> Optional[NpcResponse]:
        """Get npc by ID"""
        try:
            entity = self.db.query(NpcEntity).filter(
                NpcEntity.id == npc_id,
                NpcEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return NpcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting npc {npc_id}: {str(e)}")
            raise

    async def update_npc(
        self, 
        npc_id: UUID, 
        request: UpdateNpcRequest
    ) -> NpcResponse:
        """Update existing npc"""
        try:
            entity = await self._get_entity_by_id(npc_id)
            if not entity:
                raise NpcNotFoundError(f"Npc {npc_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated npc {entity.id} successfully")
            return NpcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating npc {npc_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_npc(self, npc_id: UUID) -> bool:
        """Soft delete npc"""
        try:
            entity = await self._get_entity_by_id(npc_id)
            if not entity:
                raise NpcNotFoundError(f"Npc {npc_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted npc {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting npc {npc_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_npcs(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[NpcResponse], int]:
        """List npcs with pagination and filters"""
        try:
            query = self.db.query(NpcEntity).filter(
                NpcEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(NpcEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        NpcEntity.name.ilike(f"%{search}%"),
                        NpcEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(NpcEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [NpcResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing npcs: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[NpcEntity]:
        """Get entity by name"""
        return self.db.query(NpcEntity).filter(
            NpcEntity.name == name,
            NpcEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[NpcEntity]:
        """Get entity by ID"""
        return self.db.query(NpcEntity).filter(
            NpcEntity.id == entity_id,
            NpcEntity.is_active == True
        ).first()

    async def get_npc_statistics(self) -> Dict[str, Any]:
        """Get npc system statistics"""
        try:
            total_count = self.db.query(func.count(NpcEntity.id)).filter(
                NpcEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(NpcEntity.id)).filter(
                NpcEntity.is_active == True,
                NpcEntity.status == "active"
            ).scalar()
            
            return {
                "total_npcs": total_count,
                "active_npcs": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting npc statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_npc_service(db_session: Session) -> NpcService:
    """Create npc service instance"""
    return NpcService(db_session)
