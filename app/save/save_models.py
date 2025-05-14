"""
Save model definitions.
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON, DateTime, Boolean, Float, ForeignKey
from datetime import datetime
from app.core.database import db

class SaveGame(db.Model):
    """Save game model for storing game states."""
    __tablename__ = 'save_games'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    character_id: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    game_state: Mapped[dict] = mapped_column(JSON, nullable=False)  # Complete game state
    location: Mapped[dict] = mapped_column(JSON, nullable=False)  # Current location data
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_auto_save: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert save game to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'character_id': self.character_id,
            'name': self.name,
            'description': self.description,
            'game_state': self.game_state,
            'location': self.location,
            'timestamp': self.timestamp.isoformat(),
            'is_auto_save': self.is_auto_save,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update_state(self, new_state: dict) -> None:
        """Update the game state."""
        self.game_state.update(new_state)
        self.updated_at = datetime.utcnow()

class SaveMetadata(db.Model):
    """Save metadata model for storing save-related information."""
    __tablename__ = 'save_metadata'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    save_id: Mapped[int] = mapped_column(Integer, nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert save metadata to dictionary."""
        return {
            'id': self.id,
            'save_id': self.save_id,
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update_value(self, new_value: str) -> None:
        """Update the metadata value."""
        self.value = new_value
        self.updated_at = datetime.utcnow()

class SaveBackup(db.Model):
    """Save backup model for storing backup copies of saves."""
    __tablename__ = 'save_backups'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    save_id: Mapped[int] = mapped_column(Integer, nullable=False)
    backup_data: Mapped[dict] = mapped_column(JSON, nullable=False)  # Complete backup data
    reason: Mapped[str] = mapped_column(String(200), nullable=True)  # Reason for backup
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert save backup to dictionary."""
        return {
            'id': self.id,
            'save_id': self.save_id,
            'backup_data': self.backup_data,
            'reason': self.reason,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def restore(self) -> dict:
        """Get the backup data for restoration."""
        return self.backup_data

class SaveSlot(db.Model):
    """Save slot model for storing multiple save games."""
    __tablename__ = 'save_slots'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_number: Mapped[int] = mapped_column(Integer, nullable=False)
    save_game_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert save slot to dictionary."""
        return {
            'id': self.id,
            'slot_number': self.slot_number,
            'save_game_id': self.save_game_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def activate(self) -> bool:
        """Activate this save slot."""
        self.is_active = True
        self.updated_at = datetime.utcnow()
        return True

    def deactivate(self) -> bool:
        """Deactivate this save slot."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        return True

class GameState(db.Model):
    """Game state model for storing the current game state."""
    __tablename__ = 'game_states'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    save_id: Mapped[int] = mapped_column(Integer, ForeignKey('save_games.id'), nullable=False)
    state_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert game state to dictionary."""
        return {
            'id': self.id,
            'save_id': self.save_id,
            'state_data': self.state_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SaveManager:
    """Manager class for handling save operations."""
    
    @staticmethod
    def create_save(user_id: int, character_id: int, game_state: dict) -> dict:
        """Create a new save game."""
        save = SaveGame(
            user_id=user_id,
            character_id=character_id,
            game_state=game_state,
            timestamp=datetime.utcnow()
        )
        db.session.add(save)
        db.session.commit()
        return save.to_dict()
    
    @staticmethod
    def load_save(save_id: int) -> dict:
        """Load a save game by ID."""
        save = SaveGame.query.get(save_id)
        if not save:
            raise ValueError(f"Save game {save_id} not found")
        return save.to_dict()
    
    @staticmethod
    def delete_save(save_id: int) -> bool:
        """Delete a save game by ID."""
        save = SaveGame.query.get(save_id)
        if not save:
            return False
        db.session.delete(save)
        db.session.commit()
        return True 