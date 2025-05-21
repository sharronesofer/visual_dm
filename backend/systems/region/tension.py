"""
Tension Management Utilities for Region System

This module contains utilities for managing tension levels in regions and POIs.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

from backend.core.utils.error import TensionError
from backend.world.utils.world_event_utils import log_world_event

@dataclass
class TensionConfig:
    """Configuration for tension calculations.
    
    Attributes:
        base_tension: Default tension level for the location
        decay_rate: How quickly tension naturally decreases (per hour)
        max_tension: Maximum possible tension level
        min_tension: Minimum possible tension level
        player_impact: How much player actions affect tension
        npc_impact: How much NPC presence affects tension
        environmental_impact: How much environmental factors affect tension
    """
    base_tension: float
    decay_rate: float
    max_tension: float
    min_tension: float
    player_impact: float
    npc_impact: float
    environmental_impact: float

class TensionManager:
    """Manages tension levels for regions and POIs."""
    
    def __init__(self):
        """Initialize the TensionManager."""
        self.tension_configs = self._load_tension_configs()
        self.tension_state = {}  # region_id -> poi_id -> state
        self.last_updated = {}  # region_id -> poi_id -> datetime
        
    def _load_tension_configs(self) -> Dict[str, TensionConfig]:
        """Load tension configuration for different location types.
        
        Returns:
            Dict mapping location types to tension configs.
        """
        # In a real implementation, this would load from a file
        # or database. For now, hardcoded defaults.
        return {
            'city': TensionConfig(
                base_tension=0.2,
                decay_rate=0.05,
                max_tension=1.0,
                min_tension=0.1,
                player_impact=1.5,
                npc_impact=1.0,
                environmental_impact=0.5
            ),
            'dungeon': TensionConfig(
                base_tension=0.7,
                decay_rate=0.02,
                max_tension=1.0,
                min_tension=0.5,
                player_impact=2.0,
                npc_impact=1.5,
                environmental_impact=1.0
            ),
            'wilderness': TensionConfig(
                base_tension=0.4,
                decay_rate=0.03,
                max_tension=1.0,
                min_tension=0.2,
                player_impact=1.0,
                npc_impact=0.8,
                environmental_impact=2.0
            ),
            'default': TensionConfig(
                base_tension=0.3,
                decay_rate=0.04,
                max_tension=1.0,
                min_tension=0.1,
                player_impact=1.0,
                npc_impact=1.0,
                environmental_impact=1.0
            )
        }
        
    def calculate_tension(
        self,
        region_id: str,
        poi_id: str,
        current_time: Optional[datetime] = None
    ) -> float:
        """Calculate the current tension for a location.
        
        Args:
            region_id: The region ID
            poi_id: The POI ID
            current_time: The current time (defaults to now)
            
        Returns:
            Current tension level (0.0 to 1.0)
        """
        try:
            if current_time is None:
                current_time = datetime.utcnow()
                
            # Get location type for configuration
            location_type = self._get_location_type(region_id, poi_id)
            config = self.tension_configs.get(location_type, self.tension_configs['default'])
            
            # Get current tension state or initialize
            if region_id not in self.tension_state:
                self.tension_state[region_id] = {}
                self.last_updated[region_id] = {}
                
            if poi_id not in self.tension_state[region_id]:
                self.tension_state[region_id][poi_id] = config.base_tension
                self.last_updated[region_id][poi_id] = current_time
                return config.base_tension
                
            # Calculate time-based decay
            current_tension = self.tension_state[region_id][poi_id]
            decay = self._calculate_time_decay(
                region_id,
                poi_id,
                config.decay_rate,
                current_time
            )
            
            # Update tension
            new_tension = max(config.min_tension, min(config.max_tension, current_tension - decay))
            self.tension_state[region_id][poi_id] = new_tension
            self.last_updated[region_id][poi_id] = current_time
            
            return new_tension
            
        except Exception as e:
            raise TensionError(f"Failed to calculate tension: {str(e)}")
            
    def _get_location_type(self, region_id: str, poi_id: str) -> str:
        """Determine the location type for a region/POI.
        
        Args:
            region_id: The region ID
            poi_id: The POI ID
            
        Returns:
            Location type (city, dungeon, wilderness, etc.)
        """
        # In a real implementation, this would query the region/POI
        # For now, return a default
        return 'default'
        
    def update_tension(
        self,
        region_id: str,
        poi_id: str,
        player_action: Optional[str] = None,
        npc_change: Optional[Dict] = None,
        environmental_change: Optional[Dict] = None
    ) -> None:
        """Update tension based on world events.
        
        Args:
            region_id: The region ID
            poi_id: The POI ID
            player_action: Optional action from a player
            npc_change: Optional NPC-related change
            environmental_change: Optional environmental change
        """
        try:
            # Calculate current tension first (handles initialization)
            current_tension = self.calculate_tension(region_id, poi_id)
            
            # Get config
            location_type = self._get_location_type(region_id, poi_id)
            config = self.tension_configs.get(location_type, self.tension_configs['default'])
            
            # Apply impacts
            delta = 0.0
            if player_action:
                self._update_player_impact(region_id, poi_id, player_action)
                delta += self._get_player_impact(region_id, poi_id) * config.player_impact
                
            if npc_change:
                self._update_npc_impact(region_id, poi_id, npc_change)
                delta += self._get_npc_impact(region_id, poi_id) * config.npc_impact
                
            if environmental_change:
                self._update_environmental_impact(region_id, poi_id, environmental_change)
                delta += self._get_environmental_impact(region_id, poi_id) * config.environmental_impact
                
            # Update tension
            new_tension = max(config.min_tension, min(config.max_tension, current_tension + delta))
            self.tension_state[region_id][poi_id] = new_tension
            
        except Exception as e:
            raise TensionError(f"Failed to update tension: {str(e)}")
            
    def _calculate_time_decay(
        self,
        region_id: str,
        poi_id: str,
        decay_rate: float,
        current_time: Optional[datetime] = None
    ) -> float:
        """Calculate tension decay based on time elapsed.
        
        Args:
            region_id: The region ID
            poi_id: The POI ID
            decay_rate: The decay rate per hour
            current_time: The current time
            
        Returns:
            Tension decay amount
        """
        if current_time is None:
            current_time = datetime.utcnow()
            
        last_time = self.last_updated.get(region_id, {}).get(poi_id, current_time)
        hours_elapsed = (current_time - last_time).total_seconds() / 3600.0
        return decay_rate * hours_elapsed
        
    def _get_player_impact(self, region_id: str, poi_id: str) -> float:
        """Get player impact on tension."""
        # Placeholder
        return random.uniform(0.0, 0.1)
        
    def _get_npc_impact(self, region_id: str, poi_id: str) -> float:
        """Get NPC impact on tension."""
        # Placeholder
        return random.uniform(0.0, 0.05)
        
    def _get_environmental_impact(self, region_id: str, poi_id: str) -> float:
        """Get environmental impact on tension."""
        # Placeholder
        return random.uniform(0.0, 0.02)
        
    def _update_player_impact(
        self,
        region_id: str,
        poi_id: str,
        action: str
    ) -> None:
        """Update player impact based on action."""
        # Placeholder - would update a player impact tracker
        pass
        
    def _update_npc_impact(
        self,
        region_id: str,
        poi_id: str,
        change: Dict
    ) -> None:
        """Update NPC impact based on changes."""
        # Placeholder - would update an NPC impact tracker
        pass
        
    def _update_environmental_impact(
        self,
        region_id: str,
        poi_id: str,
        change: Dict
    ) -> None:
        """Update environmental impact based on changes."""
        # Placeholder - would update an environmental impact tracker
        pass

def decay_region_tension(region) -> None:
    """Decay tension for all POIs in a region."""
    # Placeholder implementation
    pass

def check_faction_war_triggers(region) -> List[Dict]:
    """Check if tension has triggered faction conflicts."""
    # Placeholder implementation
    return []

def get_regions_by_tension(session, min_tension: float = 0.0) -> List:
    """Get regions with tension above the minimum threshold."""
    # Placeholder implementation
    return []

def get_region_factions_at_war(session, region_id: int) -> List[Dict]:
    """Get factions that are currently at war in a region."""
    # Placeholder implementation  
    return []

def simulate_revolt_in_poi(region_id: str, poi_id: str, factions_present: list, npc_list: list, tension_level: float):
    """
    Simulate a revolt in a POI based on tension level.
    
    Args:
        region_id: The region ID
        poi_id: The POI ID
        factions_present: List of factions in the POI
        npc_list: List of NPCs in the POI
        tension_level: Current tension level (0.0 to 1.0)
        
    Returns:
        Revolt event details or None if no revolt triggered
    """
    if tension_level < 0.7:
        # Tension too low for revolt
        return None
        
    # Chance of revolt based on tension
    revolt_chance = (tension_level - 0.7) * 3.0  # 0% at 0.7, 90% at 1.0
    
    if random.random() > revolt_chance:
        # No revolt triggered
        return None
        
    # Select opposing factions if multiple present
    opposing_factions = []
    if len(factions_present) >= 2:
        # Select two random factions to oppose each other
        opposing_factions = random.sample(factions_present, 2)
    elif len(factions_present) == 1:
        # Revolt against the ruling faction
        opposing_factions = [factions_present[0], "rebels"]
    else:
        # Generic unrest
        opposing_factions = ["citizens", "authorities"]
        
    # Calculate casualties
    casualty_count = int(len(npc_list) * random.uniform(0.05, 0.2) * tension_level)
    casualties = random.sample(npc_list, min(casualty_count, len(npc_list)))
    
    # Generate event
    event = {
        "event_type": "revolt",
        "region_id": region_id,
        "poi_id": poi_id,
        "tension_level": tension_level,
        "opposing_factions": opposing_factions,
        "casualty_count": casualty_count,
        "casualties": [npc.get('id', 'unknown') for npc in casualties],
        "outcome": random.choice(["suppressed", "ongoing", "successful"]),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Log the event
    log_world_event({
        "type": "revolt",
        "location": f"{region_id}/{poi_id}",
        "description": f"Revolt between {opposing_factions[0]} and {opposing_factions[1]}",
        "casualties": casualty_count,
        "tension": tension_level
    })
    
    return event 