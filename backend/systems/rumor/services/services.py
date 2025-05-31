"""
Rumor System Services

This module provides business logic services for the rumor system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.rumor.models import (
    RumorEntity,
    RumorModel,
    CreateRumorRequest,
    UpdateRumorRequest,
    RumorResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    RumorNotFoundError,
    RumorValidationError,
    RumorConflictError
)

logger = logging.getLogger(__name__)


class RumorService(BaseService[RumorEntity]):
    """Service class for rumor business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, RumorEntity)
        self.db = db_session

    async def create_rumor(
        self, 
        request: CreateRumorRequest,
        user_id: Optional[UUID] = None
    ) -> RumorResponse:
        """Create a new rumor"""
        try:
            logger.info(f"Creating rumor: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise RumorConflictError(f"Rumor with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = RumorEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created rumor {entity.id} successfully")
            return RumorResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating rumor: {str(e)}")
            self.db.rollback()
            raise

    async def get_rumor_by_id(self, rumor_id: UUID) -> Optional[RumorResponse]:
        """Get rumor by ID"""
        try:
            entity = self.db.query(RumorEntity).filter(
                RumorEntity.id == rumor_id,
                RumorEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return RumorResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting rumor {_rumor_id}: {str(e)}")
            raise

    async def update_rumor(
        self, 
        rumor_id: UUID, 
        request: UpdateRumorRequest
    ) -> RumorResponse:
        """Update existing rumor"""
        try:
            entity = await self._get_entity_by_id(rumor_id)
            if not entity:
                raise RumorNotFoundError(f"Rumor {_rumor_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated rumor {entity.id} successfully")
            return RumorResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating rumor {_rumor_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_rumor(self, rumor_id: UUID) -> bool:
        """Soft delete rumor"""
        try:
            entity = await self._get_entity_by_id(rumor_id)
            if not entity:
                raise RumorNotFoundError(f"Rumor {_rumor_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted rumor {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting rumor {_rumor_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_rumors(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[RumorResponse], int]:
        """List rumors with pagination and filters"""
        try:
            query = self.db.query(RumorEntity).filter(
                RumorEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(RumorEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        RumorEntity.name.ilike(f"%{search}%"),
                        RumorEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(RumorEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [RumorResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing rumors: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[RumorEntity]:
        """Get entity by name"""
        return self.db.query(RumorEntity).filter(
            RumorEntity.name == name,
            RumorEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[RumorEntity]:
        """Get entity by ID"""
        return self.db.query(RumorEntity).filter(
            RumorEntity.id == entity_id,
            RumorEntity.is_active == True
        ).first()

    async def get_rumor_statistics(self) -> Dict[str, Any]:
        """Get rumor system statistics"""
        try:
            total_count = self.db.query(func.count(RumorEntity.id)).filter(
                RumorEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(RumorEntity.id)).filter(
                RumorEntity.is_active == True,
                RumorEntity.status == "active"
            ).scalar()
            
            return {
                "total_rumors": total_count,
                "active_rumors": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting rumor statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_rumor_service(db_session: Session) -> RumorService:
    """Create rumor service instance"""
    return RumorService(db_session)
