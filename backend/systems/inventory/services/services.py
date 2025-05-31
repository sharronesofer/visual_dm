"""
Inventory System Services

This module provides business logic services for the inventory system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.systems.inventory.models import (
    InventoryEntity,
    InventoryModel,
    CreateInventoryRequest,
    UpdateInventoryRequest,
    InventoryResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    InventoryNotFoundError,
    InventoryValidationError,
    InventoryConflictError
)

logger = logging.getLogger(__name__)


class InventoryService(BaseService[InventoryEntity]):
    """Service class for inventory business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, InventoryEntity)
        self.db = db_session

    async def create_inventory(
        self, 
        request: CreateInventoryRequest,
        user_id: Optional[UUID] = None
    ) -> InventoryResponse:
        """Create a new inventory"""
        try:
            logger.info(f"Creating inventory: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise InventoryConflictError(f"Inventory with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = InventoryEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created inventory {entity.id} successfully")
            return InventoryResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating inventory: {str(e)}")
            self.db.rollback()
            raise

    async def get_inventory_by_id(self, inventory_id: UUID) -> Optional[InventoryResponse]:
        """Get inventory by ID"""
        try:
            entity = self.db.query(InventoryEntity).filter(
                InventoryEntity.id == inventory_id,
                InventoryEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return InventoryResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting inventory {_inventory_id}: {str(e)}")
            raise

    async def update_inventory(
        self, 
        inventory_id: UUID, 
        request: UpdateInventoryRequest
    ) -> InventoryResponse:
        """Update existing inventory"""
        try:
            entity = await self._get_entity_by_id(inventory_id)
            if not entity:
                raise InventoryNotFoundError(f"Inventory {_inventory_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated inventory {entity.id} successfully")
            return InventoryResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating inventory {_inventory_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_inventory(self, inventory_id: UUID) -> bool:
        """Soft delete inventory"""
        try:
            entity = await self._get_entity_by_id(inventory_id)
            if not entity:
                raise InventoryNotFoundError(f"Inventory {_inventory_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted inventory {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting inventory {_inventory_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_inventorys(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[InventoryResponse], int]:
        """List inventorys with pagination and filters"""
        try:
            query = self.db.query(InventoryEntity).filter(
                InventoryEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(InventoryEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        InventoryEntity.name.ilike(f"%{search}%"),
                        InventoryEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(InventoryEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [InventoryResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing inventorys: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[InventoryEntity]:
        """Get entity by name"""
        return self.db.query(InventoryEntity).filter(
            InventoryEntity.name == name,
            InventoryEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[InventoryEntity]:
        """Get entity by ID"""
        return self.db.query(InventoryEntity).filter(
            InventoryEntity.id == entity_id,
            InventoryEntity.is_active == True
        ).first()

    async def get_inventory_statistics(self) -> Dict[str, Any]:
        """Get inventory system statistics"""
        try:
            total_count = self.db.query(func.count(InventoryEntity.id)).filter(
                InventoryEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(InventoryEntity.id)).filter(
                InventoryEntity.is_active == True,
                InventoryEntity.status == "active"
            ).scalar()
            
            return {
                "total_inventorys": total_count,
                "active_inventorys": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting inventory statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_inventory_service(db_session: Session) -> InventoryService:
    """Create inventory service instance"""
    return InventoryService(db_session)
