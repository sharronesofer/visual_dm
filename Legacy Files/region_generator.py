import random
from collections import deque
import openai
import uuid
import json
from datetime import datetime
from typing import Set, Tuple, Dict, Any, List

from firebase_admin import db
from gpt_endpoints import log_gpt_usage

def generate_region_shape(
    seed_x: int,
    seed_y: int,
    min_tiles: int = 20,
    max_tiles: int = 40,
    direction_bias: float = 0.75
) -> Set[Tuple[int, int]]:
    """
    Generates a set of tile coordinates representing a contiguous region
    expanding from a seed (seed_x, seed_y).
    """
    target_size = random.randint(min_tiles, max_tiles)
    region_tiles = set()
    queue = deque()
    visited = set()

    seed = (seed_x, seed_y)
    queue.append(seed)
    region_tiles.add(seed)
    visited.add(seed)

    # Directions to explore
    directions = [
        (0, 1), (1, 0), (0, -1), (-1, 0),
        (1, 1), (1, -1), (-1, -1), (-1, 1)
    ]

    while queue and len(region_tiles) < target_size:
        current_tile = queue.popleft()
        random.shuffle(directions)
        for dx, dy in directions:
            # Only expand in this direction with 'direction_bias' probability
            if random.random() < direction_bias:
                neighbor = (current_tile[0] + dx, current_tile[1] + dy)
                if neighbor not in visited:
                    visited.add(neighbor)
                    region_tiles.add(neighbor)
                    queue.append(neighbor)
                    if len(region_tiles) >= target_size:
                        break

    return region_tiles


def generate_region(seed_x: int, seed_y: int) -> Dict[str, Any]:
    """
    Generates a fantasy region using GPT-4 for theming and faction data,
    then stores region info and tile references in Firebase.
    """
    region_id = f"region_{seed_x}_{seed_y}_{str(uuid.uuid4())[:8]}"
    tiles = generate_region_shape(seed_x, seed_y)

    # Prompt GPT for regional themes and density
    region_prompt = (
        "Generate a fantasy region for a tabletop world. Return JSON with:\n"
        "  {\n"
        "    \"region_name\": \"...\",\n"
        "    \"encouraged_land_types\": [3-5 land types],\n"
        "    \"forbidden_land_types\": [1-3 land types],\n"
        "    \"poi_density_cap\": (integer from 4 to 10)\n"
        "  }"
    )

    try:
        region_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a worldbuilding assistant."},
                {"role": "user", "content": region_prompt}
            ],
            temperature=0.85,
            max_tokens=300
        )
        log_gpt_usage("gpt-4", region_response.get("usage", {}))

        # Safely parse JSON returned by GPT
        region_data_str = region_response.choices[0].message.content.strip()
        region_meta = json.loads(region_data_str)
    except Exception as e:
        return {"error": f"GPT error while generating region theme: {e}"}

    region_name = region_meta.get("region_name", f"Unnamed {region_id}")
    region_meta["region_id"] = region_id
    region_meta["name"] = region_name
    region_meta["tiles"] = []

    # Partial updates for each tile so we don't overwrite other data
    for (x, y) in tiles:
        tile_key = f"{x}_{y}"
        tile_ref = db.reference(f"/locations/{tile_key}")

        # Just set or update region_id on the tile
        tile_ref.update({"region_id": region_id})

        region_meta["tiles"].append(tile_key)

    # Next: GPT to generate factions
    faction_prompt = (
        f"Generate 2 to 4 factions for a fantasy region called '{region_name}'.\n"
        f"Themes: encouraged = {region_meta.get('encouraged_land_types', [])},\n"
        f"        forbidden = {region_meta.get('forbidden_land_types', [])}.\n"
        "Include one primary government faction.\n"
        "Return a JSON list of factions, each with:\n"
        "  {\n"
        "    \"name\": \"...\",\n"
        "    \"alignment\": \"...\",\n"
        "    \"goals\": \"...\",\n"
        "    \"motto\": \"...\",\n"
        "    \"type\": \"government|religious|...\",\n"
        "    \"primary\": true|false\n"
        "  }"
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

        faction_json_str = faction_response.choices[0].message.content.strip()
        factions = json.loads(faction_json_str)

        region_meta["factions"] = []
        for faction in factions:
            faction_id = str(uuid.uuid4())
            faction["region"] = region_id

            # Store faction in Firebase
            db.reference(f"/factions/{faction_id}").set(faction)
            region_meta["factions"].append(faction_id)

            # If it's a primary government faction, link to region
            if faction.get("primary") and faction.get("type") == "government":
                region_meta["government_faction_id"] = faction_id

    except Exception as e:
        region_meta["faction_error"] = str(e)

    # Store final region metadata
    db.reference(f"/regions/{region_id}").set(region_meta)
    return region_meta


def update_region_arcs(
    region_id: str,
    arc_name: str,
    status: str,
    progress: int,
    quests: List[str],
    npc_reactions: Dict[str, Any]
) -> Dict[str, str]:
    """
    Adds or updates an arc in a region's metadata.
    """
    region_ref = db.reference(f"/regions/{region_id}")
    region_data = region_ref.get()

    if not region_data:
        return {"error": "Region not found"}

    current_arcs = region_data.get("current_arcs", [])

    # Check if an arc with this name already exists
    existing_arc = next((arc for arc in current_arcs if arc.get("arc_name") == arc_name), None)
    if existing_arc:
        # Update the existing arc in place
        existing_arc["status"] = status
        existing_arc["progress"] = progress
        existing_arc["quests"] = quests
        existing_arc["npc_reactions"] = npc_reactions
        existing_arc["last_updated"] = datetime.utcnow().isoformat()
    else:
        # Add a new arc
        current_arcs.append({
            "arc_name": arc_name,
            "status": status,
            "progress": progress,
            "quests": quests,
            "npc_reactions": npc_reactions,
            "last_updated": datetime.utcnow().isoformat()
        })

    region_ref.update({"current_arcs": current_arcs})

    return {"status": "Region arc updated", "region_id": region_id}
