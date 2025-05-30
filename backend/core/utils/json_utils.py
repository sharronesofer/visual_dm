"""
JSON utility functions for the backend.
"""

import json
import os
from typing import Any, Dict, Optional, Union
from pathlib import Path


def load_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data, empty dict if file doesn't exist or is invalid
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except (FileNotFoundError, json.JSONDecodeError, PermissionError) as e:
        print(f"Warning: Could not load JSON from {file_path}: {e}")
        return {}


def save_json(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save as JSON
        file_path: Path where to save the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, TypeError, PermissionError) as e:
        print(f"Warning: Could not save JSON to {file_path}: {e}")
        return False


def load_json_safe(file_path: str, default: Optional[Any] = None) -> Any:
    """
    Load JSON data from a file with a default fallback.
    
    Args:
        file_path: Path to the JSON file
        default: Default value to return if loading fails
        
    Returns:
        JSON data or default value
    """
    if default is None:
        default = {}
        
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return default 