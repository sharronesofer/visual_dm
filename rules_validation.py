# rules_validation.py

from flask import Blueprint, request, jsonify
import json
import logging

rules_validation_bp = Blueprint('rules_validation', __name__)
__all__ = ["rules_validation_bp"]

# -----------------------
# Utility: Load JSON safely
# -----------------------

def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {path}: {e}")
        return {}

skills = load_json("rules/skills.json")
feat_list = load_json("rules/feats.json")
feats = {feat.get("name"): feat for feat in feat_list if "name" in feat}
abilities = load_json("rules/abilities.json")

# -----------------------
# Character Creation Validation
# -----------------------

@rules_validation_bp.route('/validate_character_creation', methods=['POST'])
def validate_character_creation():
    data = request.json
    issues = []
    abilities_input = data.get("abilities", {})

    # Ability Score Validation
    for ability, score in abilities_input.items():
        if ability not in abilities:
            issues.append(f"Unknown ability: {ability}")
        elif not isinstance(score, int):
            issues.append(f"Invalid score for {ability}: must be int")

    # Feat Validation
    for feat in data.get("feats", []):
        if feat not in feats:
            issues.append(f"Unknown feat: {feat}")
            continue

        prereq = feats[feat].get("prerequisites", [])
        for condition in prereq:
            if condition.startswith("Str"):
                try:
                    required_str = int(condition[-2:])
                    if abilities_input.get("Strength", 0) < required_str:
                        issues.append(f"Missing prerequisite for {feat}: {condition}")
                except ValueError:
                    issues.append(f"Unparseable prerequisite for {feat}: {condition}")

    return jsonify({
        "valid": len(issues) == 0,
        "issues": issues
    })

# -----------------------
# Skill Check Resolution
# -----------------------

@rules_validation_bp.route('/resolve_skill_check', methods=['POST'])
def resolve_skill_check():
    data = request.json
    skill = data.get("skill")
    ability_score = data.get("ability_score", 10)
    modifiers = data.get("modifiers", [])
    dc = data.get("dc", 10)

    base = (ability_score - 10) // 2
    total = base + sum(modifiers)
    success = total >= dc

    return jsonify({
        "skill": skill,
        "base": base,
        "modifiers": modifiers,
        "total": total,
        "dc": dc,
        "success": success
    })

# -----------------------
# Combat Action Resolution
# -----------------------

@rules_validation_bp.route('/resolve_combat_action', methods=['POST'])
def resolve_combat_action():
    data = request.json
    attacker = data.get("attacker", {})
    defender = data.get("defender", {})
    roll = data.get("roll", 10)

    bab = attacker.get("base_attack_bonus", 0)
    strength_mod = attacker.get("strength_modifier", 0)
    attack_total = roll + bab + strength_mod
    ac = defender.get("armor_class", 10)
    hit = attack_total >= ac

    return jsonify({
        "roll": roll,
        "attack_total": attack_total,
        "defender_ac": ac,
        "hit": hit,
        "combat_narration": (
            f"Attack Roll: {roll} + {bab} (BAB) + {strength_mod} (STR) = "
            f"{attack_total} vs AC {ac} → {'HIT' if hit else 'MISS'}"
        )
    })

# -----------------------
# Rule Lookup (Abilities, Skills, Feats)
# -----------------------

@rules_validation_bp.route('/lookup_rule', methods=['GET'])
def lookup_rule():
    category = request.args.get("category")
    name = request.args.get("name", "").strip()

    if category == "skill":
        result = skills.get(name)
    elif category == "feat":
        result = feats.get(name)
    elif category == "ability":
        result = abilities.get(name)
    else:
        result = None

    if not result:
        return jsonify({"error": f"{name} not found in {category}"}), 404

    return jsonify(result)

# -----------------------
# Spell Lookup
# -----------------------

@rules_validation_bp.route('/lookup_spell', methods=['GET'])
def lookup_spell():
    level = request.args.get("level")
    name = request.args.get("name", "").strip().lower()

    if not level or not name:
        return jsonify({"error": "Missing spell level or name"}), 400

    path = f"rules/spells/{int(level)}.json"
    spells_data = load_json(path)

    for spell_name, spell_data in spells_data.items():
        if spell_name.lower() == name:
            return jsonify(spell_data)

    return jsonify({"error": f"Spell '{name}' not found at level {level}"}), 404
