"""
Character Service
-----------------
Service layer for character-related operations, encapsulating business logic
and database interactions.
"""
from typing import Dict, List, Optional, Any, Tuple, Union # Added Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError # Added for more specific exception handling
from uuid import UUID, uuid4 # Added uuid4
import random # Added
import math # Added
from datetime import datetime # Added

# Assuming Character model exists and is an SQLAlchemy model
from backend.systems.character.models.character import Character, Skill # Assuming Skill is also needed here
# Assuming CharacterBuilder exists
from backend.systems.character.services.character_builder import CharacterBuilder
# Import the relationship, mood, and goal models/services
from backend.systems.character.models.relationship import Relationship, RelationshipType
from backend.systems.character.models.mood import CharacterMood, EmotionalState, MoodIntensity, MoodModifier
from backend.systems.character.models.goal import Goal, GoalType, GoalPriority, GoalStatus
# Import our services
from backend.systems.character.services.relationship_service import RelationshipService
from backend.systems.character.services.mood_service import MoodService
from backend.systems.character.services.goal_service import GoalService
# Import event dispatcher
from backend.infrastructure.events.event_dispatcher import EventDispatcher
from backend.infrastructure.events.canonical_events import (
    CharacterCreated, CharacterLeveledUp, CharacterUpdated, CharacterDeleted,
    MoodChanged, GoalCreated, GoalCompleted, GoalFailed, GoalProgressUpdated
)

# Assuming utility functions for db interaction and errors
from backend.infrastructure.database.session import get_db_session # Or however session is managed
from backend.infrastructure.shared.exceptions import NotFoundError, DatabaseError, ValidationError
from backend.infrastructure.shared.rules import balance_constants, load_data # For things like starting gold, etc.

# Constants from character_utils, can be moved to a config or rules file if preferred
RACES = ['human', 'elf', 'dwarf', 'halfling', 'gnome', 'half-elf', 'half-orc', 'tiefling']
CLASSES = ['fighter', 'wizard', 'cleric', 'rogue', 'barbarian', 'bard', 'druid', 'monk', 'paladin', 'ranger', 'sorcerer', 'warlock']

class CharacterService:
    def __init__(self, db_session: Optional[Session] = None):
        self.db = db_session if db_session else next(get_db())
        self.event_dispatcher = EventDispatcher()
        self.relationship_service = RelationshipService(db_session=self.db)
        self.mood_service = MoodService(db_session=self.db)
        self.goal_service = GoalService(db_session=self.db)
        
    # --- Helper Methods (adapted from character_utils.py) ---
    def _calculate_ability_modifier(self, score: int) -> int:
        """Calculate ability score modifier using standard D&D formula."""
        return (max(1, score) - 10) // 2

    def _has_spellcasting(self, class_name: str) -> bool:
        """Check if a class has spellcasting based on balance_constants."""
        # This relies on balance_constants.CLASS_SPELLCASTING_ABILITY being populated
        return class_name in balance_constants.CLASS_SPELLCASTING_ABILITY
    
    def _calculate_xp_for_level(self, level: int) -> int:
        """Calculate total XP needed to reach a given level."""
        if level <= 1:
            return 0
        # Formula: base_xp * (target_level - 1)^scaling_factor
        return int(balance_constants.BASE_XP * ((level -1) ** balance_constants.XP_SCALING_FACTOR))

    def _get_character_orm_by_id(self, character_id: Union[int, UUID]) -> Character:
        """Internal helper to fetch a Character ORM instance by ID."""
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise NotFoundError(f"Character with ID {character_id} not found")
        return character
        
    def _get_character_orm_by_uuid(self, character_uuid: Union[str, UUID]) -> Character:
        """Internal helper to fetch a Character ORM instance by UUID."""
        character = self.db.query(Character).filter(Character.uuid == str(character_uuid)).first()
        if not character:
            raise NotFoundError(f"Character with UUID {character_uuid} not found")
        return character

    # --- Core Character Methods (CRUD, Level up) ---
    def create_character_from_builder(self, builder: CharacterBuilder, commit: bool = True) -> Character:
        """Creates a new Character in the database from a CharacterBuilder instance."""
        if not builder.is_valid(): # Assumes builder has validation logic
            # This should ideally raise specific validation errors from the builder
            raise ValidationError("CharacterBuilder data is invalid.") 
            
        char_data = builder.finalize() # This returns a dictionary
        
        # Validate required fields from builder output (some might be handled by builder.is_valid)
        if not char_data.get("character_name") or not char_data.get("race"):
            raise ValidationError("Character name and race are required from builder output.")

        # Map char_data dictionary to Character ORM model fields
        new_character_orm = Character(
            name=char_data.get("character_name"),
            race=char_data.get("race"),
            level=char_data.get("level", 1),
            stats=char_data.get("attributes"), # Character.stats is JSON, stores STR, DEX, etc.
            background=char_data.get("background"), # From builder if available
            alignment=char_data.get("alignment", "Neutral"), # From builder or default
            notes=char_data.get("notes", []), # From builder if available
            # created_at and updated_at should be handled by SQLAlchemy model defaults
        )
        # Add other fields from char_data if they exist on the Character ORM model
        # Example: if Character ORM has 'xp' and 'gold' fields:
        # if 'XP' in char_data: new_character_orm.xp = char_data['XP']
        # if 'gold' in char_data: new_character_orm.gold = char_data['gold']

        self.db.add(new_character_orm)
        if commit:
            try:
                self.db.commit()
                self.db.refresh(new_character_orm)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to create character in DB: {str(e)}")
        
        # TODO: Handle inventory/equipment using InventoryService
        # inventory_service = InventoryService(db_session=self.db)
        # starter_equipment = char_data.get("starter_kit", {}).get("equipment", [])
        # character_inventory = inventory_service.get_or_create_inventory(new_character_orm.id, 'character')
        # for item_name_or_id in starter_equipment:
            # inventory_service.add_item_to_inventory(character_inventory.id, item_name_or_id, quantity=1)

        # TODO: Handle initial skills if Character ORM supports it (e.g., via relationships)
        # selected_skills_names = char_data.get("skills", [])
        # for skill_name in selected_skills_names:
        #    skill_orm = self.db.query(Skill).filter(Skill.name.ilike(skill_name)).first()
        #    if skill_orm and skill_orm not in new_character_orm.skills:
        #        new_character_orm.skills.append(skill_orm)
        # if commit and selected_skills_names: # commit again if skills were added to relationship
        #    try:
        #        self.db.commit()
        #    except SQLAlchemyError as e:
        #        self.db.rollback()
        #        raise DatabaseError(f"Failed to link skills to character: {str(e)}")

        # Initialize mood for the new character
        self.mood_service.initialize_mood(new_character_orm.uuid)
        
        # Dispatch character created event
        self.event_dispatcher.dispatch(CharacterCreated(
            character_id=new_character_orm.uuid,
            name=new_character_orm.name
        ))
        
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
        
        for key, value in update_data.items():
            if hasattr(character_orm, key):
                setattr(character_orm, key, value)
            elif key in character_orm.stats and isinstance(character_orm.stats, dict): # For updating within stats JSON
                # Ensure stats is a mutable dictionary if it's a JSON field
                if not isinstance(character_orm.stats, dict):
                    character_orm.stats = dict(character_orm.stats or {})
                character_orm.stats[key] = value
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(character_orm, "stats") # Mark JSON field as modified for SQLAlchemy
            else:
                # Log or handle fields not directly on the model or in primary stats JSON
                # Consider raising a ValidationError for unknown fields or logging a warning.
                print(f"Warning: Character ORM does not have attribute '{key}'. Update for this field might be ignored or need specific handling.")

        if commit:
            try:
                self.db.commit()
                self.db.refresh(character_orm)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to update character {character_id}: {str(e)}")
                
        # Dispatch character updated event
        self.event_dispatcher.dispatch(CharacterUpdated(
            character_id=character_orm.uuid,
            changes=update_data
        ))
        
        return character_orm

    def delete_character(self, character_id: Union[int, UUID], commit: bool = True) -> bool:
        """Deletes a Character from the database by its ID."""
        character_orm = self._get_character_orm_by_id(character_id)
        character_uuid = character_orm.uuid  # Save UUID for event dispatch
        
        self.db.delete(character_orm)
        if commit:
            try:
                self.db.commit()
                
                # Dispatch character deleted event
                self.event_dispatcher.dispatch(CharacterDeleted(
                    character_id=character_uuid
                ))
                
                return True
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to delete character {character_id}: {str(e)}")
        return False # If commit is false, indicates success of marking for deletion (but not committed)

    def level_up_character(self, character_id: Union[int, UUID], commit: bool = True) -> Character:
        """Handles the logic for leveling up a character."""
        character_orm = self._get_character_orm_by_id(character_id)
        
        # Ensure stats is a mutable dictionary if it's a JSON field being modified
        current_stats = dict(character_orm.stats or {})
        current_level = character_orm.level
        char_class = character_orm.stats.get('class') # Assuming class is stored in stats
        if not char_class: # Or character_orm.class_ if it's a direct field
            raise ValidationError("Character class not defined, cannot process level up.")

        # HP gain
        con_score = current_stats.get('constitution', 10)
        con_mod = self._calculate_ability_modifier(con_score)
        hit_die = balance_constants.CLASS_HIT_DICE.get(char_class, balance_constants.DEFAULT_HIT_DIE)
        hp_gain = max(1, random.randint(1, hit_die) + con_mod)
        current_stats['hit_points'] = current_stats.get('hit_points', 0) + hp_gain
        
        # MP gain (if spellcaster)
        if self._has_spellcasting(char_class):
            spellcasting_ability_name = balance_constants.CLASS_SPELLCASTING_ABILITY.get(char_class, 'wisdom')
            spellcasting_score = current_stats.get(spellcasting_ability_name.lower(), 10)
            ability_mod = self._calculate_ability_modifier(spellcasting_score)
            mana_die = balance_constants.CLASS_MANA_DICE.get(char_class, balance_constants.DEFAULT_MANA_DIE)
            mp_gain = max(0, random.randint(1, mana_die) + ability_mod)
            current_stats['mana_points'] = current_stats.get('mana_points', 0) + mp_gain
        
        # Update level and skill points
        character_orm.level += 1
        current_stats['skill_points'] = current_stats.get('skill_points', 0) + balance_constants.SKILL_POINTS_PER_LEVEL
        
        # Update XP to the threshold of the new level
        new_level = character_orm.level
        current_stats['xp'] = self._calculate_xp_for_level(new_level)
        
        # Update character stats (assuming stats is a JSON field)
        character_orm.stats = current_stats
        
        if commit:
            try:
                self.db.commit()
                self.db.refresh(character_orm)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to level up character {character_id}: {str(e)}")
                
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
        """Validates the data used for character creation."""
        required_fields = ['name', 'race']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")
                
        # Check for valid race
        if data.get('race') and data.get('race') not in RACES:
            raise ValidationError(f"Invalid race: {data.get('race')}. Valid races are: {', '.join(RACES)}")
            
        # If class is provided, check if valid
        if data.get('class') and data.get('class') not in CLASSES:
            raise ValidationError(f"Invalid class: {data.get('class')}. Valid classes are: {', '.join(CLASSES)}")

    # --- Relationship Integration ---
    def add_faction_relationship(self, character_id: Union[int, UUID], faction_id: Union[str, UUID], 
                                reputation: int, standing: str) -> Relationship:
        """
        Create a faction relationship between a character and a faction.
        
        Args:
            character_id: The ID of the character
            faction_id: The UUID of the faction
            reputation: Numerical reputation value
            standing: String representation of standing (friendly, neutral, hostile)
            
        Returns:
            The created relationship object
        """
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
        
        # Initialize basic goals based on character background/class
        self._initialize_character_goals(character_orm)
        
        # Initialize starting mood based on character background
        self._initialize_character_mood(character_orm)
        
        return character_orm.to_dict() if hasattr(character_orm, 'to_dict') else {'id': character_orm.id, 'name': character_orm.name}
        
    def _initialize_character_goals(self, character: Character) -> None:
        """
        Initialize basic goals for a new character based on their class/background.
        
        Args:
            character: The character object
        """
        # Add a basic goal based on character class
        char_class = character.stats.get('class')
        if char_class:
            class_goals = {
                'fighter': 'Master a new combat technique',
                'wizard': 'Learn a new spell',
                'cleric': 'Increase standing with deity',
                'rogue': 'Acquire a valuable item through stealth',
                'barbarian': 'Test strength against a worthy opponent',
                'bard': 'Compose a tale of recent adventures',
                'druid': 'Commune with nature in a new environment',
                'monk': 'Achieve a higher state of meditation',
                'paladin': 'Uphold oath in a challenging situation',
                'ranger': 'Track a dangerous creature',
                'sorcerer': 'Control growing magical abilities',
                'warlock': 'Fulfill a task for patron'
            }
            
            default_goal = class_goals.get(char_class.lower(), 'Advance skills and abilities')
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
                self.db.commit()
                self.db.refresh(character)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to update character visual model: {str(e)}")
        
        return character.get_visual_model()
    
    def update_character_appearance(self, character_id: Union[int, UUID], 
                                  appearance_updates: Dict[str, Any], 
                                  commit: bool = True):
        """Update specific aspects of a character's visual appearance."""
        character = self._get_character_orm_by_id(character_id)
        character.update_visual_appearance(appearance_updates)
        
        if commit:
            try:
                self.db.commit()
                self.db.refresh(character)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to update character appearance: {str(e)}")
        
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
                self.db.commit()
                self.db.refresh(character)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to randomize character appearance: {str(e)}")
        
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
                self.db.commit()
                self.db.refresh(character)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to apply visual preset: {str(e)}")
        
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
                self.db.commit()
                self.db.refresh(character)
            except SQLAlchemyError as e:
                self.db.rollback()
                raise DatabaseError(f"Failed to import visual data: {str(e)}")
        
        return visual_model