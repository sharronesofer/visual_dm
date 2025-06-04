"""
Combatant Domain Model

This module defines the Combatant domain model according to
the Development Bible standards. Pure business logic with no infrastructure concerns.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field

from .status_effect import StatusEffect


@dataclass
class Combatant:
    """
    Domain model representing a single participant in combat.
    
    Encapsulates all state and business rules for a combatant,
    including stats, status effects, and combat state.
    """
    
    # Identity
    id: UUID = field(default_factory=uuid4)
    character_id: Optional[UUID] = None  # Reference to character system
    combat_encounter_id: Optional[UUID] = None
    
    # Basic Information
    name: str = "Unknown Combatant"
    team: str = "neutral"  # player, hostile, neutral, etc.
    combatant_type: str = "character"  # character, npc, creature, etc.
    
    # Combat Stats
    current_hp: int = 20
    max_hp: int = 20
    temporary_hp: int = 0
    armor_class: int = 10
    initiative: int = 0
    dex_modifier: int = 0
    
    # Combat State
    is_active: bool = True
    is_conscious: bool = True
    position: Optional[Dict[str, float]] = None  # x, y coordinates if using grid
    
    # Status Effects
    status_effects: List[StatusEffect] = field(default_factory=list)
    
    # Action Economy (reset each turn)
    has_used_standard_action: bool = False
    has_used_bonus_action: bool = False
    has_used_reaction: bool = False
    used_free_actions: int = 0
    max_free_actions: int = 2
    remaining_movement: float = 30.0
    
    # Equipment and Abilities
    equipped_weapons: List[str] = field(default_factory=list)
    equipped_armor: Optional[str] = None
    available_spells: List[str] = field(default_factory=list)
    class_features: List[str] = field(default_factory=list)
    damage_reduction: Dict[str, int] = field(default_factory=dict)  # DR by damage type
    
    # Metadata
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def take_damage(self, damage: int) -> Dict[str, Any]:
        """
        Apply damage to the combatant.
        
        Args:
            damage: Amount of damage to apply
            
        Returns:
            Dictionary with damage application results
        """
        if damage < 0:
            raise ValueError("Damage cannot be negative")
        
        # Apply damage to temporary HP first
        temp_damage = 0
        if self.temporary_hp > 0:
            temp_damage = min(damage, self.temporary_hp)
            self.temporary_hp -= temp_damage
            damage -= temp_damage
        
        # Apply remaining damage to regular HP
        actual_damage = min(damage, self.current_hp)
        self.current_hp = max(0, self.current_hp - damage)
        
        # Check if combatant is unconscious
        was_conscious = self.is_conscious
        self.is_conscious = self.current_hp > 0
        
        # Check if combatant is still active
        if self.current_hp <= 0:
            self.is_active = False
        
        return {
            "damage_dealt": temp_damage + actual_damage,
            "temp_damage": temp_damage,
            "regular_damage": actual_damage,
            "overkill": max(0, damage - actual_damage),
            "remaining_hp": self.current_hp,
            "remaining_temp_hp": self.temporary_hp,
            "became_unconscious": was_conscious and not self.is_conscious,
            "is_active": self.is_active
        }
    
    def apply_damage_reduction(self, damage: int, damage_type: str) -> int:
        """Apply damage reduction based on damage type"""
        dr = self.damage_reduction.get(damage_type, 0)
        return max(0, damage - dr)
    
    def heal(self, healing: int) -> Dict[str, Any]:
        """
        Apply healing to the combatant.
        
        Args:
            healing: Amount of healing to apply
            
        Returns:
            Dictionary with healing application results
        """
        if healing < 0:
            raise ValueError("Healing cannot be negative")
        
        old_hp = self.current_hp
        actual_healing = min(healing, self.max_hp - self.current_hp)
        self.current_hp = min(self.max_hp, self.current_hp + healing)
        
        # Check if combatant regained consciousness
        was_conscious = self.is_conscious
        self.is_conscious = self.current_hp > 0
        
        # Reactivate if healed from unconsciousness
        if not was_conscious and self.is_conscious:
            self.is_active = True
        
        return {
            "healing_applied": actual_healing,
            "overhealing": max(0, healing - actual_healing),
            "previous_hp": old_hp,
            "current_hp": self.current_hp,
            "regained_consciousness": not was_conscious and self.is_conscious
        }
    
    def add_status_effect(self, effect: StatusEffect) -> None:
        """Add a status effect to the combatant."""
        # Check if effect already exists (handle stacking rules)
        existing_effect = self.get_status_effect(effect.name)
        
        if existing_effect:
            if effect.stackable:
                # Add as new instance
                self.status_effects.append(effect)
            else:
                # Refresh duration if new effect has longer duration
                if effect.duration > existing_effect.duration:
                    existing_effect.duration = effect.duration
                if hasattr(effect, 'value') and hasattr(existing_effect, 'value'):
                    # Update value if applicable
                    existing_effect.value = max(getattr(effect, 'value', 0), getattr(existing_effect, 'value', 0))
        else:
            self.status_effects.append(effect)
        
        effect.combatant_id = self.id
    
    def remove_status_effect(self, effect_name: str) -> bool:
        """Remove a status effect by name."""
        for i, effect in enumerate(self.status_effects):
            if effect.name == effect_name:
                self.status_effects.pop(i)
                return True
        return False
    
    def get_status_effect(self, effect_name: str) -> Optional[StatusEffect]:
        """Get a status effect by name."""
        for effect in self.status_effects:
            if effect.name == effect_name:
                return effect
        return None
    
    def has_status_effect(self, effect_name: str) -> bool:
        """Check if combatant has a specific status effect."""
        return self.get_status_effect(effect_name) is not None
    
    def tick_status_effects(self) -> List[str]:
        """
        Process status effects for one turn (reduce durations, remove expired).
        
        Returns:
            List of effect names that expired this turn
        """
        expired_effects = []
        remaining_effects = []
        
        for effect in self.status_effects:
            effect.duration -= 1
            if effect.duration <= 0:
                expired_effects.append(effect.name)
            else:
                remaining_effects.append(effect)
        
        self.status_effects = remaining_effects
        return expired_effects
    
    def get_effective_armor_class(self) -> int:
        """Calculate effective AC including status effect modifications."""
        base_ac = self.armor_class
        
        for effect in self.status_effects:
            if hasattr(effect, 'ac_modifier'):
                base_ac += effect.ac_modifier
        
        return max(0, base_ac)  # AC can't go below 0
    
    def get_effective_stat(self, stat_name: str) -> int:
        """Get effective stat value including status effect modifications."""
        base_value = getattr(self, stat_name, 0)
        
        for effect in self.status_effects:
            modifier_attr = f"{stat_name}_modifier"
            if hasattr(effect, modifier_attr):
                base_value += getattr(effect, modifier_attr)
        
        return base_value
    
    def reset_action_economy(self, movement_speed: Optional[float] = None) -> None:
        """Reset action economy for a new turn."""
        self.has_used_standard_action = False
        self.has_used_bonus_action = False
        self.has_used_reaction = False
        self.used_free_actions = 0
        self.remaining_movement = movement_speed or 30.0
    
    def can_take_action(self, action_type: str) -> bool:
        """Check if combatant can take a specific type of action."""
        if not self.is_active or not self.is_conscious:
            return False
        
        # Check for status effects that prevent actions
        for effect in self.status_effects:
            if hasattr(effect, 'blocks_actions') and effect.blocks_actions:
                return False
            if hasattr(effect, 'blocked_action_types') and action_type in effect.blocked_action_types:
                return False
        
        # Check action economy
        action_type_lower = action_type.lower()
        if action_type_lower == "standard" and self.has_used_standard_action:
            return False
        if action_type_lower == "bonus" and self.has_used_bonus_action:
            return False
        if action_type_lower == "reaction" and self.has_used_reaction:
            return False
        if action_type_lower == "free" and self.used_free_actions >= self.max_free_actions:
            return False
        
        return True
    
    def use_action(self, action_type: str) -> bool:
        """Mark an action type as used for this turn."""
        if not self.can_take_action(action_type):
            return False
        
        action_type_lower = action_type.lower()
        if action_type_lower == "standard":
            self.has_used_standard_action = True
        elif action_type_lower == "bonus":
            self.has_used_bonus_action = True
        elif action_type_lower == "reaction":
            self.has_used_reaction = True
        elif action_type_lower == "free":
            self.used_free_actions += 1
        
        return True
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of the combatant's current status."""
        return {
            "id": str(self.id),
            "name": self.name,
            "team": self.team,
            "hp": f"{self.current_hp}/{self.max_hp}",
            "temp_hp": self.temporary_hp,
            "ac": self.get_effective_armor_class(),
            "is_active": self.is_active,
            "is_conscious": self.is_conscious,
            "status_effects": [effect.name for effect in self.status_effects],
            "actions_available": {
                "standard": not self.has_used_standard_action,
                "bonus": not self.has_used_bonus_action,
                "reaction": not self.has_used_reaction,
                "free": f"{self.max_free_actions - self.used_free_actions}/{self.max_free_actions}",
                "movement": self.remaining_movement
            }
        }
    
    def is_enemy_of(self, other: 'Combatant') -> bool:
        """Check if this combatant is an enemy of another combatant."""
        if self.team == other.team:
            return False
        
        # Define enemy relationships
        enemy_teams = {
            "player": ["hostile", "enemy"],
            "hostile": ["player", "ally"],
            "enemy": ["player", "ally"],
            "ally": ["hostile", "enemy"]
        }
        
        return other.team in enemy_teams.get(self.team, [])
    
    def is_ally_of(self, other: 'Combatant') -> bool:
        """Check if this combatant is an ally of another combatant."""
        return self.team == other.team and self != other


__all__ = ["Combatant"] 