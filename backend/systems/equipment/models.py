"""
Equipment model definitions.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, JSON, Boolean, ForeignKey, Text, Enum
from datetime import datetime
from backend.core.database import db
from backend.core.models.base import BaseModel # Assuming this is needed, or db.Model is sufficient

class Equipment(db.Model): # Or BaseModel
    """
    Equipment model for character equipment.
    Represents an item equipped in a specific slot for a character.
    """
    __tablename__ = 'equipment'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), nullable=False)
    slot: Mapped[str] = mapped_column(String(50), nullable=False)  # head, body, weapon, etc.
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey('items.id'), nullable=True)
    properties: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # Store item-specific equipment properties
    is_identified: Mapped[bool] = mapped_column(Boolean, default=True)  # Track if magical properties are identified
    current_durability: Mapped[float] = mapped_column(Float, default=100.0)  # Current durability percentage
    max_durability: Mapped[float] = mapped_column(Float, default=100.0)  # Maximum durability percentage
    is_broken: Mapped[bool] = mapped_column(Boolean, default=False)  # Whether the item is broken (0 durability)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment to dictionary."""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'slot': self.slot,
            'item_id': self.item_id,
            'properties': self.properties,
            'is_identified': self.is_identified,
            'current_durability': self.current_durability,
            'max_durability': self.max_durability,
            'is_broken': self.is_broken,
            'durability_percentage': round((self.current_durability / self.max_durability) * 100, 1) if self.max_durability > 0 else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class EquipmentSet(db.Model):
    """
    Equipment Set model for defining sets of equipment that provide bonuses when
    multiple pieces are equipped together.
    """
    __tablename__ = 'equipment_sets'
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    set_bonuses: Mapped[Dict] = mapped_column(JSON, nullable=False)  # Maps number of pieces to bonuses
    item_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)  # List of item IDs that belong to this set
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment set to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'set_bonuses': self.set_bonuses,
            'item_ids': self.item_ids,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class EquipmentDurabilityLog(db.Model):
    """
    Equipment Durability Log model for tracking changes to equipment durability over time.
    Useful for analytics, item history, and determining repair costs.
    """
    __tablename__ = 'equipment_durability_logs'
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey('equipment.id'), nullable=False)
    previous_durability: Mapped[float] = mapped_column(Float, nullable=False)
    new_durability: Mapped[float] = mapped_column(Float, nullable=False)
    change_amount: Mapped[float] = mapped_column(Float, nullable=False)  # Can be negative (damage) or positive (repair)
    change_reason: Mapped[str] = mapped_column(String(50), nullable=False)  # combat, wear, repair, etc.
    event_details: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)  # Additional context about the change
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert durability log entry to dictionary."""
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'previous_durability': self.previous_durability,
            'new_durability': self.new_durability,
            'change_amount': self.change_amount,
            'change_reason': self.change_reason,
            'event_details': self.event_details,
            'timestamp': self.timestamp.isoformat()
        } 