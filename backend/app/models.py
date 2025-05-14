from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, DateTime, Boolean, Text, Float, JSON, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.sql import text
from sqlalchemy.orm import foreign, remote
import enum
from datetime import datetime
import re
from typing import List, Optional, Dict, Any

Base = declarative_base()

# Association tables
character_quests = Table('character_quests', Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('quest_id', Integer, ForeignKey('quests.id'), primary_key=True)
)

character_factions = Table('character_factions', Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('faction_id', Integer, ForeignKey('factions.id'), primary_key=True)
)

class Race(str, enum.Enum):
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    HALFLING = "Halfling"
    GNOME = "Gnome"
    HALF_ELF = "Half-Elf"
    HALF_ORC = "Half-Orc"
    TIEFLING = "Tiefling"
    AASIMAR = "Aasimar"
    DRAGONBORN = "Dragonborn"

class Class(str, enum.Enum):
    BARBARIAN = "Barbarian"
    BARD = "Bard"
    CLERIC = "Cleric"
    DRUID = "Druid"
    FIGHTER = "Fighter"
    MONK = "Monk"
    PALADIN = "Paladin"
    RANGER = "Ranger"
    ROGUE = "Rogue"
    SORCERER = "Sorcerer"
    WARLOCK = "Warlock"
    WIZARD = "Wizard"

class Alignment(str, enum.Enum):
    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"

class Faction(Base):
    __tablename__ = 'factions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    alignment = Column(Enum(Alignment), nullable=False)
    headquarters = Column(String(200))
    leader_id = Column(Integer, ForeignKey('characters.id'))
    parent_faction_id = Column(Integer, ForeignKey('factions.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    leader = relationship("Character", foreign_keys=[leader_id])
    parent_faction = relationship("Faction", remote_side=[id], backref="subfactions")
    members = relationship("Character", secondary=character_factions, back_populates="factions")
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) == 0:
            raise ValueError("Faction name cannot be empty")
        return name.strip()

class Quest(Base):
    __tablename__ = 'quests'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    level_requirement = Column(Integer, nullable=False)
    reward_gold = Column(Integer, nullable=False)
    reward_xp = Column(Integer, nullable=False)
    faction_id = Column(Integer, ForeignKey('factions.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    faction = relationship("Faction", backref="quests")
    characters = relationship("Character", secondary=character_quests, back_populates="quests")
    
    @validates('title')
    def validate_title(self, key, title):
        if not title or len(title.strip()) == 0:
            raise ValueError("Quest title cannot be empty")
        return title.strip()
    
    @validates('level_requirement')
    def validate_level_requirement(self, key, level):
        if level < 1:
            raise ValueError("Level requirement must be at least 1")
        return level
    
    @validates('reward_gold', 'reward_xp')
    def validate_rewards(self, key, value):
        if value < 0:
            raise ValueError(f"{key} cannot be negative")
        return value

class Character(Base):
    """Character model."""
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    race = Column(String(50), nullable=False)
    background = Column(String(50), nullable=False)
    strength = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    constitution = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    quests = relationship("Quest", secondary=character_quests, back_populates="characters")
    factions = relationship("Faction", secondary=character_factions, back_populates="members")
    led_factions = relationship("Faction", foreign_keys=[Faction.leader_id], back_populates="leader")
    
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) == 0:
            raise ValueError("Character name cannot be empty")
        return name.strip()
    
    @validates('level')
    def validate_level(self, key, level):
        if level < 1:
            raise ValueError("Level must be at least 1")
        return level 