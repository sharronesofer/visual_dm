"""
Save system for managing game saves.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy import String, Integer, JSON, ForeignKey, DateTime, func
from datetime import datetime
import json
import os
from app.core.database import db
from app.core.models.character import Character
from app.core.models.user import User
from pathlib import Path
from app.core.models.game_state import GameState

class SaveGame(db.Model):
    """Model for game saves."""
    __tablename__ = 'saves'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(1000))
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id', ondelete='CASCADE'))
    game_state: Mapped[Dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    player = relationship("User", back_populates="saves")
    character = relationship("Character", back_populates="saves")

    def to_dict(self) -> Dict:
        """Convert the save to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'player_id': self.player_id,
            'character_id': self.character_id,
            'game_state': self.game_state,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SaveManager:
    """Manager for handling game saves."""
    def __init__(self, save_dir: str = "saves"):
        self.save_dir = Path(save_dir)
        self._ensure_save_directory()
        self.saves: Dict[int, SaveGame] = {}
        self.db = db.session

    def _ensure_save_directory(self):
        """Ensure the save directory exists."""
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def create_save(self, name: str, description: str, player_id: int, 
                   character_id: int, game_state: GameState) -> SaveGame:
        """Create a new save game."""
        save = SaveGame(
            name=name,
            description=description,
            player_id=player_id,
            character_id=character_id,
            game_state=game_state.dict()
        )
        self.db.add(save)
        self.db.commit()
        self.saves[save.id] = save
        self._save_to_file(save)
        return save

    def load_save(self, save_id: int) -> Optional[GameState]:
        """Load a save game."""
        if save_id in self.saves:
            return GameState(**self.saves[save_id].game_state)
        save = self.db.query(SaveGame).get(save_id)
        if save:
            self.saves[save.id] = save
            return GameState(**save.game_state)
        return None

    def update_save(self, save_id: int, game_state: GameState) -> bool:
        """Update an existing save game."""
        save = self.db.query(SaveGame).get(save_id)
        if save:
            save.game_state = game_state.dict()
            save.updated_at = datetime.now()
            self.db.commit()
            self.saves[save.id] = save
            self._save_to_file(save)
            return True
        return False

    def delete_save(self, save_id: int) -> bool:
        """Delete a save game."""
        save = self.db.query(SaveGame).get(save_id)
        if save:
            self.db.delete(save)
            self.db.commit()
            if save_id in self.saves:
                del self.saves[save_id]
            save_file = self.save_dir / f"{save_id}.json"
            if save_file.exists():
                save_file.unlink()
            return True
        return False

    def list_saves(self, player_id: Optional[int] = None) -> List[SaveGame]:
        """List all save games, optionally filtered by player_id."""
        query = self.db.query(SaveGame)
        if player_id is not None:
            query = query.filter(SaveGame.player_id == player_id)
        saves = query.all()
        for save in saves:
            self.saves[save.id] = save
        return saves

    def get_latest_save(self, player_id: int) -> Optional[SaveGame]:
        """Get the most recent save for a player."""
        save = (self.db.query(SaveGame)
                .filter(SaveGame.player_id == player_id)
                .order_by(SaveGame.updated_at.desc())
                .first())
        if save:
            self.saves[save.id] = save
        return save

    def _save_to_file(self, save: SaveGame) -> None:
        """Save game state to a file."""
        save_file = self.save_dir / f"{save.id}.json"
        with open(save_file, "w") as f:
            json.dump(save.game_state, f, indent=2)

    def _load_from_file(self, save_id: int) -> Optional[Dict]:
        """Load game state from a file."""
        save_file = self.save_dir / f"{save_id}.json"
        if save_file.exists():
            with open(save_file, "r") as f:
                return json.load(f)
        return None

    def create_backup(self, save_id: int) -> bool:
        """Create a backup of a save game."""
        save = self.load_save(save_id)
        if not save:
            return False

        backup_path = self.save_dir / f"save_{save_id}_backup_{int(datetime.utcnow().timestamp())}.json"
        with open(backup_path, 'w') as f:
            json.dump(save.dict(), f, indent=2)
        return True

    def restore_backup(self, backup_path: str) -> Optional[SaveGame]:
        """Restore a save game from a backup file."""
        backup_file = Path(backup_path)
        if not backup_file.exists():
            return None

        with open(backup_file, 'r') as f:
            data = json.load(f)
            save = SaveGame(**data)
            self.db.add(save)
            self.db.commit()
            self.saves[save.id] = save
            self._save_to_file(save)
            return save 