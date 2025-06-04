"""
POI Repository - Database Access Layer

This module provides database operations for the POI system,
separated from business logic according to Development Bible standards.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.systems.poi.models import (
    PoiEntity,
    PoiModel,
    CreatePoiRequest,
    UpdatePoiRequest,
    PoiResponse
)
from backend.infrastructure.shared.exceptions import (
    PoiNotFoundError,
    PoiValidationError,
    PoiConflictError
)

logger = logging.getLogger(__name__)


# Import the business domain model for protocol compliance
class PoiData:
    """Business domain POI data structure (repeated here for repository compliance)"""
    def __init__(self, 
                 id: UUID,
                 name: str,
                 description: Optional[str] = None,
                 poi_type: str = 'village',
                 state: str = 'active',
                 properties: Optional[Dict[str, Any]] = None,
                 population: int = 0,
                 max_population: int = 100,
                 prosperity_level: float = 0.5,
                 happiness: float = 0.5):
        self.id = id
        self.name = name
        self.description = description
        self.poi_type = poi_type
        self.state = state
        self.properties = properties or {}
        self.population = population
        self.max_population = max_population
        self.prosperity_level = prosperity_level
        self.happiness = happiness


class PoiRepository:
    """Repository for POI database operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_poi_by_id(self, poi_id: UUID) -> Optional[PoiData]:
        """Get POI entity by ID and convert to business domain model"""
        try:
            entity = self.db.query(PoiEntity).filter(
                PoiEntity.id == poi_id,
                PoiEntity.is_active == True
            ).first()
            
            if entity:
                return self._entity_to_poi_data(entity)
            return None
            
        except Exception as e:
            logger.error(f"Error getting poi {poi_id}: {str(e)}")
            raise

    def get_poi_by_name(self, name: str) -> Optional[PoiData]:
        """Get POI entity by name and convert to business domain model"""
        try:
            entity = self.db.query(PoiEntity).filter(
                PoiEntity.name == name,
                PoiEntity.is_active == True
            ).first()
            
            if entity:
                return self._entity_to_poi_data(entity)
            return None
            
        except Exception as e:
            logger.error(f"Error getting poi by name {name}: {str(e)}")
            raise

    def create_poi(self, poi_data: PoiData) -> PoiData:
        """Create a new POI entity from business domain model"""
        try:
            entity_data = {
                'id': poi_data.id,
                'name': poi_data.name,
                'description': poi_data.description,
                'poi_type': poi_data.poi_type,
                'state': poi_data.state,  # Changed from status to state
                'properties': poi_data.properties,
                'population': poi_data.population,
                'max_population': poi_data.max_population,
                'created_at': datetime.utcnow(),
                'is_active': True
            }
            
            entity = PoiEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            return self._entity_to_poi_data(entity)
            
        except Exception as e:
            logger.error(f"Error creating poi: {str(e)}")
            self.db.rollback()
            raise

    def update_poi(self, poi_data: PoiData) -> PoiData:
        """Update existing POI entity from business domain model"""
        try:
            entity = self.db.query(PoiEntity).filter(
                PoiEntity.id == poi_data.id,
                PoiEntity.is_active == True
            ).first()
            
            if not entity:
                raise PoiNotFoundError(f"POI with ID {poi_data.id} not found")
            
            # Update entity fields
            entity.name = poi_data.name
            entity.description = poi_data.description
            entity.poi_type = poi_data.poi_type
            entity.state = poi_data.state
            entity.properties = poi_data.properties
            entity.population = poi_data.population
            entity.max_population = poi_data.max_population
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(entity)
            
            return self._entity_to_poi_data(entity)
            
        except Exception as e:
            logger.error(f"Error updating poi {poi_data.id}: {str(e)}")
            self.db.rollback()
            raise

    def delete_poi(self, poi_id: UUID) -> bool:
        """Soft delete POI"""
        try:
            entity = self.db.query(PoiEntity).filter(
                PoiEntity.id == poi_id,
                PoiEntity.is_active == True
            ).first()
            
            if entity:
                entity.is_active = False
                entity.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting poi {poi_id}: {str(e)}")
            self.db.rollback()
            raise

    def list_pois(
        self,
        page: int = 1,
        size: int = 50,
        state: Optional[str] = None,  # Changed from status to state
        search: Optional[str] = None
    ) -> Tuple[List[PoiData], int]:
        """List POIs with pagination and filters, returning business domain models"""
        try:
            query = self.db.query(PoiEntity).filter(
                PoiEntity.is_active == True
            )
            
            # Apply filters
            if state:  # Changed from status to state
                query = query.filter(PoiEntity.state == state)
            
            if search:
                query = query.filter(
                    or_(
                        PoiEntity.name.ilike(f"%{search}%"),
                        PoiEntity.description.ilike(f"%{search}%")
                    )
                )
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            offset = (page - 1) * size
            entities = query.order_by(PoiEntity.created_at.desc()).offset(offset).limit(size).all()
            
            # Convert to business domain models
            poi_data_list = [self._entity_to_poi_data(entity) for entity in entities]
            
            return poi_data_list, total
            
        except Exception as e:
            logger.error(f"Error listing pois: {str(e)}")
            raise

    def get_poi_statistics(self) -> Dict[str, Any]:
        """Get POI system statistics"""
        try:
            total_count = self.db.query(func.count(PoiEntity.id)).filter(
                PoiEntity.is_active == True
            ).scalar()
            
            active_count = self.db.query(func.count(PoiEntity.id)).filter(
                PoiEntity.is_active == True,
                PoiEntity.state == "active"  # Changed from status to state
            ).scalar()
            
            return {
                "total_pois": total_count,
                "active_pois": active_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting poi statistics: {str(e)}")
            raise

    def _entity_to_poi_data(self, entity: PoiEntity) -> PoiData:
        """Convert database entity to business domain model"""
        return PoiData(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            poi_type=entity.poi_type,
            state=entity.state,  # Changed from status to state
            properties=entity.properties or {},
            population=entity.population or 0,
            max_population=entity.max_population or 100,
            prosperity_level=0.5,  # Default value, could be calculated
            happiness=0.5  # Default value, could be calculated
        )


def create_poi_repository(db_session: Session) -> PoiRepository:
    """Factory function to create POI repository"""
    return PoiRepository(db_session) 