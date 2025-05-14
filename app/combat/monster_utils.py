
#This module generates monster encounter groups appropriate for a player level, using stored JSON files and simple CR math. It is a content-loading and encounter-scaling tool.

import os
import json
from itertools import combinations
import openai

def load_monsters_from_folder(folder="rules/monsters"):
    monsters = []
    for fname in os.listdir(folder):
        if fname.endswith(".json"):
            with open(os.path.join(folder, fname)) as f:
                monsters.append(json.load(f))
    return monsters

def get_monster_group_for_player_level(player_level, region, poi_id):
    """
    Returns a thematically appropriate monster group for the player's level and POI context.
    Filters by region type and motif pressure.
    """
    all_monsters = db.reference("/rules/monsters").get() or {}

    # Load POI metadata
    poi_data = db.reference(f"/poi_state/{region}/{poi_id}").get() or {}
    region_type = poi_data.get("region_type", "forest")
    motifs = poi_data.get("motif_pool", {}).get("active_motifs", [])

    # 🧠 Tags to match: region + motifs
    motif_tags = [m["theme"] for m in motifs]
    target_cr = player_level + random.choice([-1, 0, 1])

    candidates = []
    for monster_id, data in all_monsters.items():
        if abs(data.get("estimated_cr", 0) - target_cr) > 1.5:
            continue
        if region_type not in data.get("tags", []) and not any(tag in data.get("tags", []) for tag in motif_tags):
            continue
        candidates.append((monster_id, data))

    if not candidates:
        return {"error": "No valid monsters found."}

    selected = random.choice(candidates)
    return {
        "group": [selected[1]],
        "flavor": generate_monster_flavor(selected[1], region_type, motif_tags)
    }

def generate_monster_flavor(monster, region_type, motif_tags):
    try:
        prompt = (
            f"This monster: {monster['name']} appears in a {region_type} region influenced by: {', '.join(motif_tags)}. "
            "Write a short atmospheric description."
        )
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fantasy horror narrator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return f"{monster['name']} lurks nearby."
