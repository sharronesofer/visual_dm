from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime
import random

class RelationshipStatus(Enum):
    HOSTILE = -2
    UNFRIENDLY = -1
    NEUTRAL = 0
    FRIENDLY = 1
    ALLIED = 2

class SocialInteractionType(Enum):
    PERSUASION = "persuasion"
    INTIMIDATION = "intimidation"
    DECEPTION = "deception"
    PERFORMANCE = "performance"
    INSIGHT = "insight"

def calculate_relationship_change(
    interaction_type: SocialInteractionType,
    success: bool,
    current_status: RelationshipStatus,
    modifiers: Dict[str, float] = None
) -> int:
    """Calculate relationship change based on interaction."""
    base_change = 1 if success else -1
    modifiers = modifiers or {}
    
    # Apply modifiers
    for modifier, value in modifiers.items():
        base_change *= value
    
    # Limit change based on current status
    if current_status == RelationshipStatus.ALLIED and base_change > 0:
        return 0
    if current_status == RelationshipStatus.HOSTILE and base_change < 0:
        return 0
        
    return base_change

def process_social_interaction(
    character_stats: Dict,
    npc_stats: Dict,
    interaction_type: SocialInteractionType,
    difficulty_class: int
) -> Tuple[bool, str]:
    """Process a social interaction attempt."""
    # Get relevant skill modifier
    skill_mod = character_stats.get(f"{interaction_type.value}_modifier", 0)
    
    # Roll check
    from random import randint
    roll = randint(1, 20)
    total = roll + skill_mod
    
    success = total >= difficulty_class
    
    # Generate response message
    if success:
        return True, f"Success! Roll: {roll} + {skill_mod} = {total} vs DC {difficulty_class}"
    else:
        return False, f"Failure. Roll: {roll} + {skill_mod} = {total} vs DC {difficulty_class}"

def update_npc_disposition(
    npc_id: str,
    change: int,
    current_disposition: Dict[str, any]
) -> Dict[str, any]:
    """Update NPC's disposition towards the player."""
    new_disposition = current_disposition.copy()
    new_disposition['value'] = max(
        RelationshipStatus.HOSTILE.value,
        min(RelationshipStatus.ALLIED.value,
            current_disposition.get('value', 0) + change
        )
    )
    return new_disposition

def calculate_social_status(
    character_stats: Dict,
    location: Dict,
    modifiers: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Calculate a character's social status in a given location."""
    base_status = 0
    modifiers = modifiers or {}
    
    # Base status from character attributes
    charisma_mod = (character_stats.get("CHA", 10) - 10) // 2
    base_status += charisma_mod * 2
    
    # Modify based on character class and background
    class_name = character_stats.get("class", "").lower()
    if class_name in ["noble", "paladin", "bard"]:
        base_status += 2
    
    background = character_stats.get("background", "").lower()
    if background in ["noble", "guild_artisan", "sage"]:
        base_status += 1
    
    # Location-based modifiers
    if location.get("type") == "city":
        if character_stats.get("race") == location.get("dominant_race"):
            base_status += 1
    
    # Apply custom modifiers
    for key, value in modifiers.items():
        base_status += value
    
    # Calculate final status level
    if base_status >= 5:
        status_level = "respected"
    elif base_status >= 2:
        status_level = "accepted"
    elif base_status >= -1:
        status_level = "neutral"
    elif base_status >= -4:
        status_level = "suspicious"
    else:
        status_level = "unwelcome"
    
    return {
        "status_level": status_level,
        "base_score": base_status,
        "modifiers": modifiers,
        "location_effects": {
            "race_bonus": character_stats.get("race") == location.get("dominant_race"),
            "class_bonus": class_name in ["noble", "paladin", "bard"],
            "background_bonus": background in ["noble", "guild_artisan", "sage"]
        }
    }

def update_relationship(
    character_id: str,
    npc_id: str,
    change: int,
    reason: str
) -> Dict[str, Any]:
    """
    Update the relationship between a character and an NPC.
    
    Args:
        character_id: ID of the character
        npc_id: ID of the NPC
        change: Amount to change the relationship (-5 to +5)
        reason: Reason for the change
        
    Returns:
        Dict containing updated relationship data
    """
    try:
        # Get current relationship
        ref = db.reference(f"/relationships/{character_id}/{npc_id}")
        relationship = ref.get() or {
            "value": 0,
            "history": [],
            "last_interaction": None
        }
        
        # Apply change
        new_value = max(-10, min(10, relationship["value"] + change))
        
        # Record interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "change": change,
            "reason": reason,
            "old_value": relationship["value"],
            "new_value": new_value
        }
        
        # Update relationship
        relationship["value"] = new_value
        relationship["history"].append(interaction)
        relationship["last_interaction"] = interaction["timestamp"]
        
        # Save changes
        ref.set(relationship)
        
        return relationship
        
    except Exception as e:
        print(f"Error updating relationship: {e}")
        return None

def generate_social_event(character_id: str, location_id: str) -> Dict[str, Any]:
    """
    Generate a social event for a character at a given location.
    
    Args:
        character_id: ID of the character initiating the event
        location_id: ID of the location where the event occurs
        
    Returns:
        Dict containing event details including type, participants, and outcome
    """
    event_types = [
        "conversation",
        "trade",
        "quest_offer",
        "rumor_sharing",
        "challenge",
        "celebration"
    ]
    
    event_type = random.choice(event_types)
    timestamp = datetime.utcnow().isoformat()
    
    event = {
        "type": event_type,
        "initiator_id": character_id,
        "location_id": location_id,
        "timestamp": timestamp,
        "status": "pending",
        "participants": [character_id],
        "outcome": None
    }
    
    # Add event-specific details based on type
    if event_type == "conversation":
        event["topic"] = random.choice([
            "local_news",
            "world_events",
            "personal_story",
            "advice_seeking",
            "gossip"
        ])
    elif event_type == "trade":
        event["trade_type"] = random.choice([
            "goods",
            "information",
            "services"
        ])
    elif event_type == "quest_offer":
        event["quest_difficulty"] = random.choice([
            "easy",
            "medium",
            "hard"
        ])
    
    return event

def handle_gossip(character_id: str, npc_id: str, topic: str) -> Dict[str, Any]:
    """
    Handle gossip interaction between a character and NPC.
    
    Args:
        character_id: ID of the character
        npc_id: ID of the NPC
        topic: Topic of the gossip
        
    Returns:
        Dict containing interaction results
    """
    try:
        # Get character and NPC data
        char_ref = db.reference(f"/characters/{character_id}")
        npc_ref = db.reference(f"/npcs/{npc_id}")
        
        character = char_ref.get()
        npc = npc_ref.get()
        
        if not character or not npc:
            return {"success": False, "message": "Character or NPC not found"}
            
        # Calculate success chance based on charisma
        charisma_mod = (character.get("CHA", 10) - 10) // 2
        success_chance = 0.5 + (charisma_mod * 0.05)
        
        # Roll for success
        success = random.random() < success_chance
        
        # Generate response
        if success:
            # Get random piece of information
            info = random.choice([
                "local_news",
                "quest_hint",
                "character_rumor",
                "location_secret"
            ])
            
            return {
                "success": True,
                "message": f"Successfully shared gossip about {topic}",
                "information_gained": info,
                "relationship_change": 1
            }
        else:
            return {
                "success": False,
                "message": f"Failed to share gossip about {topic}",
                "relationship_change": -1
            }
            
    except Exception as e:
        print(f"Error handling gossip: {e}")
        return {"success": False, "message": "Error processing gossip"}

def process_faction_influence(
    faction_id: str,
    region_id: str,
    action_type: str,
    magnitude: int = 1
) -> Dict[str, Any]:
    """
    Process changes in faction influence in a region.
    
    Args:
        faction_id: ID of the faction
        region_id: ID of the region
        action_type: Type of influence action
        magnitude: Magnitude of the influence change
        
    Returns:
        Dict containing updated influence data
    """
    try:
        # Get faction and region data
        faction_ref = db.reference(f"/factions/{faction_id}")
        region_ref = db.reference(f"/regions/{region_id}")
        
        faction = faction_ref.get()
        region = region_ref.get()
        
        if not faction or not region:
            return {
                "success": False,
                "message": "Faction or region not found"
            }
            
        # Get current influence
        influence_ref = db.reference(f"/faction_influence/{region_id}/{faction_id}")
        current_influence = influence_ref.get() or {
            "value": 0,
            "history": [],
            "controlled_locations": []
        }
        
        # Calculate influence change
        base_change = magnitude
        if action_type == "quest_completion":
            base_change *= 2
        elif action_type == "trade_agreement":
            base_change *= 1.5
        elif action_type == "hostile_action":
            base_change *= -2
            
        # Apply change
        new_value = max(-100, min(100, current_influence["value"] + base_change))
        
        # Record change
        change_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "old_value": current_influence["value"],
            "new_value": new_value,
            "change": base_change
        }
        
        # Update influence data
        current_influence["value"] = new_value
        current_influence["history"].append(change_record)
        
        # Check for control changes
        if new_value >= 75:
            # Add any uncontrolled locations to faction control
            for location in region.get("locations", []):
                if location not in current_influence["controlled_locations"]:
                    current_influence["controlled_locations"].append(location)
        elif new_value <= -75:
            # Remove all controlled locations
            current_influence["controlled_locations"] = []
            
        # Save changes
        influence_ref.set(current_influence)
        
        return {
            "success": True,
            "influence": current_influence,
            "change": change_record
        }
        
    except Exception as e:
        print(f"Error processing faction influence: {e}")
        return {
            "success": False,
            "message": "Error processing influence change"
        } 