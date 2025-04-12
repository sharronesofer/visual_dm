# basic.py

from flask import Blueprint, request, jsonify, current_app
from firebase_admin import db
import uuid
import datetime
import random

# ----------------------------
# Blueprint Definitions
# ----------------------------

basic_bp = Blueprint("basic", __name__)
auth_bp = Blueprint("auth", __name__)
__all__ = ["basic_bp", "auth_bp"]

# ----------------------------
# Authentication & User Management
# ----------------------------

@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Email, password, and username are required"}), 400

    uid = str(uuid.uuid4())
    user_ref = db.reference(f"/users/{uid}")
    user_ref.set({
        "username": username,
        "email": email,
        "password": password,
        "character_data": {},
        "created_at": datetime.datetime.utcnow().isoformat()
    })

    return jsonify({"message": "User created successfully", "user_id": uid}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    users_ref = db.reference("/users")
    all_users = users_ref.get() or {}

    for uid, user_data in all_users.items():
        if user_data.get("username") == username:
            if user_data.get("password") == password:
                return jsonify({"message": "Login successful", "user_id": uid}), 200
            return jsonify({"error": "Invalid password"}), 401

    return jsonify({"error": "User not found"}), 404


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "User logged out (handled client-side)."}), 200

# ----------------------------
# Housekeeping Utilities
# ----------------------------

def generate_ability_scores():
    """4d6-drop-lowest ability score generation."""
    abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    scores = {}
    for ab in abilities:
        rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
        scores[ab] = sum(rolls[:3])
    return scores

def log_gpt_usage(model, usage):
    """Logs GPT usage details to Firebase."""
    timestamp = datetime.datetime.utcnow().isoformat()
    log_ref = db.reference(f'/gpt_usage/{model}/{timestamp}')
    log_ref.set(usage)

# ----------------------------
# Debugging and Utility Endpoints
# ----------------------------

@basic_bp.route('/debug_routes', methods=['GET'])
def debug_routes():
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "rule": rule.rule
        })
    return jsonify(routes)

@basic_bp.route('/debug_state', methods=['GET'])
def debug_state():
    try:
        state = db.reference('/global_state').get() or {}
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
