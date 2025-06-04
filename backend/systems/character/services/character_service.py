"""
Character Service
-----------------
Service for managing character entities, including creation, updates, and lifecycle management.
Includes proper integration with inventory and equipment systems.
"""
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID, uuid4
import random
import math
from datetime import datetime

# Business logic imports
from backend.systems.character.models.character import Character
from backend.systems.character.services.character_builder import CharacterBuilder
from backend.systems.character.models.relationship import Relationship, RelationshipType
from backend.systems.character.models.mood import CharacterMood, EmotionalState, MoodIntensity, MoodModifier
from backend.systems.character.models.goal import Goal, GoalType, GoalPriority, GoalStatus

# Service imports - avoiding circular imports via dependency injection
from backend.systems.character.services.mood_service import MoodService
from backend.systems.character.services.goal_service import GoalService

# Infrastructure imports
from backend.infrastructure.database_services.character_repository import CharacterRepository
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from backend.infrastructure.events.events.canonical_events import (
    CharacterCreated, CharacterLeveledUp, CharacterUpdated, CharacterDeleted,
    MoodChanged, GoalCreated, GoalCompleted, GoalFailed, GoalProgressUpdated
)
from backend.infrastructure.shared.exceptions import NotFoundError, RepositoryError, ValidationError

# Import the canonical rules system instead of duplicated balance constants
from backend.systems.rules.rules import (
    balance_constants,
    calculate_ability_modifier,
    calculate_proficiency_bonus,
    calculate_hp_for_level,
    calculate_mana_points,
    get_starting_equipment
)

# LLM service imports for dynamic character interactions
from backend.infrastructure.llm.services.llm_service import LLMService, GenerationContext
from backend.systems.character.utils.personality_interpreter import format_personality_for_display

# Constants from character_utils, can be moved to a config or rules file if preferred
RACES = ['human', 'elf', 'dwarf', 'halfling', 'gnome', 'half-elf', 'half-orc', 'tiefling']

import logging

logger = logging.getLogger(__name__)

# Simple cache for JSON configuration files
_config_cache = {}

class CharacterService:
    """Service for managing character entities with full inventory integration and dynamic LLM interactions"""
    
    def __init__(self, 
                 character_repository: Optional[CharacterRepository] = None,
                 event_dispatcher: Optional[EventDispatcher] = None,
                 mood_service: Optional[MoodService] = None,
                 goal_service: Optional[GoalService] = None,
                 llm_service: Optional[LLMService] = None):
        """
        Initialize character service with dependencies.
        
        Args:
            character_repository: Repository for character data
            event_dispatcher: Event dispatcher for character events
            mood_service: Service for character mood management
            goal_service: Service for character goal management
            llm_service: LLM service for dynamic character interactions
        """
        # Repository and event handling
        self.character_repository = character_repository or CharacterRepository()
        self.event_dispatcher = event_dispatcher or EventDispatcher()
        
        # Related services - can be injected via dependency injection
        self.mood_service = mood_service
        self.goal_service = goal_service
        self.relationship_service = None  # Will be injected if needed
        
        # LLM service for dynamic interactions
        self.llm_service = llm_service
        
        # Hidden attribute adjustment engine
        self.hidden_attribute_engine = HiddenAttributeAdjustmentEngine()
        
        logger.info("CharacterService initialized with inventory integration")
        
    # --- Helper Methods (adapted from character_utils.py) ---
    def _calculate_ability_modifier(self, score: int) -> int:
        """Calculate ability score modifier using CANONICAL rules system formula."""
        return calculate_ability_modifier(score)

    def _has_spellcasting(self, character_data: dict) -> bool:
        """Check if a character has spellcasting based on their abilities."""
        # In ability-based system, spellcasting is determined by abilities, not class
        character_abilities = character_data.get('abilities', []) or character_data.get('feats', [])  # Support legacy 'feats' terminology temporarily
        spellcasting_abilities = ['arcane_initiate', 'divine_magic', 'nature_magic', 'occult_studies']
        return any(ability in spellcasting_abilities for ability in character_abilities)
    
    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a given level using canonical XP thresholds."""
        if level <= 1:
            return 0
        
        # Use XP thresholds from canonical rules system
        xp_thresholds = balance_constants['xp_thresholds']
        if level <= len(xp_thresholds):
            return xp_thresholds[level - 1]
        
        # For levels beyond the table, use the last threshold
        return xp_thresholds[-1]

    def _get_character_orm_by_id(self, character_id: Union[int, UUID]) -> Character:
        """Internal helper to fetch a Character ORM instance by ID."""
        character = self.character_repository.get_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character with ID {character_id} not found")
        return character
        
    def _get_character_orm_by_uuid(self, character_uuid: Union[str, UUID]) -> Character:
        """Internal helper to fetch a Character ORM instance by UUID."""
        character = self.character_repository.get_by_uuid(character_uuid)
        if not character:
            raise NotFoundError(f"Character with UUID {character_uuid} not found")
        return character

    def _load_json_config(self, config_filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file from the character system data directory.
        Uses caching to improve performance for repeated access.
        Returns empty dict if file not found or invalid JSON.
        """
        import json
        import os
        
        # Check cache first
        if config_filename in _config_cache:
            logger.debug(f"Using cached configuration for {config_filename}")
            return _config_cache[config_filename]
        
        try:
            # Construct path to the configuration file
            config_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # Go up to backend/
                '..', 'data', 'systems', 'character'  # Then to data/systems/character/
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

    @classmethod
    def clear_config_cache(cls) -> None:
        """Clear the JSON configuration cache. Useful for testing and development."""
        global _config_cache
        _config_cache.clear()
        logger.info("Character system JSON configuration cache cleared")

    # --- Core Character Methods (CRUD, Level up) ---
    def create_character_from_builder(self, builder: CharacterBuilder, commit: bool = True) -> Character:
        """
        Creates a new Character in the database from a CharacterBuilder instance.
        Now includes proper inventory and equipment integration.
        """
        if not builder.is_valid():
            raise ValidationError("CharacterBuilder is not valid")

        char_data = builder.finalize()

        # Map char_data dictionary to Character creation data
        character_data = {
            "name": char_data.get("character_name"),
            "race": char_data.get("race"),
            "level": char_data.get("level", 1),
            "stats": char_data.get("attributes"),
            "background": char_data.get("background"),
            "alignment": char_data.get("alignment", "Neutral"),
            "notes": char_data.get("notes", []),
        }

        new_character_orm = self.character_repository.create(character_data)
        
        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(new_character_orm)
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to create character in DB: {str(e)}")
        
        # FIXED: Handle inventory/equipment using InventoryService
        try:
            self._setup_character_inventory(new_character_orm, char_data, commit)
        except Exception as e:
            logger.error(f"Failed to setup inventory for character {new_character_orm.id}: {str(e)}")
            if commit:
                # Don't fail character creation if inventory setup fails
                logger.warning("Character created but inventory setup failed")

        # FIXED: Handle initial skills if Character ORM supports it
        try:
            self._setup_character_skills(new_character_orm, char_data, commit)
        except Exception as e:
            logger.error(f"Failed to setup skills for character {new_character_orm.id}: {str(e)}")

        # Initialize mood for the new character
        self.mood_service.initialize_mood(new_character_orm.uuid)
        
        # Dispatch character created event
        self.event_dispatcher.dispatch(CharacterCreated(
            character_id=new_character_orm.uuid,
            name=new_character_orm.name
        ))
        
        logger.info(f"Character created: {new_character_orm.name} (ID: {new_character_orm.id})")
        return new_character_orm

    def get_character_by_id(self, character_id: Union[int, UUID]) -> Character:
        """Retrieves a Character ORM instance by its ID."""
        return self._get_character_orm_by_id(character_id)
        
    def get_character_by_uuid(self, character_uuid: Union[str, UUID]) -> Character:
        """Retrieves a Character ORM instance by its UUID."""
        return self._get_character_orm_by_uuid(character_uuid)

    def get_character_builder_by_id(self, character_id: Union[int, UUID]) -> CharacterBuilder:
        """Retrieves a Character, converts it to a CharacterBuilder instance, and returns the builder."""
        character_orm = self._get_character_orm_by_id(character_id)
        if not hasattr(character_orm, 'to_builder') or not callable(getattr(character_orm, 'to_builder')):
            # This method must be implemented on the Character ORM model
            raise NotImplementedError("Character ORM model does not have a to_builder() method.")
        return character_orm.to_builder()

    def update_character_data(self, character_id: Union[int, UUID], update_data: Dict[str, Any], commit: bool = True) -> Character:
        """Updates a Character ORM instance with data from a dictionary."""
        character_orm = self._get_character_orm_by_id(character_id)
        
        updated_character = self.character_repository.update(character_orm, update_data)

        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(updated_character)
                
                # Dispatch character updated event
                self.event_dispatcher.dispatch(CharacterUpdated(
                    character_id=updated_character.uuid,
                    name=updated_character.name,
                    changes=update_data
                ))
                
                logger.info(f"Character updated: {updated_character.name} (ID: {updated_character.id})")
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to update character: {str(e)}")

        return updated_character

    def delete_character(self, character_id: Union[int, UUID], commit: bool = True) -> bool:
        """Deletes a Character from the database by its ID."""
        character_orm = self._get_character_orm_by_id(character_id)
        character_uuid = character_orm.uuid  # Save UUID for event dispatch
        
        self.character_repository.delete(character_orm)
        if commit:
            try:
                self.character_repository.commit()
                
                # Dispatch character deleted event
                self.event_dispatcher.dispatch(CharacterDeleted(
                    character_id=character_uuid
                ))
                
                return True
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to delete character {character_id}: {str(e)}")
        return False # If commit is false, indicates success of marking for deletion (but not committed)

    def level_up_character(self, character_id: Union[int, UUID], commit: bool = True) -> Character:
        """Handles the logic for leveling up a character using CANONICAL rules system."""
        character_orm = self._get_character_orm_by_id(character_id)
        
        # Ensure stats is a mutable dictionary if it's a JSON field being modified
        current_stats = dict(character_orm.stats or {})
        current_level = character_orm.level
        character_abilities = current_stats.get('abilities', [])
        
        # Use CANONICAL hit point calculation from rules system
        con_score = current_stats.get('constitution', 10)
        con_mod = self._calculate_ability_modifier(con_score)
        
        # Calculate hit points for the new level using canonical formula
        new_level = current_level + 1
        new_total_hp = calculate_hp_for_level(new_level, con_mod)
        old_total_hp = calculate_hp_for_level(current_level, con_mod)
        hp_gain = new_total_hp - old_total_hp
        
        # Update total hit points to canonical value for the new level
        current_stats['hit_points'] = new_total_hp
        
        # Use CANONICAL mana point calculation if character has spellcasting
        if self._has_spellcasting(current_stats):
            # Determine spellcasting ability based on abilities
            spellcasting_ability_name = 'wisdom'  # default
            for ability in character_abilities:
                ability_name = ability.get("name", "").lower() if isinstance(ability, dict) else str(ability).lower()
                if any(keyword in ability_name for keyword in ["arcane", "wizard", "sorcerer"]):
                    spellcasting_ability_name = 'intelligence'
                    break
                elif any(keyword in ability_name for keyword in ["charisma", "bard", "warlock"]):
                    spellcasting_ability_name = 'charisma'
                    break
            
            spellcasting_score = current_stats.get(spellcasting_ability_name.lower(), 10)
            spell_mod = self._calculate_ability_modifier(spellcasting_score)
            
            # Calculate mana points for the new level using canonical formula
            new_total_mp = calculate_mana_points(new_level, spell_mod)
            current_stats['mana_points'] = new_total_mp
        
        # Update level and skill points using canonical values
        character_orm.level = new_level
        skill_points_per_level = balance_constants.get('skill_points_per_level', 4)
        current_stats['skill_points'] = current_stats.get('skill_points', 0) + skill_points_per_level
        
        # Update XP to the threshold of the new level using canonical thresholds
        current_stats['xp'] = self._calculate_xp_for_level(new_level)
        
        # Update character stats (assuming stats is a JSON field)
        character_orm.stats = current_stats
        
        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(character_orm)
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to level up character {character_id}: {str(e)}")
                
        # Add positive mood modifier for leveling up
        self.mood_service.add_mood_modifier(
            character_orm.uuid,
            EmotionalState.HAPPY,
            MoodIntensity.MEDIUM,
            f"Gained level and reached level {new_level}",
            duration_hours=12
        )
        
        # Create a goal to try new abilities
        self.goal_service.add_goal(
            character_orm.uuid,
            f"Try out new level {new_level} abilities",
            GoalType.MECHANICAL,
            GoalPriority.MEDIUM
        )
        
        # Dispatch level up event
        self.event_dispatcher.dispatch(CharacterLeveledUp(
            character_id=character_orm.uuid,
            old_level=current_level,
            new_level=new_level
        ))
        
        return character_orm

    def validate_character_creation_data(self, data: Dict[str, Any]) -> None:
        """Validates the data used for character creation using JSON configuration."""
        # Load validation rules from configuration
        validation_config = self._load_json_config('validation_rules.json')
        
        # Basic required fields validation
        required_fields = ['name', 'race']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Race validation - check against available races or fallback to hardcoded list
        valid_races = RACES  # Default fallback
        if validation_config.get('character_creation', {}).get('valid_races'):
            valid_races = validation_config['character_creation']['valid_races']
        
        if data.get('race') and data.get('race') not in valid_races:
            raise ValidationError(f"Invalid race: {data.get('race')}. Valid races are: {', '.join(valid_races)}")
        
        # Stats validation using JSON config
        stats_rules = validation_config.get('stats', {})
        min_stat = stats_rules.get('min_value', -3)
        max_stat = stats_rules.get('max_value', 5)
        
        stats = data.get('stats', {}) or data.get('attributes', {})  # Support both field names
        for stat_name, stat_value in stats.items():
            if stat_name.upper() in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
                if not isinstance(stat_value, int) or stat_value < min_stat or stat_value > max_stat:
                    raise ValidationError(f"Invalid {stat_name} value: {stat_value}. Must be between {min_stat} and {max_stat}.")
        
        # Skills validation using JSON config
        skills_config = self._load_json_config('skills.json')
        valid_skills = set(skills_config.get('skills', {}).keys()) if skills_config else set()
        
        character_skills = data.get('skills', {})
        for skill_name in character_skills.keys():
            if valid_skills and skill_name not in valid_skills:
                logger.warning(f"Unknown skill: {skill_name}. Valid skills from config: {', '.join(valid_skills)}")
        
        # Personality traits validation using JSON config
        personality_config = self._load_json_config('personality_traits.json')
        valid_traits = set(personality_config.get('personality_traits', {}).keys()) if personality_config else set()
        
        personality_traits = data.get('personality_traits', [])
        for trait in personality_traits:
            if valid_traits and trait not in valid_traits:
                logger.warning(f"Unknown personality trait: {trait}. Valid traits from config: {', '.join(valid_traits)}")
        
        # Hidden personality attributes validation
        personality_rules = validation_config.get('personality', {})
        min_personality = personality_rules.get('min_value', 0)
        max_personality = personality_rules.get('max_value', 6)
        
        hidden_personality = data.get('hidden_personality', {})
        for trait_name, trait_value in hidden_personality.items():
            if isinstance(trait_value, (int, float)):
                if trait_value < min_personality or trait_value > max_personality:
                    raise ValidationError(f"Invalid {trait_name} value: {trait_value}. Must be between {min_personality} and {max_personality}.")
        
        # Level and abilities validation 
        level = data.get('level', 1)
        abilities = data.get('abilities', []) or data.get('feats', [])  # Support both terms for backward compatibility
        
        # Use progression rules if available
        progression_config = self._load_json_config('progression_rules.json')
        if progression_config.get('ability_progression'):
            ability_progression = progression_config['ability_progression']
            max_abilities = ability_progression.get('base_abilities', 7)  # Default 7 at level 1
            abilities_per_level = ability_progression.get('abilities_per_level', 3)  # Default 3 per level after 1
            
            if level > 1:
                max_abilities += (level - 1) * abilities_per_level
        else:
            # Fallback to Visual DM default rules
            if level == 1:
                max_abilities = 7
            else:
                max_abilities = 7 + ((level - 1) * 3)
        
        if len(abilities) > max_abilities:
            raise ValidationError(f"Too many abilities for level {level}: {len(abilities)} > {max_abilities}")

    # --- Relationship Integration ---
    def add_faction_relationship(self, character_id: Union[int, UUID], faction_id: Union[str, UUID], 
                                reputation: int, standing: str) -> Relationship:
        """
        Create a faction relationship between a character and a faction.
        
        Args:
            character_id: The ID of the character
            faction_id: The UUID of the faction
            reputation: Numeric reputation value
            standing: Standing description
            
        Returns:
            The created relationship object
        """
        if not self.relationship_service:
            raise ValueError("RelationshipService not available - inject as dependency")
            
        character = self._get_character_orm_by_id(character_id)
        
        relationship = self.relationship_service.create_relationship(
            character.uuid,
            faction_id,
            RelationshipType.FACTION,
            {
                "reputation": reputation, 
                "standing": standing,
                "last_interaction": datetime.utcnow().isoformat()
            }
        )
        
        return relationship

    def get_character_relationships(self, character_id: Union[int, UUID], 
                                   relationship_type: Optional[str] = None) -> List[Relationship]:
        """
        Get relationships for a character, optionally filtered by type.
        
        Args:
            character_id: The ID of the character
            relationship_type: Optional type filter
            
        Returns:
            List of relationship objects
        """
        if not self.relationship_service:
            raise ValueError("RelationshipService not available - inject as dependency")
            
        character = self._get_character_orm_by_id(character_id)
        
        relationships = self.relationship_service.get_relationships_by_source(
            character.uuid,
            relationship_type
        )
        
        return relationships

    def add_quest_relationship(self, character_id: Union[int, UUID], quest_id: Union[str, UUID], 
                              status: str, progress: float) -> Relationship:
        """
        Create a quest relationship between a character and a quest.
        
        Args:
            character_id: The ID of the character
            quest_id: The UUID of the quest
            status: Current quest status (active, completed, failed)
            progress: Float progress value (0.0 to 1.0)
            
        Returns:
            The created relationship object
        """
        if not self.relationship_service:
            raise ValueError("RelationshipService not available - inject as dependency")
            
        character = self._get_character_orm_by_id(character_id)
        
        relationship = self.relationship_service.create_relationship(
            character.uuid,
            quest_id,
            RelationshipType.QUEST,
            {
                "status": status, 
                "progress": progress,
                "started_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }
        )
        
        return relationship
        
    def add_character_relationship(self, source_character_id: Union[int, UUID], 
                                 target_character_id: Union[int, UUID],
                                 relationship_data: Dict[str, Any]) -> Relationship:
        """
        Create a character-to-character relationship.
        
        Args:
            source_character_id: The ID of the source character
            target_character_id: The ID of the target character
            relationship_data: Dictionary of relationship attributes
            
        Returns:
            The created relationship object
        """
        if not self.relationship_service:
            raise ValueError("RelationshipService not available - inject as dependency")
            
        source_character = self._get_character_orm_by_id(source_character_id)
        target_character = self._get_character_orm_by_id(target_character_id)
        
        relationship = self.relationship_service.create_relationship(
            source_character.uuid,
            target_character.uuid,
            RelationshipType.CHARACTER,
            relationship_data
        )
        
        return relationship
        
    # --- Mood System Integration ---
    def get_character_mood(self, character_id: Union[int, UUID]) -> CharacterMood:
        """
        Get the current mood for a character.
        
        Args:
            character_id: The ID of the character
            
        Returns:
            The character's mood object
        """
        character = self._get_character_orm_by_id(character_id)
        
        mood = self.mood_service.get_mood(character.uuid)
        return mood
        
    def add_character_mood_modifier(self, character_id: Union[int, UUID],
                                  emotional_state: str,
                                  intensity: str,
                                  reason: str,
                                  duration_hours: Optional[float] = None) -> MoodModifier:
        """
        Add a mood modifier to a character.
        
        Args:
            character_id: The ID of the character
            emotional_state: The emotion type
            intensity: The intensity level
            reason: Description of what caused this mood
            duration_hours: How long the modifier lasts
            
        Returns:
            The created mood modifier
        """
        character = self._get_character_orm_by_id(character_id)
        
        modifier = self.mood_service.add_mood_modifier(
            character.uuid,
            emotional_state,
            intensity,
            reason,
            duration_hours
        )
        
        return modifier
        
    # --- Goal System Integration ---
    def add_character_goal(self, character_id: Union[int, UUID],
                         description: str,
                         goal_type: Optional[str] = None,
                         priority: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Goal:
        """
        Add a new goal to a character.
        
        Args:
            character_id: The ID of the character
            description: Description of the goal
            goal_type: Type of goal
            priority: Goal priority
            metadata: Additional goal metadata
            
        Returns:
            The created goal
        """
        character = self._get_character_orm_by_id(character_id)
        
        goal = self.goal_service.add_goal(
            character.uuid,
            description,
            goal_type,
            priority,
            metadata
        )
        
        return goal
        
    def get_character_goals(self, character_id: Union[int, UUID],
                          status: Optional[str] = None,
                          goal_type: Optional[str] = None,
                          priority: Optional[str] = None) -> List[Goal]:
        """
        Get goals for a character, optionally filtered.
        
        Args:
            character_id: The ID of the character
            status: Filter by status
            goal_type: Filter by type
            priority: Filter by priority
            
        Returns:
            List of matching goals
        """
        character = self._get_character_orm_by_id(character_id)
        
        goals = self.goal_service.get_character_goals(
            character.uuid,
            goal_type,
            status,
            priority
        )
        
        return goals
        
    def update_goal_progress(self, character_id: Union[int, UUID],
                           goal_id: Union[str, UUID],
                           progress: float) -> Goal:
        """
        Update the progress of a character's goal.
        
        Args:
            character_id: The ID of the character
            goal_id: The ID of the goal
            progress: New progress value (0.0 to 1.0)
            
        Returns:
            The updated goal
        """
        character = self._get_character_orm_by_id(character_id)
        
        goal = self.goal_service.update_goal_progress(
            character.uuid,
            goal_id,
            progress
        )
        
        return goal
        
    def complete_goal(self, character_id: Union[int, UUID],
                    goal_id: Union[str, UUID]) -> Goal:
        """
        Mark a character's goal as completed.
        
        Args:
            character_id: The ID of the character
            goal_id: The ID of the goal
            
        Returns:
            The updated goal
        """
        character = self._get_character_orm_by_id(character_id)
        
        goal = self.goal_service.complete_goal(
            character.uuid,
            goal_id
        )
        
        # Add a positive mood modifier for completing a goal
        self.mood_service.add_mood_modifier(
            character.uuid,
            EmotionalState.PROUD,
            MoodIntensity.MEDIUM,
            f"Completed goal: {goal.description}",
            duration_hours=6
        )
        
        return goal
        
    def fail_goal(self, character_id: Union[int, UUID],
                goal_id: Union[str, UUID],
                reason: Optional[str] = None) -> Goal:
        """
        Mark a character's goal as failed.
        
        Args:
            character_id: The ID of the character
            goal_id: The ID of the goal
            reason: Optional reason for failure
            
        Returns:
            The updated goal
        """
        character = self._get_character_orm_by_id(character_id)
        
        goal = self.goal_service.fail_goal(
            character.uuid,
            goal_id,
            reason
        )
        
        # Add a negative mood modifier for failing a goal
        self.mood_service.add_mood_modifier(
            character.uuid,
            EmotionalState.DISAPPOINTED,
            MoodIntensity.MEDIUM,
            f"Failed goal: {goal.description}" + (f" - {reason}" if reason else ""),
            duration_hours=4
        )
        
        return goal

    def build_character_from_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a Character from input data and returns a dictionary representation.
        
        Args:
            input_data: Dictionary of character attributes
            
        Returns:
            Dictionary representation of created character
        """
        self.validate_character_creation_data(input_data)
        
        # Create a builder and use it to create the character
        builder = CharacterBuilder()
        builder.load_from_input(input_data)
        
        character_orm = self.create_character_from_builder(builder)
        
        # Initialize basic goals based on character background/abilities
        self._initialize_character_goals(character_orm)
        
        # Initialize starting mood based on character background
        self._initialize_character_mood(character_orm)
        
        return character_orm.to_dict() if hasattr(character_orm, 'to_dict') else {'id': character_orm.id, 'name': character_orm.name}
        
    def _initialize_character_goals(self, character: Character) -> None:
        """
        Initialize basic goals for a new character based on their background/abilities.
        
        Args:
            character: The character object
        """
        # Add a basic goal based on character's prominent abilities or background
        background = character.stats.get('background')
        abilities = character.stats.get('abilities', [])
        
        if background:
            background_goals = {
                'acolyte': 'Increase standing with deity',
                'criminal': 'Acquire a valuable item through stealth',
                'folk_hero': 'Help the common people',
                'noble': 'Maintain or increase social standing',
                'sage': 'Discover new knowledge',
                'soldier': 'Complete a military objective'
            }
            
            default_goal = background_goals.get(background.lower(), 'Advance abilities and skills')
        elif abilities:
            # Generate goal based on abilities
            ability_goals = {
                'martial_prowess': 'Test strength against a worthy opponent',
                'arcane_initiate': 'Learn a new spell or magical technique',
                'divine_magic': 'Fulfill a divine mission',
                'stealth_master': 'Complete a stealth-based objective',
                'social_expert': 'Build influential relationships'
            }
            
            # Use the first ability that has an associated goal
            default_goal = None
            for ability in abilities:
                if ability in ability_goals:
                    default_goal = ability_goals[ability]
                    break
            
            if not default_goal:
                default_goal = 'Master new abilities and techniques'
        else:
            default_goal = 'Advance abilities and skills'
            
        self.add_character_goal(
            character.id,
            default_goal,
            GoalType.PERSONAL,
            GoalPriority.MEDIUM
        )
            
        # Add a universal goal
        self.add_character_goal(
            character.id,
            'Build reputation in the world',
            GoalType.NARRATIVE,
            GoalPriority.LOW,
            {'long_term': True}
        )
        
    def _initialize_character_mood(self, character: Character) -> None:
        """
        Initialize starting mood for a new character based on their background.
        
        Args:
            character: The character object
        """
        background = character.background
        
        # Default is neutral mood
        emotional_state = EmotionalState.NEUTRAL
        intensity = MoodIntensity.MILD
        reason = "Starting a new adventure"
        
        # Adjust based on background if available
        if background:
            background_moods = {
                'soldier': (EmotionalState.SERIOUS, MoodIntensity.MEDIUM, "Military training instills discipline"),
                'criminal': (EmotionalState.CAUTIOUS, MoodIntensity.MEDIUM, "Always watching for trouble"),
                'noble': (EmotionalState.PROUD, MoodIntensity.MILD, "Sense of nobility and purpose"),
                'sage': (EmotionalState.CURIOUS, MoodIntensity.MEDIUM, "Thirst for knowledge"),
                'hermit': (EmotionalState.CALM, MoodIntensity.STRONG, "Years of solitude brings inner peace"),
                'outlander': (EmotionalState.VIGILANT, MoodIntensity.MEDIUM, "Survival instincts from the wilds"),
                'urchin': (EmotionalState.CAUTIOUS, MoodIntensity.STRONG, "Street smarts and wariness"),
                'entertainer': (EmotionalState.HAPPY, MoodIntensity.MEDIUM, "Born performer with flair")
            }
            
            if background.lower() in background_moods:
                emotional_state, intensity, reason = background_moods[background.lower()]
        
        # Set the initial mood
        self.add_character_mood_modifier(
            character.id,
            emotional_state,
            intensity,
            reason,
            duration_hours=24  # Initial mood lasts a day
        )

    # --- Visual Model Integration Methods ---
    def get_character_visual_model(self, character_id: Union[int, UUID]):
        """Get the visual model for a character."""
        from backend.systems.character.models.visual_model import CharacterModel
        
        character = self._get_character_orm_by_id(character_id)
        return character.get_visual_model()
    
    def set_character_visual_model(self, character_id: Union[int, UUID], 
                                 visual_model_data: Union[Dict[str, Any], "CharacterModel"], 
                                 commit: bool = True):
        """Set the visual model for a character."""
        character = self._get_character_orm_by_id(character_id)
        character.set_visual_model(visual_model_data)
        
        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(character)
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to update character visual model: {str(e)}")
        
        return character.get_visual_model()
    
    def update_character_appearance(self, character_id: Union[int, UUID], 
                                  appearance_updates: Dict[str, Any], 
                                  commit: bool = True):
        """Update specific aspects of a character's visual appearance."""
        character = self._get_character_orm_by_id(character_id)
        character.update_visual_appearance(appearance_updates)
        
        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(character)
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to update character appearance: {str(e)}")
        
        return character.get_visual_model()
    
    def randomize_character_appearance(self, character_id: Union[int, UUID], 
                                     constraints: Optional[Dict[str, Any]] = None,
                                     commit: bool = True):
        """Randomize a character's visual appearance within optional constraints."""
        character = self._get_character_orm_by_id(character_id)
        visual_model = character.get_visual_model()
        visual_model.randomize(constraints)
        character.set_visual_model(visual_model)
        
        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(character)
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to randomize character appearance: {str(e)}")
        
        return visual_model
    
    def apply_visual_preset(self, character_id: Union[int, UUID], 
                          preset_data: Dict[str, Any], 
                          commit: bool = True):
        """Apply a visual preset to a character's appearance."""
        character = self._get_character_orm_by_id(character_id)
        visual_model = character.get_visual_model()
        visual_model.apply_preset(preset_data)
        character.set_visual_model(visual_model)
        
        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(character)
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to apply visual preset: {str(e)}")
        
        return visual_model
    
    def export_character_visual_data(self, character_id: Union[int, UUID]) -> Dict[str, Any]:
        """Export a character's visual model data for external use."""
        character = self._get_character_orm_by_id(character_id)
        visual_model = character.get_visual_model()
        return visual_model.to_dict()
    
    def import_character_visual_data(self, character_id: Union[int, UUID], 
                                   visual_data: Dict[str, Any], 
                                   commit: bool = True):
        """Import visual model data for a character."""
        from backend.systems.character.models.visual_model import CharacterModel
        
        character = self._get_character_orm_by_id(character_id)
        visual_model = CharacterModel.from_dict(visual_data)
        character.set_visual_model(visual_model)
        
        if commit:
            try:
                self.character_repository.commit()
                self.character_repository.refresh(character)
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to import visual data: {str(e)}")
        
        return visual_model

    def _setup_character_inventory(self, character: Character, char_data: Dict[str, Any], commit: bool = True):
        """
        Set up inventory and starting equipment for a new character.
        
        Args:
            character: Character ORM instance
            char_data: Character data from builder
            commit: Whether to commit changes
        """
        # Import here to avoid circular imports
        from backend.systems.inventory.services.inventory_service import InventoryService
        
        inventory_service = InventoryService()
        
        # Create character's main inventory
        character_inventory = inventory_service.get_or_create_inventory(
            owner_id=str(character.uuid),
            owner_type='character',
            name=f"{character.name}'s Inventory",
            max_slots=20,  # Default inventory size
            max_weight=100.0  # Default weight limit
        )
        
        # Add starter equipment from starter kit
        starter_equipment = char_data.get("starter_kit", {}).get("equipment", [])
        for equipment_item in starter_equipment:
            try:
                # equipment_item could be a string (item name) or dict (item with quantity)
                if isinstance(equipment_item, str):
                    item_name = equipment_item
                    quantity = 1
                elif isinstance(equipment_item, dict):
                    item_name = equipment_item.get("name") or equipment_item.get("item")
                    quantity = equipment_item.get("quantity", 1)
                else:
                    continue
                    
                # Add item to inventory
                inventory_service.add_item_to_inventory(
                    inventory_id=character_inventory.id,
                    item_identifier=item_name,
                    quantity=quantity
                )
                logger.debug(f"Added {quantity}x {item_name} to {character.name}'s inventory")
                
            except Exception as e:
                logger.warning(f"Failed to add starter item {equipment_item}: {str(e)}")
        
        # Set starting gold
        starting_gold = char_data.get("gold", 0)
        if starting_gold > 0:
            inventory_service.update_inventory_currency(character_inventory.id, starting_gold)
            
        if commit:
            try:
                self.character_repository.commit()
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to setup character inventory: {str(e)}")
    
    def _setup_character_skills(self, character: Character, char_data: Dict[str, Any], commit: bool = True):
        """
        Set up character skills using the new JSON-based system.
        Stores skill proficiencies directly in the character's skills JSON field.
        
        Args:
            character: Character instance to configure
            char_data: Character data containing skills information
            commit: Whether to commit to database
        """
        try:
            skills_data = char_data.get("skills", [])
            
            # Initialize skills as empty dict if not already set
            if not hasattr(character, 'skills') or character.skills is None:
                character.skills = {}
            
            # Handle skills as list (default proficiency) or dict (with custom proficiency data)
            if isinstance(skills_data, list):
                # Simple list of skill names - all get basic proficiency
                for skill_name in skills_data:
                    # Validate skill exists in configuration
                    skill_info = config_loader.get_skill_info(skill_name)
                    if skill_info:
                        canonical_name = skill_info["name"]
                        character.skills[canonical_name] = {
                            "proficient": True,
                            "expertise": False,
                            "bonus": 0
                        }
                    else:
                        logger.warning(f"Unknown skill '{skill_name}' skipped for character {character.name}")
                        
            elif isinstance(skills_data, dict):
                # Dict format: {"skill_name": proficiency_data or True/False}
                for skill_name, skill_data in skills_data.items():
                    # Validate skill exists in configuration
                    skill_info = config_loader.get_skill_info(skill_name)
                    if not skill_info:
                        logger.warning(f"Unknown skill '{skill_name}' skipped for character {character.name}")
                        continue
                        
                    canonical_name = skill_info["name"]
                    
                    if isinstance(skill_data, bool):
                        # Simple boolean proficiency
                        character.skills[canonical_name] = {
                            "proficient": skill_data,
                            "expertise": False,
                            "bonus": 0
                        }
                    elif isinstance(skill_data, dict):
                        # Full proficiency data
                        character.skills[canonical_name] = {
                            "proficient": skill_data.get("proficient", True),
                            "expertise": skill_data.get("expertise", False),
                            "bonus": skill_data.get("bonus", 0)
                        }
                    else:
                        # Default to proficient if unclear
                        character.skills[canonical_name] = {
                            "proficient": True,
                            "expertise": False,
                            "bonus": 0
                        }
            
            # Apply racial skill bonuses if any
            if character.race:
                races_config = config_loader.load_races_config()
                race_data = races_config.get(character.race, {})
                skill_bonuses = race_data.get("skill_bonuses", {})
                
                for skill_name, bonus in skill_bonuses.items():
                    # Validate skill exists
                    skill_info = config_loader.get_skill_info(skill_name)
                    if skill_info:
                        canonical_name = skill_info["name"]
                        if canonical_name not in character.skills:
                            character.skills[canonical_name] = {
                                "proficient": False,
                                "expertise": False,
                                "bonus": bonus
                            }
                        else:
                            character.skills[canonical_name]["bonus"] += bonus
            
            if commit:
                self.character_repository.commit()
                
            logger.info(f"Set up {len(character.skills)} skills for character {character.name}")
            
        except Exception as e:
            logger.error(f"Failed to set up character skills: {e}")
            if commit:
                self.character_repository.rollback()
            raise RepositoryError(f"Failed to set up character skills: {e}")

    def process_character_action(self, character_id: UUID, action_data: dict) -> dict:
        """
        Process a character action and update hidden attributes based on choices
        
        Args:
            character_id: ID of character performing action
            action_data: Dictionary containing action details
            
        Returns:
            Result of attribute adjustment
        """
        character = self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        # Analyze action impact
        recommendations = self.hidden_attribute_engine.analyze_action_impact(
            str(character_id), action_data
        )
        
        # Apply changes if confidence is high enough
        result = self.hidden_attribute_engine.apply_gradual_changes(character, recommendations)
        
        if result["applied"]:
            # Save character changes
            try:
                self.character_repository.update(character)
                self.character_repository.commit()
                
                # Dispatch event for hidden attribute change
                self.event_dispatcher.dispatch(CharacterUpdated(
                    character_id=character_id,
                    change_type="hidden_attributes",
                    changes=result["changes"],
                    reason=action_data.get("choice", "unknown_action")
                ))
                
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to save character attribute changes: {e}")
        
        return result
    
    def process_character_action_batch(self, character_id: UUID, actions: list) -> dict:
        """
        Process multiple character actions for cumulative attribute adjustments
        
        Args:
            character_id: ID of character performing actions
            actions: List of action dictionaries
            
        Returns:
            Result of batch attribute adjustment
        """
        character = self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        # Add character_id to each action
        for action in actions:
            action["character_id"] = str(character_id)
        
        # Get batch recommendations
        recommendations = self.hidden_attribute_engine.get_batch_recommendations(actions)
        
        # Apply changes
        result = self.hidden_attribute_engine.apply_gradual_changes(character, recommendations)
        
        if result["applied"]:
            try:
                self.character_repository.update(character)
                self.character_repository.commit()
                
                # Dispatch event for batch attribute changes
                self.event_dispatcher.dispatch(CharacterUpdated(
                    character_id=character_id,
                    change_type="hidden_attributes_batch",
                    changes=result["changes"],
                    action_count=recommendations["action_count"]
                ))
                
            except Exception as e:
                self.character_repository.rollback()
                raise RepositoryError(f"Failed to save batch character attribute changes: {e}")
        
        return result
    
    def get_character_hidden_attributes(self, character_id: UUID) -> dict:
        """
        Get character's hidden personality attributes (for admin/debug use)
        
        Args:
            character_id: Character ID
            
        Returns:
            Dictionary of hidden attributes
        """
        character = self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        return getattr(character, 'hidden_personality', {})
    
    def predict_character_behavior(self, character_id: UUID) -> dict:
        """
        Predict character behavior tendencies based on hidden attributes
        
        Args:
            character_id: Character ID
            
        Returns:
            Dictionary of behavioral predictions
        """
        character = self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        hidden_attrs = getattr(character, 'hidden_personality', {})
        if not hidden_attrs:
            return {"error": "No hidden personality data available"}
        
        # Calculate behavioral tendencies
        tendencies = {}
        
        # Aggression tendency (impulsivity + low discipline)
        aggression = (hidden_attrs.get('impulsivity', 3) + (6 - hidden_attrs.get('discipline', 3))) / 2
        tendencies['aggression_level'] = self._categorize_attribute(aggression)
        
        # Trustworthiness (integrity + discipline)
        trustworthiness = (hidden_attrs.get('integrity', 3) + hidden_attrs.get('discipline', 3)) / 2
        tendencies['trustworthiness'] = self._categorize_attribute(trustworthiness)
        
        # Risk tolerance (impulsivity + ambition - pragmatism)
        risk_tolerance = (hidden_attrs.get('impulsivity', 3) + hidden_attrs.get('ambition', 3) - hidden_attrs.get('pragmatism', 3)) / 2
        tendencies['risk_tolerance'] = self._categorize_attribute(max(0, min(6, risk_tolerance)))
        
        # Leadership potential (ambition + discipline + integrity)
        leadership = (hidden_attrs.get('ambition', 3) + hidden_attrs.get('discipline', 3) + hidden_attrs.get('integrity', 3)) / 3
        tendencies['leadership_potential'] = self._categorize_attribute(leadership)
        
        # Stress handling (resilience + discipline)
        stress_handling = (hidden_attrs.get('resilience', 3) + hidden_attrs.get('discipline', 3)) / 2
        tendencies['stress_handling'] = self._categorize_attribute(stress_handling)
        
        return {
            "tendencies": tendencies,
            "raw_attributes": hidden_attrs,
            "interpretation": "These predictions are based on hidden personality attributes and may change over time"
        }
    
    def _categorize_attribute(self, value: float) -> str:
        """Helper method to categorize attribute values"""
        if value >= 5:
            return "very_high"
        elif value >= 4:
            return "high"
        elif value >= 3:
            return "moderate"
        elif value >= 2:
            return "low"
        else:
            return "very_low"

    # --- Dynamic LLM Interaction Methods ---
    
    async def generate_character_dialogue(self, character_id: UUID, 
                                        context: str,
                                        player_input: Optional[str] = None,
                                        conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Generate dynamic dialogue for a character using LLM based on personality and context.
        
        Args:
            character_id: Character ID
            context: Current situation/context for dialogue
            player_input: What the player said (if any)
            conversation_history: Previous conversation turns
            
        Returns:
            Dictionary containing generated dialogue and metadata
        """
        if not self.llm_service:
            return {
                "dialogue": "I have nothing to say right now.",
                "error": "LLM service not available",
                "generated_via": "fallback"
            }
        
        character = self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        try:
            # Prepare character context for LLM
            personality_description = format_personality_for_display(
                getattr(character, 'hidden_personality', {}),
                include_full_profile=True,
                profession=getattr(character, 'profession', None),
                race=getattr(character, 'race', None),
                age=getattr(character, 'age', None)
            )
            
            # Get current mood if available
            mood_context = ""
            if self.mood_service:
                try:
                    mood = self.mood_service.get_mood(character.uuid)
                    if mood:
                        mood_context = f"Current mood: {mood.current_emotional_state} (intensity: {mood.current_intensity})"
                except:
                    pass
            
            # Format conversation history
            history_text = ""
            if conversation_history:
                history_lines = []
                for turn in conversation_history[-5:]:  # Last 5 turns
                    speaker = turn.get('speaker', 'Unknown')
                    message = turn.get('message', '')
                    history_lines.append(f"{speaker}: {message}")
                history_text = "\n".join(history_lines)
            
            # Create prompt for dialogue generation
            template_vars = {
                "character_name": getattr(character, 'name', 'Unknown'),
                "personality": personality_description,
                "mood": mood_context,
                "context": context,
                "player_input": player_input or "No player input",
                "conversation_history": history_text or "No previous conversation",
            }
            
            # Generate dialogue using LLM
            response = await self.llm_service.generate_with_template(
                "character_dialogue",
                template_vars,
                context=GenerationContext.DIALOGUE
            )
            
            return {
                "dialogue": response.get("content", "I have nothing to say."),
                "generated_via": "llm",
                "character_id": str(character_id),
                "context_used": context,
                "mood_influence": mood_context,
                "generation_metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to generate character dialogue: {e}")
            return {
                "dialogue": "I'm not sure what to say right now.",
                "error": str(e),
                "generated_via": "error_fallback"
            }
    
    async def generate_character_reaction(self, character_id: UUID, 
                                        event_description: str,
                                        emotional_impact: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a character's reaction to an event based on their personality.
        
        Args:
            character_id: Character ID
            event_description: Description of what happened
            emotional_impact: Optional description of emotional impact
            
        Returns:
            Dictionary containing reaction and any mood changes
        """
        if not self.llm_service:
            return {
                "reaction": "The character notices what happened.",
                "error": "LLM service not available",
                "generated_via": "fallback"
            }
        
        character = self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        try:
            # Get personality context
            personality_description = format_personality_for_display(
                getattr(character, 'hidden_personality', {}),
                include_full_profile=True
            )
            
            template_vars = {
                "character_name": getattr(character, 'name', 'Unknown'),
                "personality": personality_description,
                "event": event_description,
                "emotional_impact": emotional_impact or "moderate impact"
            }
            
            # Generate reaction
            response = await self.llm_service.generate_with_template(
                "character_reaction",
                template_vars,
                context=GenerationContext.NARRATIVE
            )
            
            # Apply any mood changes based on the reaction
            mood_changes = []
            if self.mood_service and emotional_impact:
                try:
                    # Simple mood impact logic - could be enhanced
                    if "positive" in emotional_impact.lower():
                        modifier = self.mood_service.add_mood_modifier(
                            character.uuid,
                            "happy",
                            "medium",
                            f"Reaction to: {event_description}",
                            duration_hours=2
                        )
                        mood_changes.append(modifier)
                    elif "negative" in emotional_impact.lower():
                        modifier = self.mood_service.add_mood_modifier(
                            character.uuid,
                            "upset",
                            "medium", 
                            f"Reaction to: {event_description}",
                            duration_hours=2
                        )
                        mood_changes.append(modifier)
                except Exception as mood_error:
                    logger.warning(f"Failed to apply mood changes: {mood_error}")
            
            return {
                "reaction": response.get("content", "The character reacts to the event."),
                "generated_via": "llm",
                "mood_changes": [change.to_dict() for change in mood_changes],
                "generation_metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to generate character reaction: {e}")
            return {
                "reaction": "The character seems to notice what happened.",
                "error": str(e),
                "generated_via": "error_fallback"
            }

    async def transform_rumor_through_character(self, character_id: UUID,
                                             original_rumor: str,
                                             event_context: str,
                                             distortion_level: float = 0.3) -> Dict[str, Any]:
        """
        Transform a rumor as it might be retold by this specific character.
        Uses the existing RumorPromptManager pattern with actual LLM integration.
        
        Args:
            character_id: Character ID
            original_rumor: The original rumor text
            event_context: Context about the original event
            distortion_level: How much to distort (0.0 = truthful, 1.0 = wildly distorted)
            
        Returns:
            Dictionary containing transformed rumor and metadata
        """
        if not self.llm_service:
            return {
                "transformed_rumor": original_rumor,
                "error": "LLM service not available",
                "generated_via": "passthrough"
            }
        
        character = self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError(f"Character {character_id} not found")
        
        try:
            # Get personality traits for rumor transformation
            personality_description = format_personality_for_display(
                getattr(character, 'hidden_personality', {}),
                include_full_profile=False  # Brief description for rumor context
            )
            
            # Import and use the existing RumorPromptManager
            from backend.systems.character.services.prompt_manager import RumorPromptManager
            
            # Build the prompt using existing pattern
            prompt = RumorPromptManager.build_prompt(
                event_context,
                original_rumor,
                personality_description,
                distortion_level
            )
            
            # Generate transformed rumor
            response = await self.llm_service.generate_content(
                prompt,
                context=GenerationContext.NARRATIVE
            )
            
            return {
                "transformed_rumor": response.get("content", original_rumor),
                "original_rumor": original_rumor,
                "character_id": str(character_id),
                "distortion_level": distortion_level,
                "personality_influence": personality_description,
                "generated_via": "llm",
                "generation_metadata": response.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to transform rumor through character: {e}")
            return {
                "transformed_rumor": original_rumor,
                "error": str(e),
                "generated_via": "error_fallback"
            }

class HiddenAttributeAdjustmentEngine:
    """
    Analyzes player actions and recommends hidden attribute changes
    """
    
    def __init__(self):
        # Action type mapping to attribute impact patterns
        self.action_patterns = {
            "dialogue_choice": {
                "threatens": {"impulsivity": 1, "integrity": -1},
                "lies": {"integrity": -2, "pragmatism": 1},
                "diplomatic": {"pragmatism": 1, "integrity": 1},
                "aggressive": {"impulsivity": 2, "discipline": -1},
                "helps_stranger": {"integrity": 2, "pragmatism": -1},
                "breaks_promise": {"integrity": -2, "discipline": -1},
                "keeps_promise_despite_cost": {"integrity": 2, "discipline": 1},
                "sacrifices_for_others": {"integrity": 2, "resilience": 1, "pragmatism": -1},
                "betrays_ally": {"integrity": -3, "pragmatism": 1}
            },
            "combat_choice": {
                "flees_immediately": {"impulsivity": 1, "resilience": -1},
                "fights_hopeless_battle": {"resilience": 2, "pragmatism": -2},
                "protects_weak": {"integrity": 2, "resilience": 1},
                "abandons_allies": {"integrity": -2, "pragmatism": 1},
                "tactical_retreat": {"discipline": 1, "pragmatism": 1},
                "charges_recklessly": {"impulsivity": 2, "discipline": -1}
            },
            "resource_management": {
                "hoards_supplies": {"pragmatism": 1, "integrity": -1},
                "shares_resources": {"integrity": 1, "pragmatism": -1},
                "wastes_resources": {"discipline": -1, "impulsivity": 1},
                "saves_for_emergency": {"discipline": 1, "pragmatism": 1}
            },
            "quest_choice": {
                "accepts_despite_danger": {"ambition": 1, "resilience": 1},
                "refuses_easy_money": {"integrity": 1, "pragmatism": -1},
                "abandons_difficult_quest": {"resilience": -1, "discipline": -1},
                "persists_against_odds": {"resilience": 2, "discipline": 1}
            }
        }
        
        # Confidence thresholds
        self.confidence_threshold = 0.7
        self.max_change_per_action = 1  # Max attribute change per single action
        self.change_decay_rate = 0.1  # How much changes fade over time
        
    def analyze_action_impact(self, character_id: str, action_data: dict) -> dict:
        """
        Returns recommended attribute adjustments based on action
        
        Args:
            character_id: Character performing action
            action_data: Dictionary with action details
             
        Returns:
            Dictionary with recommended changes and confidence
        """
        action_type = action_data.get("action_type", "unknown")
        choice = action_data.get("choice", "unknown")
        context = action_data.get("context", "")
        outcome = action_data.get("outcome", "")
        
        # Get base pattern for this action type and choice
        base_changes = {}
        confidence = 0.5  # Default confidence
        
        if action_type in self.action_patterns:
            if choice in self.action_patterns[action_type]:
                base_changes = self.action_patterns[action_type][choice].copy()
                confidence = 0.8  # High confidence for known patterns
        
        # Context modifiers
        if context and outcome:
            confidence += 0.1  # Boost confidence when we have context
            
            # Modify based on outcome
            if "success" in outcome.lower():
                # Successful outcomes don't change the moral implications but boost confidence
                confidence = min(1.0, confidence + 0.1)
            elif "failure" in outcome.lower():
                # Failed outcomes might reduce some attribute gains
                for attr in base_changes:
                    if base_changes[attr] > 0:
                        base_changes[attr] = max(0, base_changes[attr] - 1)
        
        # Cap individual changes
        for attr in base_changes:
            base_changes[attr] = max(-self.max_change_per_action, 
                                   min(self.max_change_per_action, base_changes[attr]))
        
        return {
            "changes": base_changes,
            "confidence": confidence,
            "reason": f"Action: {choice} in {context}"
        }
    
    def get_batch_recommendations(self, character_actions: list) -> dict:
        """
        Batch analyze multiple actions for cumulative recommendations
        """
        cumulative_changes = {}
        total_confidence = 0.0
        action_count = 0
        reasons = []
        
        for action in character_actions:
            result = self.analyze_action_impact(action.get("character_id"), action)
            
            # Accumulate changes
            for attr, change in result["changes"].items():
                cumulative_changes[attr] = cumulative_changes.get(attr, 0) + change
            
            total_confidence += result["confidence"]
            action_count += 1
            reasons.append(result["reason"])
        
        # Average confidence
        avg_confidence = total_confidence / max(action_count, 1)
        
        # Cap cumulative changes (prevent massive swings)
        max_cumulative = 3
        for attr in cumulative_changes:
            cumulative_changes[attr] = max(-max_cumulative, 
                                         min(max_cumulative, cumulative_changes[attr]))
        
        return {
            "changes": cumulative_changes,
            "confidence": avg_confidence,
            "action_count": action_count,
            "reasons": reasons
        }

    def apply_gradual_changes(self, character, recommendations: dict) -> dict:
        """
        Apply changes gradually over time (prevents sudden personality shifts)
        """
        if recommendations["confidence"] < self.confidence_threshold:
            return {"applied": False, "reason": "Confidence too low"}
        
        changes = recommendations["changes"]
        applied_changes = {}
        
        # Get current hidden personality
        current_personality = getattr(character, 'hidden_personality', {})
        if not current_personality:
            # Initialize with default values if missing
            current_personality = {
                'ambition': 3, 'integrity': 3, 'discipline': 3,
                'impulsivity': 3, 'pragmatism': 3, 'resilience': 3
            }
        
        # Apply changes with bounds checking (0-6 scale)
        for attr, change in changes.items():
            if attr in current_personality:
                old_value = current_personality[attr]
                new_value = max(0, min(6, old_value + change))
                
                if new_value != old_value:
                    current_personality[attr] = new_value
                    applied_changes[attr] = {"old": old_value, "new": new_value, "change": change}
        
        # Update character
        character.hidden_personality = current_personality
        
        return {
            "applied": True,
            "changes": applied_changes,
            "confidence": recommendations["confidence"]
        }