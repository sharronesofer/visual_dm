"""
Faction models for the Visual DM system.

This module defines the core models for factions, including the Faction,
FactionRelationship, and FactionMembership classes.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Faction(Base):
    """
    Represents a faction in the game world.
    
    Factions are groups with shared interests, ideologies, or goals,
    such as kingdoms, guilds, or tribes.
    """
    __tablename__ = 'factions'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    type = Column(String(50))  # Maps to FactionType enum
    alignment = Column(String(50))  # Maps to FactionAlignment enum
    influence = Column(Float, default=50.0)  # 0-100 scale
    reputation = Column(Float, default=0.0)
    
    # JSON fields for rich data storage
    resources = Column(JSON, default=lambda: {
        'gold': 1000,
        'materials': {},
        'special_resources': {},
        'income_sources': [],
        'expenses': []
    })
    territory = Column(JSON, default=dict)
    relationships = Column(JSON, default=lambda: {
        'allies': [],
        'enemies': [],
        'neutral': [],
        'trade_partners': []
    })
    
    # Text fields
    history = Column(Text)
    
    # Boolean flags
    is_active = Column(Boolean, default=True)
    
    # Foreign keys
    leader_id = Column(Integer, ForeignKey('npcs.id', use_alter=True, name='fk_faction_leader'), nullable=True)
    headquarters_id = Column(Integer, ForeignKey('regions.id', use_alter=True, name='fk_faction_headquarters'), nullable=True)
    parent_faction_id = Column(Integer, ForeignKey('factions.id'), nullable=True)
    
    # Relationships
    leader = relationship('NPC', foreign_keys=[leader_id], backref='led_faction')
    headquarters = relationship('Region', backref='based_factions', foreign_keys=[headquarters_id])
    parent_faction = relationship('Faction', remote_side=[id], backref='subfactions')
    
    # Child relationships
    controlled_regions = relationship('Region', backref='controlling_faction', foreign_keys='Region.controlling_faction_id')
    members = relationship('FactionMembership', back_populates='faction')
    
    # Metrics
    power = Column(Float, default=1.0)
    wealth = Column(Float, default=1000.0)
    
    # Goals and policies
    goals = Column(JSON, default=lambda: {
        'current': [],
        'completed': [],
        'failed': []
    })
    policies = Column(JSON, default=lambda: {
        'diplomatic': {
            'aggression': 0,
            'trade_focus': 0,
            'expansion': 0
        },
        'economic': {
            'tax_rate': 10,
            'trade_tariffs': 5,
            'investment_focus': []
        },
        'military': {
            'stance': 'defensive',
            'recruitment_rate': 'normal',
            'training_focus': []
        }
    })
    
    # State tracking
    state = Column(JSON, default=lambda: {
        'active_wars': [],
        'current_projects': [],
        'recent_events': [],
        'statistics': {
            'members_count': 0,
            'territory_count': 0,
            'quest_success_rate': 0
        }
    })
    
    # World relationship
    world_id = Column(Integer, ForeignKey('worlds.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Faction(id={self.id}, name='{self.name}', type='{self.type}')>"
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "alignment": self.alignment,
            "influence": self.influence,
            "reputation": self.reputation,
            "resources": self.resources,
            "territory": self.territory,
            "relationships": self.relationships,
            "history": self.history,
            "is_active": self.is_active,
            "leader_id": self.leader_id,
            "headquarters_id": self.headquarters_id,
            "parent_faction_id": self.parent_faction_id,
            "power": self.power,
            "wealth": self.wealth,
            "goals": self.goals,
            "policies": self.policies,
            "state": self.state,
            "world_id": self.world_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class FactionRelationship(Base):
    """
    Represents a relationship between two factions.
    
    This tracks diplomatic stance, treaties, and dynamic relationships
    between any two factions.
    """
    __tablename__ = 'faction_relationships'
    
    id = Column(Integer, primary_key=True)
    
    # The two factions in the relationship
    faction_id = Column(Integer, ForeignKey('factions.id'), nullable=False)
    other_faction_id = Column(Integer, ForeignKey('factions.id'), nullable=False)
    
    # Relationship metrics
    diplomatic_stance = Column(String(50))  # Maps to DiplomaticStance enum
    tension = Column(Float, default=0.0)  # -100 (alliance) to +100 (war)
    
    # Relationship details
    treaties = Column(JSON, default=list)  # List of active treaties
    war_state = Column(JSON, default=lambda: {"at_war": False, "war_details": {}})
    
    # History and metadata
    history = Column(JSON, default=list)  # Historical relationship events
    metadata = Column(JSON, default=dict)  # Additional data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    faction = relationship('Faction', foreign_keys=[faction_id], backref='outgoing_relationships')
    other_faction = relationship('Faction', foreign_keys=[other_faction_id], backref='incoming_relationships')
    
    def __repr__(self):
        return f"<FactionRelationship(id={self.id}, faction_id={self.faction_id}, other_faction_id={self.other_faction_id}, stance='{self.diplomatic_stance}')>"
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "faction_id": self.faction_id,
            "other_faction_id": self.other_faction_id,
            "diplomatic_stance": self.diplomatic_stance,
            "tension": self.tension,
            "treaties": self.treaties,
            "war_state": self.war_state,
            "history": self.history,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class FactionMembership(Base):
    """
    Represents a character's membership in a faction.
    
    This tracks reputation, role, join date, and other metadata about
    a character's relationship with a faction.
    """
    __tablename__ = 'faction_memberships'
    
    id = Column(Integer, primary_key=True)
    
    # The faction and character
    faction_id = Column(Integer, ForeignKey('factions.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    
    # Membership details
    role = Column(String(100))  # Position/role within the faction
    rank = Column(Integer, default=0)  # Numerical rank
    reputation = Column(Float, default=0.0)  # -100 to +100
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="active")  # active, inactive, banned, etc.
    
    # Additional data
    achievements = Column(JSON, default=list)  # Achievements within this faction
    history = Column(JSON, default=list)  # History of actions/events
    metadata = Column(JSON, default=dict)  # Additional data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    faction = relationship('Faction', back_populates='members')
    character = relationship('Character', backref='faction_memberships')
    
    def __repr__(self):
        return f"<FactionMembership(id={self.id}, faction_id={self.faction_id}, character_id={self.character_id}, role='{self.role}')>"
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "faction_id": self.faction_id,
            "character_id": self.character_id,
            "role": self.role,
            "rank": self.rank,
            "reputation": self.reputation,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "is_active": self.is_active,
            "status": self.status,
            "achievements": self.achievements,
            "history": self.history,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 