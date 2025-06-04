"""
Persistence Service for the Time System

Handles saving and loading of time system state to/from files.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from backend.systems.game_time.models.time_model import (
    GameTime, Calendar, TimeConfig  # Weather, TimeEvent - moved to separate systems
)

logger = logging.getLogger(__name__)


class PersistenceService:
    """
    Handles persistence operations for the time system.
    
    Saves and loads game time, calendar, configuration, and weather state.
    """
    
    def __init__(self, save_directory: str = "data/game_time"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.game_time_file = self.save_directory / "game_time.json"
        self.calendar_file = self.save_directory / "calendar.json"
        self.config_file = self.save_directory / "config.json"
        self.weather_file = self.save_directory / "weather.json"
        self.events_file = self.save_directory / "events.json"
    
    def save_game_time(self, game_time: GameTime) -> bool:
        """
        Save the current game time state.
        
        Args:
            game_time: GameTime object to save
            
        Returns:
            bool: True if successful
        """
        try:
            data = {
                "year": game_time.year,
                "month": game_time.month,
                "day": game_time.day,
                "hour": game_time.hour,
                "minute": game_time.minute,
                "second": game_time.second,
                "tick": game_time.tick,
                "time_scale": game_time.time_scale,
                "is_paused": game_time.is_paused,
                "total_game_seconds": game_time.total_game_seconds,
                "season": game_time.season.value,
                "current_datetime": game_time.current_datetime.isoformat(),
                "saved_at": datetime.utcnow().isoformat()
            }
            
            with open(self.game_time_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Game time saved to {self.game_time_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save game time: {e}")
            return False
    
    def load_game_time(self) -> Optional[GameTime]:
        """
        Load game time state from file.
        
        Returns:
            GameTime object if successful, None otherwise
        """
        try:
            if not self.game_time_file.exists():
                logger.warning(f"Game time file not found: {self.game_time_file}")
                return None
            
            with open(self.game_time_file, 'r') as f:
                data = json.load(f)
            
            # Import Season enum here to avoid circular imports
            from backend.systems.game_time.models.time_model import Season
            
            game_time = GameTime(
                year=data["year"],
                month=data["month"],
                day=data["day"],
                hour=data["hour"],
                minute=data["minute"],
                second=data["second"],
                tick=data["tick"],
                time_scale=data["time_scale"],
                is_paused=data["is_paused"],
                total_game_seconds=data["total_game_seconds"],
                season=Season(data["season"]),
                current_datetime=datetime.fromisoformat(data["current_datetime"])
            )
            
            logger.info(f"Game time loaded from {self.game_time_file}")
            return game_time
            
        except Exception as e:
            logger.error(f"Failed to load game time: {e}")
            return None
    
    def save_calendar(self, calendar: Calendar) -> bool:
        """
        Save calendar state.
        
        Args:
            calendar: Calendar object to save
            
        Returns:
            bool: True if successful
        """
        try:
            data = {
                "days_per_month": calendar.days_per_month,
                "months_per_year": calendar.months_per_year,
                "hours_per_day": calendar.hours_per_day,
                "minutes_per_hour": calendar.minutes_per_hour,
                "has_leap_year": calendar.has_leap_year,
                "leap_year_interval": calendar.leap_year_interval,
                "current_season": calendar.current_season.value,
                "current_day_of_year": calendar.current_day_of_year,
                "important_dates": calendar.important_dates,
                "saved_at": datetime.utcnow().isoformat()
            }
            
            with open(self.calendar_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Calendar saved to {self.calendar_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save calendar: {e}")
            return False
    
    def load_calendar(self) -> Optional[Calendar]:
        """
        Load calendar state from file.
        
        Returns:
            Calendar object if successful, None otherwise
        """
        try:
            if not self.calendar_file.exists():
                logger.warning(f"Calendar file not found: {self.calendar_file}")
                return None
            
            with open(self.calendar_file, 'r') as f:
                data = json.load(f)
            
            # Import Season enum here to avoid circular imports
            from backend.systems.game_time.models.time_model import Season
            
            calendar = Calendar(
                days_per_month=data["days_per_month"],
                months_per_year=data["months_per_year"],
                hours_per_day=data["hours_per_day"],
                minutes_per_hour=data["minutes_per_hour"],
                has_leap_year=data["has_leap_year"],
                leap_year_interval=data["leap_year_interval"],
                current_season=Season(data["current_season"]),
                current_day_of_year=data["current_day_of_year"],
                important_dates=data["important_dates"]
            )
            
            logger.info(f"Calendar loaded from {self.calendar_file}")
            return calendar
            
        except Exception as e:
            logger.error(f"Failed to load calendar: {e}")
            return None
    
    def save_config(self, config: TimeConfig) -> bool:
        """
        Save time configuration.
        
        Args:
            config: TimeConfig object to save
            
        Returns:
            bool: True if successful
        """
        try:
            data = {
                "real_seconds_per_game_hour": config.real_seconds_per_game_hour,
                "ticks_per_second": config.ticks_per_second,
                "time_scale": config.time_scale,
                "is_paused": config.is_paused,
                "enable_seasonal_events": config.enable_seasonal_events,
                "enable_weather_system": config.enable_weather_system,
                "weather_change_frequency_hours": config.weather_change_frequency_hours,
                "weather_seasonal_influence": config.weather_seasonal_influence,
                "weather_randomness": config.weather_randomness,
                "auto_save_interval": config.auto_save_interval,
                "saved_at": datetime.utcnow().isoformat()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Config saved to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def load_config(self) -> Optional[TimeConfig]:
        """
        Load time configuration from file.
        
        Returns:
            TimeConfig object if successful, None otherwise
        """
        try:
            if not self.config_file.exists():
                logger.warning(f"Config file not found: {self.config_file}")
                return None
            
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            config = TimeConfig(
                real_seconds_per_game_hour=data["real_seconds_per_game_hour"],
                ticks_per_second=data["ticks_per_second"],
                time_scale=data["time_scale"],
                is_paused=data["is_paused"],
                enable_seasonal_events=data["enable_seasonal_events"],
                enable_weather_system=data["enable_weather_system"],
                weather_change_frequency_hours=data["weather_change_frequency_hours"],
                weather_seasonal_influence=data["weather_seasonal_influence"],
                weather_randomness=data["weather_randomness"],
                auto_save_interval=data["auto_save_interval"]
            )
            
            logger.info(f"Config loaded from {self.config_file}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return None
    
    # TODO: Weather system moved to separate module
    # def save_weather(self, weather: Weather) -> bool:
    #     """Save weather state."""
    #     pass
    
    # def load_weather(self) -> Optional[Weather]:
    #     """Load weather state from file."""
    #     pass
    
    def save_all(self, game_time: GameTime, calendar: Calendar, 
                 config: TimeConfig) -> bool:  # removed weather parameter
        """
        Save all time system state.
        
        Args:
            game_time: GameTime object to save
            calendar: Calendar object to save
            config: TimeConfig object to save
            
        Returns:
            bool: True if all saves successful
        """
        try:
            success = True
            success &= self.save_game_time(game_time)
            success &= self.save_calendar(calendar)
            success &= self.save_config(config)
            # success &= self.save_weather(weather)  # TODO: Re-enable when weather system integrated
            
            if success:
                logger.info("All time system state saved successfully")
            else:
                logger.warning("Some time system saves failed")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to save all time system state: {e}")
            return False
    
    def load_all(self) -> Dict[str, Any]:
        """
        Load all time system state.
        
        Returns:
            Dictionary with loaded objects (may contain None values)
        """
        return {
            "game_time": self.load_game_time(),
            "calendar": self.load_calendar(),
            "config": self.load_config(),
            # "weather": self.load_weather()  # TODO: Re-enable when weather system integrated
        }
    
    def backup_saves(self, backup_suffix: str = None) -> bool:
        """
        Create backup copies of all save files.
        
        Args:
            backup_suffix: Optional suffix for backup files
            
        Returns:
            bool: True if successful
        """
        if backup_suffix is None:
            backup_suffix = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        try:
            backup_dir = self.save_directory / f"backups_{backup_suffix}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            files_to_backup = [
                self.game_time_file,
                self.calendar_file,
                self.config_file,
                self.weather_file,
                self.events_file
            ]
            
            for file_path in files_to_backup:
                if file_path.exists():
                    backup_path = backup_dir / file_path.name
                    backup_path.write_text(file_path.read_text())
            
            logger.info(f"Backup created in {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10) -> None:
        """
        Remove old backup directories, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backup directories to keep
        """
        try:
            backup_dirs = [d for d in self.save_directory.iterdir() 
                          if d.is_dir() and d.name.startswith("backups_")]
            
            # Sort by modification time (newest first)
            backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            for old_backup in backup_dirs[keep_count:]:
                import shutil
                shutil.rmtree(old_backup)
                logger.info(f"Removed old backup: {old_backup}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
    
    def get_save_info(self) -> Dict[str, Any]:
        """
        Get information about existing save files.
        
        Returns:
            Dictionary with save file information
        """
        info = {}
        
        files = [
            ("game_time", self.game_time_file),
            ("calendar", self.calendar_file),
            ("config", self.config_file),
            ("weather", self.weather_file),
            ("events", self.events_file)
        ]
        
        for name, file_path in files:
            if file_path.exists():
                stat = file_path.stat()
                info[name] = {
                    "exists": True,
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            else:
                info[name] = {"exists": False}
        
        return info 