# core_combat_rules.py

from typing import Literal, Optional
from dataclasses import dataclass

ActionType = Literal["Action", "Bonus Action", "Free Action", "Movement"]
TriggerType = Literal["Action Trigger", "Bonus Trigger", "Free Trigger"]

@dataclass
class Character:
    level: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    armor_dr: int
    armor_ac_bonus: int
    feat_dr_bonus: int = 0
    feat_ac_bonus: int = 0

    def max_hp(self):
        return self.level * (12 + self.constitution)

    def max_mp(self):
        return int((self.level * 8) + (self.intelligence * self.level))

    def total_dr(self):
        return self.armor_dr + self.feat_dr_bonus

    def total_ac(self):
        return 10 + self.dexterity + self.feat_ac_bonus


def calculate_attack_roll(attribute_mod: int, skill_score: int):
    return f"1d20 + {attribute_mod} + {skill_score // 3}"


def calculate_crit():
    return "Natural 20 = Critical Hit (double damage)"


def resolve_save(dc: int, modifier: int):
    return f"1d20 + {modifier} vs DC {dc}"


def calculate_save_dc(attribute: Optional[int] = None, skill: Optional[int] = None):
    if attribute is not None:
        return 10 + attribute
    elif skill is not None:
        return 10 + skill
    return None


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

def wild_shape_options(nature_score: int):
    cr_cap = (nature_score // 4) * 0.25
    return f"CR limit: {cr_cap} — player chooses from eligible beasts"

# Additional Systems

def xp_for_level(level: int) -> int:
    xp_table = {
        1: 0, 2: 1000, 3: 3000, 4: 6000, 5: 10000,
        6: 15000, 7: 21000, 8: 28000, 9: 36000, 10: 45000,
        11: 55000, 12: 66000, 13: 78000, 14: 91000, 15: 105000,
        16: 120000, 17: 136000, 18: 153000, 19: 171000, 20: 190000
    }
    return xp_table.get(level, -1)

def skill_point_cap(level: int) -> int:
    return level + 3

def skill_points_per_level(intelligence: int) -> int:
    return 4 + intelligence

def feat_count_at_level(level: int) -> int:
    return 7 + (level - 1) * 3 if level > 1 else 7
