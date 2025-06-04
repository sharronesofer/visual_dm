"""
Espionage Infrastructure Service

Handles technical infrastructure for the Economic Espionage System including
database operations, API integrations, and external service coordination.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.espionage.models import (
    CreateEspionageRequest,
    UpdateEspionageRequest
)
from backend.infrastructure.models.espionage_models import EspionageEntity
from backend.infrastructure.repositories.espionage_repository import EspionageRepository
from backend.infrastructure.schemas.espionage_schemas import EspionageSchema
from backend.infrastructure.database import get_db_session


class EspionageInfrastructureService:
    """Infrastructure service for espionage entities - handles technical operations"""

    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        self.repository = EspionageRepository(self.db_session)

    async def create_espionage_entity(self, request: CreateEspionageRequest) -> EspionageSchema:
        """Create a new espionage entity in the database"""
        entity = EspionageEntity(
            name=request.name,
            description=request.description,
            properties=request.properties or {}
        )
        
        created_entity = await self.repository.create(entity)
        return EspionageSchema.model_validate(created_entity)

    async def get_espionage_entity(self, entity_id: UUID) -> Optional[EspionageSchema]:
        """Get an espionage entity by ID from database"""
        entity = await self.repository.get_by_id(entity_id)
        if entity:
            return EspionageSchema.model_validate(entity)
        return None

    async def update_espionage_entity(self, entity_id: UUID, request: UpdateEspionageRequest) -> Optional[EspionageSchema]:
        """Update an espionage entity in the database"""
        entity = await self.repository.get_by_id(entity_id)
        if not entity:
            return None

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        entity.updated_at = datetime.utcnow()
        updated_entity = await self.repository.update(entity)
        return EspionageSchema.model_validate(updated_entity)

    async def delete_espionage_entity(self, entity_id: UUID) -> bool:
        """Delete an espionage entity from database"""
        return await self.repository.delete(entity_id)

    async def list_espionage_entities(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[EspionageSchema]:
        """List espionage entities from database with optional filtering"""
        filters = {}
        if status:
            filters["status"] = status

        entities = await self.repository.list_with_filters(filters, skip, limit)
        return [EspionageSchema.model_validate(entity) for entity in entities] 