"""
Disease Infrastructure Service

Coordinates infrastructure components for the disease system including
repositories, configuration loaders, and external integrations.
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from ..repositories.disease_repository import DiseaseRepository, get_disease_repository
from ..repositories.disease_outbreak_repository import DiseaseOutbreakRepository, get_disease_outbreak_repository
from ..config_loaders.disease_config_loader import DiseaseConfigLoader, get_disease_config_loader

logger = logging.getLogger(__name__)


class DiseaseInfrastructureService:
    """
    Infrastructure service that coordinates disease system technical components.
    
    Provides a unified interface for accessing repositories, configuration,
    and other infrastructure concerns.
    """
    
    def __init__(
        self,
        db_session: Session = None,
        disease_repository: DiseaseRepository = None,
        outbreak_repository: DiseaseOutbreakRepository = None,
        config_loader: DiseaseConfigLoader = None
    ):
        self.db_session = db_session
        self._disease_repository = disease_repository
        self._outbreak_repository = outbreak_repository
        self._config_loader = config_loader
    
    @property
    def disease_repository(self) -> DiseaseRepository:
        """Get the disease repository instance."""
        if self._disease_repository is None:
            self._disease_repository = get_disease_repository(self.db_session)
        return self._disease_repository
    
    @property
    def outbreak_repository(self) -> DiseaseOutbreakRepository:
        """Get the disease outbreak repository instance."""
        if self._outbreak_repository is None:
            self._outbreak_repository = get_disease_outbreak_repository(self.db_session)
        return self._outbreak_repository
    
    @property
    def config_loader(self) -> DiseaseConfigLoader:
        """Get the disease configuration loader instance."""
        if self._config_loader is None:
            self._config_loader = get_disease_config_loader()
        return self._config_loader
    
    # Disease Profile Operations
    def get_disease_profiles_from_config(self) -> List[Dict[str, Any]]:
        """Get all disease profiles from configuration."""
        return self.config_loader.get_disease_profiles()
    
    def get_disease_profile_config(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific disease profile from configuration."""
        return self.config_loader.get_disease_profile_by_id(profile_id)
    
    def get_disease_profiles_by_type_config(self, disease_type: str) -> List[Dict[str, Any]]:
        """Get disease profiles by type from configuration."""
        return self.config_loader.get_disease_profiles_by_type(disease_type)
    
    # Environmental Configuration
    def get_environmental_factors_config(self) -> Dict[str, Any]:
        """Get environmental factors configuration."""
        return self.config_loader.get_environmental_factors()
    
    def get_crowding_multipliers_config(self) -> Dict[str, float]:
        """Get crowding multipliers from configuration."""
        return self.config_loader.get_crowding_multipliers()
    
    def get_hygiene_multipliers_config(self) -> Dict[str, float]:
        """Get hygiene multipliers from configuration."""
        return self.config_loader.get_hygiene_multipliers()
    
    def get_healthcare_multipliers_config(self) -> Dict[str, float]:
        """Get healthcare multipliers from configuration."""
        return self.config_loader.get_healthcare_multipliers()
    
    # Outbreak Configuration
    def get_outbreak_parameters_config(self) -> Dict[str, Any]:
        """Get outbreak parameters from configuration."""
        return self.config_loader.get_outbreak_parameters()
    
    def get_stage_thresholds_config(self) -> Dict[str, float]:
        """Get disease stage thresholds from configuration."""
        return self.config_loader.get_stage_thresholds()
    
    def get_intervention_effectiveness_config(self) -> Dict[str, Any]:
        """Get intervention effectiveness from configuration."""
        return self.config_loader.get_intervention_effectiveness()
    
    # Database Operations - Diseases
    def get_disease_by_id(self, disease_id: UUID) -> Optional[Dict[str, Any]]:
        """Get disease by ID from database."""
        return self.disease_repository.get_disease_by_id(disease_id)
    
    def get_disease_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get disease by name from database."""
        return self.disease_repository.get_disease_by_name(name)
    
    def get_diseases_by_type(self, disease_type: str) -> List[Dict[str, Any]]:
        """Get diseases by type from database."""
        return self.disease_repository.get_diseases_by_type(disease_type)
    
    def get_active_diseases(self) -> List[Dict[str, Any]]:
        """Get all active diseases from database."""
        return self.disease_repository.get_active_diseases()
    
    def create_disease(self, disease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new disease in database."""
        return self.disease_repository.create_disease(disease_data)
    
    def update_disease(self, disease_id: UUID, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing disease in database."""
        return self.disease_repository.update_disease(disease_id, update_data)
    
    def delete_disease(self, disease_id: UUID) -> bool:
        """Delete a disease from database."""
        return self.disease_repository.delete_disease(disease_id)
    
    # Database Operations - Outbreaks
    def get_outbreak_by_id(self, outbreak_id: UUID) -> Optional[Dict[str, Any]]:
        """Get outbreak by ID from database."""
        return self.outbreak_repository.get_outbreak_by_id(outbreak_id)
    
    def get_outbreaks_by_region(self, region_id: UUID) -> List[Dict[str, Any]]:
        """Get outbreaks by region from database."""
        return self.outbreak_repository.get_outbreaks_by_region(region_id)
    
    def get_outbreaks_by_population(self, population_id: UUID) -> List[Dict[str, Any]]:
        """Get outbreaks by population from database."""
        return self.outbreak_repository.get_outbreaks_by_population(population_id)
    
    def get_active_outbreaks(self) -> List[Dict[str, Any]]:
        """Get all active outbreaks from database."""
        return self.outbreak_repository.get_active_outbreaks()
    
    def get_outbreaks_by_disease(self, disease_profile_id: UUID) -> List[Dict[str, Any]]:
        """Get outbreaks by disease from database."""
        return self.outbreak_repository.get_outbreaks_by_disease(disease_profile_id)
    
    def get_outbreaks_by_stage(self, stage: str) -> List[Dict[str, Any]]:
        """Get outbreaks by stage from database."""
        return self.outbreak_repository.get_outbreaks_by_stage(stage)
    
    def create_outbreak(self, outbreak_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new outbreak in database."""
        return self.outbreak_repository.create_outbreak(outbreak_data)
    
    def update_outbreak(self, outbreak_id: UUID, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing outbreak in database."""
        return self.outbreak_repository.update_outbreak(outbreak_id, update_data)
    
    def end_outbreak(self, outbreak_id: UUID) -> bool:
        """End an outbreak."""
        return self.outbreak_repository.end_outbreak(outbreak_id)
    
    def delete_outbreak(self, outbreak_id: UUID) -> bool:
        """Delete an outbreak from database."""
        return self.outbreak_repository.delete_outbreak(outbreak_id)
    
    # Utility Methods
    def reload_configuration(self):
        """Reload disease configuration from files."""
        self.config_loader.reload_config()
        logger.info("Disease configuration reloaded")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall disease system infrastructure status."""
        try:
            active_diseases = len(self.get_active_diseases())
            active_outbreaks = len(self.get_active_outbreaks())
            config_profiles = len(self.get_disease_profiles_from_config())
            
            return {
                "status": "healthy",
                "active_diseases": active_diseases,
                "active_outbreaks": active_outbreaks,
                "configured_profiles": config_profiles,
                "database_connected": self.db_session is not None,
                "config_loaded": self._config_loader is not None
            }
        except Exception as e:
            logger.error(f"Error getting disease system status: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "database_connected": False,
                "config_loaded": False
            }


# Global instance management
_disease_infrastructure_service = None

def get_disease_infrastructure_service(db_session: Session = None) -> DiseaseInfrastructureService:
    """Get the disease infrastructure service instance."""
    global _disease_infrastructure_service
    if _disease_infrastructure_service is None or db_session is not None:
        _disease_infrastructure_service = DiseaseInfrastructureService(db_session=db_session)
    return _disease_infrastructure_service 