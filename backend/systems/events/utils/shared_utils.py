"""
Shared utilities used by multiple modules to avoid circular imports.
"""

from firebase_admin import db
from datetime import datetime
import random

def get_current_game_day():
    """Get the current game day from global state."""
    ref = db.reference("/global_state")
    return ref.get().get("current_day", 0)

def process_poi_raid(poi_id: str, poi_type: str, danger: int, npc_count: int, region_name: str) -> dict:
    """
    Process a raid on a POI and return the event data if any changes occurred.
    """
    raid_strength = danger * 5 + random.randint(0, danger * 3)
    day = get_current_game_day()
    
    if poi_type == "social":
        defense_score = npc_count * 5 + random.randint(0, 15)
        if raid_strength > defense_score:
            return {
                "type": "overrun_by_monsters",
                "poi_id": poi_id,
                "region": region_name,
                "danger": danger,
                "day": day
            }
    elif poi_type == "dungeon":
        reclaim_score = danger * 6 + random.randint(0, 20)
        if reclaim_score > raid_strength:
            return {
                "type": "reclaimed_by_npcs",
                "poi_id": poi_id,
                "region": region_name,
                "danger": danger,
                "day": day
            }
    
    return None 