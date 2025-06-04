"""
Disease Repository Implementation

Database adapter that implements the disease repository protocol
for the business services.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.models.disease.models import (
    DiseaseEntity,
    DiseaseResponse
)
from backend.infrastructure.shared.services import BaseService
from backend.infrastructure.shared.exceptions import (
    DiseaseNotFoundError,
    DiseaseValidationError,
    DiseaseConflictError
)

logger = logging.getLogger(__name__)


class DiseaseRepository(BaseService[DiseaseEntity]):
    """
    Database repository implementation for disease entities.
    
    This adapter implements the repository protocol expected by the business services
    and handles all database operations.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, DiseaseEntity)
        self.db = db_session

    def get_disease_by_id(self, disease_id: UUID) -> Optional[Dict[str, Any]]:
        """Get disease by ID and return as business data"""
        try:
            entity = self.db.query(DiseaseEntity).filter(
                DiseaseEntity.id == disease_id,
                DiseaseEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error getting disease {disease_id}: {str(e)}")
            raise

    def get_disease_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get disease by name and return as business data"""
        try:
            entity = self.db.query(DiseaseEntity).filter(
                DiseaseEntity.name == name,
                DiseaseEntity.is_active == True
            ).first()
            
            if not entity:
                return None
                
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error getting disease by name {name}: {str(e)}")
            raise

    def get_diseases_by_type(self, disease_type: str) -> List[Dict[str, Any]]:
        """Get all diseases of a specific type"""
        try:
            entities = self.db.query(DiseaseEntity).filter(
                DiseaseEntity.disease_type == disease_type,
                DiseaseEntity.is_active == True
            ).all()
            
            return [self._entity_to_business_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting diseases by type {disease_type}: {str(e)}")
            raise

    def get_active_diseases(self) -> List[Dict[str, Any]]:
        """Get all active diseases"""
        try:
            entities = self.db.query(DiseaseEntity).filter(
                DiseaseEntity.status == 'active',
                DiseaseEntity.is_active == True
            ).all()
            
            return [self._entity_to_business_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting active diseases: {str(e)}")
            raise

    def create_disease(self, disease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new disease entity"""
        try:
            entity_data = {
                "name": disease_data["name"],
                "description": disease_data.get("description"),
                "disease_type": disease_data.get("disease_type", "fever"),
                "status": disease_data.get("status", "active"),
                "mortality_rate": disease_data.get("mortality_rate", 0.1),
                "transmission_rate": disease_data.get("transmission_rate", 0.3),
                "incubation_days": disease_data.get("incubation_days", 3),
                "recovery_days": disease_data.get("recovery_days", 7),
                "immunity_duration_days": disease_data.get("immunity_duration_days", 365),
                "crowding_factor": disease_data.get("crowding_factor", 1.5),
                "hygiene_factor": disease_data.get("hygiene_factor", 1.3),
                "healthcare_factor": disease_data.get("healthcare_factor", 0.7),
                "targets_young": disease_data.get("targets_young", False),
                "targets_old": disease_data.get("targets_old", False),
                "targets_weak": disease_data.get("targets_weak", False),
                "properties": disease_data.get("properties", {}),
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            entity = DiseaseEntity(**entity_data)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created disease {entity.id}")
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error creating disease: {str(e)}")
            self.db.rollback()
            raise

    def update_disease(self, disease_id: UUID, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing disease entity"""
        try:
            entity = self.db.query(DiseaseEntity).filter(
                DiseaseEntity.id == disease_id,
                DiseaseEntity.is_active == True
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
            
            logger.info(f"Updated disease {disease_id}")
            return self._entity_to_business_data(entity)
            
        except Exception as e:
            logger.error(f"Error updating disease {disease_id}: {str(e)}")
            self.db.rollback()
            raise

    def delete_disease(self, disease_id: UUID) -> bool:
        """Soft delete a disease entity"""
        try:
            entity = self.db.query(DiseaseEntity).filter(
                DiseaseEntity.id == disease_id,
                DiseaseEntity.is_active == True
            ).first()
            
            if not entity:
                return False
            
            entity.is_active = False
            entity.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"Deleted disease {disease_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting disease {disease_id}: {str(e)}")
            self.db.rollback()
            raise

    def _entity_to_business_data(self, entity: DiseaseEntity) -> Dict[str, Any]:
        """Convert database entity to business data format"""
        return {
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "disease_type": entity.disease_type,
            "status": entity.status,
            "mortality_rate": entity.mortality_rate,
            "transmission_rate": entity.transmission_rate,
            "incubation_days": entity.incubation_days,
            "recovery_days": entity.recovery_days,
            "immunity_duration_days": entity.immunity_duration_days,
            "crowding_factor": entity.crowding_factor,
            "hygiene_factor": entity.hygiene_factor,
            "healthcare_factor": entity.healthcare_factor,
            "targets_young": entity.targets_young,
            "targets_old": entity.targets_old,
            "targets_weak": entity.targets_weak,
            "properties": entity.properties or {},
            "created_at": entity.created_at,
            "updated_at": entity.updated_at
        }


# Global instance management
_disease_repository = None

def get_disease_repository(db_session: Session = None) -> DiseaseRepository:
    """Get the disease repository instance."""
    global _disease_repository
    if _disease_repository is None or db_session is not None:
        if db_session is None:
            from backend.infrastructure.database import get_db_session
            db_session = next(get_db_session())
        _disease_repository = DiseaseRepository(db_session)
    return _disease_repository 