"""
World State management system for tracking and modifying game world state.

This module provides a centralized system for managing world state data,
tracking changes over time, and enabling querying for historical states.
"""
from typing import Dict, List, Optional, Any, Set, Union, Callable, TypeVar
from enum import Enum, auto
from datetime import datetime
import uuid
import json
import os
import logging
import asyncio
from pydantic import BaseModel, Field, ConfigDict
import time

from backend.infrastructure.events.core.event_base import EventBase
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
# Note: These schemas don't exist in canonical structure, commenting out for now
# from backend.app.schemas.world_state_types import WorldState, WorldStateChange, WorldStateChangeCustomData, ActiveEffect
# from backend.app.schemas.quest_components import FactionType # Assuming FactionType is defined here or imported

logger = logging.getLogger(__name__)

class StateChangeType(Enum):
    """Types of state changes that can occur."""
    CREATED = auto()
    UPDATED = auto()
    DELETED = auto()
    MERGED = auto()
    CALCULATED = auto()

class WorldRegion(Enum):
    """Represents major world regions for state organization."""
    GLOBAL = auto()  # Global state affecting the entire world
    NORTHERN = auto()
    SOUTHERN = auto()
    EASTERN = auto()
    WESTERN = auto()
    CENTRAL = auto()

class StateCategory(Enum):
    """Categories for organizing state data."""
    POLITICAL = auto()
    ECONOMIC = auto()
    MILITARY = auto()
    SOCIAL = auto()
    ENVIRONMENTAL = auto()
    RELIGIOUS = auto()
    MAGICAL = auto()
    QUEST = auto()
    OTHER = auto()

class StateChangeRecord(BaseModel):
    """
    Record of a change made to a state variable.
    
    This provides historical tracking of all changes for analysis,
    rollback capability, and narrative continuity.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    state_key: str
    old_value: Optional[Any] = None
    new_value: Any
    change_type: StateChangeType
    change_reason: Optional[str] = None
    entity_id: Optional[str] = None  # ID of entity that caused the change, if applicable
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class StateVariable(BaseModel):
    """
    A single state variable tracked in the world state.
    
    State variables have metadata to help with organization,
    querying, and semantic understanding of the data.
    """
    key: str
    value: Any
    category: StateCategory = StateCategory.OTHER
    region: WorldRegion = WorldRegion.GLOBAL
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    change_history: List[StateChangeRecord] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __str__(self) -> str:
        """String representation of the state variable."""
        return f"{self.key}={self.value} ({self.category.value}, {self.region.value})"

class WorldStateEvent(EventBase):
    """Event emitted when world state changes occur."""
    state_key: str
    change_type: StateChangeType
    old_value: Optional[Any] = None
    new_value: Any
    region: WorldRegion = WorldRegion.GLOBAL
    category: StateCategory = StateCategory.OTHER
    entity_id: Optional[str] = None

class WorldStateManager:
    """
    Manages world state variables and emits WorldStateChanged events via the canonical EventDispatcher.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(WorldStateManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, 
                storage_path: str = "data/world_state/",
                event_dispatcher: Optional[EventDispatcher] = None,
                auto_save: bool = True,
                initial_state: Optional[WorldState] = None):
        """
        Initialize the WorldStateManager.
        Args:
            storage_path: Base path for storing world state data
            event_dispatcher: Optional event dispatcher for publishing state changes (uses canonical singleton if None)
            auto_save: Whether to automatically save state changes to disk
            initial_state: Optional initial world state to set
        """
        if self._initialized:
            return
        self._storage_path = storage_path
        self._event_dispatcher = event_dispatcher or EventDispatcher.get_instance()
        self._auto_save = auto_save
        self._state_variables: Dict[str, StateVariable] = {}
        self._state_lock = asyncio.Lock()
        self._loaded = False
        os.makedirs(self._storage_path, exist_ok=True)
        if self._event_dispatcher:
            logger.info("Registering WorldStateManager with event system")
        self._initialized = True
        
        if initial_state:
            self.world_state = initial_state
        else:
            self.world_state = WorldState() # Initialize with default empty state
        
        # These were used in TS to track changes, might not be needed if state is mutated directly
        # and changes are logged/event-sourced elsewhere.
        self._state_changes_log: List[WorldStateChange] = [] # Chronological log of applied changes
        self._location_changes: Dict[str, List[WorldStateChange]] = {} # Location-specific logs
    
    async def _load_state(self) -> None:
        """Load state data from storage."""
        if self._loaded:
            return
            
        try:
            state_file = os.path.join(self._storage_path, "world_state.json")
            if os.path.exists(state_file):
                async with asyncio.Lock():
                    try:
                        import aiofiles
                        async with aiofiles.open(state_file, "r") as f:
                            data = await f.read()
                            state_data = json.loads(data)
                            
                            for key, value in state_data.items():
                                self._state_variables[key] = StateVariable(**value)
                        
                        logger.info(f"Loaded {len(self._state_variables)} state variables")
                    except Exception as e:
                        logger.error(f"Error loading world state: {e}")
                        # Create empty state
                        self._state_variables = {}
            else:
                logger.info("No world state file found, starting with empty state")
                self._state_variables = {}
                
            self._loaded = True
        except Exception as e:
            logger.error(f"Error in _load_state: {e}")
            raise
    
    async def _save_state(self) -> None:
        """Save state to storage."""
        try:
            if not self._initialized:
                return

            state_file = os.path.join(self._storage_path, "world_state.json")
            
            # Create a serializable representation of the state
            state_dict = {}
            for key, variable in self._state_variables.items():
                # Use model_dump() instead of dict() for Pydantic v2 compatibility
                var_dict = variable.model_dump()
                # Special handling for change history
                var_dict["change_history"] = [record.model_dump() for record in variable.change_history]
                state_dict[key] = var_dict
            
            try:
                import aiofiles
                async with aiofiles.open(state_file, "w") as f:
                    await f.write(json.dumps(state_dict, default=str, indent=2))
                
                logger.debug("Saved world state")
            except Exception as e:
                logger.error(f"Error saving world state: {e}")
        except Exception as e:
            logger.error(f"Error in _save_state: {e}")
            raise
    
    async def set(self, 
               key: str, 
               value: Any, 
               category: StateCategory = StateCategory.OTHER,
               region: WorldRegion = WorldRegion.GLOBAL,
               tags: List[str] = None,
               reason: Optional[str] = None,
               entity_id: Optional[str] = None) -> None:
        """
        Set a state variable with the given key to the specified value.
        
        Args:
            key: Unique key for the state variable (can use dot notation for hierarchy)
            value: The value to set
            category: Category for organizing the state variable
            region: World region this state applies to
            tags: Optional list of tags for additional categorization
            reason: Optional reason for the state change
            entity_id: Optional ID of the entity that caused the change
        """
        if not self._loaded:
            await self._load_state()
            
        async with self._state_lock:
            old_value = None
            change_type = StateChangeType.CREATED
            
            if key in self._state_variables:
                state_var = self._state_variables[key]
                old_value = state_var.value
                change_type = StateChangeType.UPDATED
                
                # Create change record
                change_record = StateChangeRecord(
                    state_key=key,
                    old_value=old_value,
                    new_value=value,
                    change_type=change_type,
                    change_reason=reason,
                    entity_id=entity_id
                )
                
                # Update existing state
                state_var.value = value
                state_var.updated_at = datetime.utcnow()
                state_var.change_history.append(change_record)
            else:
                # Create new state variable
                change_record = StateChangeRecord(
                    state_key=key,
                    new_value=value,
                    change_type=change_type,
                    change_reason=reason,
                    entity_id=entity_id
                )
                
                state_var = StateVariable(
                    key=key,
                    value=value,
                    category=category,
                    region=region,
                    tags=tags or [],
                    change_history=[change_record]
                )
                
                self._state_variables[key] = state_var
            
            # Auto-save if enabled
            if self._auto_save:
                await self._save_state()
            
            # Emit event
            if self._event_dispatcher:
                event = WorldStateEvent(
                    event_type="world_state.change",
                    state_key=key,
                    change_type=change_type,
                    old_value=old_value,
                    new_value=value,
                    region=state_var.region,
                    category=state_var.category,
                    entity_id=entity_id
                )
                await self._event_dispatcher.publish(event)
    
    async def get(self, key: str, default: Any = None, timestamp: Optional[datetime] = None) -> Any:
        """
        Get the value of a state variable.
        
        Args:
            key: The key of the state variable to retrieve
            default: Default value to return if the key doesn't exist
            timestamp: Optional timestamp to get historical state (if None, returns current)
            
        Returns:
            The value of the state variable or the default if not found
        """
        if not self._loaded:
            await self._load_state()
            
        if key not in self._state_variables:
            return default
            
        state_var = self._state_variables[key]
        
        # Return current value if no timestamp specified
        if timestamp is None:
            return state_var.value
            
        # Find historical value
        for change in reversed(state_var.change_history):
            if change.timestamp <= timestamp:
                return change.new_value
                
        # If no history before the timestamp, return default
        return default
    
    async def delete(self, key: str, reason: Optional[str] = None, entity_id: Optional[str] = None) -> bool:
        """
        Delete a state variable.
        
        Args:
            key: The key of the state variable to delete
            reason: Optional reason for the deletion
            entity_id: Optional ID of the entity that caused the deletion
            
        Returns:
            True if deleted, False if not found
        """
        if not self._loaded:
            await self._load_state()
            
        async with self._state_lock:
            if key not in self._state_variables:
                return False
                
            state_var = self._state_variables[key]
            old_value = state_var.value
            
            # Emit event before deletion
            if self._event_dispatcher:
                event = WorldStateEvent(
                    event_type="world_state.change",
                    state_key=key,
                    change_type=StateChangeType.DELETED,
                    old_value=old_value,
                    new_value=None,
                    region=state_var.region,
                    category=state_var.category,
                    entity_id=entity_id
                )
                await self._event_dispatcher.publish(event)
            
            # Remove from state
            del self._state_variables[key]
            
            # Auto-save if enabled
            if self._auto_save:
                await self._save_state()
                
            return True
    
    async def query(self, 
                 category: Optional[StateCategory] = None,
                 region: Optional[WorldRegion] = None,
                 tags: Optional[List[str]] = None,
                 prefix: Optional[str] = None,
                 timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Query state variables based on criteria.
        
        Args:
            category: Optional category to filter by
            region: Optional region to filter by
            tags: Optional list of tags to filter by (any match)
            prefix: Optional key prefix to filter by
            timestamp: Optional timestamp to get historical state
            
        Returns:
            Dictionary of matching state variables (key -> value)
        """
        if not self._loaded:
            await self._load_state()
            
        results = {}
        
        for key, state_var in self._state_variables.items():
            # Apply filters
            if category is not None and state_var.category != category:
                continue
                
            if region is not None and state_var.region != region:
                continue
                
            if tags is not None and not any(tag in state_var.tags for tag in tags):
                continue
                
            if prefix is not None and not key.startswith(prefix):
                continue
            
            # Get historical or current value
            if timestamp is not None:
                # Find historical value
                value = None
                for change in reversed(state_var.change_history):
                    if change.timestamp <= timestamp:
                        value = change.new_value
                        break
                
                if value is None:
                    continue  # Skip if no history before timestamp
            else:
                value = state_var.value
            
            results[key] = value
            
        return results
    
    async def get_history(self, key: str) -> List[StateChangeRecord]:
        """
        Get the complete history of changes for a state variable.
        
        Args:
            key: The key of the state variable
            
        Returns:
            List of change records in chronological order
        """
        if not self._loaded:
            await self._load_state()
            
        if key not in self._state_variables:
            return []
            
        return self._state_variables[key].change_history
    
    async def get_state_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a state variable.
        
        Args:
            key: The key of the state variable
            
        Returns:
            Dictionary with metadata or None if not found
        """
        if not self._loaded:
            await self._load_state()
            
        if key not in self._state_variables:
            return None
            
        state_var = self._state_variables[key]
        return {
            "key": state_var.key,
            "category": state_var.category,
            "region": state_var.region,
            "tags": state_var.tags,
            "created_at": state_var.created_at,
            "updated_at": state_var.updated_at,
            "change_count": len(state_var.change_history)
        }
    
    def get_sync(self, key: str, default: Any = None) -> Any:
        """
        Synchronous version of get() for use in contexts where async isn't possible.
        Note: This doesn't guarantee the state is loaded from disk.
        
        Args:
            key: The key of the state variable to retrieve
            default: Default value to return if the key doesn't exist
            
        Returns:
            The value of the state variable or the default if not found
        """
        if key not in self._state_variables:
            return default
            
        return self._state_variables[key].value
    
    def set_sync(self, 
              key: str, 
              value: Any,
              category: StateCategory = StateCategory.OTHER,
              region: WorldRegion = WorldRegion.GLOBAL,
              tags: List[str] = None,
              reason: Optional[str] = None,
              entity_id: Optional[str] = None) -> None:
        """
        Synchronous version of set() for use in contexts where async isn't possible.
        Note: This doesn't save to disk immediately or emit events.
        
        Args:
            key: Unique key for the state variable
            value: The value to set
            category: Category for organizing the state variable
            region: World region this state applies to
            tags: Optional list of tags for additional categorization
            reason: Optional reason for the state change
            entity_id: Optional ID of the entity that caused the change
        """
        old_value = None
        change_type = StateChangeType.CREATED
        
        if key in self._state_variables:
            state_var = self._state_variables[key]
            old_value = state_var.value
            change_type = StateChangeType.UPDATED
            
            # Create change record
            change_record = StateChangeRecord(
                state_key=key,
                old_value=old_value,
                new_value=value,
                change_type=change_type,
                change_reason=reason,
                entity_id=entity_id
            )
            
            # Update existing state
            state_var.value = value
            state_var.updated_at = datetime.utcnow()
            state_var.change_history.append(change_record)
        else:
            # Create new state variable
            change_record = StateChangeRecord(
                state_key=key,
                new_value=value,
                change_type=change_type,
                change_reason=reason,
                entity_id=entity_id
            )
            
            state_var = StateVariable(
                key=key,
                value=value,
                category=category,
                region=region,
                tags=tags or [],
                change_history=[change_record]
            )
            
            self._state_variables[key] = state_var 

    def save_state(self) -> bool:
        """
        Synchronously save the world state to disk.
        
        This is used for application shutdown to ensure state is persisted.
        For normal runtime operation, the async _save_state method is used.
        
        Returns:
            bool: Whether the save was successful
        """
        try:
            if not self._initialized:
                logger.warning("Cannot save world state: not initialized")
                return False

            # Ensure state is loaded before attempting to save
            if not self._loaded:
                logger.warning("Cannot save world state: not loaded")
                return False

            state_file = os.path.join(self._storage_path, "world_state.json")
            
            # Create a serializable representation of the state
            state_dict = {}
            for key, variable in self._state_variables.items():
                # Use model_dump() instead of dict() for Pydantic v2 compatibility
                var_dict = variable.model_dump()
                # Special handling for change history
                var_dict["change_history"] = [record.model_dump() for record in variable.change_history]
                state_dict[key] = var_dict
            
            with open(state_file, "w") as f:
                f.write(json.dumps(state_dict, default=str, indent=2))
            
            logger.info("Saved world state during shutdown")
            return True
        except Exception as e:
            logger.error(f"Error in save_state during shutdown: {e}")
            return False 

    def apply_world_state_change(self, change: WorldStateChange) -> None:
        self._state_changes_log.append(change)
        if change.location:
            location_key = change.location.lower()
            if location_key not in self._location_changes:
                self._location_changes[location_key] = []
            self._location_changes[location_key].append(change)

        # Apply the change to self.world_state
        # The switch statement from TS is mapped to if/elif here
        if change.type == 'RESOURCE':
            self._handle_resource_change(change)
        elif change.type == 'TERRITORY':
            self._handle_territory_change(change)
        elif change.type == 'INFLUENCE':
            self._handle_influence_change(change)
        elif change.type == 'FACTION_TENSION_CHANGE':
            self._handle_tension_change(change)
        elif change.type == 'CUSTOM':
            self._handle_custom_change(change)
        elif change.type == 'QUEST_FAILURE':
            self._handle_quest_failure(change)
        # Handle types from the generic handleWorldStateChange in TS
        elif change.type == 'ENVIRONMENT':
            if change.custom_data and change.custom_data.value is not None: # Assuming value is in custom_data for these
                 self.world_state.environmental_conditions["environment"] = change.custom_data.value
        elif change.type == 'ECONOMY':
            if change.custom_data and isinstance(change.custom_data.value, dict):
                 self.world_state.economy_factors.update(change.custom_data.value)
        elif change.type == 'QUEST_AVAILABILITY':
            if change.custom_data and change.custom_data.value and isinstance(change.custom_data.value, dict):
                to_add = change.custom_data.value.get("add", [])
                to_remove = change.custom_data.value.get("remove", [])
                for quest_id in to_add:
                    self.world_state.available_quests.add(quest_id)
                for quest_id in to_remove:
                    self.world_state.available_quests.discard(quest_id)
        elif change.type == 'ACTIVE_EFFECTS': # Assuming 'ACTIVE_EFFECTS' is the type for adding one effect
            if change.custom_data and isinstance(change.custom_data.value, dict):
                try:
                    effect_data = ActiveEffect.model_validate(change.custom_data.value)
                    self.world_state.active_effects.append(effect_data)
                except Exception as e: # Pydantic ValidationError
                    print(f"Error validating ActiveEffect data: {e}")
        else:
            print(f"Warning: Unhandled world state change type: {change.type}")

    def get_world_state(self) -> WorldState:
        return self.world_state

    def get_all_state_changes_log(self) -> List[WorldStateChange]:
        return self._state_changes_log

    def get_location_changes_log(self, location: str) -> List[WorldStateChange]:
        return self._location_changes.get(location.lower(), [])
    
    # Specific getters from TS version
    def get_territory_control(self) -> Dict[str, FactionType]:
        return self.world_state.territory_control

    def get_resource_availability(self, resource_id: str) -> float:
        return self.world_state.resources.get(resource_id, 0.0)

    def get_environmental_conditions(self) -> Dict[str, Any]:
        return self.world_state.environmental_conditions

    # Private handler methods translated from TS
    def _handle_resource_change(self, change: WorldStateChange) -> None:
        if change.custom_data and change.custom_data.resource_id and change.value is not None:
            resource_id = change.custom_data.resource_id
            current_value = self.world_state.resources.get(resource_id, 0.0)
            self.world_state.resources[resource_id] = current_value + change.value
        else:
            print(f"Warning: Insufficient data for RESOURCE change: {change.model_dump_json()}")

    def _handle_territory_change(self, change: WorldStateChange) -> None:
        if not (change.custom_data and change.custom_data.territory and change.custom_data.faction):
            print(f"Warning: Insufficient data for TERRITORY change: {change.model_dump_json()}")
            return

        territory_id = change.custom_data.territory
        faction_id = change.custom_data.faction # This is FactionType
        
        current_territories = self.world_state.territories.get(faction_id, [])
        if change.value is not None and change.value > 0: # Gain territory
            if territory_id not in current_territories:
                current_territories.append(territory_id)
            self.world_state.territory_control[territory_id] = faction_id
        else: # Lose territory (value <= 0 or None implied)
            if territory_id in current_territories:
                current_territories.remove(territory_id)
            if self.world_state.territory_control.get(territory_id) == faction_id:
                # Only remove control if this faction was the controller
                del self.world_state.territory_control[territory_id]
        
        self.world_state.territories[faction_id] = current_territories

    def _handle_influence_change(self, change: WorldStateChange) -> None:
        if not (change.custom_data and change.custom_data.faction and change.value is not None):
            print(f"Warning: Insufficient data for INFLUENCE change: {change.model_dump_json()}")
            return
        
        faction_id = change.custom_data.faction # This is FactionType
        current_value = self.world_state.influence.get(faction_id, 0.0)
        self.world_state.influence[faction_id] = current_value + change.value
        # Also update the separate factionInfluence map if it's meant to be kept in sync
        self.world_state.faction_influence[faction_id] = self.world_state.influence[faction_id]

    def _handle_tension_change(self, change: WorldStateChange) -> None:
        if not (len(change.affected_factions) == 2 and change.value is not None):
            print(f"Warning: Insufficient data for FACTION_TENSION_CHANGE: {change.model_dump_json()}")
            return
        
        factions = sorted([f.value for f in change.affected_factions]) # Sort to ensure consistent key
        tension_key = f"{factions[0]}_{factions[1]}"
        current_tension = self.world_state.faction_tensions.get(tension_key, 0.0)
        self.world_state.faction_tensions[tension_key] = current_tension + change.value

    def _handle_custom_change(self, change: WorldStateChange) -> None:
        if not (change.custom_data and change.custom_data.key and hasattr(change.custom_data, 'value')):
            print(f"Warning: Insufficient data for CUSTOM change: {change.model_dump_json()}")
            return
        self.world_state.custom_states[change.custom_data.key] = change.custom_data.value

    def _handle_quest_failure(self, change: WorldStateChange) -> None:
        if not (change.custom_data and change.custom_data.quest_id):
            print(f"Warning: Insufficient data for QUEST_FAILURE: {change.model_dump_json()}")
            return

        failure_details = {
            "quest_id": change.custom_data.quest_id,
            "timestamp": change.custom_data.timestamp or time.time(),
            "affected_factions": [f.value for f in change.affected_factions],
            "reason": change.description
        }
        self.world_state.quest_failures.append(failure_details)

        if change.value is not None and change.value != 0:
            for faction_id in change.affected_factions:
                current_influence = self.world_state.influence.get(faction_id, 0.0)
                self.world_state.influence[faction_id] = current_influence + change.value
                self.world_state.faction_influence[faction_id] = self.world_state.influence[faction_id]

    def update_active_effects(self) -> None:
        """Update world state (check expired effects, etc.)."""
        current_time = time.time()
        active_effects_still_valid = []
        for effect in self.world_state.active_effects:
            if effect.duration is None: # Permanent until explicitly removed
                active_effects_still_valid.append(effect)
                continue
            if (effect.start_time + effect.duration) > current_time:
                active_effects_still_valid.append(effect)
        self.world_state.active_effects = active_effects_still_valid

        # Expire location-specific changes if they have a duration
        # This assumes WorldStateChange.custom_data.duration and .timestamp are used for temporary changes
        for location_key, changes_at_location in list(self._location_changes.items()): # Use list() for safe iteration if modifying
            valid_changes_at_location = []
            for change_item in changes_at_location:
                if change_item.custom_data and change_item.custom_data.duration is not None and change_item.custom_data.timestamp is not None:
                    if (change_item.custom_data.timestamp + change_item.custom_data.duration) > current_time:
                        valid_changes_at_location.append(change_item)
                else: # No duration, or no timestamp, assume permanent in log
                    valid_changes_at_location.append(change_item)
            if valid_changes_at_location:
                self._location_changes[location_key] = valid_changes_at_location
            else:
                del self._location_changes[location_key] # Clean up if no valid changes remain 
