from flask import Blueprint, request, jsonify
from app.regions.tension_utils import get_tension, modify_tension, reset_tension, decay_tension

# Constants
tension_levels = [
    (0, 10, "peaceful"),
    (11, 30, "watchful"),
    (31, 60, "anxious"),
    (61, 80, "violent"),
    (81, 100, "collapsing")
]

tension_bp = Blueprint('tension', __name__)

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
