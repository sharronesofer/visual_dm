"""
Time System Services

This module provides business logic services for the time system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.time.models import (
    TimeEntity,
    TimeModel,
    CreateTimeRequest,
    UpdateTimeRequest,
    TimeResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    TimeNotFoundError,
    TimeValidationError,
    TimeConflictError
)

logger = logging.getLogger(__name__)


class TimeService(BaseService[TimeEntity]):
    """Service class for time business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, TimeEntity)
        self.db = db_session

    async def create_time(
        self, 
        request: CreateTimeRequest,
        user_id: Optional[UUID] = None
    ) -> TimeResponse:
        """Create a new time"""
        try:
            logger.info(f"Creating time: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise TimeConflictError(f"Time with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = TimeEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created time {entity.id} successfully")
            return TimeResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating time: {str(e)}")
            self.db.rollback()
            raise

    async def get_time_by_id(self, time_id: UUID) -> Optional[TimeResponse]:
        """Get time by ID"""
        try:
            entity = self.db.query(TimeEntity).filter(
                TimeEntity.id == time_id,
                TimeEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return TimeResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting time {_time_id}: {str(e)}")
            raise

    async def update_time(
        self, 
        time_id: UUID, 
        request: UpdateTimeRequest
    ) -> TimeResponse:
        """Update existing time"""
        try:
            entity = await self._get_entity_by_id(time_id)
            if not entity:
                raise TimeNotFoundError(f"Time {_time_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated time {entity.id} successfully")
            return TimeResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating time {_time_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_time(self, time_id: UUID) -> bool:
        """Soft delete time"""
        try:
            entity = await self._get_entity_by_id(time_id)
            if not entity:
                raise TimeNotFoundError(f"Time {_time_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted time {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting time {_time_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_times(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[TimeResponse], int]:
        """List times with pagination and filters"""
        try:
            query = self.db.query(TimeEntity).filter(
                TimeEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(TimeEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        TimeEntity.name.ilike(f"%{search}%"),
                        TimeEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(TimeEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [TimeResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing times: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[TimeEntity]:
        """Get entity by name"""
        return self.db.query(TimeEntity).filter(
            TimeEntity.name == name,
            TimeEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[TimeEntity]:
        """Get entity by ID"""
        return self.db.query(TimeEntity).filter(
            TimeEntity.id == entity_id,
            TimeEntity.is_active == True
        ).first()

    async def get_time_statistics(self) -> Dict[str, Any]:
        """Get time system statistics"""
        try:
            total_count = self.db.query(func.count(TimeEntity.id)).filter(
                TimeEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(TimeEntity.id)).filter(
                TimeEntity.is_active == True,
                TimeEntity.status == "active"
            ).scalar()
            
            return {
                "total_times": total_count,
                "active_times": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting time statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_time_service(db_session: Session) -> TimeService:
    """Create time service instance"""
    return TimeService(db_session)
