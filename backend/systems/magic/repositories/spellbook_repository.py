"""
Spellbook repository for the magic system.

This module contains the repository class for spellbook operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_

from .base import BaseRepository
from ..models import Spellbook, SpellModel

class SpellbookRepository(BaseRepository):
    """Repository for spellbooks."""
    
    def create(self, spellbook_data: Dict[str, Any]) -> Spellbook:
        """
        Create a new spellbook.
        
        Args:
            spellbook_data: Dictionary with spellbook data
            
        Returns:
            Created spellbook instance
        """
        spellbook = Spellbook(**spellbook_data)
        self.db.add(spellbook)
        self.db.flush()
        return spellbook
    
    def get_by_id(self, spellbook_id: int) -> Optional[Spellbook]:
        """
        Get a spellbook by ID.
        
        Args:
            spellbook_id: Spellbook ID
            
        Returns:
            Spellbook instance or None if not found
        """
        return self.db.query(Spellbook).filter(Spellbook.id == spellbook_id).first()
    
    def get_by_owner(self, owner_id: int) -> List[Spellbook]:
        """
        Get spellbooks by owner ID.
        
        Args:
            owner_id: Owner ID
            
        Returns:
            List of spellbook instances owned by the specified owner
        """
        return self.db.query(Spellbook).filter(Spellbook.owner_id == owner_id).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Spellbook]:
        """
        Get all spellbooks.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of spellbook instances
        """
        return self.db.query(Spellbook).offset(skip).limit(limit).all()
    
    def update(self, spellbook_id: int, spellbook_data: Dict[str, Any]) -> Optional[Spellbook]:
        """
        Update a spellbook.
        
        Args:
            spellbook_id: Spellbook ID
            spellbook_data: Dictionary with updated spellbook data
            
        Returns:
            Updated spellbook instance or None if not found
        """
        spellbook = self.get_by_id(spellbook_id)
        if not spellbook:
            return None
            
        for key, value in spellbook_data.items():
            setattr(spellbook, key, value)
            
        self.db.flush()
        return spellbook
    
    def delete(self, spellbook_id: int) -> bool:
        """
        Delete a spellbook.
        
        Args:
            spellbook_id: Spellbook ID
            
        Returns:
            True if deleted, False if not found
        """
        spellbook = self.get_by_id(spellbook_id)
        if not spellbook:
            return False
            
        self.db.delete(spellbook)
        self.db.flush()
        return True
    
    def add_spell(self, spellbook_id: int, spell_id: int) -> bool:
        """
        Add a spell to a spellbook.
        
        Args:
            spellbook_id: Spellbook ID
            spell_id: Spell ID
            
        Returns:
            True if added successfully, False otherwise
        """
        spellbook = self.get_by_id(spellbook_id)
        spell = self.db.query(SpellModel).filter(SpellModel.id == spell_id).first()
        
        if not spellbook or not spell:
            return False
            
        if spell not in spellbook.spells:
            spellbook.spells.append(spell)
            self.db.flush()
            
        return True
    
    def remove_spell(self, spellbook_id: int, spell_id: int) -> bool:
        """
        Remove a spell from a spellbook.
        
        Args:
            spellbook_id: Spellbook ID
            spell_id: Spell ID
            
        Returns:
            True if removed successfully, False otherwise
        """
        spellbook = self.get_by_id(spellbook_id)
        spell = self.db.query(SpellModel).filter(SpellModel.id == spell_id).first()
        
        if not spellbook or not spell:
            return False
            
        if spell in spellbook.spells:
            spellbook.spells.remove(spell)
            self.db.flush()
            
        return True 