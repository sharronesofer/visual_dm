import openai
import os
import json
import math
import random
import uuid
import logging
from datetime import datetime, timezone, timedelta
from itertools import combinations
from random import randint
import firebase_admin
import openai
from openai import ChatCompletion
from flask import Blueprint, request, jsonify, render_template, current_app
from firebase_admin import initialize_app, credentials, db

basic_bp = Blueprint("basic", __name__)
gpt_bp = Blueprint("gpt", __name__)
relationship_bp = Blueprint("relationship", __name__)
auth_bp = Blueprint("auth", __name__)

# basic.py
@basic_bp.route('/update_known_tiles/<character_id>', methods=['PATCH'])  # <-- PATCH here!
def update_known_tiles(character_id):
    data = request.get_json(force=True)

    ref = db.reference(f"/players/{character_id}")
    existing = ref.get()
    if not existing:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    # Only update fields explicitly provided:
    allowed_fields = ["known_tiles", "location"]
    for field in allowed_fields:
        if field in data:
            existing[field] = data[field]

    ref.set(existing)

    return jsonify({
        "message": "Character data patched successfully.",
        "updated_fields": {field: existing[field] for field in allowed_fields if field in data}
    }), 200

with open("openai_api_key.json") as f:
    data = json.load(f)
openai.api_key = data["api_key"]

# If referencing GPT usage from another module:
try:
    from gpt_endpoints import log_gpt_usage
except ImportError:
    def log_gpt_usage(*args, **kwargs):
        pass

# If referencing character validation from somewhere else, fallback stubs:
try:
    from character_utils import complete_character, validate_npc
except ImportError:
    def complete_character(npc_data):
        npc_data.setdefault("XP", 0)
        return npc_data

    def validate_npc(npc_data):
        return npc_data

# ==============================
# Example of Merged Function
# ==============================

conversation_mem = []   # list of {"role":..., "content":...}
summaries = []
char_count = 0          # track how many characters are in conversation_mem
MAX_CHARS = 5000        # the threshold at which we summarize
CHUNK_SIZE_CHARS = 2000 # how many characters to group for a summary

def store_message(role: str, content: str):
    """
    Stores the new message in memory. If the total character count 
    goes above MAX_CHARS, summarize the oldest CHUNK_SIZE_CHARS chunk.
    """
    global conversation_mem, summaries, char_count

    new_entry = {"role": role, "content": content}
    conversation_mem.append(new_entry)
    char_count += len(content)  # approximate measure

    # If we exceed MAX_CHARS, summarize the oldest chunk of size ~CHUNK_SIZE_CHARS
    while char_count > MAX_CHARS:
        # Summarize enough data from the front to free space
        chunk_to_summarize = []
        chunk_size = 0

        # Collect messages from the front until we hit ~CHUNK_SIZE_CHARS
        while conversation_mem and chunk_size < CHUNK_SIZE_CHARS:
            oldest = conversation_mem.pop(0)
            chunk_size += len(oldest["content"])
            char_count -= len(oldest["content"])
            chunk_to_summarize.append(oldest)

        # Summarize that chunk
        summary_text = gpt_summarize_chunk(chunk_to_summarize)
        # Store as one big summary
        summaries.append(summary_text)

def gpt_summarize_chunk(messages) -> str:
    """
    Summarize the list of messages into 1 short text. 
    Each item: {"role": "user"/"assistant", "content": "..."}.
    """
    import openai
    import logging

    try:
        combined_text = ""
        for m in messages:
            combined_text += f"{m['role'].upper()}: {m['content']}\n"

        system_prompt = {
            "role": "system",
            "content": (
                "You are summarizing a chunk of conversation. "
                "Return a concise summary in 1-2 sentences, ignoring fluff."
            )
        }
        user_prompt = {"role": "user", "content": combined_text}

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_prompt, user_prompt],
            temperature=0.5,
            max_tokens=200
        )
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        logging.error(f"Error summarizing chunk: {e}")
        return f"(Error summarizing chunk: {e})"


def roll_4d6_drop_lowest():
    """
    Roll 4d6, drop the lowest die, sum the remaining three.
    Returns a tuple: (total, [die1, die2, die3, die4]).
    """
    rolls = [random.randint(1, 6) for _ in range(4)]
    sorted_rolls = sorted(rolls)
    # drop the lowest
    total = sum(sorted_rolls[1:])
    return total, rolls

def generate_ability_scores():
    """
    Generates a dict of ability scores for STR, DEX, CON, INT, WIS, CHA,
    each using roll_4d6_drop_lowest.
    Returns something like:
    {
       "STR": {"total": 15, "rolls": [4,5,3,6]},
       "DEX": {"total": 12, "rolls": [6,2,2,4]},
       ...
    }
    """
    abilities = {}
    for ability in ["STR", "DEX", "CON", "INT", "WIS", "CHA"]:
        total, rolls = roll_4d6_drop_lowest()
        abilities[ability] = {
            "total": total,
            "rolls": rolls
        }
    return abilities

def generate_npcs_for_poi(x, y):
    """
    Merged from basic.py + npc_generator.py
    Generates NPCs for a POI at (x, y). Possibly converts it to an 'enclave' 
    with extra buildings. Calls GPT to produce structured NPC JSON.
    """
    key = f"{x}_{y}"
    poi_ref = db.reference(f"/locations/{key}")
    poi_data = poi_ref.get()
    if not poi_data or not poi_data.get("POI"):
        return  # Not a valid POI

    buildings = poi_data.get("buildings", [])
    terrain = poi_data.get("terrain", "grassland")
    region_id = poi_data.get("region_id", "default")
    tags = poi_data.get("tags", {})
    tone = tags.get("tone", "neutral")
    focus = tags.get("focus", "exploration")
    building_count = len(buildings) if isinstance(buildings, list) else 5

    base_npcs = building_count * 1.85
    # If referencing land_type_meta, ensure we load it or have fallback
    try:
        with open("rules/land_types.json") as f:
            land_type_meta = json.load(f)
        terrain_mod = land_type_meta.get(terrain, {}).get("population_modifier", 1.0)
    except:
        terrain_mod = 1.0

    # Possibly convert POI to an enclave
    enclave_mod = 1.0
    if random.random() < 0.05:
        enclave_mod = random.uniform(2.0, 3.0)
        poi_data.setdefault("tags", {})["enclave"] = True
        poi_data["enclave_multiplier"] = enclave_mod
        try:
            building_prompt = (
                f"The POI is an enclave. Generate additional buildings for a large city in {terrain}."
            )
            response = ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Generate a list of fantasy metropolis buildings."},
                    {"role": "user", "content": building_prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            extra_buildings = response.choices[0].message.content.strip()
            usage = response.get("usage", {})
            log_gpt_usage("gpt-4o-mini", usage)

            if isinstance(buildings, list):
                lines = [b.strip() for b in extra_buildings.split("\n") if b.strip()]
                buildings.extend(lines)
                poi_data["buildings"] = buildings
        except Exception as e:
            poi_data["building_error"] = str(e)

    # Calculate density-based NPC count
    all_pois = db.reference("/locations").get() or {}
    density_sum = 0
    for poi_key, loc_data in all_pois.items():
        if poi_key == key or not loc_data.get("POI"):
            continue
        if loc_data.get("tags", {}).get("tone") not in ["friendly", "neutral"]:
            continue
        num_npcs = len(loc_data.get("npcs_present", []))
        try:
            px, py = map(int, poi_key.split("_"))
            dist = math.sqrt((px - x)**2 + (py - y)**2)
            if dist > 0:
                density_sum += num_npcs / (dist**2)
        except:
            pass

    distance_mod = 1 / (1 + density_sum)
    tag_mod = 1.0
    if "crossroads" in tags:
        tag_mod *= 1.15
    if "water_access" in tags:
        tag_mod *= 1.15

    npc_count = round(base_npcs * terrain_mod * enclave_mod * distance_mod * tag_mod)
    npc_count = max(2, npc_count)

    # GPT prompt for strict JSON
    prompt_text = (
        f"Generate {npc_count} fantasy NPCs for a {tone} POI with focus {focus} in a {terrain} biome.\n"
        "Return them in strict JSON. Each must have stats, goals, inventory, narrative_motif_pool, etc."
    )

    try:
        npc_response = ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a game master assistant. Return ONLY JSON."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.85,
            max_tokens=1500
        )
        content = npc_response.choices[0].message.content.strip()
        usage = npc_response.get("usage", {})
        log_gpt_usage("gpt-4o", usage)

        data_list = json.loads(content)
        npc_ids = []
        for npc_data in data_list:
            npc_id = str(uuid.uuid4())
            validated = validate_npc(npc_data)
            completed = complete_character(validated)
            db.reference(f"/npcs/{npc_id}").set({**completed, "poi": key})
            npc_ids.append(npc_id)

        poi_data["npcs_present"] = npc_ids
        poi_ref.set(poi_data)

    except Exception as e:
        poi_data["npc_error"] = str(e)
        poi_ref.set(poi_data)


# ==============================
# RELATIONSHIP_Bp and other sections remain if needed
# ==============================


# === ChromaDB Imports for Memory Management ===
from chromadb import PersistentClient, Client

# Initialize Short-Term Memory (Chroma Persistent)
short_term_client = PersistentClient(path="./chroma_store")
short_term_collection = short_term_client.get_or_create_collection(name="npc_short_term_memory")

# Initialize Long-Term Memory (Chroma In-Memory or separate DB)
long_term_client = Client()
long_term_collection = long_term_client.get_or_create_collection(name="visual_dm_memory")

# -----------------------------------------------
# GPT Router, Logging, and Utility Functions
# -----------------------------------------------

def gpt_router(score=5, flags=None):
    """
    Routes to the appropriate GPT model based on importance score and flags.
    """
    flags = flags or {}

    # If certain flags are set, route togpt-4o:
    if flags.get("plot") or flags.get("secret") or flags.get("emotional"):
        return "gpt-4o"

    if flags.get("force_gpt4"):
        return "gpt-4o"

    # Score-based routing logic:
    if score <= 3:
        return "gpt-4o-mini"
    elif 4 <= score <= 7:
        return "gpt-4o"
    else:
        return "gpt-4o"

def classify_request(user_prompt: str) -> str:
    """
    Returns 'mechanical' if the text seems to involve game rules or stats,
    otherwise 'narrative'.
    """
    mechanics_keywords = [
        "roll", "damage", "armor class", "ac", "hp", "level up", "xp", 
        "skill check", "feats", "proficiency", "saving throw", "dc", 
        "bonus action", "initiative", "spell slot"
    ]
    text_lower = user_prompt.lower()
    for kw in mechanics_keywords:
        if kw in text_lower:
            return "mechanical"
    return "narrative"

def log_gpt_usage(model, usage):
    """
    Log GPT API usage data to Firebase for monitoring purposes.
    """
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_ref = db.reference(f'/gpt_usage/{model}/{timestamp}')
        log_ref.set(usage)
    except Exception as e:
        logging.error("Error logging GPT usage: %s", str(e))


def call_gpt_model(model, messages, temperature=0.7, max_tokens=150):
    """
    Make a call to the GPT API using the provided model and messages.
    Returns either a parsed JSON (if possible) or the raw text response.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        usage = response.get("usage", {})
        log_gpt_usage(model, usage)
        message_content = response.choices[0].message.content.strip()

        # Try to parse JSON
        try:
            return json.loads(message_content)
        except Exception:
            return message_content
    except Exception as e:
        logging.error(f"Error calling GPT model {model}: {str(e)}")
        return None

user_modes = {}  # e.g. { "<user_id>": "character_creation" or "normal" }

def generate_ability_scores():
    """
    Example 4d6-drop-lowest generator for each D&D ability.
    Returns a dict like:
      {
        "STR": { "total": 14, "rolls": [3, 6, 4, 1] },
        "DEX": { "total": 12, "rolls": [2, 5, 3, 4] },
        ...
      }
    """
    abilities = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    result = {}

    for ab in abilities:
        rolls = [random.randint(1, 6) for _ in range(4)]
        sorted_rolls = sorted(rolls)
        # drop the lowest
        total = sum(sorted_rolls[1:])
        result[ab] = {"total": total, "rolls": rolls}

    return result

def save_partial_character_data(player_id, field, value):
    """
    Store partial picks in /temp_characters/{player_id}/{field}.
    E.g., save_partial_character_data("user123", "race", "Dwarf")
    """
    temp_ref = db.reference(f"/temp_characters/{player_id}")
    data = temp_ref.get() or {}
    data[field] = value
    temp_ref.set(data)

def finalize_character_creation(player_id):
    """
    Move all partial data from /temp_characters/{player_id}
    into /players/{character_id}, and explicitly delete the temp node.
    """
    temp_ref = db.reference(f"/temp_characters/{player_id}")
    temp_data = temp_ref.get()
    if not temp_data:
        return {"error": "No partial data found."}, 404

    # Explicitly generate UUID for new character
    character_id = str(uuid.uuid4())

    # Explicitly build your final character data dict
    core = {
        "character_id": character_id,
        "player_id": player_id,
        "character_name": temp_data.get("name", "Unnamed"),
        "characterType": "Player Character",
        "race": temp_data.get("race", "Human"),
        "class": temp_data.get("class", "Fighter"),
        "region_of_origin": temp_data.get("region_of_origin", "DefaultRegion"),
        "location": "0_0",
        "region_id": "default_region",
        "XP": 0,
        "level": 1,
        "alignment": "Neutral",
        "inventory": [],
        "equipment": [],
        "languages": ["Common"],
    }

    # Explicitly copy ability_scores if stored
    if "ability_scores" in temp_data:
        for abbr, score_info in temp_data["ability_scores"].items():
            core[abbr] = score_info["total"]

    # Explicitly save final character under /players/{character_id}
    players_ref = db.reference(f"/players/{character_id}")
    players_ref.set(core)

    # Explicitly clean up temporary node
    temp_ref.delete()

    return {"message": "Character creation finalized", "character_id": character_id, "player_id": player_id}, 200

# --- Character Creation Endpoints ---
@basic_bp.route('/debug_routes', methods=['GET'])
def debug_routes():
    routes = [
        {"rule": str(rule), "methods": list(rule.methods), "endpoint": rule.endpoint}
        for rule in current_app.url_map.iter_rules()
    ]
    return jsonify(routes)

@basic_bp.route('/test_known_tiles/<character_id>', methods=['POST'])
def test_known_tiles(character_id):
    return jsonify({
        "message": "Route test successful.",
        "character_id": character_id
    }), 200

@basic_bp.route("/players/<character_id>", methods=["GET"])
def get_character(character_id):
    """
    Explicitly retrieves character data stored at /players/{character_id}.
    """
    ref = db.reference(f"/players/{character_id}")
    existing = ref.get()

    if not existing:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    return jsonify(existing), 200

@basic_bp.route('/debug_firebase_connection', methods=['GET'])
def debug_firebase_connection():
    try:
        root_ref = db.reference('/')
        data = root_ref.get()
        return jsonify({
            "success": True, 
            "root_keys": list(data.keys()) if data else [],
            "database_url": db.reference().path
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@gpt_bp.route('/dm_response', methods=['POST'])
def dm_response():
    data = request.get_json(force=True)
    mode = data.get("mode", "normal")
    user_prompt = data.get("prompt", "")
    user_id = data.get("user_id", "anonymous")

    if not user_prompt:
        return jsonify({"reply": "No prompt provided"}), 400

    user_ref = db.reference(f"/users/{user_id}")
    user_data = user_ref.get() or {}
    dm_mode = user_data.get("dm_mode", "normal")

    lowered = user_prompt.lower()

    if "create" in lowered and "character" in lowered:
        dm_mode = "character_creation"
        user_data["dm_mode"] = dm_mode
        user_ref.set(user_data)
        temp_ref = db.reference(f"/temp_characters/{user_id}")
        temp_data = {
            "creation_started": datetime.utcnow().isoformat(),
            "name": None,
            "race": None,
            "class": None,
            "ability_scores": {},
            "background": None
        }
        temp_ref.set(temp_data)
        scores = generate_ability_scores()
        save_partial_character_data(user_id, "ability_scores", scores)

    if "finish" in lowered or "done" in lowered:
        result = finalize_character_creation(user_id)
        dm_mode = "normal"
        user_data["dm_mode"] = dm_mode
        user_ref.set(user_data)
        return jsonify(result)

    if dm_mode == "character_creation":
        if "race" in lowered:
            if "dwarf" in lowered:
                save_partial_character_data(user_id, "race", "Dwarf")
            elif "elf" in lowered:
                save_partial_character_data(user_id, "race", "Elf")
        if "class" in lowered:
            if "wizard" in lowered:
                save_partial_character_data(user_id, "class", "Wizard")
            elif "fighter" in lowered:
                save_partial_character_data(user_id, "class", "Fighter")
        if "background" in lowered:
            if "noble" in lowered:
                save_partial_character_data(user_id, "background", "Noble")
            elif "soldier" in lowered:
                save_partial_character_data(user_id, "background", "Soldier")
        if "name is" in lowered:
            try:
                proposed_name = user_prompt.split("name is", 1)[1].strip()
                save_partial_character_data(user_id, "name", proposed_name)
            except Exception:
                pass

    if mode == "start_game":
        world_state = db.reference("/world_state").get() or {}
        character_id = data.get("character_id")

        if not character_id:
            return jsonify({"reply": "Missing character_id."}), 400

        character_data = db.reference(f"/players/{character_id}").get()
        if not character_data:
            return jsonify({"reply": f"No character found for ID {character_id}."}), 404

        prompt_content = (
            "Generate a detailed world overview for this fantasy RPG including the following sections:\n"
            "1) World Description\n"
            "2) Major Factions\n"
            "3) Religions\n"
            "4) Current Tensions\n"
            "5) A personalized starting quest hook for the character\n\n"
            "World Context:\n" + json.dumps(world_state, indent=2) + "\n\n"
            "Character Details:\n" + json.dumps(character_data, indent=2)
        )
        system_content = (
            "You are a worldbuilding assistant for a fantasy RPG. Produce output with clear section labels "
            "('World Description', 'Factions', 'Religions', 'Current Tensions', 'Quest Hook'), each on a new line."
        )
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt_content}
        ]

    else:
        try:
            classification_prompt = [
                {"role": "system", "content": (
                    "You are a text classifier. Respond ONLY with valid JSON: {\"style\": \"mechanical\"} or {\"style\": \"narrative\"}. "
                    "Use 'mechanical' for rules, stats, or mechanics; otherwise 'narrative'."
                )},
                {"role": "user", "content": user_prompt}
            ]
            classification_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=classification_prompt,
                temperature=0
            )
            classification_text = classification_resp.choices[0].message.content.strip()
            classification_data = json.loads(classification_text)
            user_style = classification_data.get("style", "narrative")
        except Exception as e:
            logging.error(f"Classification error: {e}")
            user_style = "narrative"

        system_content = (
            "You are a D&D rules assistant. Respond succinctly with mechanics and rules."
            if user_style == "mechanical"
            else "You are the Dungeon Master in a fantasy RPG. Respond immersively with detailed narrative."
        )
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = f"Error calling GPT: {e}"

    return jsonify({"reply": reply_text})

def get_character_creation_prompt():
    return {
        "role": "system",
        "content": (
            "You are assisting with a straightforward character creation process. "
            "Use a direct, factual, and concise style without flowery language. "
            "Only ask relevant questions about name, race, class, background, personality traits, etc."
        )
    }
def get_npc_response(npc_context, conversation_history, prompt, importance_score=5, flags=None, temperature=0.7, max_tokens=150):
    """
    High-level NPC prompt function: returns a system-level 'NPC in a persistent fantasy world' response.
    """
    model = gpt_router(score=importance_score, flags=flags)
    messages = [
        {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation. Take a look at your character sheet and respond based on that information. Please structure your response as dialogue, separated by blank lines. Do not combine everything into a single paragraph."},
        {"role": "user", "content": f"NPC Context: {npc_context}\nConversation History: {conversation_history}\nPrompt: {prompt}"}
    ]
    return call_gpt_model(model, messages, temperature, max_tokens)

def score_interaction(flags: dict) -> int:
    """
    Returns an importance score (1–10) based on interaction flags.
    This feeds into GPT model routing.
    """
    if not flags:
        return 5

    score = 5
    if flags.get("emotionally_charged"):
        score += 2
    if flags.get("conflict_type") in ["loyalty", "morality", "betrayal"]:
        score += 2

    scope = flags.get("scope", "")
    if scope == "regional":
        score += 1
    elif scope == "global":
        score += 2

    if flags.get("force_gpt4"):
        return 10

    return min(score, 10)

# -----------------------------------------------
# LAND TYPES, CHARACTER VALIDATION, AND MOTIFS
# -----------------------------------------------

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
    """
    Ensures the NPC dictionary has all REQUIRED_FIELDS.
    Any missing field is set to None to maintain consistency.
    """
    for field in REQUIRED_FIELDS:
        if field not in npc:
            npc[field] = None
    return npc

def generate_motifs(n=3):
    """
    Generates a list of motif objects with random theme, lifespan, and weight.
    """
    return [{
        "theme": random.randint(1, 50),
        "lifespan": (life := random.randint(2, 4)),
        "entropy_tick": 0,
        "weight": 6 - life
    } for _ in range(n)]

def rotate_motifs_if_needed(pool):
    """
    Increments entropy_tick of active motifs. 
    If motifs expire, they are moved to motif_history, and new motifs are generated.
    """
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
    """
    Ensures the character dictionary has all key fields for gameplay, 
    including narrative_motif_pool, XP, alignment, and various defaults.
    Calls rotate_motifs_if_needed to manage motif expiration.
    """
    pool = core.get("narrative_motif_pool", {
        "active_motifs": generate_motifs(),
        "motif_history": [],
        "last_rotated": datetime.utcnow().isoformat()
    })
    core["narrative_motif_pool"] = rotate_motifs_if_needed(pool)

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
    core.setdefault("narrator_style", "ToA mix between Cormac McCarthy, Lovecraft, and Herman Melvillelkien")
    return core
    core.setdefault("dr", sum(equip["dr"] for equip in equipment if "dr" in equip))  # BAD if equip = names

# -----------------------------------------------
# SKILL CHECK MAPPING
# -----------------------------------------------
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
    """
    Performs a skill check based on the character's ability modifier and 
    any proficiency in the given skill. Returns result details.
    """
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

# -----------------------------------------------
# MONSTER LOADING
# -----------------------------------------------
def load_monsters_from_folder():
    """
    Loads monster JSON data from the 'rules/monsters' folder 
    and returns a list of monster dicts.
    """
    monster_dir = "rules/monsters"
    monsters = []
    for fname in os.listdir(monster_dir):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(monster_dir, fname)) as f:
                    monster = json.load(f)
                    monsters.append(monster)
            except Exception as e:
                print(f"Failed to load {fname}: {e}")
    return monsters

ALL_MONSTERS = load_monsters_from_folder()

def get_monster_group_for_player_level(player_level):
    """
    Returns a small group of monsters from ALL_MONSTERS whose total CR 
    is suitable for the given player level, using minimal or no advanced logic.
    """
    min_cr = round(player_level * 0.25 - 0.25, 2)
    max_cr = round(player_level * 0.25 + 0.25, 2)
    candidates = [m for m in ALL_MONSTERS if min_cr <= m["challenge_rating"] <= max_cr]
    if not candidates:
        return []
    best_combo = []
    for r in range(1, 5):
        for combo in combinations(candidates, r):
            total_cr = round(sum(m["challenge_rating"] for m in combo), 2)
            if min_cr <= total_cr <= max_cr:
                best_combo = list(combo)
                break
        if best_combo:
            break
    return best_combo

# -----------------------------------------------
# MEMORY & INTERACTIONS (short-term, long-term)
# -----------------------------------------------

def parse_iso(ts):
    """
    Helper to parse ISO timestamp, handling trailing Z if present.
    """
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(ts)
    except Exception:
        return None

def store_interaction(npc_id, character_id, interaction_text, tags=None):
    """
    Stores an interaction in short-term memory (Chroma).
    """
    memory_id = str(uuid.uuid4())
    metadata = {
        "npc_id": npc_id,
        "character_id": character_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if tags:
        metadata.update(tags)

    short_term_collection.add(
        documents=[interaction_text],
        metadatas=[metadata],
        ids=[memory_id]
    )
    return memory_id

def get_recent_interactions(npc_id, character_id=None, limit=5):
    """
    Fetch short-term memory entries for the NPC, optionally filtered by character_id.
    Queries the collection but uses a minimal 'query_texts' trick for recency.
    """
    filters = {"npc_id": npc_id}
    if player_id:
        filters["character_id"] = character_id

    results = short_term_collection.query(
        query_texts=["recent conversation"],
        n_results=limit,
        where=filters
    )
    return results["documents"][0] if results.get("documents") else []

def summarize_and_clean_memory(npc_id, character_id=None, days_old=3):
    """
    Summarizes expired short-term memory entries for an NPC (optionally per player),
    stores the summary in Firebase, and deletes the old entries.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=days_old)

    filters = {"npc_id": npc_id}
    if character_id:
        filters["character_id"] = player_id

    results = short_term_collection.get(where=filters)
    if not results or not results.get("metadatas"):
        return {"message": "No memory to clean."}

    expired_docs = []
    for doc_id, meta, text in zip(results["ids"], results["metadatas"], results["documents"]):
        ts = parse_iso(meta.get("timestamp", ""))
        if ts and ts < cutoff:
            expired_docs.append((doc_id, text))

    if not expired_docs:
        return {"message": "No expired memory entries."}

    combined_text = "\n".join(text for _, text in expired_docs)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are summarizing old NPC dialogue. Recap emotions and key facts."},
                {"role": "user", "content": combined_text}
            ],
            temperature=0.5,
            max_tokens=250
        )
        summary = response.choices[0].message.content.strip()
        usage = response.get("usage", {})
        log_gpt_usage("gpt-4o-mini", usage)
    except Exception as e:
        return {"error": f"GPT summarization failed: {str(e)}"}

    mem_ref = db.reference(f"/npc_memory/{npc_id.lower()}")
    existing = mem_ref.get() or {}
    combined = (existing.get("summary", "") + "\n" + summary).strip()
    mem_ref.update({"summary": combined})

    ids_to_delete = [doc_id for doc_id, _ in expired_docs]
    short_term_collection.delete(ids=ids_to_delete)

    return {
        "message": f"Summarized and cleaned {len(ids_to_delete)} expired memory entries.",
        "summary": summary
    }

# === LONG-TERM MEMORY (Chroma-based) ===

def store_log(entry: dict):
    """
    Stores a log entry in the long-term memory (Chroma).
    """
    if "text" not in entry:
        return {"error": "Missing log text"}

    uid = f"{entry.get('speaker', 'unknown')}_{datetime.utcnow().isoformat()}"
    long_term_collection.add(
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
    Query the long-term memory for recent logs from a speaker, optionally filtered by region.
    Only returns logs from the past 3 hours as 'recent'.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=3)

    filters = {
        "$and": []
    }
    # Construct filter conditions
    if speaker_id:
        filters["$and"].append({"speaker": speaker_id})
    if region:
        filters["$and"].append({"region": region})
    # Timestamp-based filter
    filters["$and"].append({"timestamp": {"$gt": cutoff.isoformat()}})

    results = long_term_collection.get(where=filters)
    if not results or not results.get("documents"):
        return []

    # Sort by timestamp descending
    meta_docs = list(zip(results["metadatas"], results["documents"]))
    # Extract timestamp and sort
    def parse_ts(m): 
        return parse_iso(m[0].get("timestamp", "")) or datetime.min

    meta_docs.sort(key=parse_ts, reverse=True)
    # Grab the top N
    top = meta_docs[:n]
    # Return structured logs
    out = []
    for meta, doc in top:
        out.append({"text": doc, "meta": meta})
    return out

def summarize_memory(npc_id, player_id, logs):
    """
    Summarize a list of log entries to see what the NPC remembers about the player.
    """
    if not logs:
        return None

    lines = [f"- {log['text']}" for log in logs]
    prompt = (
        "You are an NPC in a fantasy world. Summarize your recent interactions with the player.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph.\n\n"
        f"Recent Logs:\n{chr(10).join(lines)}\n\n"
        "In 1–2 sentences, what stood out and what do you remember?"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a reflective NPC summarizing memory of the player.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150
        )
        usage = response.get("usage", {})
        log_gpt_usage("gpt-4o", usage)

        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def update_long_term_memory(npc_id, character_id, region=None):
    """
    High-level helper to gather recent logs about a player in a region
    and generate a short summary to store in Firebase under NPC data.
    """
    recent_logs = query_recent(speaker_id=character_id, region=region, n=10)
    summary = summarize_memory(npc_id, character_id, recent_logs)

    if summary:
        ref = db.reference(f"/npcs/{npc_id}/long_term_memory/{player_id}")
        ref.set({
            "last_summary": summary,
            "summary_date": datetime.utcnow().isoformat()
        })
        return {
            "npc_id": npc_id,
            "character_id": character_id,
            "summary": summary
        }

    return {"error": "No recent memory to summarize"}

# -----------------------------------------------
# NPC/POI/Relationship/Combat Blueprints, etc.
# (Place your existing route definitions here)
# ...
# For brevity, not re-pasting the entire code from prior consolidated examples
# -----------------------------------------------


# === NPC GENERATION AND REGION SETUP ===
def generate_starting_city_and_region():
    """
    Creates a default city at 0_0 if it doesn't exist, 
    then populates it with NPCs.
    """
    key = "0_0"
    poi_ref = db.reference(f"/locations/{key}")
    if not poi_ref.get():
        try:
            response = ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Generate a fantasy capital city in JSON format with fields: "
                            "name, description, danger_level, buildings (list), tags (tone, focus)."
                        )
                    },
                    {
                        "role": "user",
                        "content": "Create a sprawling capital city for the region 'Sunveil Dominion'."
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
            generate_npcs_for_poi(0, 0)
        except Exception as e:
            poi_ref.set({"error": str(e)})

def create_player(character_id, name, race, class_type):
    """
    Creates a new player entry in the database, ensuring 
    the starting region (0_0) is initialized.
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
    finished = complete_character(core)
    db.reference(f"/players/{character_id}").set(finished)
    return finished

# === STATUS EFFECTS AND COOLDOWNS ===

def handle_cooldowns(npc_id):
    """
    Decrements cooldown counters for an NPC. 
    If a cooldown reaches 0, it is removed from that NPC's record.
    """
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
    """
    Rolls a d20 + stat_mod vs a difficulty class (dc).
    Returns success/fail boolean and details.
    """
    roll_total = random.randint(1, 20) + stat_mod
    success = roll_total >= dc
    return {"roll": roll_total, "modifier": stat_mod, "dc": dc, "success": success}

def get_total_party_level(party_id, mode="sum"):
    """
    Returns the sum (or average) of levels for all members 
    in a specified party.
    """
    party = db.reference(f"/parties/{party_id}").get()
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
    """
    Awards a given amount of XP to each member of a party.
    Returns a dictionary of updated XP values.
    """
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

# === ARC & QUEST MANAGEMENT (FROM EARLIER MERGED CODE) ===

# Updated import references for your new architecture:

from rules_endpoints import lookup_rule, resolve_skill_check
from quest_engine import append_to_existing_log, extract_quest_from_reply

 # (We already included a local version above, but here for reference.)

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
    player_ref = db.reference(f"/players/{character_id}")
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

def update_player_arc(character_id, arc_name, arc_choices, arc_progress, npc_reactions):
    """
    Update a player's current arc details.
    """
    player_ref = db.reference(f"/players/{character_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })
    return {"status": "Player arc updated", "character_id": character_id}

def generate_quests_for_active_arc(character_id, arc_name, arc_progress):
    """
    Generate quests based on a player's active arc and its progress.
    """
    player_ref = db.reference(f"/players/{character_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    if arc_name == player_data.get("current_arc") and arc_progress < 100:
        quests = []
        if arc_name == "The Fallen Noble":
            if arc_progress < 50:
                quests = ["recover_lost_legacy", "find_allies_in_exile"]
            else:
                quests = ["seek_revenge", "infiltrate_the_royal_palace"]
        for quest in quests:
            append_to_existing_log(character_id, npc_name="NPC", summary=f"Quest generated: {quest}")
        return {"status": "New quests generated", "quests": quests}
    return {"status": "Arc not active or complete."}

def handle_event_and_progress_arc(entity_type, entity_id, event_name):
    """
    Update arc progress based on a game event.
    """
    if event_name == "kingdom_falls":
        update_arc_progress(entity_type, entity_id, "The Kingdom's Fall", 100, "completed")
        if entity_type == "player":
            update_arc_progress(entity_type, entity_id, "Rebuild the Kingdom", 0, "active")
    elif event_name == "rebellion_succeeds":
        update_arc_progress(entity_type, entity_id, "Revolutionary Victory", 100, "completed")
        if entity_type == "player":
            update_arc_progress(entity_type, entity_id, "The Rise of a New Order", 0, "active")
    return {"status": f"Event '{event_name}' processed."}

def trigger_arc_branch(character_id, arc_name, new_branch):
    """
    Trigger a new branch for an active arc.
    """
    ref = db.reference(f"/players/{character_id}")
    player = ref.get() or {}
    current_arcs = player.get("current_arcs", [])
    for arc in current_arcs:
        if arc.get("arc_name") == arc_name and arc.get("status") == "active":
            arc["branch"] = new_branch
            arc["npc_reaction"] = "shifted"
            ref.update({"current_arcs": current_arcs})
            return {"status": "branch triggered", "arc": arc_name, "branch": new_branch}
    return {"error": "Arc not found or inactive"}

def generate_npc_response_with_arc_context(npc_id, character_id, prompt):
    """
    Generate an NPC response using arc context from both NPC and player.
    """
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()
    player_ref = db.reference(f"/players/{character_id}")
    player_data = player_ref.get()
    npc_arc = npc_data.get("current_arcs", [])
    player_arc = player_data.get("current_arc", "")
    if npc_arc:
        arc_context = f"NPC Arc: {npc_arc[-1]['arc_name']} ({npc_arc[-1]['status']})"
    else:
        arc_context = "NPC Arc: None"

    player_context = f"Player Arc: {player_arc}"
    full_prompt = f"{arc_context} {player_context}\n{prompt}"
    return get_dm_response("Arc Context", full_prompt, importance_score=7)

# === BLUEPRINTS ===

auth_bp = Blueprint('auth', __name__)
basic_bp = Blueprint('basic', __name__)
relationship_bp = Blueprint('relationship', __name__)

# === AUTH ROUTES ===

@basic_bp.route('/chat')
def chat():
    return render_template("chat.html")

@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Email, password, and username are required"}), 400

    try:
        # Just store the user in Firebase /users/<uid>
        uid = str(uuid.uuid4())
        user_ref = db.reference(f"/users/{uid}")
        user_ref.set({
            "username": username,
            "email": email,
            "password": password,  # plain text for demonstration
            "character_data": {},
            "narrator_style": "A mix between Cormac McCarthy, Lovecraft, and Herman Melville"
        })
        return jsonify({"message": "User created successfully", "user_id": uid}), 201
    except Exception as e:
        current_app.logger.error(f"Error during sign up: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Retrieve all users from /users
    users_ref = db.reference("/users")
    all_users = users_ref.get() or {}

    found_user = None
    found_uid = None

    for uid, user_data in all_users.items():
        if user_data.get("username") == username:
            found_user = user_data
            found_uid = uid
            break

    if not found_user:
        return jsonify({"error": "User not found"}), 404

    if found_user.get("password") != password:
        return jsonify({"error": "Invalid password"}), 401

    return jsonify({
        "message": "Login successful",
        "user_id": found_uid,
        "username": found_user["username"]
    })

@basic_bp.route('/players', methods=['GET'])
def list_players():
    ref = db.reference("/players")
    raw = ref.get() or {}

    # Just return 'raw' directly
    return jsonify(raw)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "User logged out (handled client-side)."})

# === BASIC ROUTES ===

@basic_bp.route('/')
def index():
    """
    Basic index route that renders a template (e.g., homepage).
    """
    return render_template("index.html")

@basic_bp.route('/generate_location_gpt', methods=['POST'])
def generate_location_gpt():
    """
    Usesgpt-4o to generate a new location at coordinates x,y in strict JSON format
    and saves it to Firebase.
    """
    data = request.get_json(force=True)
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
        response = ChatCompletion.create(
            model="gpt-4o",
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

        usage = response.get("usage", {})
        log_gpt_usage("gpt-4o", usage)

        return jsonify({"message": "Location generated and saved.", "location": location_data})
    except Exception as e:
        return jsonify({"error": f"GPT or Firebase error: {str(e)}"}), 500

@basic_bp.route('/move_player', methods=['POST'])
def move_player():
    """
    Moves a character from their current location to a new_location (x_y format),
    generating POIs and terrain data along the path. Rolls for random combat encounters.
    """
    data = request.get_json(force=True)
    character_id = data.get("character_id")
    new_location = data.get("new_location")
    if not character_id or not new_location:
        return jsonify({"error": "character_id and new_location are required"}), 400

    character_ref = db.reference(f'/players/{character_id}')
    character_state = character_ref.get() or {}
    prev_location = character_state.get("location")

    def parse_coords(loc):
        try:
            x_coord, y_coord = map(int, loc.split("_"))
            return x_coord, y_coord
        except:
            return None, None

    x1, y1 = parse_coords(prev_location)
    x2, y2 = parse_coords(new_location)
    if None in [x1, y1, x2, y2]:
        return jsonify({"error": "Invalid coordinate format. Expected 'x_y'."}), 400

    path = []
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    for i in range(1, steps + 1):
        x_coord = x1 + round(i * dx / steps)
        y_coord = y1 + round(i * dy / steps)
        path.append((x_coord, y_coord))

    combat_info = None
    from worldgen import choose_land_type, roll_danger_for_tile, should_generate_poi

    for x_coord, y_coord in path:
        key = f"{x_coord}_{y_coord}"
        # Terrain check / generation
        terrain = db.reference(f"/terrain_map/{key}").get()
        if not terrain:
            region_id = character_state.get("region_id", "default")
            terrain = choose_land_type(x_coord, y_coord, region_id)

        tile_ref = db.reference(f"/locations/{key}")
        tile_data = tile_ref.get() or {}
        if "danger_level" not in tile_data:
            tile_data["danger_level"] = roll_danger_for_tile(x_coord, y_coord)

        # Possibly generate new POI
        if "POI" not in tile_data:
            if should_generate_poi(x_coord, y_coord):
                try:
                    lore_response = ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Generate a brief name and description for a fantasy Point of Interest."},
                            {"role": "user", "content": f"Create a location in a {terrain} biome."}
                        ],
                        temperature=0.8,
                        max_tokens=150
                    )
                    lore = lore_response.choices[0].message.content.strip()
                    tile_data.update({
                        "POI": True,
                        "terrain": terrain,
                        "region_id": character_state.get("region_id", "default"),
                        "description": lore
                    })

                    usage = lore_response.get("usage", {})
                    log_gpt_usage("gpt-4o-mini", usage)

                    tag_response = ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Classify the tone (friendly, neutral, hostile) and focus "
                                    "(combat, roleplay, exploration) of a POI based on its description."
                                )
                            },
                            {"role": "user", "content": lore}
                        ],
                        temperature=0.7,
                        max_tokens=100
                    )
                    tag_text = tag_response.choices[0].message.content.strip()
                    tile_data["tags"] = {"tone": "neutral", "focus": "exploration"}
                    if ":" in tag_text:
                        for line in tag_text.split("\n"):
                            if ":" in line:
                                k, v = line.split(":", 1)
                                tile_data["tags"][k.strip().lower()] = v.strip().lower()
                    log_gpt_usage("gpt-4o-mini", tag_response.get("usage", {}))

                    building_response = ChatCompletion.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Generate a list of buildings for a fantasy Point of Interest."},
                            {
                                "role": "user",
                                "content": (
                                    f"List the buildings that might be found at a new POI in a {terrain} biome. "
                                    f"The region encourages {tile_data.get('region_id', 'unknown')} themes."
                                )
                            }
                        ],
                        temperature=0.8,
                        max_tokens=250
                    )
                    building_text = building_response.choices[0].message.content.strip()
                    tile_data["buildings"] = building_text
                    log_gpt_usage("gpt-4o-mini", building_response.get("usage", {}))

                    tile_ref.set(tile_data)
                    generate_npcs_for_poi(x_coord, y_coord)
                    tile_data = tile_ref.get()
                except Exception as e:
                    tile_data["POI_error"] = str(e)

        tile_ref.set(tile_data)

        dl = tile_data["danger_level"]
        combat_chance = dl * 7.5
        combat_roll = randint(0, 99)
        if combat_roll < combat_chance:
            character_state["location"] = key
            updated_character = complete_character(character_state)
            character_ref.set(updated_character)
            combat_info = {
                "combat_triggered": True,
                "combat_tile": key,
                "combat_chance_percent": combat_chance,
                "combat_roll": combat_roll,
                "character_state": updated_character
            }
            break

    if not combat_info:
        character_state["location"] = new_location
        updated_character = complete_character(character_state)
        character_ref.set(updated_character)
        combat_info = {
            "combat_triggered": False,
            "character_state": updated_character
        }

    return jsonify({
        "message": f"Character {character_id} moved to {combat_info['character_state']['location']}",
        **combat_info
    })


@basic_bp.route('/debug_state', methods=['GET'])
def debug_state():
    """
    Returns the global state from Firebase for debugging.
    """
    try:
        state = db.reference('/global_state').get() or {}
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@basic_bp.route('/update_npc_memory', methods=['POST'])
def update_npc_memory():
    """
    Records an interaction in the named NPC's 'rag_log', and 
    summarizes older interactions after 3 days.
    """
    data = request.get_json(force=True)
    npc_name = data.get("npc_name", "").lower()
    interaction = data.get("interaction", "")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())
    if not npc_name or not interaction:
        return jsonify({"error": "npc_name and interaction are required"}), 400

    ref = db.reference(f'/npc_memory/{npc_name}')
    memory = ref.get() or {"rag_log": [], "summary": ""}
    memory["rag_log"].append({
        "interaction": interaction,
        "timestamp": timestamp
    })

    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    new_rag = []
    expired_interactions = []
    for entry in memory["rag_log"]:
        try:
            timestamp_str = entry.get("timestamp")
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str.replace("Z", "+00:00")
            entry_ts = datetime.fromisoformat(timestamp_str)
            if entry_ts.tzinfo is None:
                entry_ts = entry_ts.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if entry_ts < cutoff:
            expired_interactions.append(entry["interaction"])
        else:
            new_rag.append(entry)

    memory["rag_log"] = new_rag
    if expired_interactions:
        current_summary = memory.get("summary", "")
        new_summary = current_summary + " " + " ".join(expired_interactions)
        memory["summary"] = new_summary.strip()

    ref.set(memory)
    return jsonify({
        "message": f"Memory updated for {npc_name}",
        "memory": memory
    })

@basic_bp.route('/simulate_npc_interactions', methods=['POST'])
def simulate_npc_interactions():
    """
    Simulates interactions between NPCs present in a specified POI.
    Uses GPT to generate a short summary, updates NPC memory and relationship scores.
    """
    data = request.get_json(force=True)
    region_name = data.get("region_name", "")
    poi_id = data.get("poi_id", "")
    if not region_name or not poi_id:
        return jsonify({"error": "Both region_name and poi_id are required."}), 400

    poi_ref = db.reference(f'/poi_state/{region_name}/{poi_id}')
    poi_state = poi_ref.get()
    if not poi_state:
        return jsonify({"error": f"POI '{poi_id}' in region '{region_name}' not found."}), 404

    npcs = poi_state.get("npcs_present", [])
    if len(npcs) < 2:
        return jsonify({"message": "Not enough NPCs present to simulate interactions."}), 200

    from rumor_engine import share_rumors_between_npcs
    interaction_log = []
    for npc in npcs:
        others = [o for o in npcs if o != npc]
        if not others or random.random() > 0.6:
            continue
        partner = random.choice(others)
        matrix_ref = db.reference(f'/npc_opinion_matrix/{npc}/{partner}')
        score = matrix_ref.get() or 0

        if score >= 5:
            tone = "friendly"
        elif score <= -5:
            tone = "hostile"
        else:
            tone = "neutral"

        system_prompt = "You are narrating social encounters between NPCs in a persistent fantasy world.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph."
        user_prompt = (
            f"NPC A ({npc}) and NPC B ({partner}) are having a {tone} interaction at a POI called '{poi_id}'. "
            f"You are the Dungeon Master in a fantasy RPG setting. Narrate with an epic, immersive tone inspired by A mix between Cormac McCarthy, Lovecraft, and Herman Melville. Balance these elements fluidly to enhance immersion, intrigue, and emotional engagement for the players."
        )
        try:
            response = ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=60
            )
            summary = response.choices[0].message.content.strip()
            usage = response.get("usage", {})
            log_gpt_usage("gpt-4o-mini", usage)
        except Exception as e:
            summary = f"{npc} and {partner} interact (GPT failed)."

        for id_ in [npc, partner]:
            mem_ref = db.reference(f"/npc_memory/{id_.lower()}")
            memory = mem_ref.get() or {"rag_log": [], "summary": ""}
            memory["rag_log"].append({
                "interaction": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
            mem_ref.set(memory)

        rumor_result = share_rumors_between_npcs(npc, partner)
        score_delta = {"friendly": +2, "neutral": 0, "hostile": -2}[tone]
        new_score = score + score_delta
        matrix_ref.set(new_score)
        interaction_log.append({
            "npc": npc,
            "partner": partner,
            "tone": tone,
            "summary": summary,
            "shared_rumors": rumor_result.get("shared", []),
            "new_score": new_score
        })

    return jsonify({
        "message": f"Simulated interactions at POI '{poi_id}' in region '{region_name}'.",
        "interactions": interaction_log
    })

@basic_bp.route("/players/<character_id>", methods=["PATCH"])
def patch_character(character_id):
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    ref = db.reference(f"/players/{character_id}")
    existing = ref.get()

    if not existing:
        return jsonify({"error": f"No character found with ID {character_id}"}), 404

    for k, v in data.items():
        existing[k] = v

    ref.set(existing)

    return jsonify(existing), 200

@basic_bp.route('/ascii_map', methods=['GET'])
def ascii_map():
    """
    Creates a simple ASCII map explicitly centered on (0,0), showing known locations (L) vs unknown (.).
    """
    all_locations = db.reference('/locations').get() or {}

    GRID_SIZE = 21  # Explicitly sets a fixed size (21x21), adjustable as needed
    HALF_GRID = GRID_SIZE // 2

    grid = []
    # Y goes from positive (top) to negative (bottom)
    for y in range(HALF_GRID, -HALF_GRID - 1, -1):
        row = ""
        # X goes from negative (left) to positive (right)
        for x in range(-HALF_GRID, HALF_GRID + 1):
            key = f"{x}_{y}"
            if x == 0 and y == 0:
                row += "@"  # Explicitly mark the starting position (0,0)
            else:
                row += "L" if key in all_locations else "."
        grid.append(row)

    ascii_map_text = "\n".join(grid)
    return ascii_map_text, 200, {'Content-Type': 'text/plain'}


@basic_bp.route('/combat_round', methods=['POST'])
def combat_round():
    """
    Endpoint to simulate an entire tactical combat round among provided combatants.
    """
    data = request.get_json(force=True)
    combatants = data.get("combatants", [])
    if not combatants or not isinstance(combatants, list):
        return jsonify({"error": "A combatants list is required."}), 400
    result = simulate_tactical_combat_round(combatants)
    return jsonify(result)

@basic_bp.route('/questlog/<character_id>', methods=['GET'])
def get_questlog(player_id):
    """
    Retrieves a player's questlog.
    """
    questlog = db.reference(f'/questlogs/{character_id}').get() or []
    return jsonify(questlog)

@basic_bp.route('/questlog/<character_id>', methods=['POST'])
def add_quest(character_id):
    """
    Adds a new quest to a player's questlog.
    """
    data = request.get_json(force=True)
    quest = data.get("quest")
    if not quest:
        return jsonify({"error": "quest is required"}), 400
    questlog_ref = db.reference(f'/questlogs/{character_id}')
    questlog = questlog_ref.get() or []
    new_entry = {"quest": quest, "timestamp": datetime.utcnow().isoformat()}
    questlog.append(new_entry)
    questlog_ref.set(questlog)
    return jsonify({"message": "Quest added", "questlog": questlog})

@basic_bp.route('/region/<region_id>', methods=['GET'])
def get_region(region_id):
    """
    Retrieves region data from Firebase by region_id.
    """
    region = db.reference(f'/regions/{region_id}').get() or {}
    return jsonify(region)

@basic_bp.route('/region/<region_id>', methods=['POST'])
def update_region(region_id):
    """
    Updates or creates region data in Firebase.
    """
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "No data provided"}), 400
    region_ref = db.reference(f'/regions/{region_id}')
    region_ref.set(data)
    return jsonify({"message": f"Region {region_id} updated.", "region": data})

@basic_bp.route('/region/<region_id>', methods=['DELETE'])
def delete_region(region_id):
    """
    Deletes a region entirely from Firebase.
    """
    region_ref = db.reference(f'/regions/{region_id}')
    region_ref.delete()
    return jsonify({"message": f"Region {region_id} deleted."})

@basic_bp.route('/rotate_motifs/<character_id>', methods=['POST'])
def rotate_motifs_route(character_id):
    """
    Rotates narrative motifs for a single character by re-running complete_character().
    """
    ref = db.reference(f'/characters/{character_id}')
    character = ref.get()
    if not character:
         return jsonify({"error": "Character not found."}), 404
    updated_character = complete_character(character)
    ref.set(updated_character)
    return jsonify({"message": "Character motifs rotated", "character": updated_character})

@basic_bp.route('/npc_motif_tick', methods=['POST'])
def npc_motif_tick():
    """
    Rotates motifs for all NPCs by re-running complete_character() on each NPC in /npcs.
    """
    all_npcs = db.reference('/npcs').get() or {}
    updated = {}
    for npc_id in all_npcs.keys():
        ref = db.reference(f'/npcs/{npc_id}')
        npc = ref.get()
        if not npc:
            continue
        updated_npc = complete_character(npc)
        ref.set(updated_npc)
        updated[npc_id] = updated_npc.get("narrative_motif_pool", {}).get("active_motifs", [])
    return jsonify({"message": "NPC motifs rotated", "updated": updated})

@basic_bp.route('/generate_encounter_v2', methods=['POST'])
def generate_encounter_v2():
    """
    POST /generate_encounter_v2
    {
      "party_id": "...",
      "location": "x_y"
    }

    Similar to generate_encounter, but includes distance-based logic
    to potentially spawn higher-CR monsters the farther you are from (0,0).
    """
    import math
    import random

    data = request.get_json(force=True)
    party_id = data.get("party_id")
    location = data.get("location", "0_0")
    if not party_id:
        return jsonify({"error": "party_id is required"}), 400

    # 1) Parse the player's location => (px, py)
    try:
        x_str, y_str = location.split("_")
        px, py = int(x_str), int(y_str)
    except:
        px, py = 0, 0  # fallback if parsing fails

    # 2) Compute distance from (0,0)
    dist = math.sqrt(px**2 + py**2)

    # 3) Figure out the farthest discovered tile in the same quadrant
    #    (so if player is in NE quadrant, only compare NE-located tiles).
    all_locations = db.reference("/locations").get() or {}
    farthest_distance = 50.0  # at least 50
    for loc_key in all_locations:
        try:
            lx_str, ly_str = loc_key.split("_")
            lx, ly = int(lx_str), int(ly_str)
        except:
            continue
        # skip if not in same quadrant as the player
        if (lx >= 0) != (px >= 0):  # x sign doesn't match
            continue
        if (ly >= 0) != (py >= 0):  # y sign doesn't match
            continue

        d = math.sqrt(lx**2 + ly**2)
        if d > farthest_distance:
            farthest_distance = d

    # 4) Compute distance_fraction. No effect if dist < 50.
    if dist <= 50:
        distance_fraction = 0.0
    else:
        # if farthest_distance == 50, we'd get a div-by-zero, so clamp
        max_span = max(1.0, (farthest_distance - 50))
        distance_fraction = (dist - 50) / max_span
        distance_fraction = max(0.0, min(distance_fraction, 1.0))

    # 5) Convert that fraction into a random CR increment up to +1.0
    #    Probability table at fraction=1.0: 
    #       +0.25 => 5%, +0.50 => 15%, +0.75 => 30%, +1.00 => 50%.
    #    Scale each by distance_fraction and do a single pass.
    tiers = [
        (0.25, 0.05),
        (0.50, 0.15),
        (0.75, 0.30),
        (1.00, 0.50),
    ]
    roll_val = random.random()
    cr_increment = 0.0
    for (step, base_chance) in tiers:
        chance_now = base_chance * distance_fraction
        if roll_val < chance_now:
            cr_increment = step
            break
        roll_val -= chance_now

    # 6) Gather the party and choose monsters based on the new CR
    #    i.e. "party_party" from your existing code
    party_ref = db.reference(f"/parties/{party_id}")
    party_data = party_ref.get()
    if not party_data:
        return jsonify({"error": f"Party {party_id} not found"}), 404

    player_party = []
    for member_id in party_data.get("members", []):
        if member_id.startswith("player"):
            char = db.reference(f"/players/{member_id}").get() or {}
        else:
            char = db.reference(f"/npcs/{member_id}").get() or {}
        if char:
            player_party.append({**char, "id": member_id})

    if not player_party:
        return jsonify({"error": "Party has no valid members"}), 400

    from rules_endpoints import award_xp_to_party
    from combat_engine import start_combat

    # 7) Calculate the final CR range using total party level + cr_increment
    total_level = 0
    for member in player_party:
        total_level += member.get("level", 1)
    # Or if you prefer average:
    # total_level = get_total_party_level(party_id, mode="average")

    effective_level = total_level + cr_increment
    min_cr = round(effective_level * 0.25 - 0.25, 2)
    max_cr = round(effective_level * 0.25 + 0.25, 2)
    if min_cr < 0:
        min_cr = 0.0

    # 8) Filter monsters from /rules/monsters
    all_monsters_data = db.reference("/rules/monsters").get() or {}
    valid_monsters = [
        m for m in all_monsters_data.values() 
        if min_cr <= m.get("challenge_rating", 0) <= max_cr
    ]
    if not valid_monsters:
        return jsonify({
            "error": "No suitable monsters found for this distance-based CR range.",
            "distance_fraction": distance_fraction,
            "cr_increment": cr_increment,
            "effective_level": effective_level,
            "min_cr": min_cr,
            "max_cr": max_cr
        }), 500

    # 9) Randomly pick up to 3 monsters to spawn
    import random
    enemy_group = random.sample(valid_monsters, min(3, len(valid_monsters)))
    enemy_party = []
    for m in enemy_group:
        m_id = "enemy_" + str(random.randint(1000, 9999))
        enemy_party.append({
            "id": m_id,
            "name": m.get("name", "Unknown"),
            "HP": m.get("hp", 20),
            "AC": m.get("ac", 12),
            "DEX": m.get("dex", 10),
            "team": "hostile"
        })

    # 10) Start combat with your existing logic
    encounter_name = f"Encounter at {location}"
    battle_id, combat_data = start_combat(encounter_name, player_party, enemy_party)

    # 11) XP awarding
    xp_reward = sum(m.get("xp", 50) for m in enemy_group)
    xp_result = award_xp_to_party(party_id, xp_reward)

    return jsonify({
        "message": "Combat started with distance-based CR scaling",
        "battle_id": battle_id,
        "encounter_name": encounter_name,
        "player_party": player_party,
        "enemy_party": enemy_party,
        "xp_awarded": xp_result,
        "location": location,
        "distance_fraction": distance_fraction,
        "cr_increment": cr_increment,
        "effective_level": effective_level,
        "min_cr": min_cr,
        "max_cr": max_cr
    })

from relationship_engine import update_relationships, daily_relationship_tick

# === RELATIONSHIP ENGINE HOOKS ===

@relationship_bp.route('/relationships/update', methods=['POST'])
def api_update_relationship():
    """
    Updates relationships between two NPCs by calling a function in relationship_engine.py.
    """
    data = request.get_json(force=True)
    npc_id = data.get("npc_id")
    target_id = data.get("target_id")
    if not npc_id or not target_id:
        return jsonify({"error": "Both npc_id and target_id are required"}), 400
    result = update_relationships(npc_id, target_id)
    return jsonify(result)

@relationship_bp.route('/relationships/daily_tick', methods=['POST'])
def api_relationship_tick():
    """
    Triggers a daily relationship tick for all NPCs, gradually shifting relationships.
    """
    result = daily_relationship_tick()
    return jsonify({"message": "Daily relationship tick completed.", "result": result})

# === COMBAT ENGINE ===

from rules_endpoints import apply_status_effect, resolve_status_effects

def roll_initiative(DEX):
    """
    Roll d20 + (DEX-10)//2 for initiative ordering.
    """
    return random.randint(1, 20) + ((DEX - 10) // 2)

def choose_action(attacker, targets):
    """
    Simple AI to choose an action for an NPC. 
    Behavior is role-based or random for variety.
    """
    role = attacker.get("role", "fighter")
    hp = attacker.get("HP", 10)
    if hp < 5 and role != "tank":
        return "flee"
    if role == "healer":
        low_hp_allies = [t for t in targets if t["team"] == attacker["team"] and t["HP"] < 6]
        if low_hp_allies:
            return "heal"
        return "support"
    if role == "caster":
        return random.choice(["cast", "blast", "defend"])
    if role == "rogue":
        return random.choice(["stab", "hide", "backstab"])
    return random.choice(["strike", "defend", "cleave"])

def apply_action(attacker, target, action):
    """
    Applies a chosen action from an attacker onto a target,
    returning a short string log of what happened.
    """
    log = ""
    if action in ["strike", "cleave", "stab", "blast", "backstab"]:
        attack_roll = random.randint(1, 20) + attacker.get("ATK", 3)
        defense = target.get("AC", 10)
        if attack_roll >= defense:
            damage = random.randint(4, 12)
            target["HP"] = max(target["HP"] - damage, 0)
            log = f"{attacker['id']} used {action} on {target['id']} for {damage} dmg. [{target['HP']} HP left]"
        else:
            log = f"{attacker['id']} missed {target['id']} with {action}."
    elif action == "heal":
        heal_amount = random.randint(5, 10)
        target["HP"] += heal_amount
        log = f"{attacker['id']} healed {target['id']} for {heal_amount}. [{target['HP']} HP]"
    elif action == "flee":
        log = f"{attacker['id']} attempts to flee the fight!"
    else:
        log = f"{attacker['id']} holds position with {action}."
    return log

def simulate_tactical_combat_round(combatants):
    """
    Sorts combatants by initiative, then each performs an action once. 
    Returns final state and a log of actions.
    """
    combat_log = []
    sorted_combatants = sorted(combatants, key=lambda c: roll_initiative(c.get("DEX", 0)), reverse=True)

    for attacker in sorted_combatants:
        if attacker.get("HP", 0) <= 0:
            continue
        targets = [c for c in sorted_combatants if c["id"] != attacker["id"] and c.get("HP", 0) > 0]
        if not targets:
            combat_log.append(f"{attacker['id']} has no targets.")
            continue

        enemies = [t for t in targets if t["team"] != attacker["team"]]
        target = random.choice(enemies if enemies else targets)
        action = choose_action(attacker, targets)
        log = apply_action(attacker, target, action)
        combat_log.append(log)

    return {
        "combatants": sorted_combatants,
        "combat_log": combat_log
    }

def start_combat(encounter_name, player_party, enemy_party, battle_map=None):
    """
    Initializes a new combat state with participants from both sides 
    and saves it under /combat_state/{battle_id} in Firebase.
    """
    battle_id = str(uuid.uuid4())
    all_participants = {}

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
    """
    Progresses the combat by one turn in an ongoing battle. 
    If the acting participant is an NPC, attempts to have GPT pick an action.
    """
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

    if actor["team"] == "party":
        combat_data["log"].append(f"It is now {actor['name']}'s turn.")
        combat_data["current_turn"] = (current_index + 1) % len(turn_order)
        ref.set(combat_data)
        return {
            "acting_id": acting_id,
            "action": f"Waiting for player action ({actor['name']})",
            "log": combat_data["log"][-5:]
        }, 200

    # For NPC actors, attempt GPT-based decision
    context_lines = [
        f"{p['name']} (HP: {p['HP']}, Team: {p['team']})"
        for p in combat_data["participants"].values()
    ]
    context = "\n".join(context_lines)
    prompt = (
        f"You are controlling the NPC named {actor['name']} in a turn-based fantasy RPG battle.\n"
        f"Here are the combatants:\n{context}\n\n"
        f"Choose a reasonable action as JSON like:\n"
        f'{{"action": "attack", "target": "player_1", "roll": 17, "value": 9, "notes": "slashes with scimitar"}}\n\n'
        f"ONLY return the JSON."
    )

    try:
        # We can override or set a high importance to force 'gpt-4', or use the router
        model = gpt_router(score=8, flags={"force_gpt4": True}) 
        gpt_response = ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an NPC tactician in a fantasy battle."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        content = gpt_response.choices[0].message.content.strip()
        usage = gpt_response.get("usage", {})
        log_gpt_usage(model, usage)

        parsed = json.loads(content)
        action_type = parsed.get("action", "attack")
        target_id = parsed.get("target")
        roll = parsed.get("roll", 10)
        value = parsed.get("value", 0)
        notes = parsed.get("notes", "")
        status_effect = parsed.get("status_effect")
        spell_name = parsed.get("spell_name")
        spell_level = parsed.get("spell_level")

        result, status = apply_combat_action(
            battle_id, acting_id, target_id, action_type, roll, value,
            notes, status_effect, spell_name, spell_level
        )
        return result, status

    except Exception as e:
        fallback_log = f"{actor['name']} hesitates. ({str(e)})"
        combat_data["log"].append(fallback_log)
        combat_data["current_turn"] = (current_index + 1) % len(turn_order)
        ref.set(combat_data)
        return {
            "acting_id": acting_id,
            "action": fallback_log,
            "log": combat_data["log"][-5:]
        }, 200

def apply_combat_action(
    battle_id, actor_id, target_id, action_type, roll, value, notes="",
    status_effect=None, spell_name=None, spell_level=None
):
    """
    Applies a combat action (attack, heal, spell, etc.) within 
    an ongoing battle state. Updates HP, logs, increments turn.
    """
    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()
    if not combat_data:
        return {"error": "Battle not found."}, 404

    current_index = combat_data.get("current_turn", 0)
    turn_order = combat_data.get("turn_order", [])
    if turn_order[current_index] != actor_id:
        return {"error": "It's not this character's turn."}, 400

    participants = combat_data["participants"]
    actor = participants.get(actor_id)
    target = participants.get(target_id)

    if not actor or not target:
        return {"error": "Invalid actor or target ID."}, 400

    narration = f"{actor['name']} uses {action_type}"
    if spell_name:
        narration = f"{actor['name']} casts {spell_name}"

    if action_type == "attack" and roll >= target.get("AC", 10):
        target["HP"] = max(0, target["HP"] - value)
        narration += f" and hits {target['name']} for {value} damage!"
    elif action_type == "heal":
        target["HP"] = target.get("HP", 0) + value
        narration += f" and heals {target['name']} for {value} HP!"
    else:
        narration += " but it fails."

    if status_effect:
        from character_utils import apply_status_effect
        apply_status_effect(target_id, status_effect, 2, actor_id)
        narration += f" {target['name']} is now {status_effect}!"
    if notes:
        narration += f" ({notes})"

    combat_data["participants"][target_id] = target
    combat_data.setdefault("log", []).append(narration)

    from character_utils import resolve_status_effects
    for p_id in combat_data["participants"]:
        resolve_status_effects(p_id)

    combat_data["current_turn"] = (current_index + 1) % len(turn_order)
    ref.set(combat_data)

    return {
        "result": narration,
        "updated_target": target,
        "turn_advanced_to": turn_order[combat_data["current_turn"]],
        "log": combat_data["log"][-5:]
    }, 200

# === GPT Blueprint: NPC INTERACTION ===

@gpt_bp.route('/npc_interact', methods=['POST'])
def npc_interact():
    """
    Endpoint to handle a conversation prompt with an NPC.
    Potentially runs skill checks, stores interaction memory, 
    logs quest hooks, etc.
    """
    data = request.get_json(force=True)
    npc_id = data.get("npc_id")
    player_id = data.get("character_id")
    prompt = data.get("prompt", "")
    conversation_history = data.get("conversation_history", "")
    flags = data.get("flags", {})
    player_memory = data.get("player_memory", "")
    player_state = data.get("player_state", {})

    if not npc_id or not prompt:
        return jsonify({"error": "npc_id and prompt are required"}), 400

    importance_score = score_interaction(flags)

    # Extra context: if player_memory is provided
    extra_context = ""
    if player_memory:
        extra_context += f"Player Memory: {player_memory}. "

    # Load NPC's current motifs, if present
    npc_data = db.reference(f"/npcs/{npc_id}").get() or {}
    motifs = npc_data.get("narrative_motif_pool", {}).get("active", [])
    if motifs:
        formatted = ", ".join(f"{m['theme']} (intensity {m['weight']})" for m in motifs)
        extra_context += f"NPC Emotional State: {formatted}. "

    # Fetch recent short-term memory
    recent_memory = get_recent_interactions(npc_id, player_id, limit=5)
    memory_context = "\n".join(recent_memory)
    extra_context += f"Short-Term Memory:\n{memory_context}"

    # Combine with NPC memory + knowledge
    try:
        npc_memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
        npc_knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    except Exception:
        npc_memory, npc_knowledge = {}, {}

    npc_context = f"NPC Memory: {json.dumps(npc_memory)}; NPC Knowledge: {json.dumps(npc_knowledge)}; {extra_context}"

    # Detect skill check intent
    skill_context = ""
    skill = detect_skill_action(prompt)
    if skill:
        # Example: map skill to a single ability
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
        result = resolve_skill_check(skill, ability_score, modifiers, dc)
        skill_context = (
            f"Skill Check Result: {skill.title()} Roll = {result['roll']} "
            f"vs DC {dc} → {'SUCCESS' if result['success'] else 'FAILURE'}\n"
        )

    full_prompt = (
        f"{skill_context}"
        f"NPC Context: {npc_context}\n"
        f"Conversation History: {conversation_history}\n"
        f"Prompt: {prompt}"
    )

    # Decide which GPT model to use
    model = gpt_router(score=importance_score, flags=flags)
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        reply = response.choices[0].message.content.strip()
        usage = response.get("usage", {})
        log_gpt_usage(model, usage)
    except Exception as e:
        logging.error(f"[NPC INTERACT ERROR] {e}")
        return jsonify({"error": str(e)}), 500

    # Extract quest hook if present
    hook = extract_quest_from_reply(npc_id, player_id, reply)
    if hook.get("quest") and player_id:
        append_to_existing_log(
            player_id=player_id,
            npc_name=npc_id,
            summary=f"[Quest: {hook['quest']['title']}] {hook['quest']['summary']}"
        )

    # Store the interaction in memory
    store_interaction(npc_id, character_id, reply, tags={"type": "dialogue"})

    # Summarize and clean memory
    summarize_and_clean_memory(npc_id, character_id)

    return jsonify({
        "npc_id": npc_id,
        "reply": reply,
        "skill_used": skill,
        "model_used": model,
        "roll_context": skill_context.strip()
    })

@basic_bp.route("/debug_routes")
def debug_routes():
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "rule": rule.rule
        })
    return jsonify(routes)

@basic_bp.route("/basic_routes")
def basic_routes():
    return jsonify([
        {"endpoint": rule.endpoint, "methods": list(rule.methods), "rule": rule.rule}
        for rule in current_app.url_map.iter_rules()
        if rule.endpoint.startswith('basic.')
    ])