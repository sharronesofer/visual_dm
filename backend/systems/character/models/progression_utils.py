from typing import Dict, Any
from backend.systems.character.models import Character, Feat

def calculate_experience_needed(level: int) -> int:
    """Calculate the experience needed for the next level."""
    return 300 * (2 ** (level - 1))

def process_level_up(character: Character) -> Dict[str, Any]:
    """Process a character's level up."""
    try:
        # Calculate new hit points
        hp_gain = calculate_hit_points(character, is_level_up=True)
        character.max_hit_points += hp_gain
        character.hit_points = character.max_hit_points
        
        # Update level and proficiency bonus
        character.level += 1
        update_proficiency_bonus(character)
        
        return {
            "success": True,
            "level": character.level,
            "hp_gain": hp_gain
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def apply_ability_score_increase(character: Character, ability: str) -> Dict[str, Any]:
    """Apply an ability score increase."""
    try:
        if ability not in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            raise ValueError(f"Invalid ability: {ability}")
        
        current_score = getattr(character, ability)
        if current_score >= 20:
            return {"success": False, "error": "Maximum ability score reached"}
        
        setattr(character, ability, current_score + 1)
        return {"success": True, ability: current_score + 1}
    except Exception as e:
        return {"success": False, "error": str(e)}

def select_feat(character: Character, feat: Feat) -> Dict[str, Any]:
    """Select a feat for a character."""
    try:
        if not character.can_take_feat(feat):
            return {"success": False, "error": "Feat prerequisites not met"}
        
        character.feats.append(feat)
        return {"success": True, "feat": feat.name}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_proficiency_bonus(character: Character) -> None:
    """Update a character's proficiency bonus based on level."""
    character.proficiency_bonus = 2 + ((character.level - 1) // 4)

def calculate_hit_points(character: Character, is_level_up: bool = False) -> int:
    """Calculate hit points for a character."""
    base_hp = 10 if character.class_name == "Fighter" else 8
    con_mod = (character.constitution - 10) // 2
    
    if is_level_up:
        return base_hp + con_mod
    else:
        return base_hp + (con_mod * character.level) 