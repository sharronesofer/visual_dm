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
