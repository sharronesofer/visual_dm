"""
Combat statistics model.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.infrastructure.models import BaseModel

class CombatStats(BaseModel):
    """
    Model for tracking character combat statistics.
    """
    __tablename__ = 'combat_stats'
    
    # id, created_at, updated_at are inherited from BaseModel
    
    character_id = Column(UUID(as_uuid=True), ForeignKey('characters.id'), nullable=False)
    armor_class = Column(Integer, default=10)
    initiative_bonus = Column(Integer, default=0)
    attack_bonus = Column(Integer, default=0)
    damage_reduction = Column(Integer, default=0)
    hit_dice = Column(String(20), default="1d8")  # Format: "1d8"
    current_hp = Column(Integer, default=10)
    max_hp = Column(Integer, default=10)
    temporary_hp = Column(Integer, default=0)
    resistances = Column(JSON, default=lambda: [])
    vulnerabilities = Column(JSON, default=lambda: [])
    immunities = Column(JSON, default=lambda: [])
    conditions = Column(JSON, default=lambda: [])
    
    # Relationship with character
    character = relationship("Character", back_populates="combat_stats")
    
    def __repr__(self):
        return f"<CombatStats(id={self.id}, character_id={self.character_id}, hp={self.current_hp}/{self.max_hp})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "character_id": str(self.character_id),
            "armor_class": self.armor_class,
            "initiative_bonus": self.initiative_bonus,
            "attack_bonus": self.attack_bonus,
            "damage_reduction": self.damage_reduction,
            "hit_dice": self.hit_dice,
            "current_hp": self.current_hp,
            "max_hp": self.max_hp,
            "temporary_hp": self.temporary_hp,
            "resistances": self.resistances,
            "vulnerabilities": self.vulnerabilities,
            "immunities": self.immunities,
            "conditions": self.conditions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CombatStats":
        """Create model from dictionary."""
        return cls(
            character_id=data.get("character_id"),
            armor_class=data.get("armor_class", 10),
            initiative_bonus=data.get("initiative_bonus", 0),
            attack_bonus=data.get("attack_bonus", 0),
            damage_reduction=data.get("damage_reduction", 0),
            hit_dice=data.get("hit_dice", "1d8"),
            current_hp=data.get("current_hp", 10),
            max_hp=data.get("max_hp", 10),
            temporary_hp=data.get("temporary_hp", 0),
            resistances=data.get("resistances", []),
            vulnerabilities=data.get("vulnerabilities", []),
            immunities=data.get("immunities", []),
            conditions=data.get("conditions", []),
        ) 