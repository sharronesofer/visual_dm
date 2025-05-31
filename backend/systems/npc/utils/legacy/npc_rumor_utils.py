"""Utility functions for handling NPC rumors and gossip mechanics."""

import random
from datetime import datetime
from app.models.npc import NPC
# # # # from app.core.database import db

def generate_rumor(npc_id, topic=None):
    """Generate a rumor from an NPC based on their knowledge and relationships."""
    try:
        npc = NPC.query.get(npc_id)
        if not npc:
            return None
            
        # Basic rumor templates
        rumor_templates = [
            "I heard that {target} was seen {action} near {location}...",
            "They say {target} has been {action} lately...",
            "Word is that {target} might be involved with {action}..."
        ]
        
        # Placeholder data - in real implementation, would pull from game state
        targets = ["the merchant", "the guard captain", "the mysterious stranger"]
        actions = ["meeting suspicious characters", "acting strangely", "hiding something"]
        locations = ["the tavern", "the docks", "the old temple"]
        
        rumor = random.choice(rumor_templates).format(
            target=random.choice(targets),
            action=random.choice(actions),
            location=random.choice(locations)
        )
        
        return {
            'content': rumor,
            'source_npc': npc_id,
            'timestamp': datetime.utcnow(),
            'reliability': random.random()  # 0-1 scale of rumor reliability
        }
        
    except Exception as e:
        print(f"Error generating rumor: {str(e)}")
        return None

def spread_rumor(rumor_data, target_npcs):
    """Spread a rumor to other NPCs in the area."""
    try:
        for target_id in target_npcs:
            npc = NPC.query.get(target_id)
            if not npc:
                continue
                
            # Add rumor to NPC's knowledge
            if not hasattr(npc, 'known_rumors'):
                npc.known_rumors = []
            
            npc.known_rumors.append(rumor_data)
            npc.last_rumor_update = datetime.utcnow()
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error spreading rumor: {str(e)}")
        return False 