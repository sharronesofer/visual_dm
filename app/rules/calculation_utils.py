#This utility contains formulae and rules for core game mechanics, including:
#Attack rolls
#Saving throws
#Movement rules
#Advantage/disadvantage resolution
#Wild Shape CR limits
#It supports the combat, character, rulebook, and shapeshifting systems.

from app.core.utils.json_utils import load_json
from typing import Dict, Any

def calculate_attack_roll(attribute_mod: int, skill_score: int):
    return f"1d20 + {attribute_mod} + {skill_score // 3}"

def calculate_crit():
    return "Natural 20 = Critical Hit (double damage)"

def calculate_save_dc(attribute_value=None, skill_value=None):
    """
    Returns calculated save DC:
    - Attribute: 10 + (attribute modifier)
    - Skill: 10 + (skill // 3)
    Defaults to DC 10 if both are missing.
    """
    if attribute_value is not None:
        return 10 + ((attribute_value - 10) // 2)
    elif skill_value is not None:
        return 10 + (skill_value // 3)
    else:
        return 10

def movement_rule(allied: bool):
    if allied:
        return "Can move through ally square at half speed"
    return "Must pass Acrobatics vs target's Athletics to move through enemy space"

def resistance_rule():
    return "Resistance = 1/2 damage taken"

def vulnerability_rule():
    return "Vulnerability = double damage taken"

def advantage_rule():
    return "Advantage/disadvantage cancel 1:1, but multiple stacks can override"

def wild_shape_options(nature_score):
    max_cr = round(nature_score / 4, 2)
    all_monsters = load_json("monsters.json") or []
    eligible = []

    for monster in all_monsters:
        cr = monster.get("estimated_cr", 0)
        tags = monster.get("tags", [])
        if cr <= max_cr and "animal" in [t.lower() for t in tags]:
            eligible.append(monster)

    return eligible

def calculate_ability_modifier(score: int) -> int:
    """Calculate ability modifier from ability score."""
    return (score - 10) // 2

def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on level."""
    return 2 + ((level - 1) // 4)

def calculate_skill_modifier(ability_score: int, is_proficient: bool = False, proficiency_bonus: int = 0) -> int:
    """Calculate skill modifier."""
    ability_modifier = calculate_ability_modifier(ability_score)
    return ability_modifier + (proficiency_bonus if is_proficient else 0)

def calculate_saving_throw_dc(ability_modifier: int, proficiency_bonus: int = 0) -> int:
    """Calculate saving throw DC."""
    return 8 + ability_modifier + proficiency_bonus

def calculate_attack_bonus(ability_modifier: int, proficiency_bonus: int = 0) -> int:
    """Calculate attack bonus."""
    return ability_modifier + proficiency_bonus

def calculate_damage_bonus(ability_modifier: int, is_ranged: bool = False) -> int:
    """Calculate damage bonus."""
    return ability_modifier if not is_ranged else 0

def calculate_skill_check_difficulty(difficulty: str) -> int:
    """Calculate DC for skill checks based on difficulty."""
    difficulties = {
        "Very Easy": 5,
        "Easy": 10,
        "Medium": 15,
        "Hard": 20,
        "Very Hard": 25,
        "Nearly Impossible": 30
    }
    return difficulties.get(difficulty, 15)

def calculate_combat_round_time(actions: int, bonus_actions: int = 0, reactions: int = 0) -> float:
    """Calculate time taken for a combat round in seconds."""
    base_time = 6.0  # 6 seconds per round
    action_time = actions * 2.0
    bonus_action_time = bonus_actions * 1.0
    reaction_time = reactions * 0.5
    return base_time + action_time + bonus_action_time + reaction_time