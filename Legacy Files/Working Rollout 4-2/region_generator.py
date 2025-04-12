import random
from collections import deque
import openai
import uuid
from firebase_admin import db
from gpt_endpoints import log_gpt_usage

# === Step 1: Generate Region Shape ===
def generate_region_shape(seed_x, seed_y, min_tiles=20, max_tiles=40):
    target_size = random.randint(min_tiles, max_tiles)
    region_tiles = set()
    queue = deque()
    visited = set()

    seed = (seed_x, seed_y)
    queue.append(seed)
    region_tiles.add(seed)
    visited.add(seed)

    direction_weights = [
        (0, 1), (1, 0), (0, -1), (-1, 0),
        (1, 1), (1, -1), (-1, -1), (-1, 1)
    ]

    while queue and len(region_tiles) < target_size:
        current = queue.popleft()
        random.shuffle(direction_weights)
        for dx, dy in direction_weights:
            if random.random() < 0.75:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor not in visited:
                    visited.add(neighbor)
                    region_tiles.add(neighbor)
                    queue.append(neighbor)
                    if len(region_tiles) >= target_size:
                        break

    return region_tiles

# === Step 2: Generate Region with GPT Themes and Factions ===
def generate_region(seed_x, seed_y):
    region_id = f"region_{seed_x}_{seed_y}_{str(uuid.uuid4())[:8]}"
    tiles = generate_region_shape(seed_x, seed_y)

    # GPT prompt for regional themes and density
    prompt = (
        "Generate a fantasy region for a tabletop world. "
        "Return JSON with: region_name, encouraged_land_types (3-5), forbidden_land_types (1-3), and poi_density_cap (integer 4-10)."
    )

    try:
        theme_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a worldbuilding assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=300
        )
        log_gpt_usage("gpt-4", theme_response.get("usage", {}))
        region_data = theme_response.choices[0].message.content.strip()
        region_meta = eval(region_data)  # Can be replaced with json.loads() if JSON is enforced

    except Exception as e:
        return {"error": f"GPT error: {e}"}

    region_name = region_meta.get("region_name", f"Unnamed {region_id}")
    region_meta.update({"region_id": region_id, "name": region_name, "tiles": []})

    # Update tiles and save to Firebase
    for x, y in tiles:
        key = f"{x}_{y}"
        tile_ref = db.reference(f"/locations/{key}")
        tile = tile_ref.get() or {}
        tile["region_id"] = region_id
        tile_ref.set(tile)
        region_meta["tiles"].append(key)

    # GPT faction generation
    faction_prompt = (
        f"Generate 2 to 4 factions for a fantasy region called '{region_name}'. "
        f"Themes: encouraged = {region_meta.get('encouraged_land_types', [])}, forbidden = {region_meta.get('forbidden_land_types', [])}. "
        "Include one primary government faction. Return a JSON list of factions. Each faction should have: name, alignment, goals, motto, type (e.g., government, religious), and primary (true/false)."
    )

    try:
        faction_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a creative fantasy faction designer."},
                {"role": "user", "content": faction_prompt}
            ],
            temperature=0.9,
            max_tokens=600
        )
        log_gpt_usage("gpt-4", faction_response.get("usage", {}))
        faction_json = faction_response.choices[0].message.content.strip()
        factions = eval(faction_json)  # Prefer json.loads in strict mode

        region_meta["factions"] = []
        for faction in factions:
            faction_id = str(uuid.uuid4())
            faction["region"] = region_id
            db.reference(f"/factions/{faction_id}").set(faction)
            region_meta["factions"].append(faction_id)

            if faction.get("primary") and faction.get("type") == "government":
                region_meta["government_faction_id"] = faction_id

    except Exception as e:
        region_meta["faction_error"] = str(e)

    db.reference(f"/regions/{region_id}").set(region_meta)
    return region_meta

# Example call:
# generate_region(10, 10)

def update_region_arcs(region_id, arc_name, status, progress, quests, npc_reactions):
    region_ref = db.reference(f"/regions/{region_id}")
    region_data = region_ref.get()

    if not region_data:
        return {"error": "Region not found"}

    # Update the region's active arcs
    current_arcs = region_data.get("current_arcs", [])
    current_arcs.append({
        "arc_name": arc_name,
        "status": status,
        "progress": progress,
        "quests": quests,
        "npc_reactions": npc_reactions
    })

    region_ref.update({"current_arcs": current_arcs})
    return {"status": "Region arc updated", "region_id": region_id}
