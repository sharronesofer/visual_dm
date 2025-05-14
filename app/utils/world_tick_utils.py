from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.models import Region, Event, NPC
from firebase_admin import db

def tick_world_day() -> Dict[str, Any]:
    """Process one day of world time."""
    try:
        # Get all regions
        regions = Region.query.all()
        events = []
        
        for region in regions:
            # Update region state
            region.last_updated = datetime.utcnow()
            
            # Generate new events
            new_events = generate_region_events(region)
            events.extend(new_events)
            
            # Update NPCs in region
            update_region_npcs(region)
        
        return {
            "success": True,
            "events": events,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def generate_region_events(region: Region) -> List[Event]:
    """Generate new events for a region."""
    events = []
    # Add event generation logic here
    return events

def update_region_npcs(region: Region) -> None:
    """Update NPCs in a region."""
    npcs = NPC.query.filter_by(region_id=region.id).all()
    for npc in npcs:
        # Update NPC state
        npc.last_updated = datetime.utcnow()
        # Add more NPC update logic here

def process_world_tick() -> Dict[str, Any]:
    """Process the world tick and update all necessary components."""
    try:
        result = tick_world_day()
        if result["success"]:
            # Add additional processing here
            pass
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def cleanup_old_events(events: List[Dict], max_age_days: int = 30) -> List[Dict]:
    """Remove events older than the specified age."""
    current_time = datetime.now()
    return [
        event for event in events
        if (current_time - datetime.fromtimestamp(event['timestamp'])).days <= max_age_days
    ]

def tick_all_shops(shops: List[Dict]) -> List[Dict]:
    """Update shop inventories and prices."""
    for shop in shops:
        # Restock items
        for item in shop['inventory']:
            if item['quantity'] < item['restock_threshold']:
                item['quantity'] = min(
                    item['quantity'] + item['restock_rate'],
                    item['max_quantity']
                )
        
        # Update prices based on supply and demand
        for item in shop['inventory']:
            demand_modifier = calculate_demand_modifier(item)
            item['current_price'] = item['base_price'] * demand_modifier
    
    return shops

def calculate_demand_modifier(item: Dict) -> float:
    """Calculate price modifier based on supply and demand."""
    supply_ratio = item['quantity'] / item['max_quantity']
    
    if supply_ratio <= 0.2:  # Very low supply
        return 1.5
    elif supply_ratio <= 0.5:  # Low supply
        return 1.2
    elif supply_ratio >= 0.9:  # High supply
        return 0.8
    else:  # Normal supply
        return 1.0

def process_world_tick(world_state: Dict) -> Dict:
    """Process one tick of world time."""
    # Update time
    world_state['current_time'] += world_state['tick_duration']
    
    # Process weather changes
    world_state['weather'] = update_weather(world_state['weather'])
    
    # Process NPC schedules
    world_state['npcs'] = update_npc_schedules(world_state['npcs'])
    
    # Process active effects
    world_state['active_effects'] = process_active_effects(world_state['active_effects'])
    
    return world_state

def update_weather(current_weather: Dict) -> Dict:
    """Update weather conditions."""
    # Implementation would depend on your weather system
    return current_weather

def update_npc_schedules(npcs: List[Dict]) -> List[Dict]:
    """Update NPC locations and activities based on their schedules."""
    current_hour = datetime.now().hour
    
    for npc in npcs:
        if 'schedule' in npc:
            for time_slot in npc['schedule']:
                if time_slot['start_hour'] <= current_hour < time_slot['end_hour']:
                    npc['current_location'] = time_slot['location']
                    npc['current_activity'] = time_slot['activity']
                    break
    
    return npcs

def process_active_effects(effects: List[Dict]) -> List[Dict]:
    """Process and update active effects in the world."""
    current_time = datetime.now()
    
    # Remove expired effects
    active_effects = [
        effect for effect in effects
        if datetime.fromtimestamp(effect['end_time']) > current_time
    ]
    
    # Process ongoing effects
    for effect in active_effects:
        if effect.get('tick_function'):
            effect['tick_function'](effect)
    
    return active_effects

def calculate_time_passed(start_time: datetime, end_time: datetime) -> Dict[str, int]:
    """Calculate time passed between two timestamps."""
    time_diff = end_time - start_time
    
    return {
        "days": time_diff.days,
        "hours": time_diff.seconds // 3600,
        "minutes": (time_diff.seconds % 3600) // 60,
        "total_hours": time_diff.days * 24 + time_diff.seconds // 3600
    }

def tick_all_motifs(world_state: Dict[str, Any]) -> Dict[str, Any]:
    """Process and update all world motifs during a world tick."""
    motifs = world_state.get("motifs", {})
    current_time = datetime.now()
    
    for motif_id, motif in motifs.items():
        # Skip inactive motifs
        if not motif.get("active", False):
            continue
            
        # Calculate time since last update
        last_update = datetime.fromisoformat(motif.get("last_update", current_time.isoformat()))
        time_passed = calculate_time_passed(last_update, current_time)
        
        # Update motif strength based on time and factors
        strength_change = 0
        
        # Time decay
        strength_change -= time_passed["days"] * motif.get("daily_decay", 0.1)
        
        # Supporting events
        for event in motif.get("supporting_events", []):
            if event.get("timestamp") > last_update.isoformat():
                strength_change += event.get("impact", 0.5)
        
        # Opposing events
        for event in motif.get("opposing_events", []):
            if event.get("timestamp") > last_update.isoformat():
                strength_change -= event.get("impact", 0.5)
        
        # Update motif strength
        motifs[motif_id]["strength"] = max(0, min(10, motif["strength"] + strength_change))
        motifs[motif_id]["last_update"] = current_time.isoformat()
        
        # Check for motif completion or failure
        if motifs[motif_id]["strength"] >= motif.get("completion_threshold", 10):
            motifs[motif_id]["active"] = False
            motifs[motif_id]["status"] = "completed"
        elif motifs[motif_id]["strength"] <= motif.get("failure_threshold", 0):
            motifs[motif_id]["active"] = False
            motifs[motif_id]["status"] = "failed"
    
    world_state["motifs"] = motifs
    return world_state

def tick_all_loyalty(world_state: Dict[str, Any]) -> Dict[str, Any]:
    """Process and update all NPC loyalty values during a world tick."""
    npcs = world_state.get("npcs", {})
    current_time = datetime.now()
    
    for npc_id, npc in npcs.items():
        # Skip NPCs without loyalty tracking
        if "loyalty" not in npc:
            continue
            
        # Calculate time since last update
        last_update = datetime.fromisoformat(npc.get("last_loyalty_update", current_time.isoformat()))
        time_passed = calculate_time_passed(last_update, current_time)
        
        # Base loyalty change from time
        loyalty_change = 0
        
        # Daily decay
        loyalty_change -= time_passed["days"] * npc.get("loyalty_decay", 0.1)
        
        # Recent interactions
        for interaction in npc.get("recent_interactions", []):
            if interaction.get("timestamp") > last_update.isoformat():
                loyalty_change += interaction.get("loyalty_impact", 0)
        
        # Apply faction effects
        for faction, relation in npc.get("faction_relations", {}).items():
            faction_change = relation * npc.get("faction_loyalty_multiplier", 0.5)
            loyalty_change += faction_change
        
        # Update loyalty
        npcs[npc_id]["loyalty"] = max(0, min(100, npc["loyalty"] + loyalty_change))
        npcs[npc_id]["last_loyalty_update"] = current_time.isoformat()
        
        # Check for loyalty thresholds
        if npcs[npc_id]["loyalty"] <= npc.get("betrayal_threshold", 20):
            npcs[npc_id]["status"] = "hostile"
        elif npcs[npc_id]["loyalty"] >= npc.get("devotion_threshold", 80):
            npcs[npc_id]["status"] = "devoted"
    
    world_state["npcs"] = npcs
    return world_state

def tick_npc_emotions(npc_id: str) -> Dict[str, Any]:
    """
    Update NPC emotions based on recent events and personality.
    
    Args:
        npc_id: ID of the NPC
        
    Returns:
        Dict containing updated emotion values
    """
    try:
        # Get NPC data
        npc_ref = db.reference(f"/npcs/{npc_id}")
        npc = npc_ref.get()
        
        if not npc:
            return {"success": False, "message": "NPC not found"}
            
        # Get recent events
        events_ref = db.reference(f"/npc_events/{npc_id}")
        events = events_ref.get() or []
        
        # Initialize emotion changes
        emotion_changes = {
            "happiness": 0,
            "anger": 0,
            "fear": 0,
            "trust": 0
        }
        
        # Process recent events
        for event in events[-5:]:  # Look at last 5 events
            event_type = event.get("type")
            magnitude = event.get("magnitude", 1)
            
            # Apply emotion changes based on event type
            if event_type == "positive_interaction":
                emotion_changes["happiness"] += magnitude
                emotion_changes["trust"] += magnitude
            elif event_type == "negative_interaction":
                emotion_changes["anger"] += magnitude
                emotion_changes["trust"] -= magnitude
            elif event_type == "threat":
                emotion_changes["fear"] += magnitude
                emotion_changes["trust"] -= magnitude
                
        # Update NPC emotions
        current_emotions = npc.get("emotions", {})
        for emotion, change in emotion_changes.items():
            current_value = current_emotions.get(emotion, 0)
            new_value = max(-10, min(10, current_value + change))
            current_emotions[emotion] = new_value
            
        # Save updated emotions
        npc_ref.update({"emotions": current_emotions})
        
        return {
            "success": True,
            "emotions": current_emotions,
            "changes": emotion_changes
        }
        
    except Exception as e:
        print(f"Error updating NPC emotions: {e}")
        return {"success": False, "message": "Error processing emotions"} 