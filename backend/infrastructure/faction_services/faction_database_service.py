"""
Faction Database Service

This module provides database operations for faction entities,
separated from business logic according to clean architecture principles.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.models.faction.models import (
    FactionEntity,
    CreateFactionRequest,
    UpdateFactionRequest,
    FactionResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    FactionNotFoundError,
    FactionConflictError,
    NotFoundError,
    ValidationError
)

logger = logging.getLogger(__name__)


class FactionDatabaseService(BaseService[FactionEntity]):
    """Database service layer for faction operations"""
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, FactionEntity)
        self.db_session = db_session

    async def create_faction_entity(self, faction_entity: FactionEntity) -> FactionEntity:
        """Create a new faction entity in the database"""
        try:
            self.db_session.add(faction_entity)
            self.db_session.flush()  # Get the ID
            
            logger.info(f"Created faction: {faction_entity.name} (ID: {faction_entity.id})")
            return faction_entity
            
        except Exception as e:
            logger.error(f"Error creating faction entity: {e}")
            self.db_session.rollback()
            raise

    async def get_faction_by_id(self, faction_id: UUID) -> Optional[FactionEntity]:
        """Get faction entity by ID"""
        try:
            entity = self.db_session.query(FactionEntity).filter(
                FactionEntity.id == faction_id,
                FactionEntity.is_active == True
            ).first()
            
            return entity
            
        except Exception as e:
            logger.error(f"Error getting faction {faction_id}: {str(e)}")
            raise

    async def get_faction_by_name(self, name: str) -> Optional[FactionEntity]:
        """Get faction by name"""
        return self.db_session.query(FactionEntity).filter(
            FactionEntity.name == name,
            FactionEntity.is_active == True
        ).first()

    async def update_faction_entity(self, entity: FactionEntity) -> FactionEntity:
        """Update existing faction entity"""
        try:
            entity.updated_at = datetime.utcnow()
            self.db_session.commit()
            self.db_session.refresh(entity)
            
            logger.info(f"Updated faction {entity.id} successfully")
            return entity
            
        except Exception as e:
            logger.error(f"Error updating faction {entity.id}: {str(e)}")
            self.db_session.rollback()
            raise

    async def delete_faction_entity(self, entity: FactionEntity) -> bool:
        """Soft delete faction entity"""
        try:
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            logger.info(f"Deleted faction {entity.id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting faction {entity.id}: {str(e)}")
            self.db_session.rollback()
            raise

    async def list_factions(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[FactionEntity], int]:
        """List factions with pagination and filtering"""
        try:
            query = self.db_session.query(FactionEntity).filter(
                FactionEntity.is_active == True
            )
            
            if status:
                query = query.filter(FactionEntity.status == status)
                
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        FactionEntity.name.ilike(search_term),
                        FactionEntity.description.ilike(search_term)
                    )
                )
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.offset(offset).limit(size).all()
            
            return entities, total_count
            
        except Exception as e:
            logger.error(f"Error listing factions: {str(e)}")
            raise

    async def get_faction_statistics(self) -> Dict[str, Any]:
        """Get faction statistics from database"""
        try:
            total_count = self.db_session.query(FactionEntity).filter(
                FactionEntity.is_active == True
            ).count()
            
            active_count = self.db_session.query(FactionEntity).filter(
                FactionEntity.is_active == True,
                FactionEntity.status == 'active'
            ).count()
            
            # Calculate average hidden attributes
            avg_ambition = self.db_session.query(func.avg(FactionEntity.hidden_ambition)).filter(
                FactionEntity.is_active == True
            ).scalar() or 0
            
            avg_integrity = self.db_session.query(func.avg(FactionEntity.hidden_integrity)).filter(
                FactionEntity.is_active == True
            ).scalar() or 0
            
            return {
                "total_factions": total_count,
                "active_factions": active_count,
                "average_ambition": round(float(avg_ambition), 2),
                "average_integrity": round(float(avg_integrity), 2),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting faction statistics: {str(e)}")
            raise


def create_faction_database_service(db_session: Session) -> FactionDatabaseService:
    """Factory function to create faction database service"""
    return FactionDatabaseService(db_session) 