# rules_data.py

from flask import Blueprint, jsonify
import json
import logging
import random

rules_data_bp = Blueprint('rules_data', __name__)
__all__ = ["rules_data_bp"]

# -----------------------
# Utility: Load JSON safely
# -----------------------

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {path}: {e}")
        return {}

# -----------------------
# Feats
# -----------------------

@rules_data_bp.route('/feats', methods=['GET'])
def get_all_feats():
    feats = load_json("rules/feats.json")
    return jsonify(feats or [])

@rules_data_bp.route('/feats_by_category', methods=['GET'])
def get_feats_by_category():
    feats = load_json("rules/feats.json")
    groups = {}
    for feat in feats or []:
        category = feat.get("category", "Misc")
        groups.setdefault(category, []).append(feat)
    return jsonify(groups)

@rules_data_bp.route('/feats_index', methods=['GET'])
def get_feats_index():
    feats_index = load_json("rules/feats_index.json")
    return jsonify(feats_index or {})

# -----------------------
# Skills & Ability Rolls
# -----------------------

@rules_data_bp.route('/skills', methods=['GET'])
def get_all_skills():
    skills = load_json("rules/skills.json")
    return jsonify(skills or {})

@rules_data_bp.route('/ability_scores/4d6', methods=['GET'])
def roll_ability_scores():
    results = []
    for _ in range(6):
        rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
        total = 19 if rolls == [6, 6, 6, 6] else sum(rolls[:3])
        results.append({"rolls": rolls, "score": total})
    return jsonify({"method": "4d6-drop-lowest", "results": results})

# -----------------------
# Starter Kits & Equipment
# -----------------------

@rules_data_bp.route('/starting_kits', methods=['GET'])
def get_starting_kits():
    kits = load_json("rules/starter_kits.json")
    return jsonify(kits or {})

@rules_data_bp.route('/equipment', methods=['GET'])
def get_equipment():
    equipment = load_json("rules/equipment.json")
    return jsonify(equipment or {})

# -----------------------
# Races
# -----------------------

@rules_data_bp.route('/races', methods=['GET'])
def get_all_races():
    races = load_json("rules/races.json")
    return jsonify(races or {})

# -----------------------
# Spells
# -----------------------

@rules_data_bp.route('/spells/<int:level>', methods=['GET'])
def get_spells_by_level(level):
    spells = load_json(f"rules/spells/{level}.json")
    if spells:
        return jsonify(spells)
    return jsonify({"error": f"Spells for level {level} not found."}), 404
