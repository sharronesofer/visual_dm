"""
Magic system repositories.

This module contains repository classes for database operations
related to the magic system.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from datetime import datetime

from .models import (
    MagicModel, SpellModel, SpellSlot, SpellSchool, 
    Spellbook, SpellComponent, SpellEffect
)

class BaseRepository:
    """Base repository for common operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def commit(self):
        """Commit changes to the database."""
        self.db.commit()
    
    def rollback(self):
        """Rollback changes."""
        self.db.rollback()


class MagicRepository(BaseRepository):
    """Repository for magic abilities."""
    
    def create(self, data: Dict[str, Any]) -> MagicModel:
        """
        Create a new magic ability.
        
        Args:
            data: Dictionary containing magic ability data
            
        Returns:
            MagicModel: The created magic ability
        """
        db_item = MagicModel(**data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_by_id(self, id: int) -> Optional[MagicModel]:
        """
        Get a magic ability by ID.
        
        Args:
            id: The magic ability ID
            
        Returns:
            Optional[MagicModel]: The magic ability or None
        """
        return self.db.query(MagicModel).filter(MagicModel.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[MagicModel]:
        """
        Get all magic abilities.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List[MagicModel]: List of magic abilities
        """
        return self.db.query(MagicModel).offset(skip).limit(limit).all()
    
    def get_by_owner(self, owner_type: str, owner_id: int) -> List[MagicModel]:
        """
        Get magic abilities by owner.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            owner_id: The ID of the owner
            
        Returns:
            List[MagicModel]: List of magic abilities
        """
        return self.db.query(MagicModel).filter(
            and_(
                MagicModel.owner_type == owner_type,
                MagicModel.owner_id == owner_id
            )
        ).all()
    
    def get_by_type(self, ability_type: str) -> List[MagicModel]:
        """
        Get magic abilities by type.
        
        Args:
            ability_type: The type of ability
            
        Returns:
            List[MagicModel]: List of magic abilities
        """
        return self.db.query(MagicModel).filter(
            MagicModel.ability_type == ability_type
        ).all()
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[MagicModel]:
        """
        Update a magic ability.
        
        Args:
            id: The magic ability ID
            data: Dictionary containing updated magic ability data
            
        Returns:
            Optional[MagicModel]: The updated magic ability or None
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return None
        
        for key, value in data.items():
            setattr(db_item, key, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def delete(self, id: int) -> bool:
        """
        Delete a magic ability.
        
        Args:
            id: The magic ability ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True

    def create_magic_ability(self, data: Dict[str, Any]) -> MagicModel:
        """
        Create a magic ability.
        
        Args:
            data: Dictionary containing magic ability data
            
        Returns:
            MagicModel: The created magic ability
        """
        ability = MagicModel(**data)
        self.db.add(ability)
        self.db.commit()
        self.db.refresh(ability)
        return ability
    
    def update_magic_ability(self, ability_id: int, data: Dict[str, Any]) -> Optional[MagicModel]:
        """
        Update a magic ability.
        
        Args:
            ability_id: The ID of the ability
            data: Dictionary containing updated data
            
        Returns:
            Optional[MagicModel]: The updated ability if found, None otherwise
        """
        ability = self.get_by_id(ability_id)
        if not ability:
            return None
        
        for key, value in data.items():
            if hasattr(ability, key):
                setattr(ability, key, value)
        
        self.db.commit()
        self.db.refresh(ability)
        return ability
    
    def delete_magic_ability(self, ability_id: int) -> bool:
        """
        Delete a magic ability.
        
        Args:
            ability_id: The ID of the ability
            
        Returns:
            bool: True if deleted, False if not found
        """
        ability = self.get_by_id(ability_id)
        if not ability:
            return False
        
        self.db.delete(ability)
        self.db.commit()
        return True


class SpellRepository(BaseRepository):
    """Repository for spells."""
    
    def create(self, data: Dict[str, Any]) -> SpellModel:
        """
        Create a new spell.
        
        Args:
            data: Dictionary containing spell data
            
        Returns:
            SpellModel: The created spell
        """
        db_item = SpellModel(**data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_by_id(self, id: int) -> Optional[SpellModel]:
        """
        Get a spell by ID.
        
        Args:
            id: The spell ID
            
        Returns:
            Optional[SpellModel]: The spell or None
        """
        return self.db.query(SpellModel).filter(SpellModel.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100, school: Optional[str] = None) -> List[SpellModel]:
        """
        Get all spells.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            school: Optional filter by spell school
            
        Returns:
            List[SpellModel]: List of spells
        """
        query = self.db.query(SpellModel)
        if school:
            query = query.filter(SpellModel.school == school)
        return query.offset(skip).limit(limit).all()
    
    def search(self, 
               name: Optional[str] = None, 
               level_min: Optional[int] = None,
               level_max: Optional[int] = None,
               school: Optional[str] = None) -> List[SpellModel]:
        """
        Search for spells with filters.
        
        Args:
            name: Optional name filter (partial match)
            level_min: Optional minimum level filter
            level_max: Optional maximum level filter
            school: Optional school filter
            
        Returns:
            List[SpellModel]: List of matching spells
        """
        query = self.db.query(SpellModel)
        
        if name:
            query = query.filter(SpellModel.name.ilike(f"%{name}%"))
        
        if level_min is not None:
            query = query.filter(SpellModel.level >= level_min)
            
        if level_max is not None:
            query = query.filter(SpellModel.level <= level_max)
            
        if school:
            query = query.filter(SpellModel.school == school)
            
        return query.all()
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[SpellModel]:
        """
        Update a spell.
        
        Args:
            id: The spell ID
            data: Dictionary containing updated spell data
            
        Returns:
            Optional[SpellModel]: The updated spell or None
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return None
        
        for key, value in data.items():
            setattr(db_item, key, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def delete(self, id: int) -> bool:
        """
        Delete a spell.
        
        Args:
            id: The spell ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True


class SpellbookRepository(BaseRepository):
    """Repository for spellbooks."""
    
    def create(self, data: Dict[str, Any]) -> Spellbook:
        """
        Create a new spellbook.
        
        Args:
            data: Dictionary containing spellbook data
            
        Returns:
            Spellbook: The created spellbook
        """
        db_item = Spellbook(**data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_by_id(self, id: int) -> Optional[Spellbook]:
        """
        Get a spellbook by ID.
        
        Args:
            id: The spellbook ID
            
        Returns:
            Optional[Spellbook]: The spellbook or None
        """
        return self.db.query(Spellbook).filter(Spellbook.id == id).first()
    
    def get_by_owner(self, owner_type: str, owner_id: int) -> Optional[Spellbook]:
        """
        Get spellbook by owner.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            owner_id: The ID of the owner
            
        Returns:
            Optional[Spellbook]: The spellbook if found, None otherwise
        """
        return self.db.query(Spellbook).filter(
            and_(
                Spellbook.owner_type == owner_type,
                Spellbook.owner_id == owner_id
            )
        ).first()
    
    def get_all(self, owner_type: Optional[str] = None) -> List[Spellbook]:
        """
        Get all spellbooks, optionally filtered by owner type.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            
        Returns:
            List[Spellbook]: List of spellbooks
        """
        query = self.db.query(Spellbook)
        if owner_type:
            query = query.filter(Spellbook.owner_type == owner_type)
        return query.all()
    
    def add_spell(self, spellbook_id: int, spell_id: int) -> bool:
        """
        Add a spell to a spellbook.
        
        Args:
            spellbook_id: The spellbook ID
            spell_id: The spell ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        spellbook = self.get_by_id(spellbook_id)
        if not spellbook:
            return False
        
        # Check if spell already exists in the spellbook
        if spell_id in [s.id for s in spellbook.spells]:
            return True  # Spell already added
        
        # Get the spell
        spell = self.db.query(SpellModel).filter(SpellModel.id == spell_id).first()
        if not spell:
            return False
        
        # Add the spell to the spellbook
        spellbook.spells.append(spell)
        self.db.commit()
        return True
    
    def remove_spell(self, spellbook_id: int, spell_id: int) -> bool:
        """
        Remove a spell from a spellbook.
        
        Args:
            spellbook_id: The spellbook ID
            spell_id: The spell ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        spellbook = self.get_by_id(spellbook_id)
        if not spellbook:
            return False
        
        # Check if spell exists in the spellbook
        spell = next((s for s in spellbook.spells if s.id == spell_id), None)
        if not spell:
            return False  # Spell not in spellbook
        
        # Remove the spell from the spellbook
        spellbook.spells.remove(spell)
        self.db.commit()
        return True
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[Spellbook]:
        """
        Update a spellbook.
        
        Args:
            id: The spellbook ID
            data: Dictionary containing updated spellbook data
            
        Returns:
            Optional[Spellbook]: The updated spellbook or None
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return None
        
        for key, value in data.items():
            if key != "spells":  # Handle spells separately
                setattr(db_item, key, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def delete(self, id: int) -> bool:
        """
        Delete a spellbook.
        
        Args:
            id: The spellbook ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True


class SpellEffectRepository(BaseRepository):
    """Repository for spell effects."""
    
    def create(self, data: Dict[str, Any]) -> SpellEffect:
        """
        Create a new spell effect.
        
        Args:
            data: Dictionary containing spell effect data
            
        Returns:
            SpellEffect: The created spell effect
        """
        db_item = SpellEffect(**data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_by_id(self, id: int) -> Optional[SpellEffect]:
        """
        Get a spell effect by ID.
        
        Args:
            id: The spell effect ID
            
        Returns:
            Optional[SpellEffect]: The spell effect or None
        """
        return self.db.query(SpellEffect).filter(SpellEffect.id == id).first()
    
    def get_by_target(self, target_type: str, target_id: int) -> List[SpellEffect]:
        """
        Get spell effects by target.
        
        Args:
            target_type: The type of target (character, npc, etc.)
            target_id: The ID of the target
            
        Returns:
            List[SpellEffect]: List of spell effects
        """
        return self.db.query(SpellEffect).filter(
            and_(
                SpellEffect.target_type == target_type,
                SpellEffect.target_id == target_id
            )
        ).all()
    
    def get_active_effects(self, target_type: str, target_id: int) -> List[SpellEffect]:
        """
        Get active spell effects on a target.
        
        Args:
            target_type: The type of target (character, npc, etc.)
            target_id: The ID of the target
            
        Returns:
            List[SpellEffect]: List of active spell effects
        """
        return self.db.query(SpellEffect).filter(
            and_(
                SpellEffect.target_type == target_type,
                SpellEffect.target_id == target_id,
                SpellEffect.is_active == True
            )
        ).all()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[SpellEffect]:
        """
        Get all spell effects.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List[SpellEffect]: List of spell effects
        """
        return self.db.query(SpellEffect).offset(skip).limit(limit).all()
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[SpellEffect]:
        """
        Update a spell effect.
        
        Args:
            id: The spell effect ID
            data: Dictionary containing updated spell effect data
            
        Returns:
            Optional[SpellEffect]: The updated spell effect or None
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return None
        
        for key, value in data.items():
            setattr(db_item, key, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def delete(self, id: int) -> bool:
        """
        Delete a spell effect.
        
        Args:
            id: The spell effect ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True
    
    def reduce_duration(self, id: int, rounds: int = 1) -> Optional[SpellEffect]:
        """
        Reduce the duration of a spell effect.
        
        Args:
            id: The spell effect ID
            rounds: Number of rounds to reduce duration by
            
        Returns:
            Optional[SpellEffect]: The updated spell effect or None
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return None
        
        if db_item.duration <= rounds:
            db_item.duration = 0
            db_item.is_active = False
        else:
            db_item.duration -= rounds
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_all_active(self) -> List[SpellEffect]:
        """
        Get all active spell effects.
        
        Returns:
            List[SpellEffect]: List of active spell effects
        """
        return self.db.query(SpellEffect).filter(SpellEffect.is_active == True).all()
    
    def get_by_spell(self, spell_id: int) -> List[SpellEffect]:
        """
        Get all effects created by a specific spell.
        
        Args:
            spell_id: The spell ID
            
        Returns:
            List[SpellEffect]: List of spell effects
        """
        return self.db.query(SpellEffect).filter(SpellEffect.spell_id == spell_id).all()
    
    def end_effect(self, id: int) -> bool:
        """
        End a spell effect (mark as inactive).
        
        Args:
            id: The spell effect ID
            
        Returns:
            bool: True if ended, False otherwise
        """
        effect = self.get_by_id(id)
        if not effect:
            return False
        
        effect.is_active = False
        effect.remaining_duration = 0
        effect.ended_at = datetime.utcnow()
        
        self.db.commit()
        return True


class SpellSlotRepository(BaseRepository):
    """Repository for spell slots."""
    
    def create(self, data: Dict[str, Any]) -> SpellSlot:
        """
        Create a new spell slot.
        
        Args:
            data: Dictionary containing spell slot data
            
        Returns:
            SpellSlot: The created spell slot
        """
        db_item = SpellSlot(**data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def get_by_id(self, id: int) -> Optional[SpellSlot]:
        """
        Get a spell slot by ID.
        
        Args:
            id: The spell slot ID
            
        Returns:
            Optional[SpellSlot]: The spell slot or None
        """
        return self.db.query(SpellSlot).filter(SpellSlot.id == id).first()
    
    def get_by_owner(self, owner_type: str, owner_id: int) -> List[SpellSlot]:
        """
        Get spell slots by owner.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            owner_id: The ID of the owner
            
        Returns:
            List[SpellSlot]: List of spell slots
        """
        return self.db.query(SpellSlot).filter(
            and_(
                SpellSlot.owner_type == owner_type,
                SpellSlot.owner_id == owner_id
            )
        ).all()
    
    def get_available_slots(self, owner_type: str, owner_id: int, level: int) -> List[SpellSlot]:
        """
        Get available spell slots by level.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            owner_id: The ID of the owner
            level: The spell level
            
        Returns:
            List[SpellSlot]: List of available spell slots
        """
        return self.db.query(SpellSlot).filter(
            and_(
                SpellSlot.owner_type == owner_type,
                SpellSlot.owner_id == owner_id,
                SpellSlot.level == level,
                SpellSlot.is_used == False
            )
        ).all()
    
    def use_slot(self, id: int) -> Optional[SpellSlot]:
        """
        Mark a spell slot as used.
        
        Args:
            id: The spell slot ID
            
        Returns:
            Optional[SpellSlot]: The updated spell slot or None
        """
        db_item = self.get_by_id(id)
        if not db_item or db_item.is_used:
            return None
        
        db_item.is_used = True
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def restore_slot(self, id: int) -> Optional[SpellSlot]:
        """
        Restore a used spell slot.
        
        Args:
            id: The spell slot ID
            
        Returns:
            Optional[SpellSlot]: The updated spell slot or None
        """
        db_item = self.get_by_id(id)
        if not db_item or not db_item.is_used:
            return None
        
        db_item.is_used = False
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def restore_all_slots(self, owner_type: str, owner_id: int) -> bool:
        """
        Restore all spell slots for an owner.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            owner_id: The ID of the owner
            
        Returns:
            bool: True if restored, False otherwise
        """
        slots = self.get_by_owner(owner_type, owner_id)
        if not slots:
            return False
        
        for slot in slots:
            slot.is_used = False
        
        self.db.commit()
        return True
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[SpellSlot]:
        """
        Update a spell slot.
        
        Args:
            id: The spell slot ID
            data: Dictionary containing updated spell slot data
            
        Returns:
            Optional[SpellSlot]: The updated spell slot or None
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return None
        
        for key, value in data.items():
            setattr(db_item, key, value)
        
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    def delete(self, id: int) -> bool:
        """
        Delete a spell slot.
        
        Args:
            id: The spell slot ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        db_item = self.get_by_id(id)
        if not db_item:
            return False
        
        self.db.delete(db_item)
        self.db.commit()
        return True
    
    def get_all_slots(self, owner_type: str, owner_id: int) -> List[SpellSlot]:
        """
        Get all spell slots for an owner.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            owner_id: The ID of the owner
            
        Returns:
            List[SpellSlot]: List of all spell slots
        """
        return self.db.query(SpellSlot).filter(
            and_(
                SpellSlot.owner_type == owner_type,
                SpellSlot.owner_id == owner_id
            )
        ).all()
    
    def refresh_slots(self, owner_type: str, owner_id: int, level: Optional[int] = None) -> int:
        """
        Refresh all used spell slots for an owner.
        
        Args:
            owner_type: The type of owner (character, npc, etc.)
            owner_id: The ID of the owner
            level: Optional level to refresh only slots of that level
            
        Returns:
            int: Number of slots refreshed
        """
        query = self.db.query(SpellSlot).filter(
            and_(
                SpellSlot.owner_type == owner_type,
                SpellSlot.owner_id == owner_id,
                SpellSlot.used == True
            )
        )
        
        if level is not None:
            query = query.filter(SpellSlot.level == level)
        
        slots = query.all()
        count = 0
        
        for slot in slots:
            slot.used = False
            count += 1
        
        self.db.commit()
        return count 