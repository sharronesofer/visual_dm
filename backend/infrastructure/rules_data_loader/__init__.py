"""
Rules Data Loader Infrastructure
---------------------------------
Technical infrastructure for loading rules configuration files.
Handles file I/O, JSON parsing, and error handling for rules system.
"""

from .config_loader import (
    load_json_config,
    reload_rules_config,
    RulesConfigError
)
from .rules_config_bridge import (
    RulesConfigBridge,
    initialize_rules_system,
    setup_rules_configuration
)
from .rumor_config_bridge import initialize_rumor_system

__all__ = [
    'load_json_config',
    'reload_rules_config', 
    'RulesConfigError',
    'RulesConfigBridge',
    'initialize_rules_system',
    'setup_rules_configuration',
    'initialize_rumor_system'
]

def initialize_all_systems() -> None:
    """
    Initialize all game systems with proper configuration providers.
    
    This function should be called during application startup to set up
    dependency injection for all systems that need configuration loading.
    """
    initialize_rules_system()
    initialize_rumor_system() 