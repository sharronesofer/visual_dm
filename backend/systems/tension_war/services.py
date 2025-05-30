"""
Tension and War Management Services

This module implements the core services for tension and war management:
- TensionManager: Manages faction tensions, updates, and decay
- WarManager: Manages war initialization, battle simulation, and outcomes

These services consolidate and replace functionality previously scattered across
tension_utils.py and war_utils.py.
"""

from typing import Dict, List, Optional, Tuple, Any
import random
import math
from datetime import datetime, timedelta
from enum import Enum
from fastapi import HTTPException

from app.core.logging import logger
from app.core.events.event_dispatcher import EventDispatcher

from .models import TensionLevel, WarOutcomeType
from .utils import (
    calculate_border_tension,
    calculate_event_tension,
    calculate_disputed_regions,
    calculate_war_chances,
    evaluate_battle_outcome,
    calculate_resource_changes
)

# Database interface (this should be replaced with your actual database implementation)
class DBInterface:
    """Simple database interface for demonstration purposes.
    In a real implementation, this would connect to your actual database.
    """
    
    @staticmethod
    def get_region_tensions(region_id: str) -> Dict[str, int]:
        """Get tension values for factions in a region"""
        # In a real implementation, this would fetch from your database
        # For now, return sample data
        return {
            "faction_a": 30,
            "faction_b": 50,
            "faction_c": -20
        }
    
    @staticmethod
    def set_region_tension(region_id: str, faction: str, value: int) -> None:
        """Set tension value for a faction in a region"""
        # In a real implementation, this would update your database
        # For now, just log the action
        logger.info(f"Setting tension for {faction} in {region_id} to {value}")
    
    @staticmethod
    def get_region_tension_history(region_id: str) -> List[Dict[str, Any]]:
        """Get tension history for a region"""
        # In a real implementation, this would fetch from your database
        # For now, return sample data
        return [
            {
                "timestamp": datetime.utcnow() - timedelta(days=3),
                "faction": "faction_a",
                "value": 25,
                "reason": "border_dispute"
            },
            {
                "timestamp": datetime.utcnow() - timedelta(days=2),
                "faction": "faction_b",
                "value": 45,
                "reason": "trade_conflict"
            }
        ]
    
    @staticmethod
    def add_tension_history_entry(region_id: str, faction: str, value: int, reason: Optional[str]) -> None:
        """Add an entry to tension history"""
        # In a real implementation, this would update your database
        # For now, just log the action
        logger.info(f"Adding tension history entry for {faction} in {region_id}: {value} ({reason})")
    
    @staticmethod
    def get_war_status(region_id: str) -> Dict[str, Any]:
        """Get war status for a region"""
        # In a real implementation, this would fetch from your database
        # For now, return sample data
        return {
            "is_active": True,
            "faction_a": "kingdom_of_arendelle",
            "faction_b": "southern_isles",
            "start_date": datetime.utcnow() - timedelta(days=5),
            "day": 5,
            "controlled_pois": {
                "kingdom_of_arendelle": ["arendelle_castle", "northern_forest"],
                "southern_isles": ["southern_harbor", "mountain_pass"]
            },
            "battle_log": [
                {
                    "day": 2,
                    "victor": "kingdom_of_arendelle",
                    "loser": "southern_isles",
                    "location": "mountain_pass",
                    "victor_losses": 20,
                    "loser_losses": 35,
                    "timestamp": datetime.utcnow() - timedelta(days=3),
                    "description": "Battle at the mountain pass"
                }
            ]
        }
    
    @staticmethod
    def set_war_status(region_id: str, war_data: Dict[str, Any]) -> None:
        """Set war status for a region"""
        # In a real implementation, this would update your database
        # For now, just log the action
        logger.info(f"Setting war status for {region_id}: {war_data}")
    
    @staticmethod
    def update_poi_control(region: str, poi_id: str, faction: str) -> None:
        """Update POI control by a faction"""
        # In a real implementation, this would update your database
        # For now, just log the action
        logger.info(f"Updating POI control: {poi_id} in {region} now controlled by {faction}")


class TensionManager:
    """
    Manages faction tension relationships, updates, and decay.
    
    Tension ranges from -100 (alliance) to +100 (war/hostile)
    with decay over time in both directions.
    """
    
    def __init__(self):
        """Initialize the TensionManager."""
        self.db = DBInterface()
        self._tension_levels = {
            (-100, -76): TensionLevel.ALLIANCE,
            (-75, -26): TensionLevel.FRIENDLY,
            (-25, 25): TensionLevel.NEUTRAL,
            (26, 50): TensionLevel.RIVALRY,
            (51, 99): TensionLevel.HOSTILE,
            (100, 100): TensionLevel.WAR
        }
        self._last_update = {}  # Used for tracking last update times
        self.event_dispatcher = EventDispatcher.get_instance()
    
    def get_tension(self, region_id: str) -> Dict[str, Any]:
        """
        Get current tension values for factions in a region.
        
        Args:
            region_id: The ID of the region to get tension for
            
        Returns:
            Dict containing region_id, tensions, and last_updated timestamps
        """
        tensions = self.db.get_region_tensions(region_id)
        
        # In a real implementation, you would fetch last_updated timestamps from your database
        # For now, use the current time
        last_updated = {faction: datetime.utcnow() for faction in tensions}
        
        return {
            "region_id": region_id,
            "tensions": tensions,
            "last_updated": last_updated
        }
    
    def modify_tension(self, region_id: str, faction: str, value: int, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Modify tension for a faction in a region.
        
        Args:
            region_id: The ID of the region to modify tension for
            faction: The faction to modify tension for
            value: The amount to modify tension by (positive or negative)
            reason: Optional reason for the tension change
            
        Returns:
            Dict containing updated tension information
        """
        # Get current tensions
        current_tensions = self.db.get_region_tensions(region_id)
        
        # Update tension for the specific faction
        current_value = current_tensions.get(faction, 0)
        new_value = max(-100, min(100, current_value + value))
        current_tensions[faction] = new_value
        
        # Update in database
        self.db.set_region_tension(region_id, faction, new_value)
        
        # Add to history
        self.db.add_tension_history_entry(region_id, faction, value, reason)
        
        # Update last_updated timestamp
        # In a real implementation, you would store this in your database
        now = datetime.utcnow()
        if region_id not in self._last_update:
            self._last_update[region_id] = {}
        self._last_update[region_id][faction] = now
        
        # Emit event if needed
        # self.event_dispatcher.publish_sync(TensionChangedEvent(...))
        
        # Return updated tension information
        return {
            "region_id": region_id,
            "tensions": current_tensions,
            "last_updated": {faction: now for faction in current_tensions}
        }
    
    def reset_tension(self, region_id: str) -> Dict[str, Any]:
        """
        Reset all tension values for a region to zero.
        
        Args:
            region_id: The ID of the region to reset tension for
            
        Returns:
            Dict containing updated tension information
        """
        # Get current tensions
        current_tensions = self.db.get_region_tensions(region_id)
        
        # Reset all tensions to zero
        for faction in current_tensions:
            current_tensions[faction] = 0
            self.db.set_region_tension(region_id, faction, 0)
            self.db.add_tension_history_entry(region_id, faction, 0, "reset")
        
        # Update last_updated timestamps
        now = datetime.utcnow()
        if region_id not in self._last_update:
            self._last_update[region_id] = {}
        for faction in current_tensions:
            self._last_update[region_id][faction] = now
        
        # Return updated tension information
        return {
            "region_id": region_id,
            "tensions": current_tensions,
            "last_updated": {faction: now for faction in current_tensions}
        }
    
    def decay_tension(self, region_id: str, decay_rate: float = 1.0) -> Dict[str, Any]:
        """
        Apply decay to tension values for a region.
        
        Args:
            region_id: The ID of the region to decay tension for
            decay_rate: Multiplier for tension decay (default: 1.0)
            
        Returns:
            Dict containing updated tension information
        """
        # Get current tensions
        current_tensions = self.db.get_region_tensions(region_id)
        
        # Apply decay to each tension value
        for faction, tension in current_tensions.items():
            # Calculate decay amount
            # Tension decays towards 0 at a rate of 1-5% per day
            decay_amount = max(1, abs(tension) * 0.03) * decay_rate
            
            # Apply decay in the appropriate direction
            if tension > 0:
                new_value = max(0, tension - decay_amount)
            elif tension < 0:
                new_value = min(0, tension + decay_amount)
            else:
                new_value = 0
            
            # Update tension
            current_tensions[faction] = int(new_value)
            self.db.set_region_tension(region_id, faction, int(new_value))
            self.db.add_tension_history_entry(region_id, faction, int(new_value) - tension, "decay")
        
        # Update last_updated timestamps
        now = datetime.utcnow()
        if region_id not in self._last_update:
            self._last_update[region_id] = {}
        for faction in current_tensions:
            self._last_update[region_id][faction] = now
        
        # Return updated tension information
        return {
            "region_id": region_id,
            "tensions": current_tensions,
            "last_updated": {faction: now for faction in current_tensions}
        }
    
    def get_tension_level(self, tension_value: float) -> TensionLevel:
        """
        Get the tension level category for a given tension value.
        
        Args:
            tension_value: The tension value to categorize
            
        Returns:
            TensionLevel enum value
        """
        for (min_val, max_val), level in self._tension_levels.items():
            if min_val <= tension_value <= max_val:
                return level
        
        # Default if no match (should not happen if ranges are complete)
        return TensionLevel.NEUTRAL
    
    def update_tension(self, faction_a_id: str, faction_b_id: str, value: float, reason: Optional[str] = None) -> float:
        """
        Update tension between two factions.
        
        Args:
            faction_a_id: ID of the first faction
            faction_b_id: ID of the second faction
            value: The change in tension (positive or negative)
            reason: Optional reason for the tension change
            
        Returns:
            New tension value
        """
        # Normalize faction order (e.g., "A, B" same as "B, A")
        if faction_a_id > faction_b_id:
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        # Get current tension
        current_tension = 0  # In a real implementation, fetch from database
        
        # Calculate new tension value
        new_tension = max(-100, min(100, current_tension + value))
        
        # Update last_update timestamp
        now = datetime.utcnow()
        if faction_a_id not in self._last_update:
            self._last_update[faction_a_id] = {}
        self._last_update[faction_a_id][faction_b_id] = now
        
        # In a real implementation, update in database
        
        # Emit event if needed
        # self.event_dispatcher.publish_sync(TensionChangedEvent(...))
        
        return new_tension


class WarManager:
    """
    Manages war declaration, simulation, and outcomes between factions.
    
    This includes:
    - War declaration and initiation
    - Battle simulation
    - Daily war advancement
    - War outcome determination
    """
    
    def __init__(self):
        """Initialize the WarManager."""
        self.db = DBInterface()
        self.event_dispatcher = EventDispatcher.get_instance()
    
    def get_war_status(self, region_id: str) -> Dict[str, Any]:
        """
        Get current war status for a region.
        
        Args:
            region_id: The ID of the region to get war status for
            
        Returns:
            Dict containing war status information
        """
        war_status = self.db.get_war_status(region_id)
        
        return {
            "region_id": region_id,
            "is_active": war_status["is_active"],
            "faction_a": war_status.get("faction_a"),
            "faction_b": war_status.get("faction_b"),
            "start_date": war_status.get("start_date"),
            "day": war_status.get("day"),
            "controlled_pois": war_status.get("controlled_pois"),
            "battle_log": war_status.get("battle_log", [])
        }
    
    def initialize_war(self, region_a: str, region_b: str, faction_a: str, faction_b: str) -> Dict[str, Any]:
        """
        Initialize a new war between two factions in their respective regions.
        
        Args:
            region_a: ID of the first region
            region_b: ID of the second region
            faction_a: ID of the first faction
            faction_b: ID of the second faction
            
        Returns:
            Dict containing initialized war status
        """
        # Create war data
        war_data = {
            "is_active": True,
            "faction_a": faction_a,
            "faction_b": faction_b,
            "start_date": datetime.utcnow(),
            "day": 0,
            "controlled_pois": {
                faction_a: [],  # Would populate with controlled POIs in region_a
                faction_b: []   # Would populate with controlled POIs in region_b
            },
            "battle_log": []
        }
        
        # Update war status in both regions
        self.db.set_war_status(region_a, war_data)
        self.db.set_war_status(region_b, war_data)
        
        # Emit event if needed
        # self.event_dispatcher.publish_sync(WarDeclaredEvent(...))
        
        # Return updated war status
        return {
            "region_id": region_a,  # Return status for the first region
            "is_active": True,
            "faction_a": faction_a,
            "faction_b": faction_b,
            "start_date": war_data["start_date"],
            "day": 0,
            "controlled_pois": war_data["controlled_pois"],
            "battle_log": []
        }
    
    def advance_war_day(self, region_id: str) -> Dict[str, Any]:
        """
        Advance the war by one day in the specified region.
        
        Args:
            region_id: The ID of the region to advance war for
            
        Returns:
            Dict containing updated war status and events that occurred
        """
        # Get current war status
        war_status = self.db.get_war_status(region_id)
        
        # Check if war is active
        if not war_status["is_active"]:
            raise HTTPException(status_code=400, detail="No active war in this region")
        
        # Increment day
        new_day = war_status["day"] + 1
        war_status["day"] = new_day
        
        # Simulate events for this day
        events = []
        new_raids = []
        
        # Determine if a battle occurs
        battle_chance = 0.3  # 30% chance of battle per day
        if random.random() < battle_chance:
            battle = evaluate_battle_outcome(
                faction_a_id=war_status["faction_a"],
                faction_b_id=war_status["faction_b"],
                faction_a_strength=random.randint(80, 120),  # Mock strength values
                faction_b_strength=random.randint(80, 120),
                battle_location=region_id
            )
            
            # Add timestamp and day
            battle["timestamp"] = datetime.utcnow()
            battle["day"] = new_day
            
            # Add to battle log
            war_status["battle_log"].append(battle)
            
            # Add to events
            events.append({
                "type": "battle",
                "data": battle
            })
        
        # Generate raids
        raid_chance = 0.4  # 40% chance of raids per day
        if random.random() < raid_chance:
            raids = self.generate_daily_raids(region_id)
            new_raids = raids
            
            # Add to events
            for raid in raids:
                events.append({
                    "type": "raid",
                    "data": raid
                })
        
        # Determine if war continues
        continues = True
        end_reason = None
        
        # Check victory conditions (simplified)
        faction_a_victories = sum(1 for battle in war_status["battle_log"] if battle["victor"] == war_status["faction_a"])
        faction_b_victories = sum(1 for battle in war_status["battle_log"] if battle["victor"] == war_status["faction_b"])
        
        # If one side has won significantly more battles, they may win the war
        victory_threshold = 3  # Need 3 more victories than opponent
        if faction_a_victories - faction_b_victories >= victory_threshold:
            continues = False
            end_reason = f"{war_status['faction_a']} achieves victory"
        elif faction_b_victories - faction_a_victories >= victory_threshold:
            continues = False
            end_reason = f"{war_status['faction_b']} achieves victory"
        
        # Update war status
        war_status["is_active"] = continues
        self.db.set_war_status(region_id, war_status)
        
        # If war ended, emit event
        if not continues:
            # self.event_dispatcher.publish_sync(WarEndedEvent(...))
            pass
        
        # Return updated status and events
        return {
            "region_id": region_id,
            "day": new_day,
            "events": events,
            "new_raids": new_raids,
            "continues": continues,
            "end_reason": end_reason
        }
    
    def record_poi_conquest(self, region: str, poi_id: str, faction: str) -> Dict[str, Any]:
        """
        Record the conquest of a POI by a faction.
        
        Args:
            region: The ID of the region where the POI is located
            poi_id: The ID of the POI being conquered
            faction: The ID of the faction conquering the POI
            
        Returns:
            Dict containing conquest information
        """
        # Get current war status
        war_status = self.db.get_war_status(region)
        
        # Check if war is active
        if not war_status["is_active"]:
            raise HTTPException(status_code=400, detail="No active war in this region")
        
        # Check if faction is involved in the war
        if faction != war_status["faction_a"] and faction != war_status["faction_b"]:
            raise HTTPException(status_code=400, detail="Faction not involved in this war")
        
        # Update POI control
        self.db.update_poi_control(region, poi_id, faction)
        
        # Update POI in controlled_pois
        opposing_faction = war_status["faction_a"] if faction == war_status["faction_b"] else war_status["faction_b"]
        
        # Add to conquering faction's list if not already there
        if poi_id not in war_status["controlled_pois"].get(faction, []):
            if faction not in war_status["controlled_pois"]:
                war_status["controlled_pois"][faction] = []
            war_status["controlled_pois"][faction].append(poi_id)
        
        # Remove from opposing faction's list if present
        if opposing_faction in war_status["controlled_pois"]:
            if poi_id in war_status["controlled_pois"][opposing_faction]:
                war_status["controlled_pois"][opposing_faction].remove(poi_id)
        
        # Update war status
        self.db.set_war_status(region, war_status)
        
        # Emit event if needed
        # self.event_dispatcher.publish_sync(PoiConquestEvent(...))
        
        # Return conquest information
        return {
            "region": region,
            "poi_id": poi_id,
            "faction": faction,
            "timestamp": datetime.utcnow(),
            "day": war_status["day"]
        }
    
    def generate_daily_raids(self, region_id: str) -> List[Dict[str, Any]]:
        """
        Generate daily raids for a region in war.
        
        Args:
            region_id: The ID of the region to generate raids for
            
        Returns:
            List of raid events
        """
        # Get current war status
        war_status = self.db.get_war_status(region_id)
        
        # Check if war is active
        if not war_status["is_active"]:
            raise HTTPException(status_code=400, detail="No active war in this region")
        
        # Determine available targets for each faction
        # In a real implementation, fetch actual POIs from the region
        faction_a_targets = ["town_1", "farm_1", "outpost_1"]  # Mock targets
        faction_b_targets = ["city_1", "mine_1", "castle_1"]   # Mock targets
        
        # Generate raids
        raids = []
        num_raids = random.randint(1, 3)  # 1-3 raids per day
        
        for _ in range(num_raids):
            # Randomly select attacker
            if random.random() < 0.5:
                attacker = war_status["faction_a"]
                defender = war_status["faction_b"]
                targets = faction_b_targets
            else:
                attacker = war_status["faction_b"]
                defender = war_status["faction_a"]
                targets = faction_a_targets
            
            # Select a target
            if not targets:
                continue
            target = random.choice(targets)
            
            # Determine success
            success = random.random() < 0.6  # 60% success rate
            
            # Calculate losses
            losses = random.randint(5, 20)
            
            # Generate plunder if successful
            plunder = None
            if success:
                plunder = {
                    "gold": random.randint(50, 200),
                    "supplies": random.randint(10, 50)
                }
            
            # Create raid event
            raid = {
                "attacker": attacker,
                "defender": defender,
                "target": target,
                "success": success,
                "losses": losses,
                "plunder": plunder,
                "timestamp": datetime.utcnow(),
                "description": f"Raid on {target} by {attacker} forces"
            }
            
            raids.append(raid)
        
        return raids
    
    def declare_war(self, faction_a_id: str, faction_b_id: str, disputed_regions: List[str] = None) -> Dict[str, Any]:
        """
        Declare war between two factions.
        
        Args:
            faction_a_id: ID of the first faction
            faction_b_id: ID of the second faction
            disputed_regions: Optional list of disputed region IDs
            
        Returns:
            War state object
        """
        # In a real implementation, you would:
        # 1. Check if a war already exists between these factions
        # 2. Create a war entry in your database
        # 3. Initialize war state data
        
        # For now, return a mock war state
        return {
            "faction_a_id": faction_a_id,
            "faction_b_id": faction_b_id,
            "start_date": datetime.utcnow(),
            "disputed_regions": disputed_regions or [],
            "exhaustion_a": 0.0,
            "exhaustion_b": 0.0,
            "battles": [],
            "is_active": True
        }
    
    def get_war(self, faction_a_id: str, faction_b_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current war state between two factions.
        
        Args:
            faction_a_id: ID of the first faction
            faction_b_id: ID of the second faction
            
        Returns:
            War state object or None if no active war
        """
        # In a real implementation, you would fetch from your database
        # For now, return mock data or None
        if random.random() < 0.5:  # 50% chance of active war for demo
            return {
                "faction_a_id": faction_a_id,
                "faction_b_id": faction_b_id,
                "start_date": datetime.utcnow() - timedelta(days=random.randint(5, 20)),
                "disputed_regions": ["region_1", "region_2"],
                "exhaustion_a": random.uniform(0.1, 0.5),
                "exhaustion_b": random.uniform(0.1, 0.5),
                "battles": [],
                "is_active": True
            }
        return None
    
    def end_war(self, war: Dict[str, Any], outcome_type: WarOutcomeType, winner_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        End a war with a specified outcome.
        
        Args:
            war: The war state object
            outcome_type: Type of war outcome
            winner_id: Optional ID of winning faction
            
        Returns:
            Tuple of (success, reason)
        """
        # Validate outcome
        if outcome_type in [WarOutcomeType.DECISIVE_VICTORY, WarOutcomeType.VICTORY] and not winner_id:
            return False, "Winner must be specified for victory outcomes"
        
        if winner_id and winner_id not in [war["faction_a_id"], war["faction_b_id"]]:
            return False, "Winner must be one of the war participants"
        
        # Update war state
        war["is_active"] = False
        
        # In a real implementation, you would update your database
        
        # Emit event if needed
        # self.event_dispatcher.publish_sync(WarEndedEvent(...))
        
        return True, "War ended successfully" 