import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from backend.systems.game_time.models.time_model import (
    GameTime, Calendar, TimeConfig, TimeEvent, EventType, Season
)

class TimeRepository:
    """
    Repository for persisting time-related data (game time, calendar, events).
    
    Provides methods for loading and saving time system state.
    """
    
    def __init__(self, data_dir: str = "data/time"):
        """
        Initialize the repository with a data directory.
        
        Args:
            data_dir: Directory where time data will be stored
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.game_time_path = self.data_dir / "game_time.json"
        self.calendar_path = self.data_dir / "calendar.json"
        self.config_path = self.data_dir / "time_config.json"
        self.events_path = self.data_dir / "time_events.json"
    
    def save_game_time(self, game_time: GameTime) -> None:
        """
        Save the current game time to disk.
        
        Args:
            game_time: The game time to save
        """
        with open(self.game_time_path, "w") as f:
            json.dump(game_time.dict(), f, indent=2)
    
    def load_game_time(self) -> Optional[GameTime]:
        """
        Load the game time from disk.
        
        Returns:
            GameTime: The loaded game time, or None if not found
        """
        if not self.game_time_path.exists():
            return None
        
        try:
            with open(self.game_time_path, "r") as f:
                data = json.load(f)
                return GameTime(**data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def save_calendar(self, calendar: Calendar) -> None:
        """
        Save the calendar configuration to disk.
        
        Args:
            calendar: The calendar configuration to save
        """
        with open(self.calendar_path, "w") as f:
            json.dump(calendar.dict(), f, indent=2)
    
    def load_calendar(self) -> Optional[Calendar]:
        """
        Load the calendar configuration from disk.
        
        Returns:
            Calendar: The loaded calendar, or None if not found
        """
        if not self.calendar_path.exists():
            return None
        
        try:
            with open(self.calendar_path, "r") as f:
                data = json.load(f)
                return Calendar(**data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def save_config(self, config: TimeConfig) -> None:
        """
        Save the time system configuration to disk.
        
        Args:
            config: The time configuration to save
        """
        with open(self.config_path, "w") as f:
            json.dump(config.dict(), f, indent=2)
    
    def load_config(self) -> Optional[TimeConfig]:
        """
        Load the time system configuration from disk.
        
        Returns:
            TimeConfig: The loaded configuration, or None if not found
        """
        if not self.config_path.exists():
            return None
        
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                return TimeConfig(**data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def save_events(self, events: List[TimeEvent]) -> None:
        """
        Save the time events to disk.
        
        Args:
            events: List of time events to save
        """
        event_dicts = [event.dict() for event in events]
        
        # Convert datetime objects to strings
        for event_dict in event_dicts:
            if "next_trigger_time" in event_dict:
                event_dict["next_trigger_time"] = event_dict["next_trigger_time"].isoformat()
            if "created_at" in event_dict:
                event_dict["created_at"] = event_dict["created_at"].isoformat()
            if "recurrence_interval" in event_dict and event_dict["recurrence_interval"]:
                # Convert timedelta to seconds
                event_dict["recurrence_interval"] = event_dict["recurrence_interval"].total_seconds()
        
        with open(self.events_path, "w") as f:
            json.dump(event_dicts, f, indent=2)
    
    def load_events(self) -> List[TimeEvent]:
        """
        Load the time events from disk.
        
        Returns:
            List[TimeEvent]: The loaded events, or empty list if not found
        """
        if not self.events_path.exists():
            return []
        
        try:
            with open(self.events_path, "r") as f:
                event_dicts = json.load(f)
                
                # Convert string dates back to datetime objects
                from datetime import datetime, timedelta
                for event_dict in event_dicts:
                    if "next_trigger_time" in event_dict:
                        event_dict["next_trigger_time"] = datetime.fromisoformat(event_dict["next_trigger_time"])
                    if "created_at" in event_dict:
                        event_dict["created_at"] = datetime.fromisoformat(event_dict["created_at"])
                    if "recurrence_interval" in event_dict and event_dict["recurrence_interval"]:
                        # Convert seconds back to timedelta
                        event_dict["recurrence_interval"] = timedelta(seconds=float(event_dict["recurrence_interval"]))
                
                return [TimeEvent(**event_dict) for event_dict in event_dicts]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_all(self, game_time: GameTime, calendar: Calendar, config: TimeConfig, events: List[TimeEvent]) -> None:
        """
        Save all time system state to disk.
        
        Args:
            game_time: Current game time
            calendar: Calendar configuration
            config: Time system configuration
            events: List of active time events
        """
        self.save_game_time(game_time)
        self.save_calendar(calendar)
        self.save_config(config)
        self.save_events(events)
    
    def load_all(self) -> Dict[str, Any]:
        """
        Load all time system state from disk.
        
        Returns:
            Dict containing game_time, calendar, config, and events
        """
        return {
            "game_time": self.load_game_time(),
            "calendar": self.load_calendar(),
            "config": self.load_config(),
            "events": self.load_events()
        }
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """
        Create a backup of all time system data.
        
        Args:
            backup_name: Optional name for the backup (default: timestamp)
            
        Returns:
            Path to the backup directory
        """
        if backup_name is None:
            backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = self.data_dir / "backups" / backup_name
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files to backup directory
        for file_path in [self.game_time_path, self.calendar_path, self.config_path, self.events_path]:
            if file_path.exists():
                backup_file = backup_dir / file_path.name
                backup_file.write_bytes(file_path.read_bytes())
        
        return str(backup_dir)
    
    def restore_backup(self, backup_name: str) -> bool:
        """
        Restore time system data from a backup.
        
        Args:
            backup_name: Name of the backup to restore
            
        Returns:
            True if successful, False otherwise
        """
        backup_dir = self.data_dir / "backups" / backup_name
        
        if not backup_dir.exists():
            return False
        
        # Copy all files from backup directory
        for file_path in backup_dir.glob("*.json"):
            target_path = self.data_dir / file_path.name
            target_path.write_bytes(file_path.read_bytes())
        
        return True
    
    def get_available_backups(self) -> List[str]:
        """
        Get a list of available backup names.
        
        Returns:
            List of backup names
        """
        backup_dir = self.data_dir / "backups"
        
        if not backup_dir.exists():
            return []
        
        return [d.name for d in backup_dir.iterdir() if d.is_dir()] 