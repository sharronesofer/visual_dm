"""
Save game model for tracking game saves.
"""

from typing import Dict, Any, Optional
from sqlalchemy import Integer, String, JSON, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.core.database import db
from app.core.models.base import BaseModel
from sqlalchemy.dialects.postgresql import UUID

class SaveGame(BaseModel):
    """
    Model for game saves.
    Fields:
        id (int): Primary key.
        name (str): Save name.
        description (str): Description of the save.
        version (str): Save version.
        is_auto_save (bool): Whether this is an auto-save.
        game_state (dict): Complete game state.
        character_data (dict): Character states.
        world_state (dict): World state.
        quest_progress (dict): Quest progress.
        inventory (dict): Inventory states.
        combat_state (dict): Combat states.
        settings (dict): Game settings.
        save_metadata (dict): Additional metadata.
        user_id (UUID): Foreign key to user.
        user (User): Related user.
    """
    __tablename__ = 'save_games'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, doc="Primary key.")
    name: Mapped[str] = mapped_column(String(100), nullable=False, doc="Save name.")
    description: Mapped[Optional[str]] = mapped_column(Text, doc="Description of the save.")
    version: Mapped[Optional[str]] = mapped_column(String(20), doc="Save version.")
    is_auto_save: Mapped[bool] = mapped_column(Boolean, default=False, doc="Whether this is an auto-save.")
    game_state: Mapped[dict] = mapped_column(JSON, default=dict, doc="Complete game state.")
    character_data: Mapped[dict] = mapped_column(JSON, default=dict, doc="Character states.")
    world_state: Mapped[dict] = mapped_column(JSON, default=dict, doc="World state.")
    quest_progress: Mapped[dict] = mapped_column(JSON, default=dict, doc="Quest progress.")
    inventory: Mapped[dict] = mapped_column(JSON, default=dict, doc="Inventory states.")
    combat_state: Mapped[dict] = mapped_column(JSON, default=dict, doc="Combat states.")
    settings: Mapped[dict] = mapped_column(JSON, default=dict, doc="Game settings.")
    save_metadata: Mapped[dict] = mapped_column(JSON, default=dict, doc="Additional metadata.")

    user_id: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), doc="Foreign key to user.")
    user: Mapped[Optional['User']] = relationship('User', back_populates='save_games')

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