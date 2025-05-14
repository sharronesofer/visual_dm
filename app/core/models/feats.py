from enum import Enum
from typing import List, Dict, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime

class FeatType(Enum):
    PASSIVE = "passive"  # Always active effects
    ACTIVATED = "activated"  # Must be activated to use
    REACTIVE = "reactive"  # Triggers on specific conditions
    STANCE = "stance"  # Can be toggled on/off

class TriggerType(Enum):
    ON_ATTACK = "on_attack"
    ON_DAMAGE_TAKEN = "on_damage_taken"
    ON_SKILL_CHECK = "on_skill_check"
    ON_SAVE = "on_save"
    ON_TURN_START = "on_turn_start"
    ON_TURN_END = "on_turn_end"
    ON_REST = "on_rest"
    MANUAL = "manual"  # For activated abilities

class ResourceType(Enum):
    NONE = "none"
    PER_REST = "per_rest"
    PER_DAY = "per_day"
    PER_ENCOUNTER = "per_encounter"
    CHARGES = "charges"

@dataclass
class FeatPrerequisite:
    stat_requirements: Dict[str, int] = None  # e.g., {"strength": 13}
    level_requirement: int = 1
    feat_requirements: List[str] = None
    class_requirements: List[str] = None
    race_requirements: List[str] = None
    skill_requirements: Dict[str, int] = None

@dataclass
class FeatResource:
    type: ResourceType
    amount: int
    current: int = 0
    last_refresh: datetime = None

class FeatEffect:
    def __init__(
        self,
        effect_type: str,
        magnitude: Union[int, float, str],
        duration: Optional[int] = None,
        conditions: Optional[Dict] = None
    ):
        self.effect_type = effect_type
        self.magnitude = magnitude
        self.duration = duration
        self.conditions = conditions or {}
        
    def apply(self, target, source):
        """Apply the effect to the target"""
        raise NotImplementedError

    def remove(self, target):
        """Remove the effect from the target"""
        raise NotImplementedError

class Feat:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        feat_type: FeatType,
        prerequisites: FeatPrerequisite,
        effects: List[FeatEffect],
        trigger: Optional[TriggerType] = None,
        resource: Optional[FeatResource] = None,
        stacking: bool = False,
        tags: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.feat_type = feat_type
        self.prerequisites = prerequisites
        self.effects = effects
        self.trigger = trigger
        self.resource = resource
        self.stacking = stacking
        self.tags = tags or []
        self.active = feat_type == FeatType.PASSIVE
        
    def can_activate(self, character) -> bool:
        """Check if the feat can be activated"""
        if self.resource and self.resource.current <= 0:
            return False
        return self.check_prerequisites(character)
    
    def check_prerequisites(self, character) -> bool:
        """Check if prerequisites are met"""
        if not self.prerequisites:
            return True
            
        # Check stat requirements
        if self.prerequisites.stat_requirements:
            for stat, req_value in self.prerequisites.stat_requirements.items():
                if getattr(character, stat, 0) < req_value:
                    return False
                    
        # Check level
        if character.level < self.prerequisites.level_requirement:
            return False
            
        # Check feats
        if self.prerequisites.feat_requirements:
            character_feats = {feat.id for feat in character.feats}
            if not all(req_feat in character_feats for req_feat in self.prerequisites.feat_requirements):
                return False
                
        # Add more prerequisite checks as needed
        return True
    
    def activate(self, character, target=None):
        """Activate the feat's effects"""
        if not self.can_activate(character):
            return False
            
        if self.resource:
            self.resource.current -= 1
            
        for effect in self.effects:
            effect.apply(target or character, character)
            
        self.active = True
        return True
    
    def deactivate(self, character, target=None):
        """Deactivate the feat's effects"""
        if not self.active:
            return False
            
        for effect in self.effects:
            effect.remove(target or character)
            
        self.active = False
        return True

# Example Effect implementations
class StatModifierEffect(FeatEffect):
    def apply(self, target, source):
        stat = self.effect_type.split('_')[1]  # e.g., "modify_strength" -> "strength"
        current_value = getattr(target, stat, 0)
        setattr(target, stat, current_value + self.magnitude)
        
    def remove(self, target):
        stat = self.effect_type.split('_')[1]
        current_value = getattr(target, stat, 0)
        setattr(target, stat, current_value - self.magnitude)

class DamageModifierEffect(FeatEffect):
    def apply(self, target, source):
        if "damage_type" in self.conditions:
            # Only modify damage of specific type
            target.damage_modifiers[self.conditions["damage_type"]] = self.magnitude
        else:
            # Modify all damage
            target.damage_modifier = self.magnitude
            
    def remove(self, target):
        if "damage_type" in self.conditions:
            del target.damage_modifiers[self.conditions["damage_type"]]
        else:
            target.damage_modifier = 1.0  # Reset to normal

# Feat Manager for handling feat interactions
class FeatManager:
    def __init__(self):
        self.feats: Dict[str, Feat] = {}
        
    def register_feat(self, feat: Feat):
        """Register a new feat type"""
        self.feats[feat.id] = feat
        
    def get_feat(self, feat_id: str) -> Optional[Feat]:
        """Get a feat by ID"""
        return self.feats.get(feat_id)
        
    def create_feat_instance(self, feat_id: str) -> Optional[Feat]:
        """Create a new instance of a feat for a character"""
        feat_template = self.get_feat(feat_id)
        if not feat_template:
            return None
            
        # Create a new instance with its own resource tracking
        return Feat(
            id=feat_template.id,
            name=feat_template.name,
            description=feat_template.description,
            feat_type=feat_template.feat_type,
            prerequisites=feat_template.prerequisites,
            effects=[type(effect)(**vars(effect)) for effect in feat_template.effects],
            trigger=feat_template.trigger,
            resource=FeatResource(**vars(feat_template.resource)) if feat_template.resource else None,
            stacking=feat_template.stacking,
            tags=feat_template.tags.copy() if feat_template.tags else None
        ) 