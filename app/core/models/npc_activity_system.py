from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import random
import uuid

from app.core.enums import (
    TimeOfDay,
    NPCActivityType,
    NPCProfession,
    NPCRelationshipType,
    WeatherType,
    WeatherIntensity
)
from app.core.models.time_system import TimeSystem
from app.core.models.weather_system import WeatherSystem
from app.utils.constants import (
    HOURS_PER_DAY,
    MINUTES_PER_HOUR,
    BASE_ENERGY_RECOVERY,
    MAX_ENERGY,
    MIN_ENERGY_FOR_ACTIVITY,
    RELATIONSHIP_DECAY_RATE,
    RELATIONSHIP_IMPROVEMENT_RATE
)

@dataclass
class NPCScheduleEntry:
    """Represents a scheduled activity for an NPC."""
    activity_type: NPCActivityType
    start_time: datetime
    duration: timedelta
    location: str
    priority: int = 1
    is_flexible: bool = True
    participants: Set[str] = field(default_factory=set)

@dataclass
class NPCState:
    """Represents the current state of an NPC."""
    id: str
    name: str
    profession: NPCProfession
    current_activity: NPCActivityType
    current_location: str
    energy: float = MAX_ENERGY
    happiness: float = 0.5
    relationships: Dict[str, NPCRelationshipType] = field(default_factory=dict)
    schedule: List[NPCScheduleEntry] = field(default_factory=list)
    needs: Dict[str, float] = field(default_factory=lambda: {
        "rest": 1.0,
        "social": 1.0,
        "work": 1.0,
        "recreation": 1.0
    })

class NPCActivitySystem:
    """Manages NPC activities, schedules, and interactions."""
    
    def __init__(self, time_system: TimeSystem, weather_system: WeatherSystem):
        self.time_system = time_system
        self.weather_system = weather_system
        self.npcs: Dict[str, NPCState] = {}
        self.locations: Dict[str, Dict] = {}
        self.social_groups: Dict[str, Set[str]] = {}
        
    def register_npc(self, name: str, profession: NPCProfession, location: str) -> str:
        """Register a new NPC in the system."""
        npc_id = str(uuid.uuid4())
        npc = NPCState(
            id=npc_id,
            name=name,
            profession=profession,
            current_activity=NPCActivityType.IDLE,
            current_location=location
        )
        self.npcs[npc_id] = npc
        self._generate_initial_schedule(npc)
        return npc_id
    
    def register_location(self, location_id: str, name: str, type: str, capacity: int,
                         allowed_activities: List[NPCActivityType]) -> None:
        """Register a new location where NPCs can perform activities."""
        self.locations[location_id] = {
            "name": name,
            "type": type,
            "capacity": capacity,
            "current_occupants": set(),
            "allowed_activities": set(allowed_activities)
        }
    
    def update(self, delta_time: float) -> None:
        """Update all NPCs' states and activities."""
        current_time = self.time_system.current_time
        current_weather = self.weather_system.current_weather
        
        for npc_id, npc in self.npcs.items():
            # Update needs based on current activity and time passed
            self._update_npc_needs(npc, delta_time)
            
            # Check if current activity should be changed
            if self._should_change_activity(npc, current_time, current_weather):
                next_activity = self._get_next_activity(npc, current_time)
                if next_activity:
                    self._transition_to_activity(npc, next_activity)
            
            # Apply activity effects
            self._apply_activity_effects(npc, delta_time, current_weather)
            
            # Update relationships
            self._update_relationships(npc)
            
            # Generate new schedule entries if needed
            if self._needs_schedule_update(npc):
                self._update_npc_schedule(npc)
    
    def _update_npc_needs(self, npc: NPCState, delta_time: float) -> None:
        """Update NPC's needs based on their current activity and time passed."""
        hours_passed = delta_time / 3600  # Convert seconds to hours
        
        # Apply activity effects on needs
        activity_effects = {
            NPCActivityType.SLEEPING: {"rest": 0.2},
            NPCActivityType.WORKING: {"work": 0.1, "rest": -0.05},
            NPCActivityType.SOCIALIZING: {"social": 0.15, "energy": -0.02},
            NPCActivityType.RECREATION: {"recreation": 0.1, "rest": -0.02},
            NPCActivityType.EATING: {"energy": 0.1},
            NPCActivityType.TRAVELING: {"energy": -0.05},
            NPCActivityType.MAINTENANCE: {"work": 0.05, "energy": -0.03},
            NPCActivityType.SHOPPING: {"recreation": 0.05, "energy": -0.02},
            NPCActivityType.EMERGENCY: {"energy": -0.1}
        }
        
        if npc.current_activity in activity_effects:
            effects = activity_effects[npc.current_activity]
            for need, change in effects.items():
                if need == "energy":
                    npc.energy = max(0.0, min(MAX_ENERGY, npc.energy + change * hours_passed))
                else:
                    npc.needs[need] = max(0.0, min(1.0, npc.needs[need] + change * hours_passed))
        
        # Natural decay of needs over time
        decay_rate = 0.02 * hours_passed
        for need in npc.needs:
            npc.needs[need] = max(0.0, npc.needs[need] - decay_rate)
    
    def _should_change_activity(self, npc: NPCState, current_time: datetime,
                              current_weather: Tuple[WeatherType, WeatherIntensity]) -> bool:
        """Determine if the NPC should change their current activity."""
        if not npc.schedule:
            return True
            
        current_schedule = next((s for s in npc.schedule if 
            s.start_time <= current_time < (s.start_time + s.duration)), None)
            
        if not current_schedule:
            return True
            
        # Check if current activity is weather-appropriate
        weather_type, intensity = current_weather
        if (weather_type.movement_speed_modifier < 0.5 and 
            npc.current_activity.weather_sensitivity > 0.7):
            return True
            
        # Check if NPC has enough energy for current activity
        if npc.energy < MIN_ENERGY_FOR_ACTIVITY:
            return True
            
        # Check if any critical needs are too low
        critical_needs = {
            "rest": 0.2,
            "social": 0.3,
            "work": 0.4
        }
        for need, threshold in critical_needs.items():
            if npc.needs[need] < threshold:
                return True
                
        return False
    
    def _get_next_activity(self, npc: NPCState, current_time: datetime) -> Optional[NPCScheduleEntry]:
        """Determine the next activity for the NPC based on their schedule and needs."""
        # First check scheduled activities
        next_scheduled = next((s for s in npc.schedule if s.start_time > current_time), None)
        
        # If energy is critically low, override with rest
        if npc.energy < MIN_ENERGY_FOR_ACTIVITY:
            return NPCScheduleEntry(
                activity_type=NPCActivityType.SLEEPING,
                start_time=current_time,
                duration=timedelta(hours=1),
                location=npc.current_location,
                priority=3
            )
        
        # Check for critical needs
        critical_need = None
        critical_threshold = 0.2
        for need, value in npc.needs.items():
            if value < critical_threshold:
                critical_need = need
                break
        
        if critical_need:
            # Map needs to activities
            need_activities = {
                "rest": NPCActivityType.SLEEPING,
                "social": NPCActivityType.SOCIALIZING,
                "work": NPCActivityType.WORKING,
                "recreation": NPCActivityType.RECREATION
            }
            return NPCScheduleEntry(
                activity_type=need_activities[critical_need],
                start_time=current_time,
                duration=timedelta(hours=1),
                location=self._find_suitable_location(npc, need_activities[critical_need]),
                priority=2
            )
        
        return next_scheduled or NPCScheduleEntry(
            activity_type=NPCActivityType.IDLE,
            start_time=current_time,
            duration=timedelta(minutes=30),
            location=npc.current_location,
            priority=0
        )
    
    def _transition_to_activity(self, npc: NPCState, new_activity: NPCScheduleEntry) -> None:
        """Handle the transition to a new activity."""
        # Leave old location
        if npc.current_location in self.locations:
            self.locations[npc.current_location]["current_occupants"].remove(npc.id)
        
        # Enter new location
        if new_activity.location in self.locations:
            self.locations[new_activity.location]["current_occupants"].add(npc.id)
        
        # Update NPC state
        npc.current_activity = new_activity.activity_type
        npc.current_location = new_activity.location
        
        # Handle social activities
        if new_activity.activity_type == NPCActivityType.SOCIALIZING:
            self._handle_social_interaction(npc)
    
    def _apply_activity_effects(self, npc: NPCState, delta_time: float,
                              current_weather: Tuple[WeatherType, WeatherIntensity]) -> None:
        """Apply the effects of the current activity and conditions on the NPC."""
        weather_type, intensity = current_weather
        hours_passed = delta_time / 3600
        
        # Apply energy costs
        energy_cost = npc.current_activity.energy_cost * hours_passed
        weather_modifier = 1.0
        if npc.current_activity.weather_sensitivity > 0.5:
            weather_modifier = weather_type.movement_speed_modifier * intensity.effect_multiplier
        
        npc.energy = max(0.0, min(MAX_ENERGY, npc.energy - (energy_cost * weather_modifier)))
        
        # Update happiness based on activity success and conditions
        activity_satisfaction = self._calculate_activity_satisfaction(npc, weather_modifier)
        npc.happiness = max(0.0, min(1.0, npc.happiness + activity_satisfaction * hours_passed))
    
    def _update_relationships(self, npc: NPCState) -> None:
        """Update NPC's relationships based on interactions and time."""
        current_time = self.time_system.current_time
        
        # Decay relationships over time
        for other_id in list(npc.relationships.keys()):
            if other_id not in self.npcs:
                del npc.relationships[other_id]
                continue
                
            relationship = npc.relationships[other_id]
            if relationship != NPCRelationshipType.FAMILY:  # Family relationships don't decay
                decay = RELATIONSHIP_DECAY_RATE
                if relationship == NPCRelationshipType.ENEMY:
                    decay *= 0.5  # Enemies decay slower
                elif relationship == NPCRelationshipType.RIVAL:
                    decay *= 0.7  # Rivals decay slower
                
                # Calculate new relationship level
                current_level = relationship.social_modifier
                new_level = max(-1.0, min(1.0, current_level - decay))
                
                # Convert back to relationship type
                if new_level <= -0.6:
                    npc.relationships[other_id] = NPCRelationshipType.ENEMY
                elif new_level <= -0.2:
                    npc.relationships[other_id] = NPCRelationshipType.RIVAL
                elif new_level <= 0.2:
                    npc.relationships[other_id] = NPCRelationshipType.STRANGER
                elif new_level <= 0.4:
                    npc.relationships[other_id] = NPCRelationshipType.ACQUAINTANCE
                elif new_level <= 0.6:
                    npc.relationships[other_id] = NPCRelationshipType.FRIEND
                elif new_level > 0.6:
                    npc.relationships[other_id] = NPCRelationshipType.CLOSE_FRIEND
    
    def _generate_initial_schedule(self, npc: NPCState) -> None:
        """Generate an initial schedule for a new NPC based on their profession."""
        current_time = self.time_system.current_time
        template = npc.profession.schedule_template
        
        # Clear existing schedule
        npc.schedule.clear()
        
        # Generate a week's worth of activities
        for day in range(7):
            day_start = current_time.replace(hour=0, minute=0, second=0) + timedelta(days=day)
            
            for time_of_day, activities in template.items():
                for activity in activities:
                    # Find appropriate location
                    location = self._find_suitable_location(npc, activity)
                    
                    # Calculate start time and duration based on time of day
                    if time_of_day == TimeOfDay.DAWN:
                        start_hour = 5
                    elif time_of_day == TimeOfDay.MORNING:
                        start_hour = 8
                    elif time_of_day == TimeOfDay.NOON:
                        start_hour = 12
                    elif time_of_day == TimeOfDay.AFTERNOON:
                        start_hour = 14
                    elif time_of_day == TimeOfDay.DUSK:
                        start_hour = 18
                    else:  # NIGHT
                        start_hour = 21
                    
                    start_time = day_start.replace(hour=start_hour)
                    
                    # Duration depends on activity type
                    if activity == NPCActivityType.SLEEPING:
                        duration = timedelta(hours=8)
                    elif activity == NPCActivityType.WORKING:
                        duration = timedelta(hours=4)
                    elif activity == NPCActivityType.EATING:
                        duration = timedelta(hours=1)
                    else:
                        duration = timedelta(hours=2)
                    
                    schedule_entry = NPCScheduleEntry(
                        activity_type=activity,
                        start_time=start_time,
                        duration=duration,
                        location=location,
                        priority=2 if activity in [NPCActivityType.SLEEPING, NPCActivityType.WORKING] else 1
                    )
                    
                    npc.schedule.append(schedule_entry)
        
        # Sort schedule by start time
        npc.schedule.sort(key=lambda x: x.start_time)
    
    def _update_npc_schedule(self, npc: NPCState) -> None:
        """Update an NPC's schedule with new activities."""
        # Remove past schedule entries
        current_time = self.time_system.current_time
        npc.schedule = [s for s in npc.schedule if s.start_time + s.duration > current_time]
        
        # If schedule is getting low, generate more
        if len(npc.schedule) < 10:
            last_time = max((s.start_time + s.duration for s in npc.schedule), default=current_time)
            template = npc.profession.schedule_template
            
            # Generate next 3 days of activities
            for day in range(3):
                day_start = last_time.replace(hour=0, minute=0, second=0) + timedelta(days=day)
                
                for time_of_day, activities in template.items():
                    for activity in activities:
                        location = self._find_suitable_location(npc, activity)
                        
                        # Use same time calculations as in _generate_initial_schedule
                        if time_of_day == TimeOfDay.DAWN:
                            start_hour = 5
                        elif time_of_day == TimeOfDay.MORNING:
                            start_hour = 8
                        elif time_of_day == TimeOfDay.NOON:
                            start_hour = 12
                        elif time_of_day == TimeOfDay.AFTERNOON:
                            start_hour = 14
                        elif time_of_day == TimeOfDay.DUSK:
                            start_hour = 18
                        else:  # NIGHT
                            start_hour = 21
                        
                        start_time = day_start.replace(hour=start_hour)
                        
                        if activity == NPCActivityType.SLEEPING:
                            duration = timedelta(hours=8)
                        elif activity == NPCActivityType.WORKING:
                            duration = timedelta(hours=4)
                        elif activity == NPCActivityType.EATING:
                            duration = timedelta(hours=1)
                        else:
                            duration = timedelta(hours=2)
                        
                        schedule_entry = NPCScheduleEntry(
                            activity_type=activity,
                            start_time=start_time,
                            duration=duration,
                            location=location,
                            priority=2 if activity in [NPCActivityType.SLEEPING, NPCActivityType.WORKING] else 1
                        )
                        
                        npc.schedule.append(schedule_entry)
            
            # Sort updated schedule
            npc.schedule.sort(key=lambda x: x.start_time)
    
    def _find_suitable_location(self, npc: NPCState, activity: NPCActivityType) -> str:
        """Find a suitable location for the given activity."""
        suitable_locations = [
            loc_id for loc_id, loc_data in self.locations.items()
            if activity in loc_data["allowed_activities"] and
            len(loc_data["current_occupants"]) < loc_data["capacity"]
        ]
        
        if suitable_locations:
            return random.choice(suitable_locations)
        return npc.current_location  # Fallback to current location if no suitable place found
    
    def _handle_social_interaction(self, npc: NPCState) -> None:
        """Handle social interaction between NPCs in the same location."""
        if npc.current_location not in self.locations:
            return
            
        location = self.locations[npc.current_location]
        other_npcs = location["current_occupants"] - {npc.id}
        
        for other_id in other_npcs:
            if other_id not in self.npcs:
                continue
                
            other_npc = self.npcs[other_id]
            
            # Initialize relationship if it doesn't exist
            if other_id not in npc.relationships:
                npc.relationships[other_id] = NPCRelationshipType.STRANGER
            if npc.id not in other_npc.relationships:
                other_npc.relationships[npc.id] = NPCRelationshipType.STRANGER
            
            # Calculate interaction success chance
            base_chance = 0.6
            relationship_mod = (npc.relationships[other_id].social_modifier + 1) / 2  # Convert -1..1 to 0..1
            profession_compatibility = 0.2 if npc.profession == other_npc.profession else 0
            
            success_chance = base_chance + relationship_mod + profession_compatibility
            
            # Determine interaction outcome
            if random.random() < success_chance:
                # Positive interaction
                self._improve_relationship(npc, other_npc)
                npc.happiness = min(1.0, npc.happiness + 0.1)
                other_npc.happiness = min(1.0, other_npc.happiness + 0.1)
            else:
                # Negative interaction
                self._worsen_relationship(npc, other_npc)
                npc.happiness = max(0.0, npc.happiness - 0.1)
                other_npc.happiness = max(0.0, other_npc.happiness - 0.1)
    
    def _improve_relationship(self, npc1: NPCState, npc2: NPCState) -> None:
        """Improve the relationship between two NPCs."""
        def improve_one_way(a: NPCState, b: NPCState):
            current = a.relationships[b.id]
            current_value = current.social_modifier
            new_value = min(1.0, current_value + RELATIONSHIP_IMPROVEMENT_RATE)
            
            if new_value >= 0.8:
                a.relationships[b.id] = NPCRelationshipType.CLOSE_FRIEND
            elif new_value >= 0.5:
                a.relationships[b.id] = NPCRelationshipType.FRIEND
            elif new_value >= 0.2:
                a.relationships[b.id] = NPCRelationshipType.ACQUAINTANCE
            elif new_value >= 0:
                a.relationships[b.id] = NPCRelationshipType.STRANGER
        
        improve_one_way(npc1, npc2)
        improve_one_way(npc2, npc1)
    
    def _worsen_relationship(self, npc1: NPCState, npc2: NPCState) -> None:
        """Worsen the relationship between two NPCs."""
        def worsen_one_way(a: NPCState, b: NPCState):
            current = a.relationships[b.id]
            current_value = current.social_modifier
            new_value = max(-1.0, current_value - RELATIONSHIP_IMPROVEMENT_RATE)
            
            if new_value <= -0.6:
                a.relationships[b.id] = NPCRelationshipType.ENEMY
            elif new_value <= -0.2:
                a.relationships[b.id] = NPCRelationshipType.RIVAL
            elif new_value <= 0.2:
                a.relationships[b.id] = NPCRelationshipType.STRANGER
        
        worsen_one_way(npc1, npc2)
        worsen_one_way(npc2, npc1)
    
    def _calculate_activity_satisfaction(self, npc: NPCState, weather_modifier: float) -> float:
        """Calculate how satisfied the NPC is with their current activity."""
        base_satisfaction = 0.05  # Small positive by default
        
        # Activity-specific satisfaction
        if npc.current_activity == NPCActivityType.SLEEPING and npc.needs["rest"] < 0.3:
            base_satisfaction += 0.1
        elif npc.current_activity == NPCActivityType.WORKING and npc.needs["work"] < 0.3:
            base_satisfaction += 0.08
        elif npc.current_activity == NPCActivityType.SOCIALIZING and npc.needs["social"] < 0.3:
            base_satisfaction += 0.12
        elif npc.current_activity == NPCActivityType.RECREATION and npc.needs["recreation"] < 0.3:
            base_satisfaction += 0.1
        
        # Weather impact
        if npc.current_activity.weather_sensitivity > 0.5:
            base_satisfaction *= weather_modifier
        
        # Energy level impact
        if npc.energy < MIN_ENERGY_FOR_ACTIVITY:
            base_satisfaction *= 0.5
        
        return base_satisfaction
    
    def _needs_schedule_update(self, npc: NPCState) -> bool:
        """Determine if the NPC's schedule needs to be updated."""
        if not npc.schedule:
            return True
            
        # Check if we're running low on scheduled activities
        current_time = self.time_system.current_time
        future_activities = [s for s in npc.schedule if s.start_time > current_time]
        
        return len(future_activities) < 10  # Maintain at least 10 future activities 