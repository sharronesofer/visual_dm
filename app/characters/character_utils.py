import os
import json
import random
from firebase_admin import db
from app.characters.character_builder_class import CharacterBuilder
from datetime import datetime

# === PATH CONFIG ===
RULES_PATH = os.path.join(os.path.dirname(__file__), "../../rules_json")


# === JSON LOADERS ===
def load_json(file):
    path = os.path.join(RULES_PATH, file)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_race_data():
    return load_json("races.json")

def load_feat_data():
    return load_json("feats.json")

def load_skill_list():
    return load_json("skills.json").get("skills", [])

def load_starter_kits():
    return load_json("starter_kits.json")


# === CHARACTER CREATION ===
def build_character_from_input(input_data):
    """
    Constructs and finalizes a full character using the CharacterBuilder class.
    Input must include: race, stats, feats, skills, and optional starter_kit.
    """
    race_data = load_race_data()
    feat_data = load_feat_data()
    skill_list = load_skill_list()
    starter_kits = load_starter_kits()

    builder = CharacterBuilder(race_data, feat_data, skill_list)

    try:
        builder.set_race(input_data["race"])
        for stat, value in input_data.get("stats", {}).items():
            builder.assign_stat(stat, value)

        for feat in input_data.get("feats", []):
            builder.add_feat(feat)

        for skill in input_data.get("skills", []):
            builder.assign_skill(skill)

        if "starter_kit" in input_data:
            builder.apply_starter_kit(input_data["starter_kit"], starter_kits)

    except ValueError as e:
        raise ValueError(f"Character build error: {e}")

    if not builder.is_valid():
        raise ValueError("Character build failed validation")

    return builder.finalize()


# === TEMP CHARACTER STORAGE ===
def save_partial_character_data(player_id, field, value):
    """
    Saves a single field to the temp character entry for a player (during creation steps).
    """
    ref = db.reference(f"/temp_characters/{player_id}")
    data = ref.get() or {}
    data[field] = value
    ref.set(data)


# === GENERAL UTILITIES ===
def parse_coords(loc):
    try:
        return tuple(map(int, loc.split("_")))
    except Exception:
        return None, None

def perform_skill_check(character, skill, dc=12):
    SKILL_TO_ABILITY = {
        "stealth": "DEX", "pickpocket": "DEX", "intimidate": "CHA", "diplomacy": "CHA",
        "persuasion": "CHA", "deception": "CHA", "perception": "WIS", "insight": "WIS", "arcana": "INT"
    }
    ability = SKILL_TO_ABILITY.get(skill.lower(), "INT")
    modifier = (character.get(ability, 10) - 10) // 2
    if skill.lower() in [s.lower() for s in character.get("skills", [])]:
        modifier += 2
    roll = random.randint(1, 20)
    total = roll + modifier
    return {
        "skill": skill,
        "roll": roll,
        "modifier": modifier,
        "total": total,
        "success": total >= dc,
        "dc": dc
    }

def save_character_to_firebase(character_id: str, character_data: dict, is_npc=False):
    path = f"/npcs/{character_id}" if is_npc else f"/players/{character_id}"
    db.reference(path).set(character_data)

def load_character_from_firebase(character_id: str, is_npc=False):
    path = f"/npcs/{character_id}" if is_npc else f"/players/{character_id}"
    return db.reference(path).get()