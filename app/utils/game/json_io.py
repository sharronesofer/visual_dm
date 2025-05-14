"""JSON file I/O utilities."""

import json
from pathlib import Path
from typing import Any, Dict

def load_json(filename: str) -> Dict[str, Any]:
    """
    Load a JSON file from the data directory.
    
    Args:
        filename: Name of the JSON file to load
        
    Returns:
        Dict containing the JSON data
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    file_path = data_dir / filename
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: JSON file {filename} not found")
        return {}
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in file {filename}")
        return {}

def save_json(filename: str, data: Dict[str, Any]) -> bool:
    """
    Save data to a JSON file in the data directory.
    
    Args:
        filename: Name of the JSON file to save to
        data: Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    file_path = data_dir / filename
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON file {filename}: {e}")
        return False 