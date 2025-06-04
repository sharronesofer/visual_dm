"""
Character Builder
---------------
Canonical character builder class for creating and modifying character data. 
Translates input into structured JSON-compatible data ready for storage or gameplay. 
Supports race selection, attribute assignment, abilities, skills, starter kits, and derived attributes.

This is the single canonical character builder - backend/systems/character/core/character_builder_class.py 
should be deprecated in favor of this implementation.
"""

import os
import random
import logging
from datetime import datetime
from uuid import uuid4
import uuid
from typing import Dict, Any, List, Optional

# Updated imports for the new structure
from backend.infrastructure.utils.json_utils import load_json
from backend.systems.character.utils.character_utils import calculate_ability_modifier
from backend.infrastructure.config_loaders.character_config_loader import config_loader
from backend.systems.character.utils.personality_interpreter import (
    interpret_personality_for_llm, 
    generate_complete_personality_deterministic,
    get_personality_backstory_elements,
    format_personality_for_display
)

# Business domain imports
from backend.systems.character.models.character import Character
from backend.systems.character.models.mood import CharacterMood
from backend.systems.character.models.goal import Goal

logger = logging.getLogger(__name__)

# Simple cache for JSON configuration files
_config_cache = {}

# Get the absolute paths to the JSON files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', '..', 'data', 'builders', 'content')
EQUIPMENT_DATA = load_json(os.path.join(DATA_DIR, 'equipment', 'equipment.json'))
ABILITIES_DATA = load_json(os.path.join(DATA_DIR, 'abilities.json'))
RACES_DATA = load_json(os.path.join(DATA_DIR, 'races.json'))

# Extract abilities from the nested structure
ABILITIES_LIST = {ability["name"]: ability for ability in ABILITIES_DATA.get("feats", [])}  # Note: JSON still uses "feats" key for backward compatibility, but Visual DM terminology is "abilities"

class CharacterBuilder:
    """
    Canonical builder pattern class for character creation that provides a fluent API
    for setting character attributes and validating the result.
    
    This consolidates the functionality from both character builder implementations
    into a single canonical class with JSON-driven configuration.
    
    Visual DM uses "abilities" for what D&D traditionally calls "feats" to better
    reflect their role in character customization and world building.
    """

    def __init__(self, race_data=None, ability_data=None, skill_list=None):
        """
        Initialize a new character builder.
        
        Args:
            race_data: Dictionary of race data keyed by race name
            ability_data: Dictionary of ability data keyed by ability name  
            skill_list: List of available skill names (now loaded from JSON)
        """
        self.race_data = race_data or RACES_DATA
        self.ability_data = ability_data or ABILITIES_LIST
        self.skill_list = skill_list or config_loader.get_skill_list()
        
        # Load validation configuration from JSON files
        self.validation_config = self._load_json_config('validation_rules.json')
        self.skills_config = self._load_json_config('skills.json')
        self.personality_config = self._load_json_config('personality_traits.json')
        self.progression_config = self._load_json_config('progression_rules.json')
        
        # Load validation limits from config or use defaults
        validation_limits = self.validation_config.get('stats', {})
        self.validation_limits = {
            'min_stat': validation_limits.get('min_value', -3),
            'max_stat': validation_limits.get('max_value', 5),
            'default_stat': validation_limits.get('default_value', 0)
        }
        
        # Load validation rules
        self.validation_rules = self.validation_config

        self.character_name = None
        self.selected_race = None
        # Visual DM uses direct attribute assignment from -3 to +5
        self.attributes = {key: self.validation_limits['default_stat'] for key in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
        self.selected_abilities = []  # Primary term in Visual DM
        self.selected_skills = []
        self.skill_points = 0
        self.starter_kit = {}
        self.level = 1
        self.gold = 0
        self.hidden_personality = self.generate_hidden_traits()
    
    def _load_json_config(self, config_filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file from the character system data directory.
        Uses caching to improve performance for repeated access.
        Returns empty dict if file not found or invalid JSON.
        """
        import json
        
        # Check cache first
        if config_filename in _config_cache:
            logger.debug(f"Using cached configuration for {config_filename}")
            return _config_cache[config_filename]
        
        try:
            # Construct path to the configuration file
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),  # Go up to backend/systems/
                '..', '..', 'data', 'systems', 'character'  # Then to data/systems/character/
            )
            config_path = os.path.join(config_dir, config_filename)
            
            if not os.path.exists(config_path):
                logger.warning(f"Configuration file not found: {config_path}")
                _config_cache[config_filename] = {}
                return {}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                logger.debug(f"Loaded and cached configuration from {config_filename}")
                _config_cache[config_filename] = config_data
                return config_data
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file {config_filename}: {str(e)}")
            _config_cache[config_filename] = {}
            return {}
        except Exception as e:
            logger.error(f"Error loading configuration file {config_filename}: {str(e)}")
            _config_cache[config_filename] = {}
            return {}

    def generate_hidden_traits(self) -> Dict[str, Any]:
        """
        Generate hidden personality attributes using the development bible's 6-attribute system.
        
        Returns:
            Dictionary containing the 6 hidden attributes (0-6 scale each):
            ambition, integrity, discipline, impulsivity, pragmatism, resilience
        """
        try:
            personality_config = config_loader.load_personality_config()
            generation_rules = config_loader.get_generation_rules()
            
            # Get generation parameters
            base_mean = generation_rules.get("base_mean", 3.0)
            base_std_dev = generation_rules.get("base_std_dev", 1.2)
            min_total_variation = generation_rules.get("min_total_variation", 8)
            max_total_variation = generation_rules.get("max_total_variation", 24)
            
            # Get background influences if race is set
            background_biases = {}
            if hasattr(self, 'selected_race') and self.selected_race:
                # Try to map race to background for influences
                race_to_background_map = {
                    'human': 'folk_hero',
                    'elf': 'sage', 
                    'dwarf': 'guild_artisan',
                    'halfling': 'entertainer',
                    'gnome': 'sage',
                    'half-elf': 'entertainer',
                    'half-orc': 'criminal',
                    'tiefling': 'criminal'
                }
                background = race_to_background_map.get(self.selected_race.lower())
                if background:
                    background_biases = config_loader.get_background_influences(background)
            
            # Generate the 6 hidden attributes
            attributes = ['ambition', 'integrity', 'discipline', 'impulsivity', 'pragmatism', 'resilience']
            hidden_traits = {}
            
            for attribute in attributes:
                # Start with base random value using normal distribution
                base_value = random.gauss(base_mean, base_std_dev)
                
                # Apply background bias if available
                bias = 0
                if attribute in background_biases:
                    bias = background_biases[attribute].get('bias', 0)
                
                # Calculate final value with bias
                final_value = base_value + bias
                
                # Clamp to valid range (0-6)
                final_value = max(0, min(6, final_value))
                
                # Round to nearest integer for clean values
                hidden_traits[attribute] = round(final_value)
            
            # Ensure some variation exists (characters shouldn't all be average)
            total_variation = sum(abs(value - 3) for value in hidden_traits.values())
            if total_variation < min_total_variation:
                # Add some random variation to make character more distinctive
                attributes_to_vary = random.sample(attributes, 2)
                for attr in attributes_to_vary:
                    adjustment = random.choice([-1, 1]) * random.randint(1, 2)
                    new_value = hidden_traits[attr] + adjustment
                    hidden_traits[attr] = max(0, min(6, new_value))
            
            elif total_variation > max_total_variation:
                # Reduce extreme values to keep characters realistic
                for attr in attributes:
                    if hidden_traits[attr] == 0:
                        hidden_traits[attr] = 1
                    elif hidden_traits[attr] == 6:
                        hidden_traits[attr] = 5
            
            return hidden_traits
            
        except Exception as e:
            logger.warning(f"Failed to generate hidden traits using configuration: {e}")
            # Fallback to simple generation matching development bible structure
            return {
                'ambition': random.randint(1, 5),
                'integrity': random.randint(1, 5), 
                'discipline': random.randint(1, 5),
                'impulsivity': random.randint(1, 5),
                'pragmatism': random.randint(1, 5),
                'resilience': random.randint(1, 5)
            }

    def load_from_input(self, input_data: Dict[str, Any]) -> 'CharacterBuilder':
        """
        Load character data from a dictionary.
        
        Args:
            input_data: Dictionary containing character data
            
        Returns:
            Self for method chaining
        """
        self.character_name = input_data.get("character_name") or input_data.get("name")
        
        if "race" in input_data:
            self.set_race(input_data["race"])

        for attribute, value in input_data.get("attributes", {}).items():
            self.assign_attribute(attribute, value)

        # Handle abilities/feats - both terms are supported for backward compatibility
        abilities = input_data.get("abilities", []) or input_data.get("feats", [])
        for ability in abilities:
            self.add_ability(ability)

        # Handle skills - can be either a list or a dict
        skills = input_data.get("skills", [])
        if isinstance(skills, list):
            for skill in skills:
                self.assign_skill(skill)
        elif isinstance(skills, dict):
            for skill, rank in skills.items():
                self.assign_skill(skill)

        if "starter_kit" in input_data:
            self.apply_starter_kit(input_data["starter_kit"])
            
        return self

    def set_race(self, race_name: str) -> 'CharacterBuilder':
        """
        Set the character's race and apply racial modifiers.
        
        Args:
            race_name: Name of the race
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the race is unknown
        """
        if race_name not in self.race_data:
            raise ValueError(config_loader.get_error_message("race_invalid", race=race_name))
        self.selected_race = race_name
        self.apply_racial_modifiers()
        return self

    def apply_racial_modifiers(self) -> None:
        """
        Apply racial ability modifiers based on the selected race.
        """
        if not self.selected_race:
            return
            
        mods = self.race_data[self.selected_race].get("ability_modifiers", {})
        for attribute, bonus in mods.items():
            if attribute in self.attributes:
                self.attributes[attribute] += bonus

    def assign_attribute(self, attribute: str, value: int) -> 'CharacterBuilder':
        """
        Assign a value to an attribute using Visual DM's direct assignment system.
        
        Args:
            attribute: Attribute name (STR, DEX, etc.)
            value: Attribute value (-3 to +5 in Visual DM)
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the attribute is unknown or value is invalid
        """
        attribute = attribute.upper()
        if attribute not in self.attributes:
            raise ValueError(f"Unknown attribute: {attribute}")
        
        # Validate attribute range using configuration (Visual DM uses -3 to +5)
        min_val = self.validation_limits.get("min_stat", -3)
        max_val = self.validation_limits.get("max_stat", 5)
        
        if value < min_val or value > max_val:
            raise ValueError(config_loader.get_error_message(
                "attribute_invalid_value", 
                attribute=attribute, 
                value=value, 
                min=min_val, 
                max=max_val
            ))
        
        self.attributes[attribute] = value
        return self

    def add_ability(self, ability_name: str) -> 'CharacterBuilder':
        """
        Add an ability to the character.
        
        Args:
            ability_name: Name of the ability to add
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If character already has maximum abilities for level
        """
        # Calculate max abilities for current level
        max_abilities = 7 + (self.level - 1) * 3
        
        if len(self.selected_abilities) >= max_abilities:
            raise ValueError(config_loader.get_error_message("too_many_abilities", 
                                                             level=self.level, 
                                                             max_abilities=max_abilities))
        
        # Validate ability exists
        available_abilities = config_loader.get_available_abilities()
        if ability_name not in [ability[0] for ability in available_abilities]:
            raise ValueError(config_loader.get_error_message("ability_not_found", ability=ability_name))
        
        self.selected_abilities.append(ability_name)
        return self
    
    # Legacy method for backward compatibility
    def add_feat(self, feat_name: str) -> 'CharacterBuilder':
        """Legacy method - use add_ability instead"""
        return self.add_ability(feat_name)

    def assign_skill(self, skill_name: str) -> 'CharacterBuilder':
        """
        Add a skill to the character.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the skill is unknown or validation fails
        """
        # Validate skill exists in configuration
        skill_info = config_loader.get_skill_info(skill_name)
        if not skill_info:
            raise ValueError(config_loader.get_error_message("skill_invalid", skill=skill_name))
        
        # Check for duplicates
        if not self.validation_rules.get("allow_duplicate_skills", False):
            skill_names_lower = [s.lower() for s in self.selected_skills]
            if skill_name.lower() in skill_names_lower:
                raise ValueError(config_loader.get_error_message("skill_duplicate", skill=skill_name))
        
        # Check skill limits
        max_skills = self.validation_limits.get("max_skills", 36)
        if len(self.selected_skills) >= max_skills:
            raise ValueError(config_loader.get_error_message(
                "too_many_skills", 
                max=max_skills, 
                selected=len(self.selected_skills)
            ))
        
        # Use the canonical name from configuration
        canonical_name = skill_info["name"]
        self.selected_skills.append(canonical_name)
        return self

    def assign_skills(self, skills_dict: Dict[str, int]) -> 'CharacterBuilder':
        """
        Assign multiple skills with ranks.
        
        Args:
            skills_dict: Dictionary of skill names to ranks
            
        Returns:
            Self for method chaining
        """
        for skill_name, rank in skills_dict.items():
            # Validate skill exists
            if config_loader.get_skill_info(skill_name):
                self.assign_skill(skill_name)
        return self
                
    def get_available_starter_kits(self) -> List[Dict[str, Any]]:
        """Get all available starter kits."""
        try:
            starter_kits_data = load_json(os.path.join(DATA_DIR, 'starter_kits.json'))
            return starter_kits_data.get('starter_kits', [])
        except Exception as e:
            print(f"Error loading starter kits: {e}")
            return []

    def apply_starter_kit(self, kit_name: str) -> 'CharacterBuilder':
        """
        Apply a starter kit to the character.
        
        Args:
            kit_name: Name of the starter kit
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the starter kit is unknown
        """
        starter_kits = self.get_available_starter_kits()
        kit = next((k for k in starter_kits if k['name'] == kit_name), None)
        
        if not kit:
            raise ValueError(f"Unknown starter kit: {kit_name}")
            
        self.starter_kit = {
            'equipment': kit.get('equipment', []),
            'gold': kit.get('gold', 0)
        }
        self.gold = kit.get('gold', 0)
        return self

    def is_valid(self) -> bool:
        """
        Validate the current character configuration using JSON rules.
        
        Returns:
            True if character is valid, False otherwise
        """
        valid = True
        
        # Check required fields from validation config
        character_creation_rules = self.validation_config.get("character_creation", {})
        required_fields = character_creation_rules.get("required_fields", ["character_name", "race"])
        
        if "character_name" in required_fields and not self.character_name:
            print("❌ Validation: Character name is required")
            valid = False
        if "race" in required_fields and not self.selected_race:
            print("❌ Validation: Race is required")
            valid = False
        
        # Check name length from validation config
        if self.character_name:
            min_length = character_creation_rules.get("name_min_length", 2)
            max_length = character_creation_rules.get("name_max_length", 50)
            if len(self.character_name) < min_length:
                print(f"❌ Validation: Character name too short (minimum {min_length} characters)")
                valid = False
            if len(self.character_name) > max_length:
                print(f"❌ Validation: Character name too long (maximum {max_length} characters)")
                valid = False
        
        # Check attribute values are within valid range
        for attr_name, attr_value in self.attributes.items():
            if attr_value < self.validation_limits['min_stat'] or attr_value > self.validation_limits['max_stat']:
                print(f"❌ Validation: {attr_name} value {attr_value} outside valid range ({self.validation_limits['min_stat']} to {self.validation_limits['max_stat']})")
                valid = False
        
        # Check ability limits using progression config (Visual DM system)
        progression_rules = self.progression_config.get('ability_progression', {})
        base_abilities = progression_rules.get('base_abilities', 7)
        abilities_per_level = progression_rules.get('abilities_per_level', 3)
        
        if self.level == 1:
            max_abilities = base_abilities
        else:
            max_abilities = base_abilities + ((self.level - 1) * abilities_per_level)
            
        if len(self.selected_abilities) > max_abilities:
            print(f"❌ Validation: Too many abilities ({len(self.selected_abilities)} > {max_abilities} for level {self.level})")
            valid = False
            
        # Check skill limits from validation config
        skills_rules = self.validation_config.get("skills", {})
        max_skills = skills_rules.get("max_skills_selectable", 36)
        if len(self.selected_skills) > max_skills:
            print(f"❌ Validation: Too many skills ({len(self.selected_skills)} > {max_skills})")
            valid = False
        
        # Validate skills against known skills from config
        valid_skills = set(self.skills_config.get('skills', {}).keys()) if self.skills_config else set()
        if valid_skills:
            for skill in self.selected_skills:
                if skill not in valid_skills:
                    print(f"❌ Validation: Unknown skill '{skill}'. Valid skills: {', '.join(sorted(valid_skills))}")
                    valid = False
        
        # Validate hidden personality attributes
        personality_rules = self.validation_config.get("personality", {})
        min_personality = personality_rules.get("min_value", 0)
        max_personality = personality_rules.get("max_value", 6)
        
        for trait_name, trait_value in self.hidden_personality.items():
            if trait_value < min_personality or trait_value > max_personality:
                print(f"❌ Validation: Hidden personality trait {trait_name} value {trait_value} outside valid range ({min_personality} to {max_personality})")
                valid = False
            
        return valid

    def finalize(self) -> Dict[str, Any]:
        """
        Finalize the character data and return it as a dictionary.
        
        Returns:
            Dictionary containing the finalized character data
            
        Raises:
            ValueError: If character data is not valid
        """
        if not self.is_valid():
            raise ValueError("Character data is not valid")
            
        # Visual DM doesn't use ability modifier calculation - attributes are used directly
        INT = self.attributes.get("INT", 0)
        CON = self.attributes.get("CON", 0)
        DEX = self.attributes.get("DEX", 0)
        level = self.level

        character_id = (
            self.character_name.lower().replace(" ", "_") + "_" + uuid.uuid4().hex[:4]
            if self.character_name else "unnamed_character_" + uuid.uuid4().hex[:4]
        )

        char = {
            "character_name": self.character_name,
            "character_id": character_id,
            "race": self.selected_race,
            "attributes": self.attributes,
            "abilities": self.selected_abilities,  # Primary term in Visual DM
            "feats": self.selected_abilities,      # Alias for backward compatibility with legacy terminology
            "skills": self.selected_skills,
            # Visual DM HP/MP calculations (using attributes directly, not modifiers)
            "HP": level * (12 + CON),
            "MP": (level * 8) + (INT * level),
            "AC": 10 + DEX,  # Visual DM: 10 + DEX + abilities + magic
            "XP": 0,
            "level": level,
            "alignment": "Neutral",
            "languages": ["Common"],
            "created_at": datetime.utcnow().isoformat(),
            # Inventory and equipment are now managed by Inventory/InventoryItem models/services
            "gold": self.gold,
            "features": [],
            "proficiencies": [],
            "faction_affiliations": [],
            "reputation": 0,
            "cooldowns": {},
            "attributeus_effects": [],
            "notable_possessions": [],
            "spells": [],
            "known_languages": ["Common"],
            "rumor_index": [],
            "beliefs": {},
            "hidden_personality": self.hidden_personality,
            "narrative_motif_pool": {
                "active_motifs": [],
                "motif_history": [],
                "last_rotated": datetime.utcnow().isoformat()
            },
            "narrator_style": "Cormac McCarthy meets Lovecraft",
            "personality_description": self._get_personality_description()
        }
        
        return char

    def _get_personality_description(self) -> str:
        """
        Get a comprehensive personality description using enhanced deterministic generation.
        
        Returns:
            Formatted string describing the personality traits
        """
        try:
            # Use enhanced deterministic generation instead of LLM-dependent approach
            return format_personality_for_display(
                self.hidden_personality,
                include_full_profile=True,
                profession=getattr(self, 'profession', None),
                race=self.selected_race,
                age=getattr(self, 'age', None)
            )
        except Exception as e:
            logger.warning(f"Failed to generate enhanced personality description: {e}")
            # Fallback to simple LLM-ready description
            try:
                return interpret_personality_for_llm(self.hidden_personality)
            except Exception as e2:
                logger.error(f"Failed to generate fallback personality description: {e2}")
                # Final fallback to simple description
                traits = []
                for attr, value in self.hidden_personality.items():
                    traits.append(f"{attr}: {value}/6")
                return f"Personality: {', '.join(traits)}"
    
    def get_complete_personality_profile(self) -> Dict[str, Any]:
        """
        Get a complete personality profile with all components.
        
        Returns:
            Dictionary containing comprehensive personality information
        """
        try:
            return generate_complete_personality_deterministic(
                self.hidden_personality,
                profession=getattr(self, 'profession', None),
                race=self.selected_race,
                age=getattr(self, 'age', None)
            )
        except Exception as e:
            logger.error(f"Failed to generate complete personality profile: {e}")
            return {
                "personality_summary": "A character with balanced traits.",
                "speech_style": "Speaks in a straightforward manner.",
                "primary_motivations": ["survival", "basic needs"],
                "personality_quirks": ["has typical behaviors"],
                "professional_attitude": "Views work as necessary.",
                "raw_values": self.hidden_personality
            }
    
    def get_backstory_elements(self) -> Dict[str, str]:
        """
        Get deterministic backstory elements based on personality and character data.
        
        Returns:
            Dictionary containing backstory components
        """
        try:
            return get_personality_backstory_elements(
                self.hidden_personality,
                profession=getattr(self, 'profession', None),
                race=self.selected_race
            )
        except Exception as e:
            logger.error(f"Failed to generate backstory elements: {e}")
            return {
                "childhood": "Had a typical upbringing.",
                "formative_experience": "Experienced normal life events.",
                "professional_path": "Found their current path through circumstance.",
                "current_situation": "Living a typical life."
            }

def generate_basic_attributes(attribute_distribution: Optional[str] = "balanced") -> Dict[str, int]:
    """
    Generate basic character attributes using Visual DM's direct assignment system (-3 to +5).
    
    Args:
        attribute_distribution: Distribution type ("balanced", "specialized", "random")
        
    Returns:
        Dictionary of attribute names to values
    """
    attributes = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    
    if attribute_distribution == "balanced":
        # Balanced character: mostly 1s and 2s
        return {attribute: random.choice([1, 1, 2, 2]) for attribute in attributes}
    elif attribute_distribution == "specialized":
        # Specialized character: one high attribute, others lower
        values = [0, 0, 1, 1, 2, 4]
        random.shuffle(values)
        return dict(zip(attributes, values))
    else:  # random
        # Random distribution within reasonable bounds
        return {attribute: random.randint(-1, 3) for attribute in attributes}

# Export the classes and functions that should be available
__all__ = ['CharacterBuilder', 'RACES_DATA', 'ABILITIES_LIST', 'generate_basic_attributes'] 