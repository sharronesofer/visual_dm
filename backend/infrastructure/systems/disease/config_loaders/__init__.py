"""
Disease System Configuration Loaders

Infrastructure components for loading disease configuration from JSON files.
"""

from .disease_config_loader import (
    DiseaseConfigLoader,
    get_disease_config_loader
)

__all__ = [
    'DiseaseConfigLoader',
    'get_disease_config_loader'
] 