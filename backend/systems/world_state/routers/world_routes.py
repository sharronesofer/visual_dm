from backend.systems.region.region_generation_utils import generate_region
from fastapi import APIRouter as APIRouter, jsonify, request
from backend.systems.world_state.core.manager import WorldStateManager

world_bp = Blueprint("world_bootstrap", __name__)

@world_bp.route('/generate_initial_world', methods=['POST'])
def generate_initial_world():
    """
    Creates a world, stores it as the default /global_state/home_region.
    """
    try:
        region_id, region_data = generate_region()

        # Use the WorldStateManager to update the state
        manager = WorldStateManager()
        world_state = manager.get_world_state()
        world_state["home_region"] = region_id
        manager.update_world_state({"home_region": region_id})

        return jsonify({
            "message": f"World generated with starting region {region_id}.",
            "region_id": region_id,
            "tiles_created": len(region_data.get("tiles", {})),
            "poi_count": len(region_data.get("poi_list", []))
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@world_bp.route("/world_summary", methods=["GET"])
def get_world_summary():
    try:
        # Use the WorldStateManager to get state data
        manager = WorldStateManager()
        world_state = manager.get_world_state()
        
        # Extract the components needed for the summary
        global_state = world_state.get("global", {})
        regional_state = world_state.get("regions", {})
        poi_state = world_state.get("pois", {})

        summary = {
            "global_state": global_state,
            "regional_state": regional_state,
            "poi_state": poi_state
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@world_bp.route("/tick_world", methods=["POST"])
def tick_world():
    try:
        # Use the WorldStateManager to advance time
        manager = WorldStateManager()
        data = request.get_json(force=True) or {}
        days = data.get("days", 0)
        hours = data.get("hours", 0)
        minutes = data.get("minutes", 1)  # Default to 1 minute if not specified
        
        # Advance the world time
        updated_state = manager.advance_world_time(days=days, hours=hours, minutes=minutes)
        
        return jsonify({
            "message": "World tick processed.",
            "current_date": updated_state.get("current_date", {})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@world_bp.route('/global_state', methods=['GET'])
def get_global_state():
    """
    Fetches the current global state document.
    """
    try:
        # Use the WorldStateManager to get global state
        manager = WorldStateManager()
        world_state = manager.get_world_state()
        global_state = world_state.get("global", {})
        return jsonify(global_state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@world_bp.route('/global_state/update', methods=['POST'])
def update_global_state():
    """
    Updates the global state document with provided fields.
    """
    try:
        data = request.get_json(force=True)
        
        # Use the WorldStateManager to update the state
        manager = WorldStateManager()
        updates = {"global": data}
        manager.update_world_state(updates)
        
        return jsonify({"message": "Global state updated successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

