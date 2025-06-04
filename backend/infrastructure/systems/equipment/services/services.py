"""
Equipment System Services

This module provides business logic services for the equipment system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from ..models.models import (
    EquipmentEntity,
    EquipmentModel,
    CreateEquipmentRequest,
    UpdateEquipmentRequest,
    EquipmentResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    EquipmentNotFoundError,
    EquipmentValidationError,
    EquipmentConflictError
)

logger = logging.getLogger(__name__)


class EquipmentService(BaseService[EquipmentEntity]):
    """Service class for equipment business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, EquipmentEntity)
        self.db = db_session

    async def create_equipment(
        self, 
        request: CreateEquipmentRequest,
        user_id: Optional[UUID] = None
    ) -> EquipmentResponse:
        """Create a new equipment"""
        try:
            logger.info(f"Creating equipment: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise EquipmentConflictError(f"Equipment with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = EquipmentEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created equipment {entity.id} successfully")
            return EquipmentResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating equipment: {str(e)}")
            self.db.rollback()
            raise

    async def get_equipment_by_id(self, equipment_id: UUID) -> Optional[EquipmentResponse]:
        """Get equipment by ID"""
        try:
            entity = self.db.query(EquipmentEntity).filter(
                EquipmentEntity.id == equipment_id,
                EquipmentEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return EquipmentResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting equipment {_equipment_id}: {str(e)}")
            raise

    async def update_equipment(
        self, 
        equipment_id: UUID, 
        request: UpdateEquipmentRequest
    ) -> EquipmentResponse:
        """Update existing equipment"""
        try:
            entity = await self._get_entity_by_id(equipment_id)
            if not entity:
                raise EquipmentNotFoundError(f"Equipment {_equipment_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated equipment {entity.id} successfully")
            return EquipmentResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating equipment {_equipment_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_equipment(self, equipment_id: UUID) -> bool:
        """Soft delete equipment"""
        try:
            entity = await self._get_entity_by_id(equipment_id)
            if not entity:
                raise EquipmentNotFoundError(f"Equipment {_equipment_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted equipment {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting equipment {_equipment_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_equipments(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[EquipmentResponse], int]:
        """List equipments with pagination and filters"""
        try:
            query = self.db.query(EquipmentEntity).filter(
                EquipmentEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(EquipmentEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        EquipmentEntity.name.ilike(f"%{search}%"),
                        EquipmentEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(EquipmentEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [EquipmentResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing equipments: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[EquipmentEntity]:
        """Get entity by name"""
        return self.db.query(EquipmentEntity).filter(
            EquipmentEntity.name == name,
            EquipmentEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[EquipmentEntity]:
        """Get entity by ID"""
        return self.db.query(EquipmentEntity).filter(
            EquipmentEntity.id == entity_id,
            EquipmentEntity.is_active == True
        ).first()

    async def get_equipment_statistics(self) -> Dict[str, Any]:
        """Get equipment system statistics"""
        try:
            total_count = self.db.query(func.count(EquipmentEntity.id)).filter(
                EquipmentEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(EquipmentEntity.id)).filter(
                EquipmentEntity.is_active == True,
                EquipmentEntity.status == "active"
            ).scalar()
            
            return {
                "total_equipments": total_count,
                "active_equipments": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting equipment statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_equipment_service(db_session: Session) -> EquipmentService:
    """Create equipment service instance"""
    return EquipmentService(db_session)
