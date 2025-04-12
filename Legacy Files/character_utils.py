import openai
import random
import math
import uuid
import json
from firebase_admin import db
from datetime import datetime
from gpt_integration import log_gpt_usage

with open("rules/land_types.json", "r") as f:
    land_type_meta = json.load(f)

REQUIRED_FIELDS = [
    "character_name", "characterType", "level", "class", "race", "gender", "alignment", "region_of_origin", "background",
    "HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", "XP", "feats", "skills", "proficiencies", "features", "spells",
    "equipment", "inventory", "notable_possessions",
    "known_languages", "faction_affiliations", "reputation", "personality_traits", "notable_relationships",
    "hidden_ambition", "hidden_compassion", "hidden_discipline", "hidden_impulsivity",
    "hidden_integrity", "hidden_pragmatism", "hidden_resilience",
    "private_goal_short_term", "private_goal_mid_term", "private_goal_long_term",
    "opinion_of_pc", "opinion_of_party", "narrative_motif_pool",
    "status_effects", "cooldowns", "gold"
]

def validate_npc(npc):
    for field in REQUIRED_FIELDS:
        if field not in npc:
            npc[field] = None
    return npc

def generate_motifs(n=3):
    return [{
        "theme": random.randint(1, 50),
        "lifespan": (life := random.randint(2, 4)),
        "entropy_tick": 0,
        "weight": 6 - life
    } for _ in range(n)]

def rotate_motifs_if_needed(pool):
    now = datetime.utcnow().isoformat()
    rotated = False
    active = []
    for motif in pool.get("active_motifs", []):
        motif["entropy_tick"] += 1
        if motif["entropy_tick"] < motif["lifespan"]:
            active.append(motif)
        else:
            rotated = True
            pool.setdefault("motif_history", []).append(motif["theme"])
    while len(active) < 3:
        life = random.randint(2, 4)
        new_motif = {
            "theme": random.randint(1, 50),
            "lifespan": life,
            "entropy_tick": 0,
            "weight": 6 - life
        }
        active.append(new_motif)
        pool.setdefault("motif_history", []).append(new_motif["theme"])
    if rotated:
        pool["last_rotated"] = now
    pool["active_motifs"] = active
    return pool

def complete_character(core):
    pool = core.get("narrative_motif_pool", {
        "active_motifs": generate_motifs(),
        "motif_history": [],
        "last_rotated": datetime.utcnow().isoformat()
    })
    core["narrative_motif_pool"] = rotate_motifs_if_needed(pool)

    # Default fields (if missing)
    core.setdefault("XP", 0)
    core.setdefault("alignment", "Neutral")
    core.setdefault("proficiencies", [])
    core.setdefault("features", [])
    core.setdefault("languages", ["Common"])
    core.setdefault("inventory", core.get("equipment", []))
    core.setdefault("faction_affiliations", [])
    core.setdefault("reputation", 0)
    core.setdefault("opinion_of_party", {})
    core.setdefault("hidden_ambition", "")
    core.setdefault("current_location", core.get("location", "Unknown"))
    core.setdefault("last_rest_timestamp", datetime.utcnow().isoformat())
    core.setdefault("rumor_index", [])
    core.setdefault("beliefs", {})
    core.setdefault("narrator_style", "Tolkien")
    return core

# === Skill Check Support ===
SKILL_TO_ABILITY = {
    "stealth": "DEX",
    "pickpocket": "DEX",
    "intimidate": "CHA",
    "diplomacy": "CHA",
    "persuasion": "CHA",
    "deception": "CHA",
    "perception": "WIS",
    "insight": "WIS",
    "arcana": "INT"
}

def perform_skill_check(character, skill, dc=12):
    ability = SKILL_TO_ABILITY.get(skill.lower(), "INT")
    modifier = (character.get(ability, 10) - 10) // 2
    if skill.lower() in [s.lower() for s in character.get("skills", [])]:
        modifier += 2
    roll = random.randint(1, 20)
    total = roll + modifier
    return {
        "skill": skill,
        "roll": roll,
        "modifier": modifier,
        "total": total,
        "success": total >= dc,
        "dc": dc
    }

def generate_npcs_for_poi(x, y):
    key = f"{x}_{y}"
    poi_ref = db.reference(f"/locations/{key}")
    poi_data = poi_ref.get()
    if not poi_data or not poi_data.get("POI"):
        return

    buildings = poi_data.get("buildings", [])
    terrain = poi_data.get("terrain", "grassland")
    region_id = poi_data.get("region_id", "default")
    tags = poi_data.get("tags", {})
    tone = tags.get("tone", "neutral")
    focus = tags.get("focus", "exploration")
    building_count = len(buildings) if isinstance(buildings, list) else 5

    base_npcs = building_count * 1.85
    terrain_mod = land_type_meta.get(terrain, {}).get("population_modifier", 1.0)

    if random.random() < 0.05:
        enclave_mod = random.uniform(2.0, 3.0)
        poi_data.setdefault("tags", {})["enclave"] = True
        poi_data["enclave_multiplier"] = enclave_mod

        building_prompt = f"The POI is an enclave. Generate additional buildings appropriate for a large city in a {terrain} biome."
        try:
            building_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate a list of buildings for a fantasy metropolis."},
                    {"role": "user", "content": building_prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            extra_buildings = building_response.choices[0].message.content.strip()
            log_gpt_usage("gpt-3.5-turbo", building_response.get("usage", {}))
            if isinstance(buildings, list):
                buildings.extend([b.strip() for b in extra_buildings.split("\n") if b.strip()])
                poi_data["buildings"] = buildings
        except Exception as e:
            poi_data["building_error"] = str(e)
    else:
        enclave_mod = 1.0

    all_pois = db.reference("/locations").get() or {}
    density_sum = 0
    for k, loc in all_pois.items():
        if k == key or not loc.get("POI"):
            continue
        loc_tags = loc.get("tags", {})
        if loc_tags.get("tone") not in ["friendly", "neutral"]:
            continue
        npcs_here = len(loc.get("npcs_present", []))
        try:
            px, py = map(int, k.split("_"))
            dist = math.sqrt((px - x) ** 2 + (py - y) ** 2)
            if dist > 0:
                density_sum += npcs_here / (dist ** 2)
        except:
            continue
    distance_mod = 1 / (1 + density_sum)

    tag_mod = 1.0
    if "crossroads" in tags:
        tag_mod *= 1.15
    if "water_access" in tags:
        tag_mod *= 1.15

    npc_count = round(base_npcs * terrain_mod * enclave_mod * distance_mod * tag_mod)
    npc_count = max(2, npc_count)

    prompt = (
        f"Generate {npc_count} detailed fantasy NPCs for a {tone} Point of Interest with a {focus} focus in a {terrain} biome.\n"
        f"Each NPC must be returned in strict JSON format, using a list of NPC objects.\n"
        f"Each must include fields from the game system, including stats, goals, inventory, and narrative_motif_pool."
    )

    try:
        npc_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a game master assistant. Return ONLY JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=1500
        )
        npc_json = npc_response.choices[0].message.content.strip()
        log_gpt_usage("gpt-4", npc_response.get("usage", {}))

        npc_list = json.loads(npc_json)
        npc_ids = []
        for npc in npc_list:
            npc_id = str(uuid.uuid4())
            validated = validate_npc(npc)
            completed_npc = complete_character(validated)
            db.reference(f"/npcs/{npc_id}").set({**completed_npc, "poi": key})
            npc_ids.append(npc_id)

        poi_data["npcs_present"] = npc_ids
        poi_ref.set(poi_data)
    except Exception as e:
        poi_data["npc_error"] = str(e)
        poi_ref.set(poi_data)

def generate_starting_city_and_region():
    key = "0_0"
    poi_ref = db.reference(f"/locations/{key}")
    if not poi_ref.get():
        try:
            lore_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate a fantasy capital city in JSON format with fields: name, description, danger_level, buildings (list), tags (tone, focus)."},
                    {"role": "user", "content": "Create a sprawling capital city for the region 'Sunveil Dominion'."}
                ],
                temperature=0.8,
                max_tokens=500
            )
            city_data = json.loads(lore_response.choices[0].message.content.strip())
            city_data["POI"] = True
            city_data["terrain"] = "grassland"
            city_data["region_id"] = "sunveil_dominion"
            poi_ref.set(city_data)
            generate_npcs_for_poi(0, 0)
        except Exception as e:
            poi_ref.set({"error": str(e)})

def create_player(player_id, name, race, class_type):
    generate_starting_city_and_region()
    core = {
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
        "languages": ["Common"]
    }
    finished = complete_character(core)
    db.reference(f"/players/{player_id}").set(finished)
    return finished

# === Status Effects ===
def apply_status_effect(target_id, effect_name, duration, source_id=None):
    ref = db.reference(f"/npcs/{target_id}")
    npc = ref.get()
    if not npc:
        return {"error": f"NPC {target_id} not found."}

    current_effects = npc.get("status_effects", [])
    effect_entry = {
        "name": effect_name,
        "duration": duration,
        "applied_by": source_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    current_effects.append(effect_entry)
    npc["status_effects"] = current_effects
    ref.set(npc)
    return {"status": "applied", "npc_id": target_id, "effect": effect_entry}

def resolve_status_effects(npc_id):
    ref = db.reference(f"/npcs/{npc_id}")
    npc = ref.get()
    if not npc:
        return {"error": f"NPC {npc_id} not found."}

    effects = npc.get("status_effects", [])
    updated_effects = []
    for effect in effects:
        effect["duration"] -= 1
        if effect["duration"] > 0:
            updated_effects.append(effect)

    npc["status_effects"] = updated_effects
    ref.set(npc)
    return {"npc_id": npc_id, "remaining_effects": updated_effects}

# === Cooldowns ===
def handle_cooldowns(npc_id):
    ref = db.reference(f"/npcs/{npc_id}")
    npc = ref.get()
    if not npc:
        return {"error": f"NPC {npc_id} not found."}

    cooldowns = npc.get("cooldowns", {})
    for key in list(cooldowns.keys()):
        cooldowns[key] = max(0, cooldowns[key] - 1)
        if cooldowns[key] == 0:
            del cooldowns[key]

    npc["cooldowns"] = cooldowns
    ref.set(npc)
    return {"npc_id": npc_id, "cooldowns": cooldowns}

# === Saving Throws ===
def resolve_saving_throw(stat_mod, dc):
    roll = random.randint(1, 20) + stat_mod
    success = roll >= dc
    return {"roll": roll, "modifier": stat_mod, "dc": dc, "success": success}

def get_total_party_level(party_id, mode="sum"):
    """
    Returns total or average party level depending on mode.
    Mode can be "sum" or "average"
    """
    party_ref = db.reference(f"/parties/{party_id}")
    party = party_ref.get()
    if not party:
        return 1

    total_level = 0
    count = 0

    for member_id in party.get("members", []):
        if member_id.startswith("player"):
            data = db.reference(f"/players/{member_id}").get()
        else:
            data = db.reference(f"/npcs/{member_id}").get()

        if data:
            total_level += data.get("level", 1)
            count += 1

    if count == 0:
        return 1

    return total_level if mode == "sum" else total_level // count

def award_xp_to_party(party_id, amount):
    ref = db.reference(f"/parties/{party_id}")
    party = ref.get()
    if not party:
        return {"error": "Party not found"}

    awarded = {}
    for member_id in party.get("members", []):
        if member_id.startswith("player"):
            char_ref = db.reference(f"/players/{member_id}")
        else:
            char_ref = db.reference(f"/npcs/{member_id}")
        char = char_ref.get() or {}
        char["XP"] = char.get("XP", 0) + amount
        char_ref.set(char)
        awarded[member_id] = char["XP"]

    return {"message": f"{amount} XP awarded to all members", "awarded": awarded}

