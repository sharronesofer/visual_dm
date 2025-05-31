"""
JSON file I/O utilities.
"""

import json
import os
from typing import Any, Dict, Optional

def load_json(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load and parse a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Optional[Dict[str, Any]]: Parsed JSON data or None if error
    """
    try:
        print(f"📂 Loading from path: {os.path.abspath(filepath)}")
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error loading {filepath}: {e}")
        return None

def save_json(filepath: str, data: Dict[str, Any]) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        filepath: Path where to save the JSON file
        data: Data to save
        
    Returns:
        bool: True if save successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save JSON to {filepath}: {e}")
        return False 