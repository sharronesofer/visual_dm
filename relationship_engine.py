"""
relationship_engine.py
Handles NPC relationship fields, trust/respect/envy, daily ticks, loyalty events, etc.
"""

import random
import logging
import math
import json
from datetime import datetime
from flask import Blueprint, jsonify
from firebase_admin import db
from typing import Optional, Dict, Any

try:
    import openai
    from openai import ChatCompletion
except ImportError:
    pass

try:
    from gpt_endpoints import log_gpt_usage
except ImportError:
    def log_gpt_usage(*args, **kwargs): pass

releng_bp = Blueprint("releng", __name__)
__all__ = ["releng_bp"]

################################################################################
# Constants, Metadata, and Required Fields
################################################################################

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

REQUIRED_FIELDS = [
    "character_name", "characterType", "level", "class", "race", "gender", "alignment", "region_of_origin", "background",
    "HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", "XP", "feats", "skills", "proficiencies", "features", "spells",
    "equipment", "inventory", "notable_possessions", "known_languages", "faction_affiliations", "reputation",
    "personality_traits", "notable_relationships", "hidden_ambition", "hidden_compassion", "hidden_discipline",
    "hidden_impulsivity", "hidden_integrity", "hidden_pragmatism", "hidden_resilience",
    "private_goal_short_term", "private_goal_mid_term", "private_goal_long_term",
    "opinion_of_pc", "opinion_of_party", "narrative_motif_pool", "status_effects", "cooldowns", "gold"
]

# Load land type metadata (if needed by your code)
try:
    with open("rules/land_types.json", "r") as f:
        land_type_meta = json.load(f)
except Exception as e:
    land_type_meta = {}
    print(f"Warning: Could not load land_types.json. {e}")

################################################################################
# Validation and Utility
################################################################################

def validate_npc(npc):
    """
    Ensures the NPC dict has all required fields from REQUIRED_FIELDS.
    Fills in None if missing.
    """
    for field in REQUIRED_FIELDS:
        if field not in npc:
            npc[field] = None
    return npc

################################################################################
# NPC Mobility / Movement
################################################################################

def update_npc_location(npc_id):
    """
    Updates an NPC's location based on their 'mobility' dict in Firebase.
    Has a random 'travel_chance' to move to a different POI within 'radius'.
    """
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()
    if not npc:
        return {"error": f"NPC {npc_id} not found."}

    mobility = npc.get("mobility", {})
    home = mobility.get("home_poi")
    current = mobility.get("current_poi", home)
    radius = mobility.get("radius", 1)
    travel_chance = mobility.get("travel_chance", 0.15)

    # Decide if the NPC actually travels this tick
    if random.random() > travel_chance:
        return {"npc_id": npc_id, "stayed": True}

    # Find all POIs in range
    all_pois = db.reference("/locations").get() or {}
    valid_pois = []

    try:
        cx, cy = map(int, current.split("_"))
    except Exception:
        return {"error": f"Invalid current_poi for {npc_id}: {current}"}

    for key, poi_data in all_pois.items():
        if not poi_data.get("POI"):
            continue
        try:
            x, y = map(int, key.split("_"))
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if 0 < dist <= radius:
                valid_pois.append(key)
        except:
            continue

    if not valid_pois:
        return {"npc_id": npc_id, "stayed": True, "reason": "No valid POIs in range"}

    new_location = random.choice(valid_pois)
    npc["mobility"]["current_poi"] = new_location
    npc["mobility"]["last_moved"] = datetime.utcnow().isoformat()
    npc_ref.set(npc)

    return {"npc_id": npc_id, "moved_to": new_location}

################################################################################
# NPC Loyalty / Goodwill
################################################################################

def loyalty_tick(npc_id, character_id, context_tags=None, cha_score=10):
    """
    Increases goodwill by a small amount if NPC's loyalty is positive.
    Maximum goodwill is 10. 
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{character_id}")
    rel_data = rel_ref.get() or {}

    loyalty = rel_data.get("loyalty", 0)
    goodwill = rel_data.get("goodwill", 5)
    tags = rel_data.get("tags", [])

    # Decide how much goodwill regenerates
    if loyalty >= 10:
        regen = 3
    elif loyalty > 0:
        regen = 1
    else:
        regen = 0

    goodwill = min(10, goodwill + regen)
    rel_data["goodwill"] = goodwill
    rel_ref.set(rel_data)

    return {
        "npc_id": npc_id,
        "character_id": character_id,
        "loyalty": loyalty,
        "goodwill": goodwill,
        "tags": tags,
        "regen_applied": regen
    }

def apply_loyalty_event(npc_id, character_id, alignment_score):
    """
    Adjusts loyalty and goodwill for an NPC->player relationship
    based on a positive or negative alignment score. 
    Accounts for tags like 'loyalist', 'coward', 'bestie', 'nemesis'.
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{character_id}")
    rel_data = rel_ref.get() or {}

    loyalty = rel_data.get("loyalty", 0)
    goodwill = rel_data.get("goodwill", 5)
    tags = rel_data.get("tags", [])

    gain_mod = 1.0
    loss_mod = 1.0

    # Tag-based modifications
    if "loyalist" in tags:
        gain_mod, loss_mod = 1.5, 0.5
    elif "coward" in tags:
        gain_mod, loss_mod = 0.5, 1.5
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

    # Clamp values
    loyalty = max(-10, min(10, loyalty))
    goodwill = max(0, min(10, goodwill))

    rel_data["loyalty"] = loyalty
    rel_data["goodwill"] = goodwill
    rel_ref.set(rel_data)

    return rel_data

def betrayal_check(npc_id, character_id, cha_score):
    """
    If loyalty <= 0 and goodwill == 0, chance of betrayal.
    Rolls 1d20 + CHA mod vs DC = 10 + abs(loyalty).
    """
    rel_ref = db.reference(f"/npcs/{npc_id}/relationships/{character_id}")
    rel_data = rel_ref.get() or {}

    loyalty = rel_data.get("loyalty", 0)
    goodwill = rel_data.get("goodwill", 0)

    # If either is positive, no betrayal chance
    if goodwill > 0 or loyalty > 0:
        return {"status": "stable", "message": "No betrayal risk."}

    dc = 10 + abs(loyalty)
    roll = random.randint(1, 20) + ((cha_score - 10) // 2)
    outcome = "betrays" if roll < dc else "stays"

    return {
        "npc_id": npc_id,
        "character_id": character_id,
        "dc": dc,
        "roll": roll,
        "cha_score": cha_score,
        "outcome": outcome
    }

################################################################################
# World Updating Functions
################################################################################

def update_world_state():
    """
    Called periodically to update NPCs' movement or behaviors.
    """
    all_npcs = db.reference("/npcs").get() or {}
    for npc_id in all_npcs.keys():
        update_npc_location(npc_id)
    # Add more global updates if desired

def daily_world_tick():
    """
    Called once per day (or game day) to run world-level logic.
    """
    update_world_state()
    # Possibly more daily logic like region events or resource resets

################################################################################
# NPC Emotional State & Motifs
################################################################################

def tick_npc_motifs(npc_id):
    """
    Ticks an NPC's emotional flags and motif entropy.
    Possibly adds new emotions at random.
    """
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()
    if not npc_data:
        return {"error": f"NPC {npc_id} not found"}

    updated = False

    # Motif entropy
    entropy = npc_data.get("motif_entropy", {})
    for motif in npc_data.get("core_motifs", []):
        entropy[motif] = min(entropy.get(motif, 0) + 1, 5)
    npc_data["motif_entropy"] = entropy
    updated = True

    # Emotional flags countdown
    emotional_flags = npc_data.get("emotional_flags", [])
    new_flags = []
    for flag in emotional_flags:
        flag["duration"] -= 1
        if flag["duration"] > 0:
            new_flags.append(flag)
    npc_data["emotional_flags"] = new_flags

    # Chance to add a new emotion if under 3 flags
    if len(new_flags) < 3 and random.random() < 0.2:
        emotion = random.choice(EMOTION_POOL)
        intensity = random.randint(1, 5)
        duration = max(1, 6 - intensity)
        new_flags.append({
            "emotion": emotion,
            "intensity": intensity,
            "duration": duration
        })
        npc_data["emotional_flags"] = new_flags

    updated = True
    if updated:
        npc_data["last_motif_tick"] = datetime.utcnow().isoformat()
        npc_ref.set(npc_data)

    return {
        "npc_id": npc_id,
        "motif_entropy": npc_data["motif_entropy"],
        "emotional_flags": npc_data["emotional_flags"]
    }

def get_npc_motif_prompt(npc_id):
    """
    Create a short summary of the NPC's emotional state and active motifs
    to feed into GPT or other logic.
    """
    npc_data = db.reference(f"/npcs/{npc_id}").get()
    if not npc_data:
        return ""

    flags = npc_data.get("emotional_flags", [])
    phrases = []
    for f in flags:
        label = f"{f['emotion']} (intensity {f['intensity']})"
        phrases.append(label)

    core_motifs = npc_data.get("core_motifs", [])
    entropy = npc_data.get("motif_entropy", {})
    active_motifs = [m for m in core_motifs if entropy.get(m, 0) >= 3]

    result = []
    if phrases:
        result.append("Emotional State: " + ", ".join(phrases))
    if active_motifs:
        result.append("Active Motivations: " + ", ".join(active_motifs))

    return " | ".join(result)

################################################################################
# Flask Routes referencing these functions
################################################################################

@releng_bp.route('/npc/travel/<npc_id>', methods=['POST'])
def route_npc_travel(npc_id):
    """
    POST /npc/travel/<npc_id>
    Calls update_npc_location to possibly move an NPC to a nearby POI.
    """
    result = update_npc_location(npc_id)
    return jsonify(result)

@releng_bp.route('/npc_motif_tick/<npc_id>', methods=['POST'])
def route_tick_motifs(npc_id):
    """
    POST /npc_motif_tick/<npc_id>
    Ticks NPC emotional flags and motif entropy.
    """
    result = tick_npc_motifs(npc_id)
    return jsonify(result)

RELATIONSHIP_MODIFIERS = {
    "trust": 2,
    "respect": 1.5,
    "envy": 1.2,
    "shared_history": 0.8
}

def update_relationships(npc_id: str, other_npc_id: str) -> Dict[str, Any]:
    """
    Updates relationship fields (trust, respect, envy) between npc_id and other_npc_id
    based on shared history or events in the 'shared_history' list.
    """
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()
    other_npc_data = db.reference(f"/npcs/{other_npc_id}").get()

    if not npc_data or not other_npc_data:
        return {"error": "NPCs not found"}

    relationships = npc_data.setdefault("relationships", {})
    rel_record = relationships.setdefault(other_npc_id, {
        "trust": 0,
        "respect": 0,
        "envy": 0,
        "shared_history": []
    })

    curr_trust = rel_record.get("trust", 0)
    curr_respect = rel_record.get("respect", 0)
    curr_envy = rel_record.get("envy", 0)
    shared_history = rel_record.get("shared_history", [])

    # Basic influence calculation from events
    influence_factor = 0
    if "helped_in_battle" in shared_history:
        influence_factor += 2
    if "betrayed_in_combat" in shared_history:
        influence_factor -= 3

    # Apply numeric changes
    new_trust = curr_trust + influence_factor * RELATIONSHIP_MODIFIERS["trust"]
    new_respect = curr_respect + influence_factor * RELATIONSHIP_MODIFIERS["respect"]
    new_envy = curr_envy - influence_factor * RELATIONSHIP_MODIFIERS["envy"]

    # Clamp values between -10 and 10
    new_trust = float(max(-10, min(10, new_trust)))
    new_respect = float(max(-10, min(10, new_respect)))
    new_envy = float(max(-10, min(10, new_envy)))

    rel_record.update({
        "trust": new_trust,
        "respect": new_respect,
        "envy": new_envy,
        "last_updated": datetime.utcnow().isoformat()
    })

    # Perform a partial update so we don’t overwrite other fields in npc_data
    npc_ref.update({"relationships": relationships})

    return {
        "npc_id": npc_id,
        "target_npc_id": other_npc_id,
        "updated_relationship": rel_record
    }

def daily_relationship_tick() -> None:
    """
    Called once per day to iterate over all NPCs, applying update_relationships
    to each pair for which a relationship already exists.
    """
    all_npcs = db.reference("/npcs").get() or {}
    for npc_id, npc_data in all_npcs.items():
        rel_dict = npc_data.get("relationships", {})
        for target_id in rel_dict.keys():
            if target_id != npc_id:
                update_relationships(npc_id, target_id)

@releng_bp.route('/daily_world_tick', methods=['POST'])
def route_daily_world_tick():
    """
    POST /daily_world_tick
    Triggers a daily cycle that updates NPC movement and other world logic.
    """
    daily_world_tick()
    return jsonify({"status": "Daily world tick completed"})

@releng_bp.route('/get_npc_motif_prompt/<npc_id>', methods=['GET'])
def route_get_npc_motif_prompt(npc_id):
    """
    GET /get_npc_motif_prompt/<npc_id>
    Returns a short text summary of the NPC's emotional state and active motifs.
    """
    prompt = get_npc_motif_prompt(npc_id)
    return jsonify({"npc_id": npc_id, "motif_prompt": prompt})

################################################################################
# (Any other routes you want in this file would go below, if needed)
################################################################################
