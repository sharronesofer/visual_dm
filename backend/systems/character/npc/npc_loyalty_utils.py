from app.core.models.character import Character
from app.core.models.party import Party
import random
from datetime import datetime
from app.models.npc import NPC
# # # # from app.core.database import db

def should_abandon(npc: Character, party: Party) -> bool:
    """
    Determines if an NPC should abandon their party based on various factors.
    
    Args:
        npc (Character): The NPC character
        party (Party): The party they're in
        
    Returns:
        bool: True if the NPC should abandon the party, False otherwise
    """
    # Base chance of abandonment
    base_chance = 0.1  # 10% base chance
    
    # Adjust based on NPC's loyalty trait if it exists
    loyalty_modifier = 0
    if hasattr(npc, 'traits') and 'loyalty' in npc.traits:
        loyalty_modifier = (npc.traits['loyalty'] - 5) * 0.05  # Scale loyalty from 1-10 to -0.2 to 0.2
    
    # Adjust based on party size (smaller parties are more likely to be abandoned)
    size_modifier = (10 - len(party.members)) * 0.02  # 2% per missing member
    
    # Adjust based on time in party (longer time = less likely to abandon)
    time_modifier = 0
    if hasattr(npc, 'joined_party_at'):
        days_in_party = (datetime.utcnow() - npc.joined_party_at).days
        time_modifier = -min(days_in_party * 0.01, 0.2)  # Up to 20% reduction
    
    # Calculate final chance
    final_chance = max(0, min(1, base_chance + loyalty_modifier + size_modifier + time_modifier))
    
    # Roll the dice
    return random.random() < final_chance 

def calculate_loyalty_change(npc_id, action_type, magnitude=1):
    """Calculate loyalty changes based on player actions."""
    try:
        npc = NPC.query.get(npc_id)
        if not npc:
            return None
            
        base_changes = {
            'gift': 5,
            'help': 10,
            'betray': -15,
            'attack': -20
        }
        
        change = base_changes.get(action_type, 0) * magnitude
        return change
        
    except Exception as e:
        print(f"Error calculating loyalty: {str(e)}")
        return None

def update_npc_loyalty(npc_id, loyalty_change):
    """Update an NPC's loyalty score."""
    try:
        npc = NPC.query.get(npc_id)
        if not npc:
            return False
            
        new_loyalty = max(0, min(100, npc.loyalty + loyalty_change))
        npc.loyalty = new_loyalty
        npc.last_loyalty_update = datetime.utcnow()
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating loyalty: {str(e)}")
        return False 