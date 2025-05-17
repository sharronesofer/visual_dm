#This utility module provides core helpers for:
#Reading full tile metadata (including terrain)
#Updating a tile's POI field with validation
#It supports the map, poi, tilemap, terrain, and worldgen systems.

from firebase_admin import db

def get_tile_info(tile_key):
    try:
        tile_data = db.reference(f"/locations/{tile_key}").get() or {}
        terrain = db.reference(f"/terrain_map/{tile_key}").get() or "unknown"
        return {
            "tile_key": tile_key,
            "terrain": terrain,
            **tile_data
        }
    except Exception as e:
        return {"error": str(e), "tile_key": tile_key}


def update_tile_poi(tile_key, poi_data):
    if not isinstance(poi_data, dict):
        return {"error": "Invalid POI data format."}

    if "name" not in poi_data:
        return {"error": "Missing POI name."}

    db.reference(f"/locations/{tile_key}/POI").set(poi_data)
    return {"status": "success", "updated_tile": tile_key}

import random

def tick_tile_danger(region):
    """
    Increases or decreases tile danger based on surrounding POIs, tension, and randomness.
    """
    tilemap_ref = db.reference(f"/tilemap/{region}")
    tiles = tilemap_ref.get() or {}

    region_data = db.reference(f"/regional_state/{region}").get() or {}
    tension = region_data.get("tension_score", 25)  # default mid tension

    poi_data = db.reference(f"/poi_state/{region}").get() or {}

    for tile_id, tile in tiles.items():
        danger = tile.get("danger_score", 5)

        # Nearby POIs raise or lower local danger
        neighbors = tile.get("connected_tiles", [])
        dungeon_weight = 0
        for poi_id, poi in poi_data.items():
            if poi.get("location_tile") in neighbors or poi.get("location_tile") == tile_id:
                if poi.get("poi_type") == "dungeon":
                    dungeon_weight += 1
                elif poi.get("poi_type") == "social":
                    dungeon_weight -= 1

        # Regional tension adds pressure to rise
        delta = random.randint(-1, 1) + (tension // 50) + dungeon_weight
        new_danger = max(0, min(10, danger + delta))

        tilemap_ref.child(tile_id).child("danger_score").set(new_danger)

def get_visible_tiles(player_id):
    """
    Returns three groups:
    - visible: fully revealed tiles (from known_tiles)
    - adjacent: nearby but unrevealed (1-2 tiles out)
    - fogged: not shown
    """
    player = db.reference(f"/players/{player_id}").get()
    if not player:
        return {"error": "Player not found"}

    known = set(player.get("known_tiles", []))
    tiles = db.reference("/locations").get() or {}

    visible = {}
    adjacent = {}

    # Add full details for known tiles
    for tile_id in known:
        if tile_id in tiles:
            visible[tile_id] = tiles[tile_id]

            # Compute adjacent tiles (1 square out in all directions)
            try:
                x, y = map(int, tile_id.split("_"))
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if abs(dx) + abs(dy) <= 2 and not (dx == 0 and dy == 0):
                            tid = f"{x+dx}_{y+dy}"
                            if tid in tiles and tid not in known:
                                partial = tiles[tid].copy()
                                partial.pop("POI", None)
                                partial.pop("npcs_present", None)
                                adjacent[tid] = partial
            except:
                continue

    return {
        "visible": visible,
        "adjacent": adjacent
    }

def reveal_tile_to_player(player_id, tile_id):
    ref = db.reference(f"/players/{player_id}/known_tiles")
    current = ref.get() or []
    if tile_id not in current:
        current.append(tile_id)
        ref.set(current)

def get_tile_terrain(tile_key: str) -> str:
    """Get the terrain type for a tile."""
    location = db.reference(f"/locations/{tile_key}").get() or {}
    return location.get("terrain_type", "unknown")

def set_tile_poi(tile_key: str, poi_data: dict):
    """Set POI data for a tile."""
    location = db.reference(f"/locations/{tile_key}").get() or {}
    location["poi"] = poi_data
    db.reference(f"/locations/{tile_key}").set(location)

def get_all_locations() -> dict:
    """Get all locations from the database."""
    return db.reference("/locations").get() or {}