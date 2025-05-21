"""
Region Revolt/Conflict Simulation Utilities
Handles simulated revolts in POIs for capitol change mechanics.
See docs/stubs_needs_consolidation_qna.md for requirements.
"""
from firebase_admin import db
from backend.npcs.npc_leveling_utils import get_npc_level
from backend.world.utils.world_event_utils import log_world_event
from datetime import datetime

def simulate_revolt_in_poi(region_id: str, poi_id: str, factions_present: list, npc_list: list, tension_level: float):
    """
    Simulate a revolt in a POI if tension is at 'war' level and one faction outnumbers/outlevels others.
    Args:
        region_id: The region ID
        poi_id: The POI ID
        factions_present: List of faction IDs present
        npc_list: List of NPC dicts (must include 'faction_affiliations', 'role', 'npc_id')
        tension_level: Current tension (0-100)
    Returns:
        Dict with revolt outcome and winner, or None if no revolt
    Q&A: Revolt can happen when a faction outnumbers others in a POI and tension is at 'war' levels. Simulate conflict based on total NPC level per faction.
    """
    if tension_level < 80:
        return None  # Not at war level
    # Tally total level per faction
    faction_strength = {f: 0 for f in factions_present}
    for npc in npc_list:
        for f in npc.get('faction_affiliations', []):
            if f in faction_strength:
                faction_strength[f] += get_npc_level(npc.get('role', 'laborer'))
    # Find the strongest faction
    winner = max(faction_strength, key=lambda f: faction_strength[f])
    # Check if winner outnumbers/outlevels all others
    if all(faction_strength[winner] > faction_strength[f] for f in faction_strength if f != winner):
        # Fetch current ruling faction
        poi_ref = db.reference(f"/poi_state/{region_id}/{poi_id}")
        poi_data = poi_ref.get() or {}
        ruling_faction = poi_data.get('ruling_faction')
        if ruling_faction != winner:
            # Trigger capitol change
            poi_ref.child('ruling_faction').set(winner)
            # Log as world event
            log_world_event({
                "type": "capitol_change",
                "region_id": region_id,
                "poi_id": poi_id,
                "old_faction": ruling_faction,
                "new_faction": winner,
                "timestamp": datetime.utcnow().isoformat(),
                "details": {"revolt": True, "faction_strength": faction_strength}
            })
            # Log as core memory in region
            mem_ref = db.reference(f"/regions/{region_id}/memory")
            memory = mem_ref.get() or []
            memory.append({
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": "capitol_change",
                "details": {
                    "poi_id": poi_id,
                    "old_faction": ruling_faction,
                    "new_faction": winner,
                    "revolt": True,
                    "faction_strength": faction_strength
                },
                "core": True
            })
            mem_ref.set(memory)
            return {"revolt": True, "winner": winner, "old_faction": ruling_faction, "faction_strength": faction_strength}
    return None 
