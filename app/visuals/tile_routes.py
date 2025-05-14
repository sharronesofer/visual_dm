#This module provides endpoints for:
#Tile metadata
#Sprite asset resolution
#Player map visibility
#NPC data (map context)
#It supports map, poi, player visibility, sprite UI, and npc systems.

from flask import Blueprint, request, jsonify, send_file
from firebase_admin import db
import os
from app.models.region import Region
from app.models.point_of_interest import PointOfInterest

tiles_bp = Blueprint('tiles', __name__)

# Get the absolute path to the sprite file
SPRITE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                          'visual_client', 'assets', 'tiles', 'fantasyhextiles_v3.png')

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

@tiles_bp.route('/tiles/sprite')
def get_sprite():
    """Get the tile sprite sheet"""
    try:
        return send_file(SPRITE_FILE, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tiles_bp.route('/tiles/regions')
def get_region_tiles():
    """Get all region tiles"""
    try:
        regions = Region.query.all()
        return jsonify([region.to_dict() for region in regions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tiles_bp.route('/tiles/pois')
def get_poi_tiles():
    """Get all point of interest tiles"""
    try:
        pois = PointOfInterest.query.all()
        return jsonify([poi.to_dict() for poi in pois])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
