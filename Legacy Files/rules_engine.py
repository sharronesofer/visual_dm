import json
import os
from firebase_admin import db
from datetime import datetime
import random

# === Helper: Load JSON ===
def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

# === Load Core Rules ===
skills = load_json("rules/skills.json")
classes = load_json("rules/classes.json")
feats = load_json("rules/feats.json")
abilities = load_json("rules/abilities.json")

# === Validate Character Creation ===
def validate_character_creation(data):
    issues = []
    name = data.get("name")
    race = data.get("race")
    cls = data.get("class")
    feats_input = data.get("feats", [])
    abilities_input = data.get("abilities", {})

    # Validate class
    class_data = classes.get(cls)
    if not class_data:
        issues.append(f"Invalid class: {cls}")

    # Validate abilities
    for ability, score in abilities_input.items():
        if ability not in abilities:
            issues.append(f"Unknown ability: {ability}")
        elif not isinstance(score, int):
            issues.append(f"Invalid score for {ability}: must be int")

    # Validate feats
    for feat in feats_input:
        if feat not in feats:
            issues.append(f"Unknown feat: {feat}")
        else:
            prereq = feats[feat].get("prerequisites", [])
            for condition in prereq:
                if condition.startswith("Str") and abilities_input.get("Strength", 0) < int(condition[-2:]):
                    issues.append(f"Missing prerequisite for {feat}: {condition}")
                # Additional parsing logic can be added here

    return {
        "character": name,
        "valid": len(issues) == 0,
        "issues": issues
    }

# === Resolve Skill Check ===
def resolve_skill_check(skill, ability_score, modifiers, dc):
    base = (ability_score - 10) // 2
    total = base + sum(modifiers)
    return {
        "skill": skill,
        "base": base,
        "modifiers": modifiers,
        "total": total,
        "dc": dc,
        "success": total >= dc
    }

# === Resolve Combat Action ===
def resolve_combat_action(attacker, defender, roll):
    bab = attacker.get("base_attack_bonus", 0)
    strength = attacker.get("strength_modifier", 0)
    attack_total = roll + bab + strength
    ac = defender.get("armor_class", 10)
    hit = attack_total >= ac
    return {
        "roll": roll,
        "base_attack_bonus": bab,
        "strength_modifier": strength,
        "attack_total": attack_total,
        "defender_ac": ac,
        "hit": hit,
        "combat_narration": f"Attack Roll: {roll} + {bab} (BAB) + {strength} (STR) = {attack_total} vs AC {ac} → {'HIT' if hit else 'MISS'}"
    }


# === Lookup Rule (Skill, Class, Feat, etc.) ===
def lookup_rule(category, name):
    name = name.strip()
    if category == "skill":
        return skills.get(name)
    elif category == "class":
        return classes.get(name)
    elif category == "feat":
        return feats.get(name)
    elif category == "ability":
        return abilities.get(name)
    return None

# === Lookup Spell ===
def lookup_spell(level, name):
    try:
        path = f"rules/spells/{int(level)}.json"
        spells = load_json(path)
        name_lower = name.strip().lower()
        for key, value in spells.items():
            if key.lower() == name_lower:
                return value
        return None
    except Exception as e:
        print(f"Spell lookup failed: {e}")
        return None
    
# --- Skill Intent Detection Helper ---
def detect_skill_action(text):
    text = text.lower()
    skill_map = {
        "stealth": ["sneak", "hide", "move silently", "avoid detection"],
        "pickpocket": ["steal", "lift", "pick pocket", "swipe"],
        "intimidate": ["intimidate", "threaten", "scare", "bully"],
        "diplomacy": ["persuade", "negotiate", "convince", "diplomacy", "talk down"]
    }

    for skill, keywords in skill_map.items():
        if any(kw in text for kw in keywords):
            return skill
    return None

# === WORLD STATE TRUTH EVENT LOGGING ===
def log_world_event(event_data):
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    event_data["event_id"] = event_id
    event_data["timestamp"] = datetime.utcnow().isoformat()
    ref = db.reference(f"/global_state/world_log/{event_id}")
    ref.set(event_data)
    return event_data

# === BELIEF GENERATION LOGIC ===
def distort_summary(summary):
    return summary.replace("was", "may have been").replace("at", "somewhere near")

def fabricate_alternate(event_data):
    return f"Someone claims {event_data.get('summary', 'something strange')} — but it sounds suspicious."

def generate_npc_belief(npc_name, event_data):
    trust_level = random.randint(1, 5)
    roll = random.random()
    if roll < trust_level / 5:
        accuracy = "accurate"
        belief_summary = event_data["summary"]
    elif roll < 0.8:
        accuracy = "partial"
        belief_summary = distort_summary(event_data["summary"])
    else:
        accuracy = "false"
        belief_summary = fabricate_alternate(event_data)

    return {
        "belief_summary": belief_summary,
        "accuracy": accuracy,
        "source": "world_log",
        "trust_level": trust_level,
        "heard_at": event_data.get("poi", "unknown")
    }

# === REGION-WIDE NPC SYNC ===
def sync_event_beliefs(region_name, event_data):
    poi_ref = db.reference(f"/poi_state/{region_name}")
    pois = poi_ref.get() or {}

    npc_belief_count = 0
    for poi_id, poi in pois.items():
        npcs = poi.get("npcs_present", [])
        for npc_name in npcs:
            belief = generate_npc_belief(npc_name, event_data)
            belief_ref = db.reference(f"/npc_knowledge/{npc_name}/beliefs/{event_data['event_id']}")
            belief_ref.set(belief)
            npc_belief_count += 1

    return npc_belief_count