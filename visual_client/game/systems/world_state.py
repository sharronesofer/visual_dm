from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import random
import json
import os

"""
WorldState: Manages the game world's state, events, and world-tick progression.

Includes WorldTickEventSystem for monster siege event generation and extensible world-tick triggers.
"""

class WorldTickEventSystem:
    """
    Manages world-tick events, including monster siege triggers.

    Extension points:
    - Add new trigger conditions by extending _load_trigger_conditions and implementing new methods.
    - Add new event types by extending _generate_siege_event or adding new event generators.
    - Integrate with NPC memory, settlements, or API by extending _process_event_queue or event generation logic.
    - Configure tick interval and probability logic as needed (see config loading below).
    - Monster data is loaded from data/schemas/monsters_1.json (can be extended to load more files).
    - Settlement/location data is currently a stub (see self.settlements); replace with real data for production use.

    Configuration:
    - Loads tick interval and siege trigger probability from config/config.json if present.
    - Uses defaults if config is missing or incomplete.
    - Location-based siege trigger uses a 10% chance per tick and randomly selects a stub settlement.
    """
    def __init__(self, world_state: 'WorldState', tick_interval_hours: int = 1):
        self.world_state = world_state
        config = self._load_config()
        self.tick_interval = timedelta(hours=config.get('tick_interval_hours', tick_interval_hours))
        self.siege_probability = config.get('siege_probability', 0.2)
        self.last_tick = world_state.current_time
        self.event_queue = []  # List[Dict]
        self.trigger_conditions = self._load_trigger_conditions()
        self.monster_data = self._load_monster_data()
        # --- Settlement/Location Stub ---
        # Replace this with real settlement/location data when available.
        self.settlements = [
            {'name': 'Redvale', 'type': 'village'},
            {'name': 'Stoneford', 'type': 'town'},
            {'name': 'Highspire', 'type': 'city'},
        ]

    def _load_config(self) -> dict:
        config_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            # Support nested config structure
            game_config = config.get('game', {})
            siege_config = config.get('siege', {})
            # Allow top-level or nested
            return {
                'tick_interval_hours': siege_config.get('tick_interval_hours', config.get('tick_interval_hours', 1)),
                'siege_probability': siege_config.get('siege_probability', config.get('siege_probability', 0.2)),
            }
        except Exception:
            return {}

    def _load_trigger_conditions(self) -> list:
        """
        Returns a list of trigger condition callables. Extend this list to add new trigger types.
        """
        return [
            self.time_based_trigger,
            self.location_based_trigger,
            self.world_state_trigger
        ]

    def _load_monster_data(self) -> list:
        """
        Loads monster data from the first monster schema file. Extend to load more or merge files as needed.
        """
        monsters_path = os.path.join(os.path.dirname(__file__), '../../data/schemas/monsters_1.json')
        try:
            with open(monsters_path, 'r') as f:
                return json.load(f)
        except Exception:
            return []

    def process_tick(self):
        """
        Process world-tick event triggers and queue events if conditions are met.
        Called once per world tick from WorldState.
        """
        for trigger in self.trigger_conditions:
            event = trigger()
            if event:
                self.event_queue.append(event)
                self.world_state.add_event(event)
        self._process_event_queue()

    def time_based_trigger(self) -> Optional[Dict]:
        """
        Example trigger: At midnight (hour 0), configurable chance to trigger a siege event.
        Probability is loaded from config or defaults to 0.2.
        """
        if self.world_state.current_time.hour == 0 and random.random() < self.siege_probability:
            return self._generate_siege_event(reason='midnight')
        return None

    def location_based_trigger(self) -> Optional[Dict]:
        """
        Example location-based siege trigger: With a 10% chance each tick, select a random settlement and trigger a siege event.
        Replace the stub with real settlement/location logic when available.
        """
        if self.settlements and random.random() < 0.1:
            settlement = random.choice(self.settlements)
            return self._generate_siege_event(reason='location', settlement=settlement)
        return None

    def world_state_trigger(self) -> Optional[Dict]:
        """
        Placeholder for world-state-based triggers (e.g., low prosperity, high unrest).
        Implement logic as needed for your game world.
        """
        return None

    def _generate_siege_event(self, reason: str, settlement: Optional[Dict] = None) -> Dict:
        """
        Generates a monster siege event. Selects a random monster from loaded data.
        Optionally includes a settlement/location if provided.
        """
        monster = random.choice(self.monster_data) if self.monster_data else {'name': 'Unknown Monster'}
        event = {
            'type': 'monster_siege',
            'monster': monster['name'],
            'monster_id': monster.get('id'),
            'reason': reason,
            'time': self.world_state.current_time,
            'details': {
                'challenge_rating': monster.get('challenge_rating'),
                'environment': monster.get('environment'),
                'traits': monster.get('traits', []),
            },
        }
        if settlement:
            event['settlement'] = settlement
        return event

    def _process_event_queue(self):
        """
        Placeholder for event resolution, notification, or integration with other systems.
        Extend to notify UI, update NPC memory, or trigger API calls.
        """
        # --- NPC Memory Integration Stub ---
        # For each siege event, update NPC memory/affinity as needed.
        # Example:
        # for event in self.event_queue:
        #     if event['type'] == 'monster_siege':
        #         npc_memory_system.record_siege_event(event)
        # --- API Integration Stub ---
        # For each siege event, send data to an external API if needed.
        # Example:
        # for event in self.event_queue:
        #     if event['type'] == 'monster_siege':
        #         api_client.send_siege_event(event)
        pass

class WorldState:
    """Manages the game world's state and events."""
    
    def __init__(self):
        self.events: List[Dict] = []
        self.last_tick_time: Optional[datetime] = None
        self.current_time: datetime = datetime.now()
        self.siege_event_system = WorldTickEventSystem(self)
        
    def process_world_tick(self) -> None:
        """Process a single world tick, updating time and events."""
        if self.last_tick_time is None:
            self.last_tick_time = self.current_time
            
        # Advance time by one tick
        self.current_time += timedelta(hours=1)
        
        # Process events
        self._process_events()
        
        # Update world state
        self._update_world_state()
        
        # Process monster siege triggers
        self.siege_event_system.process_tick()
        
        self.last_tick_time = self.current_time
        
    def _process_events(self) -> None:
        """Process and clean up old events."""
        current_events = []
        for event in self.events:
            if self._should_keep_event(event):
                current_events.append(event)
        self.events = current_events
        
    def _should_keep_event(self, event: Dict) -> bool:
        """Determine if an event should be kept or removed."""
        event_time = event.get('time')
        if not event_time:
            return True
            
        # Remove events older than 24 hours
        return (self.current_time - event_time) < timedelta(hours=24)
        
    def _update_world_state(self) -> None:
        """Update the world state based on current time and events."""
        # Update NPC schedules
        self._update_npc_schedules()
        
        # Update weather and environment
        self._update_environment()
        
        # Update faction relations
        self._update_faction_relations()
        
    def _update_npc_schedules(self) -> None:
        """Update NPC schedules based on time of day."""
        # Implementation for updating NPC schedules
        pass
        
    def _update_environment(self) -> None:
        """Update weather and environmental conditions."""
        # Implementation for updating environment
        pass
        
    def _update_faction_relations(self) -> None:
        """Update relations between factions."""
        # Implementation for updating faction relations
        pass
        
    def add_event(self, event: Dict) -> None:
        """Add a new event to the world state."""
        event['time'] = self.current_time
        self.events.append(event)
        
    def get_current_events(self) -> List[Dict]:
        """Get all current events."""
        return self.events
        
    def cleanup_old_events(self) -> None:
        """Remove events older than 24 hours."""
        self._process_events()

    def simulate_ticks(self, num_ticks: int) -> List[Dict]:
        """
        Simulate a number of world ticks and collect all monster siege events generated.
        Useful for automated testing and debugging of the monster siege event system.
        Returns a list of siege event dicts for all ticks in the simulation, with trigger type info.
        """
        siege_events = []
        for _ in range(num_ticks):
            self.process_world_tick()
            # Collect siege events from this tick
            for event in self.get_current_events():
                if event.get('type') == 'monster_siege':
                    # Add trigger_type for debugging
                    trigger_type = event.get('reason', 'unknown')
                    event_with_trigger = dict(event)
                    event_with_trigger['trigger_type'] = trigger_type
                    siege_events.append(event_with_trigger)
        return siege_events

if __name__ == "__main__":
    # Simple test: simulate 1000 ticks and print siege event summary
    ws = WorldState()
    events = ws.simulate_ticks(1000)
    from collections import Counter
    trigger_counts = Counter(e['trigger_type'] for e in events)
    print(f"Total siege events: {len(events)}")
    for trigger, count in trigger_counts.items():
        print(f"  Trigger: {trigger:10} | Count: {count}")
    if events:
        print("Example event:")
        import pprint
        pprint.pprint(events[0]) 