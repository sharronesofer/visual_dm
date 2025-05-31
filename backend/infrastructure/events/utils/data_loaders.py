"""
Utility functions for loading game data from JSON files.
"""

import os
import json
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """Base class for loading game data from JSON files."""
    
    @staticmethod
    def load_json_file(file_path: str) -> Any:
        """Load a JSON file and return its contents."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return None

class DamageTypeLoader:
    """Loader for damage types."""
    
    _damage_types = None
    
    @classmethod
    def load_damage_types(cls) -> Dict[str, str]:
        """Load damage types from the weapons.json file."""
        if cls._damage_types is not None:
            return cls._damage_types
            
        # Initialize with fallback/default damage types in case file loading fails
        default_types = {
            "BLUDGEONING": "bludgeoning",
            "PIERCING": "piercing",
            "SLASHING": "slashing",
            "FIRE": "fire",
            "COLD": "cold",
            "LIGHTNING": "lightning",
            "THUNDER": "thunder",
            "ACID": "acid",
            "POISON": "poison",
            "PSYCHIC": "psychic",
            "NECROTIC": "necrotic",
            "RADIANT": "radiant",
            "FORCE": "force"
        }
        
        # Try to load from weapons schema which defines valid damage types
        try:
            base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                     'data', 'modding', 'weapons', 'weapon.schema.json')
            if os.path.exists(base_path):
                schema_data = DataLoader.load_json_file(base_path)
                if schema_data and 'properties' in schema_data:
                    # Extract damage types from the weapon schema
                    damage_type_enum = schema_data['properties']['damage']['properties']['type']['enum']
                    cls._damage_types = {dt.upper(): dt for dt in damage_type_enum}
                    logger.info(f"Loaded {len(cls._damage_types)} damage types from weapon schema")
                    return cls._damage_types
        except Exception as e:
            logger.error(f"Error loading damage types from schema: {e}")
        
        # Fallback: load from weapons.json to extract unique damage types
        try:
            base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
                                     'data', 'modding', 'weapons.json')
            if os.path.exists(base_path):
                weapons_data = DataLoader.load_json_file(base_path)
                if weapons_data:
                    # Extract unique damage types from weapons
                    unique_types = set()
                    for weapon in weapons_data:
                        if 'damage_type' in weapon and weapon['damage_type']:
                            unique_types.add(weapon['damage_type'])
                    
                    # Convert to dictionary
                    if unique_types:
                        cls._damage_types = {dt.upper(): dt for dt in unique_types}
                        logger.info(f"Loaded {len(cls._damage_types)} damage types from weapons.json")
                        return cls._damage_types
        except Exception as e:
            logger.error(f"Error loading damage types from weapons.json: {e}")
        
        # If everything fails, use the default types
        logger.warning("Using fallback damage types")
        cls._damage_types = default_types
        return cls._damage_types

    @classmethod
    def get_damage_types(cls) -> Dict[str, str]:
        """Get the loaded damage types or load them if not already loaded."""
        if cls._damage_types is None:
            return cls.load_damage_types()
        return cls._damage_types 