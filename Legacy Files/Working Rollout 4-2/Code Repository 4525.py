Auth.py

from flask import Blueprint, request, jsonify
from firebase_admin import auth, db  # Firebase is already initialized in main.py

# Define a Blueprint for authentication-related routes
auth_bp = Blueprint('auth', __name__)

# Sign-Up Route
@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    try:
        # Use Firebase Auth to create a new user
        user = auth.create_user(email=email, password=password)

        # Store additional user information in Firebase Realtime Database
        user_ref = db.reference(f"/users/{user.uid}")
        user_ref.set({
            "username": username,
            "email": email,
            "character_data": {}  # Initially set empty character_data object
        })

        return jsonify({"message": "User created successfully", "user_id": user.uid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")  # Note: Firebase Admin SDK does not verify passwords directly

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Firebase Admin SDK cannot verify passwords directly, so you typically validate them on the client-side
        # Here, we just confirm the user exists in Firebase Auth
        user = auth.get_user_by_email(email)

        # Fetch user data from the Realtime Database
        user_ref = db.reference(f"/users/{user.uid}")
        user_data = user_ref.get()

        if not user_data:
            return jsonify({"error": "User data not found in database"}), 404

        return jsonify({
            "message": "Login successful",
            "user_id": user.uid,
            "username": user_data.get("username"),
            "character_data": user_data.get("character_data")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Logout Route
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Firebase Auth does not maintain server-side sessions, logout can be handled by client-side tokens.
    return jsonify({"message": "User logged out successfully"})


basic.py

Auth.py

from flask import Blueprint, request, jsonify
from firebase_admin import auth, db  # Firebase is already initialized in main.py

# Define a Blueprint for authentication-related routes
auth_bp = Blueprint('auth', __name__)

# Sign-Up Route
@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    try:
        # Use Firebase Auth to create a new user
        user = auth.create_user(email=email, password=password)

        # Store additional user information in Firebase Realtime Database
        user_ref = db.reference(f"/users/{user.uid}")
        user_ref.set({
            "username": username,
            "email": email,
            "character_data": {}  # Initially set empty character_data object
        })

        return jsonify({"message": "User created successfully", "user_id": user.uid}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Login Route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")  # Note: Firebase Admin SDK does not verify passwords directly

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        # Firebase Admin SDK cannot verify passwords directly, so you typically validate them on the client-side
        # Here, we just confirm the user exists in Firebase Auth
        user = auth.get_user_by_email(email)

        # Fetch user data from the Realtime Database
        user_ref = db.reference(f"/users/{user.uid}")
        user_data = user_ref.get()

        if not user_data:
            return jsonify({"error": "User data not found in database"}), 404

        return jsonify({
            "message": "Login successful",
            "user_id": user.uid,
            "username": user_data.get("username"),
            "character_data": user_data.get("character_data")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Logout Route
@auth_bp.route('/logout', methods=['POST'])
def logout():
    # Firebase Auth does not maintain server-side sessions, logout can be handled by client-side tokens.
    return jsonify({"message": "User logged out successfully"})

character_utils.py

import openai
import random
import math
import uuid
import json
from firebase_admin import db
from gpt_endpoints import log_gpt_usage

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

def complete_character(core):
    # Dummy safe version just for booting
    core["narrative_motif_pool"] = core.get("narrative_motif_pool", {})
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
        f"Generate {npc_count} detailed fantasy NPCs for a {tone} Point of Interest with a {focus} focus in a {terrain} biome."
        f"Each NPC must be returned in strict JSON format, with the following fields: \n"
        f"- character_name, characterType (must be 'NPC'), level, class, race, gender, alignment, region_of_origin, background \n"
        f"- HP, AC, STR, DEX, CON, INT, WIS, CHA, XP, feats, skills, proficiencies, features, spells \n"
        f"- equipment, inventory, notable_possessions \n"
        f"- known_languages, faction_affiliations, reputation, personality_traits, notable_relationships \n"
        f"- hidden_ambition, hidden_compassion, hidden_discipline, hidden_impulsivity, hidden_integrity, hidden_pragmatism, hidden_resilience \n"
        f"- private_goal_short_term, private_goal_mid_term, private_goal_long_term \n"
        f"- opinion_of_pc, opinion_of_party, narrative_motif_pool \n"
        f"- status_effects, cooldowns, gold"
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

# === Player Creator ===
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

combat_engine.py

from firebase_admin import db
from datetime import datetime
import uuid
import random
from openai import ChatCompletion

def roll_initiative(DEX):
    return random.randint(1, 20) + ((DEX - 10) // 2)

def start_combat(encounter_name, player_party, enemy_party, battle_map=None):
    battle_id = str(uuid.uuid4())
    all_participants = {}

    # Add players
    for pc in player_party:
        all_participants[pc["id"]] = {
            "name": pc["name"],
            "team": "party",
            "HP": pc.get("HP", 20),
            "AC": pc.get("AC", 12),
            "DEX": pc.get("DEX", 10),
            "initiative": roll_initiative(pc.get("DEX", 10)),
            "status_effects": [],
        }

    # Add enemies
    for npc in enemy_party:
        all_participants[npc["id"]] = {
            "name": npc["name"],
            "team": "hostile",
            "HP": npc.get("HP", 20),
            "AC": npc.get("AC", 12),
            "DEX": npc.get("DEX", 10),
            "initiative": roll_initiative(npc.get("DEX", 10)),
            "status_effects": [],
        }

    # Sort turn order
    turn_order = sorted(all_participants.items(), key=lambda kv: kv[1]["initiative"], reverse=True)
    turn_order_ids = [pid for pid, _ in turn_order]

    combat_state = {
        "battle_id": battle_id,
        "name": encounter_name,
        "participants": all_participants,
        "turn_order": turn_order_ids,
        "current_turn": 0,
        "battle_map": battle_map or {"type": "open", "lighting": "normal"},
        "started_at": datetime.utcnow().isoformat(),
        "log": []
    }

    db.reference(f"/combat_state/{battle_id}").set(combat_state)
    return battle_id, combat_state

def combat_tick(battle_id):
    import openai
    import json

    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()

    if not combat_data:
        return {"error": "Battle not found."}, 404

    turn_order = combat_data["turn_order"]
    current_index = combat_data.get("current_turn", 0)
    acting_id = turn_order[current_index]
    actor = combat_data["participants"].get(acting_id)

    if not actor:
        return {"error": "Invalid actor ID."}, 400

    # === PLAYER TURN ===
    if actor["team"] == "party":
        combat_data["log"].append(f"It is now {actor['name']}'s turn.")
        combat_data["current_turn"] = (current_index + 1) % len(turn_order)
        ref.set(combat_data)

        return {
            "acting_id": acting_id,
            "action": f"Waiting for player action ({actor['name']})",
            "log": combat_data["log"][-5:]
        }, 200

    # === NPC TURN → GPT DECISION ===
    participants = combat_data["participants"]
    context_lines = [
        f"{p['name']} (HP: {p['HP']}, Team: {p['team']})"
        for p in participants.values()
    ]
    context = "\n".join(context_lines)

    prompt = (
        f"You are controlling the NPC named {actor['name']} in a turn-based fantasy RPG battle.\n"
        f"Here are the combatants:\n{context}\n\n"
        f"Choose a reasonable action as JSON like:\n"
        f"{{\"action\": \"attack\", \"target\": \"player_1\", \"roll\": 17, \"value\": 9, \"notes\": \"slashes with scimitar\"}}\n\n"
        f"ONLY return the JSON."
    )

    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an NPC tactician in a fantasy battle."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        content = gpt_response.choices[0].message.content.strip()
        parsed = json.loads(content)

        # Extract values from GPT's structured response
        action_type = parsed.get("action", "attack")
        target_id = parsed.get("target")
        roll = parsed.get("roll", 10)
        value = parsed.get("value", 0)
        notes = parsed.get("notes", "")
        status_effect = parsed.get("status_effect")
        spell_name = parsed.get("spell_name")
        spell_level = parsed.get("spell_level")

        from combat_engine import apply_combat_action
        result, status = apply_combat_action(
            battle_id, acting_id, target_id, action_type, roll, value,
            notes, status_effect, spell_name, spell_level
        )
        return result, status

    except Exception as e:
        # Fallback: NPC hesitates
        fallback_log = f"{actor['name']} hesitates, unsure what to do. ({str(e)})"
        combat_data["log"].append(fallback_log)
        combat_data["current_turn"] = (current_index + 1) % len(turn_order)
        ref.set(combat_data)

        return {
            "acting_id": acting_id,
            "action": fallback_log,
            "log": combat_data["log"][-5:]
        }, 200


def apply_combat_action(battle_id, actor_id, target_id, action_type, roll, value, notes="", status_effect=None, spell_name=None):
    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()

    if not combat_data:
        return {"error": "Battle not found."}, 404

    current_index = combat_data.get("current_turn", 0)
    turn_order = combat_data.get("turn_order", [])
    if turn_order[current_index] != actor_id:
        return {"error": "It's not this character's turn."}, 400

    participants = combat_data["participants"]

    if actor_id not in participants or target_id not in participants:
        return {"error": "Invalid actor or target ID."}, 400

    actor = participants[actor_id]
    target = participants[target_id]

    narration = f"{actor['name']} uses {action_type}"
    if spell_name:
        narration = f"{actor['name']} casts {spell_name}"

    # === Handle result logic ===
    if action_type == "attack" and roll >= target.get("AC", 10):
        target["HP"] = max(0, target["HP"] - value)
        narration += f" and hits {target['name']} for {value} damage!"
    elif action_type == "heal":
        target["HP"] = target.get("HP", 0) + value
        narration += f" and heals {target['name']} for {value} HP!"
    else:
        narration += " but it fails."

    # === Handle status effect ===
    if status_effect:
        effect_obj = {"type": status_effect, "duration": 2}
        target.setdefault("status_effects", []).append(effect_obj)
        narration += f" {target['name']} is now {status_effect}!"

    if notes:
        narration += f" ({notes})"

    combat_data["participants"][target_id] = target
    combat_data.setdefault("log", []).append(narration)

    # === Tick status effects for all participants ===
    for p_id, pdata in participants.items():
        updated = []
        expired = []
        for effect in pdata.get("status_effects", []):
            effect["duration"] -= 1
            if effect["duration"] > 0:
                updated.append(effect)
            else:
                expired.append(effect["type"])
        pdata["status_effects"] = updated
        if expired:
            combat_data["log"].append(f"{pdata['name']} is no longer affected by {', '.join(expired)}.")

    # Advance turn
    combat_data["current_turn"] = (current_index + 1) % len(turn_order)
    ref.set(combat_data)

    return {
        "result": narration,
        "updated_target": target,
        "turn_advanced_to": combat_data["turn_order"][combat_data["current_turn"]],
        "log": combat_data["log"][-5:]
    }, 200

combat_utilities.py

from firebase_admin import db
from datetime import datetime, timedelta
import random

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

def resolve_saving_throw(stat_mod, dc):
    roll = random.randint(1, 20) + stat_mod
    success = roll >= dc
    return {"roll": roll, "modifier": stat_mod, "dc": dc, "success": success}

gpt_endpoints.py

from flask import Blueprint, request, jsonify
import json
import openai
from firebase_admin import db
import logging
from datetime import datetime
from rules_engine import lookup_rule  # ← Added for rule context
import random
from quest_tracker import append_to_existing_log

gpt_bp = Blueprint('gpt', __name__)
basic_bp = Blueprint('basic', __name__)

# --- Helper Functions for Arc Management ---
def update_arc_progress(entity_type, entity_id, arc_name, progress, status="active"):
    """ Update arc progress for an entity (player, npc, or region) """
    entity_ref = db.reference(f"/{entity_type}s/{entity_id}")
    entity_data = entity_ref.get()

    if not entity_data:
        return {"error": f"{entity_type} not found"}

    current_arcs = entity_data.get("current_arcs", [])
    updated = False
    for arc in current_arcs:
        if arc["arc_name"] == arc_name:
            arc["progress"] = progress
            arc["status"] = status
            updated = True
            break

    if not updated:
        current_arcs.append({
            "arc_name": arc_name,
            "status": status,
            "progress": progress,
            "quests": [],
            "npc_reaction": "neutral"
        })

    entity_ref.update({"current_arcs": current_arcs})
    return {"status": f"{arc_name} arc updated for {entity_type}", "entity_id": entity_id}


def complete_arc_and_trigger_next(player_id, arc_name, new_arc_name=None):
    """ Mark arc as completed and trigger the next arc """
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    current_arc = player_data.get("current_arc", "")
    if current_arc == arc_name:
        player_ref.update({"current_arc_status": "completed"})
        if new_arc_name:
            update_player_arc(player_id, new_arc_name, arc_choices=[], arc_progress=0, npc_reactions={})
            return {"status": f"Arc '{arc_name}' completed, and '{new_arc_name}' triggered."}

    return {"status": f"Arc '{arc_name}' is already completed or not found."}


def generate_quests_for_active_arc(player_id, arc_name, arc_progress):
    """ Generate quests based on active arc progress """
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    if arc_name == player_data.get("current_arc") and arc_progress < 100:
        quests = []
        if arc_name == "The Fallen Noble":
            if arc_progress < 50:
                quests = ["recover_lost_legacy", "find_allies_in_exile"]
            elif arc_progress >= 50 and arc_progress < 100:
                quests = ["seek_revenge", "infiltrate_the_royal_palace"]

        for quest in quests:
            append_to_existing_log(player_id, npc_name="NPC", summary=f"Quest generated: {quest}")

        return {"status": "New quests generated based on current arc.", "quests": quests}

    return {"status": "Arc is not active or progress is complete."}

def update_player_arc(player_id, arc_name, arc_choices, arc_progress, npc_reactions):
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    # Update the player's arc data
    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })

    # Optionally trigger a new arc after completing an old one
    # Example: Player finishes "The Fallen Noble" arc, trigger "Revenge of the Exiled"
    if arc_progress >= 100:
        # Trigger new arc logic here
        pass

    return {"status": "Player arc updated", "player_id": player_id}

def handle_event_and_progress_arc(entity_type, entity_id, event_name):
    # Handle specific event
    if event_name == "kingdom_falls":
        # If the player or NPC triggers the fall of a kingdom
        update_arc_progress(entity_type, entity_id, "The Kingdom's Fall", 100, "completed")
        # Trigger the next arc
        if entity_type == "player":
            new_arc_name = "Rebuild the Kingdom"
            update_arc_progress(entity_type, entity_id, new_arc_name, 0, "active")

    elif event_name == "rebellion_succeeds":
        # Another example event
        update_arc_progress(entity_type, entity_id, "Revolutionary Victory", 100, "completed")
        if entity_type == "player":
            new_arc_name = "The Rise of a New Order"
            update_arc_progress(entity_type, entity_id, new_arc_name, 0, "active")

    return {"status": f"Event '{event_name}' processed and arc progress updated."}

def generate_npc_response_with_arc_context(npc_id, player_id, prompt):
    # Fetch NPC and Player Arc Data
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()

    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    # Fetch the current arcs of both NPC and Player
    npc_arc = npc_data.get("current_arcs", [])
    player_arc = player_data.get("current_arc", "")

    # Add arc context to GPT prompt
    arc_context = f"NPC is currently involved in the arc: {npc_arc[-1]['arc_name']} (Status: {npc_arc[-1]['status']})"
    player_context = f"Player is currently in the arc: {player_arc}."

    full_prompt = f"{arc_context} {player_context} {prompt}"

    # Send the prompt to GPT with arc context
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()

# --- Existing Code ---
def build_dm_context():
    try:
        global_state = db.reference('/global_state').get() or {}
    except Exception as e:
        logging.error("Error fetching global state for DM context: %s", str(e))
        global_state = {}
    return f"Global State: {json.dumps(global_state)}"

def build_npc_context(npc_id, extra_context=""):
    try:
        npc_memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
        npc_knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    except Exception as e:
        logging.error("Error fetching NPC data for context: %s", str(e))
        npc_memory, npc_knowledge = {}, {}
    context = f"NPC Memory: {json.dumps(npc_memory)}; NPC Knowledge: {json.dumps(npc_knowledge)}"
    if extra_context:
        context += f"; {extra_context}"
    return context

def gpt_router(importance_score, flags=None):
    if flags is None:
        flags = {}
    if importance_score >= 7 or flags.get("force_gpt4", False):
        return "gpt-4"
    else:
        return "gpt-3.5-turbo"

def log_gpt_usage(model, usage):
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_ref = db.reference(f'/gpt_usage/{model}/{timestamp}')
        log_ref.set(usage)
    except Exception as e:
        logging.error("Error logging GPT usage: %s", str(e))

@basic_bp.route('/generate_location_gpt', methods=['POST'])
def generate_location_gpt():
    data = request.json
    x = data.get("x")
    y = data.get("y")
    prompt = data.get("prompt", "Generate a fantasy location for a D&D-style world.")
    
    if x is None or y is None:
        return jsonify({"error": "Missing x or y coordinate"}), 400

    system_prompt = (
        "You are a worldbuilder AI. Generate a JSON object representing a fantasy map location. "
        "It should include: name, description, danger_level (0-10), buildings (if any), npcs (if any), tags, and lore_hooks. "
        "Use JSON formatting only."
    )

    full_prompt = f"Prompt: {prompt}\nCoordinates: ({x},{y})\n"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )

        content = response.choices[0].message.content.strip()
        location_data = json.loads(content)

        location_data["coordinates"] = {"x": x, "y": y}
        location_key = f"{x}_{y}"
        db.reference(f"/locations/{location_key}").set(location_data)

        return jsonify({"message": "Location generated and saved.", "location": location_data})

    except Exception as e:
        return jsonify({"error": f"GPT or Firebase error: {str(e)}"}), 500

@gpt_bp.route('/npc_interact', methods=['POST'])
def npc_interact():
    from rules_engine import resolve_skill_check
    from utils.intent_utils import detect_skill_action
    from quest_tracker import append_to_existing_log  # ✅ NEW

    data = request.json
    npc_id = data.get("npc_id", "")
    conversation_history = data.get("conversation_history", "")
    prompt = data.get("prompt", "")
    importance_score = data.get("importance_score", 5)
    flags = data.get("flags", {})
    player_memory = data.get("player_memory", "")
    npc_motifs = data.get("npc_motifs", "")
    player_state = data.get("player_state", {})  # Pass this from frontend if possible
    player_id = data.get("player_id", "")  # ✅ REQUIRED for quest logging

    if not npc_id or not prompt:
        return jsonify({"error": "npc_id and prompt are required"}), 400

    # NPC context
    extra_context = ""
    if player_memory:
        extra_context += f"Player Memory: {player_memory}. "
    if npc_motifs:
        extra_context += f"NPC Motifs: {npc_motifs}. "

    npc_context = build_npc_context(npc_id, extra_context)

    # Skill detection
    skill_context = ""
    skill = detect_skill_action(prompt)
    if skill:
        stat_map = {
            "intimidate": "CHA",
            "diplomacy": "CHA",
            "stealth": "DEX",
            "pickpocket": "DEX"
        }
        ability = stat_map.get(skill, "CHA")
        ability_score = player_state.get(ability, 10)
        modifiers = player_state.get("modifiers", [])
        dc = 15

        skill_result = resolve_skill_check(skill, ability_score, modifiers, dc)
        skill_context = (
            f"Skill Check Result: {skill.title()} Roll = {skill_result['roll']} "
            f"vs DC {dc} → {'SUCCESS' if skill_result['success'] else 'FAILURE'}\n"
        )

    # Build prompt
    full_prompt = (
        f"{skill_context}"
        f"NPC Context: {npc_context}\n"
        f"Conversation History: {conversation_history}\n"
        f"Prompt: {prompt}"
    )

    model_to_use = gpt_router(importance_score, flags)

    response = openai.ChatCompletion.create(
        model=model_to_use,
        messages=[
            {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )

    reply = response.choices[0].message.content.strip()
    usage = response.get("usage", {})
    log_gpt_usage(model_to_use, usage)

    # ✅ QUEST HOOK DETECTION
    system_note = response.choices[0].message.get("function_call", {}).get("name", "")
    if "quest" in system_note.lower() and player_id:
        append_to_existing_log(
            player_id=player_id,
            npc_name=npc_id,
            summary=reply
        )

    # Update NPC Arc after interaction (if needed)
    # Example: If a certain action happens, trigger arc progression
    update_arc_progress('npc', npc_id, "The Fallen Noble", 50)  # You may replace this with dynamic logic

    return jsonify({
        "npc_id": npc_id,
        "reply": reply,
        "skill_used": skill,
        "model_used": model_to_use,
        "roll_context": skill_context.strip()
    })

@gpt_bp.route('/quest_log/<player_id>', methods=['GET'])
def get_quest_log(player_id):
    ref = db.reference(f"/quest_log/{player_id}")
    log = ref.get() or {}
    return jsonify(log)

@gpt_bp.route('/dm_response', methods=['POST'])
def dm_response():
    import re
    import random
    from datetime import datetime

    data = request.json
    prompt = data.get("prompt", "")
    importance_score = data.get("importance_score", 5)
    flags = data.get("flags", {})

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    # --- Dice Roller ---
    def roll_expression(expr):
        expr = expr.lower().strip().replace(" ", "")
        match = re.match(r"(\d*)d(\d+)([+-]\d+)?", expr)
        if not match:
            return f"Invalid: {expr}"
        num = int(match.group(1)) if match.group(1) else 1
        die = int(match.group(2))
        mod = int(match.group(3)) if match.group(3) else 0
        rolls = [random.randint(1, die) for _ in range(num)]
        total = sum(rolls) + mod
        breakdown = f"{' + '.join(map(str, rolls))}"
        if mod != 0:
            breakdown += f" {'+' if mod > 0 else '-'} {abs(mod)}"
        return f"{total} ({breakdown})"

    # --- Basic combat keyword detection ---
    def needs_combat_roll(text):
        combat_keywords = ["attack", "strike", "hit", "shoot", "swing", "stab", "slash", "cleave", "punch", "bash", "smash"]
        text = text.lower()
        return any(word in text for word in combat_keywords)

    # --- Create roll context based on intent ---
    roll_context = ""
    if needs_combat_roll(prompt):
        attack_result = roll_expression("1d20+5")
        damage_result = roll_expression("1d12+3")
        roll_context = f"Dice Results:\nAttack Roll = {attack_result}\nDamage Roll = {damage_result}"

    # --- System prompt ---
    system_instruction = (
        "You are the Dungeon Master narrating a persistent fantasy world.\n"
        "The player has declared an action. The system has rolled any required dice.\n"
        "You will receive those results as 'Dice Results', and you must narrate the outcome based on them.\n"
        "Include ONLY the outcome of the damage roll, if applicable."
    )

    # --- Global context ---
    dm_context = build_dm_context()
    full_prompt = f"DM Context: {dm_context}\n{roll_context}\nPrompt: {prompt}"
    model_to_use = gpt_router(importance_score, flags)

    # --- Send to GPT ---
    response = openai.ChatCompletion.create(
        model=model_to_use,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.8,
        max_tokens=200
    )

    raw_reply = response.choices[0].message.content.strip()
    reply = raw_reply

    # --- Log token usage (with sanitized path) ---
    usage = response.get("usage", {})
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_gpt_usage(model_to_use, usage)
    except Exception as e:
        import logging
        logging.error("Error logging GPT usage: %s", str(e))

    return jsonify({"reply": reply, "model_used": model_to_use})

@gpt_bp.route('/gpt_guess_action', methods=['POST'])
def gpt_guess_action():
    from openai import ChatCompletion
    user_input = request.json.get("text", "")
    prompt = f"What D&D 3.5e action is being described by: '{user_input}'?"
    response = ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert D&D parser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=100
    )
    return jsonify({"inferred_action": response.choices[0].message.content.strip()})

gpt_router.py

def gpt_router(score=5, flags=None):
    """
    Routes to the appropriate GPT model based on importance score and flags.

    Args:
        score (int): Importance score from 1–10
        flags (dict): Optional flags like {'emotional': True, 'plot': True}

    Returns:
        str: GPT model name (e.g. 'gpt-4o', 'gpt-3.5-turbo')
    """

    flags = flags or {}

    # Shortcut for major flags
    if flags.get("plot") or flags.get("secret") or flags.get("emotional"):
        return "gpt-4"

    # Score-based routing
    if score <= 3:
        return "gpt-4o-mini"  # cheap and fast
    elif 4 <= score <= 7:
        return "gpt-4o"  # balanced
    else:
        return "gpt-4"  # full power

loyalty_engine.py

from firebase_admin import db
import random

def loyalty_tick(npc_id, player_id, context_tags=None, cha_score=10):
    """
    Called once per combat or major scene.
    Adjusts goodwill based on loyalty, and handles potential betrayal if goodwill is too low.
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 5)
    tags = rel.get("tags", [])

    # Goodwill regeneration after event
    regen = 0
    if loyalty >= 10:
        regen = 3
    elif loyalty > 0:
        regen = 1
    elif loyalty <= -5:
        regen = 0

    goodwill += regen

    # Cap goodwill
    goodwill = min(goodwill, 10)

    rel["goodwill"] = goodwill
    rel_ref.set(rel)

    return {
        "npc_id": npc_id,
        "player_id": player_id,
        "loyalty": loyalty,
        "goodwill": goodwill,
        "tags": tags,
        "regen_applied": regen
    }

def apply_loyalty_event(npc_id, player_id, alignment_score):
    """
    Adjusts loyalty and goodwill based on a scored action (-5 to +5).
    alignment_score is the degree to which the action aligned with NPC hidden attributes.
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 5)
    tags = rel.get("tags", [])

    # Apply loyalty tag modifiers
    gain_mod, loss_mod = 1.0, 1.0
    if "loyalist" in tags:
        gain_mod = 1.5
        loss_mod = 0.5
    elif "coward" in tags:
        gain_mod = 0.5
        loss_mod = 1.5
    elif "bestie" in tags:
        loyalty = 10
    elif "nemesis" in tags:
        loyalty = -10

    if alignment_score > 0:
        loyalty += int(alignment_score * gain_mod)
        goodwill += 1
    elif alignment_score < 0:
        loyalty += int(alignment_score * loss_mod)
        goodwill -= abs(alignment_score)

    loyalty = max(-10, min(10, loyalty))
    goodwill = max(0, min(10, goodwill))

    rel.update({"loyalty": loyalty, "goodwill": goodwill})
    rel_ref.set(rel)

    return rel

def betrayal_check(npc_id, player_id, cha_score):
    """
    Runs when goodwill hits zero and loyalty is low.
    CHA check against DC = 10 + abs(loyalty)
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{player_id}")
    rel = rel_ref.get() or {}

    loyalty = rel.get("loyalty", 0)
    goodwill = rel.get("goodwill", 0)

    if goodwill > 0 or loyalty > 0:
        return {"status": "stable", "message": "No betrayal risk."}

    dc = 10 + abs(loyalty)
    roll = random.randint(1, 20) + int((cha_score - 10) / 2)

    outcome = "stays"
    if roll < dc:
        outcome = "betrays"

    return {
        "npc_id": npc_id,
        "player_id": player_id,
        "dc": dc,
        "roll": roll,
        "cha_score": cha_score,
        "outcome": outcome
    }

main.py

from flask import Flask
from basic import basic_bp
from gpt_endpoints import gpt_bp
from rules_endpoints import rules_bp  # ← New rules system
from auth import auth_bp  # Import the authentication blueprint
import firebase_admin
from firebase_admin import credentials
import json
import openai
from flask import send_from_directory
from rules_endpoints import rules_bp
from basic import relationship_bp

# Load OpenAI API key
try:
    with open("openai_api_key.json") as key_file:
        key_data = json.load(key_file)
    openai.api_key = key_data.get("api_key")
    if not openai.api_key:
        raise ValueError("No API key found in openai_api_key.json")
    print("OpenAI API key loaded successfully.")
except Exception as e:
    print("Failed to load OpenAI API key:", e)

# Initialize Firebase Admin SDK (Only once in main.py)
try:
    cred = credentials.Certificate('./firebase_credentials.json')  # Ensure this path is correct
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://visual-dm-default-rtdb.firebaseio.com/'  # Ensure this is your Firebase Realtime Database URL
    })
    print("Firebase initialized successfully.")
except Exception as e:
    print("Firebase initialization failed:", e)

# Initialize the Flask app
app = Flask(__name__)

# Register the blueprints
app.register_blueprint(basic_bp)
app.register_blueprint(gpt_bp)
app.register_blueprint(rules_bp)  # Register rules endpoints
app.register_blueprint(auth_bp, url_prefix='/auth')  # Register authentication endpoints with `/auth` prefix
app.register_blueprint(relationship_bp)

@app.route('/chat/')
def serve_index():
    return send_from_directory('.', 'chat.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)

def update_player_arc(player_id, arc_name, arc_choices, arc_progress, npc_reactions):
    # Update the player's arc data
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    # Update the player's arc data
    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })

    return {"status": "Player arc updated", "player_id": player_id}

memory_engine.py

import chromadb
from datetime import datetime, timedelta
import openai
from firebase_admin import db

client = chromadb.Client()
collection = client.get_or_create_collection(name="visual_dm_memory")

def store_log(entry: dict):
    """
    Stores a log entry in ChromaDB.
    Entry should contain: speaker, text, region, tags, timestamp
    """
    if "text" not in entry:
        return {"error": "Missing log text"}
    
    uid = f"{entry.get('speaker', 'unknown')}_{datetime.utcnow().isoformat()}"
    collection.add(
        documents=[entry["text"]],
        metadatas=[{
            "speaker": entry.get("speaker", "unknown"),
            "region": entry.get("region", "unknown"),
            "tags": entry.get("tags", []),
            "timestamp": datetime.utcnow().isoformat()
        }],
        ids=[uid]
    )
    return {"status": "stored", "id": uid}

def query_recent(speaker_id: str, region=None, n=5):
    """
    Returns top N most recent logs related to a speaker or region.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=3)  # short-term only

    results = collection.get(where={
        "$and": [
            {"speaker": speaker_id} if speaker_id else {},
            {"region": region} if region else {},
            {"timestamp": {"$gt": cutoff.isoformat()}}
        ]
    })

    # Sort by recency
    memory = sorted(results["metadatas"], key=lambda x: x["timestamp"], reverse=True)
    top = memory[:n]
    return [{"text": doc, "meta": meta} for doc, meta in zip(results["documents"], top)]

def summarize_memory(npc_id, player_id, logs):
    if not logs:
        return None

    text_lines = [f"- {log['text']}" for log in logs]
    prompt = (
        "You are an NPC in a fantasy roleplaying world. Summarize your recent interactions with the player.\n\n"
        "Recent Logs:\n"
        f"{chr(10).join(text_lines)}\n\n"
        "In 1–2 sentences, summarize what stood out to you and what you remember long-term:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a reflective NPC summarizing memory of the player."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def update_long_term_memory(npc_id, player_id, region=None):
    recent = query_recent(speaker_id=player_id, region=region, n=10)
    summary = summarize_memory(npc_id, player_id, recent)

    if summary:
        ref = db.reference(f"/npcs/{npc_id}/long_term_memory/{player_id}")
        ref.set({
            "last_summary": summary,
            "summary_date": datetime.utcnow().isoformat()
        })
        return {
            "npc_id": npc_id,
            "player_id": player_id,
            "summary": summary
        }
    else:
        return {"error": "No recent memory to summarize"}
    
    mobility_engine.py

    from firebase_admin import db
import random
import math
from datetime import datetime

def update_npc_location(npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()

    if not npc:
        return {"error": "NPC not found"}

    mobility = npc.get("mobility", {})
    home = mobility.get("home_poi")
    current = mobility.get("current_poi", home)
    radius = mobility.get("radius", 1)
    travel_chance = mobility.get("travel_chance", 0.15)

    if random.random() > travel_chance:
        return {"npc_id": npc_id, "stayed": True}

    # Find all POIs within range
    all_pois = db.reference("/locations").get() or {}
    valid = []

    try:
        cx, cy = map(int, current.split("_"))
    except:
        return {"error": "Invalid current_poi"}

    for key, poi in all_pois.items():
        if not poi.get("POI"):
            continue
        try:
            x, y = map(int, key.split("_"))
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if 0 < dist <= radius:
                valid.append(key)
        except:
            continue

    if not valid:
        return {"npc_id": npc_id, "stayed": True, "reason": "no valid POIs"}

    new_location = random.choice(valid)
    npc["mobility"]["current_poi"] = new_location
    npc["mobility"]["last_moved"] = datetime.utcnow().isoformat()
    npc_ref.set(npc)

    return {"npc_id": npc_id, "moved_to": new_location}

motif_engine.py

from firebase_admin import db
from datetime import datetime
import random

# Sample emotion pool (replace or expand)
EMOTION_POOL = [
    "rage", "melancholy", "anxiety", "hope", "grief", "love", 
    "jealousy", "serenity", "defiance", "regret", "ambition", 
    "happiness", "pride", "shame", "guilt", "fear", "envy", 
    "sorrow", "frustration", "despair", "elation", "embarrassment", 
    "contentment", "insecurity", "compassion", "resentment", "boredom", 
    "nervousness", "gratitude", "excitement", "disgust", "loneliness", 
    "affection", "sympathy", "passion", "righteousness", "hopelessness", 
    "curiosity", "surprise", "anticipation", "exhaustion", "wonder", 
    "doubt", "confusion", "relief", "inspiration", "pragmatism", 
    "melancholy", "nostalgia", "rage", "compromise", "clarity", 
    "rebellion", "stubbornness", "defeat", "bitterness", "fearlessness", 
    "submission", "optimism", "pessimism", "indifference", "disappointment", 
    "tenderness", "vulnerability", "understanding", "admiration", 
    "revulsion", "alienation", "humility", "acquiescence", "peace"
]


def tick_npc_motifs(npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()
    if not npc:
        return {"error": "NPC not found"}

    updated = False

    # --- Tick entropy ---
    entropy = npc.get("motif_entropy", {})
    for motif in npc.get("core_motifs", []):
        entropy[motif] = min(entropy.get(motif, 0) + 1, 5)
    npc["motif_entropy"] = entropy
    updated = True

    # --- Tick emotional flags ---
    emotional_flags = npc.get("emotional_flags", [])
    new_flags = []
    for flag in emotional_flags:
        flag["duration"] -= 1
        if flag["duration"] > 0:
            new_flags.append(flag)
    npc["emotional_flags"] = new_flags
    updated = True

    # --- Add new emotion? 20% chance ---
    if len(new_flags) < 3 and random.random() < 0.2:
        emotion = random.choice(EMOTION_POOL)
        intensity = random.randint(1, 5)
        duration = max(1, 6 - intensity)
        new_flags.append({
            "emotion": emotion,
            "intensity": intensity,
            "duration": duration
        })
        npc["emotional_flags"] = new_flags

    if updated:
        npc["last_motif_tick"] = datetime.utcnow().isoformat()
        npc_ref.set(npc)

    return {
        "npc_id": npc_id,
        "motif_entropy": npc["motif_entropy"],
        "emotional_flags": new_flags
    }

def get_npc_motif_prompt(npc_id):
    npc = db.reference(f"/npcs/{npc_id}").get()
    if not npc:
        return ""

    flags = npc.get("emotional_flags", [])
    phrases = []
    for flag in flags:
        label = f"{flag['emotion']} (intensity {flag['intensity']})"
        phrases.append(label)

    core_motifs = npc.get("core_motifs", [])
    entropy = npc.get("motif_entropy", {})
    motive_tags = [m for m in core_motifs if entropy.get(m, 0) >= 3]

    result = []
    if phrases:
        result.append("Emotional State: " + ", ".join(phrases))
    if motive_tags:
        result.append("Active Motivations: " + ", ".join(motive_tags))
    return " | ".join(result)

npc_generator.py

import openai
import random
import math
import uuid
import json
from firebase_admin import db
from gpt_endpoints import log_gpt_usage
from character_utils import complete_character

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
        f"Generate {npc_count} detailed fantasy NPCs for a {tone} Point of Interest with a {focus} focus in a {terrain} biome."
        f"Each NPC must be returned in strict JSON format, with the following fields: \n"
        f"- character_name, characterType (must be 'NPC'), level, class, race, gender, alignment, region_of_origin, background \n"
        f"- HP, AC, STR, DEX, CON, INT, WIS, CHA, XP, feats, skills, proficiencies, features, spells \n"
        f"- equipment, inventory, notable_possessions \n"
        f"- known_languages, faction_affiliations, reputation, personality_traits, notable_relationships \n"
        f"- hidden_ambition, hidden_compassion, hidden_discipline, hidden_impulsivity, hidden_integrity, hidden_pragmatism, hidden_resilience \n"
        f"- private_goal_short_term, private_goal_mid_term, private_goal_long_term \n"
        f"- opinion_of_pc, opinion_of_party, narrative_motif_pool \n"
        f"- status_effects, cooldowns, gold"
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

        def update_npc_arcs(npc_id, arc_name, status, progress, quests, npc_reaction):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()

    if not npc_data:
        return {"error": "NPC not found"}

    # Update the NPC's arcs
    npc_arcs = npc_data.get("current_arcs", [])
    npc_arcs.append({
        "arc_name": arc_name,
        "status": status,
        "progress": progress,
        "quests": quests,
        "npc_reaction": npc_reaction
    })

    npc_ref.update({"current_arcs": npc_arcs})
    return {"status": "Arc updated for NPC", "npc_id": npc_id}

party_engine.py

from firebase_admin import db
from datetime import datetime
import uuid

def create_party(player_id, npc_ids, party_name="Adventuring Party"):
    party_id = str(uuid.uuid4())
    members = [player_id] + npc_ids

    party_ref = db.reference(f"/parties/{party_id}")
    party_ref.set({
        "name": party_name,
        "members": members,
        "created_at": datetime.utcnow().isoformat()
    })

    db.reference(f"/players/{player_id}/party_id").set(party_id)
    for npc_id in npc_ids:
        db.reference(f"/npcs/{npc_id}/party_id").set(party_id)

    return party_id

def add_to_party(party_id, npc_id):
    party_ref = db.reference(f"/parties/{party_id}")
    party_data = party_ref.get()
    if not party_data:
        return False

    party_data["members"].append(npc_id)
    party_ref.set(party_data)
    db.reference(f"/npcs/{npc_id}/party_id").set(party_id)
    return True

quest_tracker.py

from firebase_admin import db
from datetime import datetime
import uuid

def create_quest_log_entry(player_id, npc_name, summary, region=None, poi=None):
    note_id = str(uuid.uuid4())
    log_ref = db.reference(f"/quest_log/{player_id}/{note_id}")
    log_data = {
        "note_id": note_id,
        "origin_npc": npc_name,
        "region": region or "unknown",
        "poi": poi or "unknown",
        "first_heard": datetime.utcnow().isoformat(),
        "status": "unresolved",
        "notes": [summary],
        "current_priority": 4
    }
    log_ref.set(log_data)
    return log_data

def append_to_existing_log(player_id, npc_name, summary):
    # Optional: if you want to group repeated notes from the same NPC
    ref = db.reference(f"/quest_log/{player_id}")
    logs = ref.get() or {}
    for log in logs.values():
        if log["origin_npc"] == npc_name and log["status"] == "unresolved":
            log["notes"].append(summary)
            log["current_priority"] += 1
            ref.child(log["note_id"]).set(log)
            return log
    return create_quest_log_entry(player_id, npc_name, summary)

region_generator.py

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

relationship_engine.py

from firebase_admin import db
import random
from datetime import datetime

# Constants for relationship type modifiers
RELATIONSHIP_MODIFIERS = {
    "trust": 2,
    "respect": 1.5,
    "envy": 1.2,
    "shared_history": 0.8
}

def update_relationships(npc_id, other_npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()
    other_npc_ref = db.reference(f"/npcs/{other_npc_id}")
    other_npc = other_npc_ref.get()

    if not npc or not other_npc:
        return {"error": "NPCs not found"}

    # Update relationships between two NPCs
    relationships = npc.get("relationships", {})
    other_relationship = relationships.get(other_npc_id, {})

    # Influence factors based on shared history and events
    influence_factor = 0

    # If they have shared history, increase or decrease based on event type
    shared_history = other_relationship.get("shared_history", [])
    if "helped_in_battle" in shared_history:
        influence_factor += 2  # Positive influence
    elif "betrayed_in_combat" in shared_history:
        influence_factor -= 3  # Negative influence

    # Apply relationship modifiers
    new_trust = min(10, max(-10, relationships.get("trust", 0) + influence_factor * RELATIONSHIP_MODIFIERS["trust"]))
    new_respect = min(10, max(-10, relationships.get("respect", 0) + influence_factor * RELATIONSHIP_MODIFIERS["respect"]))
    new_envy = min(10, max(-10, relationships.get("envy", 0) - influence_factor * RELATIONSHIP_MODIFIERS["envy"]))

    relationships[other_npc_id] = {
        "trust": new_trust,
        "respect": new_respect,
        "envy": new_envy,
        "shared_history": shared_history,
        "last_updated": datetime.utcnow().isoformat()
    }

    npc_ref.set(npc)
    return {
        "npc_id": npc_id,
        "other_npc_id": other_npc_id,
        "new_trust": new_trust,
        "new_respect": new_respect,
        "new_envy": new_envy
    }

def daily_relationship_tick():
    # Update NPC relationships for each NPC with all other NPCs
    all_npcs = db.reference("/npcs").get() or {}
    for npc_id, npc in all_npcs.items():
        relationships = npc.get("relationships", {})
        for other_npc_id in relationships:
            if other_npc_id != npc_id:
                update_relationships(npc_id, other_npc_id)

relationship_logic.py

# relationship_logic.py

from firebase_admin import db
from datetime import datetime
import random

RELATIONSHIP_MODIFIERS = {
    "trust": 2,
    "respect": 1.5,
    "envy": 1.2,
    "shared_history": 0.8
}

def update_relationships(npc_id, other_npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()
    other_npc_ref = db.reference(f"/npcs/{other_npc_id}")
    other_npc = other_npc_ref.get()

    if not npc or not other_npc:
        return {"error": "NPCs not found"}

    # Relationships are stored under npc["relationships"]
    relationships = npc.get("relationships", {})
    other_rel = relationships.get(other_npc_id, {
        "trust": 0,
        "respect": 0,
        "envy": 0,
        "shared_history": []
    })

    # Modify based on shared history
    history = other_rel.get("shared_history", [])
    influence_factor = 0
    if "helped_in_battle" in history:
        influence_factor += 2
    if "betrayed_in_combat" in history:
        influence_factor -= 3

    # Apply modifiers
    other_rel["trust"] = min(10, max(-10, other_rel.get("trust", 0) + influence_factor * RELATIONSHIP_MODIFIERS["trust"]))
    other_rel["respect"] = min(10, max(-10, other_rel.get("respect", 0) + influence_factor * RELATIONSHIP_MODIFIERS["respect"]))
    other_rel["envy"] = min(10, max(-10, other_rel.get("envy", 0) - influence_factor * RELATIONSHIP_MODIFIERS["envy"]))

    other_rel["last_updated"] = datetime.utcnow().isoformat()
    relationships[other_npc_id] = other_rel
    npc["relationships"] = relationships

    npc_ref.set(npc)
    return {
        "npc_id": npc_id,
        "target_npc_id": other_npc_id,
        "updated_relationship": other_rel
    }

def daily_relationship_tick():
    """
    Iterate over all NPCs and apply `update_relationships` logic
    to every pair with an existing relationship.
    """
    all_npcs = db.reference("/npcs").get() or {}
    for npc_id, npc in all_npcs.items():
        relationships = npc.get("relationships", {})
        for target_npc_id in relationships.keys():
            if target_npc_id != npc_id:
                update_relationships(npc_id, target_npc_id)

rules_endpoints.py

from flask import Blueprint, request, jsonify
from rules_engine import (
    validate_character_creation,
    resolve_skill_check,
    resolve_combat_action,
    lookup_rule,
    lookup_spell
)

rules_bp = Blueprint('rules', __name__)

@rules_bp.route('/validate_character_creation', methods=['POST'])
def validate_character():
    data = request.json
    if not data:
        return jsonify({"error": "Missing character data"}), 400
    result = validate_character_creation(data)
    return jsonify(result)

@rules_bp.route('/resolve_skill_check', methods=['POST'])
def resolve_skill():
    data = request.json
    skill = data.get("skill")
    ability_score = data.get("ability_score", 10)
    modifiers = data.get("modifiers", [])
    dc = data.get("dc", 10)

    if not skill:
        return jsonify({"error": "Missing skill name"}), 400

    result = resolve_skill_check(skill, ability_score, modifiers, dc)
    return jsonify(result)

@rules_bp.route('/resolve_combat_action', methods=['POST'])
def resolve_combat():
    data = request.json
    attacker = data.get("attacker", {})
    defender = data.get("defender", {})
    roll = data.get("roll", 10)

    result = resolve_combat_action(attacker, defender, roll)
    return jsonify(result)

@rules_bp.route('/lookup_rule', methods=['GET'])
def rule_lookup():
    category = request.args.get("category")
    name = request.args.get("name")

    if not category or not name:
        return jsonify({"error": "Missing category or name"}), 400

    result = lookup_rule(category, name)
    if not result:
        return jsonify({"error": f"{name} not found in {category}"}), 404
    return jsonify(result)

@rules_bp.route('/lookup_spell', methods=['GET'])
def spell_lookup():
    level = request.args.get("level")
    name = request.args.get("name")

    if not level or not name:
        return jsonify({"error": "Missing spell level or name"}), 400

    result = lookup_spell(level, name)
    if not result:
        return jsonify({"error": f"{name} not found at level {level}"}), 404
    return jsonify(result)

@rules_bp.route('/log_event_and_notify_npcs', methods=['POST'])
def log_event_and_notify():
    from rules_engine import log_world_event, sync_event_beliefs

    data = request.json
    if not data:
        return jsonify({"error": "Missing event data"}), 400

    region = data.get("region")
    if not region:
        return jsonify({"error": "Missing region name"}), 400

    try:
        event = log_world_event(data)
        count = sync_event_beliefs(region, event)
        return jsonify({
            "message": f"Event logged and shared with {count} NPCs.",
            "event_id": event["event_id"],
            "region": region
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Properly defined, clean, non-duplicate route
@rules_bp.route('/start_combat', methods=['POST'])
def api_start_combat():
    from combat_engine import start_combat

    data = request.json
    encounter_name = data.get("encounter_name", "Unnamed Encounter")
    player_party = data.get("player_party", [])
    enemy_party = data.get("enemy_party", [])
    battle_map = data.get("battle_map", {})

    if not player_party or not enemy_party:
        return jsonify({"error": "Both player_party and enemy_party are required"}), 400

    battle_id, combat_data = start_combat(encounter_name, player_party, enemy_party, battle_map)
    return jsonify({"battle_id": battle_id, "combat": combat_data})

@rules_bp.route('/combat_action', methods=['POST'])
def api_combat_action():
    from combat_engine import apply_combat_action

    data = request.json
    battle_id = data.get("battle_id")
    actor_id = data.get("actor_id")
    target_id = data.get("target_id")
    action_type = data.get("action", "attack")
    roll = data.get("roll", 10)
    value = data.get("value", 0)
    notes = data.get("notes", "")
    status_effect = data.get("status_effect")  # NEW
    spell_name = data.get("spell_name")        # NEW
    spell_level = data.get("spell_level")      # NEW

    if not all([battle_id, actor_id, target_id]):
        return jsonify({"error": "Missing required fields."}), 400

    result, status = apply_combat_action(
        battle_id, actor_id, target_id, action_type, roll, value,
        notes, status_effect, spell_name, spell_level
    )
    return jsonify(result), status

@rules_bp.route('/long_rest/<player_id>', methods=['POST'])
def long_rest(player_id):
    ref = db.reference(f"/players/{player_id}")
    data = ref.get()

    if not data or "spell_slots" not in data:
        return jsonify({"error": "Character not found or has no spell slots"}), 404

    for level, slot in data["spell_slots"].items():
        slot["used"] = 0

    ref.set(data)

    return jsonify({
        "message": f"{data.get('character_name', 'Character')} has completed a long rest.",
        "spell_slots": data["spell_slots"]
    })

@rules_bp.route('/request_rest', methods=['POST'])
def request_rest():
    import openai

    data = request.json
    player_id = data.get("player_id")
    location_description = data.get("location_description", "")
    current_threats = data.get("threats", [])
    narrative_context = data.get("narrative_context", "")

    if not player_id:
        return jsonify({"error": "Missing player_id"}), 400

    prompt = (
        f"The player is attempting to take a long rest.\n"
        f"Location: {location_description}\n"
        f"Threats nearby: {', '.join(current_threats) if current_threats else 'None'}\n"
        f"Context: {narrative_context}\n\n"
        f"Reply in the following format:\n"
        f"{{\"decision\": \"yes\" or \"no\", \"narration\": \"a short narrative describing why\"}}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fantasy RPG narrator deciding if a rest is safe."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=100
        )

        content = response.choices[0].message.content.strip()

        # Safe fallback
        import json
        try:
            result = json.loads(content)
            decision = result.get("decision", "").lower()
            narration = result.get("narration", "No narration provided.")
        except:
            decision = "no"
            narration = "You try to rest, but the forest feels uneasy..."

        if "yes" in decision:
            # Grant rest
            from firebase_admin import db
            ref = db.reference(f"/players/{player_id}")
            data = ref.get()

            if not data or "spell_slots" not in data:
                return jsonify({"error": "Character not found or has no spell slots"}), 404

            for level, slot in data["spell_slots"].items():
                slot["used"] = 0
            ref.set(data)

            return jsonify({
                "result": "Long rest granted.",
                "narration": narration,
                "spell_slots": data["spell_slots"]
            })

        else:
            return jsonify({
                "result": "Rest denied",
                "narration": narration
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rules_bp.route('/recruit_npc', methods=['POST'])
def recruit_npc():
    from party_engine import create_party, add_to_party

    data = request.json
    player_id = data.get("player_id")
    npc_id = data.get("npc_id")

    player_ref = db.reference(f"/players/{player_id}")
    npc_ref = db.reference(f"/npcs/{npc_id}")

    player = player_ref.get()
    npc = npc_ref.get()

    if not player or not npc:
        return jsonify({"error": "Invalid player or NPC ID"}), 400

    existing_party = player.get("party_id")
    if existing_party:
        success = add_to_party(existing_party, npc_id)
    else:
        existing_party = create_party(player_id, [npc_id])

    return jsonify({
        "message": f"{npc['character_name']} has joined your party!",
        "party_id": existing_party
    })

@rules_bp.route('/npc_loyalty_tick', methods=['POST'])
def npc_loyalty_tick():
    from loyalty_engine import loyalty_tick

    data = request.json
    npc_id = data.get("npc_id")
    player_id = data.get("player_id")
    cha_score = data.get("cha", 10)

    if not npc_id or not player_id:
        return jsonify({"error": "Missing npc_id or player_id"}), 400

    result = loyalty_tick(npc_id, player_id, cha_score=cha_score)
    return jsonify(result)

@rules_bp.route('/tension/<region_id>', methods=['GET'])
def api_get_tension(region_id):
    from tension_engine import get_tension
    return jsonify(get_tension(region_id))

@rules_bp.route('/tension/modify', methods=['POST'])
def api_modify_tension():
    from tension_engine import modify_tension
    data = request.json
    region_id = data.get("region_id")
    source = data.get("source")
    amount = data.get("amount", 0)

    if not region_id or not source:
        return jsonify({"error": "Missing region_id or source"}), 400

    return jsonify(modify_tension(region_id, source, amount))

@rules_bp.route('/tension/reset/<region_id>', methods=['POST'])
def api_reset_tension(region_id):
    from tension_engine import reset_tension
    return jsonify(reset_tension(region_id))

@rules_bp.route('/tension/decay/<region_id>', methods=['POST'])
def api_decay_tension(region_id):
    from tension_engine import decay_tension
    return jsonify(decay_tension(region_id))

@rules_bp.route('/npc/travel/<npc_id>', methods=['POST'])
def npc_travel(npc_id):
    from mobility_engine import update_npc_location
    return jsonify(update_npc_location(npc_id))

@rules_bp.route('/propagate_beliefs/<region_id>', methods=['POST'])
def rumor_propagation(region_id):
    from rumor_engine import propagate_beliefs
    result = propagate_beliefs(region_id)
    return jsonify({"messages": result, "region": region_id})

@rules_bp.route('/npc_motif_tick/<npc_id>', methods=['POST'])
def tick_motifs(npc_id):
    from motif_engine import tick_npc_motifs
    return jsonify(tick_npc_motifs(npc_id))

@rules_bp.route('/npc_relationship_tick', methods=['POST'])
def api_npc_relationship_tick():
    from relationship_engine import daily_relationship_tick
    daily_relationship_tick()
    return jsonify({"status": "NPC relationships updated"})

@rules_bp.route('/apply_status_effect', methods=['POST'])
def apply_status_effect():
    from combat_utilities import apply_status_effect
    data = request.json
    result = apply_status_effect(**data)
    return jsonify(result)

@rules_bp.route('/run_command_parser', methods=['POST'])
def run_command_parser():
    from command_parser import parse_action_command
    data = request.json
    result = parse_action_command(data.get("text", ""), data.get("context", {}))
    return jsonify(result)

rules_engine.py

import json
import os
from firebase_admin import db
from datetime import datetime
import random

# === Helper: Load JSON ===
def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return {}

# === Load Core Rules ===
skills = load_json("rules/skills.json")
classes = load_json("rules/classes.json")
feats = load_json("rules/feats.json")
abilities = load_json("rules/abilities.json")

# === Validate Character Creation ===
def validate_character_creation(data):
    issues = []
    name = data.get("name")
    race = data.get("race")
    cls = data.get("class")
    feats_input = data.get("feats", [])
    abilities_input = data.get("abilities", {})

    # Validate class
    class_data = classes.get(cls)
    if not class_data:
        issues.append(f"Invalid class: {cls}")

    # Validate abilities
    for ability, score in abilities_input.items():
        if ability not in abilities:
            issues.append(f"Unknown ability: {ability}")
        elif not isinstance(score, int):
            issues.append(f"Invalid score for {ability}: must be int")

    # Validate feats
    for feat in feats_input:
        if feat not in feats:
            issues.append(f"Unknown feat: {feat}")
        else:
            prereq = feats[feat].get("prerequisites", [])
            for condition in prereq:
                if condition.startswith("Str") and abilities_input.get("Strength", 0) < int(condition[-2:]):
                    issues.append(f"Missing prerequisite for {feat}: {condition}")
                # Additional parsing logic can be added here

    return {
        "character": name,
        "valid": len(issues) == 0,
        "issues": issues
    }

# === Resolve Skill Check ===
def resolve_skill_check(skill, ability_score, modifiers, dc):
    base = (ability_score - 10) // 2
    total = base + sum(modifiers)
    return {
        "skill": skill,
        "base": base,
        "modifiers": modifiers,
        "total": total,
        "dc": dc,
        "success": total >= dc
    }

# === Resolve Combat Action ===
def resolve_combat_action(attacker, defender, roll):
    bab = attacker.get("base_attack_bonus", 0)
    strength = attacker.get("strength_modifier", 0)
    attack_total = roll + bab + strength
    ac = defender.get("armor_class", 10)
    hit = attack_total >= ac
    return {
        "roll": roll,
        "base_attack_bonus": bab,
        "strength_modifier": strength,
        "attack_total": attack_total,
        "defender_ac": ac,
        "hit": hit,
        "combat_narration": f"Attack Roll: {roll} + {bab} (BAB) + {strength} (STR) = {attack_total} vs AC {ac} → {'HIT' if hit else 'MISS'}"
    }


# === Lookup Rule (Skill, Class, Feat, etc.) ===
def lookup_rule(category, name):
    name = name.strip()
    if category == "skill":
        return skills.get(name)
    elif category == "class":
        return classes.get(name)
    elif category == "feat":
        return feats.get(name)
    elif category == "ability":
        return abilities.get(name)
    return None

# === Lookup Spell ===
def lookup_spell(level, name):
    try:
        path = f"rules/spells/{int(level)}.json"
        spells = load_json(path)
        name_lower = name.strip().lower()
        for key, value in spells.items():
            if key.lower() == name_lower:
                return value
        return None
    except Exception as e:
        print(f"Spell lookup failed: {e}")
        return None
    
# --- Skill Intent Detection Helper ---
def detect_skill_action(text):
    text = text.lower()
    skill_map = {
        "stealth": ["sneak", "hide", "move silently", "avoid detection"],
        "pickpocket": ["steal", "lift", "pick pocket", "swipe"],
        "intimidate": ["intimidate", "threaten", "scare", "bully"],
        "diplomacy": ["persuade", "negotiate", "convince", "diplomacy", "talk down"]
    }

    for skill, keywords in skill_map.items():
        if any(kw in text for kw in keywords):
            return skill
    return None

# === WORLD STATE TRUTH EVENT LOGGING ===
def log_world_event(event_data):
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    event_data["event_id"] = event_id
    event_data["timestamp"] = datetime.utcnow().isoformat()
    ref = db.reference(f"/global_state/world_log/{event_id}")
    ref.set(event_data)
    return event_data

# === BELIEF GENERATION LOGIC ===
def distort_summary(summary):
    return summary.replace("was", "may have been").replace("at", "somewhere near")

def fabricate_alternate(event_data):
    return f"Someone claims {event_data.get('summary', 'something strange')} — but it sounds suspicious."

def generate_npc_belief(npc_name, event_data):
    trust_level = random.randint(1, 5)
    roll = random.random()
    if roll < trust_level / 5:
        accuracy = "accurate"
        belief_summary = event_data["summary"]
    elif roll < 0.8:
        accuracy = "partial"
        belief_summary = distort_summary(event_data["summary"])
    else:
        accuracy = "false"
        belief_summary = fabricate_alternate(event_data)

    return {
        "belief_summary": belief_summary,
        "accuracy": accuracy,
        "source": "world_log",
        "trust_level": trust_level,
        "heard_at": event_data.get("poi", "unknown")
    }

# === REGION-WIDE NPC SYNC ===
def sync_event_beliefs(region_name, event_data):
    poi_ref = db.reference(f"/poi_state/{region_name}")
    pois = poi_ref.get() or {}

    npc_belief_count = 0
    for poi_id, poi in pois.items():
        npcs = poi.get("npcs_present", [])
        for npc_name in npcs:
            belief = generate_npc_belief(npc_name, event_data)
            belief_ref = db.reference(f"/npc_knowledge/{npc_name}/beliefs/{event_data['event_id']}")
            belief_ref.set(belief)
            npc_belief_count += 1

    return npc_belief_count

encounter_scaling.py

from firebase_admin import db

def get_total_party_level(party_id):
    party_ref = db.reference(f"/parties/{party_id}")
    party = party_ref.get()
    if not party:
        return 1  # fallback if solo

    total_level = 0
    for member_id in party["members"]:
        if member_id.startswith("player"):
            data = db.reference(f"/players/{member_id}").get()
        else:
            data = db.reference(f"/npcs/{member_id}").get()

        if data:
            total_level += data.get("level", 1)

    return total_level

rumor_engine.py

import random
import openai
from firebase_admin import db

def propagate_beliefs(region_id):
    all_npcs = db.reference("/npcs").get() or {}
    by_poi = {}

    # Group by current POI (Place of Interest)
    for npc_id, npc in all_npcs.items():
        if npc.get("region_id") != region_id:
            continue
        poi = npc.get("mobility", {}).get("current_poi")
        if not poi:
            continue
        by_poi.setdefault(poi, []).append((npc_id, npc))

    results = []

    for poi, npc_group in by_poi.items():
        for sender_id, sender in npc_group:
            sender_beliefs = db.reference(f"/npc_knowledge/{sender_id}/beliefs").get() or {}
            if not sender_beliefs:
                continue

            belief_key = random.choice(list(sender_beliefs.keys()))
            belief = sender_beliefs[belief_key]

            for receiver_id, receiver in npc_group:
                if receiver_id == sender_id:
                    continue

                # Check if they interacted and trust each other
                rel = db.reference(f"/npcs/{receiver_id}/relationships/{sender_id}").get() or {}
                trust = rel.get("trust", 0)
                if trust < 2:
                    continue
                if random.random() > trust / 10:
                    continue  # Didn’t share this time

                # Mutate belief based on trust
                new_belief = mutate_belief_for_receiver(belief, trust_level=trust)
                db.reference(f"/npc_knowledge/{receiver_id}/beliefs/{belief_key}").set(new_belief)
                results.append((sender_id, receiver_id, new_belief["summary"]))

    return results

def mutate_belief_for_receiver(belief, trust_level):
    """
    Ask GPT to rewrite the belief based on trust level (1–5).
    """
    prompt = (
        f"An NPC hears the following rumor: '{belief['summary']}'\n"
        f"They trust the source at level {trust_level}.\n"
        f"Rewrite the belief summary they adopt. Make it less accurate if trust is low.\n"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fantasy NPC adjusting beliefs based on trust."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=100
        )

        summary = response.choices[0].message.content.strip()
        accuracy = min(1.0, 0.4 + 0.15 * trust_level)  # Adjusted for trust

        # Return belief with new summary, accuracy, and tags
        return {
            "summary": summary,
            "source": "rumor",
            "accuracy": accuracy,
            "trust_level": trust_level,
            "tags": belief.get("tags", [])
        }

    except Exception as e:
        return belief  # In case of error, return the original belief

tension_engine.py

from firebase_admin import db
from datetime import datetime

TENSION_LEVELS = [
    (0, 10, "peaceful"),
    (11, 30, "watchful"),
    (31, 60, "anxious"),
    (61, 80, "violent"),
    (81, 100, "collapsing")
]

def get_tension_descriptor(level):
    for min_val, max_val, label in TENSION_LEVELS:
        if min_val <= level <= max_val:
            return label
    return "unknown"

def get_tension(region_id):
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}
    level = data.get("level", 0)
    label = get_tension_descriptor(level)
    return {
        "region": region_id,
        "level": level,
        "label": label,
        "modifiers": data.get("modifiers", {})
    }

def modify_tension(region_id, source, amount):
    """
    Adjust regional tension by a numeric amount (positive or negative).
    Records the source modifier.
    """
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}

    modifiers = data.get("modifiers", {})
    modifiers[source] = modifiers.get(source, 0) + amount
    level = sum(modifiers.values())
    level = max(0, min(level, 100))  # clamp

    data.update({
        "level": level,
        "modifiers": modifiers,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

def reset_tension(region_id):
    ref = db.reference(f"/regions/{region_id}/tension")
    ref.set({
        "level": 0,
        "modifiers": {},
        "last_modified": datetime.utcnow().isoformat()
    })
    return get_tension(region_id)

def decay_tension(region_id, decay_rate=1):
    """
    Gradually reduce tension modifiers over time.
    """
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get()
    if not data:
        return {"error": "Region not found"}

    modifiers = data.get("modifiers", {})
    updated = {}
    for k, v in modifiers.items():
        if abs(v) > decay_rate:
            updated[k] = v - decay_rate if v > 0 else v + decay_rate

    level = sum(updated.values())
    level = max(0, min(level, 100))

    data.update({
        "level": level,
        "modifiers": updated,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

worldgen.py

import random
import json
from firebase_admin import db
import math

# Load local land type metadata
with open("rules/land_types.json", "r") as f:
    land_type_meta = json.load(f)

def choose_land_type(x, y, region_id):
    region_data = db.reference(f"/regions/{region_id}").get() or {}
    allowed = set(region_data.get("allowed_types", []))
    forbidden = set(region_data.get("forbidden_types", []))

    usage_data = db.reference("/land_type_usage").get() or {}

    neighbor_coords = [
        (x + dx, y + dy)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                       (-1, -1), (-1, 1), (1, -1), (1, 1)]
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
        if lt in neighbor_types:
            base_score += neighbor_types.count(lt)

        used = usage_data.get(lt, 0)
        base_score = base_score / (1 + used / 1000)

        rarity = land_type_meta.get(lt, {}).get("rarity", 5)
        base_score *= (11 - rarity)

        scores[lt] = base_score

    if not scores:
        return "grassland"

    total = sum(scores.values())
    weighted = [(lt, weight / total) for lt, weight in scores.items()]
    choices, weights = zip(*weighted)
    chosen = random.choices(choices, weights=weights)[0]

    db.reference(f"/terrain_map/{x}_{y}").set(chosen)
    db.reference(f"/land_type_usage/{chosen}").set(usage_data.get(chosen, 0) + 1)

    return chosen

def roll_danger_for_tile(x, y):
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    meta = land_type_meta.get(land_type, {})
    min_danger, max_danger = meta.get("danger_range", [0, 2])
    return random.randint(min_danger, max_danger)

def should_generate_poi(x, y):
    land_type = db.reference(f"/terrain_map/{x}_{y}").get()
    region_id = db.reference(f"/region_map/{x}_{y}").get() or "default"
    region_data = db.reference(f"/regions/{region_id}").get() or {}

    poi_cap = region_data.get("poi_density_cap", 10)  # max POIs allowed in region
    existing_pois = db.reference("/locations").get() or {}

    # Count POIs in this region
    pois_in_region = [loc for loc in existing_pois.values()
                      if loc.get("POI") and loc.get("region_id") == region_id]
    if len(pois_in_region) >= poi_cap:
        return False

    # Base POI chance from land type
    base_chance = land_type_meta.get(land_type, {}).get("poi_chance", 0.05)

    # Distance to nearest POI
    min_dist = float("inf")
    for key, loc in existing_pois.items():
        if loc.get("POI"):
            try:
                px, py = map(int, key.split("_"))
                dist = math.sqrt((px - x) ** 2 + (py - y) ** 2)
                if dist < min_dist:
                    min_dist = dist
            except:
                continue

    distance_bonus = min(1.0, min_dist / 10)  # full bonus at 10+ tiles
    final_chance = base_chance * distance_bonus

    return random.random() < final_chance

short_term_memory.py

# short_term_memory.py

import chromadb
from chromadb.config import Settings
from datetime import datetime
import uuid

chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_store"  # or wherever you're storing it
))

# Initialize memory collection
memory_collection = chroma_client.get_or_create_collection(name="npc_short_term_memory")

def store_interaction(npc_id, player_id, interaction_text, tags=None):
    memory_id = str(uuid.uuid4())
    metadata = {
        "npc_id": npc_id,
        "player_id": player_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if tags:
        metadata.update(tags)
    
    memory_collection.add(
        documents=[interaction_text],
        metadatas=[metadata],
        ids=[memory_id]
    )
    return memory_id

def get_recent_interactions(npc_id, player_id=None, limit=5):
    filters = {"npc_id": npc_id}
    if player_id:
        filters["player_id"] = player_id

    results = memory_collection.query(
        query_texts=["recent conversation"],
        n_results=limit,
        where=filters
    )
    return results["documents"][0] if results["documents"] else []
