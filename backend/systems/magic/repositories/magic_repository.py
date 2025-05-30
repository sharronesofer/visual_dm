"""
Magic repository for the magic system.

This module contains the repository class for magic ability operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_

from .base import BaseRepository
from ..models import MagicModel, MagicType, MagicSchool

class MagicRepository(BaseRepository):
    """Repository for magic abilities."""
    
    def create(self, magic_data: Dict[str, Any]) -> MagicModel:
        """
        Create a new magic ability.
        
        Args:
            magic_data: Dictionary with magic ability data
            
        Returns:
            Created magic ability instance
        """
        magic_ability = MagicModel(**magic_data)
        self.db.add(magic_ability)
        self.db.flush()
        return magic_ability
    
    def get_by_id(self, magic_id: int) -> Optional[MagicModel]:
        """
        Get a magic ability by ID.
        
        Args:
            magic_id: Magic ability ID
            
        Returns:
            Magic ability instance or None if not found
        """
        return self.db.query(MagicModel).filter(MagicModel.id == magic_id).first()
    
    def get_all(self, 
               skip: int = 0, 
               limit: int = 100, 
               magic_type: Optional[MagicType] = None,
               school: Optional[MagicSchool] = None) -> List[MagicModel]:
        """
        Get all magic abilities with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            magic_type: Filter by magic type
            school: Filter by school
            
        Returns:
            List of magic ability instances
        """
        query = self.db.query(MagicModel)
        
        if magic_type:
            query = query.filter(MagicModel.magic_type == magic_type)
        
        if school:
            query = query.filter(MagicModel.school == school)
            
        return query.offset(skip).limit(limit).all()
    
    def update(self, magic_id: int, magic_data: Dict[str, Any]) -> Optional[MagicModel]:
        """
        Update a magic ability.
        
        Args:
            magic_id: Magic ability ID
            magic_data: Dictionary with updated magic ability data
            
        Returns:
            Updated magic ability instance or None if not found
        """
        magic_ability = self.get_by_id(magic_id)
        if not magic_ability:
            return None
            
        for key, value in magic_data.items():
            setattr(magic_ability, key, value)
            
        self.db.flush()
        return magic_ability
    
    def delete(self, magic_id: int) -> bool:
        """
        Delete a magic ability.
        
        Args:
            magic_id: Magic ability ID
            
        Returns:
            True if deleted, False if not found
        """
        magic_ability = self.get_by_id(magic_id)
        if not magic_ability:
            return False
            
        self.db.delete(magic_ability)
        self.db.flush()
        return True 