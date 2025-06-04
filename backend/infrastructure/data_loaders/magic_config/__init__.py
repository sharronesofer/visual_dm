"""
Magic Configuration Loader Module

Provides technical infrastructure for loading magic system configuration from JSON files.
This module isolates file I/O operations from business logic.
"""

from .magic_config_loader import (
    MagicConfigLoader,
    get_magic_config_loader,
    create_magic_config_loader
)

from .magic_config_repository_adapter import (
    MagicConfigRepositoryAdapter,
    create_magic_config_repository
)

from .damage_type_service_adapter import (
    DamageTypeServiceAdapter,
    create_damage_type_service
)

__all__ = [
    # Config loader
    "MagicConfigLoader",
    "get_magic_config_loader", 
    "create_magic_config_loader",
    
    # Adapters
    "MagicConfigRepositoryAdapter",
    "create_magic_config_repository",
    "DamageTypeServiceAdapter", 
    "create_damage_type_service"
] 