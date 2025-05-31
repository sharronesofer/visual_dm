"""
Motif System Services

This module provides business logic services for the motif system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.motif.models import (
    MotifEntity,
    MotifModel,
    CreateMotifRequest,
    UpdateMotifRequest,
    MotifResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    MotifNotFoundError,
    MotifValidationError,
    MotifConflictError
)

logger = logging.getLogger(__name__)


class MotifService(BaseService[MotifEntity]):
    """Service class for motif business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, MotifEntity)
        self.db = db_session

    async def create_motif(
        self, 
        request: CreateMotifRequest,
        user_id: Optional[UUID] = None
    ) -> MotifResponse:
        """Create a new motif"""
        try:
            logger.info(f"Creating motif: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise MotifConflictError(f"Motif with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = MotifEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created motif {entity.id} successfully")
            return MotifResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating motif: {str(e)}")
            self.db.rollback()
            raise

    async def get_motif_by_id(self, motif_id: UUID) -> Optional[MotifResponse]:
        """Get motif by ID"""
        try:
            entity = self.db.query(MotifEntity).filter(
                MotifEntity.id == motif_id,
                MotifEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return MotifResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting motif {_motif_id}: {str(e)}")
            raise

    async def update_motif(
        self, 
        motif_id: UUID, 
        request: UpdateMotifRequest
    ) -> MotifResponse:
        """Update existing motif"""
        try:
            entity = await self._get_entity_by_id(motif_id)
            if not entity:
                raise MotifNotFoundError(f"Motif {_motif_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated motif {entity.id} successfully")
            return MotifResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating motif {_motif_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_motif(self, motif_id: UUID) -> bool:
        """Soft delete motif"""
        try:
            entity = await self._get_entity_by_id(motif_id)
            if not entity:
                raise MotifNotFoundError(f"Motif {_motif_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted motif {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting motif {_motif_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_motifs(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[MotifResponse], int]:
        """List motifs with pagination and filters"""
        try:
            query = self.db.query(MotifEntity).filter(
                MotifEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(MotifEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        MotifEntity.name.ilike(f"%{search}%"),
                        MotifEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(MotifEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [MotifResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing motifs: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[MotifEntity]:
        """Get entity by name"""
        return self.db.query(MotifEntity).filter(
            MotifEntity.name == name,
            MotifEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[MotifEntity]:
        """Get entity by ID"""
        return self.db.query(MotifEntity).filter(
            MotifEntity.id == entity_id,
            MotifEntity.is_active == True
        ).first()

    async def get_motif_statistics(self) -> Dict[str, Any]:
        """Get motif system statistics"""
        try:
            total_count = self.db.query(func.count(MotifEntity.id)).filter(
                MotifEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(MotifEntity.id)).filter(
                MotifEntity.is_active == True,
                MotifEntity.status == "active"
            ).scalar()
            
            return {
                "total_motifs": total_count,
                "active_motifs": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting motif statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_motif_service(db_session: Session) -> MotifService:
    """Create motif service instance"""
    return MotifService(db_session)
