"""
Tension management system for regions and points of interest.

This module handles the dynamic tension system that affects gameplay in different regions
and points of interest (POIs). Tension represents the level of danger, hostility, or
instability in a location, affecting various game mechanics like:
- Combat encounter frequency
- NPC behavior
- Resource availability
- Event triggers
- Rest effectiveness

The tension system uses several factors to calculate and update tension levels:
1. Base tension: Inherent danger of the location
2. Player actions: Recent player activities in the area
3. Time-based decay: Natural reduction of tension over time
4. Environmental factors: Weather, time of day, etc.
5. NPC presence: Hostile or friendly NPCs in the area

Tension levels range from 0.0 (completely safe) to 1.0 (extremely dangerous).
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math
from dataclasses import dataclass
from app.core.utils.error_utils import TensionError

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
    """Manages tension levels for regions and POIs.
    
    The TensionManager handles all aspects of tension calculation and updates,
    including:
    - Initial tension setup
    - Tension updates based on various factors
    - Tension decay over time
    - Special event triggers based on tension levels
    
    Usage:
        manager = TensionManager()
        tension = manager.calculate_tension(region_id, poi_id)
        manager.update_tension(region_id, poi_id, player_action="combat")
    """
    
    def __init__(self):
        self._tension_cache: Dict[str, Dict[str, float]] = {}
        self._last_update: Dict[str, Dict[str, datetime]] = {}
        self._configs = self._load_tension_configs()
        
    def _load_tension_configs(self) -> Dict[str, TensionConfig]:
        """Load tension configurations for different location types.
        
        Returns:
            Dict mapping location types to their tension configurations.
        """
        return {
            'safe_zone': TensionConfig(
                base_tension=0.1,
                decay_rate=0.2,
                max_tension=0.3,
                min_tension=0.0,
                player_impact=0.1,
                npc_impact=0.1,
                environmental_impact=0.1
            ),
            'wilderness': TensionConfig(
                base_tension=0.4,
                decay_rate=0.1,
                max_tension=0.8,
                min_tension=0.2,
                player_impact=0.3,
                npc_impact=0.4,
                environmental_impact=0.3
            ),
            'dungeon': TensionConfig(
                base_tension=0.7,
                decay_rate=0.05,
                max_tension=1.0,
                min_tension=0.5,
                player_impact=0.4,
                npc_impact=0.5,
                environmental_impact=0.2
            )
        }
        
    def calculate_tension(
        self,
        region_id: str,
        poi_id: str,
        current_time: Optional[datetime] = None
    ) -> float:
        """Calculate the current tension level for a location.
        
        This method considers:
        1. Base tension from the location type
        2. Time-based decay since last update
        3. Recent player actions
        4. Current NPC presence
        5. Environmental factors
        
        Args:
            region_id: ID of the region
            poi_id: ID of the point of interest
            current_time: Optional override for current time (for testing)
            
        Returns:
            float: Current tension level (0.0 to 1.0)
            
        Raises:
            TensionError: If calculation fails
        """
        try:
            # Get location type and config
            location_type = self._get_location_type(region_id, poi_id)
            config = self._configs[location_type]
            
            # Calculate time-based decay
            decay = self._calculate_time_decay(
                region_id,
                poi_id,
                config.decay_rate,
                current_time
            )
            
            # Get current factors
            player_factor = self._get_player_impact(region_id, poi_id)
            npc_factor = self._get_npc_impact(region_id, poi_id)
            env_factor = self._get_environmental_impact(region_id, poi_id)
            
            # Calculate final tension
            tension = (
                config.base_tension * (1 - decay) +
                player_factor * config.player_impact +
                npc_factor * config.npc_impact +
                env_factor * config.environmental_impact
            )
            
            # Apply limits
            return max(
                config.min_tension,
                min(config.max_tension, tension)
            )
            
        except Exception as e:
            raise TensionError(f"Failed to calculate tension: {str(e)}")
            
    def update_tension(
        self,
        region_id: str,
        poi_id: str,
        player_action: Optional[str] = None,
        npc_change: Optional[Dict] = None,
        environmental_change: Optional[Dict] = None
    ) -> None:
        """Update tension based on new events or changes.
        
        This method should be called whenever:
        - A player performs an action in the area
        - NPCs enter or leave the area
        - Environmental conditions change
        - Special events occur
        
        Args:
            region_id: ID of the region
            poi_id: ID of the point of interest
            player_action: Type of player action (e.g., 'combat', 'stealth')
            npc_change: Changes in NPC presence
            environmental_change: Changes in environmental conditions
            
        Raises:
            TensionError: If update fails
        """
        try:
            # Update tension based on factors
            if player_action:
                self._update_player_impact(region_id, poi_id, player_action)
                
            if npc_change:
                self._update_npc_impact(region_id, poi_id, npc_change)
                
            if environmental_change:
                self._update_environmental_impact(
                    region_id,
                    poi_id,
                    environmental_change
                )
                
            # Update last update time
            self._last_update.setdefault(region_id, {})[poi_id] = datetime.utcnow()
            
        except Exception as e:
            raise TensionError(f"Failed to update tension: {str(e)}")
            
    def _calculate_time_decay(
        self,
        region_id: str,
        poi_id: str,
        decay_rate: float,
        current_time: Optional[datetime] = None
    ) -> float:
        """Calculate tension decay based on time since last update.
        
        Args:
            region_id: ID of the region
            poi_id: ID of the point of interest
            decay_rate: Rate of decay per hour
            current_time: Optional override for current time
            
        Returns:
            float: Decay factor (0.0 to 1.0)
        """
        try:
            current_time = current_time or datetime.utcnow()
            last_update = self._last_update.get(region_id, {}).get(poi_id)
            
            if not last_update:
                return 0.0
                
            hours_passed = (current_time - last_update).total_seconds() / 3600
            return min(1.0, hours_passed * decay_rate)
            
        except Exception as e:
            raise TensionError(f"Failed to calculate time decay: {str(e)}")
            
    def _get_player_impact(self, region_id: str, poi_id: str) -> float:
        """Get the current impact of player actions on tension.
        
        This considers:
        - Recent combat encounters
        - Stealth actions
        - Resource gathering
        - Quest activities
        
        Returns:
            float: Player impact factor (0.0 to 1.0)
        """
        # Implementation details...
        pass
        
    def _get_npc_impact(self, region_id: str, poi_id: str) -> float:
        """Get the current impact of NPC presence on tension.
        
        This considers:
        - Number of hostile NPCs
        - NPC aggression levels
        - NPC faction relationships
        - Special NPC events
        
        Returns:
            float: NPC impact factor (0.0 to 1.0)
        """
        # Implementation details...
        pass
        
    def _get_environmental_impact(self, region_id: str, poi_id: str) -> float:
        """Get the current impact of environmental factors on tension.
        
        This considers:
        - Time of day
        - Weather conditions
        - Special events
        - Location-specific hazards
        
        Returns:
            float: Environmental impact factor (0.0 to 1.0)
        """
        # Implementation details...
        pass
        
    def _update_player_impact(
        self,
        region_id: str,
        poi_id: str,
        action: str
    ) -> None:
        """Update player impact based on a new action.
        
        Args:
            region_id: ID of the region
            poi_id: ID of the point of interest
            action: Type of player action
        """
        # Implementation details...
        pass
        
    def _update_npc_impact(
        self,
        region_id: str,
        poi_id: str,
        change: Dict
    ) -> None:
        """Update NPC impact based on changes in NPC presence.
        
        Args:
            region_id: ID of the region
            poi_id: ID of the point of interest
            change: Dictionary describing NPC changes
        """
        # Implementation details...
        pass
        
    def _update_environmental_impact(
        self,
        region_id: str,
        poi_id: str,
        change: Dict
    ) -> None:
        """Update environmental impact based on changes in conditions.
        
        Args:
            region_id: ID of the region
            poi_id: ID of the point of interest
            change: Dictionary describing environmental changes
        """
        # Implementation details...
        pass

def decay_region_tension(region) -> None:
    """Decay tension in a region over time."""
    if region.tension > 0:
        region.tension = max(0, region.tension - 0.1)

def check_faction_war_triggers(region) -> List[Dict]:
    """Check for potential faction wars based on tension and relationships."""
    triggered_wars = []
    
    if region.tension < 0.8:  # Only trigger wars at high tension
        return triggered_wars
        
    for faction1 in region.factions:
        for faction2 in region.factions:
            if faction1 != faction2 and faction1.is_hostile_to(faction2.id):
                triggered_wars.append({
                    'faction1_id': faction1.id,
                    'faction2_id': faction2.id,
                    'region_id': region.id,
                    'tension': region.tension
                })
                
    return triggered_wars

def get_regions_by_tension(session, min_tension: float = 0.0) -> List:
    """Get regions filtered by minimum tension level."""
    from app.models.region import Region  # Lazy import to avoid circular dependency
    
    return session.query(Region).filter(
        Region.tension >= min_tension
    ).order_by(Region.tension.desc()).all()

def get_region_factions_at_war(session, region_id: int) -> List[Dict]:
    """Get pairs of factions currently at war in a region."""
    from app.models.region import Region  # Lazy import to avoid circular dependency
    from app.models.faction import Faction  # Lazy import
    
    region = session.query(Region).get(region_id)
    if not region:
        return []
        
    war_pairs = []
    factions = region.factions
    
    for faction1 in factions:
        for faction2 in factions:
            if faction1 != faction2 and faction1.is_hostile_to(faction2.id):
                war_pairs.append({
                    'faction1': faction1,
                    'faction2': faction2
                })
                
    return war_pairs

class TensionUtils:
    pass

__all__ = [
    'decay_region_tension',
    'check_faction_war_triggers',
    'get_regions_by_tension',
    'get_region_factions_at_war'
] 
