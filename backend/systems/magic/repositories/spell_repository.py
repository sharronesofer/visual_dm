"""
Spell repository for the magic system.

This module contains the repository class for spell operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_

from .base import BaseRepository
from ..models import SpellModel, MagicType, MagicSchool

class SpellRepository(BaseRepository):
    """Repository for spells."""
    
    def create(self, spell_data: Dict[str, Any]) -> SpellModel:
        """
        Create a new spell.
        
        Args:
            spell_data: Dictionary with spell data
            
        Returns:
            Created spell instance
        """
        spell = SpellModel(**spell_data)
        self.db.add(spell)
        self.db.flush()
        return spell
    
    def get_by_id(self, spell_id: int) -> Optional[SpellModel]:
        """
        Get a spell by ID.
        
        Args:
            spell_id: Spell ID
            
        Returns:
            Spell instance or None if not found
        """
        return self.db.query(SpellModel).filter(SpellModel.id == spell_id).first()
    
    def get_by_name(self, name: str) -> Optional[SpellModel]:
        """
        Get a spell by name.
        
        Args:
            name: Spell name
            
        Returns:
            Spell instance or None if not found
        """
        return self.db.query(SpellModel).filter(SpellModel.name == name).first()
    
    def get_all(self, 
               skip: int = 0, 
               limit: int = 100, 
               magic_type: Optional[MagicType] = None,
               school: Optional[MagicSchool] = None,
               min_level: Optional[int] = None,
               max_level: Optional[int] = None) -> List[SpellModel]:
        """
        Get all spells with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            magic_type: Filter by magic type
            school: Filter by school
            min_level: Minimum spell level
            max_level: Maximum spell level
            
        Returns:
            List of spell instances
        """
        query = self.db.query(SpellModel)
        
        if magic_type:
            query = query.filter(SpellModel.magic_type == magic_type)
        
        if school:
            query = query.filter(SpellModel.school == school)
            
        if min_level is not None:
            query = query.filter(SpellModel.level >= min_level)
            
        if max_level is not None:
            query = query.filter(SpellModel.level <= max_level)
            
        return query.offset(skip).limit(limit).all()
    
    def update(self, spell_id: int, spell_data: Dict[str, Any]) -> Optional[SpellModel]:
        """
        Update a spell.
        
        Args:
            spell_id: Spell ID
            spell_data: Dictionary with updated spell data
            
        Returns:
            Updated spell instance or None if not found
        """
        spell = self.get_by_id(spell_id)
        if not spell:
            return None
            
        for key, value in spell_data.items():
            setattr(spell, key, value)
            
        self.db.flush()
        return spell
    
    def delete(self, spell_id: int) -> bool:
        """
        Delete a spell.
        
        Args:
            spell_id: Spell ID
            
        Returns:
            True if deleted, False if not found
        """
        spell = self.get_by_id(spell_id)
        if not spell:
            return False
            
        self.db.delete(spell)
        self.db.flush()
        return True
    
    def get_by_component(self, component_type: str) -> List[SpellModel]:
        """
        Get spells by component type.
        
        Args:
            component_type: The type of component to filter by
            
        Returns:
            List of spells that use the specified component
        """
        return (self.db.query(SpellModel)
                .join(SpellModel.components)
                .filter_by(type=component_type)
                .all())
                
    def get_by_effect(self, effect_type: str) -> List[SpellModel]:
        """
        Get spells by effect type.
        
        Args:
            effect_type: The type of effect to filter by
            
        Returns:
            List of spells that produce the specified effect
        """
        return (self.db.query(SpellModel)
                .join(SpellModel.effects)
                .filter_by(type=effect_type)
                .all()) 