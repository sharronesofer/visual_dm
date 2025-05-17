from enum import Enum
from typing import List, Dict, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
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

class PowerLevel(Enum):
    """Indicates the relative power level of a feat for balancing purposes"""
    LOW = 1      # Minor benefits, minimal prerequisites
    MEDIUM = 2   # Moderate benefits, some prerequisites
    HIGH = 3     # Significant benefits, substantial prerequisites
    VERY_HIGH = 4  # Major benefits, extensive prerequisites

@dataclass
class FeatPrerequisite:
    stat_requirements: Dict[str, int] = None  # e.g., {"strength": 13}
    level_requirement: int = 1
    feat_requirements: List[str] = None
    class_requirements: List[str] = None
    race_requirements: List[str] = None
    skill_requirements: Dict[str, int] = None
    power_level: PowerLevel = PowerLevel.MEDIUM
    required_ranks: Dict[str, int] = None  # e.g., {"combat": 2} for Combat Rank 2
    
    def __post_init__(self):
        """Initialize default values for None fields"""
        if self.stat_requirements is None:
            self.stat_requirements = {}
        if self.feat_requirements is None:
            self.feat_requirements = []
        if self.class_requirements is None:
            self.class_requirements = []
        if self.race_requirements is None:
            self.race_requirements = []
        if self.skill_requirements is None:
            self.skill_requirements = {}
        if self.required_ranks is None:
            self.required_ranks = {}
    
    def validate(self, character) -> Tuple[bool, List[str]]:
        """Comprehensive validation of prerequisites against character data
        
        Returns:
            Tuple containing:
                - Boolean indicating if all prerequisites are met
                - List of string messages describing unmet prerequisites
        """
        unmet_requirements = []
        
        # Check stat requirements
        if self.stat_requirements:
            for stat, req_value in self.stat_requirements.items():
                char_value = getattr(character, stat, 0)
                if char_value < req_value:
                    unmet_requirements.append(f"Requires {stat.capitalize()} {req_value} (you have {char_value})")
        
        # Check level
        if character.level < self.level_requirement:
            unmet_requirements.append(f"Requires character level {self.level_requirement} (you are level {character.level})")
        
        # Check feats
        if self.feat_requirements:
            character_feats = {feat.id for feat in character.feats}
            missing_feats = [feat_id for feat_id in self.feat_requirements if feat_id not in character_feats]
            if missing_feats:
                unmet_requirements.append(f"Requires feat{'s' if len(missing_feats) > 1 else ''}: {', '.join(missing_feats)}")
        
        # Check class requirements
        if self.class_requirements and character.character_class not in self.class_requirements:
            unmet_requirements.append(f"Requires one of these classes: {', '.join(self.class_requirements)}")
        
        # Check race requirements
        if self.race_requirements and character.race not in self.race_requirements:
            unmet_requirements.append(f"Requires one of these races: {', '.join(self.race_requirements)}")
        
        # Check skill requirements
        if self.skill_requirements:
            for skill, req_value in self.skill_requirements.items():
                char_value = getattr(character.skills, skill, 0)
                if char_value < req_value:
                    unmet_requirements.append(f"Requires {skill.capitalize()} {req_value} (you have {char_value})")
        
        # Check rank requirements
        if self.required_ranks:
            for rank_type, req_value in self.required_ranks.items():
                char_value = getattr(character.ranks, rank_type, 0) if hasattr(character, 'ranks') else 0
                if char_value < req_value:
                    unmet_requirements.append(f"Requires {rank_type.capitalize()} Rank {req_value} (you have Rank {char_value})")
        
        return (len(unmet_requirements) == 0, unmet_requirements)
    
    def get_prerequisite_complexity(self) -> int:
        """Returns a numerical score representing the complexity/strictness of prerequisites
        
        Higher values indicate more restrictive prerequisites.
        """
        complexity = 0
        
        # Add points for each type of requirement
        complexity += len(self.stat_requirements) * 2
        complexity += self.level_requirement - 1  # Level 1 adds no complexity
        complexity += len(self.feat_requirements) * 3  # Feat dependencies are significant
        complexity += len(self.class_requirements) * 2 if self.class_requirements else 0
        complexity += len(self.race_requirements) * 2 if self.race_requirements else 0
        complexity += len(self.skill_requirements) * 2
        complexity += sum(self.required_ranks.values()) * 2 if self.required_ranks else 0
        
        return complexity

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
            
        # Use the new validate method for comprehensive checking
        meets_requirements, _ = self.prerequisites.validate(character)
        return meets_requirements
    
    def get_unmet_prerequisites(self, character) -> List[str]:
        """Get a list of unmet prerequisites with explanations"""
        if not self.prerequisites:
            return []
            
        _, unmet_requirements = self.prerequisites.validate(character)
        return unmet_requirements
        
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
        self.progression_paths: Dict[str, List[str]] = {}  # Maps path name to ordered list of feat IDs
        self.path_categories: Dict[str, str] = {}  # Maps path name to category
        
    def register_feat(self, feat: Feat):
        """Register a new feat type"""
        self.feats[feat.id] = feat
        
    def get_feat(self, feat_id: str) -> Optional[Feat]:
        """Get a feat by ID"""
        return self.feats.get(feat_id)
    
    def register_progression_path(self, path_name: str, feat_ids: List[str], category: str = "general"):
        """Register a progression path - an ordered sequence of feats that form a logical progression"""
        # Verify all feat IDs exist
        for feat_id in feat_ids:
            if feat_id not in self.feats:
                raise ValueError(f"Cannot create progression path: feat '{feat_id}' not found")
        
        self.progression_paths[path_name] = feat_ids
        self.path_categories[path_name] = category
    
    def get_progression_path(self, path_name: str) -> Optional[List[str]]:
        """Get a progression path by name"""
        return self.progression_paths.get(path_name)
    
    def get_progression_paths_by_category(self, category: str) -> Dict[str, List[str]]:
        """Get all progression paths in a specific category"""
        return {name: path for name, path in self.progression_paths.items() 
                if self.path_categories.get(name) == category}
    
    def get_available_feats(self, character) -> List[Feat]:
        """Get all feats that the character meets prerequisites for but doesn't already have"""
        character_feat_ids = {feat.id for feat in character.feats}
        available_feats = []
        
        for feat_id, feat in self.feats.items():
            if feat_id not in character_feat_ids and feat.check_prerequisites(character):
                available_feats.append(feat)
        
        return available_feats
    
    def get_feat_progression(self, character, path_name: str) -> List[Tuple[str, bool, List[str]]]:
        """Get progression status for a specific feat path
        
        Returns:
            List of tuples containing:
                - Feat ID
                - Boolean indicating if prerequisites are met
                - List of unmet prerequisites (empty if all met)
        """
        if path_name not in self.progression_paths:
            raise ValueError(f"Progression path '{path_name}' not found")
        
        character_feat_ids = {feat.id for feat in character.feats}
        progression_status = []
        
        for feat_id in self.progression_paths[path_name]:
            feat = self.feats[feat_id]
            if feat_id in character_feat_ids:
                # Character already has this feat
                progression_status.append((feat_id, True, []))
            else:
                # Check prerequisites
                meets_requirements = feat.check_prerequisites(character)
                unmet_requirements = feat.get_unmet_prerequisites(character)
                progression_status.append((feat_id, meets_requirements, unmet_requirements))
        
        return progression_status
    
    def get_next_feats_in_progressions(self, character) -> Dict[str, Tuple[Feat, bool, List[str]]]:
        """Get the next feat in each progression path for a character
        
        Returns:
            Dictionary mapping path names to tuples containing:
                - Next feat in the path
                - Boolean indicating if prerequisites are met
                - List of unmet prerequisites (empty if all met)
        """
        character_feat_ids = {feat.id for feat in character.feats}
        next_feats = {}
        
        for path_name, feat_ids in self.progression_paths.items():
            # Find the first feat in the path the character doesn't have
            for feat_id in feat_ids:
                if feat_id not in character_feat_ids:
                    feat = self.feats[feat_id]
                    meets_requirements = feat.check_prerequisites(character)
                    unmet_requirements = feat.get_unmet_prerequisites(character)
                    next_feats[path_name] = (feat, meets_requirements, unmet_requirements)
                    break
        
        return next_feats
    
    def recommend_next_feats(self, character, limit: int = 5) -> List[Tuple[Feat, str]]:
        """Recommend feats that the character should consider taking next
        
        Returns:
            List of tuples containing:
                - Feat object
                - Reason for recommendation
        """
        recommendations = []
        available_feats = self.get_available_feats(character)
        
        # First, check progression paths and recommend next steps
        character_feat_ids = {feat.id for feat in character.feats}
        for path_name, feat_ids in self.progression_paths.items():
            # Find the next feat in this path that the character doesn't have
            for feat_id in feat_ids:
                if feat_id not in character_feat_ids:
                    feat = self.feats[feat_id]
                    if feat.check_prerequisites(character):
                        recommendations.append((
                            feat, 
                            f"Next step in the {path_name} progression path"
                        ))
                    break  # Only recommend the next feat in each path
        
        # Then add other available feats based on character class, stats, etc.
        # Sort available feats by how well they match the character's profile
        remaining_slots = limit - len(recommendations)
        if remaining_slots > 0 and available_feats:
            # This is simplified - a real implementation would consider the character's
            # class, stats, playstyle, etc. to make more targeted recommendations
            for feat in available_feats[:remaining_slots]:
                if feat not in [r[0] for r in recommendations]:
                    recommendations.append((
                        feat,
                        f"Matches your character's abilities"
                    ))
        
        return recommendations[:limit]
        
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