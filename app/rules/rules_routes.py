#This module exposes read-only HTTP endpoints for rulebook data, allowing clients to fetch:
#Full feats
#Feats grouped by category
#Feat index
#Skills
#It is part of the rules, character creation, frontend support, and UI data access systems.

from flask import Blueprint, jsonify
import random
import json
import logging
from app.core.utils.json_utils import load_json
from app.rules.character_gen_rules_utils import (
    load_race_data,
    load_skill_list,
    load_feat_data,
    load_starter_kits
)


rules_bp = Blueprint('rules_data', __name__)

# -----------------------
# Feats Endpoints
# -----------------------

@rules_bp.route('/feats', methods=['GET'])
def get_all_feats():
    feats = load_json("feats.json")
    return jsonify(feats or [])

@rules_bp.route('/feats_by_category', methods=['GET'])
def get_feats_by_category():
    feats = load_json("feats.json")
    groups = {}
    for feat in feats or []:
        category = feat.get("category", "Misc")
        groups.setdefault(category, []).append(feat)
    return jsonify(groups)

@rules_bp.route('/feats_index', methods=['GET'])
def get_feats_index():
    feats_index = load_json("feats.json")
    return jsonify(feats_index or {})

# -----------------------
# Skills Endpoint
# -----------------------

@rules_bp.route('/skills', methods=['GET'])
def get_all_skills():
    skills = load_json("skills.json")
    return jsonify(skills or {})

@rules_bp.route("/races", methods=["GET"])
def get_races():
    return jsonify(load_race_data())

@rules_bp.route("/skills", methods=["GET"])
def get_skills():
    skills = load_skill_list()
    return jsonify({s: {} for s in skills})  # if skill_list is just names

@rules_bp.route("/starting_kits", methods=["GET"])
def get_starter_kits():
    return jsonify(load_starter_kits())

