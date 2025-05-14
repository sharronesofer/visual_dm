"""
NPC version control model for tracking changes to NPCs over time.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean, Index, UniqueConstraint, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.models.npc import NPC
from app.core.models.version_control import CodeVersion

class NPCVersion(BaseModel):
    """Model for tracking NPC versions and changes."""
    __tablename__ = 'npc_versions'
    __table_args__ = (
        Index('ix_npc_versions_npc_id', 'npc_id'),
        Index('ix_npc_versions_version_number', 'version_number'),
        UniqueConstraint('npc_id', 'version_number', name='uq_npc_versions'),
        {'extend_existing': True}
    )
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    npc_id: Mapped[int] = mapped_column(Integer, ForeignKey('npcs.id'), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    code_version_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('code_versions.id'))
    
    # Version data
    name: Mapped[str] = mapped_column(String(100))
    type: Mapped[str] = mapped_column(String(50))
    level: Mapped[int] = mapped_column(Integer)
    disposition: Mapped[str] = mapped_column(String(20))
    base_disposition: Mapped[float] = mapped_column(Float)
    level_requirement: Mapped[int] = mapped_column(Integer)
    interaction_cooldown: Mapped[int] = mapped_column(Integer)
    current_location_id: Mapped[Optional[int]] = mapped_column(Integer)
    home_location_id: Mapped[Optional[int]] = mapped_column(Integer)
    
    # JSON fields for complex data
    schedule: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    dialogue_options: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    behavior_flags: Mapped[Dict[str, bool]] = mapped_column(JSON, default=dict)
    inventory: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    trade_inventory: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    available_quests: Mapped[List[int]] = mapped_column(JSON, default=list)
    completed_quests: Mapped[List[int]] = mapped_column(JSON, default=list)
    goals: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    relationships: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    memories: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # Change tracking
    change_description: Mapped[str] = mapped_column(Text)
    change_type: Mapped[str] = mapped_column(String(50))  # update, creation, deletion, etc.
    changed_fields: Mapped[List[str]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    npc = relationship('NPC', backref='versions', foreign_keys=[npc_id])
    code_version = relationship('CodeVersion', backref='npc_versions')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule = kwargs.get('schedule', [])
        self.dialogue_options = kwargs.get('dialogue_options', {})
        self.behavior_flags = kwargs.get('behavior_flags', {})
        self.inventory = kwargs.get('inventory', [])
        self.trade_inventory = kwargs.get('trade_inventory', [])
        self.available_quests = kwargs.get('available_quests', [])
        self.completed_quests = kwargs.get('completed_quests', [])
        self.goals = kwargs.get('goals', {})
        self.relationships = kwargs.get('relationships', {})
        self.memories = kwargs.get('memories', [])
        self.changed_fields = kwargs.get('changed_fields', [])

    @classmethod
    def create_from_npc(cls, npc: NPC, change_type: str, change_description: str, 
                       changed_fields: List[str], code_version_id: Optional[int] = None) -> 'NPCVersion':
        """Create a new version from an NPC instance."""
        # Get the latest version number for this NPC
        latest_version = cls.query.filter_by(npc_id=npc.id).order_by(cls.version_number.desc()).first()
        new_version_number = (latest_version.version_number + 1) if latest_version else 1
        
        return cls(
            npc_id=npc.id,
            version_number=new_version_number,
            code_version_id=code_version_id,
            name=npc.name,
            type=npc.type.value,
            level=npc.level,
            disposition=npc.disposition.value,
            base_disposition=npc.base_disposition,
            level_requirement=npc.level_requirement,
            interaction_cooldown=npc.interaction_cooldown,
            current_location_id=npc.current_location_id,
            home_location_id=npc.home_location_id,
            schedule=npc.schedule,
            dialogue_options=npc.dialogue_options,
            behavior_flags=npc.behavior_flags,
            inventory=npc.inventory,
            trade_inventory=npc.trade_inventory,
            available_quests=npc.available_quests,
            completed_quests=npc.completed_quests,
            goals=npc.goals,
            relationships=npc.relationships,
            memories=npc.memories,
            change_type=change_type,
            change_description=change_description,
            changed_fields=changed_fields
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert version to dictionary representation."""
        return {
            'id': self.id,
            'npc_id': self.npc_id,
            'version_number': self.version_number,
            'code_version_id': self.code_version_id,
            'name': self.name,
            'type': self.type,
            'level': self.level,
            'disposition': self.disposition,
            'base_disposition': self.base_disposition,
            'level_requirement': self.level_requirement,
            'interaction_cooldown': self.interaction_cooldown,
            'current_location_id': self.current_location_id,
            'home_location_id': self.home_location_id,
            'schedule': self.schedule,
            'dialogue_options': self.dialogue_options,
            'behavior_flags': self.behavior_flags,
            'inventory': self.inventory,
            'trade_inventory': self.trade_inventory,
            'available_quests': self.available_quests,
            'completed_quests': self.completed_quests,
            'goals': self.goals,
            'relationships': self.relationships,
            'memories': self.memories,
            'change_type': self.change_type,
            'change_description': self.change_description,
            'changed_fields': self.changed_fields,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def apply_to_npc(self, npc: NPC) -> None:
        """Apply this version's data to an NPC instance."""
        npc.name = self.name
        npc.type = NPCType(self.type)
        npc.level = self.level
        npc.disposition = NPCDisposition(self.disposition)
        npc.base_disposition = self.base_disposition
        npc.level_requirement = self.level_requirement
        npc.interaction_cooldown = self.interaction_cooldown
        npc.current_location_id = self.current_location_id
        npc.home_location_id = self.home_location_id
        npc.schedule = self.schedule
        npc.dialogue_options = self.dialogue_options
        npc.behavior_flags = self.behavior_flags
        npc.inventory = self.inventory
        npc.trade_inventory = self.trade_inventory
        npc.available_quests = self.available_quests
        npc.completed_quests = self.completed_quests
        npc.goals = self.goals
        npc.relationships = self.relationships
        npc.memories = self.memories 