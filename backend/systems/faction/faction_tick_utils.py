#This module simulates faction influence propagation through Points of Interest (POIs) using a BFS-style algorithm. It decays influence across connections and records results per POI in Firebase.
#It's directly tied to faction, world, region, and poi systems.

import random
from firebase_admin import db
from collections import deque
from datetime import datetime

def log_poi_event(region, poi_id, event_type, data=None):
    """
    Append a new event to a POI's /event_log
    """
    ref = db.reference(f"/poi_state/{region}/{poi_id}/evolution_state/event_log")
    event_log = ref.get() or []

    entry = {
        "type": event_type,
        "day": get_current_game_day(),
        "timestamp": datetime.utcnow().isoformat()
    }
    if data:
        entry.update(data)

    event_log.append(entry)
    ref.set(event_log)

def get_all_poi_states():
    """
    Fetch and flatten all POI state data.
    Returns a dict of { poi_id: {state...} }
    """
    poi_root = db.reference("/poi_state").get() or {}
    flat = {}
    for region, pois in poi_root.items():
        for poi_id, poi_data in pois.items():
            poi_data["region"] = region  # preserve region info
            flat[poi_id] = poi_data
    return flat

def propagate_faction_influence():
    """
    Scans all factions and spreads their influence outward from origin POIs.
    Also attempts to spread faction affiliation to NPCs.
    """
    all_factions = db.reference("/factions").get() or {}
    poi_root = db.reference("/poi_state").get() or {}

    for fid, faction in all_factions.items():
        seeds = faction.get("poi_outposts", [])
        visited = set()

        for seed in seeds:
            for region_name, region_pois in poi_root.items():
                if seed not in region_pois:
                    continue

                queue = deque([(region_name, seed, 10)])  # (region, poi_id, influence)
                while queue:
                    region, poi_id, influence = queue.popleft()
                    if (region, poi_id) in visited or influence <= 0:
                        continue
                    visited.add((region, poi_id))

                    poi_ref = db.reference(f"/poi_state/{region}/{poi_id}/faction_influence/{fid}")
                    current = poi_ref.get() or 0
                    poi_ref.set(max(current, influence))

                    # Find connected POIs (neighbors)
                    region_map = db.reference(f"/poi_state/{region}").get() or {}
                    neighbors = region_map.get(poi_id, {}).get("connected_pois", [])
                    random.shuffle(neighbors)

                    for neighbor in neighbors:
                        if (region, neighbor) not in visited:
                            # Optional mutation chance
                            mutation_chance = 0.1 if influence < 6 else 0.02
                            decay = random.randint(1, 2)
                            next_influence = influence - decay

                            if random.random() < mutation_chance:
                                next_influence = max(0, next_influence - random.randint(1, 3))

                            queue.append((region, neighbor, next_influence))

        # 👇 After BFS ends for this faction, try spreading to NPCs
        poi_data_map = get_all_poi_states()
        propagate_faction_to_npcs(fid, {}, poi_data_map)

def propagate_faction_to_npcs(faction_id, region_data, poi_data_map):
    """
    Influence NPC faction affiliations in POIs where the faction is active.
    """
    influence_log = []
    for poi_id, poi_data in poi_data_map.items():
        npcs = poi_data.get("npcs_present", [])
        if faction_id not in poi_data.get("faction_influence", []):
            continue

        for npc_id in npcs:
            npc_ref = db.reference(f'/npc_core/{npc_id}')
            npc_data = npc_ref.get() or {}
            affiliations = npc_data.get("faction_affiliations", [])
            
            # Already affiliated? Skip or deepen loyalty
            if faction_id in affiliations:
                continue

            # Influence chance can be tied to loyalty, fear, rumors, etc.
            chance = 0.15 + 0.05 * poi_data.get("danger_level", 5)
            if random.random() < chance:
                affiliations.append(faction_id)
                npc_data["faction_affiliations"] = affiliations
                npc_ref.set(npc_data)
                influence_log.append({"npc": npc_id, "poi": poi_id, "method": "proximity"})

    return influence_log

def decay_faction_tensions(session, decay_rate_positive=0.5, decay_rate_negative=0.5, min_decay=0.1, max_decay=2.5):
    """
    Decay faction relationship tensions over time, in both positive and negative directions.
    
    As described in the development bible, tension decays naturally over time in both 
    directions - positive tensions (conflict) decay toward neutral, and negative tensions
    (alliances) decay toward neutral as well.
    
    Args:
        session: Database session
        decay_rate_positive: Base decay rate for positive tensions (0-100, conflict) (default: 0.5)
        decay_rate_negative: Base decay rate for negative tensions (-100-0, alliance) (default: 0.5)
        min_decay: Minimum decay amount per tick (default: 0.1)
        max_decay: Maximum decay amount per tick (default: 2.5)
        
    Returns:
        Dict with statistics about decay operations
    """
    from sqlalchemy.orm import Session
    from backend.systems.faction.models.faction import FactionRelationship
    from datetime import datetime, timedelta
    from sqlalchemy import text
    import random
    
    # Get all active relationships with non-zero tension
    relationships = session.query(FactionRelationship).filter(
        FactionRelationship.tension != 0.0
    ).all()
    
    # Skip processing if no relationships found
    if not relationships:
        return {
            "relationships_processed": 0,
            "tensions_decayed": 0,
            "total_decay_amount": 0.0
        }
    
    # Counters for statistics
    processed_count = 0
    decayed_count = 0
    total_decay = 0.0
    
    # Process each relationship
    for rel in relationships:
        # Special case: if at war, tension doesn't decay automatically
        if rel.diplomatic_stance == "at_war" and rel.war_state.get("at_war", False):
            continue
            
        processed_count += 1
        original_tension = rel.tension
        
        # Calculate decay rate with some randomization
        if original_tension > 0:  # Positive tension (conflict)
            # Higher values decay faster
            base_decay = decay_rate_positive * (0.5 + (original_tension / 200.0))
            # Add randomness +/- 30%
            randomness_factor = 0.7 + (random.random() * 0.6)  # 0.7 to 1.3
            decay_amount = base_decay * randomness_factor
            
            # Ensure decay is within bounds
            decay_amount = max(min_decay, min(max_decay, decay_amount))
            
            # Clamp to zero or current value
            new_tension = max(0, original_tension - decay_amount)
        else:  # Negative tension (alliance)
            # More negative values decay faster (closer to zero)
            base_decay = decay_rate_negative * (0.5 + (abs(original_tension) / 200.0))
            # Add randomness +/- 30%
            randomness_factor = 0.7 + (random.random() * 0.6)  # 0.7 to 1.3
            decay_amount = base_decay * randomness_factor
            
            # Ensure decay is within bounds
            decay_amount = max(min_decay, min(max_decay, decay_amount))
            
            # Clamp to zero or current value
            new_tension = min(0, original_tension + decay_amount)
            
        # Update if there was decay
        if new_tension != original_tension:
            # Update both directions of relationship
            rel.tension = new_tension
            
            # Get reciprocal relationship
            recip = session.query(FactionRelationship).filter(
                FactionRelationship.faction_id == rel.other_faction_id,
                FactionRelationship.other_faction_id == rel.faction_id
            ).first()
            
            if recip:
                recip.tension = new_tension
                
            # Record the decay in history if significant
            if abs(original_tension - new_tension) >= 1.0:
                history_entry = {
                    "type": "tension_decay",
                    "old_tension": original_tension,
                    "new_tension": new_tension,
                    "decay_amount": abs(original_tension - new_tension),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                rel.history.append(history_entry)
                if recip:
                    recip.history.append(history_entry)
                    
            decayed_count += 1
            total_decay += abs(original_tension - new_tension)
            
    # Commit changes
    if decayed_count > 0:
        session.commit()
        
    # Return statistics
    return {
        "relationships_processed": processed_count,
        "tensions_decayed": decayed_count,
        "total_decay_amount": total_decay,
        "timestamp": datetime.utcnow().isoformat()
    }

