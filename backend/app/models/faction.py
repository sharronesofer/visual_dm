from sqlalchemy import Column, String, Integer, Float, Enum, Text, Boolean, JSON, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
import enum
from backend.app.models.base import BaseModel

class FactionAlignment(enum.Enum):
    LAWFUL_GOOD = "lawful_good"
    NEUTRAL_GOOD = "neutral_good"
    CHAOTIC_GOOD = "chaotic_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    TRUE_NEUTRAL = "true_neutral"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_EVIL = "chaotic_evil"

class Faction(BaseModel):
    """Faction model representing groups or organizations in the game."""
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Faction properties
    alignment = Column(Enum(FactionAlignment))
    type = Column(String(50))  # Type of faction (e.g., "guild", "kingdom", "tribe")
    
    # Leadership and hierarchy
    leader_id = Column(Integer, ForeignKey('npc.id'), nullable=True)
    leader = relationship("NPC", foreign_keys=[leader_id])
    leadership_structure = Column(JSON)  # Leadership roles and members
    parent_faction_id = Column(Integer, ForeignKey('faction.id'), nullable=True)
    parent_faction = relationship("Faction", remote_side="Faction.id", backref="subfactions")
    
    # Territory and resources
    headquarters_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    headquarters = relationship("Location", foreign_keys=[headquarters_id])
    territories = Column(JSON)  # Controlled territories and their data
    resources = Column(JSON)  # Available resources and their states
    
    # Members
    members = relationship("NPC", back_populates="faction", foreign_keys="NPC.faction_id")
    required_reputation_join = Column(Integer, default=0)
    
    # Reputation levels
    reputation_levels = Column(JSON)  # Threshold values and names for reputation levels
    
    # Economic data
    wealth = Column(Integer, default=0)
    income = Column(Integer, default=0)  # Per game day
    expenses = Column(Integer, default=0)  # Per game day
    tax_rate = Column(Float, default=0.0)  # Base tax rate
    
    # Relationships with other factions
    relationships = Column(JSON)  # Dictionary of relationships with other factions
    
    # Faction goals and behavior
    goals = Column(JSON)  # List of goals and objectives
    
    # Cultural aspects
    culture = Column(JSON)  # Values, traditions, etc.
    
    # Current state
    is_active = Column(Boolean, default=True)
    influence = Column(Integer, default=50)  # 0-100, overall world influence
    
    # Historical data
    founding_date = Column(DateTime)
    major_events = Column(JSON)  # List of significant historical events
    
    def __repr__(self):
        return f"<Faction {self.name} ({self.type})>" 