"""
Faction System Services

This module provides business logic services for the faction system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.faction.models import (
    FactionEntity,
    FactionModel,
    CreateFactionRequest,
    UpdateFactionRequest,
    FactionResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    FactionValidationError,
    FactionConflictError
)

logger = logging.getLogger(__name__)


class FactionService(BaseService[FactionEntity]):
    """Service class for faction business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, FactionEntity)
        self.db = db_session

    async def create_faction(
        self, 
        request: CreateFactionRequest,
        user_id: Optional[UUID] = None
    ) -> FactionResponse:
        """Create a new faction"""
        try:
            logger.info(f"Creating faction: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise FactionConflictError(f"Faction with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = FactionEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created faction {entity.id} successfully")
            return FactionResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating faction: {str(e)}")
            self.db.rollback()
            raise

    async def get_faction_by_id(self, faction_id: UUID) -> Optional[FactionResponse]:
        """Get faction by ID"""
        try:
            entity = self.db.query(FactionEntity).filter(
                FactionEntity.id == faction_id,
                FactionEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return FactionResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting faction {_faction_id}: {str(e)}")
            raise

    async def update_faction(
        self, 
        faction_id: UUID, 
        request: UpdateFactionRequest
    ) -> FactionResponse:
        """Update existing faction"""
        try:
            entity = await self._get_entity_by_id(faction_id)
            if not entity:
                raise FactionNotFoundError(f"Faction {_faction_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated faction {entity.id} successfully")
            return FactionResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating faction {_faction_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_faction(self, faction_id: UUID) -> bool:
        """Soft delete faction"""
        try:
            entity = await self._get_entity_by_id(faction_id)
            if not entity:
                raise FactionNotFoundError(f"Faction {_faction_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted faction {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting faction {_faction_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_factions(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[FactionResponse], int]:
        """List factions with pagination and filters"""
        try:
            query = self.db.query(FactionEntity).filter(
                FactionEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(FactionEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        FactionEntity.name.ilike(f"%{search}%"),
                        FactionEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(FactionEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [FactionResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing factions: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[FactionEntity]:
        """Get entity by name"""
        return self.db.query(FactionEntity).filter(
            FactionEntity.name == name,
            FactionEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[FactionEntity]:
        """Get entity by ID"""
        return self.db.query(FactionEntity).filter(
            FactionEntity.id == entity_id,
            FactionEntity.is_active == True
        ).first()

    async def get_faction_statistics(self) -> Dict[str, Any]:
        """Get faction system statistics"""
        try:
            total_count = self.db.query(func.count(FactionEntity.id)).filter(
                FactionEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(FactionEntity.id)).filter(
                FactionEntity.is_active == True,
                FactionEntity.status == "active"
            ).scalar()
            
            return {
                "total_factions": total_count,
                "active_factions": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting faction statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_faction_service(db_session: Session) -> FactionService:
    """Create faction service instance"""
    return FactionService(db_session)
