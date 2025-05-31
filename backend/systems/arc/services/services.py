"""
Arc System Services

This module provides business logic services for the arc system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.arc.models import (
    Arc,
    ArcModel,
    CreateArcRequest,
    UpdateArcRequest,
    ArcResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    ArcNotFoundError,
    ArcValidationError,
    ArcConflictError
)

logger = logging.getLogger(__name__)


class ArcService(BaseService[Arc]):
    """Service class for arc business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, Arc)
        self.db = db_session

    async def create_arc(
        self, 
        request: CreateArcRequest,
        user_id: Optional[UUID] = None
    ) -> ArcResponse:
        """Create a new arc"""
        try:
            logger.info(f"Creating arc: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise ArcConflictError(f"Arc with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = Arc(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created arc {entity.id} successfully")
            return ArcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating arc: {str(e)}")
            self.db.rollback()
            raise

    async def get_arc_by_id(self, arc_id: UUID) -> Optional[ArcResponse]:
        """Get arc by ID"""
        try:
            entity = self.db.query(Arc).filter(
                Arc.id == arc_id,
                Arc.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return ArcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting arc {_arc_id}: {str(e)}")
            raise

    async def update_arc(
        self, 
        arc_id: UUID, 
        request: UpdateArcRequest
    ) -> ArcResponse:
        """Update existing arc"""
        try:
            entity = await self._get_entity_by_id(arc_id)
            if not entity:
                raise ArcNotFoundError(f"Arc {_arc_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated arc {entity.id} successfully")
            return ArcResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating arc {_arc_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_arc(self, arc_id: UUID) -> bool:
        """Soft delete arc"""
        try:
            entity = await self._get_entity_by_id(arc_id)
            if not entity:
                raise ArcNotFoundError(f"Arc {_arc_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted arc {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting arc {_arc_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_arcs(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[ArcResponse], int]:
        """List arcs with pagination and filters"""
        try:
            query = self.db.query(Arc).filter(
                Arc.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(Arc.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        Arc.name.ilike(f"%{search}%"),
                        Arc.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(Arc.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [ArcResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing arcs: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[Arc]:
        """Get entity by name"""
        return self.db.query(Arc).filter(
            Arc.name == name,
            Arc.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[Arc]:
        """Get entity by ID"""
        return self.db.query(Arc).filter(
            Arc.id == entity_id,
            Arc.is_active == True
        ).first()

    async def get_arc_statistics(self) -> Dict[str, Any]:
        """Get arc system statistics"""
        try:
            total_count = self.db.query(func.count(Arc.id)).filter(
                Arc.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(Arc.id)).filter(
                Arc.is_active == True,
                Arc.status == "active"
            ).scalar()
            
            return {
                "total_arcs": total_count,
                "active_arcs": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting arc statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_arc_service(db_session: Session) -> ArcService:
    """Create arc service instance"""
    return ArcService(db_session)
