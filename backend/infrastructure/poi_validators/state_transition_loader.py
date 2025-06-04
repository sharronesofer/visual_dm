"""
State Transition Configuration Loader

Technical service to load state transition rules from JSON configuration files.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class StateTransitionConfigLoader:
    """Loads state transition configuration from JSON files"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "data/systems/poi/state_transitions.json"
        self._config_cache: Optional[Dict[str, Any]] = None
    
    def load_state_transitions(self) -> Dict[str, Any]:
        """Load state transition configuration from JSON"""
        if self._config_cache is not None:
            return self._config_cache
        
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.error(f"State transition config file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            self._config_cache = config
            logger.info(f"Loaded state transition config from {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading state transition config: {e}")
            return self._get_default_config()
    
    def get_transition_rules(self) -> Dict[str, Any]:
        """Get state transition rules"""
        config = self.load_state_transitions()
        return config.get("state_transitions", {})
    
    def get_condition_definitions(self) -> Dict[str, Any]:
        """Get condition definitions"""
        config = self.load_state_transitions()
        return config.get("condition_definitions", {})
    
    def get_poi_type_modifiers(self) -> Dict[str, Any]:
        """Get POI type modifiers"""
        config = self.load_state_transitions()
        return config.get("poi_type_modifiers", {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file loading fails"""
        return {
            "state_transitions": {},
            "condition_definitions": {},
            "poi_type_modifiers": {}
        }
    
    def reload_config(self):
        """Force reload of configuration"""
        self._config_cache = None
        self.load_state_transitions()


def create_state_transition_loader(config_path: Optional[str] = None) -> StateTransitionConfigLoader:
    """Factory function to create state transition loader"""
    return StateTransitionConfigLoader(config_path) 