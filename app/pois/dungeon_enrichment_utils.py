"""Utility functions for enriching dungeon content with additional features and details."""

import random
from datetime import datetime
from app.models.poi import POI
from app.core.database import db

def enrich_dungeon_room(room_data):
    """Add additional details and features to a dungeon room."""
    if not room_data:
        return None
        
    # Add atmospheric details
    room_data['atmosphere'] = generate_atmosphere()
    
    # Add random features
    room_data['features'] = generate_room_features()
    
    # Add potential encounters
    room_data['encounters'] = generate_potential_encounters()
    
    return room_data

def generate_atmosphere():
    """Generate atmospheric details for a room."""
    lighting = ['dim', 'dark', 'bright', 'flickering']
    sounds = ['dripping water', 'distant echoes', 'creaking', 'silence']
    smells = ['musty', 'damp', 'stale', 'earthy']
    
    return {
        'lighting': random.choice(lighting),
        'sounds': random.choice(sounds),
        'smells': random.choice(smells)
    }

def generate_room_features():
    """Generate random features for a room."""
    features = []
    
    possible_features = [
        'cobwebs', 'cracks in walls', 'ancient markings',
        'broken furniture', 'scattered debris', 'mysterious symbols',
        'old bloodstains', 'discarded equipment', 'strange fungi'
    ]
    
    # Add 1-3 random features
    num_features = random.randint(1, 3)
    features = random.sample(possible_features, num_features)
    
    return features

def generate_potential_encounters():
    """Generate potential encounters for a room."""
    encounter_types = ['combat', 'trap', 'puzzle', 'roleplay']
    
    # 30% chance for an encounter
    if random.random() < 0.3:
        return {
            'type': random.choice(encounter_types),
            'difficulty': random.randint(1, 5),
            'reward_tier': random.randint(1, 3)
        }
    
    return None

def update_dungeon_state(dungeon_id, new_state):
    """Update the state of a dungeon POI."""
    try:
        dungeon = POI.query.get(dungeon_id)
        if not dungeon:
            return False
            
        dungeon.state = new_state
        dungeon.last_updated = datetime.utcnow()
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating dungeon state: {str(e)}")
        return False 