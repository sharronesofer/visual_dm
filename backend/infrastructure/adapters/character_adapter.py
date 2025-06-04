"""
Character Service Adapter for Magic System

Provides character abilities and data for the magic system without circular imports.
Uses direct database queries instead of importing character models.
"""

from typing import Dict, Any, Optional, Protocol
from sqlalchemy.orm import Session
from sqlalchemy import text

class CharacterAbilities(Protocol):
    """Protocol for character abilities expected by magic system"""
    
    def get_ability_modifier(self, ability_name: str) -> int:
        """Get ability modifier for given ability"""
        ...

class MockCharacterAbilities:
    """Mock implementation of character abilities for magic system"""
    
    def __init__(self, abilities: Dict[str, int] = None):
        # Default ability scores (10 = +0 modifier)
        self.abilities = abilities or {
            'strength': 10,
            'dexterity': 10, 
            'constitution': 10,
            'intelligence': 14,  # +2 modifier
            'wisdom': 12,       # +1 modifier
            'charisma': 10
        }
    
    def get_ability_modifier(self, ability_name: str) -> int:
        """Calculate ability modifier from ability score"""
        score = self.abilities.get(ability_name.lower(), 10)
        return (score - 10) // 2

class DatabaseCharacterService:
    """Character service using direct database queries"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_character_abilities(self, character_id: int) -> Optional[CharacterAbilities]:
        """Get character abilities from database without importing character models"""
        try:
            # Try to get character data from database
            result = self.db.execute(text("""
                SELECT * FROM characters WHERE id = :character_id
            """), {'character_id': character_id})
            
            character_data = result.fetchone()
            if not character_data:
                return None
            
            # Extract ability scores if available in the character data
            # This is a simplified version that may need adjustment based on actual schema
            abilities = {}
            
            # Try to get abilities from character data
            # If the character table has ability columns, use them
            if hasattr(character_data, 'strength'):
                abilities['strength'] = character_data.strength
            if hasattr(character_data, 'dexterity'):
                abilities['dexterity'] = character_data.dexterity
            if hasattr(character_data, 'constitution'):
                abilities['constitution'] = character_data.constitution
            if hasattr(character_data, 'intelligence'):
                abilities['intelligence'] = character_data.intelligence
            if hasattr(character_data, 'wisdom'):
                abilities['wisdom'] = character_data.wisdom
            if hasattr(character_data, 'charisma'):
                abilities['charisma'] = character_data.charisma
            
            # If no abilities found, use defaults based on character level/class
            if not abilities:
                # For testing, assign reasonable default abilities
                abilities = {
                    'strength': 12,
                    'dexterity': 14,
                    'constitution': 13,
                    'intelligence': 15,  # Good for arcane casting
                    'wisdom': 14,       # Good for divine casting  
                    'charisma': 12      # Good for occult casting
                }
            
            return MockCharacterAbilities(abilities)
            
        except Exception as e:
            # If database query fails, return default abilities
            print(f"Warning: Could not get character abilities for {character_id}: {e}")
            return MockCharacterAbilities()
    
    def get_proficiency_bonus(self, character_id: int) -> int:
        """Get character's proficiency bonus"""
        try:
            # Try to calculate from character level
            result = self.db.execute(text("""
                SELECT level FROM characters WHERE id = :character_id
            """), {'character_id': character_id})
            
            character_data = result.fetchone()
            if character_data and hasattr(character_data, 'level'):
                level = character_data.level
                # Standard D&D proficiency bonus calculation
                return 2 + ((level - 1) // 4)
            else:
                # Default proficiency bonus for mid-level character
                return 3
                
        except Exception:
            # Default proficiency bonus
            return 3

def create_character_service(db_session: Session) -> DatabaseCharacterService:
    """Create character service for magic system integration"""
    return DatabaseCharacterService(db_session) 