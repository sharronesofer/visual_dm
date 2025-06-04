"""
Combat Action Domain Model

This module defines the CombatAction domain model according to
the Development Bible standards. Pure business logic with no infrastructure concerns.
"""

from typing import List, Dict, Any, Optional, Set
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    """Types of actions that can be taken in combat."""
    STANDARD = "standard"    # Standard action (attack, cast spell, etc.)
    BONUS = "bonus"         # Bonus action (off-hand attack, etc.)
    REACTION = "reaction"   # Reaction (opportunity attack, etc.)
    FREE = "free"          # Free action (speak, draw weapon, etc.)
    MOVEMENT = "movement"   # Movement action
    FULL_ROUND = "full_round"  # Takes the entire turn


class ActionTarget(Enum):
    """Types of targets for actions."""
    SELF = "self"
    SINGLE_ALLY = "single_ally"
    SINGLE_ENEMY = "single_enemy"
    SINGLE_ANY = "single_any"
    MULTIPLE_ALLIES = "multiple_allies"
    MULTIPLE_ENEMIES = "multiple_enemies"
    ALL_ALLIES = "all_allies"
    ALL_ENEMIES = "all_enemies"
    AREA = "area"
    NO_TARGET = "no_target"


class ActionCategory(Enum):
    """Categories of actions for organization."""
    ATTACK = "attack"
    SPELL = "spell"
    ABILITY = "ability"
    ITEM = "item"
    MOVEMENT = "movement"
    DEFENSE = "defense"
    UTILITY = "utility"
    SOCIAL = "social"


@dataclass
class ActionResult:
    """Result of executing a combat action."""
    success: bool
    message: str
    damage_dealt: int = 0
    healing_applied: int = 0
    targets_affected: List[UUID] = field(default_factory=list)
    status_effects_applied: List[str] = field(default_factory=list)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionDefinition:
    """Definition of what an action can do (template/blueprint)."""
    
    # Required fields (no defaults)
    id: str  # Unique identifier for this action type
    name: str
    description: str
    action_type: ActionType
    target_type: ActionTarget
    category: ActionCategory
    
    # Optional fields (with defaults)
    required_weapon_types: Set[str] = field(default_factory=set)
    required_class_features: Set[str] = field(default_factory=set)
    required_spells: Set[str] = field(default_factory=set)
    minimum_level: int = 1
    range_feet: Optional[int] = None
    area_radius: Optional[int] = None
    requires_line_of_sight: bool = True
    base_damage: int = 0
    damage_type: Optional[str] = None
    damage_modifier: Optional[str] = None  # "strength", "dexterity", etc.
    applies_status_effects: List[str] = field(default_factory=list)
    status_effect_save_dc: Optional[int] = None
    spell_slot_level: Optional[int] = None
    resource_cost: Dict[str, int] = field(default_factory=dict)
    cooldown_rounds: int = 0
    max_uses_per_encounter: Optional[int] = None
    max_uses_per_day: Optional[int] = None
    tags: Set[str] = field(default_factory=set)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class CombatAction:
    """
    Domain model representing a specific action taken in combat.
    
    This is an instance of an action that was actually performed,
    as opposed to ActionDefinition which is the template.
    """
    
    # Required fields (no defaults)
    action_id: str  # Reference to ActionDefinition
    action_name: str
    actor_id: UUID  # Who performed the action
    actor_name: str
    action_type: ActionType
    category: ActionCategory
    
    # Optional fields (with defaults)
    id: UUID = field(default_factory=uuid4)
    encounter_id: Optional[UUID] = None
    round_number: int = 1
    turn_number: int = 0
    target_ids: List[UUID] = field(default_factory=list)
    target_name: Optional[str] = None  # Primary target name for logging
    success: bool = False
    hit_roll: Optional[int] = None
    damage_rolls: List[int] = field(default_factory=list)
    total_damage: int = 0
    damage_type: Optional[str] = None
    status_effects_applied: List[str] = field(default_factory=list)
    healing_applied: int = 0
    description: str = ""
    execution_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def add_target(self, target_id: UUID, target_name: Optional[str] = None) -> None:
        """Add a target to this action."""
        if target_id not in self.target_ids:
            self.target_ids.append(target_id)
            if target_name and not self.target_name:
                self.target_name = target_name
    
    def remove_target(self, target_id: UUID) -> None:
        """Remove a target from this action."""
        if target_id in self.target_ids:
            self.target_ids.remove(target_id)
    
    def set_result(self, result: ActionResult) -> None:
        """Set the result of executing this action."""
        self.success = result.success
        self.total_damage = result.damage_dealt
        self.healing_applied = result.healing_applied
        self.target_ids = result.targets_affected
        self.status_effects_applied = result.status_effects_applied
        self.execution_data.update(result.additional_data)
    
    def add_damage_roll(self, roll: int) -> None:
        """Add a damage roll to the action."""
        self.damage_rolls.append(roll)
        self.total_damage = sum(self.damage_rolls)
    
    def get_average_damage(self) -> float:
        """Calculate average damage from all rolls."""
        if not self.damage_rolls:
            return 0.0
        return sum(self.damage_rolls) / len(self.damage_rolls)
    
    def was_critical_hit(self) -> bool:
        """Check if this was a critical hit based on execution data."""
        return self.execution_data.get("critical_hit", False)
    
    def was_critical_miss(self) -> bool:
        """Check if this was a critical miss based on execution data."""
        return self.execution_data.get("critical_miss", False)
    
    def get_action_summary(self) -> Dict[str, Any]:
        """Get a summary of the action for logging/display."""
        return {
            "id": str(self.id),
            "action": self.action_name,
            "actor": self.actor_name,
            "target": self.target_name or f"{len(self.target_ids)} targets",
            "type": self.action_type.value,
            "category": self.category.value,
            "success": self.success,
            "damage": self.total_damage,
            "healing": self.healing_applied,
            "effects": self.status_effects_applied,
            "round": self.round_number,
            "turn": self.turn_number,
            "timestamp": self.timestamp.isoformat()
        }
    
    def get_detailed_result(self) -> Dict[str, Any]:
        """Get detailed results including all rolls and calculations."""
        return {
            **self.get_action_summary(),
            "hit_roll": self.hit_roll,
            "damage_rolls": self.damage_rolls,
            "damage_type": self.damage_type,
            "average_damage": self.get_average_damage(),
            "critical_hit": self.was_critical_hit(),
            "critical_miss": self.was_critical_miss(),
            "execution_data": self.execution_data,
            "description": self.description
        }
    
    @classmethod
    def create_from_definition(
        cls,
        definition: ActionDefinition,
        actor_id: UUID,
        actor_name: str,
        **kwargs
    ) -> 'CombatAction':
        """Create a CombatAction from an ActionDefinition."""
        return cls(
            action_id=definition.id,
            action_name=definition.name,
            actor_id=actor_id,
            actor_name=actor_name,
            action_type=definition.action_type,
            category=definition.category,
            damage_type=definition.damage_type,
            description=definition.description,
            **kwargs
        )


@dataclass
class CombatantActionState:
    """
    Tracks the action state for a specific combatant.
    
    This manages what actions a combatant has available and used.
    """
    
    # Required field
    combatant_id: UUID
    
    # Optional fields with defaults
    used_standard_action: bool = False
    used_bonus_action: bool = False
    used_reaction: bool = False
    used_movement: float = 0.0
    max_movement: float = 30.0
    action_cooldowns: Dict[str, int] = field(default_factory=dict)
    resources: Dict[str, int] = field(default_factory=dict)
    encounter_uses: Dict[str, int] = field(default_factory=dict)
    daily_uses: Dict[str, int] = field(default_factory=dict)
    actions_taken: List[UUID] = field(default_factory=list)
    
    def reset_turn(self) -> None:
        """Reset action usage for a new turn."""
        self.used_standard_action = False
        self.used_bonus_action = False
        self.used_reaction = False
        self.used_movement = 0.0
        
        # Tick down cooldowns
        for action_id in list(self.action_cooldowns.keys()):
            self.action_cooldowns[action_id] -= 1
            if self.action_cooldowns[action_id] <= 0:
                del self.action_cooldowns[action_id]
    
    def reset_encounter(self) -> None:
        """Reset for a new encounter."""
        self.reset_turn()
        self.encounter_uses.clear()
        self.actions_taken.clear()
        self.action_cooldowns.clear()
    
    def can_use_action(self, definition: ActionDefinition) -> tuple[bool, str]:
        """
        Check if the combatant can use a specific action.
        
        Returns:
            Tuple of (can_use, reason_if_not)
        """
        # Check action economy
        if definition.action_type == ActionType.STANDARD and self.used_standard_action:
            return False, "Standard action already used this turn"
        if definition.action_type == ActionType.BONUS and self.used_bonus_action:
            return False, "Bonus action already used this turn"
        if definition.action_type == ActionType.REACTION and self.used_reaction:
            return False, "Reaction already used this turn"
        
        # Check cooldowns
        if definition.id in self.action_cooldowns:
            rounds_left = self.action_cooldowns[definition.id]
            return False, f"Action on cooldown for {rounds_left} more round(s)"
        
        # Check encounter limits
        if definition.max_uses_per_encounter is not None:
            uses_left = self.encounter_uses.get(definition.id, definition.max_uses_per_encounter)
            if uses_left <= 0:
                return False, "No uses remaining this encounter"
        
        # Check daily limits
        if definition.max_uses_per_day is not None:
            uses_left = self.daily_uses.get(definition.id, definition.max_uses_per_day)
            if uses_left <= 0:
                return False, "No uses remaining today"
        
        # Check resource costs
        for resource, cost in definition.resource_cost.items():
            available = self.resources.get(resource, 0)
            if available < cost:
                return False, f"Insufficient {resource} ({available}/{cost})"
        
        return True, ""
    
    def use_action(self, definition: ActionDefinition, action_id: UUID) -> bool:
        """
        Mark an action as used and consume resources.
        
        Returns:
            True if action was successfully marked as used
        """
        can_use, reason = self.can_use_action(definition)
        if not can_use:
            return False
        
        # Mark action economy as used
        if definition.action_type == ActionType.STANDARD:
            self.used_standard_action = True
        elif definition.action_type == ActionType.BONUS:
            self.used_bonus_action = True
        elif definition.action_type == ActionType.REACTION:
            self.used_reaction = True
        
        # Apply cooldown
        if definition.cooldown_rounds > 0:
            self.action_cooldowns[definition.id] = definition.cooldown_rounds
        
        # Consume encounter uses
        if definition.max_uses_per_encounter is not None:
            current_uses = self.encounter_uses.get(definition.id, definition.max_uses_per_encounter)
            self.encounter_uses[definition.id] = current_uses - 1
        
        # Consume daily uses
        if definition.max_uses_per_day is not None:
            current_uses = self.daily_uses.get(definition.id, definition.max_uses_per_day)
            self.daily_uses[definition.id] = current_uses - 1
        
        # Consume resources
        for resource, cost in definition.resource_cost.items():
            current = self.resources.get(resource, 0)
            self.resources[resource] = max(0, current - cost)
        
        # Track action
        self.actions_taken.append(action_id)
        
        return True
    
    def get_available_actions(self, action_definitions: List[ActionDefinition]) -> List[ActionDefinition]:
        """Get list of actions this combatant can currently use."""
        available = []
        for definition in action_definitions:
            can_use, _ = self.can_use_action(definition)
            if can_use:
                available.append(definition)
        return available
    
    def get_action_status(self) -> Dict[str, Any]:
        """Get current action state summary."""
        return {
            "standard_action_used": self.used_standard_action,
            "bonus_action_used": self.used_bonus_action,
            "reaction_used": self.used_reaction,
            "movement_used": self.used_movement,
            "movement_remaining": self.max_movement - self.used_movement,
            "cooldowns": self.action_cooldowns.copy(),
            "resources": self.resources.copy(),
            "encounter_uses": self.encounter_uses.copy(),
            "daily_uses": self.daily_uses.copy(),
            "actions_taken_count": len(self.actions_taken)
        }


__all__ = [
    "CombatAction", 
    "ActionDefinition", 
    "ActionResult", 
    "CombatantActionState",
    "ActionType", 
    "ActionTarget", 
    "ActionCategory"
] 