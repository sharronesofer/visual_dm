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
