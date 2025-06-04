"""
Rules Configuration Bridge
--------------------------
Bridge between rules business logic and technical infrastructure.
Implements dependency injection for rules configuration loading.
"""

from typing import Dict, Any, Optional
from backend.systems.rules.rules import RulesConfigProvider, set_config_provider
from .config_loader import load_json_config


class RulesConfigBridge(RulesConfigProvider):
    """
    Implementation of RulesConfigProvider that bridges business logic to infrastructure.
    
    This class handles the technical aspects of configuration loading
    while allowing the rules system to remain pure business logic.
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


def initialize_rules_system() -> None:
    """
    Initialize the rules system with proper configuration provider.
    
    This function should be called during application startup to inject
    the infrastructure dependencies into the business logic layer.
    """
    config_bridge = RulesConfigBridge()
    set_config_provider(config_bridge)


# Convenience function for backward compatibility
def setup_rules_configuration() -> None:
    """Legacy alias for initialize_rules_system."""
    initialize_rules_system() 