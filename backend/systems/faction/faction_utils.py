
#This module manages the relationship between NPC traits and faction alignment, including:
#Calculating affinity scores
#Assigning loyalty levels
#Initializing faction opinions
#It’s central to faction dynamics, and integrates fully with npc, faction, and firebase systems.

from datetime import datetime
from firebase_admin import db
import random

# --- Affinity Calculation ---

def calculate_affinity(npc_data, faction_data):
    """
    Compares NPC traits against faction traits and returns a score (0–36).
    Used to determine how aligned the NPC is with the faction's ideals.

    Traits are assumed to be numerical vectors or shared tags.
    """
    npc_traits = npc_data.get("personality_traits", {})
    faction_traits = faction_data.get("trait_profile", {})

    score = 0
    max_score = 36  # Full alignment on all 6 scaled traits (6 * 6 = 36)

    # Trait vector comparison — assume 6 common traits for simplicity
    for trait in ["valor", "order", "ambition", "community", "freedom", "discipline"]:
        npc_val = npc_traits.get(trait, 3)         # default neutral value
        faction_val = faction_traits.get(trait, 3)  # default neutral value
        diff = abs(npc_val - faction_val)
        score += (6 - diff)  # closer = higher score

    return score  # Max is 6 traits * max alignment = 36
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

        if affinity >= 32:
            loyalty = 3
        elif affinity >= 28:
            loyalty = 2
        elif affinity >= 24:
            loyalty = 1
        elif affinity <= 18:
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

        if affinity >= 32:
            score = 3
        elif affinity >= 28:
            score = 2
        elif affinity >= 24:
            score = 1
        elif affinity <= 18:
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

    # Save faction data
    db.reference(f"/factions/{fid}").set(faction_data)

    # Log globally
    log_entry = {
        "faction": fid,
        "name": faction_data.get("name"),
        "created": now,
        "motif_seed": faction_data["motif_seed"],
        "outposts": faction_data["poi_outposts"]
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

    return {"message": f"Faction '{fid}' created and logged.", "npc_loyalists": assigned}

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
