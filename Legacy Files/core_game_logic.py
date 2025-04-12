import os
import json
import random
import math
import uuid
import logging
from datetime import datetime, timezone, timedelta
from itertools import combinations
from random import randint

import openai
from openai import ChatCompletion
from firebase_admin import db

# (Continuing from the middle portion of your original code.)

# -----------------------------------------------
# Additional NPC / Relationship / Arc logic
# -----------------------------------------------

def generate_npcs_for_poi(x, y):
    """
    Generates NPCs for a POI at (x, y), possibly upgrading to an 'enclave' 
    and calling GPT for building expansions & population.
    """
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
    from file_gpt_memory import land_type_meta  # or inline if needed
    terrain_mod = land_type_meta.get(terrain, {}).get("population_modifier", 1.0)

    enclave_mod = 1.0
    if random.random() < 0.05:
        enclave_mod = random.uniform(2.0, 3.0)
        poi_data.setdefault("tags", {})["enclave"] = True
        poi_data["enclave_multiplier"] = enclave_mod

        building_prompt = f"The POI is an enclave. Generate extra buildings for a large city in a {terrain} biome."
        try:
            response = ChatCompletion.create(
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
            from file_gpt_memory import log_gpt_usage
            log_gpt_usage("gpt-3.5-turbo", usage)

            if isinstance(buildings, list):
                buildings.extend([b.strip() for b in extra_buildings.split("\n") if b.strip()])
                poi_data["buildings"] = buildings
        except Exception as e:
            poi_data["building_error"] = str(e)

    # Calculate density-based NPC count
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
            continue

    distance_mod = 1 / (1 + density_sum)
    tag_mod = 1.0
    if "crossroads" in tags:
        tag_mod *= 1.15
    if "water_access" in tags:
        tag_mod *= 1.15

    npc_count = round(base_npcs * terrain_mod * enclave_mod * distance_mod * tag_mod)
    npc_count = max(2, npc_count)

    prompt_text = (
        f"Generate {npc_count} detailed fantasy NPCs for a {tone} "
        f"POI with {focus} focus in a {terrain} biome.\n"
        "Return them in strict JSON format with fields: name, stats, goals, inventory, etc."
    )

    try:
        response = ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a game master assistant. Return ONLY JSON."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.85,
            max_tokens=1500
        )
        npc_json_str = response.choices[0].message.content.strip()
        usage = response.get("usage", {})
        from file_gpt_memory import log_gpt_usage
        log_gpt_usage("gpt-4", usage)

        npc_list = json.loads(npc_json_str)
        npc_ids = []
        from file_core_logic import validate_npc, complete_character

        for npc_data in npc_list:
            npc_id = str(uuid.uuid4())
            validated = validate_npc(npc_data)
            completed_npc = complete_character(validated)
            db.reference(f"/npcs/{npc_id}").set({**completed_npc, "poi": key})
            npc_ids.append(npc_id)

        poi_data["npcs_present"] = npc_ids
        poi_ref.set(poi_data)
    except Exception as e:
        poi_data["npc_error"] = str(e)
        poi_ref.set(poi_data)

def generate_starting_city_and_region():
    """
    Creates a default city at 0_0 if nonexistent, populates it with NPCs.
    """
    key = "0_0"
    poi_ref = db.reference(f"/locations/{key}")
    if poi_ref.get():
        return  # Already exists

    try:
        response = ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Generate a fantasy capital city in JSON with: name, description, danger_level, buildings, tags"
                },
                {
                    "role": "user",
                    "content": "Create a sprawling capital city for 'Sunveil Dominion'."
                }
            ],
            temperature=0.8,
            max_tokens=500
        )
        city_data = json.loads(response.choices[0].message.content.strip())
        city_data["POI"] = True
        city_data["terrain"] = "grassland"
        city_data["region_id"] = "sunveil_dominion"
        poi_ref.set(city_data)

        from file_core_logic import generate_npcs_for_poi
        generate_npcs_for_poi(0, 0)
    except Exception as e:
        poi_ref.set({"error": str(e)})

def create_player(player_id, name, race, class_type):
    """
    Creates a new player entry in DB, ensuring the starting region is set up.
    """
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
    from file_core_logic import complete_character
    finished = complete_character(core)
    db.reference(f"/players/{player_id}").set(finished)
    return finished

# === STATUS EFFECTS, COOLDOWNS, COMBAT UTILS

def handle_cooldowns(npc_id):
    """
    Decrements cooldown counters for an NPC. 
    If a cooldown hits 0, remove it.
    """
    ref = db.reference(f"/npcs/{npc_id}")
    npc = ref.get()
    if not npc:
        return {"error": f"NPC {npc_id} not found."}
    cooldowns = npc.get("cooldowns", {})
    for c_key in list(cooldowns.keys()):
        cooldowns[c_key] = max(0, cooldowns[c_key] - 1)
        if cooldowns[c_key] == 0:
            del cooldowns[c_key]
    npc["cooldowns"] = cooldowns
    ref.set(npc)
    return {"npc_id": npc_id, "cooldowns": cooldowns}

def resolve_saving_throw(stat_mod, dc):
    """
    Rolls d20 + stat_mod vs DC, returns success/fail.
    """
    roll_total = random.randint(1, 20) + stat_mod
    success = roll_total >= dc
    return {"roll": roll_total, "modifier": stat_mod, "dc": dc, "success": success}

def get_total_party_level(party_id, mode="sum"):
    """
    Sum or average the levels of all party members.
    """
    party = db.reference(f"/parties/{party_id}").get()
    if not party:
        return 1
    total = 0
    count = 0
    for member_id in party.get("members", []):
        if member_id.startswith("player"):
            data = db.reference(f"/players/{member_id}").get()
        else:
            data = db.reference(f"/npcs/{member_id}").get()
        if data:
            total += data.get("level", 1)
            count += 1
    if count == 0:
        return 1
    return total if mode == "sum" else total // count

def award_xp_to_party(party_id, amount):
    """
    Give XP to each member of a party.
    """
    ref = db.reference(f"/parties/{party_id}")
    party = ref.get()
    if not party:
        return {"error": "Party not found"}

    awarded = {}
    for m_id in party.get("members", []):
        if m_id.startswith("player"):
            c_ref = db.reference(f"/players/{m_id}")
        else:
            c_ref = db.reference(f"/npcs/{m_id}")
        char_data = c_ref.get() or {}
        char_data["XP"] = char_data.get("XP", 0) + amount
        c_ref.set(char_data)
        awarded[m_id] = char_data["XP"]

    return {"message": f"{amount} XP awarded", "awarded": awarded}


# === ARC & QUEST MANAGEMENT

def update_arc_progress(entity_type, entity_id, arc_name, progress, status="active", branch=None):
    """
    Update or add an arc for an entity (player or NPC).
    """
    ref = db.reference(f"/{entity_type}s/{entity_id}")
    data = ref.get() or {}
    current_arcs = data.get("current_arcs", [])
    updated = False

    for arc in current_arcs:
        if arc.get("arc_name") == arc_name:
            arc["progress"] = progress
            arc["status"] = status
            if branch:
                arc["branch"] = branch
            updated = True
            break

    if not updated:
        current_arcs.append({
            "arc_name": arc_name,
            "status": status,
            "progress": progress,
            "branch": branch or "default",
            "quests": [],
            "npc_reaction": "neutral",
            "is_primary": (entity_type == "player"),
            "hidden": False
        })

    ref.update({"current_arcs": current_arcs})
    return {"status": "updated", "arc": arc_name, "branch": branch, "progress": progress}


def complete_arc_and_trigger_next(player_id, arc_name, new_arc_name=None):
    """
    Complete a current arc for a player, possibly start a new arc.
    """
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    current_arc = player_data.get("current_arc", "")
    if current_arc == arc_name:
        player_ref.update({"current_arc_status": "completed"})
        if new_arc_name:
            update_player_arc(player_id, new_arc_name, arc_choices=[], arc_progress=0, npc_reactions={})
            return {"status": f"Arc '{arc_name}' done, '{new_arc_name}' triggered."}
    return {"status": f"Arc '{arc_name}' not active or already completed."}


def update_player_arc(player_id, arc_name, arc_choices, arc_progress, npc_reactions):
    """
    Update a player's current arc details.
    """
    ref = db.reference(f"/players/{player_id}")
    data = ref.get()
    if not data:
        return {"error": "Player not found"}
    ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })
    return {"status": "Player arc updated", "player_id": player_id}


def generate_quests_for_active_arc(player_id, arc_name, arc_progress):
    """
    Generate new quests based on arc progress.
    """
    ref = db.reference(f"/players/{player_id}")
    data = ref.get()
    if not data:
        return {"error": "Player not found"}
    if arc_name == data.get("current_arc") and arc_progress < 100:
        quests = []
        if arc_name == "The Fallen Noble":
            if arc_progress < 50:
                quests = ["recover_lost_legacy", "find_allies_in_exile"]
            else:
                quests = ["seek_revenge", "infiltrate_the_royal_palace"]
        from quest_tracker import append_to_existing_log
        for q in quests:
            append_to_existing_log(
                player_id=player_id, npc_name="NPC",
                summary=f"Quest generated: {q}"
            )
        return {"status": "New quests added", "quests": quests}
    return {"status": "Arc not active or done."}


def handle_event_and_progress_arc(entity_type, entity_id, event_name):
    """
    Example: if event_name == "kingdom_falls", complete an arc or start a new one.
    """
    if event_name == "kingdom_falls":
        update_arc_progress(entity_type, entity_id, "The Kingdom's Fall", 100, "completed")
        if entity_type == "player":
            update_arc_progress(entity_type, entity_id, "Rebuild the Kingdom", 0, "active")
    elif event_name == "rebellion_succeeds":
        update_arc_progress(entity_type, entity_id, "Revolutionary Victory", 100, "completed")
        if entity_type == "player":
            update_arc_progress(entity_type, entity_id, "The Rise of a New Order", 0, "active")
    return {"status": f"Event {event_name} processed."}


def trigger_arc_branch(player_id, arc_name, new_branch):
    """
    Trigger a new branch for a player's active arc.
    """
    ref = db.reference(f"/players/{player_id}")
    data = ref.get() or {}
    arcs = data.get("current_arcs", [])
    for arc in arcs:
        if arc.get("arc_name") == arc_name and arc.get("status") == "active":
            arc["branch"] = new_branch
            arc["npc_reaction"] = "shifted"
            ref.update({"current_arcs": arcs})
            return {"status": "branch triggered", "arc": arc_name, "branch": new_branch}
    return {"error": "Arc not found or inactive"}


def generate_npc_response_with_arc_context(npc_id, player_id, prompt):
    """
    Generate NPC response using arc context from both NPC and player.
    """
    n_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = n_ref.get()
    p_ref = db.reference(f"/players/{player_id}")
    player_data = p_ref.get()

    npc_arc = npc_data.get("current_arcs", [])
    player_arc = player_data.get("current_arc", "")
    if npc_arc:
        arc_context = f"NPC Arc: {npc_arc[-1]['arc_name']} ({npc_arc[-1]['status']})"
    else:
        arc_context = "NPC Arc: None"

    p_ctx = f"Player Arc: {player_arc}"
    full = f"{arc_context}\n{p_ctx}\n{prompt}"

    from file_gpt_memory import get_dm_response
    return get_dm_response("Arc Context", full, importance_score=7)
