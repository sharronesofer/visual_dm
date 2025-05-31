"""
Character system - Core Character Model.

This module provides the core Character class that serves as the main interface
for character operations, bridging between the ORM model and business logic.
"""

from typing import Dict, Any, List, Optional, Union
from uuid import UUID
from datetime import datetime

from backend.systems.character.models.character import Character as CharacterORM
from backend.systems.character.core.character_builder_class import CharacterBuilder
from backend.systems.character.models.relationship import Relationship, RelationshipType
from backend.systems.character.models.visual_model import CharacterModel as VisualModel


class Character:
    """
    Core Character class providing the main interface for character operations.
    
    This class serves as the canonical character model that tests expect,
    bridging between the SQLAlchemy ORM model and business logic operations.
    It provides a clean API for character manipulation while maintaining
    compatibility with the existing database structure.
    """
    
    def __init__(self, orm_instance: Optional[CharacterORM] = None):
        """
        Initialize Character from ORM instance or create new.
        
        Args:
            orm_instance: Existing Character ORM instance, or None for new character
        """
        self._orm = orm_instance or CharacterORM()
        self._visual_model: Optional[VisualModel] = None
        self._relationships_cache: Optional[List[Relationship]] = None
    
    @property
    def id(self) -> Optional[int]:
        """Character database ID."""
        return self._orm.id
    
    @property
    def uuid(self) -> Optional[str]:
        """Character UUID."""
        return self._orm.uuid
    
    @property
    def name(self) -> Optional[str]:
        """Character name."""
        return self._orm.name
    
    @name.setter
    def name(self, value: str) -> None:
        """Set character name."""
        self._orm.name = value
    
    @property
    def race(self) -> Optional[str]:
        """Character race."""
        return self._orm.race
    
    @race.setter
    def race(self, value: str) -> None:
        """Set character race."""
        self._orm.race = value
    
    @property
    def level(self) -> int:
        """Character level."""
        return self._orm.level or 1
    
    @level.setter
    def level(self, value: int) -> None:
        """Set character level."""
        self._orm.level = value
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Character stats/attributes."""
        return self._orm.stats or {}
    
    @stats.setter
    def stats(self, value: Dict[str, Any]) -> None:
        """Set character stats."""
        self._orm.stats = value
    
    @property
    def background(self) -> Optional[str]:
        """Character background."""
        return self._orm.background
    
    @background.setter
    def background(self, value: str) -> None:
        """Set character background."""
        self._orm.background = value
    
    @property
    def alignment(self) -> Optional[str]:
        """Character alignment."""
        return self._orm.alignment
    
    @alignment.setter
    def alignment(self, value: str) -> None:
        """Set character alignment."""
        self._orm.alignment = value
    
    @property
    def notes(self) -> List[str]:
        """Character notes."""
        return self._orm.notes or []
    
    @notes.setter
    def notes(self, value: List[str]) -> None:
        """Set character notes."""
        self._orm.notes = value
    
    @property
    def created_at(self) -> Optional[datetime]:
        """Character creation timestamp."""
        return self._orm.created_at
    
    @property
    def updated_at(self) -> Optional[datetime]:
        """Character last update timestamp."""
        return self._orm.updated_at
    
    @property
    def visual_model(self) -> Optional[VisualModel]:
        """Character visual model."""
        if self._visual_model is None and hasattr(self._orm, 'visual_model_data'):
            if self._orm.visual_model_data:
                self._visual_model = VisualModel.from_dict(self._orm.visual_model_data)
        return self._visual_model
    
    @visual_model.setter
    def visual_model(self, value: VisualModel) -> None:
        """Set character visual model."""
        self._visual_model = value
        if hasattr(self._orm, 'visual_model_data'):
            self._orm.visual_model_data = value.to_dict() if value else None
    
    def to_builder(self) -> CharacterBuilder:
        """
        Convert character to CharacterBuilder for modification.
        
        Returns:
            CharacterBuilder instance populated with current character data
        """
        builder = CharacterBuilder()
        
        # Set basic character data
        if self.name:
            builder.set_name(self.name)
        if self.race:
            builder.set_race(self.race)
        if self.background:
            builder.set_background(self.background)
        if self.alignment:
            builder.set_alignment(self.alignment)
        
        # Set stats/attributes
        if self.stats:
            for stat, value in self.stats.items():
                builder.set_attribute(stat, value)
        
        # Set level and experience
        builder.set_level(self.level)
        
        # Set notes
        for note in self.notes:
            builder.add_note(note)
        
        return builder
    
    @classmethod
    def from_builder(cls, builder: CharacterBuilder) -> "Character":
        """
        Create character from CharacterBuilder.
        
        Args:
            builder: CharacterBuilder instance with character data
            
        Returns:
            New Character instance
        """
        character_data = builder.finalize()
        
        # Create new ORM instance
        orm_instance = CharacterORM(
            name=character_data.get("character_name"),
            race=character_data.get("race"),
            level=character_data.get("level", 1),
            stats=character_data.get("attributes", {}),
            background=character_data.get("background"),
            alignment=character_data.get("alignment", "Neutral"),
            notes=character_data.get("notes", [])
        )
        
        return cls(orm_instance)
    
    def get_stat(self, stat_name: str, default: int = 0) -> int:
        """
        Get character stat value.
        
        Args:
            stat_name: Name of the stat (STR, DEX, CON, INT, WIS, CHA)
            default: Default value if stat not found
            
        Returns:
            Stat value
        """
        return self.stats.get(stat_name.upper(), default)
    
    def set_stat(self, stat_name: str, value: int) -> None:
        """
        Set character stat value.
        
        Args:
            stat_name: Name of the stat (STR, DEX, CON, INT, WIS, CHA)
            value: Stat value (-3 to +5 in Visual DM)
        """
        if not self.stats:
            self._orm.stats = {}
        self.stats[stat_name.upper()] = max(-3, min(5, value))
    
    def get_stat_modifier(self, stat_name: str) -> int:
        """
        Get stat modifier (in Visual DM, stats are already modifiers).
        
        Args:
            stat_name: Name of the stat
            
        Returns:
            Stat modifier value
        """
        return self.get_stat(stat_name)
    
    def add_note(self, note: str) -> None:
        """
        Add a note to the character.
        
        Args:
            note: Note text to add
        """
        if not self.notes:
            self._orm.notes = []
        self.notes.append(note)
    
    def remove_note(self, note: str) -> bool:
        """
        Remove a note from the character.
        
        Args:
            note: Note text to remove
            
        Returns:
            True if note was removed, False if not found
        """
        if note in self.notes:
            self.notes.remove(note)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert character to dictionary representation.
        
        Returns:
            Dictionary containing character data
        """
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "race": self.race,
            "level": self.level,
            "stats": self.stats,
            "background": self.background,
            "alignment": self.alignment,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "visual_model": self.visual_model.to_dict() if self.visual_model else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Character":
        """
        Create character from dictionary representation.
        
        Args:
            data: Dictionary containing character data
            
        Returns:
            New Character instance
        """
        orm_instance = CharacterORM(
            name=data.get("name"),
            race=data.get("race"),
            level=data.get("level", 1),
            stats=data.get("stats", {}),
            background=data.get("background"),
            alignment=data.get("alignment"),
            notes=data.get("notes", [])
        )
        
        character = cls(orm_instance)
        
        # Set visual model if provided
        if data.get("visual_model"):
            character.visual_model = VisualModel.from_dict(data["visual_model"])
        
        return character
    
    def get_orm_instance(self) -> CharacterORM:
        """
        Get the underlying ORM instance.
        
        Returns:
            CharacterORM instance
        """
        return self._orm
    
    def __repr__(self) -> str:
        """String representation of character."""
        return f"<Character {self.name} (Level {self.level} {self.race})>"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.name} - Level {self.level} {self.race}"
