# tension_engine.py

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
import logging

# Tension Blueprint
tension_bp = Blueprint('tension', __name__)

# Constants
tension_levels = [
    (0, 10, "peaceful"),
    (11, 30, "watchful"),
    (31, 60, "anxious"),
    (61, 80, "violent"),
    (81, 100, "collapsing")
]

# Exported items
__all__ = [
    "tension_bp",
    "get_tension_descriptor",
    "get_tension",
    "modify_tension",
    "reset_tension",
    "decay_tension"
]

# Utility Functions

def get_tension_descriptor(level):
    for low, high, label in tension_levels:
        if low <= level <= high:
            return label
    return "unknown"

def get_tension(region_id):
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}
    level = data.get("level", 0)
    label = get_tension_descriptor(level)
    return {
        "region": region_id,
        "level": level,
        "label": label,
        "modifiers": data.get("modifiers", {})
    }

def modify_tension(region_id, source, amount):
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}

    modifiers = data.get("modifiers", {})
    modifiers[source] = modifiers.get(source, 0) + amount

    level_sum = max(0, min(sum(modifiers.values()), 100))

    data.update({
        "level": level_sum,
        "modifiers": modifiers,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

def reset_tension(region_id):
    ref = db.reference(f"/regions/{region_id}/tension")
    ref.set({
        "level": 0,
        "modifiers": {},
        "last_modified": datetime.utcnow().isoformat()
    })
    return get_tension(region_id)

def decay_tension(region_id, decay_rate=1):
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {}
    if not data:
        return {"error": "No tension data for this region"}

    modifiers = data.get("modifiers", {})
    updated_modifiers = {}
    for k, v in modifiers.items():
        if abs(v) > decay_rate:
            updated_modifiers[k] = v - decay_rate if v > 0 else v + decay_rate

    level_sum = max(0, min(sum(updated_modifiers.values()), 100))

    data.update({
        "level": level_sum,
        "modifiers": updated_modifiers,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

# Flask Routes

@tension_bp.route('/tension/<region_id>', methods=['GET'])
def route_get_tension(region_id):
    return jsonify(get_tension(region_id))

@tension_bp.route('/tension/modify', methods=['POST'])
def route_modify_tension():
    payload = request.json or {}
    region_id = payload.get("region_id")
    source = payload.get("source")
    amount = payload.get("amount", 0)

    if not region_id or not source:
        return jsonify({"error": "Missing region_id or source"}), 400

    result = modify_tension(region_id, source, amount)
    return jsonify(result)

@tension_bp.route('/tension/reset/<region_id>', methods=['POST'])
def route_reset_tension(region_id):
    data = reset_tension(region_id)
    return jsonify(data)

@tension_bp.route('/tension/decay/<region_id>', methods=['POST'])
def route_decay_tension(region_id):
    payload = request.json or {}
    decay_rate = payload.get("decay_rate", 1)

    data = decay_tension(region_id, decay_rate)
    return jsonify(data)
