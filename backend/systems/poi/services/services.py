"""
Poi System Services

This module provides business logic services for the poi system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.poi.models import (
    PoiEntity,
    PoiModel,
    CreatePoiRequest,
    UpdatePoiRequest,
    PoiResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    PoiNotFoundError,
    PoiValidationError,
    PoiConflictError
)

logger = logging.getLogger(__name__)


class PoiService(BaseService[PoiEntity]):
    """Service class for poi business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, PoiEntity)
        self.db = db_session

    async def create_poi(
        self, 
        request: CreatePoiRequest,
        user_id: Optional[UUID] = None
    ) -> PoiResponse:
        """Create a new poi"""
        try:
            logger.info(f"Creating poi: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise PoiConflictError(f"Poi with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = PoiEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created poi {entity.id} successfully")
            return PoiResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating poi: {str(e)}")
            self.db.rollback()
            raise

    async def get_poi_by_id(self, poi_id: UUID) -> Optional[PoiResponse]:
        """Get poi by ID"""
        try:
            entity = self.db.query(PoiEntity).filter(
                PoiEntity.id == poi_id,
                PoiEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return PoiResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting poi {_poi_id}: {str(e)}")
            raise

    async def update_poi(
        self, 
        poi_id: UUID, 
        request: UpdatePoiRequest
    ) -> PoiResponse:
        """Update existing poi"""
        try:
            entity = await self._get_entity_by_id(poi_id)
            if not entity:
                raise PoiNotFoundError(f"Poi {_poi_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated poi {entity.id} successfully")
            return PoiResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating poi {_poi_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_poi(self, poi_id: UUID) -> bool:
        """Soft delete poi"""
        try:
            entity = await self._get_entity_by_id(poi_id)
            if not entity:
                raise PoiNotFoundError(f"Poi {_poi_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted poi {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting poi {_poi_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_pois(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[PoiResponse], int]:
        """List pois with pagination and filters"""
        try:
            query = self.db.query(PoiEntity).filter(
                PoiEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(PoiEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        PoiEntity.name.ilike(f"%{search}%"),
                        PoiEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(PoiEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [PoiResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing pois: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[PoiEntity]:
        """Get entity by name"""
        return self.db.query(PoiEntity).filter(
            PoiEntity.name == name,
            PoiEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[PoiEntity]:
        """Get entity by ID"""
        return self.db.query(PoiEntity).filter(
            PoiEntity.id == entity_id,
            PoiEntity.is_active == True
        ).first()

    async def get_poi_statistics(self) -> Dict[str, Any]:
        """Get poi system statistics"""
        try:
            total_count = self.db.query(func.count(PoiEntity.id)).filter(
                PoiEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(PoiEntity.id)).filter(
                PoiEntity.is_active == True,
                PoiEntity.status == "active"
            ).scalar()
            
            return {
                "total_pois": total_count,
                "active_pois": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting poi statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_poi_service(db_session: Session) -> PoiService:
    """Create poi service instance"""
    return PoiService(db_session)
