from flask import Blueprint, request, jsonify
from firebase_admin import db

tiles_bp = Blueprint('tiles', __name__)

@tiles_bp.route("/tile_data/<tile_key>", methods=["GET"])
def get_tile_data(tile_key):
    tile_key = tile_key.lower()
    tile_ref = db.reference(f"/locations/{tile_key}")
    tile = tile_ref.get() or {}

    terrain = db.reference(f"/terrain_map/{tile_key}").get() or "unknown"
    tile["terrain"] = terrain

    # Optional: include poi_name for display purposes
    poi = tile.get("POI")
    if isinstance(poi, dict):
        tile["poi_name"] = poi.get("name")
    elif isinstance(poi, str):
        tile["poi_name"] = poi

    return jsonify(tile)


@tiles_bp.route("/tile_sprites/<tile_key>", methods=["GET"])
def get_tile_sprites(tile_key):
    tile_key = tile_key.lower()
    terrain = db.reference(f"/terrain_map/{tile_key}").get() or "grassland"
    tile_data = db.reference(f"/locations/{tile_key}").get() or {}

    sprite_data = {
        "base_sprite": f"tile_{terrain.lower()}.png",
        "overlay_sprite": None
    }

    poi = tile_data.get("POI")
    if isinstance(poi, dict):
        name = poi.get("name", "").lower().replace(" ", "_")
        if name:
            sprite_data["overlay_sprite"] = f"poi_{name}.png"
    elif isinstance(poi, str):
        sprite_data["overlay_sprite"] = f"poi_{poi.lower().replace(' ', '_')}.png"

    return jsonify(sprite_data)


@tiles_bp.route("/tiles_visible/<character_id>", methods=["GET"])
def get_visible_tiles(character_id):
    character_data = db.reference(f"/players/{character_id}").get() or {}
    known_tiles = character_data.get("known_tiles") or []
    return jsonify({"character_id": character_id, "known_tiles": known_tiles})


@tiles_bp.route("/npc_data/<npc_id>", methods=["GET"])
def get_npc_data(npc_id):
    npc_data = db.reference(f"/npcs/{npc_id}").get()
    if not npc_data:
        return jsonify({"error": "NPC not found."}), 404
    return jsonify(npc_data)
