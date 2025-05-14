#This module handles rule logic around:
#DR calculation (from equipment and feats)
#Equipment item validation
#JSON loading for static rule files
#Core combat actions
#It integrates with rules, equipment, feats, combat, and validation systems.

import json
import logging
from app.core.utils.json_utils import load_json
from app.equipment.inventory_utils import load_equipment_rules
from typing import Dict, List, Optional

def calculate_dr(equipment_list, feats=None):
    """
    Calculates total DR based on equipped armor and feat-based bonuses.
    `equipment_list`: list of item names (strings)
    `feats`: optional list of feat dicts or names
    """
    equipment_rules = load_equipment_rules()
    total_dr = 0

    # Equipment-based DR
    for item in equipment_list:
        if item in equipment_rules.get('armor_types', {}):
            total_dr += equipment_rules['armor_types'][item].get('dr', 0)

    # Feat-based DR
    if feats:
        for feat in feats:
            if isinstance(feat, dict):
                if 'dr_bonus' in feat:
                    total_dr += feat['dr_bonus']
            elif isinstance(feat, str):
                # Look up feat in feats.json
                feat_data = load_json('data/rules/feats.json')
                if feat in feat_data and 'dr_bonus' in feat_data[feat]:
                    total_dr += feat_data[feat]['dr_bonus']

    return total_dr

def calculate_hp(constitution, level, hit_dice):
    """Calculate maximum hit points based on constitution, level, and hit dice."""
    base_hp = hit_dice + constitution
    return base_hp + (level - 1) * (hit_dice // 2 + constitution)

def calculate_ac(dexterity, equipment_list):
    """Calculate armor class based on dexterity and equipped armor."""
    base_ac = 10 + (dexterity - 10) // 2
    equipment_rules = load_equipment_rules()
    
    for item in equipment_list:
        if item in equipment_rules.get('armor_types', {}):
            base_ac = max(base_ac, equipment_rules['armor_types'][item].get('ac', 0))
            
    return base_ac

def validate_equipment_item(item_name):
    """Validate if an equipment item exists in the rules."""
    equipment_rules = load_equipment_rules()
    return item_name in equipment_rules.get('weapon_types', {}) or \
           item_name in equipment_rules.get('armor_types', {})

def load_core_actions():
    """Load core combat actions from JSON."""
    return load_json('data/rules/core_actions.json')

def load_rules():
    """Load all rule sets from JSON files."""
    return {
        'equipment': load_equipment_rules(),
        'feats': load_json('data/rules/feats.json'),
        'skills': load_json('data/rules/skills.json'),
        'spells': load_json('data/rules/spells.json')
    }

def apply_combat_rules(attacker: Dict, defender: Dict, weapon: Optional[Dict] = None) -> Dict:
    """Apply combat rules to an attack."""
    # Calculate hit chance
    hit_bonus = attacker.get('stats', {}).get('dexterity', 10) - 10
    if weapon:
        hit_bonus += weapon.get('hit_bonus', 0)
        
    # Calculate damage
    base_damage = weapon.get('damage', '1d4') if weapon else '1d4'
    damage_bonus = attacker.get('stats', {}).get('strength', 10) - 10
    
    return {
        'hit_bonus': hit_bonus,
        'damage': base_damage,
        'damage_bonus': damage_bonus
    }

def apply_magic_rules(caster: Dict, spell: Dict, target: Optional[Dict] = None) -> Dict:
    """Apply magic rules to a spell cast."""
    # Calculate spell DC
    spell_dc = 8 + caster.get('stats', {}).get('intelligence', 10) - 10
    
    # Calculate spell damage/healing
    magnitude = spell.get('magnitude', 0)
    level_bonus = (caster.get('level', 1) - 1) * spell.get('scaling', 0)
    
    return {
        'dc': spell_dc,
        'magnitude': magnitude + level_bonus
    }

def apply_economy_rules(item: Dict, region: Optional[Dict] = None) -> Dict:
    """Apply economy rules to an item."""
    base_cost = item.get('cost', 0)
    if region:
        # Apply regional modifiers
        scarcity = region.get('resources', {}).get(item.get('type', ''), 1.0)
        base_cost = int(base_cost * scarcity)
        
    return {
        'cost': base_cost,
        'haggle_dc': 10 + base_cost // 10
    }

def apply_social_rules(actor: Dict, target: Dict, action: str) -> Dict:
    """Apply social rules to an interaction."""
    # Calculate base DC
    base_dc = 10
    if action == 'persuade':
        skill = 'charisma'
    elif action == 'intimidate':
        skill = 'strength'
    elif action == 'deceive':
        skill = 'intelligence'
    else:
        skill = 'wisdom'
        
    bonus = actor.get('stats', {}).get(skill, 10) - 10
    
    return {
        'dc': base_dc + target.get('level', 1),
        'bonus': bonus
    }

def get_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on level."""
    return 2 + (level - 1) // 4
