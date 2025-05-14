"""
Consolidated Equipment model.
Provides a single authoritative definition for equipment in the game.
"""

from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.core.database import db

class EquipmentSlot(db.Model):
    """Model for equipment slots on characters."""
    __tablename__ = 'equipment_slots'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self) -> Dict:
        """Convert equipment slot to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_primary': self.is_primary,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class EquipmentInstance(db.Model):
    """Model for instances of equipment on characters."""
    __tablename__ = 'equipment_instances'

    id = Column(Integer, primary_key=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    slot_id = Column(Integer, ForeignKey('equipment_slots.id'), nullable=False)
    is_equipped = Column(Boolean, default=False)
    condition = Column(Integer, default=100)  # 0-100
    modifications = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    character = relationship('Character', back_populates='equipment')
    item = relationship('Item', back_populates='equipment_instances')
    slot = relationship('EquipmentSlot')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modifications = kwargs.get('modifications', {})

    def to_dict(self) -> Dict:
        """Convert equipment instance to dictionary representation."""
        return {
            'id': self.id,
            'character_id': self.character_id,
            'item_id': self.item_id,
            'slot_id': self.slot_id,
            'is_equipped': self.is_equipped,
            'condition': self.condition,
            'modifications': self.modifications,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def equip(self) -> None:
        """Equip this equipment instance."""
        self.is_equipped = True
        self.updated_at = datetime.utcnow()

    def unequip(self) -> None:
        """Unequip this equipment instance."""
        self.is_equipped = False
        self.updated_at = datetime.utcnow()

    def modify(self, modifications: Dict) -> None:
        """Apply modifications to this equipment instance."""
        self.modifications.update(modifications)
        self.updated_at = datetime.utcnow()

    def get_stats(self) -> Dict:
        """Get the effective stats of this equipment instance."""
        base_stats = self.item.properties.get('stats', {})
        modified_stats = base_stats.copy()
        
        # Apply modifications
        for stat, value in self.modifications.get('stats', {}).items():
            if stat in modified_stats:
                modified_stats[stat] += value
            else:
                modified_stats[stat] = value
                
        return modified_stats

    def get_requirements(self) -> Dict:
        """Get the requirements for using this equipment instance."""
        return self.item.get_requirements()

    def get_effects(self) -> List[Dict]:
        """Get the effects of this equipment instance."""
        return self.item.get_effects() 