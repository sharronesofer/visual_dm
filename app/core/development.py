"""
Development system for managing character progression and skill development.
"""

from typing import Dict, List, Optional
from datetime import datetime
import random
from firebase_admin import firestore

class DevelopmentSystem:
    def __init__(self, app):
        self.app = app
        self.db = firestore.client()
        self.development_collection = self.db.collection('character_development')
        
    def get_character_development(self, character_id: str) -> Optional[Dict]:
        """Get character development data."""
        dev_doc = self.development_collection.document(character_id).get()
        if not dev_doc.exists:
            return None
            
        return dev_doc.to_dict()
        
    def initialize_development(self, character_id: str) -> None:
        """Initialize development tracking for a new character."""
        development_data = {
            'character_id': character_id,
            'level': 1,
            'experience': 0,
            'skill_points': 0,
            'abilities': {},
            'skills': {
                'combat': 1,
                'magic': 1,
                'stealth': 1,
                'social': 1
            },
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self.development_collection.document(character_id).set(development_data)
        
    def add_experience(self, character_id: str, amount: int) -> Dict:
        """Add experience points to a character."""
        dev_data = self.get_character_development(character_id)
        if not dev_data:
            self.initialize_development(character_id)
            dev_data = self.get_character_development(character_id)
            
        current_xp = dev_data['experience']
        new_xp = current_xp + amount
        
        # Check for level up
        level_ups = 0
        while new_xp >= self._xp_for_next_level(dev_data['level']):
            level_ups += 1
            new_xp -= self._xp_for_next_level(dev_data['level'])
            dev_data['level'] += 1
            dev_data['skill_points'] += 2
            
        dev_data['experience'] = new_xp
        dev_data['updated_at'] = datetime.utcnow().isoformat()
        
        self.development_collection.document(character_id).update(dev_data)
        
        return {
            'success': True,
            'level_ups': level_ups,
            'new_level': dev_data['level'],
            'new_xp': new_xp,
            'skill_points': dev_data['skill_points']
        }
        
    def improve_skill(self, character_id: str, skill: str, points: int = 1) -> Dict:
        """Improve a character skill using skill points."""
        dev_data = self.get_character_development(character_id)
        if not dev_data:
            return {'success': False, 'message': 'Character development not found'}
            
        if dev_data['skill_points'] < points:
            return {'success': False, 'message': 'Not enough skill points'}
            
        if skill not in dev_data['skills']:
            return {'success': False, 'message': 'Invalid skill'}
            
        dev_data['skills'][skill] += points
        dev_data['skill_points'] -= points
        dev_data['updated_at'] = datetime.utcnow().isoformat()
        
        self.development_collection.document(character_id).update(dev_data)
        
        return {
            'success': True,
            'new_skill_level': dev_data['skills'][skill],
            'remaining_points': dev_data['skill_points']
        }
        
    def unlock_ability(self, character_id: str, ability: str) -> Dict:
        """Unlock a new ability for a character."""
        dev_data = self.get_character_development(character_id)
        if not dev_data:
            return {'success': False, 'message': 'Character development not found'}
            
        if ability in dev_data['abilities']:
            return {'success': False, 'message': 'Ability already unlocked'}
            
        # Check prerequisites
        ability_data = self._get_ability_data(ability)
        if not ability_data:
            return {'success': False, 'message': 'Invalid ability'}
            
        if dev_data['level'] < ability_data.get('required_level', 1):
            return {'success': False, 'message': 'Level requirement not met'}
            
        dev_data['abilities'][ability] = {
            'unlocked_at': datetime.utcnow().isoformat(),
            'level': 1
        }
        
        self.development_collection.document(character_id).update(dev_data)
        
        return {
            'success': True,
            'ability': ability,
            'ability_data': ability_data
        }
        
    def _xp_for_next_level(self, current_level: int) -> int:
        """Calculate XP needed for next level."""
        return int(100 * (current_level ** 1.5))
        
    def _get_ability_data(self, ability: str) -> Optional[Dict]:
        """Get data for an ability."""
        # This would typically load from a config file
        abilities = {
            'double_strike': {
                'name': 'Double Strike',
                'description': 'Attack twice in one turn',
                'required_level': 3,
                'cooldown': 3
            },
            'healing_touch': {
                'name': 'Healing Touch',
                'description': 'Restore health to target',
                'required_level': 2,
                'cooldown': 4
            }
        }
        return abilities.get(ability)

# Global development system instance
development_system = None

def init_development_system(app) -> None:
    """Initialize the development system."""
    global development_system
    development_system = DevelopmentSystem(app) 