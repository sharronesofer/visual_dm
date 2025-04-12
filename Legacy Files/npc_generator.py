import openai
import random
import math
import uuid
import json
from firebase_admin import db

# External imports from your codebase
from gpt_endpoints import log_gpt_usage
from basic import complete_character

# -------------------------------------------------------
# Land Type Metadata and NPC Requirements
# -------------------------------------------------------

with open("rules/land_types.json", "r") as f:
    land_type_meta = json.load(f)

REQUIRED_FIELDS = [
    "character_name", "characterType", "level", "class", "race", "gender", "alignment", "region_of_origin", "background",
    "HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", "XP", "feats", "skills", "proficiencies", "features", "spells",
    "equipment", "inventory", "notable_possessions", "known_languages", "faction_affiliations", "reputation",
    "personality_traits", "notable_relationships", "hidden_ambition", "hidden_compassion", "hidden_discipline",
    "hidden_impulsivity", "hidden_integrity", "hidden_pragmatism", "hidden_resilience",
    "private_goal_short_term", "private_goal_mid_term", "private_goal_long_term", "opinion_of_pc", "opinion_of_party",
    "narrative_motif_pool", "status_effects", "cooldowns", "gold"
]

def validate_npc(npc):
    """
    Validates that the NPC dictionary has all the required fields.
    Any missing field is set to None for consistency.
    """
    for field in REQUIRED_FIELDS:
        if field not in npc:
            npc[field] = None
    return npc

# -------------------------------------------------------
# Primary Logic for Generating NPCs in a POI
# -------------------------------------------------------

def generate_npcs_for_poi(x, y):
    """
    Generates NPCs for a Point of Interest at (x, y) using GPT calls
    and stores them in Firebase under /npcs/.

    1. Fetch POI data from /locations/{x}_{y}.
    2. Check if it's a valid POI; if not, do nothing.
    3. Possibly convert it to an 'enclave' with extra buildings.
    4. Calculate how many NPCs to generate based on local densities.
    5. Call GPT to produce structured JSON NPC data, validate each NPC,
       and store them in Firebase.
    """
    key = f"{x}_{y}"
    poi_ref = db.reference(f"/locations/{key}")
    poi_data = poi_ref.get()

    if not poi_data or not poi_data.get("POI"):
        # Not a valid POI; exit early
        return

    # -----------------------------
    # Pull Basic Info
    buildings = poi_data.get("buildings", [])
    terrain = poi_data.get("terrain", "grassland")
    region_id = poi_data.get("region_id", "default")
    tags = poi_data.get("tags", {})
    tone = tags.get("tone", "neutral")
    focus = tags.get("focus", "exploration")

    # -----------------------------
    # Basic NPC Count Calculation
    building_count = len(buildings) if isinstance(buildings, list) else 5
    base_npcs = building_count * 1.85
    terrain_mod = land_type_meta.get(terrain, {}).get("population_modifier", 1.0)

    # -----------------------------
    # Possibly Convert POI into an Enclave
    # (Random 5% chance)
    if random.random() < 0.05:
        enclave_mod = random.uniform(2.0, 3.0)
        poi_data.setdefault("tags", {})["enclave"] = True
        poi_data["enclave_multiplier"] = enclave_mod

        building_prompt = (
            f"The POI is an enclave. Generate additional buildings "
            f"appropriate for a large city in a {terrain} biome."
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Generate a list of buildings for a fantasy metropolis."},
                    {"role": "user", "content": building_prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            extra_buildings = response.choices[0].message.content.strip()
            usage = response.get("usage", {})
            log_gpt_usage("gpt-3.5-turbo", usage)

            if isinstance(buildings, list):
                # Split lines, strip whitespace
                buildings.extend(b.strip() for b in extra_buildings.split("\n") if b.strip())
                poi_data["buildings"] = buildings
        except Exception as e:
            poi_data["building_error"] = str(e)
    else:
        enclave_mod = 1.0

    # -----------------------------
    # Calculate NPC Density Based on Surroundings
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
            dist = math.sqrt((px - x)**2 + (py - y)**2)
            if dist > 0:
                density_sum += npcs_here / (dist**2)
        except:
            # If any parse errors, skip
            continue

    # NPC density from existing friendly/neutral POIs
    distance_mod = 1 / (1 + density_sum)

    # Slight modifications for certain POI tags
    tag_mod = 1.0
    if "crossroads" in tags:
        tag_mod *= 1.15
    if "water_access" in tags:
        tag_mod *= 1.15

    # Final NPC Count
    npc_count = round(base_npcs * terrain_mod * enclave_mod * distance_mod * tag_mod)
    npc_count = max(2, npc_count)

    # -----------------------------
    # Prompt GPT for Strict JSON NPC Data
    prompt_text = (
        f"Generate {npc_count} detailed fantasy NPCs for a {tone} "
        f"Point of Interest with a {focus} focus in a {terrain} biome.\n"
        f"Each NPC must be returned in strict JSON format, with the following fields:\n"
        f"- character_name, characterType (must be 'NPC'), level, class, race, gender, alignment, region_of_origin, background\n"
        f"- HP, AC, STR, DEX, CON, INT, WIS, CHA, XP, feats, skills, proficiencies, features, spells\n"
        f"- equipment, inventory, notable_possessions\n"
        f"- known_languages, faction_affiliations, reputation, personality_traits, notable_relationships\n"
        f"- hidden_ambition, hidden_compassion, hidden_discipline, hidden_impulsivity,\n"
        f"  hidden_integrity, hidden_pragmatism, hidden_resilience\n"
        f"- private_goal_short_term, private_goal_mid_term, private_goal_long_term\n"
        f"- opinion_of_pc, opinion_of_party, narrative_motif_pool\n"
        f"- status_effects, cooldowns, gold"
    )

    try:
        npc_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a game master assistant. Return ONLY JSON."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.85,
            max_tokens=1500
        )
        npc_json_str = npc_response.choices[0].message.content.strip()
        usage = npc_response.get("usage", {})
        log_gpt_usage("gpt-4", usage)

        # Parse JSON
        npc_list = json.loads(npc_json_str)
        npc_ids = []

        # Validate and store each NPC
        for npc_data in npc_list:
            npc_id = str(uuid.uuid4())
            validated = validate_npc(npc_data)
            completed_npc = complete_character(validated)
            db.reference(f"/npcs/{npc_id}").set({
                **completed_npc,
                "poi": key
            })
            npc_ids.append(npc_id)

        poi_data["npcs_present"] = npc_ids
        poi_ref.set(poi_data)
    except Exception as e:
        # If GPT or JSON parse fails, store error in poi_data
        poi_data["npc_error"] = str(e)
        poi_ref.set(poi_data)

# -------------------------------------------------------
# Optional Additional NPC Arc Support
# -------------------------------------------------------

def update_npc_arcs(npc_id, arc_name, status, progress, quests, npc_reaction):
    """
    Adds or updates an arc in an NPC's 'current_arcs' list.
    Example usage:
        update_npc_arcs("npc_123", "A Strange Quest", "active", 10, ["find_sword"], "intrigued")
    """
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()
    if not npc_data:
        return {"error": "NPC not found"}

    npc_arcs = npc_data.get("current_arcs", [])

    # Check if an arc with this name already exists
    existing_arc = next((arc for arc in npc_arcs if arc.get("arc_name") == arc_name), None)
    if existing_arc:
        # Update the existing arc
        existing_arc["status"] = status
        existing_arc["progress"] = progress
        existing_arc["quests"] = quests
        existing_arc["npc_reaction"] = npc_reaction
    else:
        # Add a new arc
        npc_arcs.append({
            "arc_name": arc_name,
            "status": status,
            "progress": progress,
            "quests": quests,
            "npc_reaction": npc_reaction
        })

    npc_ref.update({"current_arcs": npc_arcs})

    return {"status": "Arc updated for NPC", "npc_id": npc_id}
