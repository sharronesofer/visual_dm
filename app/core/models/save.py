"""
Save game model for tracking game saves.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class SaveGame(BaseModel):
    """Model for game saves."""
    __tablename__ = 'save_games'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    version = Column(String(20))
    is_auto_save = Column(Boolean, default=False)
    game_state = Column(JSON, default=dict)  # Complete game state
    character_data = Column(JSON, default=dict)  # Character states
    world_state = Column(JSON, default=dict)  # World state
    quest_progress = Column(JSON, default=dict)  # Quest progress
    inventory = Column(JSON, default=dict)  # Inventory states
    combat_state = Column(JSON, default=dict)  # Combat states
    settings = Column(JSON, default=dict)  # Game settings
    save_metadata = Column(JSON, default=dict)  # Additional metadata
    
    # Foreign Keys
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    user = relationship('User', back_populates='save_games')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'is_auto_save': self.is_auto_save,
            'game_state': self.game_state,
            'character_data': self.character_data,
            'world_state': self.world_state,
            'quest_progress': self.quest_progress,
            'inventory': self.inventory,
            'combat_state': self.combat_state,
            'settings': self.settings,
            'save_metadata': self.save_metadata,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 