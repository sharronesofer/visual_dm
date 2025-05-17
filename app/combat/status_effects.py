from typing import Dict, List, Optional, Set, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid
import json
import os

class EffectType(Enum):
    """Types of status effects that can be applied to combatants."""
    BUFF = "buff"
    DEBUFF = "debuff"
    CONDITION = "condition"
    
class DurationType(Enum):
    """Types of duration tracking for status effects."""
    ROUNDS = "rounds"
    MINUTES = "minutes"
    HOURS = "hours"
    PERMANENT = "permanent"
    SPECIAL = "special"  # For effects with custom duration logic

@dataclass
class EffectModifier:
    """Represents a modification to a character attribute or stat."""
    attribute: str  # The attribute being modified
    value: Union[int, float]  # The modification value
    operator: str = "add"  # add, multiply, set, etc.
    
    def apply(self, base_value: Union[int, float]) -> Union[int, float]:
        """Apply the modifier to a base value."""
        if self.operator == "add":
            return base_value + self.value
        elif self.operator == "multiply":
            return base_value * self.value
        elif self.operator == "set":
            return self.value
        return base_value

@dataclass
class StatusEffect:
    """Represents a status effect that can be applied to a combatant."""
    id: str
    name: str
    type: EffectType
    description: str
    modifiers: List[EffectModifier]
    duration_type: DurationType
    duration_value: int
    source: str
    stackable: bool = False
    max_stacks: int = 1
    immunities_granted: Set[str] = None
    resistances_granted: Dict[str, float] = None
    custom_logic: Dict = None
    
    def __post_init__(self):
        if self.immunities_granted is None:
            self.immunities_granted = set()
        if self.resistances_granted is None:
            self.resistances_granted = {}
        if self.custom_logic is None:
            self.custom_logic = {}

class StatusEffectInstance:
    """An instance of a status effect applied to a specific combatant."""
    def __init__(
        self,
        effect: StatusEffect,
        target_id: str,
        start_time: datetime,
        current_stacks: int = 1
    ):
        self.id = str(uuid.uuid4())
        self.effect = effect
        self.target_id = target_id
        self.start_time = start_time
        self.current_stacks = current_stacks
        self.remaining_duration = effect.duration_value
        
    def update_duration(self, time_passed: int = 1) -> bool:
        """
        Update the remaining duration of the effect.
        Returns True if the effect is still active, False if expired.
        """
        if self.effect.duration_type == DurationType.PERMANENT:
            return True
            
        if self.effect.duration_type == DurationType.SPECIAL:
            # Custom duration logic should be handled by the combat system
            return True
            
        self.remaining_duration -= time_passed
        return self.remaining_duration > 0
        
    def add_stack(self) -> bool:
        """
        Add a stack to the effect if possible.
        Returns True if stack was added, False if at max stacks.
        """
        if not self.effect.stackable:
            return False
            
        if self.current_stacks >= self.effect.max_stacks:
            return False
            
        self.current_stacks += 1
        return True
        
    def remove_stack(self) -> bool:
        """
        Remove a stack from the effect.
        Returns True if stack was removed, False if at minimum stacks.
        """
        if self.current_stacks <= 1:
            return False
            
        self.current_stacks -= 1
        return True
        
    def get_total_modifier(self, attribute: str) -> Union[int, float]:
        """Calculate the total modification for an attribute based on current stacks."""
        total = 0
        for modifier in self.effect.modifiers:
            if modifier.attribute == attribute:
                if modifier.operator == "multiply":
                    # For multiplicative effects, we use (modifier - 1) * stacks + 1
                    # This ensures proper stacking of percentage modifiers
                    total += (modifier.value - 1) * self.current_stacks + 1
                else:
                    total += modifier.value * self.current_stacks
        return total

class StatusEffectsSystem:
    """
    System for managing status effects on combatants.
    """
    def __init__(self):
        self.active_effects: Dict[str, List[StatusEffectInstance]] = {}
        self.effect_registry: Dict[str, StatusEffect] = {}
        
    def register_effect(self, effect: StatusEffect):
        """Register a new type of status effect that can be applied."""
        self.effect_registry[effect.id] = effect
        
    def get_effect(self, effect_id: str) -> Optional[StatusEffect]:
        """Get a registered effect by ID."""
        return self.effect_registry.get(effect_id)
        
    def apply_effect(
        self,
        target_id: str,
        effect_id: str,
        start_time: datetime
    ) -> Optional[str]:
        """
        Apply a status effect to a target.
        Returns the instance ID if successful, None if failed.
        """
        effect = self.get_effect(effect_id)
        if not effect:
            return None
            
        # Check immunities
        target_effects = self.active_effects.get(target_id, [])
        for active_effect in target_effects:
            if effect.id in active_effect.effect.immunities_granted:
                return None
                
        # Check for existing instance of this effect
        existing_instance = next(
            (inst for inst in target_effects if inst.effect.id == effect_id),
            None
        )
        
        if existing_instance:
            if existing_instance.effect.stackable:
                if existing_instance.add_stack():
                    return existing_instance.id
                return None
            # Refresh duration for non-stackable effects
            existing_instance.remaining_duration = effect.duration_value
            existing_instance.start_time = start_time
            return existing_instance.id
            
        # Create new instance
        instance = StatusEffectInstance(effect, target_id, start_time)
        if target_id not in self.active_effects:
            self.active_effects[target_id] = []
        self.active_effects[target_id].append(instance)
        return instance.id
        
    def remove_effect(
        self,
        target_id: str,
        instance_id: str,
        remove_all_stacks: bool = True
    ) -> bool:
        """
        Remove a status effect from a target.
        Returns True if removed, False if not found.
        """
        if target_id not in self.active_effects:
            return False
            
        target_effects = self.active_effects[target_id]
        instance = next(
            (inst for inst in target_effects if inst.id == instance_id),
            None
        )
        
        if not instance:
            return False
            
        if not remove_all_stacks and instance.current_stacks > 1:
            instance.remove_stack()
            return True
            
        self.active_effects[target_id] = [
            inst for inst in target_effects if inst.id != instance_id
        ]
        return True
        
    def update_durations(
        self,
        current_time: datetime,
        duration_type: DurationType,
        time_passed: int = 1
    ):
        """Update durations for all effects of a specific duration type."""
        for target_id in list(self.active_effects.keys()):
            # Create a new list for effects that are still active
            active = []
            for instance in self.active_effects[target_id]:
                if instance.effect.duration_type == duration_type:
                    if instance.update_duration(time_passed):
                        active.append(instance)
                else:
                    active.append(instance)
            
            if active:
                self.active_effects[target_id] = active
            else:
                del self.active_effects[target_id]
                
    def get_active_effects(self, target_id: str) -> List[StatusEffectInstance]:
        """Get all active effects on a target."""
        return self.active_effects.get(target_id, [])
        
    def calculate_modified_value(
        self,
        target_id: str,
        attribute: str,
        base_value: Union[int, float]
    ) -> Union[int, float]:
        """Calculate the final value of an attribute after all effect modifiers."""
        if target_id not in self.active_effects:
            return base_value
            
        modified_value = base_value
        multiplicative_mods = 1.0
        
        for instance in self.active_effects[target_id]:
            for modifier in instance.effect.modifiers:
                if modifier.attribute != attribute:
                    continue
                    
                if modifier.operator == "multiply":
                    multiplicative_mods *= instance.get_total_modifier(attribute)
                elif modifier.operator == "add":
                    modified_value += instance.get_total_modifier(attribute)
                elif modifier.operator == "set":
                    # "set" operations override all other modifications
                    return instance.get_total_modifier(attribute)
                    
        return modified_value * multiplicative_mods
        
    def get_immunities(self, target_id: str) -> Set[str]:
        """Get all immunities granted by active effects."""
        immunities = set()
        for instance in self.active_effects.get(target_id, []):
            immunities.update(instance.effect.immunities_granted)
        return immunities
        
    def get_resistances(self, target_id: str) -> Dict[str, float]:
        """Get all resistances granted by active effects."""
        resistances = {}
        for instance in self.active_effects.get(target_id, []):
            for damage_type, value in instance.effect.resistances_granted.items():
                # Take the strongest resistance value for each damage type
                if damage_type not in resistances or value < resistances[damage_type]:
                    resistances[damage_type] = value
        return resistances
        
    def has_effect_type(self, target_id: str, effect_type: EffectType) -> bool:
        """Check if target has any effects of a specific type."""
        return any(
            instance.effect.type == effect_type
            for instance in self.active_effects.get(target_id, [])
        )

def load_effects_from_config(config_path: str) -> Dict[str, StatusEffect]:
    """Load status effects from a JSON configuration file."""
    with open(config_path, 'r') as f:
        data = json.load(f)
    effects = {}
    for effect_data in data.get('effects', []):
        try:
            effect = StatusEffect(
                id=effect_data['id'],
                name=effect_data['name'],
                type=EffectType(effect_data['type']),
                description=effect_data.get('description', ''),
                modifiers=[
                    EffectModifier(
                        attribute=mod['attribute'],
                        value=mod['value'],
                        operator=mod.get('operator', 'add')
                    ) for mod in effect_data.get('modifiers', [])
                ],
                duration_type=DurationType(effect_data['duration_type']),
                duration_value=effect_data['duration_value'],
                source=effect_data.get('source', ''),
                stackable=effect_data.get('stackable', False),
                max_stacks=effect_data.get('max_stacks', 1),
                immunities_granted=set(effect_data.get('immunities_granted', [])),
                resistances_granted=effect_data.get('resistances_granted', {}),
                custom_logic=effect_data.get('custom_logic', {})
            )
            effects[effect.id] = effect
        except Exception as e:
            print(f"Failed to load effect {effect_data.get('id', '<unknown>')}: {e}")
    return effects

# Example usage: load and register effects at startup
if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), 'effects', 'effects_config.json')
    effects = load_effects_from_config(config_path)
    system = StatusEffectsSystem()
    for effect in effects.values():
        system.register_effect(effect)
    print(f"Loaded and registered {len(effects)} effects.") 