from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Float, UniqueConstraint, Time
from sqlalchemy.orm import relationship, backref
from app.models.base import BaseModel, UUIDMixin
from datetime import datetime
from typing import Optional

class NPC(BaseModel, UUIDMixin):
    """
    NPC database model representing a non-player character.
    """
    __tablename__ = 'npc'

    name = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    traits = relationship('NPCTrait', back_populates='npc', cascade='all, delete-orphan')
    relationships = relationship('NPCRelationship', back_populates='npc', cascade='all, delete-orphan')

class NPCTrait(BaseModel):
    """
    Personality trait for an NPC.
    """
    __tablename__ = 'npc_trait'
    id = Column(Integer, primary_key=True)
    npc_id = Column(String, ForeignKey('npc.id', ondelete='CASCADE'), nullable=False)
    trait_type = Column(String(64), nullable=False)
    value = Column(Float, nullable=False)

    npc = relationship('NPC', back_populates='traits')
    __table_args__ = (UniqueConstraint('npc_id', 'trait_type', name='_npc_trait_uc'),)

class NPCRelationship(BaseModel):
    """
    Relationship between two NPCs or an NPC and the player.
    """
    __tablename__ = 'npc_relationship'
    id = Column(Integer, primary_key=True)
    npc_id = Column(String, ForeignKey('npc.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(String, nullable=False)  # Could be another NPC or player UUID
    relationship_type = Column(String(64), nullable=False)
    value = Column(Float, nullable=False)

    npc = relationship('NPC', back_populates='relationships')
    __table_args__ = (UniqueConstraint('npc_id', 'target_id', 'relationship_type', name='_npc_relationship_uc'),)

class NPCSchedule(BaseModel):
    """
    Daily schedule for an NPC, consisting of multiple events.
    """
    __tablename__ = 'npc_schedule'
    id = Column(Integer, primary_key=True)
    npc_id = Column(String, ForeignKey('npc.id', ondelete='CASCADE'), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    events = relationship('NPCScheduleEvent', back_populates='schedule', cascade='all, delete-orphan')

    npc = relationship('NPC', backref=backref('schedules', cascade='all, delete-orphan'))
    __table_args__ = (UniqueConstraint('npc_id', 'day_of_week', name='_npc_schedule_uc'),)

class NPCScheduleEvent(BaseModel):
    """
    An event in an NPC's daily schedule (e.g., work, sleep, special event).
    """
    __tablename__ = 'npc_schedule_event'
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('npc_schedule.id', ondelete='CASCADE'), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    activity = Column(String(64), nullable=False)
    location = Column(String(128), nullable=False)
    event_type = Column(String(64), nullable=True)  # e.g., 'routine', 'special'

    schedule = relationship('NPCSchedule', back_populates='events')
