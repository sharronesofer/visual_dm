"""
Status Effect Domain Model

This module defines the StatusEffect domain model according to
the Development Bible standards. Pure business logic with no infrastructure concerns.
"""

from typing import List, Dict, Any, Optional, Set
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class EffectType(Enum):
    """Types of status effects."""
    CONDITION = "condition"  # D&D-style conditions (stunned, blinded, etc.)
    BUFF = "buff"           # Beneficial effects
    DEBUFF = "debuff"       # Harmful effects
    DAMAGE_OVER_TIME = "damage_over_time"
    HEALING_OVER_TIME = "healing_over_time"
    TEMPORARY = "temporary"  # Short-term modifications


class EffectCategory(Enum):
    """Categories for organizing effects."""
    PHYSICAL = "physical"    # Physical conditions/effects
    MENTAL = "mental"        # Mental/psychic effects  
    MAGICAL = "magical"      # Magic-based effects
    ENVIRONMENTAL = "environmental"  # Environmental effects
    DISEASE = "disease"      # Disease effects
    POISON = "poison"        # Poison effects


@dataclass
class StatusEffect:
    """
    Domain model representing a status effect applied to a combatant.
    
    Encapsulates all state and business rules for status effects,
    including duration, stacking, and mechanical effects.
    """
    
    # Identity
    id: UUID = field(default_factory=uuid4)
    name: str = "Unknown Effect"
    description: str = ""
    
    # Effect Classification
    effect_type: EffectType = EffectType.TEMPORARY
    category: EffectCategory = EffectCategory.MAGICAL
    tags: Set[str] = field(default_factory=set)
    
    # Duration and Stacking
    duration: int = 1  # Duration in turns/rounds
    original_duration: int = 1
    stackable: bool = False
    dispellable: bool = True
    
    # Source Information
    source_name: Optional[str] = None
    source_id: Optional[UUID] = None
    combatant_id: Optional[UUID] = None
    applied_by: Optional[UUID] = None
    
    # Mechanical Effects (stat modifiers)
    hp_modifier: int = 0
    ac_modifier: int = 0
    attack_modifier: int = 0
    damage_modifier: int = 0
    speed_modifier: int = 0
    
    # Ability Score Modifiers
    strength_modifier: int = 0
    dexterity_modifier: int = 0
    constitution_modifier: int = 0
    intelligence_modifier: int = 0
    wisdom_modifier: int = 0
    charisma_modifier: int = 0
    
    # Action/Behavior Restrictions
    blocks_actions: bool = False
    blocks_movement: bool = False
    blocks_reactions: bool = False
    blocked_action_types: Set[str] = field(default_factory=set)
    
    # Damage Over Time
    damage_per_turn: int = 0
    damage_type: Optional[str] = None
    healing_per_turn: int = 0
    
    # Advantage/Disadvantage
    grants_advantage_on: Set[str] = field(default_factory=set)
    grants_disadvantage_on: Set[str] = field(default_factory=set)
    
    # Immunities and Resistances
    damage_immunities: Set[str] = field(default_factory=set)
    damage_resistances: Set[str] = field(default_factory=set)
    damage_vulnerabilities: Set[str] = field(default_factory=set)
    condition_immunities: Set[str] = field(default_factory=set)
    
    # Custom Properties
    properties: Dict[str, Any] = field(default_factory=dict)
    value: Optional[Any] = None  # Generic value for custom effects
    
    # Metadata
    applied_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Initialize computed fields after dataclass initialization."""
        if self.original_duration == 1 and self.duration != 1:
            self.original_duration = self.duration
    
    def tick(self) -> bool:
        """
        Reduce the effect duration by one turn.
        
        Returns:
            True if effect is still active, False if expired
        """
        self.duration = max(0, self.duration - 1)
        return self.duration > 0
    
    def is_expired(self) -> bool:
        """Check if the effect has expired."""
        return self.duration <= 0
    
    def refresh_duration(self, new_duration: Optional[int] = None) -> None:
        """Refresh the effect duration to original or specified value."""
        self.duration = new_duration or self.original_duration
    
    def extend_duration(self, additional_turns: int) -> None:
        """Extend the effect duration by specified turns."""
        if additional_turns < 0:
            raise ValueError("Cannot extend by negative turns")
        self.duration += additional_turns
    
    def has_tag(self, tag: str) -> bool:
        """Check if the effect has a specific tag."""
        return tag.lower() in {t.lower() for t in self.tags}
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the effect."""
        self.tags.add(tag.lower())
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the effect."""
        self.tags.discard(tag.lower())
    
    def blocks_action_type(self, action_type: str) -> bool:
        """Check if this effect blocks a specific action type."""
        if self.blocks_actions:
            return True
        return action_type.lower() in {t.lower() for t in self.blocked_action_types}
    
    def grants_advantage(self, check_type: str) -> bool:
        """Check if this effect grants advantage on a specific type of check."""
        return check_type.lower() in {t.lower() for t in self.grants_advantage_on}
    
    def grants_disadvantage(self, check_type: str) -> bool:
        """Check if this effect grants disadvantage on a specific type of check."""
        return check_type.lower() in {t.lower() for t in self.grants_disadvantage_on}
    
    def provides_immunity(self, damage_or_condition_type: str) -> bool:
        """Check if this effect provides immunity to damage or condition."""
        check_type = damage_or_condition_type.lower()
        return (check_type in {t.lower() for t in self.damage_immunities} or
                check_type in {t.lower() for t in self.condition_immunities})
    
    def provides_resistance(self, damage_type: str) -> bool:
        """Check if this effect provides resistance to a damage type."""
        return damage_type.lower() in {t.lower() for t in self.damage_resistances}
    
    def provides_vulnerability(self, damage_type: str) -> bool:
        """Check if this effect provides vulnerability to a damage type."""
        return damage_type.lower() in {t.lower() for t in self.damage_vulnerabilities}
    
    def get_total_stat_modifier(self, stat_name: str) -> int:
        """Get the total modifier this effect applies to a specific stat."""
        modifier_attr = f"{stat_name.lower()}_modifier"
        return getattr(self, modifier_attr, 0)
    
    def apply_damage_over_time(self) -> Optional[Dict[str, Any]]:
        """
        Apply damage over time if applicable.
        
        Returns:
            Damage information if damage is applied, None otherwise
        """
        if self.damage_per_turn <= 0:
            return None
        
        return {
            "damage": self.damage_per_turn,
            "damage_type": self.damage_type or "untyped",
            "source": self.name,
            "source_id": str(self.id)
        }
    
    def apply_healing_over_time(self) -> Optional[Dict[str, Any]]:
        """
        Apply healing over time if applicable.
        
        Returns:
            Healing information if healing is applied, None otherwise
        """
        if self.healing_per_turn <= 0:
            return None
        
        return {
            "healing": self.healing_per_turn,
            "source": self.name,
            "source_id": str(self.id)
        }
    
    def get_effect_summary(self) -> Dict[str, Any]:
        """Get a summary of the effect's properties."""
        return {
            "id": str(self.id),
            "name": self.name,
            "type": self.effect_type.value,
            "category": self.category.value,
            "duration": self.duration,
            "original_duration": self.original_duration,
            "stackable": self.stackable,
            "dispellable": self.dispellable,
            "source": self.source_name,
            "tags": list(self.tags),
            "modifiers": {
                "hp": self.hp_modifier,
                "ac": self.ac_modifier,
                "attack": self.attack_modifier,
                "damage": self.damage_modifier,
                "speed": self.speed_modifier
            },
            "restrictions": {
                "blocks_actions": self.blocks_actions,
                "blocks_movement": self.blocks_movement,
                "blocks_reactions": self.blocks_reactions,
                "blocked_types": list(self.blocked_action_types)
            },
            "over_time": {
                "damage": self.damage_per_turn,
                "healing": self.healing_per_turn
            }
        }
    
    def copy(self) -> 'StatusEffect':
        """Create a copy of this status effect with a new ID."""
        # Create a copy with all the same values but new ID
        effect_copy = StatusEffect(
            id=uuid4(),
            name=self.name,
            description=self.description,
            effect_type=self.effect_type,
            category=self.category,
            tags=self.tags.copy(),
            duration=self.duration,
            original_duration=self.original_duration,
            stackable=self.stackable,
            dispellable=self.dispellable,
            source_name=self.source_name,
            source_id=self.source_id,
            applied_by=self.applied_by,
            hp_modifier=self.hp_modifier,
            ac_modifier=self.ac_modifier,
            attack_modifier=self.attack_modifier,
            damage_modifier=self.damage_modifier,
            speed_modifier=self.speed_modifier,
            strength_modifier=self.strength_modifier,
            dexterity_modifier=self.dexterity_modifier,
            constitution_modifier=self.constitution_modifier,
            intelligence_modifier=self.intelligence_modifier,
            wisdom_modifier=self.wisdom_modifier,
            charisma_modifier=self.charisma_modifier,
            blocks_actions=self.blocks_actions,
            blocks_movement=self.blocks_movement,
            blocks_reactions=self.blocks_reactions,
            blocked_action_types=self.blocked_action_types.copy(),
            damage_per_turn=self.damage_per_turn,
            damage_type=self.damage_type,
            healing_per_turn=self.healing_per_turn,
            grants_advantage_on=self.grants_advantage_on.copy(),
            grants_disadvantage_on=self.grants_disadvantage_on.copy(),
            damage_immunities=self.damage_immunities.copy(),
            damage_resistances=self.damage_resistances.copy(),
            damage_vulnerabilities=self.damage_vulnerabilities.copy(),
            condition_immunities=self.condition_immunities.copy(),
            properties=self.properties.copy(),
            value=self.value
        )
        return effect_copy
    
    @classmethod
    def create_from_template(cls, template_name: str, **overrides) -> 'StatusEffect':
        """Create a status effect from a predefined template."""
        # This could load from the JSON configuration
        templates = {
            "stunned": {
                "name": "Stunned",
                "description": "Cannot take actions or reactions",
                "effect_type": EffectType.CONDITION,
                "category": EffectCategory.PHYSICAL,
                "duration": 1,
                "blocks_actions": True,
                "blocks_reactions": True,
                "tags": {"condition", "debuff"}
            },
            "poisoned": {
                "name": "Poisoned",
                "description": "Disadvantage on attack rolls and ability checks",
                "effect_type": EffectType.CONDITION,
                "category": EffectCategory.POISON,
                "duration": 10,
                "attack_modifier": -2,
                "grants_disadvantage_on": {"attack", "ability_check"},
                "tags": {"condition", "poison", "debuff"}
            },
            "blessed": {
                "name": "Blessed",
                "description": "Bonus to attack rolls and saving throws",
                "effect_type": EffectType.BUFF,
                "category": EffectCategory.MAGICAL,
                "duration": 100,
                "attack_modifier": 1,
                "grants_advantage_on": {"saving_throw"},
                "tags": {"buff", "magical"}
            }
        }
        
        template = templates.get(template_name.lower())
        if not template:
            raise ValueError(f"Unknown status effect template: {template_name}")
        
        # Merge template with overrides
        effect_data = {**template, **overrides}
        
        # Convert sets from lists if needed
        for field in ["tags", "blocked_action_types", "grants_advantage_on", 
                     "grants_disadvantage_on", "damage_immunities", 
                     "damage_resistances", "damage_vulnerabilities", 
                     "condition_immunities"]:
            if field in effect_data and isinstance(effect_data[field], (list, tuple)):
                effect_data[field] = set(effect_data[field])
        
        return cls(**effect_data)


__all__ = ["StatusEffect", "EffectType", "EffectCategory"] 