# worldgen.py

import os
import random
import math
from uuid import uuid4
from datetime import datetime, timedelta
from collections import deque
import openai
import json

from flask import Blueprint, request, jsonify
from firebase_admin import db

from character_utils import complete_character
from npc_generator import generate_npcs_for_poi
from gpt_endpoints import log_gpt_usage

# Blueprint
worldgen_bp = Blueprint("worldgen", __name__)

# Load land_types.json
try:
    with open("rules/land_types.json", "r") as f:
        land_type_meta = json.load(f)
except Exception as e:
    land_type_meta = {}
    print(f"Warning: could not load land_types.json -> {e}")

# Exported
__all__ = ["worldgen_bp"]

# ---- Utility & Worldbuilding ----

def generate_starting_city_and_region():
    key = "0_0"
    poi_ref = db.reference(f"/locations/{key}")
    if not poi_ref.get():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": (
                        "Generate a fantasy capital city in JSON format with fields: "
                        "name, description, danger_level, buildings (list), tags (tone, focus)."
                    )},
                    {"role": "user", "content": "Create a sprawling capital city for the region 'Sunveil Dominion'."}
                ],
                temperature=0.8,
                max_tokens=500
            )
            city_data = json.loads(response.choices[0].message.content.strip())
            city_data.update({
                "POI": True,
                "terrain": "grassland",
                "region_id": "sunveil_dominion"
            })
            poi_ref.set(city_data)

            generate_npcs_for_poi(0, 0)
            log_gpt_usage("gpt-4o", response.get("usage", {}))

        except Exception as e:
            poi_ref.set({"error": str(e)})

def log_world_event(event_data):
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    event_data["event_id"] = event_id
    event_data["timestamp"] = datetime.utcnow().isoformat()
    db.reference(f"/global_state/world_log/{event_id}").set(event_data)
    return event_data

def create_player(character_id, name, race, class_type):
    generate_starting_city_and_region()
    character_data = {
        "character_name": name,
        "characterType": "Player Character",
        "race": race,
        "class": class_type,
        "region_of_origin": "sunveil_dominion",
        "location": "0_0",
        "region_id": "sunveil_dominion",
        "XP": 0,
        "level": 1,
        "alignment": "Neutral",
        "inventory": [],
        "equipment": [],
        "languages": ["Common"],
        "created_at": datetime.utcnow().isoformat()
    }
    finished = complete_character(character_data)
    db.reference(f"/players/{character_id}").set(finished)
    return finished

def generate_region_shape(seed_x, seed_y, min_tiles=20, max_tiles=40, direction_bias=0.75):
    target_size = random.randint(min_tiles, max_tiles)
    region_tiles = set()
    queue = deque()
    visited = set()
    seed = (seed_x, seed_y)
    queue.append(seed)
    region_tiles.add(seed)
    visited.add(seed)
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]
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

def generate_region(seed_x, seed_y):
    region_id = f"region_{seed_x}_{seed_y}_{random.randint(1000,9999)}"
    tiles = generate_region_shape(seed_x, seed_y)

    prompt = (
        "Generate a fantasy region in JSON:\n"
        "{ 'region_name':..., 'encouraged_land_types':..., 'forbidden_land_types':..., 'poi_density_cap':... }"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a worldbuilding assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=300
        )
        region_meta = json.loads(response.choices[0].message.content.strip())
        log_gpt_usage("gpt-4", response.get("usage", {}))
    except Exception as e:
        return {"error": f"GPT error for region theme: {e}"}

    region_meta["region_id"] = region_id
    region_meta["name"] = region_meta.get("region_name", f"Unnamed {region_id}")
    region_meta["tiles"] = []

    for (x, y) in tiles:
        key = f"{x}_{y}"
        ref = db.reference(f"/locations/{key}")
        data = ref.get() or {}
        data["region_id"] = region_id
        ref.set(data)
        region_meta["tiles"].append(key)

    # Factions
    faction_prompt = (
        f"Generate 2-4 factions for region '{region_meta['name']}'. Include one primary government faction. Return JSON list."
    )
    region_meta["factions"] = []
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative fantasy faction designer."},
                {"role": "user", "content": faction_prompt}
            ],
            temperature=0.9,
            max_tokens=600
        )
        factions = json.loads(response.choices[0].message.content.strip())
        for f in factions:
            fid = str(uuid4())
            f["region"] = region_id
            db.reference(f"/factions/{fid}").set(f)
            region_meta["factions"].append(fid)
            if f.get("primary") and f.get("type") == "government":
                region_meta["government_faction_id"] = fid
    except Exception as e:
        region_meta["faction_error"] = str(e)

    db.reference(f"/regions/{region_id}").set(region_meta)
    return region_meta

# ---- Terrain & POI ----

def choose_land_type(x, y, region_id):
    terrain = random.choice(list(land_type_meta.keys()))
    db.reference(f"/terrain_map/{x}_{y}").set(terrain)
    return terrain

def roll_danger_for_tile(x, y):
    return random.randint(0, 10)

def should_generate_poi(x, y):
    return random.random() < 0.1

def refresh_cleared_pois():
    return 0

@worldgen_bp.route('/refresh_pois', methods=['POST'])
def refresh_pois():
    cnt = refresh_cleared_pois()
    return jsonify({"message": f"Refreshed {cnt} POIs."})

# ---- Encounters & Monsters ----

def generate_monsters_for_tile(x, y):
    all_monsters = db.reference("/rules/monsters").get() or {}
    return random.sample(list(all_monsters.values()), min(2, len(all_monsters)))

@worldgen_bp.route('/monster_spawns/<int:x>/<int:y>', methods=['GET'])
def monster_spawns(x, y):
    return jsonify({"tile": f"{x}_{y}", "monsters": generate_monsters_for_tile(x, y)})

@worldgen_bp.route('/generate_encounter_v2', methods=['POST'])
def generate_encounter_v2():
    data = request.get_json(force=True)
    party_id = data.get("party_id")
    location = data.get("location", "0_0")
    if not party_id:
        return jsonify({"error": "party_id is required"}), 400

    try:
        px, py = map(int, location.split("_"))
    except:
        px, py = 0, 0

    dist = math.sqrt(px**2 + py**2)
    frac = min(max((dist - 50) / 50, 0.0), 1.0) if dist > 50 else 0.0

    cr_inc, roll = 0.0, random.random()
    for step, chance in [(0.25, 0.05), (0.50, 0.15), (0.75, 0.30), (1.00, 0.50)]:
        if roll < chance * frac:
            cr_inc = step
            break
        roll -= chance * frac

    party = db.reference(f"/parties/{party_id}").get()
    if not party:
        return jsonify({"error": f"Party {party_id} not found"}), 404

    from combat_engine import start_combat
    from rules_endpoints import award_xp_to_party

    player_party = []
    for pid in party.get("members", []):
        c = db.reference(f"/players/{pid}").get() or {}
        if c:
            player_party.append({**c, "id": pid})

    total_lvl = sum(p.get("level", 1) for p in player_party)
    eff_lvl = total_lvl + cr_inc
    min_cr, max_cr = max(round(eff_lvl * 0.25 - 0.25, 2), 0), round(eff_lvl * 0.25 + 0.25, 2)

    monsters = db.reference("/rules/monsters").get() or {}
    valid = [m for m in monsters.values() if min_cr <= m.get("challenge_rating", 0) <= max_cr]
    if not valid:
        return jsonify({"error": "No suitable monsters found."}), 500

    enemies = [{
        "id": f"enemy_{uuid4().hex[:8]}",
        "name": m.get("name", "Unknown"),
        "HP": m.get("hp", 20),
        "AC": m.get("ac", 12),
        "DEX": m.get("dex", 10),
        "team": "hostile"
    } for m in random.sample(valid, min(3, len(valid)))]

    battle_id, combat_data = start_combat(f"Encounter at {location}", player_party, enemies)
    xp = sum(m.get("xp", 50) for m in enemies)
    xp_result = award_xp_to_party(party_id, xp)

    return jsonify({
        "message": "Combat started with distance-based CR scaling",
        "battle_id": battle_id,
        "player_party": player_party,
        "enemy_party": enemies,
        "xp_awarded": xp_result,
        "distance_fraction": frac,
        "effective_level": eff_lvl
    })

# ---- Bounties ----

@worldgen_bp.route('/add_bounty', methods=['POST'])
def add_bounty():
    data = request.json
    cid, region, amount = data["character_id"], data["region"], data["amount"]
    ref = db.reference(f"/bounties/{cid}")
    bounty = ref.get() or {}
    bounty[region] = bounty.get(region, 0) + amount
    ref.set(bounty)
    return jsonify(bounty)

@worldgen_bp.route('/check_bounty/<character_id>', methods=['GET'])
def check_bounty(character_id):
    bounty = db.reference(f"/bounties/{character_id}").get() or {}
    return jsonify(bounty)

@worldgen_bp.route('/decay_bounties', methods=['POST'])
def decay_bounties():
    all_bounties = db.reference("/bounties").get() or {}
    for cid, regions in all_bounties.items():
        for region in regions:
            regions[region] = int(regions[region] * 0.95)
        db.reference(f"/bounties/{cid}").set(regions)
    return jsonify({"message": "Bounties decayed."})

# ---- GPT Location Generation ----

@worldgen_bp.route('/generate_location_gpt', methods=['POST'])
def generate_location_gpt():
    data = request.get_json(force=True)
    x, y = data.get("x"), data.get("y")
    if x is None or y is None:
        return jsonify({"error": "Missing x or y coordinate"}), 400

    prompt = data.get("prompt", "Generate a fantasy location for a D&D-style world.")
    system_prompt = (
        "You are a worldbuilder AI. Generate a JSON object representing a fantasy map location. "
        "Include: name, description, danger_level (0-10), buildings (if any), npcs (if any), tags, and lore_hooks."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Prompt: {prompt}\nCoordinates: ({x},{y})"}
            ],
            temperature=0.8,
            max_tokens=500
        )
        location = json.loads(response.choices[0].message.content.strip())
        location["coordinates"] = {"x": x, "y": y}
        db.reference(f"/locations/{x}_{y}").set(location)
        log_gpt_usage("gpt-4o", response.get("usage", {}))
        return jsonify({"message": "Location generated and saved.", "location": location})
    except Exception as e:
        return jsonify({"error": f"GPT or Firebase error: {str(e)}"}), 500

# ---- ASCII Map ----

@worldgen_bp.route('/ascii_map', methods=['GET'])
def ascii_map():
    all_locations = db.reference('/locations').get() or {}
    GRID_SIZE = 21
    HALF_GRID = GRID_SIZE // 2
    grid = []
    for y in range(HALF_GRID, -HALF_GRID - 1, -1):
        row = ""
        for x in range(-HALF_GRID, HALF_GRID + 1):
            key = f"{x}_{y}"
            row += "@" if x == 0 and y == 0 else "L" if key in all_locations else "."
        grid.append(row)
    return "\n".join(grid), 200, {'Content-Type': 'text/plain'}

# ---- Motif Rotation ----

@worldgen_bp.route('/rotate_motifs/<character_id>', methods=['POST'])
def rotate_motifs_route(character_id):
    ref = db.reference(f'/characters/{character_id}')
    char = ref.get()
    if not char:
        return jsonify({"error": "Character not found."}), 404
    updated = complete_character(char)
    ref.set(updated)
    return jsonify({
        "message": "Character motifs rotated successfully.",
        "character_id": character_id,
        "active_motifs": updated.get("narrative_motif_pool", {}).get("active_motifs", [])
    }), 200
