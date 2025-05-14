from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.models.base import BaseModel
from datetime import datetime

class Resource(BaseModel):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # e.g., food, wood, gold
    amount = Column(Float, default=0.0)
    price = Column(Float, default=1.0)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=True)
    faction_id = Column(Integer, ForeignKey('factions.id'), nullable=True)
    last_updated = Column(String(50), default=datetime.utcnow)

    region = relationship('Region', back_populates='resources')
    faction = relationship('app.core.models.faction.Faction', back_populates='resources') 