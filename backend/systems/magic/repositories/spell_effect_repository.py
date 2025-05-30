"""
Spell effect repository for the magic system.

This module contains the repository class for spell effect operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_

from .base import BaseRepository
from ..models import SpellEffect, EffectType

class SpellEffectRepository(BaseRepository):
    """Repository for spell effects."""
    
    def create(self, effect_data: Dict[str, Any]) -> SpellEffect:
        """
        Create a new spell effect.
        
        Args:
            effect_data: Dictionary with spell effect data
            
        Returns:
            Created spell effect instance
        """
        effect = SpellEffect(**effect_data)
        self.db.add(effect)
        self.db.flush()
        return effect
    
    def get_by_id(self, effect_id: int) -> Optional[SpellEffect]:
        """
        Get a spell effect by ID.
        
        Args:
            effect_id: Spell effect ID
            
        Returns:
            Spell effect instance or None if not found
        """
        return self.db.query(SpellEffect).filter(SpellEffect.id == effect_id).first()
    
    def get_by_type(self, effect_type: EffectType) -> List[SpellEffect]:
        """
        Get spell effects by type.
        
        Args:
            effect_type: Effect type enum value
            
        Returns:
            List of spell effect instances of the specified type
        """
        return self.db.query(SpellEffect).filter(SpellEffect.type == effect_type).all()
    
    def get_by_spell(self, spell_id: int) -> List[SpellEffect]:
        """
        Get all effects for a specific spell.
        
        Args:
            spell_id: Spell ID
            
        Returns:
            List of spell effect instances for the specified spell
        """
        return self.db.query(SpellEffect).filter(SpellEffect.spell_id == spell_id).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[SpellEffect]:
        """
        Get all spell effects.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of spell effect instances
        """
        return self.db.query(SpellEffect).offset(skip).limit(limit).all()
    
    def update(self, effect_id: int, effect_data: Dict[str, Any]) -> Optional[SpellEffect]:
        """
        Update a spell effect.
        
        Args:
            effect_id: Spell effect ID
            effect_data: Dictionary with updated spell effect data
            
        Returns:
            Updated spell effect instance or None if not found
        """
        effect = self.get_by_id(effect_id)
        if not effect:
            return None
            
        for key, value in effect_data.items():
            setattr(effect, key, value)
            
        self.db.flush()
        return effect
    
    def delete(self, effect_id: int) -> bool:
        """
        Delete a spell effect.
        
        Args:
            effect_id: Spell effect ID
            
        Returns:
            True if deleted, False if not found
        """
        effect = self.get_by_id(effect_id)
        if not effect:
            return False
            
        self.db.delete(effect)
        self.db.flush()
        return True 