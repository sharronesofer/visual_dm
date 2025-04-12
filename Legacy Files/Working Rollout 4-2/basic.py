import os
import json
import openai
from flask import Blueprint, request, jsonify, render_template
from firebase_admin import db
from datetime import datetime, timezone, timedelta
from random import randint
import random
from gpt_endpoints import log_gpt_usage, gpt_router
from rules_engine import resolve_combat_action
from worldgen import choose_land_type, roll_danger_for_tile, should_generate_poi
from character_utils import complete_character

basic_bp = Blueprint('basic', __name__)

# === Monster Combat Support ===
from itertools import combinations

def load_monsters_from_folder():
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
    min_cr = round(player_level * 0.25 - 0.25, 2)
    max_cr = round(player_level * 0.25 + 0.25, 2)

    candidates = [m for m in ALL_MONSTERS if min_cr <= m["challenge_rating"] <= max_cr]
    if not candidates:
        return []

    best_combo = []
    for r in range(1, 5):  # Try combos up to 4 monsters
        for combo in combinations(candidates, r):
            total_cr = round(sum(m["challenge_rating"] for m in combo), 2)
            if min_cr <= total_cr <= max_cr:
                best_combo = list(combo)
                break
        if best_combo:
            break
    return best_combo

# === Index Route ===
@basic_bp.route('/')
def index():
    return render_template("index.html")

# === Player Movement with Combat Trigger ===
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

# Player Movement with Combat Roll and POI Generation
@basic_bp.route('/move_player', methods=['POST'])
def move_player():
    data = request.json
    player_id = data.get("player_id")
    new_location = data.get("new_location")

    if not player_id or not new_location:
        return jsonify({"error": "player_id and new_location are required"}), 400

    player_ref = db.reference(f'/players/{player_id}')
    player_state = player_ref.get() or {}

    prev_location = player_state.get("location")

    def parse_coords(loc):
        try:
            x, y = map(int, loc.split("_"))
            return x, y
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
        x = x1 + round(i * dx / steps)
        y = y1 + round(i * dy / steps)
        path.append((x, y))

    combat_info = None
    for x, y in path:
        key = f"{x}_{y}"

        terrain = db.reference(f"/terrain_map/{key}").get()
        if not terrain:
            region_id = player_state.get("region_id", "default")
            terrain = choose_land_type(x, y, region_id)

        tile_ref = db.reference(f"/locations/{key}")
        tile_data = tile_ref.get() or {}

        if "danger_level" not in tile_data:
            tile_data["danger_level"] = roll_danger_for_tile(x, y)

        if "POI" not in tile_data:
            if should_generate_poi(x, y):
                try:
                    # Step 1: Generate name + description
                    gpt_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Generate a brief name and description for a fantasy Point of Interest."},
                            {"role": "user", "content": f"Create a location in a {terrain} biome."}
                        ],
                        temperature=0.8,
                        max_tokens=150
                    )
                    lore = gpt_response.choices[0].message.content.strip()
                    usage = gpt_response.get("usage", {})
                    log_gpt_usage("gpt-3.5-turbo", usage)
                    tile_data.update({
                        "POI": True,
                        "terrain": terrain,
                        "region_id": player_state.get("region_id", "default"),
                        "description": lore
                    })

                    # Step 2: Classify POI tone and focus
                    tag_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Classify the tone (friendly, neutral, hostile) and focus (combat, roleplay, exploration) of a POI based on its description."},
                            {"role": "user", "content": lore }
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
                    log_gpt_usage("gpt-3.5-turbo", tag_response.get("usage", {}))

                    # Step 3: Generate buildings
                    building_response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Generate a list of buildings for a fantasy Point of Interest."},
                            {"role": "user", "content": f"List the buildings that might be found at a new POI in a {terrain} biome. The region encourages {tile_data.get('region_id', 'unknown')} themes."}
                        ],
                        temperature=0.8,
                        max_tokens=250
                    )
                    building_text = building_response.choices[0].message.content.strip()
                    tile_data["buildings"] = building_text
                    log_gpt_usage("gpt-3.5-turbo", building_response.get("usage", {}))

                    # Step 4: Generate NPCs
                    tile_ref.set(tile_data)
                    generate_npcs_for_poi(x, y)
                    tile_data = tile_ref.get()

                except Exception as e:
                    tile_data["POI_error"] = str(e)

        tile_ref.set(tile_data)

        dl = tile_data["danger_level"]
        combat_chance = dl * 7.5
        combat_roll = randint(0, 99)

        if combat_roll < combat_chance:
            player_state["location"] = key
            updated_player = complete_character(player_state)
            player_ref.set(updated_player)

            combat_info = {
                "combat_triggered": True,
                "combat_tile": key,
                "combat_chance_percent": combat_chance,
                "combat_roll": combat_roll,
                "player_state": updated_player
            }
            break

    if not combat_info:
        player_state["location"] = new_location
        updated_player = complete_character(player_state)
        player_ref.set(updated_player)

        combat_info = {
            "combat_triggered": False,
            "player_state": updated_player
        }

    return jsonify({"message": f"Player {player_id} moved to {combat_info['player_state']['location']}", **combat_info})

def generate_location_gpt_internal(x, y):
    prompt = f"The player has entered new territory at ({x}, {y}). Generate a location."
    system_prompt = (
        "You are a worldbuilder AI. Generate a JSON object representing a fantasy map location. "
        "It should include: name, description, danger_level (0-10), buildings (if any), npcs (if any), tags, and lore_hooks. "
        "Use JSON formatting only."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=500
    )

    content = response.choices[0].message.content.strip()
    location_data = json.loads(content)
    location_data["coordinates"] = {"x": x, "y": y}
    db.reference(f"/locations/{x}_{y}").set(location_data)
    return location_data

# Debug Global State
@basic_bp.route('/debug_state', methods=['GET'])
def debug_state():
    try:
        state = db.reference('/global_state').get() or {}
        return jsonify(state)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update NPC Memory
@basic_bp.route('/update_npc_memory', methods=['POST'])
def update_npc_memory():
    data = request.json
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
            # Ensure entry_ts is timezone-aware
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

# Simulate NPC Interactions
@basic_bp.route('/simulate_npc_interactions', methods=['POST'])
def simulate_npc_interactions():
    data = request.json
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

    interactions = []
    encounter_types = {
        "friendly": 2,
        "hostile": -3,
        "neutral": 0,
        "romantic": 3,
        "ideological": 1
    }
    
    for npc in npcs:
        partners = [other for other in npcs if other != npc]
        if not partners:
            continue
        if random.random() < 0.5:
            partner = random.choice(partners)
            encounter = random.choice(list(encounter_types.keys()))
            interaction_entry = {
                "npc": npc,
                "partner": partner,
                "encounter_type": encounter,
                "timestamp": datetime.utcnow().isoformat()
            }
            interactions.append(interaction_entry)
            
            matrix_ref = db.reference(f'/npc_opinion_matrix/{npc}/{partner}')
            current_score = matrix_ref.get() or 0
            new_score = current_score + encounter_types.get(encounter, 0)
            matrix_ref.set(new_score)
    
    return jsonify({
        "message": f"Simulated interactions at POI '{poi_id}' in region '{region_name}'.",
        "interactions": interactions
    })

# ASCII Map Endpoint
@basic_bp.route('/ascii_map', methods=['GET'])
def ascii_map():
    all_locations = db.reference('/locations').get() or {}
    xs = []
    ys = []
    
    for key in all_locations.keys():
        try:
            x_str, y_str = key.split('_')
            x = int(x_str)
            y = int(y_str)
            xs.append(x)
            ys.append(y)
        except Exception:
            continue

    if not xs or not ys:
        return "No locations available.", 200, {'Content-Type': 'text/plain'}
    
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    grid = []
    for y in range(max_y, min_y - 1, -1):
        row = ""
        for x in range(min_x, max_x + 1):
            key = f"{x}_{y}"
            if key in all_locations:
                row += "L"
            else:
                row += "."
        grid.append(row)
    ascii_map_text = "\n".join(grid)
    return ascii_map_text, 200, {'Content-Type': 'text/plain'}

# Combat Round Simulation
@basic_bp.route('/combat_round', methods=['POST'])
def combat_round():
    data = request.json
    combatants = data.get("combatants", [])
    if not combatants or not isinstance(combatants, list):
         return jsonify({"error": "A combatants list is required."}), 400

    random.shuffle(combatants)
    combat_log = []

    for attacker in combatants:
        if attacker.get("hp", 0) <= 0:
            continue
        targets = [c for c in combatants if c["id"] != attacker["id"] and c.get("hp", 0) > 0]
        if not targets:
            combat_log.append(f"{attacker['id']} has no targets to attack.")
            continue
        target = random.choice(targets)
        damage = random.randint(5, 15)
        target["hp"] = max(target.get("hp", 0) - damage, 0)
        combat_log.append(f"{attacker['id']} attacks {target['id']} for {damage} damage. {target['id']} HP is now {target['hp']}.")
    
    return jsonify({"combatants": combatants, "combat_log": combat_log})

# Questlog Endpoints
@basic_bp.route('/questlog/<player_id>', methods=['GET'])
def get_questlog(player_id):
    questlog = db.reference(f'/questlogs/{player_id}').get() or []
    return jsonify(questlog)

@basic_bp.route('/questlog/<player_id>', methods=['POST'])
def add_quest(player_id):
    data = request.json
    quest = data.get("quest")
    if not quest:
         return jsonify({"error": "quest is required"}), 400
    questlog_ref = db.reference(f'/questlogs/{player_id}')
    questlog = questlog_ref.get() or []
    new_entry = {"quest": quest, "timestamp": datetime.utcnow().isoformat()}
    questlog.append(new_entry)
    questlog_ref.set(questlog)
    return jsonify({"message": "Quest added", "questlog": questlog})

# Region Management Endpoints
@basic_bp.route('/region/<region_id>', methods=['GET'])
def get_region(region_id):
    region = db.reference(f'/regions/{region_id}').get() or {}
    return jsonify(region)

@basic_bp.route('/region/<region_id>', methods=['POST'])
def update_region(region_id):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    region_ref = db.reference(f'/regions/{region_id}')
    region_ref.set(data)
    return jsonify({"message": f"Region {region_id} updated.", "region": data})

@basic_bp.route('/region/<region_id>', methods=['DELETE'])
def delete_region(region_id):
    region_ref = db.reference(f'/regions/{region_id}')
    region_ref.delete()
    return jsonify({"message": f"Region {region_id} deleted."})

# Rotate Character Motifs
@basic_bp.route('/rotate_motifs/<character_id>', methods=['POST'])
def rotate_motifs(character_id):
    ref = db.reference(f'/characters/{character_id}')
    character = ref.get()
    if not character:
         return jsonify({"error": "Character not found."}), 404
    updated_character = complete_character(character)
    ref.set(updated_character)
    return jsonify({"message": "Character motifs rotated", "character": updated_character})

# --- Helper Functions for Motif Management ---
def generate_motifs(n=3):
    return [{
        "theme": randint(1, 50),
        "lifespan": (life := randint(2, 4)),
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
        life = randint(2, 4)
        new_motif = {
            "theme": randint(1, 50),
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
    return {
        **core,
        "XP": core.get("XP", 0),
        "alignment": core.get("alignment", "Neutral"),
        "proficiencies": core.get("proficiencies", []),
        "features": core.get("features", []),
        "languages": core.get("languages", ["Common"]),
        "inventory": core.get("inventory", core.get("equipment", [])),
        "faction_affiliations": core.get("faction_affiliations", []),
        "reputation": core.get("reputation", 0),
        "opinion_of_party": core.get("opinion_of_party", {}),
        "hidden_ambition": core.get("hidden_ambition", ""),
        "current_location": core.get("location", "Unknown"),
        "last_rest_timestamp": core.get("last_rest_timestamp", datetime.utcnow().isoformat()),
        "narrative_motif_pool": core["narrative_motif_pool"]
    }

@basic_bp.route('/chat')
def chat():
    return render_template("chat.html")

