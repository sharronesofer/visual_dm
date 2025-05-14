"""
World state models for managing game world state.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.core.database import db
from app.core.models.base import BaseModel as BaseModelORM
from app.core.models.time_system import TimeSystem, TimeEvent, TimeScale
from app.core.models.season_system import SeasonSystem
from app.core.models.weather_system import WeatherSystem
from app.core.models.npc_activity_system import NPCActivitySystem
from app.core.enums import TimeOfDay, Season, WeatherType
from app.core.models.faction import Faction
from app.core.models.version_control import VersionControl

class Weather(BaseModel):
    """Weather state model."""
    condition: str = "clear"
    temperature: float = 20.0
    wind_speed: float = 0.0
    precipitation: float = 0.0
    visibility: float = 100.0

class Season(BaseModel):
    """Season state model."""
    name: str = "spring"
    day: int = 1
    year: int = 1

class WorldState(BaseModelORM):
    """
    Model for tracking global game state.

    Responsibilities:
    - Dynamic world state tracking (locations, variables)
    - Faction management (relations, updates)
    - Economic system (currencies, markets, resource flows)
    - Event system (world events, triggers, resolution)
    - Calendar and time management (date, time, seasons)
    - Weather and environmental conditions
    - NPC activities and schedules
    """
    __tablename__ = 'world_states'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_saved_at = Column(DateTime, default=datetime.utcnow)
    
    # Time tracking
    game_time = Column(Float, default=0.0)  # Time in minutes since world creation
    time_scale = Column(Float, default=1.0)  # Real seconds per game minute
    is_paused = Column(Boolean, default=False)
    
    # Season and weather
    current_season = Column(String(50), default="spring")
    season_progress = Column(Float, default=0.0)  # 0.0 to 1.0
    current_weather = Column(String(50), default="clear")
    weather_duration = Column(Float, default=0.0)  # Minutes until next weather change
    
    # World data storage
    world_data = Column(JSON, default=dict)  # For flexible data storage
    
    # Version control
    version_id = Column(Integer, ForeignKey("code_versions.id"))
    version = relationship("VersionControl", backref="world_states")
    events = relationship('WorldEvent', back_populates='world_state')
    
    def __repr__(self):
        return f'<WorldState {self.name}>'

    def __init__(self, **data):
        """Initialize the world state with all required systems."""
        super().__init__(**data)
        
        # Initialize core systems
        self.time_system = TimeSystem()
        self.season_system = SeasonSystem()
        self.weather_system = WeatherSystem()
        self.npc_activity_system = NPCActivitySystem()
        
        # Initialize state tracking
        self.events: List[Dict] = []
        self.active_effects: List[Dict] = []
        self.npcs: Dict[str, Dict] = {}
        self.factions: Dict[str, Dict] = {}
        self.version = VersionControl()

    def update(self, delta_time: float) -> None:
        """Update the world state based on time passed.
        
        Args:
            delta_time: Time passed in seconds
        """
        # Update game time and get triggered events
        triggered_events = self.time_system.update(delta_time)
        
        # Process triggered events
        for event in triggered_events:
            self._handle_time_event(event)
            
        # Update world systems based on new time
        self._update_world_systems()
        
    def _handle_time_event(self, event: TimeEvent) -> None:
        """Handle a triggered time event.
        
        Args:
            event: The triggered time event
        """
        if event.type == "weather_change":
            self.weather_system.handle_event(event.data)
        elif event.type == "season_change":
            self.season_system.handle_event(event.data)
        elif event.type == "npc_schedule":
            self.npc_activity_system.handle_event(event.data)
        elif event.type == "faction_update":
            self._update_faction_relations(event.data)
        elif event.type == "effect_expiry":
            self._remove_expired_effects(event.data)
            
    def _update_world_systems(self) -> None:
        """Update all world systems based on current time."""
        current_time = self.time_system.current_time
        time_of_day = self.time_system.get_time_of_day()
        
        # Update season system
        self.season_system.update(current_time)
        
        # Update weather system with season influence
        current_season = self.season_system.current_season
        if self._should_update_weather():
            self.weather_system.update(current_time, current_season, time_of_day)
            
        # Update NPC activities with weather and season influence
        current_weather = self.weather_system.current_weather
        self.npc_activity_system.update(
            current_time,
            time_of_day,
            current_weather,
            current_season
        )
        
        # Update faction relations
        self._update_faction_relations()
        
        # Clean up expired effects
        self._remove_expired_effects()
        
    def _should_update_weather(self) -> bool:
        """Determine if weather should be updated."""
        # Update weather every game hour
        last_update = getattr(self, '_last_weather_update', None)
        if not last_update or (self.time_system.current_time - last_update) >= timedelta(hours=1):
            self._last_weather_update = self.time_system.current_time
            return True
        return False
        
    def _update_faction_relations(self, faction_data: Optional[Dict] = None) -> None:
        """Update relations between factions."""
        if faction_data:
            # Update specific faction relations
            for faction_id, relations in faction_data.items():
                if faction_id in self.factions:
                    self.factions[faction_id]["relations"].update(relations)
        else:
            # Regular faction relation updates
            for faction_id, faction in self.factions.items():
                for other_id, relation in faction.get("relations", {}).items():
                    # Decay or strengthen relations based on recent interactions
                    pass
                    
    def _remove_expired_effects(self, effect_ids: Optional[List[str]] = None) -> None:
        """Remove expired effects from the world state."""
        current_time = self.time_system.current_time
        
        if effect_ids:
            # Remove specific effects
            self.active_effects = [
                effect for effect in self.active_effects 
                if effect["id"] not in effect_ids
            ]
        else:
            # Remove all expired effects
            self.active_effects = [
                effect for effect in self.active_effects
                if effect.get("expiry_time") is None 
                or effect["expiry_time"] > current_time
            ]
            
    def add_event(self, event_type: str, trigger_time: datetime, data: Dict,
                  duration: Optional[timedelta] = None, recurring: bool = False,
                  recurrence_interval: Optional[timedelta] = None) -> str:
        """Add a timed event to the world state.
        
        Args:
            event_type: Type of event (e.g., 'weather_change', 'season_change', 'npc_schedule')
            trigger_time: When the event should occur
            data: Event-specific data
            duration: How long the event lasts (None for instant events)
            recurring: Whether the event should repeat
            recurrence_interval: Time between recurrences (required if recurring=True)
            
        Returns:
            str: ID of the created event
        """
        return self.time_system.add_event(
            event_type,
            trigger_time,
            data,
            duration,
            recurring,
            recurrence_interval
        )

    def remove_event(self, event_id: str) -> None:
        """Remove an event from the world state.
        
        Args:
            event_id: ID of the event to remove
        """
        self.time_system.remove_event(event_id)

    def set_time_scale(self, scale: TimeScale) -> None:
        """Set the time scale for the world.
        
        Args:
            scale: New time scale to use
        """
        self.time_system.set_time_scale(scale)

    def pause_time(self) -> None:
        """Pause the flow of time in the world."""
        self.time_system.pause()

    def resume_time(self) -> None:
        """Resume the flow of time in the world."""
        self.time_system.resume()

    def get_current_time(self) -> datetime:
        """Get the current world time.
        
        Returns:
            datetime: Current world time
        """
        return self.time_system.current_time

    def get_time_of_day(self) -> TimeOfDay:
        """Get the current time of day.
        
        Returns:
            TimeOfDay: Current time of day
        """
        return self.time_system.get_time_of_day()

    def format_time(self, include_seconds: bool = False) -> str:
        """Format the current time as a string.
        
        Args:
            include_seconds: Whether to include seconds in the formatted time
            
        Returns:
            str: Formatted time string
        """
        return self.time_system.format_time(include_seconds)

    def advance_time(self, days: int = 0, hours: int = 0,
                    minutes: int = 0, seconds: int = 0) -> None:
        """Advance time by a specific amount.
        
        Args:
            days: Number of days to advance
            hours: Number of hours to advance
            minutes: Number of minutes to advance
            seconds: Number of seconds to advance
        """
        # Advance time and get triggered events
        triggered_events = self.time_system.advance_time(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        
        # Process any events that were triggered
        for event in triggered_events:
            self._handle_time_event(event)
            
        # Update all systems
        self._update_world_systems()

    def advance_calendar(self, hours: int = 1) -> None:
        """Advance the world's calendar by a given number of hours.
        
        Args:
            hours: Number of hours to advance
        """
        self.advance_time(hours=hours)

    def update_all_systems(self, hours: int = 1, economic_changes: Optional[Dict[str, Any]] = None) -> None:
        """Update all core world systems.
        
        Args:
            hours: Number of hours to advance time
            economic_changes: Optional economic system updates to apply
        """
        # Advance time first
        self.advance_time(hours=hours)
        
        # Apply any economic changes
        if economic_changes:
            self.world_data.update(economic_changes)
            
        # Process world events
        self.process_world_events()

    def process_world_events(self) -> None:
        """Process any pending world events."""
        current_time = self.get_current_time()
        
        # Process events in chronological order
        for event in sorted(self.events, key=lambda e: e.get('time', current_time)):
            if event.get('time', current_time) <= current_time:
                self._handle_time_event(TimeEvent(
                    type=event['type'],
                    data=event.get('data', {})
                ))

    def get_current_season(self) -> Season:
        """Get the current season.
        
        Returns:
            Season: Current season
        """
        return self.season_system.current_season

    def get_current_weather(self) -> Weather:
        """Get the current weather conditions.
        
        Returns:
            Weather: Current weather conditions
        """
        return self.weather_system.current_weather

    def get_npc_activities(self) -> Dict[str, Dict]:
        """Get current NPC activities.
        
        Returns:
            Dict[str, Dict]: Mapping of NPC IDs to their current activities
        """
        return self.npc_activity_system.get_current_activities()

    def get_world_state(self) -> Dict[str, Any]:
        """Get a complete snapshot of the current world state.
        
        Returns:
            Dict[str, Any]: Complete world state including all subsystems
        """
        return {
            'time': self.get_current_time(),
            'time_of_day': self.get_time_of_day(),
            'season': self.get_current_season(),
            'weather': self.get_current_weather(),
            'npc_activities': self.get_npc_activities(),
            'faction_relations': self.factions,
            'world_data': self.world_data,
            'active_effects': self.active_effects,
            'events': self.events,
            'version': self.version.to_dict() if self.version else None
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert world state to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "last_saved_at": self.last_saved_at.isoformat(),
            "game_time": self.game_time,
            "time_scale": self.time_scale,
            "is_paused": self.is_paused,
            "current_season": self.current_season,
            "season_progress": self.season_progress,
            "current_weather": self.current_weather,
            "weather_duration": self.weather_duration,
            "world_data": self.world_data,
            "version": self.version.to_dict() if self.version else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorldState":
        """Create world state from dictionary data."""
        world_state = cls(
            name=data["name"],
            description=data.get("description"),
            game_time=data.get("game_time", 0.0),
            time_scale=data.get("time_scale", 1.0),
            is_paused=data.get("is_paused", False),
            current_season=data.get("current_season", "spring"),
            season_progress=data.get("season_progress", 0.0),
            current_weather=data.get("current_weather", "clear"),
            weather_duration=data.get("weather_duration", 0.0),
            world_data=data.get("world_data", {})
        )
        
        if "version" in data and data["version"]:
            world_state.version = VersionControl.from_dict(data["version"])
            
        return world_state

    def save(self) -> None:
        """Save current world state."""
        self.last_saved_at = datetime.utcnow()
        self.version.increment_minor()
        db.session.add(self)
        db.session.commit()

    def create_snapshot(self, description: str = None) -> None:
        """Create a major version snapshot of the world state."""
        self.last_saved_at = datetime.utcnow()
        self.version.increment_major()
        if description:
            self.version.description = description
        db.session.add(self)
        db.session.commit()

    def restore_snapshot(self, version_id: int) -> None:
        """Restore world state to a previous version."""
        target_version = db.session.query(VersionControl).get(version_id)
        if not target_version:
            raise ValueError(f"Version {version_id} not found")
            
        # Create new version for the restoration
        self.version = VersionControl(
            major=target_version.major,
            minor=target_version.minor,
            description=f"Restored from version {version_id}"
        )
        self.last_saved_at = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

class WorldStateManager:
    """Manager class for handling world state operations."""
    
    @staticmethod
    def create_world(name: str, description: str = None) -> WorldState:
        """Create a new world state."""
        world_state = WorldState(name=name, description=description)
        db.session.add(world_state)
        db.session.commit()
        return world_state

    @staticmethod
    def get_world(world_id: int) -> Optional[WorldState]:
        """Get a world state by ID."""
        return db.session.query(WorldState).get(world_id)

    @staticmethod
    def get_worlds() -> List[WorldState]:
        """Get all world states."""
        return db.session.query(WorldState).all()

    @staticmethod
    def save_world(world_id: int) -> None:
        """Save a specific world state."""
        world = WorldStateManager.get_world(world_id)
        if world:
            world.save()

    @staticmethod
    def create_snapshot(world_id: int, description: str = None) -> None:
        """Create a snapshot of a world state."""
        world = WorldStateManager.get_world(world_id)
        if world:
            world.create_snapshot(description)

    @staticmethod
    def restore_snapshot(world_id: int, version_id: int) -> None:
        """Restore a world state to a previous version."""
        world = WorldStateManager.get_world(world_id)
        if world:
            world.restore_snapshot(version_id)

    @staticmethod
    def delete_world(world_id: int) -> None:
        """Delete a world state."""
        world = WorldStateManager.get_world(world_id)
        if world:
            db.session.delete(world)
            db.session.commit() 