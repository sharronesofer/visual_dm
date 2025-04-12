import random
import math
import uuid
import json
import openai
from firebase_admin import db
from datetime import datetime

with open("rules/land_types.json", "r") as f:
    land_type_meta = json.load(f)

EMOTION_POOL = [
    "rage", "anxiety", "hope", "grief", "love", "jealousy", "serenity", "defiance", 
    "ambition", "fear", "envy", "despair", "excitement", "curiosity", "optimism"
]

REQUIRED_FIELDS = ["character_name", "characterType", "level", "class", "race", "gender", "alignment", "region_of_origin",
"HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", "inventory"]

def validate_npc(npc):
    for field in REQUIRED_FIELDS:
        npc.setdefault(field, None)
    return npc

def complete_character(core):
    core.setdefault("narrative_motif_pool", {})
    core.setdefault("inventory", [])
    return core

def generate_npcs_for_poi(x, y):
    key = f"{x}_{y}"
    poi_data = db.reference(f"/locations/{key}").get()
    if not poi_data:
        return

    terrain = poi_data.get("terrain", "grassland")
    base_npcs = len(poi_data.get("buildings", [])) * 2
    terrain_mod = land_type_meta.get(terrain, {}).get("population_modifier", 1.0)
    npc_count = max(2, round(base_npcs * terrain_mod))

    prompt = f"Generate {npc_count} NPCs for a {terrain} location. Provide JSON."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
        max_tokens=1500
    )

    npc_list = json.loads(response.choices[0].message.content.strip())
    npc_ids = []
    for npc in npc_list:
        npc_id = str(uuid.uuid4())
        validated_npc = validate_npc(npc)
        completed_npc = complete_character(validated_npc)
        db.reference(f"/npcs/{npc_id}").set({**completed_npc, "poi": key})
        npc_ids.append(npc_id)

    poi_data["npcs_present"] = npc_ids
    db.reference(f"/locations/{key}").set(poi_data)

def update_npc_location(npc_id):
    npc = db.reference(f"/npcs/{npc_id}").get()
    if not npc:
        return

    mobility = npc.get("mobility", {})
    home = mobility.get("home_poi")
    current = mobility.get("current_poi", home)
    radius = mobility.get("radius", 1)
    travel_chance = mobility.get("travel_chance", 0.15)

    if random.random() > travel_chance:
        return

    all_pois = db.reference("/locations").get() or {}
    valid_pois = []
    cx, cy = map(int, current.split("_"))
    for key in all_pois:
        if "POI" in all_pois[key]:
            x, y = map(int, key.split("_"))
            if 0 < math.sqrt((x - cx)**2 + (y - cy)**2) <= radius:
                valid_pois.append(key)

    if valid_pois:
        new_poi = random.choice(valid_pois)
        npc["mobility"]["current_poi"] = new_poi
        npc["mobility"]["last_moved"] = datetime.utcnow().isoformat()
        db.reference(f"/npcs/{npc_id}").set(npc)

def tick_npc_motifs(npc_id):
    npc = db.reference(f"/npcs/{npc_id}").get()
    if not npc:
        return

    entropy = npc.get("motif_entropy", {})
    for motif in npc.get("core_motifs", []):
        entropy[motif] = min(entropy.get(motif, 0) + 1, 5)

    emotional_flags = npc.get("emotional_flags", [])
    emotional_flags = [flag for flag in emotional_flags if (flag["duration"]:=flag["duration"]-1) > 0]

    if len(emotional_flags) < 3 and random.random() < 0.2:
        emotional_flags.append({
            "emotion": random.choice(EMOTION_POOL),
            "intensity": random.randint(1, 5),
            "duration": random.randint(1, 5)
        })

    npc.update({"motif_entropy": entropy, "emotional_flags": emotional_flags, "last_motif_tick": datetime.utcnow().isoformat()})
    db.reference(f"/npcs/{npc_id}").set(npc)

def propagate_beliefs(region_id):
    npcs = db.reference("/npcs").get() or {}
    poi_groups = {}
    for npc_id, npc in npcs.items():
        if npc.get("region_id") == region_id:
            poi_groups.setdefault(npc.get("mobility", {}).get("current_poi"), []).append(npc_id)

    for poi, npc_ids in poi_groups.items():
        for sender_id in npc_ids:
            sender_beliefs = db.reference(f"/npc_knowledge/{sender_id}/beliefs").get() or {}
            if sender_beliefs:
                belief_key, belief = random.choice(list(sender_beliefs.items()))
                for receiver_id in npc_ids:
                    if receiver_id != sender_id:
                        trust = db.reference(f"/npcs/{receiver_id}/relationships/{sender_id}").get().get("trust", 0)
                        if trust > 2 and random.random() < trust / 10:
                            db.reference(f"/npc_knowledge/{receiver_id}/beliefs/{belief_key}").set(belief)