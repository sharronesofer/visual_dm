"""
Party model for game parties.

Transaction-based persistence is required for all state-changing operations.
Data integrity is enforced via a SHA-256 checksum stored in the 'checksum' column.
All modifications should be atomic and validated before commit.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class Party(BaseModel):
    """Model for game parties."""
    __tablename__ = 'parties'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(50), default='active')  # active, disbanded, etc.
    inventory = Column(JSON, default=dict)  # Shared party inventory
    quest_log = Column(JSON, default=dict)  # Active and completed quests
    max_size = Column(Integer, default=4)  # Maximum party size
    
    # Foreign Keys
    leader_id = Column(Integer, ForeignKey('characters.id', use_alter=True, name='fk_party_leader'))
    region_id = Column(Integer, ForeignKey('regions.id', use_alter=True, name='fk_party_region'))
    
    # Relationships
    leader = relationship('Character', foreign_keys=[leader_id], back_populates='led_party')
    members = relationship('Character', back_populates='party', foreign_keys='Character.party_id', cascade='all, delete-orphan')
    region = relationship('Region', back_populates='parties', foreign_keys=[region_id])
    
    checksum = Column(String(64), nullable=True)  # SHA-256 checksum for integrity
    schema_version = Column(String(16), nullable=False, default='1.0.0')  # Schema version for versioning
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'inventory': self.inventory,
            'quest_log': self.quest_log,
            'max_size': self.max_size,
            'leader_id': self.leader_id,
            'region_id': self.region_id,
            'members': [member.to_dict() for member in self.members],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'checksum': self.checksum,  # Include checksum for integrity
            'schema_version': self.schema_version
        }

    def __repr__(self):
        return f'<Party {self.name}>'

    def add_member(self, character) -> bool:
        """Add a Character object to the party if there's space."""
        if len(self.members) >= self.max_size:
            return False
        if character not in self.members:
            self.members.append(character)
            return True
        return False

    def remove_member(self, character) -> bool:
        """Remove a Character object from the party."""
        if character in self.members:
            self.members.remove(character)
            return True
        return False

    def is_member(self, character) -> bool:
        """Check if a Character object is a member of the party."""
        return character in self.members

    def get_size(self) -> int:
        """Get the current size of the party."""
        return len(self.members)

    def is_full(self) -> bool:
        """Check if the party is at maximum capacity."""
        return len(self.members) >= self.max_size

    def add_to_shared_inventory(self, item_id: str, quantity: int = 1) -> None:
        """Add an item to the party's shared inventory."""
        if item_id in self.inventory:
            self.inventory[item_id] += quantity
        else:
            self.inventory[item_id] = quantity

    def remove_from_shared_inventory(self, item_id: str, quantity: int = 1) -> bool:
        """Remove an item from the party's shared inventory."""
        if item_id in self.inventory:
            if self.inventory[item_id] >= quantity:
                self.inventory[item_id] -= quantity
                if self.inventory[item_id] == 0:
                    del self.inventory[item_id]
                return True
        return False 