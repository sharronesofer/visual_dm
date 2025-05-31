"""
Combat narrative utilities for the Visual DM combat system.

This module provides storytelling and narrative generation for combat events,
including AI-powered descriptions, character dialogue, and combat logs.
"""

import json
from datetime import datetime
# from firebase_admin import db  # TODO: Replace with proper database integration

def narrate_action(actor_name, action_details, outcome):
    """
    Generate a narrative description of a combat action using AI.
    
    Args:
        actor_name: Name of the actor performing the action
        action_details: Details of the action (ability, target, etc.)
        outcome: Result of the action (hit, damage, etc.)
        
    Returns:
        str: Narrative description of the combat action
    """
    from backend.infrastructure.llm.core.gpt_client import GPTClient
    
    prompt = (
        f"{actor_name} used {action_details.get('ability', 'an action')} on {action_details.get('target')}.\n"
        f"The attack {'hit' if outcome.get('hit') else 'missed'} and dealt {outcome.get('damage', 0)} "
        f"{outcome.get('damage_type', 'damage')}.\n"
        f"Target HP after the attack: {outcome.get('target_hp', '?')}.\n\n"
        "Write a vivid, 2-4 sentence description of this combat moment."
    )

    client = GPTClient()
    return client.call(
        system_prompt="You are a fantasy combat narrator. Describe actions vividly with immersive prose.",
        user_prompt=prompt,
        temperature=0.9,
        max_tokens=150
    )

def log_combat_event(combat_id, event_data):
    """
    Log a combat event to the combat's history.
    
    Args:
        combat_id: ID of the combat
        event_data: Data about the combat event
        
    Returns:
        dict: The logged event with timestamp
    """
    event = {
        **event_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add to in-memory log if using RAM
    from backend.systems.combat.utils.combat_ram import ACTIVE_BATTLES
    if combat_id in ACTIVE_BATTLES:
        combat = ACTIVE_BATTLES[combat_id]
        combat.log.append(event)
    
    # Also log to Firebase
    combat_ref = db.reference(f"/combat_state/{combat_id}/log")
    combat_log = combat_ref.get() or []
    combat_log.append(event)
    combat_ref.set(combat_log)
    
    return event

def log_combat_start(region_name, poi_id, participant_ids):
    """
    Log the start of a combat to the POI's event log and participant memories.
    
    Args:
        region_name: Name of the region
        poi_id: ID of the POI
        participant_ids: IDs of the participants
        
    Returns:
        dict: The created combat event
    """
    timestamp = datetime.utcnow().isoformat()
    combat_event = {
        "type": "combat_started",
        "day": timestamp,
        "participants": participant_ids
    }

    # Log to POI event log
    poi_ref = db.reference(f"/poi_state/{region_name}/{poi_id}/event_log")
    poi_log = poi_ref.get() or []
    poi_log.append(combat_event)
    poi_ref.set(poi_log)

    # Add memories to NPCs
    for pid in participant_ids:
        if pid.startswith("npc_"):
            mem_ref = db.reference(f"/npc_memory/{pid}")
            memory = mem_ref.get() or {"rag_log": [], "summary": ""}
            memory["rag_log"].append({
                "interaction": f"Was present during combat at {poi_id} on {timestamp}",
                "timestamp": timestamp
            })
            mem_ref.set(memory)
            
    return combat_event

def format_combat_summary(combat_state):
    """
    Generate a human-readable summary of a combat.
    
    Args:
        combat_state: The full combat state
        
    Returns:
        str: A formatted summary of the combat
    """
    summary = []
    summary.append(f"Combat: {combat_state.get('name', 'Unnamed Battle')}")
    summary.append(f"Round: {combat_state.get('round', 1)}")
    
    # Party summary
    party = combat_state.get('party', [])
    if party:
        summary.append("\nParty:")
        for character in party:
            hp = character.get('current_hp', 0)
            max_hp = character.get('max_hp', 0)
            summary.append(f"  {character.get('name', 'Unknown')}: {hp}/{max_hp} HP")
    
    # Enemy summary
    enemies = combat_state.get('enemies', [])
    if enemies:
        summary.append("\nEnemies:")
        for enemy in enemies:
            hp = enemy.get('current_hp', 0)
            max_hp = enemy.get('max_hp', 0)
            summary.append(f"  {enemy.get('name', 'Unknown')}: {hp}/{max_hp} HP")
    
    # Recent log entries (last 3)
    log = combat_state.get('log', [])
    if log:
        summary.append("\nRecent Events:")
        for entry in log[-3:]:
            summary.append(f"  {entry}")
    
    return "\n".join(summary) 