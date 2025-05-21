"""
EffectPipeline module for the Visual DM combat system.

This module implements a comprehensive effect management system that handles
applying, stacking, timing, and removing combat effects. It integrates with
the turn system to provide proper hooks for start/end of turns.

Following the design principles from the Development Bible, this implementation:
1. Manages the application of effects to combatants
2. Handles stacking of multiple effects
3. Supports resistance, immunity, and custom timing
4. Integrates with turn system using start/end hooks
"""

import logging
import uuid
from typing import Dict, List, Any, Set, Optional, Callable, Tuple
from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class EffectStackingBehavior(Enum):
    """Defines how effects of the same type stack when applied multiple times."""
    NONE = auto()  # New effect replaces existing one
    DURATION = auto()  # Durations add together
    INTENSITY = auto()  # Intensity increases
    BOTH = auto()  # Both duration and intensity increase
    REPLACE_IF_STRONGER = auto()  # Replace only if new effect is stronger
    SEPARATE = auto()  # Create separate effect instances


class EffectType(Enum):
    """Types of combat effects."""
    BUFF = auto()  # Positive effect
    DEBUFF = auto()  # Negative effect
    CONDITION = auto()  # Special condition (prone, stunned, etc.)
    DAMAGE_OVER_TIME = auto()  # Damage applied over time
    HEAL_OVER_TIME = auto()  # Healing applied over time
    RESISTANCE = auto()  # Resistance to damage types
    VULNERABILITY = auto()  # Vulnerability to damage types
    IMMUNITY = auto()  # Immunity to damage types
    TRIGGER = auto()  # Effect triggered by certain conditions
    PASSIVE = auto()  # Always-active effect


@dataclass
class CombatEffect:
    """Base class for all combat effects."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    effect_type: EffectType = EffectType.BUFF
    duration: int = 1  # Duration in rounds, -1 for permanent
    intensity: float = 1.0  # Effect strength
    max_stacks: int = 1  # Maximum number of stacks
    current_stacks: int = 1  # Current number of stacks
    stacking_behavior: EffectStackingBehavior = EffectStackingBehavior.NONE
    source_id: Optional[str] = None  # ID of the source of the effect
    target_id: Optional[str] = None  # ID of the target of the effect
    applied_at: datetime = field(default_factory=datetime.now)  # When the effect was applied
    tags: List[str] = field(default_factory=list)  # Tags for filtering/categorizing
    
    # Callback hooks for effect events
    on_applied: List[Callable[['CombatEffect', Any], None]] = field(default_factory=list)
    on_removed: List[Callable[['CombatEffect', Any], None]] = field(default_factory=list)
    on_turn_start: List[Callable[['CombatEffect', Any], None]] = field(default_factory=list)
    on_turn_end: List[Callable[['CombatEffect', Any], None]] = field(default_factory=list)
    on_stacked: List[Callable[['CombatEffect', Any, int], None]] = field(default_factory=list)
    
    def apply(self, target: Any) -> bool:
        """
        Apply this effect to a target.
        
        Args:
            target: The target to apply the effect to
            
        Returns:
            True if the effect was applied, False otherwise
        """
        # Store the target's ID
        self.target_id = getattr(target, 'character_id', str(target))
        
        # Run on_applied callbacks
        for callback in self.on_applied:
            callback(self, target)
            
        return True
    
    def remove(self, target: Any) -> bool:
        """
        Remove this effect from a target.
        
        Args:
            target: The target to remove the effect from
            
        Returns:
            True if the effect was removed, False otherwise
        """
        # Run on_removed callbacks
        for callback in self.on_removed:
            callback(self, target)
            
        return True
    
    def on_turn_start_trigger(self, target: Any) -> None:
        """
        Trigger turn start effects.
        
        Args:
            target: The target with this effect
        """
        for callback in self.on_turn_start:
            callback(self, target)
    
    def on_turn_end_trigger(self, target: Any) -> None:
        """
        Trigger turn end effects.
        
        Args:
            target: The target with this effect
        """
        for callback in self.on_turn_end:
            callback(self, target)
            
        # Reduce duration if not permanent
        if self.duration > 0:
            self.duration -= 1
    
    def on_stacked_trigger(self, target: Any, stack_count: int) -> None:
        """
        Trigger stacking effects.
        
        Args:
            target: The target with this effect
            stack_count: New stack count
        """
        for callback in self.on_stacked:
            callback(self, target, stack_count)
    
    def can_stack(self) -> bool:
        """
        Check if this effect can stack further.
        
        Returns:
            True if the effect can stack, False otherwise
        """
        return (self.stacking_behavior != EffectStackingBehavior.NONE and 
                self.current_stacks < self.max_stacks)
    
    def stack(self, new_effect: 'CombatEffect') -> bool:
        """
        Stack this effect with a new instance.
        
        Args:
            new_effect: The new effect to stack with
            
        Returns:
            True if the effect was stacked, False otherwise
        """
        if not self.can_stack():
            return False
            
        if self.stacking_behavior == EffectStackingBehavior.DURATION:
            self.duration += new_effect.duration
            
        elif self.stacking_behavior == EffectStackingBehavior.INTENSITY:
            self.intensity += new_effect.intensity
            
        elif self.stacking_behavior == EffectStackingBehavior.BOTH:
            self.duration += new_effect.duration
            self.intensity += new_effect.intensity
            
        elif self.stacking_behavior == EffectStackingBehavior.REPLACE_IF_STRONGER:
            if new_effect.intensity > self.intensity:
                self.intensity = new_effect.intensity
                self.duration = new_effect.duration
            
        self.current_stacks = min(self.current_stacks + 1, self.max_stacks)
        return True
    
    def is_expired(self) -> bool:
        """
        Check if this effect has expired.
        
        Returns:
            True if the effect has expired, False otherwise
        """
        return self.duration == 0
    
    def modify_damage(self, damage: float, damage_type: str = None) -> float:
        """
        Modify damage based on this effect.
        
        Args:
            damage: The original damage value
            damage_type: Optional damage type
            
        Returns:
            Modified damage value
        """
        # Base implementation does nothing, subclasses should override
        return damage
    
    def get_icon_info(self) -> Dict[str, Any]:
        """
        Get information for visualizing this effect.
        
        Returns:
            Dictionary with visualization info
        """
        return {
            "name": self.name,
            "icon_type": self.effect_type.name.lower(),
            "duration": self.duration,
            "intensity": self.intensity,
            "stacks": self.current_stacks,
            "description": self.description
        }


class BuffEffect(CombatEffect):
    """Positive effect that enhances a combatant's abilities."""
    
    def __init__(self, **kwargs):
        super().__init__(effect_type=EffectType.BUFF, **kwargs)


class DebuffEffect(CombatEffect):
    """Negative effect that impairs a combatant's abilities."""
    
    def __init__(self, **kwargs):
        super().__init__(effect_type=EffectType.DEBUFF, **kwargs)


class DamageOverTimeEffect(CombatEffect):
    """Effect that deals damage each turn."""
    
    def __init__(self, damage_per_turn: float = 0, damage_type: str = "fire", **kwargs):
        super().__init__(effect_type=EffectType.DAMAGE_OVER_TIME, **kwargs)
        self.damage_per_turn = damage_per_turn
        self.damage_type = damage_type
        
        # Add turn start callback to apply damage
        def apply_damage(effect, target):
            if hasattr(target, 'apply_damage'):
                damage = effect.damage_per_turn * effect.intensity
                target.apply_damage(damage)
                logger.info(f"DoT effect {effect.name} dealt {damage} {effect.damage_type} damage to {target}")
        
        self.on_turn_start.append(apply_damage)


class HealOverTimeEffect(CombatEffect):
    """Effect that heals each turn."""
    
    def __init__(self, heal_per_turn: float = 0, **kwargs):
        super().__init__(effect_type=EffectType.HEAL_OVER_TIME, **kwargs)
        self.heal_per_turn = heal_per_turn
        
        # Add turn start callback to apply healing
        def apply_healing(effect, target):
            if hasattr(target, 'heal'):
                healing = effect.heal_per_turn * effect.intensity
                target.heal(healing)
                logger.info(f"HoT effect {effect.name} healed {healing} to {target}")
        
        self.on_turn_start.append(apply_healing)


class ConditionEffect(CombatEffect):
    """Special condition effect (prone, stunned, etc.)."""
    
    def __init__(self, condition: str = "", **kwargs):
        super().__init__(effect_type=EffectType.CONDITION, **kwargs)
        self.condition = condition
        self.name = condition if not self.name else self.name


class ResistanceEffect(CombatEffect):
    """Effect that provides resistance to certain damage types."""
    
    def __init__(self, damage_types: List[str] = None, resistance_multiplier: float = 0.5, **kwargs):
        super().__init__(effect_type=EffectType.RESISTANCE, **kwargs)
        self.damage_types = damage_types or []
        self.resistance_multiplier = resistance_multiplier
    
    def modify_damage(self, damage: float, damage_type: str = None) -> float:
        if damage_type in self.damage_types:
            return damage * self.resistance_multiplier
        return damage


class VulnerabilityEffect(CombatEffect):
    """Effect that creates vulnerability to certain damage types."""
    
    def __init__(self, damage_types: List[str] = None, vulnerability_multiplier: float = 2.0, **kwargs):
        super().__init__(effect_type=EffectType.VULNERABILITY, **kwargs)
        self.damage_types = damage_types or []
        self.vulnerability_multiplier = vulnerability_multiplier
    
    def modify_damage(self, damage: float, damage_type: str = None) -> float:
        if damage_type in self.damage_types:
            return damage * self.vulnerability_multiplier
        return damage


class ImmunityEffect(CombatEffect):
    """Effect that provides immunity to certain damage types or effects."""
    
    def __init__(self, damage_types: List[str] = None, immune_effects: List[str] = None, **kwargs):
        super().__init__(effect_type=EffectType.IMMUNITY, **kwargs)
        self.damage_types = damage_types or []
        self.immune_effects = immune_effects or []
    
    def modify_damage(self, damage: float, damage_type: str = None) -> float:
        if damage_type in self.damage_types:
            return 0
        return damage


class EffectPipeline:
    """
    Manages combat effects for all combatants.
    
    Handles application, stacking, timing, and removal of effects.
    Integrates with the turn system for proper turn start/end hooks.
    """
    
    def __init__(self):
        """Initialize an empty effect pipeline."""
        # Map of combatant to their active effects
        self._effects: Dict[Any, List[CombatEffect]] = {}
        
        # Event callbacks
        self._on_effect_applied: List[Callable[[Any, CombatEffect], None]] = []
        self._on_effect_removed: List[Callable[[Any, CombatEffect], None]] = []
        self._on_effect_expired: List[Callable[[Any, CombatEffect], None]] = []
    
    def get_applied_effects(self, combatant: Any) -> List[CombatEffect]:
        """
        Get all effects applied to a combatant.
        
        Args:
            combatant: The combatant to get effects for
            
        Returns:
            List of active effects on the combatant
        """
        combatant_id = self._get_combatant_id(combatant)
        return self._effects.get(combatant_id, []).copy()
    
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
    
    def _get_matching_effects(self, combatant: Any, effect_type: Optional[EffectType] = None,
                             effect_name: Optional[str] = None) -> List[CombatEffect]:
        """
        Get effects on a combatant matching certain criteria.
        
        Args:
            combatant: The combatant to check
            effect_type: Optional type to filter by
            effect_name: Optional name to filter by
            
        Returns:
            List of matching effects
        """
        combatant_id = self._get_combatant_id(combatant)
        if combatant_id not in self._effects:
            return []
            
        effects = self._effects[combatant_id]
        
        if effect_type is not None:
            effects = [e for e in effects if e.effect_type == effect_type]
            
        if effect_name is not None:
            effects = [e for e in effects if e.name == effect_name]
            
        return effects
    
    def apply_effect(self, source: Any, target: Any, effect: CombatEffect) -> bool:
        """
        Apply an effect from a source to a target.
        
        Args:
            source: The source of the effect
            target: The target to apply the effect to
            effect: The effect to apply
            
        Returns:
            True if the effect was applied, False otherwise
        """
        # Handle immunity
        if self.is_immune_to_effect(target, effect):
            logger.info(f"{target} is immune to {effect.name}")
            return False
        
        # Set source ID
        effect.source_id = self._get_combatant_id(source)
        
        # Get target ID
        target_id = self._get_combatant_id(target)
        
        # Initialize effects list for this target if needed
        if target_id not in self._effects:
            self._effects[target_id] = []
        
        # Check for existing effects of same type/name
        existing_effects = [e for e in self._effects[target_id] 
                           if e.name == effect.name]
        
        # If no existing effect, apply new one
        if not existing_effects:
            # Apply the effect
            if effect.apply(target):
                self._effects[target_id].append(effect)
                
                # Call callbacks
                for callback in self._on_effect_applied:
                    callback(target, effect)
                
                logger.info(f"Applied effect {effect.name} to {target}")
                return True
            return False
        
        # Handle stacking with existing effect
        existing = existing_effects[0]
        if existing.can_stack():
            if existing.stack(effect):
                existing.on_stacked_trigger(target, existing.current_stacks)
                logger.info(f"Stacked effect {effect.name} on {target}, now at {existing.current_stacks} stacks")
                return True
        
        # Replace if stacking behavior requires it
        if existing.stacking_behavior == EffectStackingBehavior.REPLACE_IF_STRONGER and effect.intensity > existing.intensity:
            self.remove_effect(target, existing)
            if effect.apply(target):
                self._effects[target_id].append(effect)
                
                # Call callbacks
                for callback in self._on_effect_applied:
                    callback(target, effect)
                
                logger.info(f"Replaced effect {existing.name} with stronger version on {target}")
                return True
        
        # If we get here, the effect couldn't be applied due to stacking rules
        logger.info(f"Effect {effect.name} not applied to {target} due to stacking rules")
        return False
    
    def remove_effect(self, target: Any, effect: CombatEffect) -> bool:
        """
        Remove a specific effect from a target.
        
        Args:
            target: The target to remove the effect from
            effect: The effect to remove
            
        Returns:
            True if the effect was removed, False otherwise
        """
        target_id = self._get_combatant_id(target)
        
        if target_id not in self._effects:
            return False
            
        if effect not in self._effects[target_id]:
            return False
        
        # Remove the effect
        if effect.remove(target):
            self._effects[target_id].remove(effect)
            
            # Call callbacks
            for callback in self._on_effect_removed:
                callback(target, effect)
            
            logger.info(f"Removed effect {effect.name} from {target}")
            return True
        
        return False
    
    def remove_effects_by_type(self, target: Any, effect_type: EffectType) -> int:
        """
        Remove all effects of a certain type from a target.
        
        Args:
            target: The target to remove effects from
            effect_type: The type of effects to remove
            
        Returns:
            Number of effects removed
        """
        target_id = self._get_combatant_id(target)
        
        if target_id not in self._effects:
            return 0
        
        effects_to_remove = [e for e in self._effects[target_id] if e.effect_type == effect_type]
        
        count = 0
        for effect in effects_to_remove:
            if self.remove_effect(target, effect):
                count += 1
        
        return count
    
    def remove_effects_by_name(self, target: Any, effect_name: str) -> int:
        """
        Remove all effects with a certain name from a target.
        
        Args:
            target: The target to remove effects from
            effect_name: The name of effects to remove
            
        Returns:
            Number of effects removed
        """
        target_id = self._get_combatant_id(target)
        
        if target_id not in self._effects:
            return 0
        
        effects_to_remove = [e for e in self._effects[target_id] if e.name == effect_name]
        
        count = 0
        for effect in effects_to_remove:
            if self.remove_effect(target, effect):
                count += 1
        
        return count
    
    def clear_effects(self, target: Any) -> int:
        """
        Remove all effects from a target.
        
        Args:
            target: The target to clear effects from
            
        Returns:
            Number of effects removed
        """
        target_id = self._get_combatant_id(target)
        
        if target_id not in self._effects:
            return 0
        
        effects_to_remove = self._effects[target_id].copy()
        
        count = 0
        for effect in effects_to_remove:
            if self.remove_effect(target, effect):
                count += 1
        
        return count
    
    def clear_all_effects(self) -> int:
        """
        Remove all effects from all combatants.
        
        Returns:
            Number of effects removed
        """
        total_count = 0
        
        for target_id in list(self._effects.keys()):
            effects_to_remove = self._effects[target_id].copy()
            
            for effect in effects_to_remove:
                # Since we don't have the actual target object, we'll fake it for remove
                dummy_target = type('DummyTarget', (), {'character_id': target_id})
                if self.remove_effect(dummy_target, effect):
                    total_count += 1
        
        return total_count
    
    def process_turn_start(self, combatant: Any) -> None:
        """
        Process turn start for a combatant, triggering all relevant effects.
        
        Args:
            combatant: The combatant whose turn is starting
        """
        combatant_id = self._get_combatant_id(combatant)
        
        if combatant_id not in self._effects:
            return
        
        # Trigger turn start for all effects
        for effect in self._effects[combatant_id]:
            effect.on_turn_start_trigger(combatant)
    
    def process_turn_end(self, combatant: Any) -> None:
        """
        Process turn end for a combatant, triggering all relevant effects.
        
        Args:
            combatant: The combatant whose turn is ending
        """
        combatant_id = self._get_combatant_id(combatant)
        
        if combatant_id not in self._effects:
            return
        
        # Trigger turn end for all effects
        for effect in self._effects[combatant_id].copy():
            effect.on_turn_end_trigger(combatant)
            
            # Check if expired
            if effect.is_expired():
                logger.info(f"Effect {effect.name} expired on {combatant}")
                self.remove_effect(combatant, effect)
                
                # Call expired callbacks
                for callback in self._on_effect_expired:
                    callback(combatant, effect)
    
    def process_before_action(self, source: Any, action: Any, target: Any) -> bool:
        """
        Process effects before an action is performed.
        
        Args:
            source: The source of the action
            action: The action being performed
            target: The target of the action
            
        Returns:
            True if the action should proceed, False if it should be blocked
        """
        # For now, just check if the source is stunned or otherwise incapacitated
        source_id = self._get_combatant_id(source)
        
        if source_id not in self._effects:
            return True
        
        # Check for conditions that prevent actions
        disabling_conditions = ['stunned', 'paralyzed', 'unconscious']
        for effect in self._effects[source_id]:
            if (effect.effect_type == EffectType.CONDITION and
                isinstance(effect, ConditionEffect) and
                effect.condition.lower() in disabling_conditions):
                logger.info(f"{source} cannot act due to being {effect.condition}")
                return False
        
        return True
    
    def process_after_action(self, source: Any, action: Any, target: Any) -> None:
        """
        Process effects after an action is performed.
        
        Args:
            source: The source of the action
            action: The action that was performed
            target: The target of the action
        """
        # This could trigger reactive abilities or effects
        # For now, just a stub
        pass
    
    def modify_damage(self, source: Any, target: Any, damage: float, damage_type: str = None) -> float:
        """
        Modify damage based on effects.
        
        Args:
            source: The source of the damage
            target: The target of the damage
            damage: The original damage value
            damage_type: Optional damage type
            
        Returns:
            Modified damage value
        """
        target_id = self._get_combatant_id(target)
        
        if target_id not in self._effects:
            return damage
        
        modified_damage = damage
        
        # Apply all damage modifier effects
        for effect in self._effects[target_id]:
            modified_damage = effect.modify_damage(modified_damage, damage_type)
        
        return modified_damage
    
    def process_damage(self, target: Any, damage: float) -> None:
        """
        Process effects when damage is taken.
        
        Args:
            target: The target taking damage
            damage: The amount of damage
        """
        # This could trigger effects that activate on damage
        # For now, just a stub
        pass
    
    def process_deal_damage(self, source: Any, target: Any, damage: float) -> None:
        """
        Process effects when damage is dealt.
        
        Args:
            source: The source dealing damage
            target: The target taking damage
            damage: The amount of damage
        """
        # This could trigger effects that activate on dealing damage
        # For now, just a stub
        pass
    
    def process_death(self, target: Any) -> None:
        """
        Process effects when a target dies.
        
        Args:
            target: The target that died
        """
        # This could trigger effects that activate on death
        # For now, just a stub
        pass
    
    def process_kill(self, source: Any, target: Any) -> None:
        """
        Process effects when a source kills a target.
        
        Args:
            source: The source that killed
            target: The target that was killed
        """
        # This could trigger effects that activate on kill
        # For now, just a stub
        pass
    
    def process_heal(self, source: Any, target: Any, healing: float) -> None:
        """
        Process effects when healing is applied.
        
        Args:
            source: The source of healing
            target: The target being healed
            healing: The amount of healing
        """
        # This could trigger effects that activate on healing
        # For now, just a stub
        pass
    
    def process_healed(self, target: Any, source: Any, healing: float) -> None:
        """
        Process effects when a target is healed.
        
        Args:
            target: The target being healed
            source: The source of healing
            healing: The amount of healing
        """
        # This could trigger effects that activate on being healed
        # For now, just a stub
        pass
    
    def register_effect_applied_callback(self, callback: Callable[[Any, CombatEffect], None]) -> None:
        """
        Register a callback for when an effect is applied.
        
        Args:
            callback: Function to call with target and effect
        """
        if callback not in self._on_effect_applied:
            self._on_effect_applied.append(callback)
    
    def register_effect_removed_callback(self, callback: Callable[[Any, CombatEffect], None]) -> None:
        """
        Register a callback for when an effect is removed.
        
        Args:
            callback: Function to call with target and effect
        """
        if callback not in self._on_effect_removed:
            self._on_effect_removed.append(callback)
    
    def register_effect_expired_callback(self, callback: Callable[[Any, CombatEffect], None]) -> None:
        """
        Register a callback for when an effect expires.
        
        Args:
            callback: Function to call with target and effect
        """
        if callback not in self._on_effect_expired:
            self._on_effect_expired.append(callback)
    
    def unregister_effect_applied_callback(self, callback: Callable[[Any, CombatEffect], None]) -> None:
        """
        Unregister a callback for when an effect is applied.
        
        Args:
            callback: The callback to remove
        """
        if callback in self._on_effect_applied:
            self._on_effect_applied.remove(callback)
    
    def unregister_effect_removed_callback(self, callback: Callable[[Any, CombatEffect], None]) -> None:
        """
        Unregister a callback for when an effect is removed.
        
        Args:
            callback: The callback to remove
        """
        if callback in self._on_effect_removed:
            self._on_effect_removed.remove(callback)
    
    def unregister_effect_expired_callback(self, callback: Callable[[Any, CombatEffect], None]) -> None:
        """
        Unregister a callback for when an effect expires.
        
        Args:
            callback: The callback to remove
        """
        if callback in self._on_effect_expired:
            self._on_effect_expired.remove(callback)
    
    def is_immune_to_effect(self, target: Any, effect: CombatEffect) -> bool:
        """
        Check if a target is immune to an effect.
        
        Args:
            target: The target to check
            effect: The effect to check immunity for
            
        Returns:
            True if the target is immune, False otherwise
        """
        target_id = self._get_combatant_id(target)
        
        if target_id not in self._effects:
            return False
        
        # Check for immunity effects
        for existing_effect in self._effects[target_id]:
            if (existing_effect.effect_type == EffectType.IMMUNITY and
                isinstance(existing_effect, ImmunityEffect)):
                # Check if immune to this effect type
                if effect.effect_type.name.lower() in existing_effect.immune_effects:
                    return True
                # Check if immune to this effect by name
                if effect.name.lower() in existing_effect.immune_effects:
                    return True
        
        return False 