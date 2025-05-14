"""
Arc-related utility functions.
Handles character arc generation, progress tracking, and persistence.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from .arc_models import PlayerArc

# In-memory storage for arcs
arcs_db = {}

def generate_arc_stages(theme: str) -> List[Dict]:
    """
    Generate stages for a character arc based on theme.
    
    Args:
        theme: The theme of the arc
    
    Returns:
        List[Dict]: The generated stages
    """
    stage_templates = {
        'redemption': [
            {'id': 1, 'title': 'The Fall', 'description': 'Character faces their darkest moment'},
            {'id': 2, 'title': 'The Awakening', 'description': 'Character realizes the need for change'},
            {'id': 3, 'title': 'The Struggle', 'description': 'Character works to overcome their past'},
            {'id': 4, 'title': 'The Redemption', 'description': 'Character achieves redemption'}
        ],
        'betrayal': [
            {'id': 1, 'title': 'Trust', 'description': 'Character forms a close bond'},
            {'id': 2, 'title': 'Doubt', 'description': 'Signs of betrayal begin to appear'},
            {'id': 3, 'title': 'Revelation', 'description': 'The betrayal is revealed'},
            {'id': 4, 'title': 'Consequences', 'description': 'Character deals with the aftermath'}
        ],
        'power': [
            {'id': 1, 'title': 'Potential', 'description': 'Character discovers their power'},
            {'id': 2, 'title': 'Training', 'description': 'Character learns to control their power'},
            {'id': 3, 'title': 'Temptation', 'description': 'Character faces the temptation of power'},
            {'id': 4, 'title': 'Mastery', 'description': 'Character achieves mastery over their power'}
        ]
    }
    
    return stage_templates.get(theme, stage_templates['redemption'])

def create_arc(character_id: str, theme: str) -> PlayerArc:
    """
    Create a new character arc.
    
    Args:
        character_id: The ID of the character
        theme: The theme of the arc
    
    Returns:
        PlayerArc: The created arc
    """
    stages = generate_arc_stages(theme)
    arc = PlayerArc(
        character_id=character_id,
        title=f"{theme.title()} Arc",
        theme=theme,
        current_stage=1,
        total_stages=len(stages),
        completed_stages=[],
        stages=stages
    )
    
    return arc

def update_arc_progress(arc_id: str, stage_id: int) -> bool:
    """
    Update arc progress when a stage is completed.
    
    Args:
        arc_id: The ID of the arc
        stage_id: The ID of the completed stage
    
    Returns:
        bool: True if the update was successful, False otherwise
    """
    try:
        arc = arcs_db.get(arc_id)
        if not arc:
            return False
            
        if stage_id not in arc.completed_stages:
            arc.completed_stages.append(stage_id)
            
        arc.current_stage = stage_id + 1 if stage_id < arc.total_stages else stage_id
        arc.updated_at = datetime.utcnow()
        
        arcs_db[arc_id] = arc
        return True
    except Exception:
        return False

def load_arc_from_firebase(arc_id: str) -> Optional[PlayerArc]:
    """
    Load a character arc from storage.
    
    Args:
        arc_id: The ID of the arc
    
    Returns:
        Optional[PlayerArc]: The loaded arc, or None if not found
    """
    return arcs_db.get(arc_id)

def save_arc_to_firebase(arc: PlayerArc) -> bool:
    """
    Save a character arc to storage.
    
    Args:
        arc: The arc to save
    
    Returns:
        bool: True if the save was successful, False otherwise
    """
    try:
        if not arc.id:
            arc.id = str(uuid.uuid4())
            
        arcs_db[arc.id] = arc
        return True
    except Exception:
        return False 