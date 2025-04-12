import random
import math
import uuid
import json
from firebase_admin import db
import os
from itertools import combinations

# Load local land type metadata
with open("rules/land_types.json", "r") as f:
    land_type_meta = json.load(f)

ALL_MONSTERS = []
for fname in os.listdir("rules/monsters"):
    if fname.endswith(".json"):
        with open(os.path.join("rules/monsters", fname)) as f:
            monster = json.load(f)
            ALL_MONSTERS.append(monster)

# Terrain and land generation logic
def choose_land_type(x, y, region_id):
    region_data = db.reference(f"/regions/{region_id}").get() or {}
    allowed = set(region_data.get("allowed_types", []))
    forbidden = set(region_data.get("forbidden_types", []))
    usage_data = db.reference("/land_type_usage").get() or {}

    neighbor_coords = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]]
    neighbor_types = [db.reference(f"/terrain_map/{nx}_{ny}").get() for nx, ny in neighbor_coords if db.reference(f"/terrain_map/{nx}_{ny}").get()]

    scores = {}
    for lt in land_type_meta:
        if lt in forbidden:
            continue
        base_score = 1
        base_score += 3 if lt in allowed else 0
        base_score += neighbor_types.count(lt)
        base_score /= (1 + usage_data.get(lt, 0) / 1000)
        base_score *= (11 - land_type_meta[lt].get("rarity", 5))
        scores[lt] = base_score

    if not scores:
        chosen = "grassland"
    else:
        total = sum(scores.values())
        choices, weights = zip(*[(lt, score / total) for lt, score in scores.items()])
        chosen = random.choices(choices, weights=weights)[0]

    db.reference(f"/terrain_map/{x}_{y}").set(chosen)
    db.reference(f"/land_type_usage/{chosen}").set(usage_data.get(chosen, 0) + 1)

    return chosen

def roll_danger_for_tile(x, y):
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    min_danger, max_danger = land_type_meta.get(land_type, {}).get("danger_range", [0, 2])
    return random.randint(min_danger, max_danger)

def should_generate_poi(x, y):
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    region_id = db.reference(f"/region_map/{x}_{y}").get() or "default"
    region_data = db.reference(f"/regions/{region_id}").get() or {}
    poi_cap = region_data.get("poi_density_cap", 10)

    existing_pois = db.reference("/locations").get() or {}
    pois_in_region = [loc for loc in existing_pois.values() if loc.get("POI") and loc.get("region_id") == region_id]
    if len(pois_in_region) >= poi_cap:
        return False

    base_chance = land_type_meta.get(land_type, {}).get("poi_chance", 0.05)
    min_dist = min([math.sqrt((int(px) - x) ** 2 + (int(py) - y) ** 2) for px, py in (key.split("_") for key, loc in existing_pois.items() if loc.get("POI"))], default=10)
    distance_bonus = min(1.0, min_dist / 10)

    return random.random() < base_chance * distance_bonus

# Region and monster management
def generate_region_shape(seed_x, seed_y, min_tiles=20, max_tiles=40):
    target_size = random.randint(min_tiles, max_tiles)
    tiles, queue, visited = set(), [(seed_x, seed_y)], {(seed_x, seed_y)}

    while queue and len(tiles) < target_size:
        current = queue.pop(0)
        tiles.add(current)
        neighbors = [(current[0]+dx, current[1]+dy) for dx, dy in [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,-1),(-1,1)]]
        random.shuffle(neighbors)
        for n in neighbors:
            if n not in visited and random.random() < 0.75:
                visited.add(n)
                queue.append(n)
                if len(tiles) >= target_size:
                    break

    return tiles

def generate_region(seed_x, seed_y):
    region_id = f"region_{seed_x}_{seed_y}_{uuid.uuid4().hex[:8]}"
    tiles = generate_region_shape(seed_x, seed_y)
    region_meta = {"region_id": region_id, "tiles": []}

    for x, y in tiles:
        key = f"{x}_{y}"
        db.reference(f"/locations/{key}").set({"region_id": region_id})
        region_meta["tiles"].append(key)

    db.reference(f"/regions/{region_id}").set(region_meta)
    return region_meta

def get_monster_group_for_player_level(player_level):
    min_cr, max_cr = round(player_level * 0.25 - 0.25, 2), round(player_level * 0.25 + 0.25, 2)
    candidates = [m for m in ALL_MONSTERS if min_cr <= m["challenge_rating"] <= max_cr]
    for r in range(1, 5):
        for combo in combinations(candidates, r):
            if min_cr <= sum(m["challenge_rating"] for m in combo) <= max_cr:
                return list(combo)
    return []