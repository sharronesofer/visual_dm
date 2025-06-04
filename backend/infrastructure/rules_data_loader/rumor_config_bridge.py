"""
Rumor Configuration Bridge
--------------------------
Bridge between rumor business logic and technical infrastructure.
Implements dependency injection for rumor configuration loading.
"""

from typing import Dict, Any, Optional
from backend.systems.rumor.utils.rumor_rules import RumorConfigProvider, set_rumor_config_provider
from .config_loader import load_json_config


class RumorConfigBridge(RumorConfigProvider):
    """
    Implementation of RumorConfigProvider that bridges business logic to infrastructure.
    
    This class handles the technical aspects of configuration loading
    while allowing the rumor system to remain pure business logic.
    """
    
    def load_json_config(self, filename: str, fallback_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load JSON configuration using infrastructure.
        
        Args:
            filename: Name of the JSON file to load
            fallback_data: Fallback data if file doesn't exist
        
        Returns:
            Configuration dictionary
        """
        return load_json_config(filename, fallback_data)


def initialize_rumor_system() -> None:
    """
    Initialize the rumor system with proper configuration provider.
    
    This function should be called during application startup to inject
    the infrastructure dependencies into the business logic layer.
    """
    config_bridge = RumorConfigBridge()
    set_rumor_config_provider(config_bridge)


# Convenience function for backward compatibility
def setup_rumor_configuration() -> None:
    """Legacy alias for initialize_rumor_system."""
    initialize_rumor_system() 