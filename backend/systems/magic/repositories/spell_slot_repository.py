"""
Spell slot repository for the magic system.

This module contains the repository class for spell slot operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_

from .base import BaseRepository
from ..models import SpellSlot

class SpellSlotRepository(BaseRepository):
    """Repository for spell slots."""
    
    def create(self, slot_data: Dict[str, Any]) -> SpellSlot:
        """
        Create a new spell slot.
        
        Args:
            slot_data: Dictionary with spell slot data
            
        Returns:
            Created spell slot instance
        """
        slot = SpellSlot(**slot_data)
        self.db.add(slot)
        self.db.flush()
        return slot
    
    def get_by_id(self, slot_id: int) -> Optional[SpellSlot]:
        """
        Get a spell slot by ID.
        
        Args:
            slot_id: Spell slot ID
            
        Returns:
            Spell slot instance or None if not found
        """
        return self.db.query(SpellSlot).filter(SpellSlot.id == slot_id).first()
    
    def get_by_character(self, character_id: int) -> List[SpellSlot]:
        """
        Get all spell slots for a specific character.
        
        Args:
            character_id: Character ID
            
        Returns:
            List of spell slot instances for the specified character
        """
        return self.db.query(SpellSlot).filter(SpellSlot.character_id == character_id).all()
    
    def get_by_level(self, character_id: int, level: int) -> List[SpellSlot]:
        """
        Get all spell slots for a specific character and level.
        
        Args:
            character_id: Character ID
            level: Spell slot level
            
        Returns:
            List of spell slot instances for the specified character and level
        """
        return (self.db.query(SpellSlot)
                .filter(SpellSlot.character_id == character_id)
                .filter(SpellSlot.level == level)
                .all())
    
    def get_available(self, character_id: int, level: Optional[int] = None) -> List[SpellSlot]:
        """
        Get all available (not used) spell slots for a specific character.
        
        Args:
            character_id: Character ID
            level: Optional spell slot level to filter by
            
        Returns:
            List of available spell slot instances
        """
        query = (self.db.query(SpellSlot)
                .filter(SpellSlot.character_id == character_id)
                .filter(SpellSlot.is_used == False))
                
        if level is not None:
            query = query.filter(SpellSlot.level == level)
            
        return query.all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[SpellSlot]:
        """
        Get all spell slots.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of spell slot instances
        """
        return self.db.query(SpellSlot).offset(skip).limit(limit).all()
    
    def update(self, slot_id: int, slot_data: Dict[str, Any]) -> Optional[SpellSlot]:
        """
        Update a spell slot.
        
        Args:
            slot_id: Spell slot ID
            slot_data: Dictionary with updated spell slot data
            
        Returns:
            Updated spell slot instance or None if not found
        """
        slot = self.get_by_id(slot_id)
        if not slot:
            return None
            
        for key, value in slot_data.items():
            setattr(slot, key, value)
            
        self.db.flush()
        return slot
    
    def delete(self, slot_id: int) -> bool:
        """
        Delete a spell slot.
        
        Args:
            slot_id: Spell slot ID
            
        Returns:
            True if deleted, False if not found
        """
        slot = self.get_by_id(slot_id)
        if not slot:
            return False
            
        self.db.delete(slot)
        self.db.flush()
        return True
    
    def use_slot(self, slot_id: int) -> bool:
        """
        Mark a spell slot as used.
        
        Args:
            slot_id: Spell slot ID
            
        Returns:
            True if marked successfully, False if not found or already used
        """
        slot = self.get_by_id(slot_id)
        if not slot or slot.is_used:
            return False
            
        slot.is_used = True
        self.db.flush()
        return True
    
    def reset_slots(self, character_id: int) -> int:
        """
        Reset all used spell slots for a character.
        
        Args:
            character_id: Character ID
            
        Returns:
            Number of slots reset
        """
        slots = (self.db.query(SpellSlot)
                .filter(SpellSlot.character_id == character_id)
                .filter(SpellSlot.is_used == True)
                .all())
                
        for slot in slots:
            slot.is_used = False
            
        self.db.flush()
        return len(slots) 