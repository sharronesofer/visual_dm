"""
Diplomacy model definitions.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Dict, Any, Optional

Base = declarative_base()

class DiplomacyModel(Base):
    """Base model for diplomacy system."""
    
    __tablename__ = "diplomacy_entities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiplomacyModel':
        """Create model from dictionary."""
        return cls(
            name=data.get('name'),
            description=data.get('description')
        )
