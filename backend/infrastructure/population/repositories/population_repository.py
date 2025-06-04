"""
Population Repository Implementation

Database adapter that implements the population repository protocol
for the business services.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.models.population.models import (
    PopulationEntity,
    PopulationResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    PopulationNotFoundError,
    PopulationValidationError,
    PopulationConflictError
)

logger = logging.getLogger(__name__)


class PopulationRepository(BaseService[PopulationEntity]):
    """
    Database repository implementation for population entities.
    
    This adapter implements the repository protocol expected by the business services
    and handles all database operations.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, PopulationEntity)
        self.db = db_session

    def get_population_by_id(self, population_id: UUID) -> Optional[Dict[str, Any]]:
        """Get population by ID and return as business data"""
        try:
            entity = self.db.query(PopulationEntity).filter(
                PopulationEntity.id == population_id,
                PopulationEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error getting population {population_id}: {str(e)}")
            raise

    def get_population_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get population by name and return as business data"""
        try:
            entity = self.db.query(PopulationEntity).filter(
                PopulationEntity.name == name,
                PopulationEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error getting population by name {name}: {str(e)}")
            raise

    def create_population(self, population_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new population entity"""
        try:
            entity_data = {
                "name": population_data["name"],
                "description": population_data.get("description"),
                "status": population_data.get("status", "active"),
                "properties": population_data.get("properties", {}),
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = PopulationEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created population {entity.id}")
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error creating population: {str(e)}")
            self.db.rollback()
            raise

    def update_population(self, population_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing population entity"""
        try:
            population_id = population_data["id"]
            entity = self.db.query(PopulationEntity).filter(
                PopulationEntity.id == population_id,
                PopulationEntity.is_active == True
            ).first()
            
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            # Update fields
            for field, value in population_data.items():
                if field != "id" and hasattr(entity, field):
                    setattr(entity, field, value)
            
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Updated population {entity.id}")
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error updating population: {str(e)}")
            self.db.rollback()
            raise

    def delete_population(self, population_id: UUID) -> bool:
        """Soft delete population entity"""
        try:
            entity = self.db.query(PopulationEntity).filter(
                PopulationEntity.id == population_id,
                PopulationEntity.is_active == True
            ).first()
            
            if not entity:
                raise PopulationNotFoundError(f"Population {population_id} not found")
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Deleted population {entity.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting population {population_id}: {str(e)}")
            self.db.rollback()
            raise

    def list_populations(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List populations with pagination and filters"""
        try:
            query = self.db.query(PopulationEntity).filter(
                PopulationEntity.is_active == True
            )
            
            # Apply filters
            if status:
                query = query.filter(PopulationEntity.status == status)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        PopulationEntity.name.ilike(search_term),
                        PopulationEntity.description.ilike(search_term)
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.offset(offset).limit(size).all()
            
            # Convert to business data
            populations = [self._entity_to_business_data(entity) for entity in entities]
            
            return populations, total
            
        except Exception as e:
            logger.error(f"Error listing populations: {str(e)}")
            raise

    def get_population_statistics(self) -> Dict[str, Any]:
        """Get population statistics"""
        try:
            total_populations = self.db.query(PopulationEntity).filter(
                PopulationEntity.is_active == True
            ).count()
            
            status_counts = self.db.query(
                PopulationEntity.status,
                func.count(PopulationEntity.id)
            ).filter(
                PopulationEntity.is_active == True
            ).group_by(PopulationEntity.status).all()
            
            return {
                "total_populations": total_populations,
                "status_distribution": dict(status_counts),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting population statistics: {str(e)}")
            raise

    def _entity_to_business_data(self, entity: PopulationEntity) -> Dict[str, Any]:
        """Convert database entity to business data format"""
        return {
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "status": entity.status,
            "properties": entity.properties or {},
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
            "is_active": entity.is_active
        }


def create_population_repository(db_session: Session) -> PopulationRepository:
    """Factory function to create population repository"""
    return PopulationRepository(db_session) 