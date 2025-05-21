"""
Character Builder
---------------
Class for creating and modifying character data. Translates input into structured
JSON-compatible data ready for storage or gameplay. Supports race selection,
attribute assignment, feats, skills, starter kits, and derived attributes.
"""

import os
import random
from datetime import datetime
from uuid import uuid4
import uuid
from typing import Dict, Any, List, Optional

# Updated imports for the new structure
from backend.core.utils.json_utils import load_json
from backend.core.database import get_db_session
from backend.systems.character.models.character import Character, Skill
from backend.systems.character.utils.character_utils import calculate_ability_modifier

# Get the absolute paths to the JSON files
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rules')
EQUIPMENT_DATA = load_json(os.path.join(DATA_DIR, 'equipment.json'))
FEATS_DATA = load_json(os.path.join(DATA_DIR, 'feats.json'))
RACES_DATA = load_json(os.path.join(DATA_DIR, 'races.json'))

# Extract feats from the nested structure
FEATS_LIST = {feat["name"]: feat for feat in FEATS_DATA.get("feats", [])}

class CharacterBuilder:
    """
    Builder pattern class for character creation that provides a fluent API
    for setting character attributes and validating the result.
    """

    def __init__(self, race_data=None, feat_data=None, skill_list=None):
        """
        Initialize a new character builder.
        
        Args:
            race_data: Dictionary of race data keyed by race name
            feat_data: Dictionary of feat data keyed by feat name
            skill_list: List of available skill names
        """
        self.race_data = race_data or RACES_DATA
        self.feat_data = feat_data or FEATS_LIST
        self.skill_list = skill_list or []

        self.character_name = None
        self.selected_race = None
        self.attributes = {key: 8 for key in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]}
        self.selected_feats = []
        self.selected_skills = []
        self.skill_points = 0
        self.starter_kit = {}
        self.level = 1
        self.gold = 0
        self.hidden_personality = self.generate_hidden_traits()

    def load_from_input(self, input_data: Dict[str, Any]) -> 'CharacterBuilder':
        """
        Load character data from a dictionary.
        
        Args:
            input_data: Dictionary containing character data
            
        Returns:
            Self for method chaining
        """
        self.character_name = input_data.get("character_name") or input_data.get("name")
        self.set_race(input_data["race"])

        for attribute, value in input_data.get("attributes", {}).items():
            self.assign_attribute(attribute, value)

        for feat in input_data.get("feats", []):
            self.add_feat(feat)

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
            raise ValueError(f"Unknown race: {race_name}")
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
        Assign a value to an attribute.
        
        Args:
            attribute: Attribute name (STR, DEX, etc.)
            value: Attribute value
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the attribute is unknown
        """
        attribute = attribute.upper()
        if attribute not in self.attributes:
            raise ValueError(f"Unknown attribute: {attribute}")
        self.attributes[attribute] = value
        return self

    def add_feat(self, feat_name: str) -> 'CharacterBuilder':
        """
        Add a feat to the character.
        
        Args:
            feat_name: Name of the feat
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the feat is unknown
        """
        if feat_name not in self.feat_data:
            raise ValueError(f"Unknown feat: {feat_name}")
        # Check prerequisites
        feat = self.feat_data[feat_name]
        for prereq in feat.get("prerequisites", []):
            # TODO: Add prerequisite checking logic here
            pass
        self.selected_feats.append(feat_name)
        return self

    def assign_skill(self, skill_name: str) -> 'CharacterBuilder':
        """
        Assign a skill to the character.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Self for method chaining
            
        Raises:
            ValueError: If the skill is unknown
        """
        # Create a case-insensitive map to handle variations in skill names
        skill_map = {s.lower(): s for s in self.skill_list}
        skill_key = skill_name.lower()
        
        if skill_key not in skill_map:
            raise ValueError(f"Unknown skill: {skill_name}")
            
        self.selected_skills.append(skill_map[skill_key])
        return self

    def assign_skills(self, skills_dict: Dict[str, int]) -> 'CharacterBuilder':
        """
        Assign multiple skills with ranks to the character.
        
        Args:
            skills_dict: Dictionary mapping skill names to ranks
            
        Returns:
            Self for method chaining
        """
        for skill_name, rank in skills_dict.items():
            if skill_name.lower() in [s.lower() for s in self.skill_list]:
                self.selected_skills.append(skill_name)
        return self
                
    def get_available_starter_kits(self) -> List[Dict[str, Any]]:
        """
        Get all available starter kits.
        
        Returns:
            List of starter kit data dictionaries
        """
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
        Check if the character data is valid.
        
        Returns:
            True if the character data is valid, False otherwise
        """
        valid = True
        if self.selected_race is None:
            print("❌ Validation: No race selected.")
            valid = False
        if len(self.selected_feats) > 7:
            print(f"❌ Validation: Too many feats ({len(self.selected_feats)} > 7)")
            valid = False
        if len(self.selected_skills) > 18:
            print(f"❌ Validation: Too many skills ({len(self.selected_skills)} > 10)")
            valid = False
        return valid

    def finalize(self) -> Dict[str, Any]:
        """
        Finalize the character data and return it as a dictionary.
        
        Returns:
            Dictionary containing the finalized character data
        """
        if not self.is_valid():
            raise ValueError("Character data is not valid")
            
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
            "feats": self.selected_feats,
            "skills": self.selected_skills,
            "HP": level * (12 + calculate_ability_modifier(CON)),
            "MP": (level * 8) + (calculate_ability_modifier(INT) * level),
            "AC": 10 + calculate_ability_modifier(DEX),
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
            "narrative_motif_pool": {
                "active_motifs": [],
                "motif_history": [],
                "last_rotated": datetime.utcnow().isoformat()
            },
            "narrator_style": "Cormac McCarthy meets Lovecraft"
        }

        # Inventory/InventoryItem creation should be handled separately using canonical services

        return char

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the builder to a dictionary.
        
        Returns:
            Dictionary representation of the finalized character
        """
        return self.finalize()

    def generate_hidden_traits(self) -> Dict[str, int]:
        """
        Generate hidden personality traits for the character.
        
        Returns:
            Dictionary of hidden traits and their values
        """
        return {
            "hidden_ambition": random.randint(0, 6),
            "hidden_integrity": random.randint(0, 6),
            "hidden_discipline": random.randint(0, 6),
            "hidden_impulsivity": random.randint(0, 6),
            "hidden_pragmatism": random.randint(0, 6),
            "hidden_resilience": random.randint(0, 6)
        }

    def save(self, db_session=None) -> Character:
        """
        Save the character to the database.
        
        Args:
            db_session: SQLAlchemy database session (optional)
            
        Returns:
            Saved Character ORM instance
        """
        if not self.is_valid():
            raise ValueError("Cannot save invalid character")
            
        session = db_session if db_session else next(get_db_session())
        try:
            char_data = self.finalize()
            
            new_character = Character(
                name=char_data['character_name'],
                race=char_data['race'],
                level=char_data['level'],
                stats=char_data['attributes'],
                notes=[]
            )
            
            # Add skills
            for skill_name in char_data['skills']:
                skill = session.query(Skill).filter(Skill.name == skill_name).first()
                if skill:
                    new_character.skills.append(skill)
                else:
                    # Create skill if it doesn't exist
                    skill = Skill(name=skill_name)
                    session.add(skill)
                    new_character.skills.append(skill)
            
            session.add(new_character)
            session.commit()
            session.refresh(new_character)
            
            return new_character
        except Exception as e:
            session.rollback()
            raise e

    @classmethod
    def load(cls, character_id, db_session=None) -> 'CharacterBuilder':
        """
        Load a character from the database and create a builder from it.
        
        Args:
            character_id: ID of the character to load
            db_session: SQLAlchemy database session (optional)
            
        Returns:
            CharacterBuilder instance populated with the character's data
            
        Raises:
            ValueError: If the character is not found
        """
        session = db_session if db_session else next(get_db_session())
        try:
            character = session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise ValueError(f"Character with ID {character_id} not found")
                
            return character.to_builder()
        except Exception as e:
            raise e

# Helper function that was in the original file
def generate_basic_stats():
    """Generate baseline stats for a new character."""
    return {
        "STR": 10,
        "DEX": 10,
        "CON": 10,
        "INT": 10,
        "WIS": 10,
        "CHA": 10
    }

__all__ = ['CharacterBuilder', 'RACES_DATA', 'FEATS_LIST', 'generate_basic_stats'] 