"""
Analytics System Services

This module provides business logic services for the analytics system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.analytics.models import (
    AnalyticsEntity,
    AnalyticsModel,
    CreateAnalyticsRequest,
    UpdateAnalyticsRequest,
    AnalyticsResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    AnalyticsNotFoundError,
    AnalyticsValidationError,
    AnalyticsConflictError
)

logger = logging.getLogger(__name__)


class AnalyticsService(BaseService[AnalyticsEntity]):
    """Service class for analytics business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, AnalyticsEntity)
        self.db = db_session

    async def create_analytics(
        self, 
        request: CreateAnalyticsRequest,
        user_id: Optional[UUID] = None
    ) -> AnalyticsResponse:
        """Create a new analytics"""
        try:
            logger.info(f"Creating analytics: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise AnalyticsConflictError(f"Analytics with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = AnalyticsEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created analytics {entity.id} successfully")
            return AnalyticsResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating analytics: {str(e)}")
            self.db.rollback()
            raise

    async def get_analytics_by_id(self, analytics_id: UUID) -> Optional[AnalyticsResponse]:
        """Get analytics by ID"""
        try:
            entity = self.db.query(AnalyticsEntity).filter(
                AnalyticsEntity.id == analytics_id,
                AnalyticsEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return AnalyticsResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting analytics {_analytics_id}: {str(e)}")
            raise

    async def update_analytics(
        self, 
        analytics_id: UUID, 
        request: UpdateAnalyticsRequest
    ) -> AnalyticsResponse:
        """Update existing analytics"""
        try:
            entity = await self._get_entity_by_id(analytics_id)
            if not entity:
                raise AnalyticsNotFoundError(f"Analytics {_analytics_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated analytics {entity.id} successfully")
            return AnalyticsResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating analytics {_analytics_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_analytics(self, analytics_id: UUID) -> bool:
        """Soft delete analytics"""
        try:
            entity = await self._get_entity_by_id(analytics_id)
            if not entity:
                raise AnalyticsNotFoundError(f"Analytics {_analytics_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted analytics {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting analytics {_analytics_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_analyticss(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[AnalyticsResponse], int]:
        """List analyticss with pagination and filters"""
        try:
            query = self.db.query(AnalyticsEntity).filter(
                AnalyticsEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(AnalyticsEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        AnalyticsEntity.name.ilike(f"%{search}%"),
                        AnalyticsEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(AnalyticsEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [AnalyticsResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing analyticss: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[AnalyticsEntity]:
        """Get entity by name"""
        return self.db.query(AnalyticsEntity).filter(
            AnalyticsEntity.name == name,
            AnalyticsEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[AnalyticsEntity]:
        """Get entity by ID"""
        return self.db.query(AnalyticsEntity).filter(
            AnalyticsEntity.id == entity_id,
            AnalyticsEntity.is_active == True
        ).first()

    async def get_analytics_statistics(self) -> Dict[str, Any]:
        """Get analytics system statistics"""
        try:
            total_count = self.db.query(func.count(AnalyticsEntity.id)).filter(
                AnalyticsEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(AnalyticsEntity.id)).filter(
                AnalyticsEntity.is_active == True,
                AnalyticsEntity.status == "active"
            ).scalar()
            
            return {
                "total_analyticss": total_count,
                "active_analyticss": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_analytics_service(db_session: Session) -> AnalyticsService:
    """Create analytics service instance"""
    return AnalyticsService(db_session)
