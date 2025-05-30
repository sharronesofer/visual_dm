"""
World State Manager

Core manager for tracking, updating and persisting world state.
Provides centralized access to world data for other systems.
"""

from typing import Dict, List, Any, Optional, Tuple
import json
import os
import time
from datetime import datetime, timedelta
import traceback
import logging
from pathlib import Path

from backend.core.utils.firebase_utils import get_firestore_client
from backend.core.utils.error_utils import NotFoundError, ValidationError
from backend.core.utils.time_utils import parse_iso_datetime
from backend.systems.integration.event_bus import integration_event_bus
from backend.systems.integration.state_sync import state_sync_manager
from backend.systems.logging.logger import logger

from backend.systems.world_state.optimized_worldgen import OptimizedWorldGenerator
from backend.systems.world_state.core.world_models import WorldMap

class WorldStateManager:
    """
    Centralized manager for world state operations.
    Handles creation, loading, updating, and persistence of world state.
    Maintains the canonical reference to the current world state.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'WorldStateManager':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = WorldStateManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the world state manager."""
        if WorldStateManager._instance is not None:
            raise RuntimeError("WorldStateManager is a singleton. Use get_instance() instead.")
        
        self.world_state = None
        self.world_generator = OptimizedWorldGenerator()
        self.db = get_firestore_client()
        self.last_update_time = None
        
        # Cache for data that doesn't change often
        self._cache = {}
        self._cache_expiry = {}
        self._default_cache_ttl = 300  # 5 minutes
        
        # Configure logging
        self.logger = logging.getLogger("world_state_manager")
        self.logger.setLevel(logging.INFO)
        
        # Register event handlers
        self._register_event_handlers()
        
        WorldStateManager._instance = self
        
        self.logger.info("WorldStateManager initialized")
    
    def _register_event_handlers(self):
        """Register handlers for world state related events."""
        integration_event_bus.subscribe("time.day_advanced", self._handle_day_advanced)
        integration_event_bus.subscribe("time.hour_advanced", self._handle_hour_advanced)
        integration_event_bus.subscribe("world.reset_requested", self._handle_world_reset)
        integration_event_bus.subscribe("save.requested", self._handle_save_request)
    
    def create_world_state(self, world_name: str, width: int = 5, height: int = 5, 
                          seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Create a new world state with the given parameters.
        
        Args:
            world_name: Name of the world
            width: Width of the world in regions
            height: Height of the world in regions
            seed: Random seed for world generation
            
        Returns:
            The newly created world state
        """
        self.logger.info(f"Creating new world: {world_name} ({width}x{height})")
        
        # Generate world using the world generator
        world_map = self.world_generator.generate_world_map(width, height, seed)
        
        # Create the world state structure
        current_time = datetime.utcnow().isoformat()
        world_state = {
            "name": world_name,
            "created_at": current_time,
            "updated_at": current_time,
            "current_date": {
                "year": 1,
                "month": 1,
                "day": 1,
                "hour": 8,
                "minute": 0
            },
            "seed": world_map.seed,
            "width": width,
            "height": height,
            "world_map": world_map.to_dict(),
            "current_weather": self._generate_initial_weather(),
            "active_events": [],
            "version": "1.0"
        }
        
        # Save to database
        self._save_world_state_to_db(world_state)
        
        # Store locally
        self.world_state = world_state
        self.last_update_time = datetime.utcnow()
        
        # Publish event
        integration_event_bus.publish("world.created", {"world_name": world_name})
        
        return world_state
    
    def get_world_state(self, reload: bool = False) -> Dict[str, Any]:
        """
        Get the current world state.
        
        Args:
            reload: Force reload from database
            
        Returns:
            World state dictionary
            
        Raises:
            NotFoundError: If no world state exists
        """
        # If we have it cached and not forcing reload, return it
        if self.world_state is not None and not reload:
            return self.world_state
            
        # Try to load from database
        try:
            world_ref = self.db.collection("world_state").document("current")
            world_doc = world_ref.get()
            
            if not world_doc.exists:
                raise NotFoundError("No world state found")
                
            self.world_state = world_doc.to_dict()
            self.last_update_time = datetime.utcnow()
            
            # Clean up and parse dates for consistency
            if "current_date" in self.world_state:
                # Ensure all expected fields are present
                date_fields = ["year", "month", "day", "hour", "minute"]
                for field in date_fields:
                    if field not in self.world_state["current_date"]:
                        self.world_state["current_date"][field] = 0
            
            self.logger.info(f"Loaded world state: {self.world_state.get('name', 'unknown')}")
            return self.world_state
            
        except Exception as e:
            self.logger.error(f"Error loading world state: {str(e)}")
            raise NotFoundError(f"Failed to load world state: {str(e)}")
    
    def update_world_state(self, updates: Dict[str, Any], save: bool = True) -> Dict[str, Any]:
        """
        Update the world state with new data.
        
        Args:
            updates: Dictionary of updates to apply
            save: Whether to save changes to the database
            
        Returns:
            Updated world state
            
        Raises:
            NotFoundError: If no world state exists
        """
        # Get current world state
        current_state = self.get_world_state()
        
        # Apply updates, with proper merging for nested objects
        self._deep_update(current_state, updates)
        
        # Update timestamp
        current_state["updated_at"] = datetime.utcnow().isoformat()
        
        # Save if requested
        if save:
            self._save_world_state_to_db(current_state)
        
        # Update local cache
        self.world_state = current_state
        self.last_update_time = datetime.utcnow()
        
        # Publish event
        integration_event_bus.publish("world.updated", {"updates": list(updates.keys())})
        
        return current_state
    
    def advance_world_time(self, days: int = 0, hours: int = 0, minutes: int = 0, 
                          save: bool = True) -> Dict[str, Any]:
        """
        Advance the world time by the specified amount.
        
        Args:
            days: Number of days to advance
            hours: Number of hours to advance
            minutes: Number of minutes to advance
            save: Whether to save changes to the database
            
        Returns:
            Updated world state
            
        Raises:
            NotFoundError: If no world state exists
            ValidationError: If invalid time values are provided
        """
        if days < 0 or hours < 0 or minutes < 0:
            raise ValidationError("Cannot advance time by negative values")
            
        # Get current world state
        current_state = self.get_world_state()
        
        # Extract current date
        current_date = current_state["current_date"]
        
        # Calculate new date
        new_minute = current_date["minute"] + minutes
        hour_overflow = new_minute // 60
        new_minute %= 60
        
        new_hour = current_date["hour"] + hours + hour_overflow
        day_overflow = new_hour // 24
        new_hour %= 24
        
        new_day = current_date["day"] + days + day_overflow
        
        # Simple calendar: each month has 30 days, each year has 12 months
        month_overflow = (new_day - 1) // 30
        new_day = ((new_day - 1) % 30) + 1
        
        new_month = current_date["month"] + month_overflow
        year_overflow = (new_month - 1) // 12
        new_month = ((new_month - 1) % 12) + 1
        
        new_year = current_date["year"] + year_overflow
        
        # Update date
        updates = {
            "current_date": {
                "year": new_year,
                "month": new_month,
                "day": new_day,
                "hour": new_hour,
                "minute": new_minute
            }
        }
        
        # Process time-based events
        processed_events = self._process_time_based_events(
            current_date,
            updates["current_date"],
            days=days + day_overflow + month_overflow * 30 + year_overflow * 360,
            hours=hours + hour_overflow,
            minutes=minutes
        )
        
        if processed_events:
            updates["processed_events"] = processed_events
        
        # Update weather if a significant amount of time has passed
        if days > 0 or hours >= 6:
            updates["current_weather"] = self._generate_weather(updates["current_date"])
        
        # Apply updates
        return self.update_world_state(updates, save=save)
    
    def _save_world_state_to_db(self, world_state: Dict[str, Any]) -> None:
        """
        Save the world state to the database.
        
        Args:
            world_state: World state to save
        """
        try:
            # Prepare a copy to avoid modifying original
            save_state = world_state.copy()
            
            # Convert any complex objects if needed
            self._prepare_for_db(save_state)
            
            # Save to database
            world_ref = self.db.collection("world_state").document("current")
            world_ref.set(save_state)
            
            # Also create a backup version
            timestamp = int(time.time())
            backup_ref = self.db.collection("world_state_backups").document(f"{timestamp}")
            backup_ref.set(save_state)
            
            # Clean up old backups (keep last 10)
            self._cleanup_old_backups(10)
            
            self.logger.info(f"Saved world state to database")
            
        except Exception as e:
            self.logger.error(f"Error saving world state: {str(e)}")
            self.logger.error(traceback.format_exc())
    
    def _cleanup_old_backups(self, keep_count: int) -> None:
        """
        Clean up old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of backups to keep
        """
        try:
            # Get all backups
            backups = self.db.collection("world_state_backups").order_by("__name__").get()
            
            # If we have more than keep_count, delete the oldest ones
            if len(backups) > keep_count:
                to_delete = backups[:-keep_count]
                
                for doc in to_delete:
                    doc.reference.delete()
                    
                self.logger.info(f"Cleaned up {len(to_delete)} old world state backups")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up backups: {str(e)}")
    
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a dictionary with values from another dictionary.
        
        Args:
            target: Dictionary to update
            source: Dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively update dictionaries
                self._deep_update(target[key], value)
            else:
                # Replace value
                target[key] = value
    
    def _prepare_for_db(self, data: Dict[str, Any]) -> None:
        """
        Prepare data for storage in the database.
        Converts complex objects to JSON-serializable format.
        
        Args:
            data: Data to prepare
        """
        if not isinstance(data, dict):
            return
            
        for key, value in list(data.items()):
            if isinstance(value, dict):
                self._prepare_for_db(value)
            elif isinstance(value, (list, tuple)):
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        self._prepare_for_db(item)
            elif hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                # Convert objects with to_dict method
                data[key] = value.to_dict()
    
    def _generate_initial_weather(self) -> Dict[str, Any]:
        """
        Generate initial weather for a new world.
        
        Returns:
            Weather data dictionary
        """
        return {
            "condition": "clear",
            "temperature": 22,
            "precipitation_chance": 0,
            "wind_speed": 5,
            "wind_direction": "north",
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def _generate_weather(self, current_date: Dict[str, int]) -> Dict[str, Any]:
        """
        Generate weather based on current date.
        
        Args:
            current_date: Current date dictionary
            
        Returns:
            Weather data dictionary
        """
        # Simple weather model based on month (season)
        month = current_date["month"]
        
        # Northern hemisphere seasons
        if 3 <= month <= 5:  # Spring
            condition_weights = {"clear": 0.4, "partly_cloudy": 0.3, "rain": 0.2, "stormy": 0.1}
            temp_range = (10, 22)
            precip_range = (0.2, 0.5)
        elif 6 <= month <= 8:  # Summer
            condition_weights = {"clear": 0.6, "partly_cloudy": 0.3, "rain": 0.1}
            temp_range = (20, 32)
            precip_range = (0.1, 0.3)
        elif 9 <= month <= 11:  # Fall
            condition_weights = {"partly_cloudy": 0.4, "cloudy": 0.3, "rain": 0.2, "clear": 0.1}
            temp_range = (5, 18)
            precip_range = (0.3, 0.6)
        else:  # Winter
            condition_weights = {"cloudy": 0.4, "snow": 0.3, "clear": 0.2, "partly_cloudy": 0.1}
            temp_range = (-10, 5)
            precip_range = (0.4, 0.7)
        
        # Choose condition based on weights
        import random
        conditions = list(condition_weights.keys())
        weights = list(condition_weights.values())
        condition = random.choices(conditions, weights=weights)[0]
        
        # Random temperature within range
        temp_min, temp_max = temp_range
        temperature = round(random.uniform(temp_min, temp_max), 1)
        
        # Precipitation chance
        precip_min, precip_max = precip_range
        precipitation_chance = round(random.uniform(precip_min, precip_max), 2)
        
        # Wind
        wind_speed = round(random.uniform(0, 30), 1)
        wind_directions = ["north", "northeast", "east", "southeast", 
                          "south", "southwest", "west", "northwest"]
        wind_direction = random.choice(wind_directions)
        
        return {
            "condition": condition,
            "temperature": temperature,
            "precipitation_chance": precipitation_chance,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def _process_time_based_events(self, old_date: Dict[str, int], new_date: Dict[str, int],
                                 days: int, hours: int, minutes: int) -> List[Dict[str, Any]]:
        """
        Process events that occur when time advances.
        
        Args:
            old_date: Previous date
            new_date: New date
            days: Days advanced
            hours: Hours advanced
            minutes: Minutes advanced
            
        Returns:
            List of processed events
        """
        processed_events = []
        
        # We would process various time-based events here:
        # - Daily population growth
        # - Weather changes
        # - Character schedules
        # - Faction activities
        # - Resource regeneration
        
        # Example: Daily population growth event
        if days > 0:
            processed_events.append({
                "type": "daily_population_change",
                "days": days,
                "processed_at": datetime.utcnow().isoformat()
            })
            
            # Publish event
            integration_event_bus.publish("time.days_advanced", {
                "days": days, 
                "old_date": old_date,
                "new_date": new_date
            })
        
        # Example: Hourly events
        if hours > 0 or days > 0:
            processed_events.append({
                "type": "hourly_update",
                "hours": hours + days * 24,
                "processed_at": datetime.utcnow().isoformat()
            })
            
            # Publish event
            integration_event_bus.publish("time.hours_advanced", {
                "hours": hours + days * 24,
                "old_date": old_date,
                "new_date": new_date
            })
        
        return processed_events
    
    def save_world_state(self) -> Dict[str, Any]:
        """
        Force saving the current world state.
        
        Returns:
            Current world state
        """
        if self.world_state is None:
            raise NotFoundError("No world state to save")
            
        self._save_world_state_to_db(self.world_state)
        return self.world_state
    
    def get_local_storage_path(self) -> Path:
        """
        Get the path for local storage of world data.
        
        Returns:
            Path object for the local storage directory
        """
        base_dir = Path(os.environ.get("DATA_DIR", "./data"))
        world_dir = base_dir / "world"
        
        # Create directory if it doesn't exist
        world_dir.mkdir(parents=True, exist_ok=True)
        
        return world_dir
    
    def save_to_local_file(self, filename: Optional[str] = None) -> str:
        """
        Save the current world state to a local file.
        
        Args:
            filename: Optional filename, defaults to timestamp
            
        Returns:
            Path to the saved file
        """
        if self.world_state is None:
            raise NotFoundError("No world state to save")
            
        # Generate filename if not provided
        if filename is None:
            timestamp = int(time.time())
            filename = f"world_state_{timestamp}.json"
            
        # Get save path
        save_dir = self.get_local_storage_path()
        save_path = save_dir / filename
        
        # Save file
        with open(save_path, 'w') as f:
            json.dump(self.world_state, f, indent=2)
            
        self.logger.info(f"Saved world state to {save_path}")
        return str(save_path)
    
    def load_from_local_file(self, path: str) -> Dict[str, Any]:
        """
        Load world state from a local file.
        
        Args:
            path: Path to the file
            
        Returns:
            Loaded world state
            
        Raises:
            NotFoundError: If file doesn't exist
        """
        file_path = Path(path)
        if not file_path.exists():
            raise NotFoundError(f"World state file not found: {path}")
            
        try:
            with open(file_path, 'r') as f:
                world_state = json.load(f)
                
            # Update and store
            self.world_state = world_state
            self.last_update_time = datetime.utcnow()
            
            # Save to database
            self._save_world_state_to_db(world_state)
            
            self.logger.info(f"Loaded world state from {path}")
            
            # Publish event
            integration_event_bus.publish("world.loaded", {"path": path})
            
            return world_state
            
        except Exception as e:
            self.logger.error(f"Error loading world state from file: {str(e)}")
            raise NotFoundError(f"Failed to load world state: {str(e)}")
    
    # Event handlers
    
    def _handle_day_advanced(self, data: Dict[str, Any]) -> None:
        """
        Handle a day advanced event.
        
        Args:
            data: Event data
        """
        self.logger.info(f"Day advanced: {data}")
        # Additional processing as needed
    
    def _handle_hour_advanced(self, data: Dict[str, Any]) -> None:
        """
        Handle an hour advanced event.
        
        Args:
            data: Event data
        """
        self.logger.debug(f"Hour advanced: {data}")
        # Additional processing as needed
    
    def _handle_world_reset(self, data: Dict[str, Any]) -> None:
        """
        Handle a world reset request.
        
        Args:
            data: Event data
        """
        self.logger.info(f"World reset requested: {data}")
        
        # Create new world with specified parameters
        world_name = data.get("world_name", f"World_{int(time.time())}")
        width = data.get("width", 5)
        height = data.get("height", 5)
        seed = data.get("seed")
        
        self.create_world_state(world_name, width, height, seed)
    
    def _handle_save_request(self, data: Dict[str, Any]) -> None:
        """
        Handle a save request event.
        
        Args:
            data: Event data
        """
        self.logger.info(f"Save requested: {data}")
        
        try:
            # Save to database
            self.save_world_state()
            
            # If local file also requested
            if data.get("save_local", False):
                filename = data.get("filename")
                path = self.save_to_local_file(filename)
                
                # Publish result
                integration_event_bus.publish("save.completed", {
                    "success": True,
                    "path": path
                })
            else:
                # Publish result
                integration_event_bus.publish("save.completed", {
                    "success": True
                })
                
        except Exception as e:
            self.logger.error(f"Error handling save request: {str(e)}")
            
            # Publish failure
            integration_event_bus.publish("save.completed", {
                "success": False,
                "error": str(e)
            }) 