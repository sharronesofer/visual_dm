"""
Integration System Services

This module provides business logic services for the integration system
according to the Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.integration.models import (
    IntegrationEntity,
    IntegrationModel,
    CreateIntegrationRequest,
    UpdateIntegrationRequest,
    IntegrationResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    IntegrationNotFoundError,
    IntegrationValidationError,
    IntegrationConflictError
)

logger = logging.getLogger(__name__)


class IntegrationService(BaseService[IntegrationEntity]):
    """Service class for integration business logic"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, IntegrationEntity)
        self.db = db_session

    async def create_integration(
        self, 
        request: CreateIntegrationRequest,
        user_id: Optional[UUID] = None
    ) -> IntegrationResponse:
        """Create a new integration"""
        try:
            logger.info(f"Creating integration: {request.name}")
            
            # Validate unique constraints
            existing = await self._get_by_name(request.name)
            if existing:
                raise IntegrationConflictError(f"Integration with name '{request.name}' already exists")
            
            # Create entity
            entity_data = {
                "name": request.name,
                "description": request.description,
                "properties": request.properties or {},
                "status": "active",
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = IntegrationEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created integration {entity.id} successfully")
            return IntegrationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error creating integration: {str(e)}")
            self.db.rollback()
            raise

    async def get_integration_by_id(self, integration_id: UUID) -> Optional[IntegrationResponse]:
        """Get integration by ID"""
        try:
            entity = self.db.query(IntegrationEntity).filter(
                IntegrationEntity.id == integration_id,
                IntegrationEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return IntegrationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error getting integration {_integration_id}: {str(e)}")
            raise

    async def update_integration(
        self, 
        integration_id: UUID, 
        request: UpdateIntegrationRequest
    ) -> IntegrationResponse:
        """Update existing integration"""
        try:
            entity = await self._get_entity_by_id(integration_id)
            if not entity:
                raise IntegrationNotFoundError(f"Integration {_integration_id} not found")
            
            # Update fields
            update_data = request.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(entity)
            
            logger.info(f"Updated integration {entity.id} successfully")
            return IntegrationResponse.from_orm(entity)
            
        except Exception as e:
            logger.error(f"Error updating integration {_integration_id}: {str(e)}")
            self.db.rollback()
            raise

    async def delete_integration(self, integration_id: UUID) -> bool:
        """Soft delete integration"""
        try:
            entity = await self._get_entity_by_id(integration_id)
            if not entity:
                raise IntegrationNotFoundError(f"Integration {_integration_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted integration {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting integration {_integration_id}: {str(e)}")
            self.db.rollback()
            raise

    async def list_integrations(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[IntegrationResponse], int]:
        """List integrations with pagination and filters"""
        try:
            query = self.db.query(IntegrationEntity).filter(
                IntegrationEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(IntegrationEntity.status == status)
            
            if search:
                query = query.filter(
                    or_(
                        IntegrationEntity.name.ilike(f"%{search}%"),
                        IntegrationEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(IntegrationEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to response models
            responses = [IntegrationResponse.from_orm(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing integrations: {str(e)}")
            raise

    async def _get_by_name(self, name: str) -> Optional[IntegrationEntity]:
        """Get entity by name"""
        return self.db.query(IntegrationEntity).filter(
            IntegrationEntity.name == name,
            IntegrationEntity.is_active == True
        ).first()

    async def _get_entity_by_id(self, entity_id: UUID) -> Optional[IntegrationEntity]:
        """Get entity by ID"""
        return self.db.query(IntegrationEntity).filter(
            IntegrationEntity.id == entity_id,
            IntegrationEntity.is_active == True
        ).first()

    async def get_integration_statistics(self) -> Dict[str, Any]:
        """Get integration system statistics"""
        try:
            total_count = self.db.query(func.count(IntegrationEntity.id)).filter(
                IntegrationEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(IntegrationEntity.id)).filter(
                IntegrationEntity.is_active == True,
                IntegrationEntity.status == "active"
            ).scalar()
            
            return {
                "total_integrations": total_count,
                "active_integrations": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting integration statistics: {str(e)}")
            raise


# Factory function for dependency injection
def create_integration_service(db_session: Session) -> IntegrationService:
    """Create integration service instance"""
    return IntegrationService(db_session)
