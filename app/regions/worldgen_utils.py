import random
import json
from collections import deque
from datetime import datetime
from uuid import uuid4
import openai
from firebase_admin import db
import math
from app.utils.gpt_utils import log_gpt_usage

# Constants and metadata (example placeholder)
land_type_meta = {
    "grassland": {},
    "forest": {},
    "mountain": {},
    "desert": {},
    "swamp": {},
    "coast": {},
}

# Generate starting city and region

def generate_npcs_for_poi(region_name: str, poi_id: str):
    poi_ref = db.reference(f"/poi_state/{region_name}/{poi_id}")
    poi = poi_ref.get()
    if not poi:
        return {"error": f"POI {poi_id} in region {region_name} not found."}

    templates = db.reference("/npc_templates").get() or {}
    if not templates:
        return {"error": "No NPC templates available."}

    # Optional: scale number based on danger level or randomness
    num_npcs = random.randint(1, 3)
    generated_npcs = []

    for _ in range(num_npcs):
        template = random.choice(list(templates.values()))
        npc_id = f"npc_{uuid4().hex[:8]}"
        npc_data = {
            "id": npc_id,
            "character_name": template.get("name", "Unnamed NPC"),
            "race": template.get("race", "Human"),
            "class": template.get("class", "Commoner"),
            "level": template.get("level", 1),
            "location": {"region": region_name, "poi": poi_id},
            "stats": template.get("stats", {}),
            "motifs": {"active_motifs": [], "entropy": 0},
            "origin_template": template.get("id", "unknown")
        }

        # Save full NPC to database
        db.reference(f"/npcs/{npc_id}").set(npc_data)
        generated_npcs.append(npc_id)

    # Link to POI
    poi["npcs_present"] = generated_npcs
    poi_ref.set(poi)

    return {"npcs_generated": generated_npcs, "region": region_name, "poi": poi_id}

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

# Log a world event
def log_world_event(event_data):
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    event_data["event_id"] = event_id
    event_data["timestamp"] = datetime.utcnow().isoformat()
    db.reference(f"/global_state/world_log/{event_id}").set(event_data)
    return event_data

# Generate shape for a region
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

# Generate a detailed region
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

def refresh_cleared_pois():
    """
    Scans all POIs in all regions and resets those marked as 'cleared': true.
    Returns the number of POIs refreshed.
    """
    root = db.reference("/poi_state")
    all_regions = root.get() or {}
    count = 0

    for region_name, pois in all_regions.items():
        for poi_id, poi_data in pois.items():
            if poi_data.get("cleared") is True:
                poi_ref = db.reference(f"/poi_state/{region_name}/{poi_id}")
                # Example reset logic — feel free to expand
                poi_data["cleared"] = False
                poi_data["danger_level"] = poi_data.get("original_danger_level", 5)
                poi_ref.set(poi_data)
                count += 1

    return count

def generate_monsters_for_tile(x: int, y: int):
    """
    Returns a randomized list of monsters appropriate for the tile.
    Uses distance from origin to scale CR.
    """
    distance = math.sqrt(x**2 + y**2)
    frac = min(max((distance - 50) / 50, 0.0), 1.0) if distance > 50 else 0.0

    monsters = db.reference("/rules/monsters").get() or {}
    if not monsters:
        return []

    min_cr = max(round(frac * 0.5, 2), 0)
    max_cr = round(frac * 2.5 + 0.25, 2)

    valid = [
        m for m in monsters.values()
        if min_cr <= m.get("challenge_rating", 0) <= max_cr
    ]

    return random.sample(valid, min(3, len(valid)))

def attempt_rest(region_name, poi_id):
    ref = db.reference(f"/poi_state/{region_name}/{poi_id}")
    poi = ref.get() or {}

    danger = poi.get("danger_level", 0)
    attack_chance = danger * 0.10
    encounter_roll = random.random()

    rest_failed = encounter_roll < attack_chance
    encounter_type = None

    if rest_failed:
        non_combat_chance = 1 - 0.9 ** danger  # asymptotic
        encounter_type = "non-combat" if random.random() < non_combat_chance else "combat"

    return {
        "success": not rest_failed,
        "encounter_triggered": rest_failed,
        "encounter_type": encounter_type
    }
