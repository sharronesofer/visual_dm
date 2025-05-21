"""
World Event & Chaos Utilities
Handles world-level event logging, chaos event injection, analytics hooks, and developer tools.
See docs/stubs_needs_consolidation_qna.md for requirements.

- World Event Logging: All major system changes (war, membership, rumor, revolt, diplomacy, arc, capitol change, tension spike, metropolis assignment) logged in global world history and as core memories.
- Chaos: Chaos events can be injected, rolled, or forced; narrative chaos table; analytics hooks for chaos triggers.
- Analytics: All events include player/NPC presence, severity, affected systems; supports dev tools for annotation and deletion.
- Cross-System Hooks: All major backend systems call log_world_event for relevant events; supports extensibility and analytics.
- TODO: Ensure all narrative/mechanical hooks are present and robust; cross-system event hooks; analytics integration; stress testing.
"""
from datetime import datetime
import random
from firebase_admin import db
from typing import List, Dict, Any, Optional, Union
import logging
import json
import os
from pathlib import Path

from backend.systems.world_state.core.types import StateCategory, WorldRegion

logger = logging.getLogger(__name__)

# Storage path for events
EVENTS_PATH = Path("data/world_state/events")
os.makedirs(EVENTS_PATH, exist_ok=True)

NARRATIVE_CHAOS_TABLE = [
    "NPC betrays a faction or personal goal",
    "Player receives a divine omen",
    "NPC vanishes mysteriously",
    "Corrupted prophecy appears in a temple or vision",
    "Artifact or item changes hands unexpectedly",
    "NPC's child arrives with a claim",
    "Villain resurfaces (real or false)",
    "Time skip or memory blackout (~5 minutes)",
    "PC is blamed for a crime in a new city",
    "Ally requests an impossible favor",
    "Magical item begins to misbehave",
    "Enemy faction completes objective offscreen",
    "False flag sent from another region",
    "NPC becomes hostile based on misinformation",
    "Rumor spreads about a player betrayal",
    "PC has a surreal dream altering perception",
    "Secret faction is revealed through slip-up",
    "NPC becomes obsessed with the PC",
    "Town leader is assassinated",
    "Prophecy misidentifies the chosen one"
]

def log_world_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log a world event to the global world log, including analytics metadata.
    
    Args:
        event_data: Event data to log
        
    Returns:
        The logged event data with added metadata
    """
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    event_data["event_id"] = event_id
    event_data["timestamp"] = datetime.utcnow().isoformat()
    event_data.setdefault("players_present", [])
    event_data.setdefault("npcs_present", [])
    event_data.setdefault("severity", 1)
    event_data.setdefault("affected_systems", [])
    
    # Save to file
    event_path = EVENTS_PATH / f"{event_id}.json"
    with open(event_path, 'w') as f:
        json.dump(event_data, f, indent=2)
    
    # Log event creation
    logger.info(f"World event logged: {event_id} - {event_data.get('summary', 'No summary')}")
    
    return event_data

def roll_chaos_event() -> str:
    """
    Randomly select a narrative chaos event from the canonical table.
    
    Returns:
        A randomly selected chaos event description
    """
    return random.choice(NARRATIVE_CHAOS_TABLE)

def inject_chaos_event(event_type: str, region: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Inject a chaos event into the world log and optionally sync beliefs in a region.
    
    Args:
        event_type: The type of chaos event
        region: Optional region identifier
        context: Optional additional context data
        
    Returns:
        The created event data
    """
    context = context or {}
    event_id = f"chaos_{int(datetime.utcnow().timestamp())}"
    summary = f"[CHAOS EVENT] {event_type}"
    event_data = {
        "event_id": event_id,
        "summary": summary,
        "type": "narrative_chaos",
        "timestamp": datetime.utcnow().isoformat(),
        "context": context
    }
    
    # Save to file
    event_path = EVENTS_PATH / f"{event_id}.json"
    with open(event_path, 'w') as f:
        json.dump(event_data, f, indent=2)
    
    if region:
        try:
            from app.npc.npc_rumor_utils import sync_event_beliefs
            sync_event_beliefs(region, event_data)
        except ImportError:
            logger.warning("Could not import sync_event_beliefs to propagate chaos event")
    
    # Log event creation
    logger.info(f"Chaos event injected: {event_id} - {event_type}")
    
    return event_data

def trigger_chaos_if_needed(npc_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Trigger a chaos event if motif/narrative thresholds are met.
    
    Args:
        npc_id: ID of the NPC to check
        region: Optional region identifier
        
    Returns:
        Result data indicating if chaos was triggered
    """
    try:
        from app.motifs.motif_engine_class import MotifEngine
        engine = MotifEngine(npc_id)
        threshold = engine.check_aggression_threshold()
        
        if not threshold:
            return {"message": "No chaos triggered"}
            
        chaos_type = roll_chaos_event()
        event = inject_chaos_event(chaos_type, region, context={"npc_id": npc_id, "threshold": threshold})
        
        return {"chaos_triggered": True, "event": event}
    except ImportError:
        logger.warning("MotifEngine not available, cannot trigger chaos")
        return {"error": "MotifEngine not available"}

def force_chaos(npc_id: str, region: Optional[str] = None) -> Dict[str, Any]:
    """
    Force a chaos event and motif rotation for an NPC, logging all changes.
    
    Args:
        npc_id: ID of the NPC to force chaos for
        region: Optional region identifier
        
    Returns:
        Result data with the forced motif and event
    """
    try:
        from app.motifs.motif_engine_class import MotifEngine
        from app.motifs.motif_utils import roll_new_motif
        
        engine = MotifEngine(npc_id)
        pool = engine.get_pool()
        
        new_motif = roll_new_motif(
            exclude=[m["theme"] for m in pool.get("active_motifs", [])],
            chaos_source=True
        )
        
        pool["active_motifs"].append(new_motif)
        pool["motif_history"].append(new_motif["theme"])
        pool["last_rotated"] = datetime.utcnow().isoformat()
        
        # Update NPC motif pool
        # Using file-based storage for now, can be updated to use DB later
        npc_path = Path(f"data/npcs/{npc_id}.json")
        if npc_path.exists():
            with open(npc_path, 'r') as f:
                npc_data = json.load(f)
            
            npc_data["narrative_motif_pool"] = pool
            
            with open(npc_path, 'w') as f:
                json.dump(npc_data, f, indent=2)
        
        chaos_type = roll_chaos_event()
        event = inject_chaos_event(chaos_type, region, context={"npc_id": npc_id, "forced": True})
        
        return {"forced_motif": new_motif, "event": event}
    except ImportError:
        logger.warning("MotifEngine or motif_utils not available, cannot force chaos")
        return {"error": "MotifEngine or motif_utils not available"}

# --- Dev Utilities ---
def delete_world_event(event_id: str) -> bool:
    """
    Delete a world event from the global world log by event_id.
    For use by devs to remove erroneous or unwanted events.
    
    Args:
        event_id: ID of the event to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        event_path = EVENTS_PATH / f"{event_id}.json"
        if event_path.exists():
            os.remove(event_path)
            logger.info(f"Deleted world event: {event_id}")
            return True
        else:
            logger.warning(f"Event not found: {event_id}")
            return False
    except Exception as e:
        logger.error(f"Error deleting world event: {str(e)}")
        return False

def annotate_world_event(event_id: str, annotation: str) -> bool:
    """
    Annotate a world event with additional notes or corrections.
    For use by devs to clarify or correct event entries.
    
    Args:
        event_id: ID of the event to annotate
        annotation: Annotation text to add
        
    Returns:
        True if successful, False otherwise
    """
    try:
        event_path = EVENTS_PATH / f"{event_id}.json"
        if not event_path.exists():
            logger.warning(f"Event not found: {event_id}")
            return False
            
        with open(event_path, 'r') as f:
            event_data = json.load(f)
            
        annotations = event_data.get("annotations", [])
        annotations.append({
            "timestamp": datetime.utcnow().isoformat(),
            "note": annotation
        })
        
        event_data["annotations"] = annotations
        
        with open(event_path, 'w') as f:
            json.dump(event_data, f, indent=2)
            
        logger.info(f"Annotated world event: {event_id}")
        return True
    except Exception as e:
        logger.error(f"Error annotating world event: {str(e)}")
        return False

def create_world_event(
    event_type: str,
    description: str,
    location: Optional[str] = None,
    category: Optional[StateCategory] = None,
    region: Optional[WorldRegion] = None,
    entity_id: Optional[str] = None,
    related_events: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create and store a world event.
    
    Args:
        event_type: Type of event
        description: Event description
        location: Optional location identifier
        category: Optional state category
        region: Optional world region
        entity_id: Optional entity ID related to the event
        related_events: Optional list of related event IDs
        metadata: Optional additional metadata
        
    Returns:
        The created event
    """
    # Generate unique event ID
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    
    # Create event data
    event = {
        "id": event_id,
        "type": event_type,
        "description": description,
        "timestamp": datetime.utcnow().isoformat(),
        "location": location,
        "category": category.name if category else None,
        "region": region.name if region else None, 
        "entity_id": entity_id,
        "related_events": related_events or [],
        "metadata": metadata or {}
    }
    
    # Save to storage
    event_path = EVENTS_PATH / f"{event_id}.json"
    with open(event_path, 'w') as f:
        json.dump(event, f, indent=2)
    
    logger.info(f"Created world event: {event_id} - {event_type}")
    return event

def link_events(source_event_id: str, target_event_id: str, relationship_type: str = "related") -> bool:
    """
    Link two world events with a specified relationship.
    
    Args:
        source_event_id: ID of the source event
        target_event_id: ID of the target event
        relationship_type: Type of relationship between events
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if both events exist
        source_path = EVENTS_PATH / f"{source_event_id}.json"
        target_path = EVENTS_PATH / f"{target_event_id}.json"
        
        if not source_path.exists() or not target_path.exists():
            logger.warning(f"Event not found when linking: {source_event_id} -> {target_event_id}")
            return False
        
        # Load source event
        with open(source_path, 'r') as f:
            source_event = json.load(f)
        
        # Load target event
        with open(target_path, 'r') as f:
            target_event = json.load(f)
        
        # Add relationship to source event
        if "relationships" not in source_event:
            source_event["relationships"] = {}
        
        if relationship_type not in source_event["relationships"]:
            source_event["relationships"][relationship_type] = []
        
        if target_event_id not in source_event["relationships"][relationship_type]:
            source_event["relationships"][relationship_type].append(target_event_id)
        
        # Add inverse relationship to target event
        if "relationships" not in target_event:
            target_event["relationships"] = {}
        
        inverse_type = f"inverse_{relationship_type}"
        if inverse_type not in target_event["relationships"]:
            target_event["relationships"][inverse_type] = []
        
        if source_event_id not in target_event["relationships"][inverse_type]:
            target_event["relationships"][inverse_type].append(source_event_id)
        
        # Save both events
        with open(source_path, 'w') as f:
            json.dump(source_event, f, indent=2)
        
        with open(target_path, 'w') as f:
            json.dump(target_event, f, indent=2)
        
        logger.info(f"Linked events: {source_event_id} -> {target_event_id} ({relationship_type})")
        return True
    except Exception as e:
        logger.error(f"Error linking events: {str(e)}")
        return False

def get_related_events(event_id: str, relationship_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Get all related events for a given event ID, optionally filtered by relationship type.
    
    Args:
        event_id: ID of the event to get related events for
        relationship_types: Optional list of relationship types to filter by
        
    Returns:
        List of related event data
    """
    try:
        event_path = EVENTS_PATH / f"{event_id}.json"
        if not event_path.exists():
            logger.warning(f"Event not found: {event_id}")
            return []
        
        with open(event_path, 'r') as f:
            event = json.load(f)
        
        if "relationships" not in event:
            return []
        
        related_ids = []
        for rel_type, ids in event["relationships"].items():
            # Skip if filtering by relationship types and this type is not in the list
            if relationship_types and rel_type not in relationship_types:
                continue
            
            related_ids.extend(ids)
        
        # Remove duplicates
        related_ids = list(set(related_ids))
        
        # Load related events
        related_events = []
        for related_id in related_ids:
            related_path = EVENTS_PATH / f"{related_id}.json"
            if related_path.exists():
                with open(related_path, 'r') as f:
                    related_events.append(json.load(f))
            else:
                logger.warning(f"Related event not found: {related_id}")
        
        return related_events
    except Exception as e:
        logger.error(f"Error getting related events: {str(e)}")
        return []

def filter_events_by_category(category: Union[StateCategory, str], limit: int = 50) -> List[Dict[str, Any]]:
    """
    Find events matching a specific category.
    
    Args:
        category: Category to filter by (either a StateCategory enum or string)
        limit: Maximum number of events to return
        
    Returns:
        List of matching event data
    """
    try:
        # Convert category to string if it's an enum
        if isinstance(category, StateCategory):
            category_str = category.name
        else:
            category_str = category
        
        matching_events = []
        event_files = list(EVENTS_PATH.glob("*.json"))
        
        for event_file in event_files:
            with open(event_file, 'r') as f:
                event = json.load(f)
            
            # Check if category matches
            if event.get("category") == category_str:
                matching_events.append(event)
                
                # Check limit
                if len(matching_events) >= limit:
                    break
        
        # Sort by timestamp (newest first)
        matching_events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        
        return matching_events
    except Exception as e:
        logger.error(f"Error filtering events by category: {str(e)}")
        return []

def filter_events_by_location(location: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Find events that occurred at a specific location.
    
    Args:
        location: Location identifier to filter by
        limit: Maximum number of events to return
        
    Returns:
        List of matching event data
    """
    try:
        matching_events = []
        event_files = list(EVENTS_PATH.glob("*.json"))
        
        for event_file in event_files:
            with open(event_file, 'r') as f:
                event = json.load(f)
            
            # Check if location matches
            if event.get("location") == location:
                matching_events.append(event)
                
                # Check limit
                if len(matching_events) >= limit:
                    break
        
        # Sort by timestamp (newest first)
        matching_events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        
        return matching_events
    except Exception as e:
        logger.error(f"Error filtering events by location: {str(e)}")
        return []

def format_event_description(event: Dict[str, Any], include_metadata: bool = False) -> str:
    """
    Format an event into a human-readable description.
    
    Args:
        event: Event data to format
        include_metadata: Whether to include metadata in the description
        
    Returns:
        Formatted description
    """
    try:
        lines = []
        
        # Add base information
        lines.append(f"Event: {event.get('id', 'Unknown ID')}")
        lines.append(f"Type: {event.get('type', 'Unknown type')}")
        lines.append(f"Time: {event.get('timestamp', 'Unknown time')}")
        
        # Add description
        if "description" in event:
            lines.append(f"Description: {event['description']}")
        
        # Add location information
        if "location" in event and event["location"]:
            lines.append(f"Location: {event['location']}")
        
        if "region" in event and event["region"]:
            lines.append(f"Region: {event['region']}")
        
        # Add entity information
        if "entity_id" in event and event["entity_id"]:
            lines.append(f"Related entity: {event['entity_id']}")
        
        # Add metadata if requested
        if include_metadata and "metadata" in event and event["metadata"]:
            lines.append("\nMetadata:")
            for key, value in event["metadata"].items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    except Exception as e:
        logger.error(f"Error formatting event description: {str(e)}")
        return f"Error formatting event: {str(e)}" 