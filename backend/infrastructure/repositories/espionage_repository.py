"""
Espionage Repository

Data access layer for the Economic Espionage System.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.infrastructure.models.espionage_models import EspionageEntity
from backend.infrastructure.repositories.base_repository import BaseRepository


class EspionageRepository(BaseRepository[EspionageEntity]):
    """Repository for espionage entities"""

    def __init__(self, db_session: Session):
        super().__init__(EspionageEntity, db_session)

    async def find_by_status(self, status: str) -> List[EspionageEntity]:
        """Find espionage entities by status"""
        return self.db_session.query(self.model).filter(
            self.model.status == status,
            self.model.is_active == True
        ).all()

    async def find_by_name_pattern(self, pattern: str) -> List[EspionageEntity]:
        """Find espionage entities by name pattern"""
        return self.db_session.query(self.model).filter(
            self.model.name.ilike(f"%{pattern}%"),
            self.model.is_active == True
        ).all()

    async def list_with_filters(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[EspionageEntity]:
        """List entities with dynamic filters"""
        query = self.db_session.query(self.model).filter(self.model.is_active == True)
        
        for field, value in filters.items():
            if hasattr(self.model, field):
                query = query.filter(getattr(self.model, field) == value)
        
        return query.offset(skip).limit(limit).all()

    async def count_by_status(self, status: str) -> int:
        """Count entities by status"""
        return self.db_session.query(self.model).filter(
            self.model.status == status,
            self.model.is_active == True
        ).count()

    async def get_active_entities(self) -> List[EspionageEntity]:
        """Get all active espionage entities"""
        return self.db_session.query(self.model).filter(
            self.model.is_active == True
        ).all() 