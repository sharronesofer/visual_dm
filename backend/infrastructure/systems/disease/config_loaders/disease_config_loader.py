"""
Disease Configuration Loader

Technical utility for loading disease configuration from JSON files.
Handles disease profiles, outbreak parameters, and environmental factors.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from uuid import UUID

logger = logging.getLogger(__name__)


class DiseaseConfigLoader:
    """Loads disease configuration from JSON files"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Optional path to disease configuration JSON
        """
        if config_path is None:
            # Default config path in data directory
            config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "systems" / "disease" / "disease_profiles.json"
        
        self.config_path = Path(config_path)
        self._config_cache = None
    
    def load_config(self) -> Dict[str, Any]:
        """Load disease configuration from JSON file."""
        if self._config_cache is not None:
            return self._config_cache
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded disease configuration from {self.config_path}")
            self._config_cache = config
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found at {self.config_path}, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide default disease configuration as fallback."""
        return {
            "disease_profiles": [
                {
                    "id": "default-fever",
                    "name": "Common Fever",
                    "disease_type": "fever",
                    "description": "A common fever affecting populations",
                    "mortality_rate": 0.05,
                    "transmission_rate": 0.2,
                    "incubation_days": 2,
                    "recovery_days": 5,
                    "immunity_duration_days": 180,
                    "transmission_modes": ["airborne", "contact"],
                    "contagious_period_days": 5,
                    "crowding_factor": 1.3,
                    "hygiene_factor": 1.2,
                    "healthcare_factor": 0.8,
                    "temperature_factor": 1.0,
                    "humidity_factor": 1.0,
                    "seasonal_preference": None,
                    "seasonal_multiplier": 1.0,
                    "targets_young": False,
                    "targets_old": False,
                    "targets_weak": True,
                    "targets_healthy": False,
                    "symptoms": ["fever", "fatigue", "headache"],
                    "complications": ["dehydration", "weakness"],
                    "treatable_with": ["herbal", "natural"],
                    "treatment_effectiveness": {
                        "herbal": 0.6,
                        "alchemical": 0.7,
                        "magical": 0.8,
                        "divine": 0.5,
                        "quarantine": 0.4,
                        "natural": 0.3
                    },
                    "productivity_impact": 0.2,
                    "treatment_cost_modifier": 1.0,
                    "is_magical": False,
                    "is_cursed": False,
                    "magical_resistance_effective": False,
                    "divine_resistance_effective": False,
                    "properties": {
                        "origin": "natural",
                        "common_disease": True
                    }
                }
            ],
            "environmental_factors": {
                "temperature_effects": {
                    "optimal_range": [15, 25],
                    "cold_penalty": 0.8,
                    "hot_penalty": 1.2
                },
                "humidity_effects": {
                    "optimal_range": [0.4, 0.7],
                    "dry_penalty": 0.9,
                    "wet_penalty": 1.3
                },
                "crowding_multipliers": {
                    "sparse": 0.7,
                    "normal": 1.0,
                    "crowded": 1.5,
                    "overcrowded": 2.0
                },
                "hygiene_multipliers": {
                    "excellent": 0.5,
                    "good": 0.7,
                    "poor": 1.3,
                    "terrible": 1.8
                },
                "healthcare_multipliers": {
                    "excellent": 0.4,
                    "good": 0.6,
                    "basic": 0.8,
                    "poor": 1.0,
                    "none": 1.2
                }
            },
            "outbreak_parameters": {
                "stage_thresholds": {
                    "emerging": 0.1,
                    "spreading": 0.3,
                    "peak": 0.6,
                    "declining": 0.3,
                    "endemic": 0.15,
                    "eradicated": 0.0
                },
                "intervention_effectiveness": {
                    "quarantine": {
                        "base_effectiveness": 0.6,
                        "compliance_factor": 0.8
                    },
                    "treatment": {
                        "early_stage_bonus": 0.3,
                        "late_stage_penalty": 0.5
                    }
                }
            }
        }
    
    def get_disease_profiles(self) -> List[Dict[str, Any]]:
        """Get all disease profiles."""
        config = self.load_config()
        return config.get("disease_profiles", [])
    
    def get_disease_profile_by_id(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific disease profile by ID."""
        profiles = self.get_disease_profiles()
        for profile in profiles:
            if profile.get("id") == profile_id:
                return profile
        return None
    
    def get_disease_profiles_by_type(self, disease_type: str) -> List[Dict[str, Any]]:
        """Get all disease profiles of a specific type."""
        profiles = self.get_disease_profiles()
        return [profile for profile in profiles if profile.get("disease_type") == disease_type]
    
    def get_environmental_factors(self) -> Dict[str, Any]:
        """Get environmental factor configuration."""
        config = self.load_config()
        return config.get("environmental_factors", {})
    
    def get_temperature_effects(self) -> Dict[str, Any]:
        """Get temperature effect configuration."""
        env_factors = self.get_environmental_factors()
        return env_factors.get("temperature_effects", {})
    
    def get_humidity_effects(self) -> Dict[str, Any]:
        """Get humidity effect configuration."""
        env_factors = self.get_environmental_factors()
        return env_factors.get("humidity_effects", {})
    
    def get_crowding_multipliers(self) -> Dict[str, float]:
        """Get crowding multiplier configuration."""
        env_factors = self.get_environmental_factors()
        return env_factors.get("crowding_multipliers", {})
    
    def get_hygiene_multipliers(self) -> Dict[str, float]:
        """Get hygiene multiplier configuration."""
        env_factors = self.get_environmental_factors()
        return env_factors.get("hygiene_multipliers", {})
    
    def get_healthcare_multipliers(self) -> Dict[str, float]:
        """Get healthcare multiplier configuration."""
        env_factors = self.get_environmental_factors()
        return env_factors.get("healthcare_multipliers", {})
    
    def get_outbreak_parameters(self) -> Dict[str, Any]:
        """Get outbreak parameter configuration."""
        config = self.load_config()
        return config.get("outbreak_parameters", {})
    
    def get_stage_thresholds(self) -> Dict[str, float]:
        """Get disease stage threshold configuration."""
        outbreak_params = self.get_outbreak_parameters()
        return outbreak_params.get("stage_thresholds", {})
    
    def get_intervention_effectiveness(self) -> Dict[str, Any]:
        """Get intervention effectiveness configuration."""
        outbreak_params = self.get_outbreak_parameters()
        return outbreak_params.get("intervention_effectiveness", {})
    
    def reload_config(self):
        """Reload configuration from file."""
        self._config_cache = None
        self.load_config()
    
    def save_default_config_file(self):
        """Save the default configuration to file for editing."""
        default_config = self._get_default_config()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Saved default disease configuration to {self.config_path}")


# Global instance for easy access
_config_loader = None

def get_disease_config_loader() -> DiseaseConfigLoader:
    """Get the global disease configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = DiseaseConfigLoader()
    return _config_loader 