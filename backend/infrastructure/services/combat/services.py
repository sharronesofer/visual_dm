"""
Combat System Services

This module provides business logic services for the combat system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.models.combat import (
    CombatEntity,
    CombatModel,
    CreateCombatRequest,
    UpdateCombatRequest,
    CombatResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    CombatNotFoundError,
    CombatValidationError,
    CombatConflictError
)

logger = logging.getLogger(__name__)


class CombatService(BaseService[CombatEntity]):
    """Service class for combat business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, CombatEntity)
        self.db = db_session

    async def create_combat(
        self, 
        request: CreateCombatRequest,
        user_id: Optional[UUID] = None
    ) -> CombatResponse:
        """Create a new combat"""
        try:
            logger.info(f"Creating combat: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise CombatConflictError(f"Combat with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = CombatEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created combat {entity.id} successfully")
            return CombatResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating combat: {str(e)}")
            self.db.rollback()
            raise

    async def get_combat_by_id(self, combat_id: UUID) -> Optional[CombatResponse]:
        """Get combat by ID"""
        try:
            entity = self.db.query(CombatEntity).filter(
                CombatEntity.id == combat_id,
                CombatEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return CombatResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting combat {_combat_id}: {str(e)}")
            raise

    async def update_combat(
        self, 
        combat_id: UUID, 
        request: UpdateCombatRequest
    ) -> CombatResponse:
        """Update existing combat"""
        try:
            entity = await self._get_entity_by_id(combat_id)
            if not entity:
                raise CombatNotFoundError(f"Combat {_combat_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated combat {entity.id} successfully")
            return CombatResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating combat {_combat_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_combat(self, combat_id: UUID) -> bool:
        """Soft delete combat"""
        try:
            entity = await self._get_entity_by_id(combat_id)
            if not entity:
                raise CombatNotFoundError(f"Combat {_combat_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted combat {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting combat {_combat_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_combats(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[CombatResponse], int]:
        """List combats with pagination and filters"""
        try:
            query = self.db.query(CombatEntity).filter(
                CombatEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(CombatEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        CombatEntity.name.ilike(f"%{search}%"),
                        CombatEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(CombatEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [CombatResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing combats: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[CombatEntity]:
        """Get entity by name"""
        return self.db.query(CombatEntity).filter(
            CombatEntity.name == name,
            CombatEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[CombatEntity]:
        """Get entity by ID"""
        return self.db.query(CombatEntity).filter(
            CombatEntity.id == entity_id,
            CombatEntity.is_active == True
        ).first()

    async def get_combat_statistics(self) -> Dict[str, Any]:
        """Get combat system statistics"""
        try:
            total_count = self.db.query(func.count(CombatEntity.id)).filter(
                CombatEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(CombatEntity.id)).filter(
                CombatEntity.is_active == True,
                CombatEntity.status == "active"
            ).scalar()
            
            return {
                "total_combats": total_count,
                "active_combats": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting combat statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_combat_service(db_session: Session) -> CombatService:
    """Create combat service instance"""
    return CombatService(db_session)
