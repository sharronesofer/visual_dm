"""
Visual Model Utilities
--------------------
Utilities for working with character visual models, including randomization,
serialization, and preset management.
"""

import json
import random
from typing import Dict, Any, List, Optional

# Serialization Constants
SERIALIZATION_VERSION = "1.0"

class RandomCharacterGenerator:
    """
    Generates random character customization data with weighted probabilities and feature locking.
    """
    def __init__(self, feature_weights: Dict[str, Dict[Any, float]]):
        self.feature_weights = feature_weights  # e.g., {"hair_color": {"blonde": 0.2, "black": 0.5, ...}}

    def weighted_choice(self, choices: Dict[Any, float]) -> Any:
        total = sum(choices.values())
        r = random.uniform(0, total)
        upto = 0
        for k, w in choices.items():
            if upto + w >= r:
                return k
            upto += w
        assert False, "Shouldn't get here"

    def generate(self, locked: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a random character customization dict, respecting locked features.
        """
        locked = locked or {}
        result = dict(locked)
        for feature, weights in self.feature_weights.items():
            if feature not in result:
                result[feature] = self.weighted_choice(weights)
        return result

def serialize_character(character: Any) -> str:
    """
    Serialize a character model to a JSON string, including versioning.
    """
    data = {
        "version": SERIALIZATION_VERSION,
        "character": character.to_dict()
    }
    return json.dumps(data, indent=2)

def deserialize_character(data: str, character_cls: Any) -> Any:
    """
    Deserialize a character model from a JSON string.
    """
    obj = json.loads(data)
    version = obj.get("version", "1.0")
    # Future: handle migrations based on version
    return character_cls.from_dict(obj["character"])

def load_preset(preset_name: str, preset_dir: str = "presets") -> Dict[str, Any]:
    """
    Load a character preset from a JSON file.
    """
    import os
    file_path = os.path.join(preset_dir, f"{preset_name}.json")
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading preset '{preset_name}': {str(e)}")

def save_preset(preset_data: Dict[str, Any], preset_name: str, preset_dir: str = "presets") -> None:
    """
    Save a character preset to a JSON file.
    """
    import os
    os.makedirs(preset_dir, exist_ok=True)
    file_path = os.path.join(preset_dir, f"{preset_name}.json")
    
    with open(file_path, 'w') as f:
        json.dump(preset_data, f, indent=2)

__all__ = [
    'RandomCharacterGenerator', 'serialize_character', 'deserialize_character',
    'load_preset', 'save_preset', 'SERIALIZATION_VERSION'
] 