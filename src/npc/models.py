from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, Float, UniqueConstraint, Time
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column
from app.models.base import BaseModel, UUIDMixin
from datetime import datetime, time
from typing import Optional, List

class NPC(BaseModel, UUIDMixin):
    """
    NPC database model representing a non-player character.
    Fields:
        name (str): NPC's name.
        is_active (bool): Whether the NPC is active.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        traits (List[NPCTrait]): List of personality traits.
        relationships (List[NPCRelationship]): List of relationships.
    """
    __tablename__ = 'npc'

    name: Mapped[str] = mapped_column(String(128), nullable=False, doc="NPC's name.")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, doc="Whether the NPC is active.")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, doc="Creation timestamp.")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, doc="Last update timestamp.")

    traits: Mapped[List['NPCTrait']] = relationship('NPCTrait', back_populates='npc', cascade='all, delete-orphan')
    relationships: Mapped[List['NPCRelationship']] = relationship('NPCRelationship', back_populates='npc', cascade='all, delete-orphan')

class NPCTrait(BaseModel):
    """
    Personality trait for an NPC.
    Fields:
        id (int): Primary key.
        npc_id (str): Foreign key to NPC.
        trait_type (str): Type of trait.
        value (float): Trait value.
        npc (NPC): Related NPC.
    """
    __tablename__ = 'npc_trait'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    npc_id: Mapped[str] = mapped_column(String, ForeignKey('npc.id', ondelete='CASCADE'), nullable=False, doc="Foreign key to NPC.")
    trait_type: Mapped[str] = mapped_column(String(64), nullable=False, doc="Type of trait.")
    value: Mapped[float] = mapped_column(Float, nullable=False, doc="Trait value.")

    npc: Mapped['NPC'] = relationship('NPC', back_populates='traits')
    __table_args__ = (UniqueConstraint('npc_id', 'trait_type', name='_npc_trait_uc'),)

class NPCRelationship(BaseModel):
    """
    Relationship between two NPCs or an NPC and the player.
    Fields:
        id (int): Primary key.
        npc_id (str): Foreign key to NPC.
        target_id (str): Target entity (NPC or player).
        relationship_type (str): Type of relationship.
        value (float): Relationship value.
        npc (NPC): Related NPC.
    """
    __tablename__ = 'npc_relationship'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    npc_id: Mapped[str] = mapped_column(String, ForeignKey('npc.id', ondelete='CASCADE'), nullable=False, doc="Foreign key to NPC.")
    target_id: Mapped[str] = mapped_column(String, nullable=False, doc="Target entity (NPC or player).")
    relationship_type: Mapped[str] = mapped_column(String(64), nullable=False, doc="Type of relationship.")
    value: Mapped[float] = mapped_column(Float, nullable=False, doc="Relationship value.")

    npc: Mapped['NPC'] = relationship('NPC', back_populates='relationships')
    __table_args__ = (UniqueConstraint('npc_id', 'target_id', 'relationship_type', name='_npc_relationship_uc'),)

class NPCSchedule(BaseModel):
    """
    Daily schedule for an NPC, consisting of multiple events.
    Fields:
        id (int): Primary key.
        npc_id (str): Foreign key to NPC.
        day_of_week (int): Day of the week (0=Monday, 6=Sunday).
        events (List[NPCScheduleEvent]): List of schedule events.
        npc (NPC): Related NPC.
    """
    __tablename__ = 'npc_schedule'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    npc_id: Mapped[str] = mapped_column(String, ForeignKey('npc.id', ondelete='CASCADE'), nullable=False, doc="Foreign key to NPC.")
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False, doc="Day of the week (0=Monday, 6=Sunday).")
    events: Mapped[List['NPCScheduleEvent']] = relationship('NPCScheduleEvent', back_populates='schedule', cascade='all, delete-orphan')

    npc: Mapped['NPC'] = relationship('NPC', backref=backref('schedules', cascade='all, delete-orphan'))
    __table_args__ = (UniqueConstraint('npc_id', 'day_of_week', name='_npc_schedule_uc'),)

class NPCScheduleEvent(BaseModel):
    """
    An event in an NPC's daily schedule (e.g., work, sleep, special event).
    Fields:
        id (int): Primary key.
        schedule_id (int): Foreign key to NPCSchedule.
        start_time (time): Event start time.
        end_time (time): Event end time.
        activity (str): Activity name.
        location (str): Location name.
        event_type (str): Event type (e.g., 'routine', 'special').
        schedule (NPCSchedule): Related schedule.
    """
    __tablename__ = 'npc_schedule_event'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey('npc_schedule.id', ondelete='CASCADE'), nullable=False, doc="Foreign key to NPCSchedule.")
    start_time: Mapped[time] = mapped_column(Time, nullable=False, doc="Event start time.")
    end_time: Mapped[time] = mapped_column(Time, nullable=False, doc="Event end time.")
    activity: Mapped[str] = mapped_column(String(64), nullable=False, doc="Activity name.")
    location: Mapped[str] = mapped_column(String(128), nullable=False, doc="Location name.")
    event_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, doc="Event type (e.g., 'routine', 'special').")

    schedule: Mapped['NPCSchedule'] = relationship('NPCSchedule', back_populates='events')
