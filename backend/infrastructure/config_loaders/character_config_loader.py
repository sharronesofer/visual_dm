"""
Character Configuration Loader
-----------------------------
Centralized loader for all character-related JSON configuration files.
Provides caching and validation of configuration data.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from functools import lru_cache

from backend.infrastructure.utils.json_utils import load_json

logger = logging.getLogger(__name__)

class CharacterConfigLoader:
    """
    Loads and validates character configuration from JSON files.
    Provides caching to avoid repeated file reads.
    """
    
    _instance = None
    _config_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CharacterConfigLoader, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
            'data', 'systems', 'character'
        )
        
        # Fallback data directory for builders content
        self.builders_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
            'data', 'builders', 'content'
        )
        
        # Initialize cache
        self._cache = {}
    
    @lru_cache(maxsize=32)
    def load_skills_config(self) -> Dict[str, Any]:
        """Load skills configuration from JSON file."""
        try:
            config_path = os.path.join(self.config_dir, 'skills.json')
            return load_json(config_path)
        except Exception as e:
            logger.warning(f"Failed to load skills config: {e}. Using fallback.")
            return self._get_fallback_skills()
    
    @lru_cache(maxsize=32)
    def load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration from JSON file."""
        try:
            config_path = os.path.join(self.config_dir, 'validation_rules.json')
            return load_json(config_path)
        except Exception as e:
            logger.warning(f"Failed to load validation rules: {e}. Using fallback.")
            return self._get_fallback_validation_rules()
    
    @lru_cache(maxsize=32)
    def load_progression_rules(self) -> Dict[str, Any]:
        """Load progression rules configuration from JSON file."""
        try:
            config_path = os.path.join(self.config_dir, 'progression_rules.json')
            return load_json(config_path)
        except Exception as e:
            logger.warning(f"Failed to load progression rules: {e}. Using fallback.")
            return self._get_fallback_progression_rules()
    
    @lru_cache(maxsize=32)
    def load_personality_config(self) -> Dict[str, Any]:
        """
        Load personality traits configuration.
        Now supports the development bible's 6-attribute hidden personality system.
        
        Returns:
            Dictionary containing personality configuration
        """
        if 'personality' not in self._cache:
            try:
                config_path = os.path.join(self.config_dir, 'personality_traits.json')
                self._cache['personality'] = load_json(config_path)
            except Exception as e:
                logger.warning(f"Failed to load personality config: {e}")
                # Fallback configuration matching development bible
                self._cache['personality'] = {
                    "hidden_attributes": {
                        "attributes": {
                            "ambition": {"min_value": 0, "max_value": 6},
                            "integrity": {"min_value": 0, "max_value": 6},
                            "discipline": {"min_value": 0, "max_value": 6},
                            "impulsivity": {"min_value": 0, "max_value": 6},
                            "pragmatism": {"min_value": 0, "max_value": 6},
                            "resilience": {"min_value": 0, "max_value": 6}
                        }
                    },
                    "generation_rules": {
                        "base_mean": 3.0,
                        "base_std_dev": 1.2
                    },
                    "background_influences": {}
                }
        
        return self._cache['personality']
    
    @lru_cache(maxsize=32)
    def load_races_config(self) -> Dict[str, Any]:
        """Load races configuration from existing builders content."""
        try:
            races_path = os.path.join(self.builders_dir, 'races.json')
            return load_json(races_path)
        except Exception as e:
            logger.error(f"Failed to load races config: {e}")
            return {}
    
    @lru_cache(maxsize=32)
    def load_abilities_config(self) -> Dict[str, Any]:
        """Load abilities/feats configuration from existing builders content."""
        try:
            abilities_path = os.path.join(self.builders_dir, 'abilities.json')
            return load_json(abilities_path)
        except Exception as e:
            logger.error(f"Failed to load abilities config: {e}")
            return {"feats": []}
    
    def get_skill_list(self) -> List[str]:
        """Get list of all available skill names."""
        skills_config = self.load_skills_config()
        return list(skills_config.get("skills", {}).keys())
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific skill."""
        skills_config = self.load_skills_config()
        return skills_config.get("skills", {}).get(skill_name.lower())
    
    def get_skill_by_ability(self, ability: str) -> List[str]:
        """Get all skills that use a specific ability score."""
        skills_config = self.load_skills_config()
        skills = skills_config.get("skills", {})
        return [
            skill_name for skill_name, skill_data in skills.items()
            if skill_data.get("ability", "").upper() == ability.upper()
        ]
    
    def get_validation_limits(self) -> Dict[str, Any]:
        """Get character validation limits."""
        validation_config = self.load_validation_rules()
        return validation_config.get("character_limits", {})
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules."""
        validation_config = self.load_validation_rules()
        return validation_config.get("validation_rules", {})
    
    def get_error_message(self, error_key: str, **kwargs) -> str:
        """Get a formatted error message."""
        validation_config = self.load_validation_rules()
        error_messages = validation_config.get("error_messages", {})
        message_template = error_messages.get(error_key, f"Validation error: {error_key}")
        
        try:
            return message_template.format(**kwargs)
        except (KeyError, ValueError):
            return message_template
    
    def clear_cache(self):
        """Clear the configuration cache to force reload from files."""
        self.load_skills_config.cache_clear()
        self.load_validation_rules.cache_clear()
        self.load_progression_rules.cache_clear()
        self.load_personality_config.cache_clear()
        self.load_races_config.cache_clear()
        self.load_abilities_config.cache_clear()
        logger.info("Character configuration cache cleared")
    
    def _get_fallback_skills(self) -> Dict[str, Any]:
        """Fallback skills configuration if file loading fails."""
        return {
            "skills": {
                skill: {
                    "name": skill.replace("_", " ").title(),
                    "description": f"The {skill.replace('_', ' ')} skill",
                    "ability": "INT",
                    "category": "knowledge"
                }
                for skill in [
                    'acrobatics', 'animal_handling', 'arcana', 'athletics', 'deception',
                    'history', 'insight', 'intimidation', 'investigation', 'medicine',
                    'nature', 'perception', 'performance', 'persuasion', 'religion',
                    'sleight_of_hand', 'stealth', 'survival'
                ]
            }
        }
    
    def _get_fallback_validation_rules(self) -> Dict[str, Any]:
        """Fallback validation rules if file loading fails."""
        return {
            "character_limits": {
                "max_feats_level_1": 7,
                "max_skills": 18,
                "min_attribute_value": 8,
                "max_attribute_value": 15
            },
            "validation_rules": {
                "required_fields": ["character_name", "race"],
                "name_min_length": 2,
                "name_max_length": 50
            },
            "error_messages": {
                "name_too_short": "Character name too short",
                "name_too_long": "Character name too long",
                "race_required": "Race is required"
            }
        }
    
    def _get_fallback_progression_rules(self) -> Dict[str, Any]:
        """Fallback progression rules if file loading fails."""
        return {
            "derived_stats": {
                "hit_points": {
                    "base_per_level": 12,
                    "constitution_modifier": True
                },
                "magic_points": {
                    "base_per_level": 8,
                    "intelligence_scaling": True
                },
                "armor_class": {
                    "base_value": 10,
                    "dexterity_modifier": True
                }
            }
        }
    
    def get_hidden_attributes_config(self) -> Dict[str, Any]:
        """
        Get the hidden attributes configuration.
        
        Returns:
            Dictionary containing the 6 hidden attributes and their configurations
        """
        personality_config = self.load_personality_config()
        return personality_config.get("hidden_attributes", {})
    
    def get_hidden_attribute_info(self, attribute_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific hidden attribute.
        
        Args:
            attribute_name: Name of the hidden attribute (ambition, integrity, etc.)
            
        Returns:
            Dictionary containing attribute information or None if not found
        """
        hidden_attrs = self.get_hidden_attributes_config()
        attributes = hidden_attrs.get("attributes", {})
        return attributes.get(attribute_name.lower())
    
    def get_background_influences(self, background: str) -> Dict[str, Any]:
        """
        Get background influences on hidden attribute generation.
        
        Args:
            background: Character background name
            
        Returns:
            Dictionary containing attribute biases for the background
        """
        personality_config = self.load_personality_config()
        background_influences = personality_config.get("background_influences", {})
        return background_influences.get(background.lower(), {})
    
    def get_generation_rules(self) -> Dict[str, Any]:
        """
        Get rules for generating hidden personality attributes.
        
        Returns:
            Dictionary containing generation rules and parameters
        """
        personality_config = self.load_personality_config()
        return personality_config.get("generation_rules", {
            "base_mean": 3.0,
            "base_std_dev": 1.2,
            "min_total_variation": 8,
            "max_total_variation": 24
        })

# Global instance
config_loader = CharacterConfigLoader() 