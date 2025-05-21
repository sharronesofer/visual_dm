"""
Quest-related utility functions.
Handles quest generation, management, and journal entries.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import random
import uuid
from dataclasses import dataclass, field

from app.quests.models.quest import Quest
from app.core.utils.firebase_utils import (
    get_firestore_client,
    get_document,
    set_document,
    update_document,
    get_collection
)
from app.core.utils.error_utils import ValidationError, NotFoundError, DatabaseError
# # # # from app.core.database import db

logger = logging.getLogger(__name__)

@dataclass
class QuestLogEntry:
    region: str
    poi: str
    summary: str
    tags: List[str]
    player_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def dict(self):
        return self.__dict__

# Quest Generation
def generate_quest_title(theme: str, difficulty: str) -> str:
    """Generate a quest title based on theme and difficulty."""
    try:
        themes = {
            'combat': ['Slay the', 'Defeat the', 'Conquer the', 'Vanquish the'],
            'exploration': ['Discover the', 'Find the', 'Explore the', 'Search for the'],
            'social': ['Convince the', 'Persuade the', 'Negotiate with the', 'Mediate between'],
            'mystery': ['Investigate the', 'Uncover the', 'Solve the', 'Decipher the']
        }
        
        difficulties = {
            'easy': ['Minor', 'Simple', 'Basic', 'Routine'],
            'medium': ['Moderate', 'Standard', 'Regular', 'Common'],
            'hard': ['Challenging', 'Difficult', 'Complex', 'Advanced'],
            'epic': ['Legendary', 'Mythic', 'Epic', 'Heroic']
        }
        
        theme_prefix = random.choice(themes.get(theme, ['Complete the']))
        difficulty_prefix = random.choice(difficulties.get(difficulty, ['']))
        
        return f"{difficulty_prefix} {theme_prefix} Quest"
    except Exception as e:
        logger.error(f"Error generating quest title: {str(e)}")
        raise DatabaseError(f"Failed to generate quest title: {str(e)}")

def generate_quest_steps(theme: str, difficulty: str) -> List[Dict[str, Any]]:
    """Generate quest steps based on theme and difficulty."""
    try:
        steps = []
        num_steps = {
            'easy': 3,
            'medium': 4,
            'hard': 5,
            'epic': 6
        }
        
        for i in range(num_steps.get(difficulty, 3)):
            step = {
                'id': i + 1,
                'description': f"Step {i + 1} for {theme} quest",
                'completed': False,
                'required_items': [],
                'required_skills': []
            }
            steps.append(step)
            
        return steps
    except Exception as e:
        logger.error(f"Error generating quest steps: {str(e)}")
        raise DatabaseError(f"Failed to generate quest steps: {str(e)}")

def calculate_quest_reward(difficulty: str, reward_type: str) -> Dict[str, Any]:
    """Calculate quest rewards based on difficulty and type."""
    try:
        reward_multipliers = {
            'easy': 1,
            'medium': 2,
            'hard': 3,
            'epic': 5
        }
        
        base_rewards = {
            'gold': 100,
            'experience': 200,
            'reputation': 50
        }
        
        multiplier = reward_multipliers.get(difficulty, 1)
        base_reward = base_rewards.get(reward_type, 0)
        
        return {
            'amount': base_reward * multiplier,
            'type': reward_type
        }
    except Exception as e:
        logger.error(f"Error calculating quest reward: {str(e)}")
        raise DatabaseError(f"Failed to calculate quest reward: {str(e)}")

# Quest Management
def validate_quest_data(data: Dict[str, Any]) -> bool:
    """Validate quest creation data."""
    try:
        required_fields = ['title', 'difficulty', 'reward_type', 'npc_id']
        valid_difficulties = ['easy', 'medium', 'hard', 'epic']
        valid_rewards = ['gold', 'item', 'experience', 'reputation']
        
        if not all(field in data for field in required_fields):
            raise ValidationError("Missing required fields")
            
        if data['difficulty'] not in valid_difficulties:
            raise ValidationError("Invalid difficulty level")
            
        if data['reward_type'] not in valid_rewards:
            raise ValidationError("Invalid reward type")
            
        return True
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error validating quest data: {str(e)}")
        raise DatabaseError(f"Failed to validate quest data: {str(e)}")

def update_quest_progress(quest_id: str, step_id: int) -> bool:
    """Update quest progress when a step is completed."""
    try:
        quest_data = get_document('quests', quest_id)
        if not quest_data:
            raise NotFoundError(f"Quest {quest_id} not found")
            
        steps = quest_data.get('steps', [])
        step_found = False
        
        for step in steps:
            if step['id'] == step_id:
                step['completed'] = True
                step_found = True
                break
                
        if not step_found:
            raise ValidationError(f"Step {step_id} not found in quest")
            
        update_document('quests', quest_id, {
            'steps': steps,
            'updated_at': datetime.utcnow().isoformat()
        })
        
        return True
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error updating quest progress: {str(e)}")
        raise DatabaseError(f"Failed to update quest progress: {str(e)}")

# Journal Management
def generate_journal_entry(quest_data: Dict[str, Any], player_id: str) -> QuestLogEntry:
    """Generate a journal entry for a quest."""
    try:
        return QuestLogEntry(
            region=quest_data.get('region', 'unknown'),
            poi=quest_data.get('poi', 'unknown'),
            summary=f"Started quest: {quest_data['title']}",
            tags=['quest', quest_data['difficulty'], quest_data['reward_type']],
            player_id=player_id
        )
    except Exception as e:
        logger.error(f"Error generating journal entry: {str(e)}")
        raise DatabaseError(f"Failed to generate journal entry: {str(e)}")

def save_journal_entry(entry: QuestLogEntry) -> bool:
    """Save a journal entry to the database."""
    try:
        set_document('journal', entry.id, entry.dict())
        return True
    except Exception as e:
        logger.error(f"Error saving journal entry: {str(e)}")
        raise DatabaseError(f"Failed to save journal entry: {str(e)}")

def get_player_journal_entries(player_id: str) -> List[QuestLogEntry]:
    """Get all journal entries for a player."""
    try:
        entries = get_collection('journal')
        return [
            QuestLogEntry(**entry)
            for entry in entries
            if entry.get('player_id') == player_id
        ]
    except Exception as e:
        logger.error(f"Error getting player journal entries: {str(e)}")
        raise DatabaseError(f"Failed to get player journal entries: {str(e)}")

# Player Arc Management
def load_player_arc(player_id: str) -> Optional[Dict[str, Any]]:
    """Load a player's story arc from the database."""
    try:
        arc_data = get_document('player_arcs', player_id)
        if not arc_data:
            return None
        return arc_data
    except Exception as e:
        logger.error(f"Error loading player arc: {str(e)}")
        raise DatabaseError(f"Failed to load player arc: {str(e)}")

def save_player_arc(player_id: str, arc_data: Dict[str, Any]) -> bool:
    """Save a player's story arc to the database."""
    try:
        set_document('player_arcs', player_id, {
            **arc_data,
            'updated_at': datetime.utcnow().isoformat()
        })
        return True
    except Exception as e:
        logger.error(f"Error saving player arc: {str(e)}")
        raise DatabaseError(f"Failed to save player arc: {str(e)}")

def create_player_arc(player_id: str) -> Dict[str, Any]:
    """Create a player story arc.
    
    Args:
        player_id: Player ID
        
    Returns:
        Story arc data
    """
    return {
        'player_id': player_id,
        'arc_type': 'main',
        'status': 'active',
        'completion': 0,
        'created_at': datetime.utcnow()
    }

def update_arc_with_event(player_id: str, event_data: Dict[str, Any]) -> bool:
    """Update a player's story arc with a new event."""
    try:
        arc_data = load_player_arc(player_id)
        if not arc_data:
            raise NotFoundError(f"Player arc not found for {player_id}")
            
        event_type = event_data.get('type')
        if event_type == 'quest_complete':
            arc_data['main_quest_line'].append(event_data)
        elif event_type == 'side_quest_complete':
            arc_data['side_quests'].append(event_data)
        elif event_type == 'major_choice':
            arc_data['major_choices'].append(event_data)
        elif event_type == 'relationship_change':
            faction_id = event_data.get('faction_id')
            arc_data['relationships'][faction_id] = event_data.get('value', 0)
            
        save_player_arc(player_id, arc_data)
        return True
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error updating arc with event: {str(e)}")
        raise DatabaseError(f"Failed to update arc with event: {str(e)}")

def trigger_war_arc(player_id: str, faction_id: str) -> Dict[str, Any]:
    """Trigger a war-related story arc for the player."""
    try:
        arc_data = load_player_arc(player_id)
        if not arc_data:
            raise NotFoundError(f"Player arc not found for {player_id}")
            
        war_arc = {
            'type': 'war',
            'faction_id': faction_id,
            'stage': 'beginning',
            'quests': [],
            'choices': [],
            'started_at': datetime.utcnow().isoformat()
        }
        
        arc_data['active_arcs'] = arc_data.get('active_arcs', [])
        arc_data['active_arcs'].append(war_arc)
        
        save_player_arc(player_id, arc_data)
        return war_arc
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error triggering war arc: {str(e)}")
        raise DatabaseError(f"Failed to trigger war arc: {str(e)}")

def generate_character_arc(player_id: str, background: str) -> Dict[str, Any]:
    """Generate a character story arc.
    
    Args:
        player_id: Player ID
        background: Character background
        
    Returns:
        Story arc data
    """
    # Choose a theme based on background
    theme = random.choice(['adventure', 'mystery', 'intrigue', 'exploration'])
    
    return {
        'player_id': player_id,
        'arc_type': 'character',
        'theme': theme,
        'background': background,
        'status': 'pending',
        'completion': 0,
        'created_at': datetime.utcnow()
    }

def npc_personal_quest_tick(npc_id: str) -> Optional[Dict[str, Any]]:
    """Generate personal quests for NPCs based on their current state."""
    try:
        npc_data = get_document('npcs', npc_id)
        if not npc_data:
            raise NotFoundError(f"NPC {npc_id} not found")
            
        # Check if NPC should generate a personal quest
        if random.random() < 0.1:  # 10% chance per tick
            quest_data = {
                'id': str(uuid.uuid4()),
                'title': f"{npc_data['name']}'s Personal Quest",
                'type': 'personal',
                'npc_id': npc_id,
                'difficulty': random.choice(['easy', 'medium', 'hard']),
                'reward_type': random.choice(['gold', 'item', 'reputation']),
                'created_at': datetime.utcnow().isoformat()
            }
            
            set_document('quests', quest_data['id'], quest_data)
            return quest_data
            
        return None
    except (NotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error in NPC quest tick: {str(e)}")
        raise DatabaseError(f"Failed in NPC quest tick: {str(e)}")

class QuestUtils:
    """Core quest functionality utilities."""
    
    @staticmethod
    def create_quest(data: Dict[str, Any]) -> str:
        """Create a new quest in the database.
        
        Args:
            data: Quest data dictionary
            
        Returns:
            str: The ID of the created quest
            
        Raises:
            DatabaseError: If quest creation fails
        """
        try:
            quest_ref = db.collection('quests').document()
            quest_ref.set(data)
            return quest_ref.id
        except Exception as e:
            raise DatabaseError(f"Failed to create quest: {str(e)}")
            
    @staticmethod
    def get_quest(quest_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a quest from the database.
        
        Args:
            quest_id: The ID of the quest to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Quest data if found, None otherwise
            
        Raises:
            DatabaseError: If quest retrieval fails
        """
        try:
            quest = db.collection('quests').document(quest_id).get()
            return quest.to_dict() if quest.exists else None
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve quest: {str(e)}")
            
    @staticmethod
    def update_quest_progress(quest_id: str, step_id: int) -> bool:
        """Update a quest's progress to a new step.
        
        Args:
            quest_id: The ID of the quest to update
            step_id: The ID of the step to progress to
            
        Returns:
            bool: True if update successful, False if quest not found
            
        Raises:
            DatabaseError: If quest update fails
        """
        try:
            quest_ref = db.collection('quests').document(quest_id)
            quest = quest_ref.get()
            
            if not quest.exists:
                return False
                
            quest_ref.update({
                'current_step': step_id,
                'last_updated': db.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            raise DatabaseError(f"Failed to update quest progress: {str(e)}")
            
    @staticmethod
    def create_journal_entry(data: Dict[str, Any]) -> str:
        """Create a new journal entry.
        
        Args:
            data: Journal entry data dictionary
            
        Returns:
            str: The ID of the created journal entry
            
        Raises:
            DatabaseError: If journal entry creation fails
        """
        try:
            journal_ref = db.collection('journal_entries').document()
            journal_ref.set(data)
            return journal_ref.id
        except Exception as e:
            raise DatabaseError(f"Failed to create journal entry: {str(e)}")
            
    @staticmethod
    def get_player_journal_entries(player_id: str) -> List[Dict[str, Any]]:
        """Retrieve all journal entries for a player.
        
        Args:
            player_id: The ID of the player
            
        Returns:
            List[Dict[str, Any]]: List of journal entries
            
        Raises:
            DatabaseError: If journal entries retrieval fails
        """
        try:
            entries = db.collection('journal_entries').where('player_id', '==', player_id).get()
            return [entry.to_dict() for entry in entries]
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve journal entries: {str(e)}")
            
    @staticmethod
    def is_valid_step(quest_data: Dict[str, Any], step_id: int) -> bool:
        """Check if a step ID is valid for a quest.
        
        Args:
            quest_data: The quest data dictionary
            step_id: The step ID to validate
            
        Returns:
            bool: True if step is valid, False otherwise
        """
        if 'steps' not in quest_data:
            return False
            
        return any(step['id'] == step_id for step in quest_data['steps'])

__all__ = [
    'generate_quest_title',
    'generate_quest_steps',
    'calculate_quest_reward',
    'validate_quest_data',
    'update_quest_progress',
    'generate_journal_entry',
    'save_journal_entry',
    'get_player_journal_entries',
    'load_player_arc',
    'save_player_arc',
    'create_player_arc',
    'update_arc_with_event',
    'trigger_war_arc',
    'generate_character_arc',
    'npc_personal_quest_tick'
] 
