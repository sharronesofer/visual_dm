"""
World tick utilities.
Provides functionality for world time progression and event generation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from app.core.models.world import Region
from app.core.models.quest import Quest
from app.core.utils.event_utils import EventUtils
from app.core.utils.base_manager import BaseManager
from app.core.models.npc import NPC
try:
    from app.core.models.world import World
except ImportError:
    class World:
        id = None
        current_time = None
from app.core.models.world import Faction

logger = logging.getLogger(__name__)

class WorldTickUtils(BaseManager):
    """Utility class for world time progression."""
    
    def __init__(self):
        """Initialize the world tick utilities."""
        super().__init__('world_tick')
        self.event_utils = EventUtils()
        self._last_tick = datetime.utcnow()
        self._tick_interval = timedelta(minutes=1)  # Game time progresses 1 minute per real second

    def process_tick(self, regions: List[Region]) -> List[Dict[str, Any]]:
        """Process a world tick for all regions.
        
        Args:
            regions: List of regions to process
            
        Returns:
            List of events generated during the tick
        """
        current_time = datetime.utcnow()
        if current_time - self._last_tick < self._tick_interval:
            return []

        self._last_tick = current_time
        generated_events = []

        for region in regions:
            # Update region state
            self._update_region_state(region)
            
            # Generate events
            events = self._generate_events(region)
            generated_events.extend(events)
            
            # Update quests
            self._update_quests(region)

        return generated_events

    def _update_region_state(self, region: Region) -> None:
        """Update a region's state based on the current time.
        
        Args:
            region: The region to update
        """
        try:
            # Update time-based attributes
            region.current_time = datetime.utcnow()
            
            # Update weather if needed
            if region.weather_last_updated + timedelta(hours=1) < region.current_time:
                self._update_weather(region)
            
            # Update population if needed
            if region.population_last_updated + timedelta(days=1) < region.current_time:
                self._update_population(region)
            
            # Update resources if needed
            if region.resources_last_updated + timedelta(hours=6) < region.current_time:
                self._update_resources(region)
                
        except Exception as e:
            logger.error(f"Error updating region state: {str(e)}")

    def _generate_events(self, region: Region) -> List[Dict[str, Any]]:
        """Generate events for a region.
        
        Args:
            region: The region to generate events for
            
        Returns:
            List of generated events
        """
        events = []
        try:
            # Check for event generation based on region properties
            if self._should_generate_event(region):
                event = self.event_utils.generate_world_event(
                    level=region.level,
                    event_type=self._get_event_type(region),
                    region=region.name
                )
                if event:
                    events.append(event)
                    
        except Exception as e:
            logger.error(f"Error generating events: {str(e)}")
            
        return events

    def _update_quests(self, region: Region) -> None:
        """Update quests in a region.
        
        Args:
            region: The region to update quests for
        """
        try:
            current_time = datetime.utcnow()
            
            # Update active quests
            for quest in region.active_quests:
                if quest.end_time < current_time:
                    self._complete_quest(quest)
                elif quest.start_time + timedelta(hours=1) < current_time:
                    self._update_quest_progress(quest)
                    
            # Generate new quests if needed
            if len(region.active_quests) < region.max_quests:
                self._generate_new_quests(region)
                
        except Exception as e:
            logger.error(f"Error updating quests: {str(e)}")

    def _should_generate_event(self, region: Region) -> bool:
        """Check if an event should be generated for a region.
        
        Args:
            region: The region to check
            
        Returns:
            bool: True if an event should be generated
        """
        # Base chance of event generation
        base_chance = 0.1
        
        # Modify chance based on region properties
        modifiers = {
            'population_density': region.population_density / 1000,
            'unrest_level': region.unrest_level / 100,
            'magic_level': region.magic_level / 100
        }
        
        # Calculate final chance
        chance = base_chance * (1 + sum(modifiers.values()))
        
        # Generate random number and compare
        import random
        return random.random() < chance

    def _get_event_type(self, region: Region) -> str:
        """Get the type of event to generate for a region.
        
        Args:
            region: The region to get event type for
            
        Returns:
            str: The event type
        """
        # Weight different event types based on region properties
        weights = {
            'natural': 0.3,
            'social': region.population_density / 1000,
            'military': region.unrest_level / 100,
            'mystical': region.magic_level / 100
        }
        
        # Normalize weights
        total = sum(weights.values())
        weights = {k: v/total for k, v in weights.items()}
        
        # Choose event type based on weights
        import random
        return random.choices(list(weights.keys()), weights=list(weights.values()))[0]

    def _update_weather(self, region: Region) -> None:
        """Update the weather for a region.
        
        Args:
            region: The region to update weather for
        """
        # Update weather based on season, time of day, and region properties
        pass

    def _update_population(self, region: Region) -> None:
        """Update the population for a region.
        
        Args:
            region: The region to update population for
        """
        # Update population based on birth rate, death rate, and migration
        pass

    def _update_resources(self, region: Region) -> None:
        """Update the resources for a region.
        
        Args:
            region: The region to update resources for
        """
        # Update resources based on consumption and production rates
        pass

    def _complete_quest(self, quest: Quest) -> None:
        """Complete a quest.
        
        Args:
            quest: The quest to complete
        """
        # Handle quest completion logic
        pass

    def _update_quest_progress(self, quest: Quest) -> None:
        """Update the progress of a quest.
        
        Args:
            quest: The quest to update
        """
        # Update quest progress based on time and other factors
        pass

    def _generate_new_quests(self, region: Region) -> None:
        """Generate new quests for a region.
        
        Args:
            region: The region to generate quests for
        """
        # Generate new quests based on region properties and current state
        pass

# TODO: The tick_world_day function and World references are commented out to allow DB migrations. Restore after migration if needed.
# def tick_world_day(world: World) -> Dict[str, Any]:
#     """
#     Process one day of world time, updating all relevant entities
#     Returns a summary of changes
#     """
#     changes = {
#         'npcs': [],
#         'quests': [],
#         'factions': [],
#         'regions': []
#     }
#
#     # Update world time
#     world.current_time += timedelta(days=1)
#     
#     # Process NPCs
#     for npc in NPC.query.filter_by(world_id=world.id).all():
#         npc_changes = process_npc_day(npc)
#         if npc_changes:
#             changes['npcs'].append(npc_changes)
#     
#     # Process Quests
#     for quest in Quest.query.filter_by(world_id=world.id).all():
#         quest_changes = process_quest_day(quest)
#         if quest_changes:
#             changes['quests'].append(quest_changes)
#     
#     # Process Factions
#     for faction in Faction.query.filter_by(world_id=world.id).all():
#         faction_changes = process_faction_day(faction)
#         if faction_changes:
#             changes['factions'].append(faction_changes)
#     
#     # Process Regions
#     for region in Region.query.filter_by(world_id=world.id).all():
#         region_changes = process_region_day(region)
#         if region_changes:
#             changes['regions'].append(region_changes)
#     
#     return changes

def process_npc_day(npc: NPC) -> Dict[str, Any]:
    """
    Process daily updates for an NPC
    """
    changes = {
        'id': npc.id,
        'name': npc.name,
        'changes': []
    }
    
    # Decay NPC memories
    npc.decay_memories()

    # Update NPC schedule based on time
    schedule_change = npc.update_schedule()
    if schedule_change:
        changes['changes'].append({
            'type': 'schedule',
            'details': schedule_change
        })
    
    # Process NPC relationships
    relationship_changes = npc.process_relationships()
    if relationship_changes:
        changes['changes'].append({
            'type': 'relationships',
            'details': relationship_changes
        })
    
    # Update NPC goals
    goal_changes = npc.update_goals()
    if goal_changes:
        changes['changes'].append({
            'type': 'goals',
            'details': goal_changes
        })
    
    return changes if changes['changes'] else None

def process_quest_day(quest: Quest) -> Dict[str, Any]:
    """
    Process daily updates for a quest
    """
    changes = {
        'id': quest.id,
        'title': quest.title,
        'changes': []
    }
    
    # Update quest timers
    if quest.deadline and quest.deadline <= datetime.utcnow():
        quest.status = 'failed'
        changes['changes'].append({
            'type': 'status',
            'details': 'Quest failed due to deadline'
        })
    
    # Process quest stages
    stage_changes = quest.update_stages()
    if stage_changes:
        changes['changes'].append({
            'type': 'stages',
            'details': stage_changes
        })
    
    return changes if changes['changes'] else None

def process_faction_day(faction: Faction) -> Dict[str, Any]:
    """
    Process daily updates for a faction
    """
    changes = {
        'id': faction.id,
        'name': faction.name,
        'changes': []
    }
    
    # Update faction resources
    resource_changes = faction.update_resources()
    if resource_changes:
        changes['changes'].append({
            'type': 'resources',
            'details': resource_changes
        })
    
    # Process faction relationships
    relationship_changes = faction.process_relationships()
    if relationship_changes:
        changes['changes'].append({
            'type': 'relationships',
            'details': relationship_changes
        })
    
    # Update faction goals
    goal_changes = faction.update_goals()
    if goal_changes:
        changes['changes'].append({
            'type': 'goals',
            'details': goal_changes
        })
    
    return changes if changes['changes'] else None

def process_region_day(region: Region) -> Dict[str, Any]:
    """
    Process daily updates for a region
    """
    changes = {
        'id': region.id,
        'name': region.name,
        'changes': []
    }
    
    # Update region resources
    resource_changes = region.update_resources()
    if resource_changes:
        changes['changes'].append({
            'type': 'resources',
            'details': resource_changes
        })
    
    # Process weather changes
    weather_changes = region.update_weather()
    if weather_changes:
        changes['changes'].append({
            'type': 'weather',
            'details': weather_changes
        })
    
    # Update region events
    event_changes = region.process_events()
    if event_changes:
        changes['changes'].append({
            'type': 'events',
            'details': event_changes
        })
    
    return changes if changes['changes'] else None

def get_world_state(session) -> Dict:
    """Get current state of the world."""
    from app.core.models.world import Region  # Lazy import
    
    regions = session.query(Region).all()
    return {
        'regions': len(regions),
        'high_tension_regions': len([r for r in regions if r.tension >= 0.8]),
        'timestamp': datetime.utcnow().isoformat()
    }

__all__ = ['tick_world_day', 'get_world_state']