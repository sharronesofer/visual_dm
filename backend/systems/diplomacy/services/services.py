"""
Diplomacy System Services

This module provides business logic services for the diplomacy system
according to the Development Bible standards.

This now acts as a facade for the UnifiedDiplomacyService while maintaining
the async interface and additional business logic patterns.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

# Import unified service
from backend.systems.diplomacy.services.unified_diplomacy_service import UnifiedDiplomacyService

from backend.systems.diplomacy.models import (
    DiplomacyEntity,
    DiplomacyModel,
    CreateDiplomacyRequest,
    UpdateDiplomacyRequest,
    DiplomacyResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    DiplomacyNotFoundError,
    DiplomacyValidationError,
    DiplomacyConflictError
)

logger = logging.getLogger(__name__)


class DiplomacyService(BaseService[DiplomacyEntity]):
    """
    Service class for diplomacy business logic.
    
    This class now delegates to UnifiedDiplomacyService while maintaining
    the async interface and additional business logic patterns.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, DiplomacyEntity)
        self.db = db_session
        # Initialize the unified service
        self._unified_service = UnifiedDiplomacyService(db_session=db_session)

    async def create_diplomacy(
        self, 
        request: CreateDiplomacyRequest,
        user_id: Optional[UUID] = None
    ) -> DiplomacyResponse:
        """Create a new diplomacy"""
        return await self._unified_service.create_diplomacy_async(request, user_id)

    async def get_diplomacy_by_id(self, diplomacy_id: UUID) -> Optional[DiplomacyResponse]:
        """Get diplomacy by ID"""
        return await self._unified_service.get_diplomacy_by_id_async(diplomacy_id)

    async def update_diplomacy(
        self, 
        diplomacy_id: UUID, 
        request: UpdateDiplomacyRequest
    ) -> DiplomacyResponse:
        """Update existing diplomacy"""
        try:
            entity = await self._get_entity_by_id(diplomacy_id)
            if not entity:
                raise DiplomacyNotFoundError(f"Diplomacy {diplomacy_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated diplomacy {entity.id} successfully")
            return DiplomacyResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating diplomacy {diplomacy_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_diplomacy(self, diplomacy_id: UUID) -> bool:
        """Soft delete diplomacy"""
        try:
            entity = await self._get_entity_by_id(diplomacy_id)
            if not entity:
                raise DiplomacyNotFoundError(f"Diplomacy {diplomacy_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted diplomacy {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting diplomacy {diplomacy_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_diplomacys(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[DiplomacyResponse], int]:
        """List diplomacys with pagination and filters"""
        try:
            query = self.db.query(DiplomacyEntity).filter(
                DiplomacyEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(DiplomacyEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        DiplomacyEntity.name.ilike(f"%{search}%"),
                        DiplomacyEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(DiplomacyEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [DiplomacyResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing diplomacys: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[DiplomacyEntity]:
        """Get entity by name"""
        return self.db.query(DiplomacyEntity).filter(
            DiplomacyEntity.name == name,
            DiplomacyEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[DiplomacyEntity]:
        """Get entity by ID"""
        return self.db.query(DiplomacyEntity).filter(
            DiplomacyEntity.id == entity_id,
            DiplomacyEntity.is_active == True
        ).first()

    async def get_diplomacy_statistics(self) -> Dict[str, Any]:
        """Get diplomacy system statistics"""
        try:
            total_count = self.db.query(func.count(DiplomacyEntity.id)).filter(
                DiplomacyEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(DiplomacyEntity.id)).filter(
                DiplomacyEntity.is_active == True,
                DiplomacyEntity.status == "active"
            ).scalar()
            
            return {
                "total_diplomacies": total_count,
                "active_diplomacies": active_count,
                "inactive_diplomacies": total_count - active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting diplomacy statistics: {str(e)}")
            raise


def create_diplomacy_service(db_session: Session) -> DiplomacyService:
    """Create diplomacy service instance"""
    return DiplomacyService(db_session)
