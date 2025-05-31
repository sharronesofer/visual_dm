"""
Events System Services

This module provides business logic services for the events system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.events.models import (
    EventsEntity,
    EventsModel,
    CreateEventsRequest,
    UpdateEventsRequest,
    EventsResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    EventsNotFoundError,
    EventsValidationError,
    EventsConflictError
)

logger = logging.getLogger(__name__)


class EventsService(BaseService[EventsEntity]):
    """Service class for events business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, EventsEntity)
        self.db = db_session

    async def create_events(
        self, 
        request: CreateEventsRequest,
        user_id: Optional[UUID] = None
    ) -> EventsResponse:
        """Create a new events"""
        try:
            logger.info(f"Creating events: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise EventsConflictError(f"Events with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = EventsEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created events {entity.id} successfully")
            return EventsResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating events: {str(e)}")
            self.db.rollback()
            raise

    async def get_events_by_id(self, events_id: UUID) -> Optional[EventsResponse]:
        """Get events by ID"""
        try:
            entity = self.db.query(EventsEntity).filter(
                EventsEntity.id == events_id,
                EventsEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return EventsResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting events {_events_id}: {str(e)}")
            raise

    async def update_events(
        self, 
        events_id: UUID, 
        request: UpdateEventsRequest
    ) -> EventsResponse:
        """Update existing events"""
        try:
            entity = await self._get_entity_by_id(events_id)
            if not entity:
                raise EventsNotFoundError(f"Events {_events_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated events {entity.id} successfully")
            return EventsResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating events {_events_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_events(self, events_id: UUID) -> bool:
        """Soft delete events"""
        try:
            entity = await self._get_entity_by_id(events_id)
            if not entity:
                raise EventsNotFoundError(f"Events {_events_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted events {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting events {_events_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_eventss(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[EventsResponse], int]:
        """List eventss with pagination and filters"""
        try:
            query = self.db.query(EventsEntity).filter(
                EventsEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(EventsEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        EventsEntity.name.ilike(f"%{search}%"),
                        EventsEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(EventsEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [EventsResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing eventss: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[EventsEntity]:
        """Get entity by name"""
        return self.db.query(EventsEntity).filter(
            EventsEntity.name == name,
            EventsEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[EventsEntity]:
        """Get entity by ID"""
        return self.db.query(EventsEntity).filter(
            EventsEntity.id == entity_id,
            EventsEntity.is_active == True
        ).first()

    async def get_events_statistics(self) -> Dict[str, Any]:
        """Get events system statistics"""
        try:
            total_count = self.db.query(func.count(EventsEntity.id)).filter(
                EventsEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(EventsEntity.id)).filter(
                EventsEntity.is_active == True,
                EventsEntity.status == "active"
            ).scalar()
            
            return {
                "total_eventss": total_count,
                "active_eventss": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting events statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_events_service(db_session: Session) -> EventsService:
    """Create events service instance"""
    return EventsService(db_session)
