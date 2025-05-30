"""
ActionSystem module for the Visual DM combat system.

This module implements action management, validation, and execution for combat.
It defines the action economy and enforces rules for when actions can be taken.

Following the design principles from the Development Bible, this implementation:
1. Provides an action economy (standard, bonus, reaction, movement)
2. Defines standard action types and validates their usage
3. Tracks action usage throughout combat turns
4. Enforces correct sequencing and limitations
"""

import logging
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Callable, Type, TypeVar, Set, Union
from dataclasses import dataclass, field

# Set up logging
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions that can be taken in combat."""
    STANDARD = auto()  # Main action
    BONUS = auto()     # Secondary/quick action
    REACTION = auto()  # Action in response to a trigger
    MOVEMENT = auto()  # Movement action
    FREE = auto()      # Free action (doesn't consume action economy)


class ActionTarget(Enum):
    """Target types for actions."""
    SELF = auto()       # Target self
    SINGLE = auto()     # Target a single entity
    MULTI = auto()      # Target multiple entities 
    AREA = auto()       # Target an area
    GLOBAL = auto()     # Target all entities (global effect)


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
    
    def can_use(self, source: Any, target: Any = None) -> bool:
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
    
    def execute(self, source: Any, target: Any = None) -> ActionResult:
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
        Reset the action state for a new turn.
        
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
    
    def can_use_action(self, action: ActionDefinition) -> bool:
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
    
    def use_action(self, action: ActionDefinition) -> None:
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
    
    def use_movement(self, distance: float) -> float:
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
    
    def register_action(self, action: ActionDefinition, categories: List[str] = None) -> None:
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
    
    def get_action(self, action_id: str) -> Optional[ActionDefinition]:
        """
        Get an action by ID.
        
        Args:
            action_id: The ID of the action
            
        Returns:
            ActionDefinition or None if not found
        """
        return self._actions.get(action_id)
    
    def get_actions_by_category(self, category: str) -> List[ActionDefinition]:
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
    
    def get_actions_for_combatant(self, combatant: Any) -> List[ActionDefinition]:
        """
        Get all actions available to a combatant.
        
        Args:
            combatant: The combatant to get actions for
            
        Returns:
            List of ActionDefinition objects
        """
        # This implementation is a placeholder - would normally check
        # combatant abilities, equipment, etc. to determine available actions
        return list(self._actions.values())
    
    def reset_combatant_actions(self, combatant: Any, movement: float = 30.0) -> None:
        """
        Reset a combatant's action state for a new turn.
        
        Args:
            combatant: The combatant to reset
            movement: Amount of movement available for the turn
        """
        combatant_id = self._get_combatant_id(combatant)
        
        if combatant_id not in self._combatant_states:
            self._combatant_states[combatant_id] = CombatantActionState()
        
        self._combatant_states[combatant_id].reset(movement)
    
    def _get_combatant_id(self, combatant: Any) -> str:
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
    
    def _get_combatant_state(self, combatant: Any) -> CombatantActionState:
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
    
    def can_use_action(self, combatant: Any, action: Union[ActionDefinition, str], 
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
    
    def use_action(self, combatant: Any, action: Union[ActionDefinition, str], 
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
    
    def use_movement(self, combatant: Any, distance: float) -> float:
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
    
    def register_reaction_trigger(self, trigger_type: str, callback: Callable) -> None:
        """
        Register a callback for a reaction trigger.
        
        Args:
            trigger_type: The type of trigger (e.g., "damage", "movement")
            callback: Function to call when trigger occurs
        """
        if trigger_type not in self._reaction_triggers:
            self._reaction_triggers[trigger_type] = []
            
        self._reaction_triggers[trigger_type].append(callback)
    
    def trigger_reaction(self, trigger_type: str, source: Any, target: Any = None,
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
    
    def get_available_reactions(self, combatant: Any, trigger_type: str, 
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
    
    def get_remaining_actions(self, combatant: Any) -> Dict[str, bool]:
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
        max_range=1.5,  # Melee range
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
        max_range=60.0,  # Medium range
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