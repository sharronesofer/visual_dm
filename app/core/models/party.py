"""
Party model for game parties.

Transaction-based persistence is required for all state-changing operations.
Data integrity is enforced via a SHA-256 checksum stored in the 'checksum' column.
All modifications should be atomic and validated before commit.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel

class Party(BaseModel):
    """
    Model for game parties.
    Fields:
        id (int): Primary key.
        name (str): Party name.
        description (str): Description of the party.
        status (str): Party status (e.g., 'active', 'disbanded').
        inventory (dict): Shared party inventory.
        quest_log (dict): Active and completed quests.
        max_size (int): Maximum party size.
        leader_id (int): Foreign key to leader character.
        region_id (int): Foreign key to region.
        leader (Character): Party leader.
        members (List[Character]): Party members.
        region (Region): Party's region.
        checksum (str): SHA-256 checksum for integrity.
        schema_version (str): Schema version for versioning.
    """
    __tablename__ = 'parties'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    name: Mapped[str] = mapped_column(String(100), nullable=False, doc="Party name.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Description of the party.")
    status: Mapped[str] = mapped_column(String(50), default='active', doc="Party status (e.g., 'active', 'disbanded').")
    inventory: Mapped[dict] = mapped_column(JSON, default=dict, doc="Shared party inventory.")
    quest_log: Mapped[dict] = mapped_column(JSON, default=dict, doc="Active and completed quests.")
    max_size: Mapped[int] = mapped_column(Integer, default=4, doc="Maximum party size.")

    leader_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('characters.id', use_alter=True, name='fk_party_leader'), doc="Foreign key to leader character.")
    region_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('regions.id', use_alter=True, name='fk_party_region'), doc="Foreign key to region.")

    leader: Mapped[Optional['Character']] = relationship('Character', foreign_keys=[leader_id], back_populates='led_party')
    members: Mapped[List['Character']] = relationship('Character', back_populates='party', foreign_keys='Character.party_id', cascade='all, delete-orphan')
    region: Mapped[Optional['Region']] = relationship('Region', back_populates='parties', foreign_keys=[region_id])

    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, doc="SHA-256 checksum for integrity.")
    schema_version: Mapped[str] = mapped_column(String(16), nullable=False, default='1.0.0', doc="Schema version for versioning.")

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
            'checksum': self.checksum,
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