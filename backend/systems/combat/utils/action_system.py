"""
ActionSystem module for the Visual DM combat system.

This module implements action management, validation, and execution for combat.
It defines the action economy and enforces rules for when actions can be taken.

Following the design principles from the Development Bible, this implementation:
1. Provides an action economy (standard, bonus, reaction, movement)
2. Defines standard action types and validates their usage
3. Tracks action usage throughout combat turns
4. Enforces correct sequencing and limitations

This is pure business logic - no I/O or database operations.
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Callable, Type, TypeVar, Set, Union
from dataclasses import dataclass, field

from backend.infrastructure.config_loaders.combat_config_loader import combat_config

# Set up logging
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions that can be taken in combat."""
    STANDARD = auto()  # Main action
    BONUS = auto()  # Secondary/quick action
    REACTION = auto()  # Action in response to a trigger
    MOVEMENT = auto()  # Movement action
    FREE = auto()  # Free action (doesn't consume action economy)

class ActionTarget(Enum):
    """Target types for actions."""
    SELF = auto()  # Target self
    SINGLE = auto()  # Target a single entity
    MULTI = auto()  # Target multiple entities
    AREA = auto()  # Target an area
    GLOBAL = auto()  # Target all entities (global effect)

class ActionResult:
    """Represents the result of an executed action."""
    
    def __init__(self, success: bool = True, message: str = "",
                 effects: List[Any] = None, damage: float = 0.0,
                 damage_type: str = ""):
        """
        Initialize an action result.
        
        Args:
            success: Whether the action succeeded
            message: Description of the action result
            effects: List of effects applied
            damage: Amount of damage dealt
            damage_type: Type of damage dealt
        """
        self.success = success
        self.message = message
        self.effects = effects or []
        self.damage = damage
        self.damage_type = damage_type
    
    def __bool__(self) -> bool:
        """Boolean representation is success value."""
        return self.success

@dataclass
class ActionDefinition:
    """Defines a combat action."""
    id: str
    name: str
    description: str
    action_type: ActionType
    target_type: ActionTarget
    
    # Function to validate if this action can be used
    validate_func: Optional[Callable[[Any, Any], bool]] = None
    
    # Function to execute the action and return a result
    execute_func: Optional[Callable[[Any, Any], ActionResult]] = None
    
    # Range in units
    min_range: float = 0.0
    max_range: float = 1.5  # Default melee range
    
    # Cooldown in rounds
    cooldown: int = 0
    current_cooldown: int = 0
    
    # Resource cost
    resource_cost: Dict[str, int] = field(default_factory=dict)
    
    # Tags for categorizing (e.g., "melee", "spell", "healing")
    tags: List[str] = field(default_factory=list)
    
    # Requirements to use this action
    requirements: List[str] = field(default_factory=list)
    
    def can_use(self, source, target: Any = None) -> bool:
        """
        Check if this action can be used.
        
        Args:
            source: The entity using the action
            target: The target of the action
            
        Returns:
            True if the action can be used, False otherwise
        """
        # Check cooldown
        if self.current_cooldown > 0:
            return False
            
        # Check if validation function exists and use it
        if self.validate_func:
            return self.validate_func(source, target)
            
        return True
    
    def execute(self, source, target: Any = None) -> ActionResult:
        """
        Execute this action.
        
        Args:
            source: The entity using the action
            target: The target of the action
            
        Returns:
            The result of the action
        """
        # Set cooldown
        self.current_cooldown = self.cooldown
        
        # Execute the action using the provided function
        if self.execute_func:
            return self.execute_func(source, target)
            
        # Default implementation if no execute function provided
        return ActionResult(
            success=True,
            message=f"{source} used {self.name} on {target}"
        )
    
    def update_cooldown(self) -> None:
        """Update (reduce) the current cooldown if active."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class CombatantActionState:
    """
    Tracks action usage for a combatant during a turn.
    
    Manages which actions have been used and enforces the action economy.
    """
    
    def __init__(self):
        """Initialize a fresh action state for a turn."""
        self.used_standard_action = False
        self.used_bonus_action = False
        self.used_reaction = False
        self.remaining_movement = 30.0  # Default 30 units of movement
        self.used_actions: Set[str] = set()  # IDs of specific actions used
        
        # Track cooldowns for actions
        self.action_cooldowns: Dict[str, int] = {}
    
    def reset(self, movement: float = 30.0) -> None:
        """
        Reset the action state for a turn.
        
        Args:
            movement: Amount of movement available for the turn
        """
        self.used_standard_action = False
        self.used_bonus_action = False
        self.used_reaction = False
        self.remaining_movement = movement
        self.used_actions.clear()
        
        # Reduce all cooldowns by 1
        for action_id in list(self.action_cooldowns.keys()):
            self.action_cooldowns[action_id] -= 1
            if self.action_cooldowns[action_id] <= 0:
                del self.action_cooldowns[action_id]
    
    def can_use_action(self, action) -> bool:
        """
        Check if a specific action can be used based on action economy.
        
        Args:
            action: The action to check
            
        Returns:
            True if the action can be used, False otherwise
        """
        # Check cooldown
        if action.id in self.action_cooldowns:
            return False
            
        # Check action type
        if action.action_type == ActionType.STANDARD:
            return not self.used_standard_action
        elif action.action_type == ActionType.BONUS:
            return not self.used_bonus_action
        elif action.action_type == ActionType.REACTION:
            return not self.used_reaction
        elif action.action_type == ActionType.MOVEMENT:
            return self.remaining_movement > 0
        elif action.action_type == ActionType.FREE:
            return True
            
        return False
    
    def use_action(self, action) -> None:
        """
        Mark an action as used.
        
        Args:
            action: The action that was used
        """
        # Record specific action use
        self.used_actions.add(action.id)
        
        # Apply cooldown if any
        if action.cooldown > 0:
            self.action_cooldowns[action.id] = action.cooldown
            
        # Update action economy
        if action.action_type == ActionType.STANDARD:
            self.used_standard_action = True
        elif action.action_type == ActionType.BONUS:
            self.used_bonus_action = True
        elif action.action_type == ActionType.REACTION:
            self.used_reaction = True
    
    def use_movement(self, distance) -> float:
        """
        Use movement and return how much was actually used.
        
        Args:
            distance: Distance to move
            
        Returns:
            Actual distance moved
        """
        actual_distance = min(distance, self.remaining_movement)
        self.remaining_movement -= actual_distance
        return actual_distance

class ActionSystem:
    """
    Manages combat actions and their usage.
    
    Handles registration, validation, and execution of actions.
    Tracks action economy for all combatants.
    """
    
    def __init__(self):
        """Initialize with empty registries."""
        # Registry of action definitions by ID
        self._actions: Dict[str, ActionDefinition] = {}
        
        # Combatant action states by combatant ID
        self._combatant_states: Dict[str, CombatantActionState] = {}
        
        # Action categories for organization and retrieval
        self._action_categories: Dict[str, List[str]] = {}
        
        # Registry of global reaction triggers
        self._reaction_triggers: Dict[str, List[Callable]] = {}
    
    def register_action(self, action, categories: List[str] = None) -> None:
        """
        Register an action definition.
        
        Args:
            action: The action to register
            categories: Optional list of categories to place this action in
        """
        if action.id in self._actions:
            logger.warning(f"Action {action.id} already registered, overwriting")
            
        self._actions[action.id] = action
        
        # Register action in categories
        if categories:
            for category in categories:
                if category not in self._action_categories:
                    self._action_categories[category] = []
                self._action_categories[category].append(action.id)
    
    def get_action(self, action_id) -> Optional[ActionDefinition]:
        """
        Get an action by ID.
        
        Args:
            action_id: The ID of the action
            
        Returns:
            ActionDefinition or None if not found
        """
        return self._actions.get(action_id)
    
    def get_actions_by_category(self, category) -> List[ActionDefinition]:
        """
        Get all actions in a category.
        
        Args:
            category: The category to get actions for
            
        Returns:
            List of ActionDefinition objects
        """
        if category not in self._action_categories:
            return []
            
        return [self._actions[action_id] for action_id in self._action_categories[category]
                if action_id in self._actions]
    
    def get_actions_for_combatant(self, combatant) -> List[ActionDefinition]:
        """
        Get all available actions for a specific combatant based on their abilities,
        equipment, status effects, and other factors.
        
        Args:
            combatant: The combatant to get actions for
            
        Returns:
            List of ActionDefinition objects
        """
        available_actions = []
        
        # Get combatant data
        combatant_data = self._extract_combatant_data(combatant)
        
        # Check each registered action
        for action in self._actions.values():
            if self._can_combatant_use_action(combatant_data, action):
                available_actions.append(action)
        
        return available_actions
    
    def _extract_combatant_data(self, combatant) -> Dict[str, Any]:
        """
        Extract relevant data from a combatant for action validation.
        
        Args:
            combatant: The combatant object or dictionary
            
        Returns:
            Dictionary with combatant data
        """
        data = {}
        
        # Handle both ORM objects and dictionaries
        if hasattr(combatant, '__dict__'):
            # ORM object - extract attributes
            data["level"] = getattr(combatant, 'level', 1)
            data["equipment"] = getattr(combatant, 'equipment', [])
            data["abilities"] = getattr(combatant, 'abilities', [])
            data["feats"] = getattr(combatant, 'feats', [])  # Legacy field - Visual DM uses 'abilities'
            data["status_effects"] = getattr(combatant, 'status_effects', [])
            data["hp"] = getattr(combatant, 'hp', 100)
            data["resources"] = getattr(combatant, 'resources', {})
            
            # Get stats/attributes
            if hasattr(combatant, 'stats'):
                stats = combatant.stats
                if isinstance(stats, dict):
                    data.update(stats)
                    
        else:
            # Dictionary - direct access
            data["level"] = combatant.get('level', 1)
            data["equipment"] = combatant.get('equipment', [])
            data["abilities"] = combatant.get('abilities', [])
            data["feats"] = combatant.get('feats', [])  # Legacy field - Visual DM uses 'abilities'
            data["status_effects"] = combatant.get('status_effects', [])
            data["hp"] = combatant.get('hp', 100)
            data["resources"] = combatant.get('resources', {})
            
            # Copy other fields
            for key in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
                if key in combatant:
                    data[key] = combatant[key]
        
        return data
    
    def _can_combatant_use_action(self, combatant_data: Dict[str, Any], action: ActionDefinition) -> bool:
        """
        Check if a combatant can use a specific action based on their capabilities.
        
        Args:
            combatant_data: Extracted combatant data
            action: The action to check
            
        Returns:
            True if the combatant can use the action, False otherwise
        """
        # Check basic requirements
        for requirement in action.requirements:
            if not self._check_requirement(combatant_data, requirement):
                return False
        
        # Check status effects that might prevent action
        for effect in combatant_data["status_effects"]:
            effect_name = effect.get("name", "") if isinstance(effect, dict) else str(effect)
            if self._status_effect_blocks_action(effect_name, action):
                return False
        
        # Check resource costs
        for resource, cost in action.resource_cost.items():
            if not self._has_sufficient_resource(combatant_data, resource, cost):
                return False
        
        # Check action-specific tags
        if action.tags:
            if not self._meets_tag_requirements(combatant_data, action.tags):
                return False
        
        return True
    
    def _check_requirement(self, combatant_data: Dict[str, Any], requirement: str) -> bool:
        """
        Check if a combatant meets a specific requirement.
        
        Args:
            combatant_data: Combatant data
            requirement: Requirement string to check
            
        Returns:
            True if requirement is met
        """
        # Parse requirement string
        req_lower = requirement.lower()
        
        # Level requirements
        if req_lower.startswith("level_"):
            required_level = int(req_lower.split("_")[1])
            return combatant_data["level"] >= required_level
        
        # Equipment requirements
        if req_lower.startswith("weapon_") or req_lower == "weapon_equipped":
            equipment = combatant_data["equipment"]
            if req_lower == "weapon_equipped":
                return any("weapon" in str(item).lower() for item in equipment)
            else:
                weapon_type = req_lower.split("_", 1)[1]
                return any(weapon_type in str(item).lower() for item in equipment)
        
        # Shield requirements
        if req_lower == "shield_equipped":
            equipment = combatant_data["equipment"]
            return any("shield" in str(item).lower() for item in equipment)
        
        # Spell level requirements
        if req_lower.startswith("spell_level_"):
            required_level = int(req_lower.split("_")[2])
            # Check if combatant can cast spells of this level
            caster_level = self._get_caster_level(combatant_data)
            return caster_level >= required_level
        
        # Ability requirements
        if req_lower.startswith("ability_"):
            ability_name = req_lower.split("_", 1)[1]
            abilities = combatant_data["abilities"]
            return any(ability_name in str(ability).lower() for ability in abilities)
        
        # Attribute requirements (e.g., "str_13" means STR >= 13)
        for attr in ["str", "dex", "con", "int", "wis", "cha"]:
            if req_lower.startswith(f"{attr}_"):
                try:
                    required_value = int(req_lower.split("_")[1])
                    actual_value = combatant_data["attributes"].get(attr.upper(), 10)
                    return actual_value >= required_value
                except (ValueError, IndexError):
                    continue
        
        # Tag requirements
        if req_lower.startswith("tag_"):
            required_tag = req_lower.split("_", 1)[1]
            return required_tag in [tag.lower() for tag in combatant_data["tags"]]
        
        # Default: unknown requirement is not met
        logger.warning(f"Unknown requirement: {requirement}")
        return False
    
    def _status_effect_blocks_action(self, effect_name: str, action: ActionDefinition) -> bool:
        """
        Check if a status effect blocks an action.
        
        Args:
            effect_name: Name of the status effect
            action: The action to check
            
        Returns:
            True if the effect blocks the action
        """
        effect_lower = effect_name.lower()
        
        # Stunned blocks all actions except reactions
        if effect_lower in ["stunned", "unconscious", "paralyzed"]:
            return action.action_type != ActionType.REACTION
        
        # Silenced blocks spells
        if effect_lower in ["silenced", "silence"] and "spell" in action.tags:
            return True
        
        # Grappled blocks movement
        if effect_lower == "grappled" and action.action_type == ActionType.MOVEMENT:
            return True
        
        # Blinded might affect certain actions
        if effect_lower == "blinded" and "ranged" in action.tags:
            return True
        
        return False
    
    def _has_sufficient_resource(self, combatant_data: Dict[str, Any], resource: str, cost: int) -> bool:
        """
        Check if combatant has sufficient resources for an action.
        
        Args:
            combatant_data: Combatant data
            resource: Resource type (e.g., "mp", "stamina", "spell_slots")
            cost: Required amount
            
        Returns:
            True if sufficient resources available
        """
        if resource == "mp" or resource == "mana":
            current_mp = combatant_data["attributes"].get("mp", 0)
            return current_mp >= cost
        
        if resource == "stamina":
            current_stamina = combatant_data["attributes"].get("stamina", 100)
            return current_stamina >= cost
        
        if resource.startswith("spell_slot_"):
            # For spell slot requirements
            level = resource.split("_")[-1]
            available_slots = combatant_data["attributes"].get(f"spell_slots_{level}", 0)
            return available_slots >= cost
        
        # Default: assume resource is available
        return True
    
    def _meets_tag_requirements(self, combatant_data: Dict[str, Any], action_tags: List[str]) -> bool:
        """
        Check if combatant meets tag-based requirements for an action.
        
        Args:
            combatant_data: Combatant data
            action_tags: List of action tags
            
        Returns:
            True if requirements are met
        """
        # If action requires spellcasting
        if "spell" in action_tags:
            caster_level = self._get_caster_level(combatant_data)
            if caster_level <= 0:
                return False
        
        # If action requires specific weapon type
        weapon_tags = [tag for tag in action_tags if tag.endswith("_weapon")]
        if weapon_tags:
            equipment = combatant_data["equipment"]
            for weapon_tag in weapon_tags:
                weapon_type = weapon_tag.replace("_weapon", "")
                if not any(weapon_type in str(item).lower() for item in equipment):
                    return False
        
        return True
    
    def _get_caster_level(self, combatant_data: Dict[str, Any]) -> int:
        """
        Get the effective caster level for a combatant based on their abilities.
        Note: Uses 'feats' field for backward compatibility, but Visual DM uses 'abilities' terminology.
        
        Args:
            combatant_data: Combatant data
            
        Returns:
            Caster level (0 if not a caster)
        """
        level = combatant_data["level"]
        abilities = combatant_data.get("feats", [])  # Legacy field name for backward compatibility
        
        # Check for spellcasting abilities to determine caster level
        if "arcane_mastery" in abilities or "divine_mastery" in abilities:
            # Full caster equivalent
            return level
        elif "arcane_initiate" in abilities or "divine_magic" in abilities:
            # Half caster equivalent  
            return max(0, level // 2)
        elif "minor_magic" in abilities or "cantrip_adept" in abilities:
            # Third caster equivalent
            return max(0, level // 3)
        
        # Non-casters
        return 0
    
    def reset_combatant_actions(self, combatant, movement: float = 30.0) -> None:
        """
        Reset a combatant's action state for a turn.
        
        Args:
            combatant: The combatant to reset
            movement: Amount of movement available for the turn
        """
        combatant_id = self._get_combatant_id(combatant)
        
        if combatant_id not in self._combatant_states:
            self._combatant_states[combatant_id] = CombatantActionState()
        
        self._combatant_states[combatant_id].reset(movement)
    
    def _get_combatant_id(self, combatant) -> str:
        """
        Get a unique identifier for a combatant.
        
        Args:
            combatant: The combatant to get an ID for
            
        Returns:
            A unique identifier string
        """
        if hasattr(combatant, 'character_id'):
            return combatant.character_id
        if hasattr(combatant, 'id'):
            return combatant.id
        return str(combatant)
    
    def _get_combatant_state(self, combatant) -> CombatantActionState:
        """
        Get the action state for a combatant, creating if needed.
        
        Args:
            combatant: The combatant to get state for
            
        Returns:
            CombatantActionState for the combatant
        """
        combatant_id = self._get_combatant_id(combatant)
        
        if combatant_id not in self._combatant_states:
            self._combatant_states[combatant_id] = CombatantActionState()
            
        return self._combatant_states[combatant_id]
    
    def can_use_action(self, combatant, action: Union[ActionDefinition, str],
                      target: Any = None) -> bool:
        """
        Check if a combatant can use a specific action.
        
        Args:
            combatant: The combatant trying to use the action
            action: The action or action ID
            target: Optional target of the action
            
        Returns:
            True if the action can be used, False otherwise
        """
        # Get action definition if an ID was provided
        action_def = action
        if isinstance(action, str):
            action_def = self.get_action(action)
        if not action_def:
            logger.warning(f"Action {action} not found in registry")
            return False
        
        # Get combatant state
        combatant_state = self._get_combatant_state(combatant)
        
        # Check action economy
        if not combatant_state.can_use_action(action_def):
            return False
            
        # Check action-specific validation
        if not action_def.can_use(combatant, target):
            return False
            
        return True
    
    def use_action(self, combatant, action: Union[ActionDefinition, str],
                  target: Any = None) -> ActionResult:
        """
        Use an action.
        
        Args:
            combatant: The combatant using the action
            action: The action or action ID
            target: The target of the action
            
        Returns:
            Result of the action
            
        Raises:
            ValueError: If the action cannot be used
        """
        # Get action definition if an ID was provided
        action_def = action
        if isinstance(action, str):
            action_def = self.get_action(action)
        if not action_def:
            raise ValueError(f"Action {action} not found in registry")
        
        # Validate the action can be used
        if not self.can_use_action(combatant, action_def, target):
            return ActionResult(
                success=False,
                message=f"{combatant} cannot use {action_def.name} at this time"
            )
        
        # Execute the action
        result = action_def.execute(combatant, target)
        
        # If successful, record the action usage
        if result.success:
            combatant_state = self._get_combatant_state(combatant)
            combatant_state.use_action(action_def)
            
        return result
    
    def use_movement(self, combatant, distance) -> float:
        """
        Use movement for a combatant.
        
        Args:
            combatant: The combatant moving
            distance: Distance to move
            
        Returns:
            Actual distance moved
        """
        combatant_state = self._get_combatant_state(combatant)
        return combatant_state.use_movement(distance)
    
    def register_reaction_trigger(self, trigger_type, callback) -> None:
        """
        Register a callback for a reaction trigger.
        
        Args:
            trigger_type: The type of trigger (e.g., "damage", "movement")
            callback: Function to call when trigger occurs
        """
        if trigger_type not in self._reaction_triggers:
            self._reaction_triggers[trigger_type] = []
            
        self._reaction_triggers[trigger_type].append(callback)
    
    def trigger_reaction(self, trigger_type, source, target: Any = None,
                       data: Any = None) -> List[ActionResult]:
        """
        Trigger reaction callbacks for a specific event.
        
        Args:
            trigger_type: The type of trigger
            source: The source of the trigger
            target: Optional target of the trigger
            data: Optional additional data
            
        Returns:
            List of ActionResults from reactions
        """
        if trigger_type not in self._reaction_triggers:
            return []
            
        results = []
        
        for callback in self._reaction_triggers[trigger_type]:
            try:
                result = callback(source, target, data)
                if result:
                    results.append(result)
            except Exception as e:
                logger.error(f"Error in reaction trigger callback: {e}")
                
        return results
    
    def get_available_reactions(self, combatant, trigger_type,
                               source: Any = None) -> List[ActionDefinition]:
        """
        Get available reactions for a combatant given a trigger.
        
        Args:
            combatant: The combatant who might react
            trigger_type: The type of trigger
            source: Optional source of the trigger
            
        Returns:
            List of available reaction actions
        """
        # Get all actions for the combatant
        all_actions = self.get_actions_for_combatant(combatant)
        
        # Filter to reactions that are available and match the trigger
        available_reactions = []
        
        for action in all_actions:
            if (action.action_type == ActionType.REACTION and
                trigger_type in action.tags and
                self.can_use_action(combatant, action)):
                available_reactions.append(action)
                
        return available_reactions
    
    def get_remaining_actions(self, combatant) -> Dict[str, bool]:
        """
        Get information about what actions a combatant has left.
        
        Args:
            combatant: The combatant to check
            
        Returns:
            Dictionary describing available actions
        """
        state = self._get_combatant_state(combatant)
        
        return {
            "standard": not state.used_standard_action,
            "bonus": not state.used_bonus_action,
            "reaction": not state.used_reaction,
            "movement": state.remaining_movement
        }

# Global instance for use throughout the combat system
action_system = ActionSystem()

# Define some basic actions
def register_basic_actions():
    """Register a set of default basic actions."""
    
    # Attack action
    attack_action = ActionDefinition(
        id="attack",
        name="Attack",
        description="Make a basic attack against a target.",
        action_type=ActionType.STANDARD,
        target_type=ActionTarget.SINGLE,
        max_range=1.5, # Melee range
        tags=["attack", "melee"]
    )
    
    # Ranged attack action
    ranged_attack_action = ActionDefinition(
        id="ranged_attack",
        name="Ranged Attack",
        description="Make a ranged attack against a target.",
        action_type=ActionType.STANDARD,
        target_type=ActionTarget.SINGLE,
        min_range=1.5,
        max_range=60.0, # Medium range
        tags=["attack", "ranged"]
    )
    
    # Dodge action
    dodge_action = ActionDefinition(
        id="dodge",
        name="Dodge",
        description="Focus on dodging attacks, gaining advantage on Dexterity saves and imposing disadvantage on attacks against you.",
        action_type=ActionType.STANDARD,
        target_type=ActionTarget.SELF,
        tags=["defensive"]
    )
    
    # Dash action
    dash_action = ActionDefinition(
        id="dash",
        name="Dash",
        description="Double your movement speed for this turn.",
        action_type=ActionType.STANDARD,
        target_type=ActionTarget.SELF,
        tags=["movement"]
    )
    
    # Disengage action
    disengage_action = ActionDefinition(
        id="disengage",
        name="Disengage",
        description="Your movement doesn't provoke opportunity attacks for the rest of the turn.",
        action_type=ActionType.STANDARD,
        target_type=ActionTarget.SELF,
        tags=["movement", "defensive"]
    )
    
    # Help action
    help_action = ActionDefinition(
        id="help",
        name="Help",
        description="Give advantage to an ally's attack or ability check.",
        action_type=ActionType.STANDARD,
        target_type=ActionTarget.SINGLE,
        max_range=5.0,
        tags=["utility", "support"]
    )
    
    # Hide action
    hide_action = ActionDefinition(
        id="hide",
        name="Hide",
        description="Attempt to hide from enemies.",
        action_type=ActionType.STANDARD,
        target_type=ActionTarget.SELF,
        tags=["utility", "stealth"]
    )
    
    # Opportunity attack reaction
    opportunity_attack = ActionDefinition(
        id="opportunity_attack",
        name="Opportunity Attack",
        description="Make an attack when an enemy leaves your reach.",
        action_type=ActionType.REACTION,
        target_type=ActionTarget.SINGLE,
        max_range=1.5,
        tags=["attack", "melee", "movement_trigger"]
    )
    
    # Register all actions
    action_system.register_action(attack_action, ["basic", "offensive"])
    action_system.register_action(ranged_attack_action, ["basic", "offensive"])
    action_system.register_action(dodge_action, ["basic", "defensive"])
    action_system.register_action(dash_action, ["basic", "movement"])
    action_system.register_action(disengage_action, ["basic", "movement", "defensive"])
    action_system.register_action(help_action, ["basic", "support"])
    action_system.register_action(hide_action, ["basic", "utility"])
    action_system.register_action(opportunity_attack, ["reaction"])

# Register default actions when module is imported
register_basic_actions()