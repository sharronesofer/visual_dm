"""
Configuration Loaders Infrastructure

Technical adapters for loading configuration data from external sources
like JSON files, databases, or remote services.
"""

from .json_config_loader import JsonConfigLoader
from .tension_config import (
    TensionConfigManager,
    TensionConfig,
    RevoltConfig,
    ConflictTriggerConfig,
    CalculationConstants
)
from .disease_config_loader import DiseaseConfigLoader, get_disease_config_loader

__all__ = [
    "JsonConfigLoader",
    "TensionConfigManager",
    "TensionConfig",
    "RevoltConfig", 
    "ConflictTriggerConfig",
    "CalculationConstants",
    "DiseaseConfigLoader",
    "get_disease_config_loader"
] 