from flask import Blueprint, jsonify, request
import random
import json
import logging

rules_validation_bp = Blueprint('rules_validation', __name__)

# Utility: Load JSON safely
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {path}: {e}")
        return {}

skills = load_json("rules_json/skills.json")
feat_list = load_json("rules_json/feats.json")
feats = {feat.get("name"): feat for feat in feat_list if "name" in feat}
abilities = load_json("rules_json/abilities.json")

# -----------------------
# Feats Endpoints
# -----------------------

rules_validation_bp.route('/feats', methods=['GET'])
def get_all_feats():
    return jsonify(feat_list or [])

rules_validation_bp.route('/feats_by_category', methods=['GET'])
def get_feats_by_category():
    groups = {}
    for feat in feat_list or []:
        category = feat.get("category", "Misc")
        groups.setdefault(category, []).append(feat)
    return jsonify(groups)

@rules_validation_bp.route('/feats_index', methods=['GET'])
def get_feats_index():
    feats_index = load_json("rules/feats_index.json")
    return jsonify(feats_index or {})

# -----------------------
# Skills Endpoint
# -----------------------

@rules_validation_bp.route('/skills', methods=['GET'])
def get_all_skills():
    return jsonify(skills or {})

# -----------------------
# Ability Score Rolls
# -----------------------

@rules_validation_bp.route('/ability_scores/3d4', methods=['GET'])
def roll_ability_scores():
    results = []
    for _ in range(6):
        rolls = sorted([random.randint(1, 4) for _ in range(3)], reverse=True)
        total = 9 if rolls == [4, 4, 4] else sum(rolls[:2])
        results.append({"rolls": rolls, "score": total})
    return jsonify({"method": "3d4-special-rules", "results": results})

# -----------------------
# Character Creation Validation
# -----------------------

@rules_validation_bp.route('/validate_character_creation', methods=['POST'])
def validate_character_creation():
    data = request.json
    issues = []
    abilities_input = data.get("abilities", {})

    for ability, score in abilities_input.items():
        if ability not in abilities:
            issues.append(f"Unknown ability: {ability}")
        elif not isinstance(score, int):
            issues.append(f"Invalid score for {ability}: must be int")

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