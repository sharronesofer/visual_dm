"""
worldgen.py
Merged from worldgen.py + region_generator.py
Handles region generation, land type selection, monster spawning, bounty system, etc.
"""

import os
import json
import random
import math
from datetime import datetime, timedelta
from collections import deque
from basic import basic_bp
import openai
from flask import Blueprint, request, jsonify
from firebase_admin import db

# If referencing GPT usage:
try:
    from gpt_endpoints import log_gpt_usage
except ImportError:
    def log_gpt_usage(*args, **kwargs):
        pass

# Attempt to load land_types
try:
    with open("rules/land_types.json", "r") as f:
        land_type_meta = json.load(f)
except Exception as e:
    land_type_meta = {}
    print(f"Warning: could not load land_types.json -> {e}")

worldgen_bp = Blueprint("worldgen", __name__)  # If you define the 'basic' blueprint here

# ========== The rest of your region generation, tile logic, bounties, monster spawns, etc. follow ==========

################################################################################
# Region Generation Logic
################################################################################

def generate_region_shape(seed_x: int, seed_y: int, min_tiles=20, max_tiles=40, direction_bias=0.75) -> set:
    """
    BFS-based region expansion from (seed_x, seed_y).
    Returns a set of (x, y) tile coordinates.
    """
    target_size = random.randint(min_tiles, max_tiles)
    region_tiles = set()
    queue = deque()
    visited = set()

    seed = (seed_x, seed_y)
    queue.append(seed)
    region_tiles.add(seed)
    visited.add(seed)

    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0),
        (1, 1), (1, -1), (-1, -1), (-1, 1)
    ]

    while queue and len(region_tiles) < target_size:
        current = queue.popleft()
        random.shuffle(directions)
        for dx, dy in directions:
            if random.random() < direction_bias:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor not in visited:
                    visited.add(neighbor)
                    region_tiles.add(neighbor)
                    queue.append(neighbor)
                    if len(region_tiles) >= target_size:
                        break
    return region_tiles

def generate_region(seed_x: int, seed_y: int) -> dict:
    """
    Creates a region around (seed_x, seed_y) via generate_region_shape
    and calls GPT for region metadata & factions. Merged from 'worldgen.py' 
    and 'region_generator.py'.
    """
    region_id = f"region_{seed_x}_{seed_y}_{random.randint(1000,9999)}"
    tiles = generate_region_shape(seed_x, seed_y)

    # Prompt GPT for region themes
    region_prompt = (
        "Generate a fantasy region in JSON:\n"
        " {\n"
        "   'region_name':..., 'encouraged_land_types':..., 'forbidden_land_types':..., 'poi_density_cap':...\n"
        " }"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a worldbuilding assistant."},
                {"role": "user", "content": region_prompt}
            ],
            temperature=0.85,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        usage = response.get("usage", {})
        log_gpt_usage("gpt-4", usage)

        region_meta = json.loads(content)
    except Exception as e:
        return {"error": f"GPT error for region theme: {e}"}

    region_name = region_meta.get("region_name", f"Unnamed {region_id}")
    region_meta["region_id"] = region_id
    region_meta["name"] = region_name
    region_meta["tiles"] = []

    # Link each tile
    for (x, y) in tiles:
        tile_key = f"{x}_{y}"
        tile_ref = db.reference(f"/locations/{tile_key}")
        tile_data = tile_ref.get() or {}
        tile_data["region_id"] = region_id
        tile_ref.set(tile_data)
        region_meta["tiles"].append(tile_key)

    # GPT for factions
    faction_prompt = (
        f"Generate 2-4 factions for region '{region_name}'. Include one primary government faction.\n"
        "Return a JSON list, e.g.\n"
        "[\n"
        "  {'name':'...', 'alignment':'...', 'goals':'...', 'motto':'...', 'type':'government|...','primary':true}\n"
        "]"
    )
    region_meta["factions"] = []
    try:
        fact_resp = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative fantasy faction designer."},
                {"role": "user", "content": faction_prompt}
            ],
            temperature=0.9,
            max_tokens=600
        )
        fact_content = fact_resp.choices[0].message.content.strip()
        log_gpt_usage("gpt-4", fact_resp.get("usage", {}))

        factions = json.loads(fact_content)
        for faction in factions:
            fid = str(uuid.uuid4())
            faction["region"] = region_id
            db.reference(f"/factions/{fid}").set(faction)
            region_meta["factions"].append(fid)
            if faction.get("primary") and faction.get("type") == "government":
                region_meta["government_faction_id"] = fid
    except Exception as e:
        region_meta["faction_error"] = str(e)

    # Save final region data
    db.reference(f"/regions/{region_id}").set(region_meta)
    return region_meta

################################################################################
# Land Type Selection and Terrains
################################################################################

def choose_land_type(x: int, y: int, region_id: str) -> str:
    """
    Chooses a land type for tile (x, y) based on region constraints 
    (allowed_types, forbidden_types, usage distribution, neighbor tiles).
    """
    region_data = db.reference(f"/regions/{region_id}").get() or {}
    allowed = set(region_data.get("allowed_types", []))
    forbidden = set(region_data.get("forbidden_types", []))

    usage_data = db.reference("/land_type_usage").get() or {}

    # Gather neighbor terrains for weighting
    neighbor_coords = [
        (x + dx, y + dy)
        for dx, dy in [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
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
        # Boost if neighbors share the same land type
        base_score += neighbor_types.count(lt)

        used = usage_data.get(lt, 0)
        base_score = base_score / (1 + used / 1000.0)

        # Adjust for rarity (1–10, typically)
        rarity = land_type_meta.get(lt, {}).get("rarity", 5)
        base_score *= (11 - rarity)

        scores[lt] = base_score

    # Fallback if no valid scores
    if not scores:
        db.reference(f"/terrain_map/{x}_{y}").set("grassland")
        return "grassland"

    total_weight = sum(scores.values())
    weighted = [(lt, val / total_weight) for lt, val in scores.items()]
    choices, weights = zip(*weighted)
    chosen = random.choices(choices, weights=weights)[0]

    db.reference(f"/terrain_map/{x}_{y}").set(chosen)
    db.reference(f"/land_type_usage/{chosen}").set(usage_data.get(chosen, 0) + 1)
    return chosen

def roll_danger_for_tile(x: int, y: int) -> int:
    """
    Returns a random 'danger' value for tile (x, y) based on land_types.json.
    If absent, defaults to range [0..2].
    """
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    meta = land_type_meta.get(land_type, {})
    min_danger, max_danger = meta.get("danger_range", [0, 2])
    return random.randint(min_danger, max_danger)

def should_generate_poi(x: int, y: int) -> bool:
    """
    Decides if tile (x, y) should become a Point of Interest (POI) 
    based on region poi_density_cap, base poi_chance, 
    and distance to existing POIs.
    """
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    region_id = db.reference(f"/region_map/{x}_{y}").get() or "default"
    region_data = db.reference(f"/regions/{region_id}").get() or {}

    poi_cap = region_data.get("poi_density_cap", 10)
    existing_pois = db.reference("/locations").get() or {}

    # Count how many POIs are already in region
    same_region_pois = [
        loc for loc in existing_pois.values()
        if loc.get("POI") and loc.get("region_id") == region_id
    ]
    if len(same_region_pois) >= poi_cap:
        return False

    base_chance = land_type_meta.get(land_type, {}).get("poi_chance", 0.05)

    # Dist to nearest POI
    min_dist = float('inf')
    for key, loc in existing_pois.items():
        if not loc.get("POI"):
            continue
        try:
            px, py = map(int, key.split("_"))
            dist = math.sqrt((px - x)**2 + (py - y)**2)
            if dist < min_dist:
                min_dist = dist
        except:
            continue

    distance_bonus = min(1.0, min_dist / 10.0)
    final_chance = base_chance * distance_bonus
    return (random.random() < final_chance)

################################################################################
# Refreshing and Updating POIs
################################################################################

def days_since(iso_ts: str) -> int:
    """
    Returns how many days have passed since iso_ts. If parse fails, returns a large number.
    """
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return (datetime.utcnow() - dt).days
    except:
        return 999

def refresh_cleared_pois() -> int:
    """
    Looks for POIs with status=='cleared' for >=3 days.
    60% chance to revert them to 'active' with random danger.
    """
    locations = db.reference("/locations").get() or {}
    count = 0
    for key, data in locations.items():
        if data.get("status") == "cleared":
            if days_since(data.get("cleared_on", "")) >= 3:
                if random.random() < 0.6:
                    data["status"] = "active"
                    data["danger_level"] = random.randint(3, 8)
                    data["description"] = data.get("description", "") + " (It seems something has returned...)"
                    db.reference(f"/locations/{key}").set(data)
                    count += 1
    return count

@basic_bp.route('/refresh_pois', methods=['POST'])
def refresh_pois():
    """
    POST /refresh_pois
    Finds old 'cleared' POIs and potentially reactivates them.
    """
    cnt = refresh_cleared_pois()
    return jsonify({"message": f"Refreshed {cnt} POIs."})

################################################################################
# Monster Generation
################################################################################

def generate_monsters_for_tile(x: int, y: int):
    """
    Pulls up to 2 random monsters matching the tile's biome from /rules/monsters.
    """
    biome = db.reference(f"/terrain_map/{x}_{y}").get() or "forest"
    all_monsters = db.reference("/rules/monsters").get() or {}
    themeds = [m for m in all_monsters.values() if biome in m.get("tags", [])]

    if not themeds:
        themeds = list(all_monsters.values())

    return random.sample(themeds, min(2, len(themeds)))

################################################################################
# Bounty System
################################################################################

def add_bounty(player_id: str, region: str, amount: int) -> dict:
    """
    Adds a 'bounty' to a player's record in a given region.
    """
    ref = db.reference(f"/players/{player_id}/bounty")
    data = ref.get() or {"total": 0, "region": {}}
    data["total"] += amount
    data["region"][region] = data["region"].get(region, 0) + amount
    data["last_offense"] = datetime.utcnow().isoformat()
    ref.set(data)
    return data

def check_bounty(player_id: str) -> dict:
    """
    Returns the bounty record for a given player.
    """
    return db.reference(f"/players/{player_id}/bounty").get() or {"total": 0, "region": {}}

def decay_bounties():
    """
    Reduces all player bounties by 5% (both total and region).
    """
    players = db.reference("/players").get() or {}
    for pid, pdata in players.items():
        bounty = pdata.get("bounty", {})
        bounty["total"] = max(0, int(bounty.get("total", 0) * 0.95))

        region_map = bounty.get("region", {})
        for r, val in region_map.items():
            region_map[r] = max(0, int(val * 0.95))

        bounty["region"] = region_map
        db.reference(f"/players/{pid}/bounty").set(bounty)

@basic_bp.route('/add_bounty', methods=['POST'])
def route_add_bounty():
    data = request.json or {}
    player_id = data.get("player_id")
    region = data.get("region")
    amount = data.get("amount", 0)

    if not player_id or not region:
        return jsonify({"error": "Missing player_id or region"}), 400

    updated = add_bounty(player_id, region, amount)
    return jsonify(updated)

@basic_bp.route('/check_bounty/<player_id>', methods=['GET'])
def route_check_bounty(player_id):
    """
    GET /check_bounty/<player_id>
    Returns the player's current bounty data.
    """
    data = check_bounty(player_id)
    return jsonify(data)

@basic_bp.route('/decay_bounties', methods=['POST'])
def route_decay_bounties():
    """
    POST /decay_bounties
    Reduces all bounties by 5%.
    """
    decay_bounties()
    return jsonify({"message": "All player bounties decayed by 5%"})

@basic_bp.route('/monster_spawns/<int:x>/<int:y>', methods=['GET'])
def route_generate_monsters_for_tile(x, y):
    """
    GET /monster_spawns/<x>/<y>
    Returns up to 2 random monsters from /rules/monsters that match the tile's biome.
    """
    monsters = generate_monsters_for_tile(x, y)
    return jsonify({"tile": f"{x}_{y}", "monsters": monsters})
