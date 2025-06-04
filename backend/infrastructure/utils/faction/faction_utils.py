#This module manages the relationship between NPC traits and faction alignment, including:
#Calculating affinity scores
#Assigning loyalty levels
#Initializing faction opinions
#It's central to faction dynamics, and integrates fully with npc, faction, and firebase systems.

from datetime import datetime
# from firebase_admin import db  # TODO: Replace with proper database integration
import random

# --- Hidden Attributes Generation ---

def generate_faction_hidden_attributes():
    """
    Generate random hidden personality attributes for a faction.
    Returns a dictionary with the same 6 attributes that NPCs have.
    
    Returns:
        dict: Dictionary containing the 6 hidden attributes with values 1-10
    """
    return {
        "hidden_ambition": random.randint(1, 10),
        "hidden_integrity": random.randint(1, 10),
        "hidden_discipline": random.randint(1, 10),
        "hidden_impulsivity": random.randint(1, 10),
        "hidden_pragmatism": random.randint(1, 10),
        "hidden_resilience": random.randint(1, 10)
    }

def validate_hidden_attributes(attributes: dict) -> dict:
    """
    Validate and clamp hidden attributes to ensure they're within valid range (1-10).
    
    Args:
        attributes (dict): Dictionary of hidden attributes
        
    Returns:
        dict: Validated and clamped attributes
    """
    valid_attributes = {}
    attribute_names = [
        "hidden_ambition", "hidden_integrity", "hidden_discipline",
        "hidden_impulsivity", "hidden_pragmatism", "hidden_resilience"
    ]
    
    for attr_name in attribute_names:
        value = attributes.get(attr_name, 5)  # Default to neutral value
        # Handle None values by defaulting to 5
        if value is None:
            value = 5
        # Clamp value between 1 and 10
        valid_attributes[attr_name] = max(1, min(10, int(value)))
    
    return valid_attributes

def calculate_faction_behavior_modifiers(hidden_attributes: dict) -> dict:
    """
    Calculate behavior modifiers based on hidden attributes.
    These can be used to influence faction decision-making.
    
    Args:
        hidden_attributes (dict): Faction's hidden attributes
        
    Returns:
        dict: Behavior modifiers for various faction actions
    """
    # Get attribute values with defaults
    ambition = hidden_attributes.get("hidden_ambition", 5)
    integrity = hidden_attributes.get("hidden_integrity", 5) 
    discipline = hidden_attributes.get("hidden_discipline", 5)
    impulsivity = hidden_attributes.get("hidden_impulsivity", 5)
    pragmatism = hidden_attributes.get("hidden_pragmatism", 5)
    resilience = hidden_attributes.get("hidden_resilience", 5)
    
    # Calculate behavior modifiers using formulas from behavior_config.json
    modifiers = {
        # Core behavior modifiers from config
        "expansion_tendency": (ambition * 0.4) + (discipline * 0.3) - (integrity * 0.2) + (pragmatism * 0.1),
        "alliance_reliability": (integrity * 0.5) + (discipline * 0.3) + (resilience * 0.2),
        "betrayal_likelihood": (ambition * 0.3) + (impulsivity * 0.3) + (pragmatism * 0.2) - (integrity * 0.4),
        "diplomatic_flexibility": (pragmatism * 0.4) + (discipline * 0.3) - (integrity * 0.2) + (ambition * 0.1),
        "crisis_management": (discipline * 0.4) + (resilience * 0.3) + (pragmatism * 0.2) - (impulsivity * 0.1),
        "military_aggression": (ambition * 0.4) + (impulsivity * 0.3) - (integrity * 0.2) + (resilience * 0.1),
        "economic_cooperation": (pragmatism * 0.4) + (integrity * 0.3) + (discipline * 0.2) - (ambition * 0.1),
        "succession_stability": (discipline * 0.4) + (integrity * 0.3) + (resilience * 0.2) - (ambition * 0.1),
        
        # Additional derived modifiers for comprehensive behavior analysis
        "territorial_aggression": (ambition + impulsivity) / 10.0,
        "trade_aggression": (ambition + pragmatism) / 10.0,
        "treaty_reliability": (integrity + discipline) / 10.0,
        "alliance_stability": (integrity + resilience) / 10.0,
        "diplomatic_trustworthiness": (integrity + (10 - impulsivity)) / 10.0,
        "strategic_planning": (discipline + (10 - impulsivity)) / 10.0,
        "military_organization": (discipline + ambition) / 10.0,
        "economic_efficiency": (discipline + pragmatism) / 10.0,
        "crisis_reaction_speed": (impulsivity + (10 - discipline)) / 10.0,
        "opportunism": (pragmatism + impulsivity) / 10.0,
        "rash_decision_making": (impulsivity + (10 - integrity)) / 10.0,
        "compromise_willingness": (pragmatism + (10 - integrity)) / 10.0,
        "principle_flexibility": (pragmatism + (10 - discipline)) / 10.0,
        "realpolitik_tendency": (pragmatism + (10 - integrity)) / 10.0,
        "recovery_speed": (resilience + pragmatism) / 10.0,
        "crisis_handling": (resilience + discipline) / 10.0,
        "stability_under_pressure": (resilience + (10 - impulsivity)) / 10.0
    }
    
    # Normalize all values to 0.0-1.0 range for consistency
    normalized_modifiers = {}
    for key, value in modifiers.items():
        # Clamp values to reasonable range and normalize
        clamped_value = max(-10.0, min(10.0, value))
        normalized_value = (clamped_value + 10.0) / 20.0  # Convert -10 to 10 range to 0.0 to 1.0
        normalized_modifiers[key] = round(normalized_value, 3)
    
    return normalized_modifiers

# --- Affinity Calculation ---

def calculate_affinity(npc_data, faction_data):
    """
    Compares NPC traits against faction traits and returns a score (0–60).
    Used to determine how aligned the NPC is with the faction's ideals.

    Traits are assumed to be numerical vectors or shared tags.
    """
    npc_traits = npc_data.get("personality_traits", {})
    faction_traits = faction_data.get("hidden_attributes", {})

    score = 0
    max_score = 60  # Full alignment on all 6 scaled traits (6 * 10 = 60)

    # Trait vector comparison — assume 6 common traits for simplicity
    for trait in ["valor", "order", "ambition", "community", "freedom", "discipline"]:
        npc_val = npc_traits.get(trait, 5)         # default neutral value
        faction_val = faction_traits.get(trait, 5)  # default neutral value
        diff = abs(npc_val - faction_val)
        score += (10 - diff)  # closer = higher score

    return score  # Max is 6 traits * max alignment = 60

# --- Assign Affiliations at Creation ---

def assign_faction_affiliations_to_npc(npc_id: str, npc_traits: dict):
    """
    Compare NPC traits to all existing factions and assign affiliations with loyalty based on affinity.
    """
    all_factions = db.reference("/factions").get() or {}
    affiliations = []

    for fid, faction in all_factions.items():
        faction_traits = faction.get("hidden_attributes", {})
        affinity = calculate_affinity(npc_traits, faction_traits)

        if affinity >= 50:  # ~83% alignment (was 32/36, now 50/60)
            loyalty = 3
        elif affinity >= 42:  # ~70% alignment (was 28/36, now 42/60)
            loyalty = 2
        elif affinity >= 36:  # ~60% alignment (was 24/36, now 36/60)
            loyalty = 1
        elif affinity <= 24:  # ~40% alignment (was 18/36, now 24/60)
            loyalty = -1
        else:
            continue  # Skip neutral alignment

        affiliations.append({"id": fid, "loyalty": loyalty})

    db.reference(f"/npcs/{npc_id}/faction_affiliations").set(affiliations)
    return affiliations

# --- Opinion Initialization (Optional) ---

def initialize_faction_opinions(npc_id: str, npc_traits: dict):
    """
    Set up faction opinion values for an NPC even if not affiliated.
    """
    all_factions = db.reference("/factions").get() or {}
    opinion_ref = db.reference(f"/npcs/{npc_id}/faction_opinions")

    for fid, faction in all_factions.items():
        faction_traits = faction.get("hidden_attributes", {})
        affinity = calculate_affinity(npc_traits, faction_traits)

        if affinity >= 50:  # ~83% alignment
            score = 3
        elif affinity >= 42:  # ~70% alignment
            score = 2
        elif affinity >= 36:  # ~60% alignment
            score = 1
        elif affinity <= 24:  # ~40% alignment
            score = -2
        else:
            score = 0

        opinion_ref.child(fid).set(score)

def register_faction_conflict(faction_a_id, faction_b_id, region_id=None, reason="unspecified"):
    """
    Registers the start of a conflict between two factions.
    Can be upgraded later to handle war escalation, peace negotiation, etc.
    """
    conflict_id = f"conflict_{faction_a_id}_{faction_b_id}_{int(datetime.utcnow().timestamp())}"
    conflict_data = {
        "faction_a": faction_a_id,
        "faction_b": faction_b_id,
        "region_id": region_id,
        "reason": reason,
        "start_time": datetime.utcnow().isoformat(),
        "status": "hostile",  # could become: neutral, war, cold_war, alliance, etc.
        "skirmishes": [],
        "peace_offers": [],
        "battle_log": []
    }

    db.reference(f"/faction_conflicts/{conflict_id}").set(conflict_data)

    # Optional: update each faction's known enemies
    for fid in [faction_a_id, faction_b_id]:
        ref = db.reference(f"/factions/{fid}/active_conflicts")
        existing = ref.get() or []
        existing.append(conflict_id)
        ref.set(existing)

    return conflict_id

def escalate_conflict_to_war(conflict_id):
    """
    Placeholder for future war logic.
    """
    ref = db.reference(f"/faction_conflicts/{conflict_id}")
    conflict = ref.get()
    if not conflict:
        return None

    conflict["status"] = "war"
    conflict["war_start_time"] = datetime.utcnow().isoformat()
    ref.set(conflict)
    return conflict

def create_faction(faction_data):
    """
    Create a new faction entry with metadata and propagate to relevant systems.
    """
    fid = faction_data.get("id")
    if not fid:
        raise ValueError("Faction must include an 'id'")

    now = datetime.utcnow().isoformat()
    faction_data["created"] = now
    faction_data.setdefault("poi_outposts", [])
    faction_data.setdefault("motif_seed", random.randint(1, 50))
    
    # Generate hidden attributes if not provided
    if "hidden_attributes" not in faction_data:
        faction_data["hidden_attributes"] = generate_faction_hidden_attributes()
    else:
        # Validate and clamp existing hidden attributes
        faction_data["hidden_attributes"] = validate_hidden_attributes(faction_data["hidden_attributes"])

    # Save faction data
    db.reference(f"/factions/{fid}").set(faction_data)

    # Log globally
    log_entry = {
        "faction": fid,
        "name": faction_data.get("name"),
        "created": now,
        "motif_seed": faction_data["motif_seed"],
        "outposts": faction_data["poi_outposts"],
        "hidden_attributes": faction_data["hidden_attributes"]
    }
    global_log = db.reference("/faction_log").get() or []
    global_log.append(log_entry)
    db.reference("/faction_log").set(global_log)

    # Log to POIs
    for poi_id in faction_data["poi_outposts"]:
        for region, pois in (db.reference("/poi_state").get() or {}).items():
            if poi_id not in pois:
                continue
            ref = db.reference(f"/poi_state/{region}/{poi_id}/evolution_state/event_log")
            current = ref.get() or []
            current.append({
                "type": "faction_created",
                "faction": fid,
                "timestamp": now
            })
            ref.set(current)

    # Optional: assign seed NPCs
    npc_pool = db.reference("/npc_core").get() or {}
    assigned = 0
    for npc_id, npc in npc_pool.items():
        if assigned >= 3:
            break
        if random.random() < 0.1:  # 10% chance of loyalty
            affiliations = npc.get("faction_affiliations", [])
            if fid not in affiliations:
                affiliations.append(fid)
                db.reference(f"/npc_core/{npc_id}/faction_affiliations").set(affiliations)
                assigned += 1

    return {
        "message": f"Faction '{fid}' created and logged.", 
        "npc_loyalists": assigned,
        "hidden_attributes": faction_data["hidden_attributes"]
    }

def adjust_faction_opinion(faction_id, character_id, delta):
    """
    Adjusts a faction's opinion score of a PC or NPC.
    """
    path = f"/factions/{faction_id}/character_opinions/{character_id}"
    ref = db.reference(path)
    current = ref.get() or {"score": 0}

    current["score"] += delta
    current["last_updated"] = datetime.utcnow().isoformat()

    ref.set(current)
    return current

def assign_faction_to_poi(region_id: str, poi_id: str, faction_id: str, control_level=10):
    """
    Assigns a faction to a POI by setting its influence and logging the control change.

    Args:
        region_id (str): Region the POI belongs to
        poi_id (str): POI being assigned
        faction_id (str): Faction gaining influence or control
        control_level (int): Influence level (default 10 = full control)
    """
    timestamp = datetime.utcnow().isoformat()

    # Set faction influence
    db.reference(f"/poi_state/{region_id}/{poi_id}/faction_influence/{faction_id}").set(control_level)

    # Mark as controlled
    db.reference(f"/poi_state/{region_id}/{poi_id}/control_status").set("controlled")

    # Log the event
    event = {
        "type": "faction_claimed_poi",
        "faction": faction_id,
        "timestamp": timestamp
    }
    ref = db.reference(f"/poi_state/{region_id}/{poi_id}/event_log")
    current_log = ref.get() or []
    current_log.append(event)
    ref.set(current_log)

    return {"message": f"{faction_id} assigned to POI {poi_id} in region {region_id}."}

def calculate_faction_compatibility(attrs_a: dict, attrs_b: dict) -> float:
    """
    Calculate compatibility score between two factions based on hidden attributes
    
    Args:
        attrs_a: Hidden attributes of faction A
        attrs_b: Hidden attributes of faction B
        
    Returns:
        Compatibility score between 0.0 and 1.0
    """
    # Normalize attributes to 0-1 scale
    norm_a = {k: v/10.0 for k, v in attrs_a.items()}
    norm_b = {k: v/10.0 for k, v in attrs_b.items()}
    
    # Calculate compatibility for key traits
    integrity_compat = 1.0 - abs(norm_a.get('hidden_integrity', 0.5) - norm_b.get('hidden_integrity', 0.5))
    pragmatism_compat = 1.0 - abs(norm_a.get('hidden_pragmatism', 0.5) - norm_b.get('hidden_pragmatism', 0.5))
    discipline_compat = 1.0 - abs(norm_a.get('hidden_discipline', 0.5) - norm_b.get('hidden_discipline', 0.5))
    
    # Ambition can be complementary (one high, one low works)
    ambition_diff = abs(norm_a.get('hidden_ambition', 0.5) - norm_b.get('hidden_ambition', 0.5))
    ambition_compat = 0.8 if ambition_diff > 0.3 else 1.0 - ambition_diff
    
    # Weight the compatibility scores
    overall_compatibility = (
        integrity_compat * 0.35 +
        pragmatism_compat * 0.25 +
        discipline_compat * 0.25 +
        ambition_compat * 0.15
    )
    
    return max(0.0, min(1.0, overall_compatibility))
