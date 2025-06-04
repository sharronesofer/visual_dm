"""
DataUtils package - compatibility layer.

This package provides imports from the existing data/utils/data_file_loader module
for backward compatibility with existing import paths.
"""

# Import from the existing data/utils location
from backend.infrastructure.data.utils.data_file_loader import *

# Import from the new game data loader module
from .game_data_loader import load_data, get_default_data

__all__ = [
    'DataFileLoader',
    'get_loader',
    'load_data_file',
    'load_json_file',
    'load_data_directory',
    'save_data_file',
    'get_file_metadata',
    'find_data_dir',
    'ensure_directory',
    'safe_write_json',
    'backup_file',
    # Game data loading functions
    'load_data',
    'get_default_data'
] 