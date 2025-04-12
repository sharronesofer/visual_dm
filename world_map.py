# world_map.py

from flask import Blueprint, jsonify
from firebase_admin import db

visual_bp = Blueprint("visual", __name__)
__all__ = ["visual_bp"]

# -------------------------------
# Tile and Terrain Data
# -------------------------------

@visual_bp.route("/tile_data/<tile_key>", methods=["GET"])
def get_tile_data(tile_key):
    tile_ref = db.reference(f"/locations/{tile_key}")
    tile = tile_ref.get() or {}

    terrain = db.reference(f"/terrain_map/{tile_key}").get() or "unknown"
    tile["terrain"] = terrain

    return jsonify(tile)

@visual_bp.route("/tile_sprites/<tile_key>", methods=["GET"])
def get_tile_sprites(tile_key):
    terrain_ref = db.reference(f"/terrain_map/{tile_key}")
    terrain = terrain_ref.get() or "grassland"

    tile_ref = db.reference(f"/locations/{tile_key}")
    tile_data = tile_ref.get() or {}

    sprite_data = {
        "base_sprite": f"tile_{terrain}.png",
        "overlay_sprite": None
    }

    if tile_data.get("POI"):
        sprite_data["overlay_sprite"] = f"poi_{tile_data['POI']}.png"

    return jsonify(sprite_data)

# -------------------------------
# Player Map Awareness
# -------------------------------

@visual_bp.route("/tiles_visible/<character_id>", methods=["GET"])
def get_visible_tiles(character_id):
    character_ref = db.reference(f"/players/{character_id}")
    character_data = character_ref.get() or {}
    known_tiles = character_data.get("known_tiles", [])

    return jsonify({"character_id": character_id, "known_tiles": known_tiles})

# -------------------------------
# NPC Info on Map
# -------------------------------

@visual_bp.route("/npc_data/<npc_id>", methods=["GET"])
def get_npc_data(npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()
    if not npc_data:
        return jsonify({"error": "NPC not found."}), 404

    return jsonify(npc_data)
