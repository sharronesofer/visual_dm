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
    character_class = Column(String(50), nullable=False)
    level = Column(Integer, default=1)
    stats = Column(JSON, nullable=False)  # Stores ability scores, HP, etc.
    background = Column(String(100))
    alignment = Column(String(50))
    equipment = Column(JSON, default=list)  # List of equipment items
    skills = relationship('Skill', secondary=character_skills, backref='characters')
    notes = Column(JSON, default=list)  # Character-specific notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Character {self.name}>"

class Skill(Base):
    __tablename__ = 'skills'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    ability = Column(String(50))  # Associated ability score
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Skill {self.name}>" 