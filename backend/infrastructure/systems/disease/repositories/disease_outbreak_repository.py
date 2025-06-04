"""
Disease Outbreak Repository Implementation

Database adapter for managing disease outbreak entities and their progression.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.models.disease.models import (
    DiseaseOutbreakEntity,
    DiseaseOutbreakResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    DiseaseNotFoundError,
    DiseaseValidationError,
    DiseaseConflictError
)

logger = logging.getLogger(__name__)


class DiseaseOutbreakRepository(BaseService[DiseaseOutbreakEntity]):
    """
    Database repository implementation for disease outbreak entities.
    
    Manages outbreak tracking, progression, and statistics.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, DiseaseOutbreakEntity)
        self.db = db_session

    def get_outbreak_by_id(self, outbreak_id: UUID) -> Optional[Dict[str, Any]]:
        """Get outbreak by ID and return as business data"""
        try:
            entity = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.id == outbreak_id,
                DiseaseOutbreakEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error getting outbreak {outbreak_id}: {str(e)}")
            raise

    def get_outbreaks_by_region(self, region_id: UUID) -> List[Dict[str, Any]]:
        """Get all outbreaks in a specific region"""
        try:
            entities = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.region_id == region_id,
                DiseaseOutbreakEntity.is_active == True
            ).all()
            
            return [self._entity_to_business_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting outbreaks for region {region_id}: {str(e)}")
            raise

    def get_outbreaks_by_population(self, population_id: UUID) -> List[Dict[str, Any]]:
        """Get all outbreaks affecting a specific population"""
        try:
            entities = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.population_id == population_id,
                DiseaseOutbreakEntity.is_active == True
            ).all()
            
            return [self._entity_to_business_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting outbreaks for population {population_id}: {str(e)}")
            raise

    def get_active_outbreaks(self) -> List[Dict[str, Any]]:
        """Get all currently active outbreaks"""
        try:
            entities = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.is_active == True,
                DiseaseOutbreakEntity.end_date.is_(None)
            ).all()
            
            return [self._entity_to_business_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting active outbreaks: {str(e)}")
            raise

    def get_outbreaks_by_disease(self, disease_profile_id: UUID) -> List[Dict[str, Any]]:
        """Get all outbreaks for a specific disease"""
        try:
            entities = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.disease_profile_id == disease_profile_id,
                DiseaseOutbreakEntity.is_active == True
            ).all()
            
            return [self._entity_to_business_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting outbreaks for disease {disease_profile_id}: {str(e)}")
            raise

    def get_outbreaks_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """Get all outbreaks in a specific stage"""
        try:
            entities = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.stage == stage,
                DiseaseOutbreakEntity.is_active == True
            ).all()
            
            return [self._entity_to_business_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting outbreaks by stage {stage}: {str(e)}")
            raise

    def create_outbreak(self, outbreak_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new disease outbreak"""
        try:
            entity_data = {
                "disease_profile_id": outbreak_data["disease_profile_id"],
                "region_id": outbreak_data.get("region_id"),
                "population_id": outbreak_data.get("population_id"),
                "stage": outbreak_data.get("stage", "emerging"),
                "infected_count": outbreak_data.get("infected_count", 0),
                "recovered_count": outbreak_data.get("recovered_count", 0),
                "death_count": outbreak_data.get("death_count", 0),
                "immune_count": outbreak_data.get("immune_count", 0),
                "days_active": outbreak_data.get("days_active", 0),
                "peak_infected": outbreak_data.get("peak_infected", 0),
                "peak_day": outbreak_data.get("peak_day"),
                "current_crowding_modifier": outbreak_data.get("current_crowding_modifier", 1.0),
                "current_hygiene_modifier": outbreak_data.get("current_hygiene_modifier", 1.0),
                "current_healthcare_modifier": outbreak_data.get("current_healthcare_modifier", 1.0),
                "current_seasonal_modifier": outbreak_data.get("current_seasonal_modifier", 1.0),
                "current_temperature_modifier": outbreak_data.get("current_temperature_modifier", 1.0),
                "current_humidity_modifier": outbreak_data.get("current_humidity_modifier", 1.0),
                "treatment_effectiveness": outbreak_data.get("treatment_effectiveness", 1.0),
                "quarantine_active": outbreak_data.get("quarantine_active", False),
                "quarantine_effectiveness": outbreak_data.get("quarantine_effectiveness", 0.0),
                "economic_damage": outbreak_data.get("economic_damage", 0.0),
                "trade_disruption": outbreak_data.get("trade_disruption", 0.0),
                "start_date": outbreak_data.get("start_date", datetime.utcnow()),
                "origin_source": outbreak_data.get("origin_source"),
                "patient_zero_location": outbreak_data.get("patient_zero_location"),
                "properties": outbreak_data.get("properties", {}),
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = DiseaseOutbreakEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created outbreak {entity.id}")
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error creating outbreak: {str(e)}")
            self.db.rollback()
            raise

    def update_outbreak(self, outbreak_id: UUID, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing outbreak"""
        try:
            entity = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.id == outbreak_id,
                DiseaseOutbreakEntity.is_active == True
            ).first()
            
            if not entity:
                return None
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
            
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Updated outbreak {outbreak_id}")
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error updating outbreak {outbreak_id}: {str(e)}")
            self.db.rollback()
            raise

    def end_outbreak(self, outbreak_id: UUID, end_date: datetime = None) -> bool:
        """Mark an outbreak as ended"""
        try:
            entity = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.id == outbreak_id,
                DiseaseOutbreakEntity.is_active == True
            ).first()
            
            if not entity:
                return False
            
            entity.end_date = end_date or datetime.utcnow()
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Ended outbreak {outbreak_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error ending outbreak {outbreak_id}: {str(e)}")
            self.db.rollback()
            raise

    def delete_outbreak(self, outbreak_id: UUID) -> bool:
        """Soft delete an outbreak"""
        try:
            entity = self.db.query(DiseaseOutbreakEntity).filter(
                DiseaseOutbreakEntity.id == outbreak_id,
                DiseaseOutbreakEntity.is_active == True
            ).first()
            
            if not entity:
                return False
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Deleted outbreak {outbreak_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting outbreak {outbreak_id}: {str(e)}")
            self.db.rollback()
            raise

    def _entity_to_business_data(self, entity: DiseaseOutbreakEntity) -> Dict[str, Any]:
        """Convert database entity to business data format"""
        return {
            "id": entity.id,
            "disease_profile_id": entity.disease_profile_id,
            "region_id": entity.region_id,
            "population_id": entity.population_id,
            "stage": entity.stage,
            "is_active": entity.is_active,
            "infected_count": entity.infected_count,
            "recovered_count": entity.recovered_count,
            "death_count": entity.death_count,
            "immune_count": entity.immune_count,
            "days_active": entity.days_active,
            "peak_infected": entity.peak_infected,
            "peak_day": entity.peak_day,
            "current_crowding_modifier": entity.current_crowding_modifier,
            "current_hygiene_modifier": entity.current_hygiene_modifier,
            "current_healthcare_modifier": entity.current_healthcare_modifier,
            "current_seasonal_modifier": entity.current_seasonal_modifier,
            "current_temperature_modifier": entity.current_temperature_modifier,
            "current_humidity_modifier": entity.current_humidity_modifier,
            "treatment_effectiveness": entity.treatment_effectiveness,
            "quarantine_active": entity.quarantine_active,
            "quarantine_effectiveness": entity.quarantine_effectiveness,
            "economic_damage": entity.economic_damage,
            "trade_disruption": entity.trade_disruption,
            "start_date": entity.start_date,
            "end_date": entity.end_date,
            "origin_source": entity.origin_source,
            "patient_zero_location": entity.patient_zero_location,
            "properties": entity.properties or {},
            "created_at": entity.created_at,
            "updated_at": entity.updated_at
        }


# Global instance management
_disease_outbreak_repository = None

def get_disease_outbreak_repository(db_session: Session = None) -> DiseaseOutbreakRepository:
    """Get the disease outbreak repository instance."""
    global _disease_outbreak_repository
    if _disease_outbreak_repository is None or db_session is not None:
        if db_session is None:
            from backend.infrastructure.database import get_db_session
            db_session = next(get_db_session())
        _disease_outbreak_repository = DiseaseOutbreakRepository(db_session)
    return _disease_outbreak_repository 