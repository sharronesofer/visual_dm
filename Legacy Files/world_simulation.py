import random
import math
from datetime import datetime
from firebase_admin import db
import openai
import uuid
import json
from gpt_endpoints import log_gpt_usage
from character_utils import complete_character

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

# Load land type metadata
with open("rules/land_types.json", "r") as f:
    land_type_meta = json.load(f)

# NPC required fields for validation
REQUIRED_FIELDS = [
    "character_name", "characterType", "level", "class", "race", "gender", "alignment", "region_of_origin", "background",
    "HP", "AC", "STR", "DEX", "CON", "INT", "WIS", "CHA", "XP", "feats", "skills", "proficiencies", "features", "spells",
    "equipment", "inventory", "notable_possessions", "known_languages", "faction_affiliations", "reputation", "personality_traits", 
    "notable_relationships", "hidden_ambition", "hidden_compassion", "hidden_discipline", "hidden_impulsivity", "hidden_integrity", 
    "hidden_pragmatism", "hidden_resilience", "private_goal_short_term", "private_goal_mid_term", "private_goal_long_term",
    "opinion_of_pc", "opinion_of_party", "narrative_motif_pool", "status_effects", "cooldowns", "gold"
]

# Validate NPC data
def validate_npc(npc):
    for field in REQUIRED_FIELDS:
        if field not in npc:
            npc[field] = None
    return npc

# --- NPC Behavior Simulation ---

def update_npc_location(npc_id):
    """
    Updates an NPC's location based on their mobility and the surrounding POIs.
    If the NPC moves, their location is updated in the database.
    """
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

def loyalty_tick(npc_id, player_id, context_tags=None, cha_score=10):
    """
    Adjusts NPC goodwill based on loyalty after a combat or major event.
    Handles potential betrayal if goodwill reaches 0 and loyalty is too low.
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
    Adjusts NPC loyalty and goodwill based on an action's alignment score.
    Applies loyalty tag modifiers and computes new values for loyalty and goodwill.
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
    Runs when goodwill reaches zero and loyalty is low.
    Checks if betrayal occurs using a CHA roll against a DC based on loyalty.
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

# --- World Management ---

def update_world_state():
    """
    Global function to update world state, including NPC behaviors, region events, etc.
    Should be called periodically (e.g., every hour or daily).
    """
    # Iterate over NPCs and handle behaviors
    all_npcs = db.reference("/npcs").get() or {}
    for npc_id in all_npcs:
        # Update NPC's location and behavior
        update_npc_location(npc_id)

    # Further global updates (e.g., global events, POI regeneration) could be added here

def daily_world_tick():
    """
    Runs a daily world tick, updating all NPCs' behaviors and handling world events.
    """
    update_world_state()  # Update NPC behaviors, locations, etc.
    # Add more world simulation logic (e.g., regional events, world state checks)

# --- NPC Emotional State & Motifs ---
def tick_npc_motifs(npc_id):
    """
    Ticks NPC's motifs, emotions, and entropy, updating their emotional state.
    """
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
    """
    Generate a prompt based on NPC's current emotional state and active motivations.
    """
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
