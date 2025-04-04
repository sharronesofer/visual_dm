from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, timezone, timedelta
import spacy
from spacy.pipeline import EntityRuler
import random
from random import randint
import logging

# Configure logging for debugging output.
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./firebase_credentials.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://visual-dm-default-rtdb.firebaseio.com/'
})

# Initialize spaCy with an empty English model and add an EntityRuler (without hardcoded patterns)
nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")
# Patterns can be loaded dynamically later

# ---------------------------
# Helper Functions
# ---------------------------
def merge_dicts(old, new):
    for key, value in new.items():
        if isinstance(value, dict) and key in old and isinstance(old[key], dict):
            merge_dicts(old[key], value)
        else:
            old[key] = value
    return old

def generate_motifs(n=3):
    return [{
        "theme": randint(1, 50),
        "lifespan": (life := randint(2, 4)),
        "entropy_tick": 0,
        "weight": 6 - life
    } for _ in range(n)
    ]

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

# ---------------------------
# World State Endpoints
# ---------------------------
# Global State
@app.route('/global_state', methods=['GET'])
def get_global_state():
    logging.debug("Fetching global state")
    ref = db.reference('/global_state')
    state = ref.get() or {}
    return jsonify(state)

@app.route('/global_state', methods=['POST'])
def update_global_state():
    data = request.json
    logging.debug(f"Updating global state with: {data}")
    if not data:
        return jsonify({"error": "No data provided"}), 400
    ref = db.reference('/global_state')
    ref.set(data)
    return jsonify({"message": "Global state updated successfully."})

@app.route('/global_state', methods=['DELETE'])
def delete_global_state():
    logging.debug("Deleting global state")
    ref = db.reference('/global_state')
    ref.delete()
    return jsonify({"message": "Global state deleted."})

# Regional State
@app.route('/regional_state/<region_name>', methods=['GET'])
def get_regional_state(region_name):
    logging.debug(f"Fetching regional state for {region_name}")
    ref = db.reference(f'/regional_state/{region_name}')
    state = ref.get() or {}
    return jsonify(state)

@app.route('/regional_state/<region_name>', methods=['POST'])
def update_regional_state(region_name):
    data = request.json
    logging.debug(f"Updating regional state for {region_name} with: {data}")
    if not data:
        return jsonify({"error": "No data provided"}), 400
    ref = db.reference(f'/regional_state/{region_name}')
    ref.set(data)
    return jsonify({"message": f"Regional state for '{region_name}' updated successfully."})

@app.route('/regional_state/<region_name>', methods=['DELETE'])
def delete_regional_state(region_name):
    logging.debug(f"Deleting regional state for {region_name}")
    ref = db.reference(f'/regional_state/{region_name}')
    ref.delete()
    return jsonify({"message": f"Regional state for '{region_name}' deleted."})

# POI (Point of Interest) State
@app.route('/poi_state/<region_name>/<poi_id>', methods=['GET'])
def get_poi_state(region_name, poi_id):
    logging.debug(f"Fetching POI state for {poi_id} in {region_name}")
    ref = db.reference(f'/poi_state/{region_name}/{poi_id}')
    state = ref.get() or {}
    return jsonify(state)

@app.route('/poi_state/<region_name>/<poi_id>', methods=['POST'])
def update_poi_state(region_name, poi_id):
    data = request.json
    logging.debug(f"Updating POI state for {poi_id} in {region_name} with: {data}")
    if not data:
        return jsonify({"error": "No data provided"}), 400
    ref = db.reference(f'/poi_state/{region_name}/{poi_id}')
    ref.set(data)
    return jsonify({"message": f"POI state for '{poi_id}' in '{region_name}' updated successfully."})

@app.route('/poi_state/<region_name>/<poi_id>', methods=['DELETE'])
def delete_poi_state(region_name, poi_id):
    logging.debug(f"Deleting POI state for {poi_id} in {region_name}")
    ref = db.reference(f'/poi_state/{region_name}/{poi_id}')
    ref.delete()
    return jsonify({"message": f"POI state for '{poi_id}' in '{region_name}' deleted."})

# Building State
@app.route('/building_state/<region_name>/<poi_id>/<building_id>', methods=['GET'])
def get_building_state(region_name, poi_id, building_id):
    logging.debug(f"Fetching building state for {building_id} in POI {poi_id} ({region_name})")
    ref = db.reference(f'/building_state/{region_name}/{poi_id}/{building_id}')
    state = ref.get() or {}
    return jsonify(state)

@app.route('/building_state/<region_name>/<poi_id>/<building_id>', methods=['POST'])
def update_building_state(region_name, poi_id, building_id):
    data = request.json
    logging.debug(f"Updating building state for {building_id} in POI {poi_id} ({region_name}) with: {data}")
    if not data:
        return jsonify({"error": "No data provided"}), 400
    ref = db.reference(f'/building_state/{region_name}/{poi_id}/{building_id}')
    ref.set(data)
    return jsonify({"message": f"Building state for '{building_id}' in POI '{poi_id}' ({region_name}) updated successfully."})

@app.route('/building_state/<region_name>/<poi_id>/<building_id>', methods=['DELETE'])
def delete_building_state(region_name, poi_id, building_id):
    logging.debug(f"Deleting building state for {building_id} in POI {poi_id} ({region_name})")
    ref = db.reference(f'/building_state/{region_name}/{poi_id}/{building_id}')
    ref.delete()
    return jsonify({"message": f"Building state for '{building_id}' in POI '{poi_id}' ({region_name}) deleted."})

# ---------------------------
# Game Time Endpoint (Real-Time Sync)
# ---------------------------
@app.route('/game_time', methods=['GET'])
def get_game_time():
    current_time = datetime.utcnow().isoformat()
    logging.debug(f"Current game time (real time): {current_time}")
    return jsonify({"current_time": current_time})

# ---------------------------
# Memory Layering for NPC Memory
# ---------------------------
@app.route('/update_npc_memory', methods=['POST'])
def update_npc_memory():
    npc_name = request.json.get("npc_name", "").lower()
    interaction = request.json.get("interaction", "")
    timestamp = request.json.get("timestamp", datetime.utcnow().isoformat())

    logging.debug(f"Updating memory for {npc_name} with interaction: {interaction} at {timestamp}")
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
        # Convert 'Z' to '+00:00' if necessary
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str.replace("Z", "+00:00")
        entry_ts = datetime.fromisoformat(timestamp_str)
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

# ---------------------------
# NPC-NPC Interaction Simulation
# ---------------------------
@app.route('/simulate_npc_interactions', methods=['POST'])
def simulate_npc_interactions():
    data = request.json
    region_name = data.get("region_name", "")
    poi_id = data.get("poi_id", "")
    
    logging.debug(f"Simulating interactions at POI {poi_id} in region {region_name}")
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

# ---------------------------
# NPC Knowledge Storage Endpoints
# ---------------------------
@app.route('/npc_knowledge/<npc_name>', methods=['GET'])
def get_npc_knowledge(npc_name):
    npc_name = npc_name.lower()
    ref = db.reference(f'/npc_knowledge/{npc_name}')
    knowledge = ref.get() or {"known_pcs": [], "rumors": [], "events": []}
    return jsonify(knowledge)

@app.route('/npc_knowledge/<npc_name>', methods=['POST'])
def update_npc_knowledge(npc_name):
    npc_name = npc_name.lower()
    data = request.json
    logging.debug(f"Updating knowledge for {npc_name} with: {data}")
    if not data:
        return jsonify({"error": "No data provided"}), 400

    ref = db.reference(f'/npc_knowledge/{npc_name}')
    knowledge = ref.get() or {"known_pcs": [], "rumors": [], "events": []}

    if "known_pcs" in data:
        for pc in data["known_pcs"]:
            if pc not in knowledge["known_pcs"]:
                knowledge["known_pcs"].append(pc)
    if "rumors" in data:
        for rumor in data["rumors"]:
            if rumor not in knowledge["rumors"]:
                knowledge["rumors"].append(rumor)
    if "events" in data:
        for event in data["events"]:
            if event not in knowledge["events"]:
                knowledge["events"].append(event)

    ref.set(knowledge)
    return jsonify({"message": f"NPC knowledge updated for {npc_name}", "knowledge": knowledge})

@app.route('/npc_knowledge/<npc_name>', methods=['DELETE'])
def delete_npc_knowledge(npc_name):
    npc_name = npc_name.lower()
    ref = db.reference(f'/npc_knowledge/{npc_name}')
    ref.delete()
    return jsonify({"message": f"NPC knowledge deleted for {npc_name}"})

# ---------------------------
# Faction + Trait Weighting Endpoints
# ---------------------------
@app.route('/npc_relationship_matrix/<npc_name>', methods=['GET'])
def get_npc_relationship_matrix(npc_name):
    npc_name = npc_name.lower()
    ref = db.reference(f'/npc_opinion_matrix/{npc_name}')
    matrix = ref.get() or {}
    return jsonify(matrix)

@app.route('/npc_relationship_matrix/<npc_name>/<target_npc>', methods=['GET'])
def get_npc_relationship(npc_name, target_npc):
    npc_name = npc_name.lower()
    target_npc = target_npc.lower()
    ref = db.reference(f'/npc_opinion_matrix/{npc_name}/{target_npc}')
    relationship = ref.get() or {"trust_score": 0, "respect": 0, "envy": 0, "faction_bias": {}}
    return jsonify(relationship)

@app.route('/npc_relationship_matrix/<npc_name>/<target_npc>', methods=['POST'])
def update_npc_relationship(npc_name, target_npc):
    npc_name = npc_name.lower()
    target_npc = target_npc.lower()
    data = request.json
    logging.debug(f"Updating relationship from {npc_name} to {target_npc} with: {data}")
    if not data:
        return jsonify({"error": "No data provided."}), 400

    ref = db.reference(f'/npc_opinion_matrix/{npc_name}/{target_npc}')
    current = ref.get() or {"trust_score": 0, "respect": 0, "envy": 0, "faction_bias": {}}
    
    if "trust_score" in data:
        current["trust_score"] += data["trust_score"]
    if "respect" in data:
        current["respect"] += data["respect"]
    if "envy" in data:
        current["envy"] += data["envy"]
    if "faction_bias" in data and isinstance(data["faction_bias"], dict):
        for faction, adjustment in data["faction_bias"].items():
            current["faction_bias"][faction] = current["faction_bias"].get(faction, 0) + adjustment

    ref.set(current)
    return jsonify({
        "message": f"Updated relationship from {npc_name} to {target_npc}.",
        "relationship": current
    })

@app.route('/npc_relationship_matrix/<npc_name>/<target_npc>', methods=['DELETE'])
def delete_npc_relationship(npc_name, target_npc):
    npc_name = npc_name.lower()
    target_npc = target_npc.lower()
    ref = db.reference(f'/npc_opinion_matrix/{npc_name}/{target_npc}')
    ref.delete()
    return jsonify({
        "message": f"Deleted relationship from {npc_name} to {target_npc}."
    })

# ---------------------------
# Action Economy Endpoint
# ---------------------------
@app.route('/perform_action', methods=['POST'])
def perform_action():
    data = request.json
    character_name = data.get("character_name", "").lower()
    action_type = data.get("action_type", "")
    parameters = data.get("parameters", {})

    logging.debug(f"Performing action {action_type} for {character_name} with parameters {parameters}")
    if not character_name or not action_type:
        return jsonify({"error": "character_name and action_type are required"}), 400

    standard_actions = ["Attack", "Move", "Flee", "Skill", "Use Item"]

    if action_type in standard_actions:
        result = {
            "character": character_name,
            "action": action_type,
            "details": f"{action_type} executed with parameters {parameters}",
            "outcome": "Standard backend logic processed the action."
        }
        return jsonify(result)
    
    elif action_type == "Wildcard":
        input_text = parameters.get("input", "")
        result = {
            "character": character_name,
            "action": action_type,
            "details": f"Received wildcard input: '{input_text}'",
            "outcome": "Wildcard action processing pending GPT integration."
        }
        return jsonify(result)
    
    else:
        return jsonify({"error": "Invalid action type provided."}), 400

# ---------------------------
# Rollback Engine & Debug Endpoints
# ---------------------------
@app.route('/create_snapshot', methods=['POST'])
def create_snapshot():
    data = request.json
    entity_type = data.get("entity_type")
    entity_id = data.get("entity_id")
    source_path = data.get("source_path")
    
    logging.debug(f"Creating snapshot for {entity_type} {entity_id} from {source_path}")
    if not entity_type or not entity_id or not source_path:
        return jsonify({"error": "entity_type, entity_id, and source_path are required"}), 400

    ref = db.reference(source_path)
    state = ref.get()
    if state is None:
        return jsonify({"error": "No state found at the specified source_path"}), 404

    timestamp = datetime.utcnow().isoformat()
    snapshot_data = {
        "snapshot_time": timestamp,
        "data": state,
        "source_path": source_path
    }
    snapshot_ref = db.reference(f'/snapshots/{entity_type}/{entity_id}/{timestamp}')
    snapshot_ref.set(snapshot_data)
    
    snapshots_folder_ref = db.reference(f'/snapshots/{entity_type}/{entity_id}')
    snapshots = snapshots_folder_ref.get() or {}
    snapshot_keys = sorted(snapshots.keys())
    while len(snapshot_keys) > 5:
        oldest = snapshot_keys.pop(0)
        db.reference(f'/snapshots/{entity_type}/{entity_id}/{oldest}').delete()
    
    return jsonify({"message": "Snapshot created", "snapshot": snapshot_data})

@app.route('/list_snapshots/<entity_type>/<entity_id>', methods=['GET'])
def list_snapshots(entity_type, entity_id):
    ref = db.reference(f'/snapshots/{entity_type}/{entity_id}')
    snapshots = ref.get() or {}
    return jsonify(snapshots)

@app.route('/rollback_snapshot', methods=['POST'])
def rollback_snapshot():
    data = request.json
    entity_type = data.get("entity_type")
    entity_id = data.get("entity_id")
    snapshot_key = data.get("snapshot_key")
    
    logging.debug(f"Rolling back {entity_type} {entity_id} to snapshot {snapshot_key}")
    if not entity_type or not entity_id or not snapshot_key:
        return jsonify({"error": "entity_type, entity_id, and snapshot_key are required"}), 400

    snapshot_ref = db.reference(f'/snapshots/{entity_type}/{entity_id}/{snapshot_key}')
    snapshot_data = snapshot_ref.get()
    if not snapshot_data:
        return jsonify({"error": "Snapshot not found"}), 404

    source_path = snapshot_data.get("source_path")
    state_data = snapshot_data.get("data")
    if not source_path or state_data is None:
        return jsonify({"error": "Invalid snapshot data"}), 500

    ref = db.reference(source_path)
    ref.set(state_data)
    return jsonify({"message": f"Rolled back to snapshot {snapshot_key}", "state": state_data})

@app.route('/compare_snapshot', methods=['POST'])
def compare_snapshot():
    data = request.json
    entity_type = data.get("entity_type")
    entity_id = data.get("entity_id")
    snapshot_key = data.get("snapshot_key")
    
    logging.debug(f"Comparing current state with snapshot {snapshot_key} for {entity_type} {entity_id}")
    if not entity_type or not entity_id or not snapshot_key:
        return jsonify({"error": "entity_type, entity_id, and snapshot_key are required"}), 400

    snapshot_ref = db.reference(f'/snapshots/{entity_type}/{entity_id}/{snapshot_key}')
    snapshot_data = snapshot_ref.get()
    if not snapshot_data:
        return jsonify({"error": "Snapshot not found"}), 404

    source_path = snapshot_data.get("source_path")
    current_state = db.reference(source_path).get()
    return jsonify({
        "snapshot": snapshot_data,
        "current_state": current_state
    })

# ---------------------------
# Integrated Debugging Endpoint
# ---------------------------
@app.route('/debug_system', methods=['GET'])
def debug_system():
    """
    Returns aggregated debugging information about the system.
    Includes:
      - Global state
      - Current game time
      - Count of snapshots in global_state (if any)
      - EntityRuler status from spaCy
    """
    debug_info = {}
    
    # Global state debug
    global_state = db.reference('/global_state').get() or {}
    debug_info["global_state"] = global_state
    
    # Game time debug (current UTC time)
    current_time = datetime.utcnow().isoformat()
    debug_info["game_time"] = current_time
    
    # Snapshot count for global_state (if exists)
    snapshots_global = db.reference('/snapshots/global_state').get() or {}
    if snapshots_global:
        debug_info["global_snapshots_count"] = sum(len(v) for v in snapshots_global.values())
    else:
        debug_info["global_snapshots_count"] = 0

    # EntityRuler status
    try:
        ruler_pipe = nlp.get_pipe("entity_ruler")
        patterns = ruler_pipe.patterns if hasattr(ruler_pipe, "patterns") else []
        debug_info["entity_ruler_pattern_count"] = len(patterns)
    except Exception as e:
        debug_info["entity_ruler_error"] = str(e)
    
    logging.debug(f"Debug system info: {debug_info}")
    return jsonify(debug_info)

# ---------------------------
# Run the Flask App
# ---------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
