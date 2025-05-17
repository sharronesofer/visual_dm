"""
Feat Progression Paths

This module defines progression paths for feats, creating logical advancement
sequences for character development.
"""

from typing import Dict, List, Set, Optional, Tuple
from .feats import FeatManager, PowerLevel, Feat, FeatType
from .feat_templates import ALL_FEATS

# Define progression path categories
class ProgressionCategory:
    COMBAT = "combat"
    MAGIC = "magic"
    SKILLS = "skills"
    SOCIAL = "social"
    CLASS_SPECIFIC = "class_specific"
    GENERAL = "general"

class FeatProgression:
    """Represents a progression path for feats"""
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 feat_ids: List[str],
                 category: str,
                 tags: List[str] = None):
        self.name = name
        self.description = description
        self.feat_ids = feat_ids
        self.category = category
        self.tags = tags or []
    
    def validate(self, feat_manager: FeatManager) -> Tuple[bool, List[str]]:
        """Validates that this progression path makes logical sense
        
        Args:
            feat_manager: FeatManager instance with registered feats
            
        Returns:
            Tuple containing:
                - Boolean indicating if progression is valid
                - List of string messages describing issues (if any)
        """
        issues = []
        
        # Check that all feats exist
        for feat_id in self.feat_ids:
            if not feat_manager.get_feat(feat_id):
                issues.append(f"Feat '{feat_id}' not found in feat manager")
        
        if issues:
            return (False, issues)
            
        # Check that power levels generally increase
        prev_power = None
        prev_level = 0
        for feat_id in self.feat_ids:
            feat = feat_manager.get_feat(feat_id)
            if hasattr(feat.prerequisites, "power_level"):
                power = feat.prerequisites.power_level
            else:
                power = PowerLevel.MEDIUM
                
            level = feat.prerequisites.level_requirement
            
            if prev_power and power.value < prev_power.value:
                issues.append(
                    f"Power level decreases from {prev_power.name} to {power.name} "
                    f"between feats in progression"
                )
                
            if level < prev_level:
                issues.append(
                    f"Level requirement decreases from {prev_level} to {level} "
                    f"between feats in progression"
                )
                
            prev_power = power
            prev_level = level
        
        # Check for missing prerequisites within progression
        for i, feat_id in enumerate(self.feat_ids):
            if i > 0:  # Skip first feat
                feat = feat_manager.get_feat(feat_id)
                prev_feat_id = self.feat_ids[i - 1]
                
                # If the previous feat in progression isn't a prerequisite,
                # flag it as a potential issue (but not a blocker)
                if not feat.prerequisites.feat_requirements or prev_feat_id not in feat.prerequisites.feat_requirements:
                    issues.append(
                        f"Warning: Feat '{feat_id}' in progression does not have "
                        f"'{prev_feat_id}' as a prerequisite"
                    )
        
        # If only warnings, still valid but with issues
        return (True, issues) if all("Warning:" in issue for issue in issues) else (False, issues)

# Dictionary of predefined progression paths
PROGRESSION_PATHS: Dict[str, FeatProgression] = {}

def register_progression_path(progression: FeatProgression) -> bool:
    """Register a progression path
    
    Args:
        progression: FeatProgression instance to register
        
    Returns:
        Boolean indicating success
    """
    if progression.name in PROGRESSION_PATHS:
        return False
        
    PROGRESSION_PATHS[progression.name] = progression
    return True

def get_progression_path(name: str) -> Optional[FeatProgression]:
    """Get a progression path by name"""
    return PROGRESSION_PATHS.get(name)

def get_progressions_by_category(category: str) -> List[FeatProgression]:
    """Get all progression paths in a specific category"""
    return [p for p in PROGRESSION_PATHS.values() if p.category == category]

def get_progressions_by_tag(tag: str) -> List[FeatProgression]:
    """Get all progression paths with a specific tag"""
    return [p for p in PROGRESSION_PATHS.values() if tag in p.tags]

def get_progressions_containing_feat(feat_id: str) -> List[FeatProgression]:
    """Get all progression paths that include a specific feat"""
    return [p for p in PROGRESSION_PATHS.values() if feat_id in p.feat_ids]

def initialize_progression_paths(feat_manager: FeatManager):
    """Initialize and register all progression paths"""
    
    # Combat progression paths
    register_progression_path(FeatProgression(
        name="Two-Weapon Fighting Mastery",
        description="Master the art of fighting with two weapons simultaneously",
        feat_ids=["two_weapon_fighting", "improved_two_weapon_fighting", "greater_two_weapon_fighting", "two_weapon_mastery"],
        category=ProgressionCategory.COMBAT,
        tags=["melee", "dual-wielding"]
    ))
    
    register_progression_path(FeatProgression(
        name="Archery Expertise",
        description="Become an expert with bows and ranged weapons",
        feat_ids=["point_blank_shot", "precise_shot", "rapid_shot", "many_shot", "pinpoint_targeting"],
        category=ProgressionCategory.COMBAT,
        tags=["ranged", "bow"]
    ))
    
    register_progression_path(FeatProgression(
        name="Defensive Combat",
        description="Focus on defensive techniques and survivability",
        feat_ids=["dodge", "mobility", "combat_expertise", "improved_combat_expertise", "defensive_stance"],
        category=ProgressionCategory.COMBAT,
        tags=["defense", "survival"]
    ))
    
    # Magic progression paths
    register_progression_path(FeatProgression(
        name="Spell Penetration",
        description="Overcome spell resistance and enhance magical power",
        feat_ids=["spell_focus", "greater_spell_focus", "spell_penetration", "greater_spell_penetration", "epic_spell_penetration"],
        category=ProgressionCategory.MAGIC,
        tags=["spellcaster", "offensive"]
    ))
    
    register_progression_path(FeatProgression(
        name="Metamagic Mastery",
        description="Master the art of shaping and enhancing spells",
        feat_ids=["extend_spell", "empower_spell", "maximize_spell", "quicken_spell", "metamagic_mastery"],
        category=ProgressionCategory.MAGIC,
        tags=["spellcaster", "versatility"]
    ))
    
    # Skill-focused paths
    register_progression_path(FeatProgression(
        name="Stealth Specialist",
        description="Become a master of stealth and subterfuge",
        feat_ids=["stealthy", "improved_stealth", "hide_in_plain_sight", "shadow_master"],
        category=ProgressionCategory.SKILLS,
        tags=["rogue", "stealth"]
    ))
    
    register_progression_path(FeatProgression(
        name="Persuasive Expert",
        description="Excel at persuasion and social manipulation",
        feat_ids=["persuasive", "negotiator", "silver_tongue", "legendary_diplomat"],
        category=ProgressionCategory.SOCIAL,
        tags=["diplomacy", "charisma"]
    ))
    
    # Class-specific paths
    register_progression_path(FeatProgression(
        name="Barbarian Rage",
        description="Enhance the barbarian's rage ability",
        feat_ids=["extra_rage", "extended_rage", "mighty_rage", "tireless_rage", "terrifying_rage"],
        category=ProgressionCategory.CLASS_SPECIFIC,
        tags=["barbarian", "rage"]
    ))
    
    register_progression_path(FeatProgression(
        name="Cleric Channel",
        description="Enhance the cleric's channel energy ability",
        feat_ids=["improved_channel", "selective_channel", "quick_channel", "divine_channel"],
        category=ProgressionCategory.CLASS_SPECIFIC,
        tags=["cleric", "healing"]
    ))
    
    # Validate all progression paths
    for name, progression in list(PROGRESSION_PATHS.items()):
        is_valid, issues = progression.validate(feat_manager)
        if not is_valid:
            print(f"Warning: Progression path '{name}' has validation issues:")
            for issue in issues:
                print(f"  - {issue}")

# Initialize manager and progression paths when module is imported
feat_manager = FeatManager()
for feat_id, feat in ALL_FEATS.items():
    feat_manager.register_feat(feat)

initialize_progression_paths(feat_manager) 