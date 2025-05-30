from sqlalchemy import Column, String, Integer, Float, Enum, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import BaseModel

class PersonalityTrait(enum.Enum):
    BRAVE = "brave"
    COWARDLY = "cowardly"
    HONEST = "honest"
    DECEITFUL = "deceitful"
    FRIENDLY = "friendly"
    HOSTILE = "hostile"
    CURIOUS = "curious"
    CAUTIOUS = "cautious"
    GREEDY = "greedy"
    GENEROUS = "generous"
    PATIENT = "patient"
    IMPULSIVE = "impulsive"
    FORGIVING = "forgiving"
    VENGEFUL = "vengeful"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"

class NPC(BaseModel):
    """NPC model representing non-player characters in the game."""
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Character attributes
    level = Column(Integer, default=1)
    health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    
    # Personality and behavior
    profession = Column(String(50))
    personality_traits = Column(JSON)  # List of PersonalityTrait values
    dialogue_data = Column(JSON)  # Structured dialogue options
    daily_schedule = Column(JSON)  # Daily routine and schedule data
    
    # Relationships
    faction_id = Column(Integer, ForeignKey('faction.id'), nullable=True)
    faction = relationship("Faction", back_populates="members")
    location_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    location = relationship("Location", back_populates="npcs")
    
    # NPC state
    relationships = Column(JSON)  # Dictionary of relationships with other entities
    memory = Column(JSON)  # Record of significant events and interactions
    
    is_merchant = Column(Boolean, default=False)
    is_quest_giver = Column(Boolean, default=False)
    respawns = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<NPC {self.name} (Level {self.level})>" 