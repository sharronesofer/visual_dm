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

