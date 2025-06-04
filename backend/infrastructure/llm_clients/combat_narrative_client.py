"""
Combat Narrative LLM Client

This module provides LLM integration for combat narrative generation.
Extracted from the combat system to separate technical infrastructure
from business logic.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from backend.infrastructure.config_loaders.combat_config_loader import combat_config
from backend.infrastructure.database_adapters.combat_database_adapter import combat_db_adapter


def narrate_action(actor_name: str, action_details: Dict[str, Any], outcome: Dict[str, Any]) -> Optional[str]:
    """
    Generate a narrative description of a combat action using AI.
    
    Args:
        actor_name: Name of the actor performing the action
        action_details: Details of the action (ability, target, etc.)
        outcome: Result of the action (hit, damage, etc.)
        
    Returns:
        str: Narrative description of the combat action, or None if generation fails
        
    Raises:
        ValueError: If required parameters are missing
        RuntimeError: If AI generation fails
    """
    # Input validation
    if not actor_name:
        raise ValueError("Actor name cannot be empty")
    if not isinstance(action_details, dict):
        raise TypeError("Action details must be a dictionary")
    if not isinstance(outcome, dict):
        raise TypeError("Outcome must be a dictionary")
    
    # Check if narrative generation is enabled
    if not combat_config.get("logging.enable_narrative_generation", True):
        return f"{actor_name} used {action_details.get('ability', 'an action')} on {action_details.get('target', 'target')}"
    
    try:
        from backend.infrastructure.llm.core.gpt_client import GPTClient
        
        # Build detailed prompt
        ability = action_details.get('ability', 'an action')
        target = action_details.get('target', 'target')
        hit_status = 'hit' if outcome.get('hit', False) else 'missed'
        damage = outcome.get('damage', 0)
        damage_type = outcome.get('damage_type', 'damage')
        target_hp = outcome.get('target_hp', '?')
        critical = outcome.get('critical', False)
        
        prompt = (
            f"{actor_name} used {ability} on {target}.\n"
            f"The attack {hit_status}"
        )
        
        if hit_status == 'hit':
            critical_text = " critically" if critical else ""
            prompt += f"{critical_text} and dealt {damage} {damage_type}.\n"
            prompt += f"Target HP after the attack: {target_hp}.\n\n"
        else:
            prompt += ".\n\n"
        
        prompt += "Write a vivid, 2-4 sentence description of this combat moment."

        client = GPTClient()
        narrative = client.call(
            system_prompt="You are a fantasy combat narrator. Describe actions vividly with immersive prose.",
            user_prompt=prompt,
            temperature=0.9,
            max_tokens=150
        )
        
        logging.info(f"Generated narrative for {actor_name}'s action")
        return narrative
        
    except ImportError as e:
        logging.warning(f"GPT client not available: {e}")
        # Return a basic description
        return f"{actor_name} {hit_status} {action_details.get('target', 'target')} with {action_details.get('ability', 'an attack')}"
    except Exception as e:
        logging.error(f"Failed to generate narrative: {e}")
        raise RuntimeError(f"Narrative generation failed: {str(e)}") from e


def log_combat_event(combat_id: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log a combat event to the combat's history.
    
    Args:
        combat_id: ID of the combat
        event_data: Data about the combat event
        
    Returns:
        dict: The logged event with timestamp
        
    Raises:
        ValueError: If invalid parameters provided
    """
    # Input validation
    if not combat_id:
        raise ValueError("Combat ID cannot be empty")
    if not isinstance(event_data, dict):
        raise TypeError("Event data must be a dictionary")
    
    if not combat_config.get("logging.enable_combat_logging", True):
        return event_data  # Return without logging if disabled
    
    try:
        event = {
            **event_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add to in-memory log if available
        active_battles = combat_db_adapter.get_active_battles()
        if combat_id in active_battles:
            combat = active_battles[combat_id]
            if hasattr(combat, 'log'):
                combat.log.append(event)
                
                # Limit log size
                max_entries = combat_config.get("logging.max_log_entries", 1000)
                if len(combat.log) > max_entries:
                    combat.log = combat.log[-max_entries:]  # Keep only recent entries
        
        # Also log to database
        success = combat_db_adapter.update_combat_log(combat_id, [event])
        if not success:
            logging.warning(f"Failed to persist combat event to database for {combat_id}")
        
        logging.debug(f"Logged combat event for {combat_id}: {event_data.get('type', 'unknown')}")
        return event
        
    except Exception as e:
        logging.error(f"Failed to log combat event: {e}")
        # Still return the event even if logging fails
        return {**event_data, "timestamp": datetime.utcnow().isoformat()}


def log_combat_start(region_name: str, poi_id: str, participant_ids: list[str]) -> Dict[str, Any]:
    """
    Log the start of a combat to the POI's event log and participant memories.
    
    Args:
        region_name: Name of the region
        poi_id: ID of the POI
        participant_ids: IDs of the participants
        
    Returns:
        dict: The created combat event
        
    Raises:
        ValueError: If invalid parameters provided
    """
    # Input validation
    if not region_name or not poi_id:
        raise ValueError("Region name and POI ID cannot be empty")
    if not isinstance(participant_ids, list):
        raise TypeError("Participant IDs must be a list")
    if not participant_ids:
        raise ValueError("Participant IDs list cannot be empty")
    
    try:
        timestamp = datetime.utcnow().isoformat()
        combat_event = {
            "type": "combat_started",
            "day": timestamp,
            "participants": participant_ids,
            "region": region_name,
            "location": poi_id
        }

        # Log to POI event log
        success = combat_db_adapter.update_poi_event_log(region_name, poi_id, [combat_event])
        if not success:
            logging.warning(f"Failed to update POI event log for {region_name}/{poi_id}")

        # Add memories to NPCs
        npc_count = 0
        for pid in participant_ids:
            if pid.startswith("npc_"):
                try:
                    memory_entry = {
                        "interaction": f"Was present during combat at {poi_id} on {timestamp}",
                        "timestamp": timestamp
                    }
                    
                    # Try to update NPC memory
                    success = combat_db_adapter.update_npc_memory(pid, {
                        "rag_log": [memory_entry],
                        "summary": f"Participated in combat at {poi_id}"
                    })
                    
                    if success:
                        npc_count += 1
                    else:
                        logging.warning(f"Failed to update memory for NPC {pid}")
                        
                except Exception as e:
                    logging.error(f"Failed to update memory for NPC {pid}: {e}")
        
        logging.info(f"Logged combat start at {region_name}/{poi_id} with {len(participant_ids)} participants ({npc_count} NPCs)")
        return combat_event
        
    except Exception as e:
        logging.error(f"Failed to log combat start: {e}")
        raise RuntimeError(f"Failed to log combat start: {str(e)}") from e 