"""
Economy System Services

This module provides business logic services for the economy system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.economy.models import (
    EconomyEntity,
    EconomyModel,
    CreateEconomyRequest,
    UpdateEconomyRequest,
    EconomyResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    EconomyNotFoundError,
    EconomyValidationError,
    EconomyConflictError
)

logger = logging.getLogger(__name__)


class EconomyService(BaseService[EconomyEntity]):
    """Service class for economy business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, EconomyEntity)
        self.db = db_session

    async def create_economy(
        self, 
        request: CreateEconomyRequest,
        user_id: Optional[UUID] = None
    ) -> EconomyResponse:
        """Create a new economy"""
        try:
            logger.info(f"Creating economy: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise EconomyConflictError(f"Economy with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = EconomyEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created economy {entity.id} successfully")
            return EconomyResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating economy: {str(e)}")
            self.db.rollback()
            raise

    async def get_economy_by_id(self, economy_id: UUID) -> Optional[EconomyResponse]:
        """Get economy by ID"""
        try:
            entity = self.db.query(EconomyEntity).filter(
                EconomyEntity.id == economy_id,
                EconomyEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return EconomyResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting economy {_economy_id}: {str(e)}")
            raise

    async def update_economy(
        self, 
        economy_id: UUID, 
        request: UpdateEconomyRequest
    ) -> EconomyResponse:
        """Update existing economy"""
        try:
            entity = await self._get_entity_by_id(economy_id)
            if not entity:
                raise EconomyNotFoundError(f"Economy {_economy_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated economy {entity.id} successfully")
            return EconomyResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating economy {_economy_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_economy(self, economy_id: UUID) -> bool:
        """Soft delete economy"""
        try:
            entity = await self._get_entity_by_id(economy_id)
            if not entity:
                raise EconomyNotFoundError(f"Economy {_economy_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted economy {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting economy {_economy_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_economys(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[EconomyResponse], int]:
        """List economys with pagination and filters"""
        try:
            query = self.db.query(EconomyEntity).filter(
                EconomyEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(EconomyEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        EconomyEntity.name.ilike(f"%{search}%"),
                        EconomyEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(EconomyEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [EconomyResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing economys: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[EconomyEntity]:
        """Get entity by name"""
        return self.db.query(EconomyEntity).filter(
            EconomyEntity.name == name,
            EconomyEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[EconomyEntity]:
        """Get entity by ID"""
        return self.db.query(EconomyEntity).filter(
            EconomyEntity.id == entity_id,
            EconomyEntity.is_active == True
        ).first()

    async def get_economy_statistics(self) -> Dict[str, Any]:
        """Get economy system statistics"""
        try:
            total_count = self.db.query(func.count(EconomyEntity.id)).filter(
                EconomyEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(EconomyEntity.id)).filter(
                EconomyEntity.is_active == True,
                EconomyEntity.status == "active"
            ).scalar()
            
            return {
                "total_economys": total_count,
                "active_economys": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting economy statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_economy_service(db_session: Session) -> EconomyService:
    """Create economy service instance"""
    return EconomyService(db_session)
