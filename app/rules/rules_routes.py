from flask import Blueprint, jsonify
import random
import json
import logging

rules_bp = Blueprint('rules_data', __name__)

# Utility: Load JSON safely
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {path}: {e}")
        return {}

# -----------------------
# Feats Endpoints
# -----------------------

@rules_bp.route('/feats', methods=['GET'])
def get_all_feats():
    feats = load_json("rules_json/feats.json")
    return jsonify(feats or [])

@rules_bp.route('/feats_by_category', methods=['GET'])
def get_feats_by_category():
    feats = load_json("rules_json/feats.json")
    groups = {}
    for feat in feats or []:
        category = feat.get("category", "Misc")
        groups.setdefault(category, []).append(feat)
    return jsonify(groups)

@rules_bp.route('/feats_index', methods=['GET'])
def get_feats_index():
    feats_index = load_json("rules_json/feats_index.json")
    return jsonify(feats_index or {})

# -----------------------
# Skills Endpoint
# -----------------------

@rules_bp.route('/skills', methods=['GET'])
def get_all_skills():
    skills = load_json("rules_json/skills.json")
    return jsonify(skills or {})
