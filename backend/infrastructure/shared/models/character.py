from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from backend.infrastructure.database.session import Base

character_skills = Table(
    'character_skills',
    Base.metadata,
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True),
    extend_existing=True
)

class Character(Base):
    __tablename__ = 'characters'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    race = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    stats = Column(JSON, nullable=False)  # Stores ability scores, HP, etc.
    background = Column(String(100))
    alignment = Column(String(50))
    equipment = Column(JSON, default=list)  # List of equipment items
    abilities = Column(JSON, default=list)  # Character abilities (Visual DM's ability-based system)
    # Note: skills relationship will be defined in the systems layer where Skill is defined
    notes = Column(JSON, default=list)  # Character-specific notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Character {self.name}>"

# Skill class moved to backend/systems/character/models/character.py 
# to follow the development bible's clean separation of concerns 