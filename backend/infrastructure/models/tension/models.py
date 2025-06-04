"""
Tension Database Models

SQLAlchemy models for tension state persistence following
Development Bible standards for infrastructure separation.
"""

from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TensionStateModel(Base):
    """Database model for tension state storage"""
    __tablename__ = 'tension_states'
    
    # Composite primary key: region_id + poi_id
    region_id = Column(String(100), primary_key=True, nullable=False)
    poi_id = Column(String(100), primary_key=True, nullable=False)
    
    # Tension state fields
    current_level = Column(Float, nullable=False, default=0.2)
    base_level = Column(Float, nullable=False, default=0.2)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # JSON serialized fields
    recent_events_json = Column(Text)  # JSON array of recent event IDs
    modifiers_json = Column(Text)      # JSON object of active modifiers
    
    def __repr__(self):
        return f"<TensionState(region='{self.region_id}', poi='{self.poi_id}', level={self.current_level})>" 