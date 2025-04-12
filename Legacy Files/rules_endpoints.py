"""
rules_endpoints.py
Holds the 'rules' Blueprint and routes for validating characters, skill checks, 
combat resolution, rule lookup, etc.
"""

import json
import logging
import openai
import random
from flask import Blueprint, request, jsonify
from firebase_admin import db

if __name__ == "__main__":
    # For debugging purposes, you can run this file standalone.
    # In production, this blueprint is registered in your main Flask app.
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(rules_bp, url_prefix='/rules')
    app.run(debug=True)
# Possibly referencing 'lookup_rule' or 'resolve_skill_check' from a separate "rules_engine"
# If so, import them:
try:
    from rules_engine import (
        validate_character_creation,
        resolve_skill_check,
        resolve_combat_action,
        lookup_rule,
        lookup_spell
    )
except ImportError:
    # fallback stubs
    def validate_character_creation(data): return {}
    def resolve_skill_check(skill, ability_score, modifiers, dc): return {}
    def resolve_combat_action(a, b, c): return {}
    def lookup_rule(cat, name): return {}
    def lookup_spell(level, name): return {}

# ADD THIS HELPER:
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {path}: {e}")
        return {}

rules_bp = Blueprint('rules', __name__)
# If referencing GPT usage:
try:
    from gpt_endpoints import log_gpt_usage
except ImportError:
    def log_gpt_usage(*args, **kwargs):
        pass

# ========== The rest of your route definitions (validate_character, etc.) follow ==========
################################################################################
# 2) CORE RULES ENGINE LOGIC (skills, , feats, abilities, etc.)
################################################################################

# Pre-load rule data
skills = load_json("rules/skills.json")
feat_list = load_json("rules/feats.json")
feats = {feat["name"]: feat for feat in feat_list}
abilities = load_json("rules/abilities.json")
feats_index = load_json("rules/feats_index.json")

def validate_character_creation(data):
    """
    Validates a character creation object, checking class validity, feats,
    and ability prerequisites. Returns a dict with any issues found.
    """
    issues = []
    name = data.get("name")
    race = data.get("race")
    cls = data.get("class")
    feats_input = data.get("feats", [])
    abilities_input = data.get("abilities", {})

    # Validate abilities
    for ability, score in abilities_input.items():
        if ability not in abilities:
            issues.append(f"Unknown ability: {ability}")
        elif not isinstance(score, int):
            issues.append(f"Invalid score for {ability}: must be int")

    # Validate feats (including prerequisites)
    for feat in feats_input:
        if feat not in feats:
            issues.append(f"Unknown feat: {feat}")
        else:
            prereq = feats[feat].get("prerequisites", [])
            for condition in prereq:
                # Example: "Str15"
                if condition.startswith("Str"):
                    required_str = int(condition[-2:])
                    if abilities_input.get("Strength", 0) < required_str:
                        issues.append(f"Missing prerequisite for {feat}: {condition}")
                # Additional prerequisite logic could go here

    return {
        "character": name,
        "valid": len(issues) == 0,
        "issues": issues
    }

def resolve_skill_check(skill, ability_score, modifiers, dc):
    """
    Resolves a skill check by calculating base bonus from ability_score,
    adding modifiers, and comparing against dc.
    """
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

def resolve_combat_action(attacker, defender, roll):
    """
    Resolves a basic combat action by comparing roll + bonuses to defender's AC.
    """
    bab = attacker.get("base_attack_bonus", 0)
    strength_mod = attacker.get("strength_modifier", 0)
    attack_total = roll + bab + strength_mod
    ac = defender.get("armor_class", 10)
    hit = attack_total >= ac

    return {
        "roll": roll,
        "base_attack_bonus": bab,
        "strength_modifier": strength_mod,
        "attack_total": attack_total,
        "defender_ac": ac,
        "hit": hit,
        "combat_narration": (
            f"Attack Roll: {roll} + {bab} (BAB) + {strength_mod} (STR) = "
            f"{attack_total} vs AC {ac} → {'HIT' if hit else 'MISS'}"
        )
    }

def lookup_rule(category, name):
    """
    Looks up rules from the loaded JSON resources (skills, , feats, abilities).
    """
    name = name.strip()
    if category == "skill":
        return skills.get(name)
    elif category == "feat":
        return feats.get(name)
    elif category == "ability":
        return abilities.get(name)
    return None

def lookup_spell(level, name):
    """
    Attempts to load a spells JSON file for the given level, then
    look for a spell matching 'name'. Returns the spell dict or None.
    """
    try:
        path = f"rules/spells/{int(level)}.json"
        spells_data = load_json(path)
        name_lower = name.strip().lower()
        for key, value in spells_data.items():
            if key.lower() == name_lower:
                return value
        return None
    except Exception as e:
        print(f"Spell lookup failed: {e}")
        return None

################################################################################
# 3) WORLD/EVENT/LOGIC (log_world_event, rumor distortion, sync_event_beliefs, etc.)
################################################################################

def log_world_event(event_data):
    """
    Logs a world event in Firebase under /global_state/world_log/<event_id>.
    """
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    event_data["event_id"] = event_id
    event_data["timestamp"] = datetime.utcnow().isoformat()
    ref = db.reference(f"/global_state/world_log/{event_id}")
    ref.set(event_data)
    return event_data

def distort_summary(summary):
    """
    Slightly distorts or confuses the event summary to simulate rumors.
    """
    return summary.replace("was", "may have been").replace("at", "somewhere near")

def fabricate_alternate(event_data):
    """
    Creates a wholly fabricated rumor about the event.
    """
    return f"Someone claims {event_data.get('summary', 'something strange')} — but it sounds suspicious."

def generate_npc_belief(npc_name, event_data):
    """
    Generates a rumor/belief record for an NPC, based on random 'trust' logic.
    """
    trust_level = random.randint(1, 5)
    roll = random.random()
    original_summary = event_data.get("summary", "some event happened")

    if roll < trust_level / 5:
        accuracy = "accurate"
        belief_summary = original_summary
    elif roll < 0.8:
        accuracy = "partial"
        belief_summary = distort_summary(original_summary)
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

def sync_event_beliefs(region_name, event_data):
    """
    For a given region, go through each POI's NPCs and store a belief record
    about the event in /npc_knowledge/<npc>/beliefs/<event_id>.
    """
    poi_ref = db.reference(f"/poi_state/{region_name}")
    pois = poi_ref.get() or {}

    npc_belief_count = 0
    for poi_id, poi_data in pois.items():
        npcs = poi_data.get("npcs_present", [])
        for npc_name in npcs:
            belief = generate_npc_belief(npc_name, event_data)
            belief_ref = db.reference(f"/npc_knowledge/{npc_name}/beliefs/{event_data['event_id']}")
            belief_ref.set(belief)
            npc_belief_count += 1

    return npc_belief_count

################################################################################
# 4) RUMOR/KNOWLEDGE SHARING LOGIC (mutate_belief_for_receiver, propagate_beliefs, etc.)
################################################################################

def mutate_belief_for_receiver(belief, trust_level):
    """
    Ask GPT to rewrite the belief based on trust level (1–5).
    If trust is low, the summary becomes less accurate.
    """
    prompt = (
        f"An NPC hears the following rumor: '{belief['summary']}'\n"
        f"They trust the source at level {trust_level}.\n"
        f"Rewrite the belief summary they adopt, making it less accurate if trust is low.\n"
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
        accuracy = min(1.0, 0.4 + 0.15 * trust_level)  # Adjust for trust

        return {
            "summary": summary,
            "source": "rumor",
            "accuracy": accuracy,
            "trust_level": trust_level,
            "tags": belief.get("tags", [])
        }
    except Exception:
        # In case GPT fails, return the original unmodified belief
        return belief

def propagate_beliefs(region_id):
    """
    Iterates over NPCs in the given region, picks a random belief from one NPC,
    and attempts to share it with others in the same POI, factoring in their trust.
    """
    all_npcs = db.reference("/npcs").get() or {}
    by_poi = {}

    # Group NPCs by their current POI
    for npc_id, npc_data in all_npcs.items():
        if npc_data.get("region_id") != region_id:
            continue
        poi = npc_data.get("mobility", {}).get("current_poi")
        if poi:
            by_poi.setdefault(poi, []).append((npc_id, npc_data))

    results = []

    for poi, npc_group in by_poi.items():
        for sender_id, sender_data in npc_group:
            sender_beliefs = db.reference(f"/npc_knowledge/{sender_id}/beliefs").get() or {}
            if not sender_beliefs:
                continue

            # Pick one random belief from the sender
            belief_key = random.choice(list(sender_beliefs.keys()))
            belief_record = sender_beliefs[belief_key]

            for receiver_id, receiver_data in npc_group:
                if receiver_id == sender_id:
                    continue

                # Check if the receiver trusts the sender
                rel = db.reference(f"/npcs/{receiver_id}/relationships/{sender_id}").get() or {}
                trust = rel.get("trust", 0)
                if trust < 2:
                    continue
                if random.random() > trust / 10:
                    continue  # No share this time

                # Convert the existing record so GPT can mutate the summary
                existing_belief = {
                    "summary": belief_record["belief_summary"],
                    "tags": belief_record.get("tags", [])
                }
                new_belief = mutate_belief_for_receiver(existing_belief, trust_level=trust)

                # Store the mutated belief in the receiver's knowledge
                db.reference(f"/npc_knowledge/{receiver_id}/beliefs/{belief_key}").set(new_belief)
                results.append((sender_id, receiver_id, new_belief["summary"]))

    return results

def share_rumors_between_npcs(npc_a, npc_b, strength_threshold=3):
    """
    Shares knowledge from npc_a to npc_b if trust is high enough.
    """
    matrix_ref = db.reference(f"/npc_opinion_matrix/{npc_a}/{npc_b}")
    trust = matrix_ref.get() or 0
    if trust < strength_threshold:
        return {"status": "too_low_trust", "shared": []}

    a_knowledge = db.reference(f"/npc_knowledge/{npc_a}").get() or {}
    b_knowledge = db.reference(f"/npc_knowledge/{npc_b}").get() or {}
    shared = []

    for topic, belief in a_knowledge.items():
        # If NPC B already has it with >= certainty, skip
        if topic in b_knowledge:
            existing_certainty = b_knowledge[topic].get("certainty", 0.5)
            incoming_certainty = belief.get("certainty", 0.5) * 0.8
            if incoming_certainty <= existing_certainty:
                continue

        # 50% chance to share each item
        if random.random() < 0.5:
            new_certainty = belief.get("certainty")
            if new_certainty is None:
                source = belief.get("source", "")
                if source == "global_truth":
                    new_certainty = 1.0
                elif source:
                    new_certainty = round(random.uniform(0.6, 0.9), 2)
                else:
                    new_certainty = round(random.uniform(0.3, 0.6), 2)

            b_knowledge[topic] = {
                "belief": belief.get("belief"),
                "source": npc_a,
                "shared_on": db.SERVER_TIMESTAMP,
                "certainty": round(new_certainty * 0.8, 2)
            }
            shared.append(topic)

    if shared:
        db.reference(f"/npc_knowledge/{npc_b}").set(b_knowledge)

    return {"status": "shared", "shared": shared}

################################################################################
# 5) TENSION ENGINE LOGIC (get_tension, modify_tension, reset_tension, decay_tension)
################################################################################

TENSION_LEVELS = [
    (0, 10, "peaceful"),
    (11, 30, "watchful"),
    (31, 60, "anxious"),
    (61, 80, "violent"),
    (81, 100, "collapsing")
]

def get_tension_descriptor(level):
    for low, high, label in TENSION_LEVELS:
        if low <= level <= high:
            return label
    return "unknown"

def get_tension(region_id):
    """
    Returns tension data for a region, including a descriptor.
    """
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
    Increments or decrements tension for the given region, clamping 0..100.
    """
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}

    modifiers = data.get("modifiers", {})
    modifiers[source] = modifiers.get(source, 0) + amount

    level_sum = sum(modifiers.values())
    level_sum = max(0, min(level_sum, 100))

    data.update({
        "level": level_sum,
        "modifiers": modifiers,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

def reset_tension(region_id):
    """
    Resets the region's tension to zero and clears modifiers.
    """
    ref = db.reference(f"/regions/{region_id}/tension")
    ref.set({
        "level": 0,
        "modifiers": {},
        "last_modified": datetime.utcnow().isoformat()
    })
    return get_tension(region_id)

def decay_tension(region_id, decay_rate=1):
    """
    Decreases each tension modifier by 'decay_rate' (default=1),
    recalculates final tension, clamps to 0..100.
    """
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {}
    if not data:
        return {"error": "No tension data for this region"}

    modifiers = data.get("modifiers", {})
    updated = {}
    for k, v in modifiers.items():
        if abs(v) > decay_rate:
            updated[k] = v - decay_rate if v > 0 else v + decay_rate

    level_sum = sum(updated.values())
    level_sum = max(0, min(level_sum, 100))

    data.update({
        "level": level_sum,
        "modifiers": updated,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

races = load_json('rules/races.json')
skills = load_json('rules/skills.json')
feat_list = load_json("rules/feats.json")
feats = {feat["name"]: feat for feat in feat_list}
equipment = load_json("rules/equipment.json")
feats_index = load_json("rules/feats_index.json")

# === Rule List Endpoints for Visual Client ===

@rules_bp.route('/starting_kits', methods=['GET'])
def get_starting_kits():
    """
    Returns the starting kits data.
    The client will use this endpoint to present kit choices instead of individual equipment.
    """
    try:
        with open("rules/starter_kits.json", "r") as f:
            kits = json.load(f)
    except Exception as e:
        logging.error(f"Error loading starter_kits.json: {e}")
        kits = {}
    return jsonify(kits)

@rules_bp.route('/feats_by_category', methods=['GET'])
def get_feats_by_category():
    """
    Loads feats from the JSON file and organizes them by their "category" field.
    Example output:
    {
      "Attack": [ {feat1}, {feat2}, ... ],
      "Spell":  [ {feat3}, {feat4}, ... ],
      "Buff":   [ ... ],
      "Debuff": [ ... ],
      "Ability": [ ... ],
      "Misc": [ ... ]
    }
    """
    feats = load_json("rules/feats.json")
    groups = {}
    for feat in feats:
        category = feat.get("category", "Misc")
        groups.setdefault(category, []).append(feat)
    return jsonify(groups)

@rules_bp.route('/feats_index', methods=['GET'])
def get_feats_index():
    return jsonify(feats_index)

@rules_bp.route('/feats', methods=['GET'])
def get_all_feats():
    # Loads feats from a JSON file (e.g. rules/feats.json)
    feats = load_json("rules/feats.json")
    return jsonify(feats)

@rules_bp.route('/skills', methods=['GET'])
def get_all_skills():
    # Loads skills from a JSON file (e.g. rules/skills.json)
    skills = load_json("rules/skills.json")
    return jsonify(skills)

@rules_bp.route('/ability_scores/4d6', methods=['GET'])
def roll_ability_scores():
    """
    Rolls 6 ability scores using 4d6-drop-lowest.
    If all four dice are 6s, returns a score of 19.
    """
    results = []
    for _ in range(6):
        rolls = sorted([random.randint(1, 6) for _ in range(4)], reverse=True)
        total = 19 if rolls == [6, 6, 6, 6] else sum(rolls[:3])
        results.append({
            "rolls": rolls,
            "score": total
        })
    return jsonify({
        "method": "4d6-drop-lowest",
        "results": results
    })

@rules_bp.route('/races', methods=['GET'])
def get_all_races():
    # Loads races from a JSON file (e.g. rules/races.json)
    races = load_json("rules/races.json")
    return jsonify(races)

@rules_bp.route('/equipment', methods=['GET'])
def get_equipment():
    # Note: With the new kits system, equipment may be deprecated on its own.
    equipment = load_json("rules/equipment.json")
    return jsonify(equipment)

@rules_bp.route('/spells/<int:level>', methods=['GET'])
def get_spells_by_level(level):
    try:
        with open(f"rules/spells/{level}.json") as f:
            spells = json.load(f)
        return jsonify(spells)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

################################################################################
# 6) FLASK ROUTES – combining everything above
################################################################################

@rules_bp.route('/validate_character_creation', methods=['POST'])
def route_validate_character():
    """
    POST /validate_character_creation
    JSON: { ... character data ... }
    """
    data = request.json
    if not data:
        return jsonify({"error": "Missing character data"}), 400

    result = validate_character_creation(data)
    return jsonify(result)

@rules_bp.route('/resolve_skill_check', methods=['POST'])
def route_resolve_skill():
    """
    POST /resolve_skill_check
    JSON: { skill, ability_score, modifiers, dc }
    """
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
def route_resolve_combat():
    """
    POST /resolve_combat_action
    JSON: { attacker, defender, roll }
    """
    data = request.json
    attacker = data.get("attacker", {})
    defender = data.get("defender", {})
    roll = data.get("roll", 10)

    result = resolve_combat_action(attacker, defender, roll)
    return jsonify(result)

@rules_bp.route('/lookup_rule', methods=['GET'])
def route_lookup_rule():
    """
    GET /lookup_rule?category=...&name=...
    """
    category = request.args.get("category")
    name = request.args.get("name")

    if not category or not name:
        return jsonify({"error": "Missing category or name"}), 400

    result = lookup_rule(category, name)
    if not result:
        return jsonify({"error": f"{name} not found in {category}"}), 404
    return jsonify(result)

@rules_bp.route('/lookup_spell', methods=['GET'])
def route_lookup_spell():
    """
    GET /lookup_spell?level=...&name=...
    """
    level = request.args.get("level")
    name = request.args.get("name")

    if not level or not name:
        return jsonify({"error": "Missing spell level or name"}), 400

    result = lookup_spell(level, name)
    if not result:
        return jsonify({"error": f"Spell '{name}' not found at level {level}"}), 404
    return jsonify(result)

@rules_bp.route('/log_event_and_notify_npcs', methods=['POST'])
def route_log_event_and_notify_npcs():
    """
    POST /log_event_and_notify_npcs
    JSON: { region, summary, ... }
    Logs a world event, then propagates beliefs in that region.
    """
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

################################################################################
# 6a) Additional routes referencing other engines: Combat, Tension, etc.
################################################################################

@rules_bp.route('/start_combat', methods=['POST'])
def api_start_combat():
    """
    POST /start_combat
    JSON: { encounter_name, player_party, enemy_party, battle_map }
    """
    from combat_engine import start_combat

    data = request.json
    encounter_name = data.get("encounter_name", "Unnamed Encounter")
    player_party = data.get("player_party", [])
    enemy_party = data.get("enemy_party", [])
    battle_map = data.get("battle_map", {})

    if not player_party or not enemy_party:
        return jsonify({"error": "Both player_party and enemy_party are required"}), 400

    battle_id, combat_data = start_combat(
        encounter_name, player_party, enemy_party, battle_map
    )
    return jsonify({"battle_id": battle_id, "combat": combat_data})

@rules_bp.route('/combat_action', methods=['POST'])
def api_combat_action():
    """
    POST /combat_action
    JSON: { battle_id, actor_id, target_id, action, roll, etc. }
    """
    from combat_engine import apply_combat_action

    data = request.json
    battle_id = data.get("battle_id")
    actor_id = data.get("actor_id")
    target_id = data.get("target_id")
    action_type = data.get("action", "attack")
    roll = data.get("roll", 10)
    value = data.get("value", 0)
    notes = data.get("notes", "")
    status_effect = data.get("status_effect")
    spell_name = data.get("spell_name")
    spell_level = data.get("spell_level")

    if not all([battle_id, actor_id, target_id]):
        return jsonify({"error": "Missing required fields."}), 400

    result, status = apply_combat_action(
        battle_id, actor_id, target_id, action_type, roll, value,
        notes, status_effect, spell_name, spell_level
    )
    return jsonify(result), status

@rules_bp.route('/long_rest/<character_id>', methods=['POST'])
def route_long_rest(character_id):
    """
    POST /long_rest/<character_id>
    Resets the player's spell slots to unused (partial update).
    """
    ref = db.reference(f"/players/{character_id}")
    data = ref.get()

    if not data or "spell_slots" not in data:
        return jsonify({"error": "Character not found or has no spell slots"}), 404

    # Reset all used slots to 0
    for level_info in data["spell_slots"].values():
        level_info["used"] = 0

    ref.update({"spell_slots": data["spell_slots"]})
    return jsonify({
        "message": f"{data.get('character_name', 'Character')} has completed a long rest.",
        "spell_slots": data["spell_slots"]
    })

@rules_bp.route('/request_rest', methods=['POST'])
def route_request_rest():
    """
    POST /request_rest
    Uses GPT to decide if the player can safely rest, potentially restoring spell slots.
    """
    data = request.json
    character_id = data.get("character_id")
    location_description = data.get("location_description", "")
    current_threats = data.get("threats", [])
    narrative_context = data.get("narrative_context", "")

    if not character_id:
        return jsonify({"error": "Missing character_id"}), 400

    prompt = (
        f"The player is attempting to take a long rest.\n"
        f"Location: {location_description}\n"
        f"Threats nearby: {', '.join(current_threats) if current_threats else 'None'}\n"
        f"Context: {narrative_context}\n"
        f"Reply in JSON with: {{\"decision\": \"yes/no\", \"narration\": \"...\"}}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fantasy RPG narrator deciding if a rest is safe."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=150
        )
        content = response.choices[0].message.content.strip()
        try:
            parsed = json.loads(content)
            decision = parsed.get("decision", "").lower()
            narration = parsed.get("narration", "No narration provided.")
        except:
            # Fallback if JSON parse fails
            decision = "no"
            narration = "You try to rest, but the forest feels uneasy..."

        if "yes" in decision:
            # Grant rest
            ref = db.reference(f"/players/{character_id}")
            char_data = ref.get()

            if not char_data or "spell_slots" not in char_data:
                return jsonify({"error": "Character not found or has no spell slots"}), 404

            for level_info in char_data["spell_slots"].values():
                level_info["used"] = 0
            ref.update({"spell_slots": char_data["spell_slots"]})

            return jsonify({
                "result": "Long rest granted.",
                "narration": narration,
                "spell_slots": char_data["spell_slots"]
            })

        return jsonify({
            "result": "Rest denied",
            "narration": narration
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rules_bp.route('/recruit_npc', methods=['POST'])
def route_recruit_npc():
    from party_engine import create_party, add_to_party

    data = request.json
    character_id = data.get("character_id")
    npc_id = data.get("npc_id")

    player_ref = db.reference(f"/players/{character_id}")
    npc_ref = db.reference(f"/npcs/{npc_id}")

    player_data = player_ref.get()
    npc_data = npc_ref.get()

    if not player_data or not npc_data:
        return jsonify({"error": "Invalid player or NPC ID"}), 400

    existing_party = player_data.get("party_id")
    if existing_party:
        _ = add_to_party(existing_party, npc_id)
    else:
        existing_party = create_party(character_id, [npc_id])

    return jsonify({
        "message": f"{npc_data['character_name']} has joined your party!",
        "party_id": existing_party
    })

@rules_bp.route('/npc_loyalty_tick', methods=['POST'])
def route_npc_loyalty_tick():
    from loyalty_engine import loyalty_tick

    data = request.json
    npc_id = data.get("npc_id")
    character_id = data.get("character_id")
    cha_score = data.get("cha", 10)

    if not npc_id or not character_id:
        return jsonify({"error": "Missing npc_id or character_id"}), 400

    result = loyalty_tick(npc_id, character_id, cha_score=cha_score)
    return jsonify(result)

################################################################################
# Tension routes
################################################################################

@rules_bp.route('/tension/<region_id>', methods=['GET'])
def route_get_tension(region_id):
    """
    GET /tension/<region_id>
    Returns tension data for a given region.
    """
    data = get_tension(region_id)
    return jsonify(data)

@rules_bp.route('/tension/modify', methods=['POST'])
def route_modify_tension():
    """
    POST /tension/modify
    JSON: { region_id, source, amount }
    """
    payload = request.json or {}
    region_id = payload.get("region_id")
    source = payload.get("source")
    amount = payload.get("amount", 0)

    if not region_id or not source:
        return jsonify({"error": "Missing region_id or source"}), 400

    result = modify_tension(region_id, source, amount)
    return jsonify(result)

@rules_bp.route('/tension/reset/<region_id>', methods=['POST'])
def route_reset_tension(region_id):
    """
    POST /tension/reset/<region_id>
    Resets tension in a region to baseline.
    """
    data = reset_tension(region_id)
    return jsonify(data)

@rules_bp.route('/tension/decay/<region_id>', methods=['POST'])
def route_decay_tension(region_id):
    """
    POST /tension/decay/<region_id>
    JSON body can optionally include {"decay_rate": <int>}
    """
    payload = request.json or {}
    decay_rate = payload.get("decay_rate", 1)

    data = decay_tension(region_id, decay_rate)
    return jsonify(data)

################################################################################
# Mobility, Rumor, Motif, Relationship, etc. routes
################################################################################

@rules_bp.route('/npc/travel/<npc_id>', methods=['POST'])
def route_npc_travel(npc_id):
    """
    POST /npc/travel/<npc_id>
    Updates an NPC's location via mobility_engine.
    """
    from mobility_engine import update_npc_location
    return jsonify(update_npc_location(npc_id))

@rules_bp.route('/propagate_beliefs/<region_id>', methods=['POST'])
def route_rumor_propagation(region_id):
    """
    POST /propagate_beliefs/<region_id>
    Invokes the inlined propagate_beliefs function.
    """
    result = propagate_beliefs(region_id)
    return jsonify({"messages": result, "region": region_id})

@rules_bp.route('/npc_motif_tick/<npc_id>', methods=['POST'])
def route_tick_motifs(npc_id):
    """
    POST /npc_motif_tick/<npc_id>
    Ticks NPC motifs from motif_engine.
    """
    from motif_engine import tick_npc_motifs
    return jsonify(tick_npc_motifs(npc_id))

@rules_bp.route('/npc_relationship_tick', methods=['POST'])
def route_npc_relationship_tick():
    """
    POST /npc_relationship_tick
    Calls relationship_engine.daily_relationship_tick to advance NPC relationships daily.
    """
    from relationship_engine import daily_relationship_tick
    daily_relationship_tick()
    return jsonify({"status": "NPC relationships updated"})

@rules_bp.route('/apply_status_effect', methods=['POST'])
def route_apply_status_effect():
    """
    POST /apply_status_effect
    Applies a status effect from combat_utilities.
    """
    from combat_utilities import apply_status_effect
    data = request.json
    result = apply_status_effect(**data)
    return jsonify(result)

@rules_bp.route('/run_command_parser', methods=['POST'])
def route_run_command_parser():
    """
    POST /run_command_parser
    Invokes command_parser.parse_action_command to interpret user text commands.
    """
    from command_parser import parse_action_command
    data = request.json
    text = data.get("text", "")
    context = data.get("context", {})
    result = parse_action_command(text, context)
    return jsonify(result)

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
################################################################################
# END OF CONSOLIDATION
################################################################################
