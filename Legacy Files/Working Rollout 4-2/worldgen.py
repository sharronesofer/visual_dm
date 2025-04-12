import random
import json
from firebase_admin import db
import math

# Load local land type metadata
with open("rules/land_types.json", "r") as f:
    land_type_meta = json.load(f)

def choose_land_type(x, y, region_id):
    region_data = db.reference(f"/regions/{region_id}").get() or {}
    allowed = set(region_data.get("allowed_types", []))
    forbidden = set(region_data.get("forbidden_types", []))

    usage_data = db.reference("/land_type_usage").get() or {}

    neighbor_coords = [
        (x + dx, y + dy)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)]
    ]
    neighbor_types = []
    for nx, ny in neighbor_coords:
        terrain = db.reference(f"/terrain_map/{nx}_{ny}").get()
        if terrain:
            neighbor_types.append(terrain)

    scores = {}
    for lt in land_type_meta.keys():
        if lt in forbidden:
            continue

        base_score = 1
        if lt in allowed:
            base_score += 3
        if lt in neighbor_types:
            base_score += neighbor_types.count(lt)

        used = usage_data.get(lt, 0)
        base_score = base_score / (1 + used / 1000)

        rarity = land_type_meta.get(lt, {}).get("rarity", 5)
        base_score *= (11 - rarity)

        scores[lt] = base_score

    if not scores:
        return "grassland"

    total = sum(scores.values())
    weighted = [(lt, weight / total) for lt, weight in scores.items()]
    choices, weights = zip(*weighted)
    chosen = random.choices(choices, weights=weights)[0]

    db.reference(f"/terrain_map/{x}_{y}").set(chosen)
    db.reference(f"/land_type_usage/{chosen}").set(usage_data.get(chosen, 0) + 1)

    return chosen

def roll_danger_for_tile(x, y):
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    meta = land_type_meta.get(land_type, {})
    min_danger, max_danger = meta.get("danger_range", [0, 2])
    return random.randint(min_danger, max_danger)

def should_generate_poi(x, y):
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    region_id = db.reference(f"/region_map/{x}_{y}").get() or "default"
    region_data = db.reference(f"/regions/{region_id}").get() or {}

    poi_cap = region_data.get("poi_density_cap", 10)  # max POIs allowed in region
    existing_pois = db.reference("/locations").get() or {}

    # Count POIs in this region
    pois_in_region = [loc for loc in existing_pois.values()
                      if loc.get("POI") and loc.get("region_id") == region_id]
    if len(pois_in_region) >= poi_cap:
        return False

    # Base POI chance from land type
    base_chance = land_type_meta.get(land_type, {}).get("poi_chance", 0.05)

    # Distance to nearest POI
    min_dist = float("inf")
    for key, loc in existing_pois.items():
        if loc.get("POI"):
            try:
                px, py = map(int, key.split("_"))
                dist = math.sqrt((px - x) ** 2 + (py - y) ** 2)
                if dist < min_dist:
                    min_dist = dist
            except:
                continue

    distance_bonus = min(1.0, min_dist / 10)  # full bonus at 10+ tiles
    final_chance = base_chance * distance_bonus

    return random.random() < final_chance
