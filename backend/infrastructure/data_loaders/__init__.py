"""
Data Loaders Infrastructure Module

Provides technical infrastructure for loading configuration data from various sources.
This module isolates data access and file I/O from business logic.
"""

# Magic system configuration loading
from .magic_config import get_magic_config_loader, create_magic_config_loader

__all__ = [
    "get_magic_config_loader",
    "create_magic_config_loader"
] 