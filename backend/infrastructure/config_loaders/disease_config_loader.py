"""
Disease Configuration Loader

Loads and manages JSON configuration files for the disease system,
providing centralized access to disease types, stages, transmission modes, and treatment types.
Follows the established JSON configuration pattern used by other systems.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from functools import lru_cache

logger = logging.getLogger(__name__)


class DiseaseConfigLoader:
    """Loads and manages disease system configuration from JSON files"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the config loader with the config directory"""
        if config_dir is None:
            # Point to the data/systems/disease directory
            config_dir = Path(__file__).parent.parent.parent.parent / "data" / "systems" / "disease"
        self.config_dir = Path(config_dir)
        self._config_cache = {}
        
    @lru_cache(maxsize=1)
    def load_disease_enums(self) -> Dict[str, Any]:
        """Load disease enum configurations from JSON file"""
        return self._load_config_file("disease_enums.json")
    
    @lru_cache(maxsize=1)
    def load_disease_profiles(self) -> Dict[str, Any]:
        """Load disease profile configurations from JSON file"""
        return self._load_config_file("disease_profiles.json")
    
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Load a specific configuration file with error handling"""
        if filename in self._config_cache:
            return self._config_cache[filename]
            
        config_file = self.config_dir / filename
        if not config_file.exists():
            logger.warning(f"Disease configuration file not found: {config_file}")
            return {}
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self._config_cache[filename] = config_data
            logger.info(f"Loaded disease configuration: {filename}")
            return config_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in disease config file {config_file}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading disease config file {config_file}: {e}")
            return {}
    
    # Disease Type methods
    def get_disease_types(self) -> Dict[str, Any]:
        """Get all disease type configurations"""
        return self.load_disease_enums().get("disease_types", {})
    
    def get_disease_type_ids(self) -> List[str]:
        """Get list of valid disease type IDs"""
        return list(self.get_disease_types().keys())
    
    def get_disease_type(self, disease_type_id: str) -> Optional[Dict[str, Any]]:
        """Get specific disease type configuration"""
        return self.get_disease_types().get(disease_type_id)
    
    def validate_disease_type(self, disease_type_id: str) -> bool:
        """Validate if disease type ID exists"""
        return disease_type_id in self.get_disease_type_ids()
    
    # Disease Stage methods
    def get_disease_stages(self) -> Dict[str, Any]:
        """Get all disease stage configurations"""
        return self.load_disease_enums().get("disease_stages", {})
    
    def get_disease_stage_ids(self) -> List[str]:
        """Get list of valid disease stage IDs"""
        return list(self.get_disease_stages().keys())
    
    def get_disease_stage(self, stage_id: str) -> Optional[Dict[str, Any]]:
        """Get specific disease stage configuration"""
        return self.get_disease_stages().get(stage_id)
    
    def validate_disease_stage(self, stage_id: str) -> bool:
        """Validate if disease stage ID exists"""
        return stage_id in self.get_disease_stage_ids()
    
    # Transmission Mode methods
    def get_transmission_modes(self) -> Dict[str, Any]:
        """Get all transmission mode configurations"""
        return self.load_disease_enums().get("transmission_modes", {})
    
    def get_transmission_mode_ids(self) -> List[str]:
        """Get list of valid transmission mode IDs"""
        return list(self.get_transmission_modes().keys())
    
    def get_transmission_mode(self, mode_id: str) -> Optional[Dict[str, Any]]:
        """Get specific transmission mode configuration"""
        return self.get_transmission_modes().get(mode_id)
    
    def validate_transmission_mode(self, mode_id: str) -> bool:
        """Validate if transmission mode ID exists"""
        return mode_id in self.get_transmission_mode_ids()
    
    # Treatment Type methods
    def get_treatment_types(self) -> Dict[str, Any]:
        """Get all treatment type configurations"""
        return self.load_disease_enums().get("treatment_types", {})
    
    def get_treatment_type_ids(self) -> List[str]:
        """Get list of valid treatment type IDs"""
        return list(self.get_treatment_types().keys())
    
    def get_treatment_type(self, treatment_id: str) -> Optional[Dict[str, Any]]:
        """Get specific treatment type configuration"""
        return self.get_treatment_types().get(treatment_id)
    
    def validate_treatment_type(self, treatment_id: str) -> bool:
        """Validate if treatment type ID exists"""
        return treatment_id in self.get_treatment_type_ids()
    
    # Disease Profile methods
    def get_disease_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get specific disease profile configuration"""
        profiles = self.load_disease_profiles().get("disease_profiles", [])
        for profile in profiles:
            if profile.get("id") == profile_id:
                return profile
        return None
    
    def get_all_disease_profiles(self) -> List[Dict[str, Any]]:
        """Get all disease profile configurations"""
        return self.load_disease_profiles().get("disease_profiles", [])
    
    def get_disease_profile_ids(self) -> List[str]:
        """Get list of all disease profile IDs"""
        profiles = self.get_all_disease_profiles()
        return [profile.get("id") for profile in profiles if profile.get("id")]


# Global instance for easy access (singleton pattern)
_disease_config_loader = None

def get_disease_config_loader() -> DiseaseConfigLoader:
    """Get the singleton instance of DiseaseConfigLoader"""
    global _disease_config_loader
    if _disease_config_loader is None:
        _disease_config_loader = DiseaseConfigLoader()
    return _disease_config_loader


# Validation helper functions following established pattern
def validate_disease_type(disease_type_id: str) -> bool:
    """Validate disease type ID"""
    return get_disease_config_loader().validate_disease_type(disease_type_id)

def validate_disease_stage(stage_id: str) -> bool:
    """Validate disease stage ID"""
    return get_disease_config_loader().validate_disease_stage(stage_id)

def validate_transmission_mode(mode_id: str) -> bool:
    """Validate transmission mode ID"""
    return get_disease_config_loader().validate_transmission_mode(mode_id)

def validate_treatment_type(treatment_id: str) -> bool:
    """Validate treatment type ID"""
    return get_disease_config_loader().validate_treatment_type(treatment_id)

def get_disease_type_data(disease_type_id: str) -> Optional[Dict[str, Any]]:
    """Get disease type data"""
    return get_disease_config_loader().get_disease_type(disease_type_id)

def get_valid_disease_types() -> List[str]:
    """Get all valid disease type IDs"""
    return get_disease_config_loader().get_disease_type_ids()

def get_valid_disease_stages() -> List[str]:
    """Get all valid disease stage IDs"""
    return get_disease_config_loader().get_disease_stage_ids()

def get_valid_transmission_modes() -> List[str]:
    """Get all valid transmission mode IDs"""
    return get_disease_config_loader().get_transmission_mode_ids()

def get_valid_treatment_types() -> List[str]:
    """Get all valid treatment type IDs"""
    return get_disease_config_loader().get_treatment_type_ids() 