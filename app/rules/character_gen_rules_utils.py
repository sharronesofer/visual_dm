#This module loads static rule JSON files used in character creation, including:
#Races
#Skills
#Feats
#Starter kits
#It provides essential data for NPCBuilder, CharacterBuilder, and rules validation.

import os, json
import os
import json
from firebase_admin import db
import logging
from collections import Counter
from app.core.utils.json_utils import load_json
from typing import Dict, List
import math

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
RULES_PATH = os.path.join(PROJECT_ROOT, "rules_json")

def load_race_data():
    return load_json("races.json")

def load_skill_list():
    from pprint import pprint
    path = os.path.join(RULES_PATH, "skills.json")
    print("📂 Reading skills.json from:", path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            print("✅ Loaded JSON successfully. Keys:")
            pprint(list(data.keys()))  # Print the actual keys
            return list(data.keys())
    except Exception as e:
        print("❌ Failed to load skills.json:", e)
        return []

def load_feat_data():
    feats = load_json("feats.json")
    return {feat["name"]: feat for feat in feats if "name" in feat}

def load_starter_kits():
    return load_json("starter_kits.json")


def validate_character_creation(character):
    """
    Validates character object at finalization step.
    Checks:
    - Ability name validity
    - Feat prerequisites
    - Skill rank caps
    - Feat conflicts
    """
    errors = []
    attributes = character.get("attributes", {})
    feats = character.get("feats", [])
    skills = character.get("skills", [])
    level = character.get("level", 1)

    # === Validate attributes ===
    valid_attributes = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    for attr in attributes:
        if attr not in valid_attributes:
            errors.append(f"Invalid attribute: {attr}")
        elif not isinstance(attributes[attr], int):
            errors.append(f"Attribute {attr} must be an integer")
        elif attributes[attr] < 3 or attributes[attr] > 20:
            errors.append(f"Attribute {attr} must be between 3 and 20")

    # === Validate skills ===
    max_skill = level + 3
    if isinstance(skills, list):
        skills = Counter(skills)
    elif not isinstance(skills, dict):
        errors.append("Skills must be a list or dictionary")

    for skill, rank in skills.items():
        if not isinstance(rank, int):
            errors.append(f"Skill rank for {skill} must be an integer")
        elif rank > max_skill:
            errors.append(f"Skill '{skill}' exceeds max allowed: {rank} > {max_skill}")

    # === Validate feats ===
    all_feats = load_json("feats.json") or []
    known_feat_ids = [f.get("id") or f.get("name") for f in all_feats]

    for feat_id in feats:
        if feat_id not in known_feat_ids:
            errors.append(f"Unknown feat: {feat_id}")
            continue

        # Feat prerequisite parsing
        for feat in all_feats:
            if feat.get("id") == feat_id or feat.get("name") == feat_id:
                prereq = feat.get("prerequisites", "")
                if isinstance(prereq, str) and "Str" in prereq:
                    try:
                        required = int(prereq.replace("Str", "").strip())
                        if attributes.get("STR", 0) < required:
                            errors.append(f"Feat '{feat_id}' requires STR {required}")
                    except Exception:
                        errors.append(f"Invalid STR prereq format in feat: {feat_id}")

    # === Validate level ===
    if not isinstance(level, int):
        errors.append("Level must be an integer")
    elif level < 1 or level > 20:
        errors.append("Level must be between 1 and 20")

    # === Validate race ===
    valid_races = load_race_data().keys()
    if character.get("race") not in valid_races:
        errors.append(f"Invalid race: {character.get('race')}")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def basic_schema_check(character):
    """
    Validates the basic schema of a character object.
    Returns (is_valid, missing_fields)
    """
    required_fields = [
        "character_name",
        "race",
        "background",
        "attributes",
        "skills",
        "feats",
        "level"
    ]
    missing = [field for field in required_fields if field not in character]
    if missing:
        return False, missing
    return True, []

def calculate_ability_modifiers(ability_scores: Dict[str, int]) -> Dict[str, int]:
    """Calculate ability modifiers from ability scores."""
    return {
        ability: math.floor((score - 10) / 2)
        for ability, score in ability_scores.items()
    }

def get_class_hit_die(class_name: str) -> int:
    """Get the hit die value for a given class."""
    hit_die_map = {
        'barbarian': 12,
        'fighter': 10,
        'paladin': 10,
        'ranger': 10,
        'monk': 8,
        'rogue': 8,
        'bard': 8,
        'cleric': 8,
        'druid': 8,
        'warlock': 8,
        'wizard': 6,
        'sorcerer': 6
    }
    return hit_die_map.get(class_name.lower(), 8)

def roll_hit_points(hit_die: int, constitution_modifier: int) -> int:
    """Roll hit points for level up."""
    from random import randint
    return max(1, randint(1, hit_die) + constitution_modifier)

def get_starting_proficiencies(class_name: str) -> Dict[str, List[str]]:
    """Get starting proficiencies for a given class."""
    # This would typically load from class data
    return {
        'armor': [],
        'weapons': [],
        'tools': [],
        'saving_throws': [],
        'skills': []
    }

def get_starting_equipment(class_name: str) -> List[str]:
    """Get starting equipment for a given class."""
    # This would typically load from class data
    return []

def calculate_hit_points(class_name: str, constitution_modifier: int, level: int) -> int:
    """Calculate hit points based on class, constitution modifier, and level."""
    hit_die = get_class_hit_die(class_name)
    
    if level == 1:
        return hit_die + constitution_modifier
    
    # First level is maximum
    total = hit_die + constitution_modifier
    
    # Subsequent levels roll
    for _ in range(level - 1):
        total += max(1, (hit_die // 2 + 1) + constitution_modifier)  # Using average
    
    return total

def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus based on character level."""
    return 2 + ((level - 1) // 4)
