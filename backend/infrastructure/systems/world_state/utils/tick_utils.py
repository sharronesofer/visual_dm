"""
Tick utilities for world state processing.

This module consolidates utilities for world tick processing, event handling, and state validation.
It provides functions for processing world ticks, validating world state, and handling world events.
"""

from datetime import datetime
import random
from typing import Dict, Any, List, Optional, Union
import logging
import json
import os

from backend.systems.world_state.world_types import WorldState
from backend.systems.region.models import Region
from backend.systems.faction.models import Faction
from backend.systems.npc import NPC

# HACK: WorldEvent system doesn't exist yet - using lazy loading
# TODO: Implement proper WorldEvent system or remove dependency
def get_world_event_class():
    """Lazy loading for WorldEvent to avoid import errors"""
    try:
        from backend.systems.world_event import WorldEvent
        return WorldEvent
    except ImportError:
        # Return a placeholder class for now
        class WorldEventPlaceholder:
            @classmethod
            def query(cls):
                class QueryPlaceholder:
                    def filter_by(self, **kwargs):
                        return self
                    def all(self):
                        return []
                return QueryPlaceholder()
        return WorldEventPlaceholder

WorldEvent = get_world_event_class()

from backend.systems.character.models.relationship import RelationshipType
logger = logging.getLogger(__name__)
from backend.infrastructure.database import db
from backend.infrastructure.utils import ValidationError
# Commented out missing validation module
# from backend.systems.validation.world_event_validation import (
#     validate_event_data,
#     validate_event_timing,
#     validate_event_status,
#     validate_affected_entities
# )

# Constants and configuration
EVENTS_DATA_PATH = os.path.join("data", "world_state", "events")
os.makedirs(EVENTS_DATA_PATH, exist_ok=True)

# World State Validation Functions

def validate_world_state(world_state: WorldState) -> bool:
    """Validate the world state for consistency."""
    try:
        if not world_state.id or not world_state.name:
            logger.error("Invalid world state: Missing required fields")
            return False
        if world_state.current_time > datetime.utcnow():
            logger.error("Invalid world state: Future time detected")
            return False
        for region in world_state.regions:
            if not validate_region_state(region):
                return False
        for faction in world_state.factions:
            if not validate_faction_state(faction):
                return False
        active_events = WorldEvent.query.filter_by(status='active').all()
        for event in active_events:
            try:
                validate_event_data(event.type, event.data)
                validate_event_timing(event.start_time, event.end_time)
                validate_event_status(event.status)
                validate_affected_entities(event.type, event.data, {
                    'factions': [f.id for f in world_state.factions],
                    'regions': [r.id for r in world_state.regions]
                })
            except Exception as e:
                logger.error(f"Invalid event {event.id}: {str(e)}")
                return False
        return True
    except Exception as e:
        logger.error(f"Error validating world state: {str(e)}")
        return False

def validate_region_state(region: Region) -> bool:
    """Validate a region's state for consistency."""
    try:
        if not region.id or not region.name:
            logger.error(f"Invalid region {region.id}: Missing required fields")
            return False
        if region.population < 0:
            logger.error(f"Invalid region {region.id}: Negative population")
            return False
        for resource in region.resources:
            if resource['amount'] < 0:
                logger.error(f"Invalid region {region.id}: Negative resource amount")
                return False
        if region.infrastructure_level < 0 or region.infrastructure_level > 100:
            logger.error(f"Invalid region {region.id}: Infrastructure level out of range")
            return False
        for building in region.buildings:
            if building['condition'] < 0 or building['condition'] > 100:
                logger.error(f"Invalid region {region.id}: Building condition out of range")
                return False
        return True
    except Exception as e:
        logger.error(f"Error validating region state: {str(e)}")
        return False

def validate_faction_state(faction: Faction) -> bool:
    """Validate a faction's state for consistency."""
    try:
        if not faction.id or not faction.name:
            logger.error(f"Invalid faction {faction.id}: Missing required fields")
            return False
        for resource in faction.resources:
            if resource['amount'] < 0:
                logger.error(f"Invalid faction {faction.id}: Negative resource amount")
                return False
        for relationship in faction.relationships:
            if relationship.value < -100 or relationship.value > 100:
                logger.error(f"Invalid faction {faction.id}: Relationship value out of range")
                return False
        if faction.influence < 0 or faction.influence > 100:
            logger.error(f"Invalid faction {faction.id}: Influence out of range")
            return False
        return True
    except Exception as e:
        logger.error(f"Error validating faction state: {str(e)}")
        return False

# World Tick Processing Functions

def process_world_tick(world_state: WorldState) -> None:
    """Process a world tick, updating all world state components."""
    try:
        if not validate_world_state(world_state):
            raise ValueError("Invalid world state")
        
        # Process factions
        for faction in world_state.factions:
            process_faction_activities(faction)
        
        # Process regions
        for region in world_state.regions:
            process_region_changes(region)
        
        # Process events
        process_world_events(world_state)
        
        # Update world state
        world_state.last_tick = datetime.utcnow()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing world tick: {str(e)}")
        raise

def process_npc_actions(npc: NPC):
    """Process actions for a single NPC."""
    # TODO: Implement NPC behavior

def process_faction_activities(faction: Faction):
    """Process activities for a single faction."""
    try:
        resource_changes = faction.update_resources()
        if resource_changes:
            log_faction_event(faction, {
                'type': 'resource_update',
                'changes': resource_changes,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        faction.decay_relations(db.session)
        goal_changes = faction.update_goals()
        
        if goal_changes:
            log_faction_event(faction, {
                'type': 'goal_update',
                'changes': goal_changes,
                'timestamp': datetime.utcnow().isoformat()
            })
            if goal_changes.get('completed') or goal_changes.get('failed'):
                new_goal = faction._generate_new_goal()
                if new_goal:
                    faction.goals['current'].append(new_goal)
        
        process_faction_state(faction)
        check_faction_conflicts(faction)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise

def process_faction_state(faction: Faction):
    """Update faction state based on current conditions."""
    faction.state['statistics'].update({
        'members_count': len(faction.members),
        'territory_count': len(faction.controlled_regions),
        'quest_success_rate': calculate_quest_success_rate(faction)
    })
    
    for war in faction.state['active_wars']:
        process_war_state(faction, war)
    
    for project in faction.state['current_projects']:
        process_project_state(faction, project)
    
    if len(faction.state['recent_events']) > 100:
        faction.state['recent_events'] = faction.state['recent_events'][-100:]

def process_war_state(faction: Faction, war: Dict[str, Any]):
    """Process the state of an ongoing war."""
    try:
        enemy_faction = Faction.query.get(war['faction_id'])
        if not enemy_faction:
            faction.state['active_wars'].remove(war)
            return
        
        if faction._check_peace_conditions(enemy_faction.id):
            faction.state['active_wars'].remove(war)
            faction.trigger_event_relation_change(db.session, enemy_faction.id, 'peace_treaty')
    except Exception as e:
        logger.error(f"Error processing war state: {str(e)}")

def process_project_state(faction: Faction, project: Dict[str, Any]):
    """Process the state of an ongoing project."""
    try:
        if 'completion_time' in project and datetime.fromisoformat(project['completion_time']) <= datetime.utcnow():
            faction.state['current_projects'].remove(project)
            
            if project['type'] == 'construction':
                territory = project.get('territory')
                if territory:
                    faction.territory[territory]['buildings'].append(project['building'])
            elif project['type'] == 'research':
                faction.resources['special_resources'][project['technology']] = project.get('bonus', 1.0)
            
            log_faction_event(faction, {
                'type': 'project_completed',
                'project': project,
                'timestamp': datetime.utcnow().isoformat()
            })
    except Exception as e:
        logger.error(f"Error processing project state: {str(e)}")

def check_faction_conflicts(faction: Faction):
    """Check for potential conflicts with other factions."""
    try:
        other_factions = Faction.query.filter(Faction.id != faction.id).all()
        
        for other in other_factions:
            rel = faction.get_relation(db.session, other.id)
            if not rel:
                continue
            
            shared_borders = get_shared_borders(faction, other)
            if shared_borders and rel.relation_type in [RelationshipType.HOSTILE.value, RelationshipType.WAR.value]:
                if random.random() < 0.2:
                    faction.trigger_event_relation_change(db.session, other.id, 'skirmish')
            
            if rel.relation_type not in [RelationshipType.WAR.value] and faction._check_trade_conditions(other.id):
                if 'trade_partners' not in faction.relationships:
                    faction.relationships['trade_partners'] = []
                
                if other.id not in faction.relationships['trade_partners']:
                    faction.relationships['trade_partners'].append(other.id)
                    faction.trigger_event_relation_change(db.session, other.id, 'trade_agreement')
    except Exception as e:
        logger.error(f"Error checking faction conflicts: {str(e)}")

def get_shared_borders(faction1: Faction, faction2: Faction) -> List[str]:
    """Get list of regions where two factions share borders."""
    try:
        faction1_regions = set(region.id for region in faction1.controlled_regions)
        faction2_regions = set(region.id for region in faction2.controlled_regions)
        shared_borders = []
        
        for region1_id in faction1_regions:
            region1 = Region.query.get(region1_id)
            if not region1:
                continue
            
            for neighbor_id in region1.neighbors:
                if neighbor_id in faction2_regions:
                    shared_borders.append(f"{region1_id}-{neighbor_id}")
        
        return shared_borders
    except Exception as e:
        logger.error(f"Error getting shared borders: {str(e)}")
        return []

def calculate_quest_success_rate(faction: Faction) -> float:
    """Calculate the faction's quest success rate."""
    try:
        completed_quests = [q for q in faction.quests if q.status == 'completed']
        failed_quests = [q for q in faction.quests if q.status == 'failed']
        total_quests = len(completed_quests) + len(failed_quests)
        
        if total_quests == 0:
            return 0.0
        
        return len(completed_quests) / total_quests * 100
    except Exception as e:
        logger.error(f"Error calculating quest success rate: {str(e)}")
        return 0.0

def log_faction_event(faction: Faction, event: Dict[str, Any]):
    """Log an event in the faction's recent events."""
    try:
        if 'recent_events' not in faction.state:
            faction.state['recent_events'] = []
        
        faction.state['recent_events'].append(event)
    except Exception as e:
        logger.error(f"Error logging faction event: {str(e)}")

def process_region_changes(region: Region):
    """Process changes for a single region."""
    try:
        # Process population dynamics
        process_population_changes(region)
        # Process resource generation and consumption
        process_resource_changes(region)
        # Process building construction and decay
        process_building_changes(region)
        # Process region-specific events
        process_region_events(region)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing region changes: {str(e)}")
        raise

def process_population_changes(region: Region):
    """Process population changes for a region"""
    try:
        # Calculate natural population growth/decline
        current_population = getattr(region, 'population', 0)
        base_growth_rate = 0.02  # 2% annual growth base rate
        
        # Environmental modifiers
        climate_modifier = _get_climate_population_modifier(region)
        resource_modifier = _get_resource_population_modifier(region)
        
        # Calculate effective growth rate
        effective_growth_rate = base_growth_rate * climate_modifier * resource_modifier
        
        # Apply population change
        population_change = int(current_population * effective_growth_rate / 365)  # Daily change
        new_population = max(0, current_population + population_change)
        
        # Update region population
        if hasattr(region, 'population'):
            region.population = new_population
        
        logger.debug(f"Region {region.id} population: {current_population} -> {new_population}")
        
    except Exception as e:
        logger.error(f"Error processing population changes for region {region.id}: {str(e)}")

def process_resource_changes(region: Region):
    """Process resource generation and consumption for a region"""
    try:
        # Get current resources
        resources = getattr(region, 'resources', {})
        if not isinstance(resources, dict):
            resources = {}
        
        # Process each resource type
        for resource_type in ['food', 'materials', 'gold', 'magical_energy']:
            current_amount = resources.get(resource_type, 0)
            
            # Calculate generation rates
            generation_rate = _calculate_resource_generation_rate(region, resource_type)
            consumption_rate = _calculate_resource_consumption_rate(region, resource_type)
            
            # Apply daily change
            net_change = generation_rate - consumption_rate
            new_amount = max(0, current_amount + net_change)
            
            resources[resource_type] = new_amount
        
        # Update region resources
        if hasattr(region, 'resources'):
            region.resources = resources
        
        logger.debug(f"Region {region.id} resources updated: {resources}")
        
    except Exception as e:
        logger.error(f"Error processing resource changes for region {region.id}: {str(e)}")

def process_building_changes(region: Region):
    """Process building construction, upgrades, and decay for a region"""
    try:
        # Get current buildings
        buildings = getattr(region, 'buildings', [])
        if not isinstance(buildings, list):
            buildings = []
        
        # Process each building
        for building in buildings:
            # Process construction completion
            if building.get('status') == 'under_construction':
                _process_building_construction(building)
            
            # Process building decay
            if building.get('status') == 'active':
                _process_building_decay(building)
            
            # Process building upgrades
            if building.get('upgrade_in_progress'):
                _process_building_upgrade(building)
        
        # Check for new building construction
        _check_new_building_construction(region, buildings)
        
        # Update region buildings
        if hasattr(region, 'buildings'):
            region.buildings = buildings
        
        logger.debug(f"Region {region.id} processed {len(buildings)} buildings")
        
    except Exception as e:
        logger.error(f"Error processing building changes for region {region.id}: {str(e)}")

def process_region_events(region: Region):
    """Process region-specific events and their effects"""
    try:
        # Get active events for this region
        region_events = getattr(region, 'active_events', [])
        if not isinstance(region_events, list):
            region_events = []
        
        # Process each active event
        events_to_remove = []
        for event in region_events:
            # Check if event has expired
            if _is_event_expired(event):
                _apply_event_completion_effects(region, event)
                events_to_remove.append(event)
            else:
                # Apply ongoing event effects
                _apply_ongoing_event_effects(region, event)
        
        # Remove completed events
        for event in events_to_remove:
            region_events.remove(event)
        
        # Check for new random events
        if _should_generate_random_event(region):
            new_event = _generate_random_region_event(region)
            if new_event:
                region_events.append(new_event)
        
        # Update region events
        if hasattr(region, 'active_events'):
            region.active_events = region_events
        
        logger.debug(f"Region {region.id} processed {len(region_events)} events")
        
    except Exception as e:
        logger.error(f"Error processing region events for region {region.id}: {str(e)}")

# Helper functions for population processing
def _get_climate_population_modifier(region: Region) -> float:
    """Get population growth modifier based on climate"""
    climate = getattr(region, 'climate', 'temperate')
    modifiers = {
        'tropical': 1.2,
        'temperate': 1.0,
        'arid': 0.8,
        'arctic': 0.6,
        'magical': 1.1
    }
    return modifiers.get(climate, 1.0)

def _get_resource_population_modifier(region: Region) -> float:
    """Get population growth modifier based on resource availability"""
    resources = getattr(region, 'resources', {})
    food_availability = resources.get('food', 0)
    population = getattr(region, 'population', 1)
    
    # Calculate food per capita
    food_per_capita = food_availability / max(population, 1)
    
    # Return modifier based on food availability
    if food_per_capita >= 2.0:
        return 1.3  # Abundant food
    elif food_per_capita >= 1.0:
        return 1.0  # Adequate food
    elif food_per_capita >= 0.5:
        return 0.7  # Scarce food
    else:
        return 0.4  # Famine conditions

# Helper functions for resource processing
def _calculate_resource_generation_rate(region: Region, resource_type: str) -> float:
    """Calculate daily resource generation rate"""
    population = getattr(region, 'population', 0)
    buildings = getattr(region, 'buildings', [])
    
    base_rates = {
        'food': population * 0.1,  # Population generates some food
        'materials': 0,
        'gold': 0,
        'magical_energy': 0
    }
    
    # Add building-based generation
    for building in buildings:
        if building.get('type') == 'farm' and resource_type == 'food':
            base_rates[resource_type] += building.get('efficiency', 1.0) * 10
        elif building.get('type') == 'mine' and resource_type == 'materials':
            base_rates[resource_type] += building.get('efficiency', 1.0) * 5
        elif building.get('type') == 'market' and resource_type == 'gold':
            base_rates[resource_type] += building.get('efficiency', 1.0) * 3
    
    return base_rates.get(resource_type, 0)

def _calculate_resource_consumption_rate(region: Region, resource_type: str) -> float:
    """Calculate daily resource consumption rate"""
    population = getattr(region, 'population', 0)
    
    consumption_rates = {
        'food': population * 0.08,  # Population consumes food
        'materials': population * 0.02,  # Some materials for maintenance
        'gold': population * 0.01,  # Some gold for services
        'magical_energy': 0  # Special consumption rules
    }
    
    return consumption_rates.get(resource_type, 0)

# Helper functions for building processing
def _process_building_construction(building: dict):
    """Process building construction progress"""
    construction_progress = building.get('construction_progress', 0)
    construction_rate = building.get('construction_rate', 1.0)
    
    # Advance construction
    construction_progress += construction_rate
    building['construction_progress'] = construction_progress
    
    # Check if construction is complete
    if construction_progress >= 100:
        building['status'] = 'active'
        building['construction_progress'] = 100

def _process_building_decay(building: dict):
    """Process building decay over time"""
    condition = building.get('condition', 100)
    decay_rate = building.get('decay_rate', 0.1)
    
    # Apply decay
    condition = max(0, condition - decay_rate)
    building['condition'] = condition
    
    # Check if building is too damaged
    if condition <= 10:
        building['status'] = 'ruins'

def _process_building_upgrade(building: dict):
    """Process building upgrade progress"""
    upgrade_progress = building.get('upgrade_progress', 0)
    upgrade_rate = building.get('upgrade_rate', 0.5)
    
    # Advance upgrade
    upgrade_progress += upgrade_rate
    building['upgrade_progress'] = upgrade_progress
    
    # Check if upgrade is complete
    if upgrade_progress >= 100:
        building['level'] = building.get('level', 1) + 1
        building['upgrade_in_progress'] = False
        building['upgrade_progress'] = 0

def _check_new_building_construction(region: Region, buildings: list):
    """Check if new buildings should start construction"""
    population = getattr(region, 'population', 0)
    resources = getattr(region, 'resources', {})
    
    # Simple logic: if population is growing and resources are available, build
    if population > len(buildings) * 50 and resources.get('materials', 0) > 100:
        new_building = {
            'type': 'house',
            'status': 'under_construction',
            'construction_progress': 0,
            'construction_rate': 2.0,
            'condition': 100,
            'level': 1
        }
        buildings.append(new_building)

# Helper functions for event processing
def _is_event_expired(event: dict) -> bool:
    """Check if an event has expired"""
    from datetime import datetime, timedelta
    
    start_time = event.get('start_time')
    duration = event.get('duration_days', 1)
    
    if not start_time:
        return True
    
    # Convert string to datetime if needed
    if isinstance(start_time, str):
        start_time = datetime.fromisoformat(start_time)
    
    expiry_time = start_time + timedelta(days=duration)
    return datetime.utcnow() > expiry_time

def _apply_event_completion_effects(region: Region, event: dict):
    """Apply effects when an event completes"""
    event_type = event.get('type', 'unknown')
    
    if event_type == 'harvest_festival':
        # Increase food production temporarily
        resources = getattr(region, 'resources', {})
        resources['food'] = resources.get('food', 0) + 50
        if hasattr(region, 'resources'):
            region.resources = resources
    
    elif event_type == 'trade_caravan':
        # Increase gold and materials
        resources = getattr(region, 'resources', {})
        resources['gold'] = resources.get('gold', 0) + 30
        resources['materials'] = resources.get('materials', 0) + 20
        if hasattr(region, 'resources'):
            region.resources = resources

def _apply_ongoing_event_effects(region: Region, event: dict):
    """Apply ongoing effects while an event is active"""
    event_type = event.get('type', 'unknown')
    
    if event_type == 'drought':
        # Reduce food production
        resources = getattr(region, 'resources', {})
        food_reduction = min(resources.get('food', 0), 5)
        resources['food'] = resources.get('food', 0) - food_reduction
        if hasattr(region, 'resources'):
            region.resources = resources

def _should_generate_random_event(region: Region) -> bool:
    """Determine if a random event should be generated"""
    import random
    # 1% chance per day of a random event
    return random.random() < 0.01

def _generate_random_region_event(region: Region) -> dict:
    """Generate a random event for the region"""
    import random
    from datetime import datetime
    
    event_types = [
        {'type': 'harvest_festival', 'duration_days': 3},
        {'type': 'trade_caravan', 'duration_days': 1},
        {'type': 'drought', 'duration_days': 7},
        {'type': 'celebration', 'duration_days': 2}
    ]
    
    selected_event = random.choice(event_types)
    selected_event['start_time'] = datetime.utcnow()
    selected_event['id'] = f"{region.id}_{datetime.utcnow().timestamp()}"
    
    return selected_event

# World Event Handling Functions

def process_world_events(world_state):
    """Process all world events for the current tick."""
    try:
        active_events = WorldEvent.query.filter_by(status='active').all()
        for event in active_events:
            handle_event_effects(event)
            if event.is_complete():
                handle_event_completion(event)
    except Exception as e:
        logger.error(f"Error processing world events: {str(e)}")

def handle_event_completion(event: WorldEvent) -> None:
    """Handle completion of a world event."""
    try:
        if event.type == 'war':
            handle_war_completion(event)
        elif event.type == 'trade':
            handle_trade_completion(event)
        elif event.type == 'diplomatic':
            handle_diplomatic_completion(event)
        elif event.type == 'festival':
            handle_festival_completion(event)
        elif event.type == 'calamity':
            handle_calamity_completion(event)
        elif event.type == 'discovery':
            handle_discovery_completion(event)
        elif event.type == 'religious':
            handle_religious_completion(event)
        else:
            logger.warning(f"Unknown event type for completion: {event.type}")
    except Exception as e:
        logger.error(f"Error handling event completion: {str(e)}")

def handle_event_effects(event: WorldEvent) -> None:
    """Apply effects of a world event."""
    try:
        if event.type == 'war':
            handle_war_effects(event)
        elif event.type == 'trade':
            handle_trade_effects(event)
        elif event.type == 'diplomatic':
            handle_diplomatic_effects(event)
        elif event.type == 'festival':
            handle_festival_effects(event)
        elif event.type == 'calamity':
            handle_calamity_effects(event)
        elif event.type == 'discovery':
            handle_discovery_effects(event)
        elif event.type == 'religious':
            handle_religious_effects(event)
        else:
            logger.warning(f"Unknown event type for effects: {event.type}")
    except Exception as e:
        logger.error(f"Error handling event effects: {str(e)}")

def handle_war_effects(event: WorldEvent) -> None:
    """Apply effects of a war event."""
    # Implementation to be added

def handle_trade_effects(event: WorldEvent) -> None:
    """Apply effects of a trade event."""
    # Implementation to be added

def handle_diplomatic_effects(event: WorldEvent) -> None:
    """Apply effects of a diplomatic event."""
    # Implementation to be added

def handle_festival_effects(event: WorldEvent) -> None:
    """Apply effects of a festival event."""
    # Implementation to be added

def handle_calamity_effects(event: WorldEvent) -> None:
    """Apply effects of a calamity event."""
    # Implementation to be added

def handle_discovery_effects(event: WorldEvent) -> None:
    """Apply effects of a discovery event."""
    # Implementation to be added

def handle_religious_effects(event: WorldEvent) -> None:
    """Apply effects of a religious event."""
    # Implementation to be added

def handle_war_completion(event: WorldEvent) -> None:
    """Handle completion of a war event."""
    # Implementation to be added

def handle_trade_completion(event: WorldEvent) -> None:
    """Handle completion of a trade event."""
    # Implementation to be added

def handle_diplomatic_completion(event: WorldEvent) -> None:
    """Handle completion of a diplomatic event."""
    # Implementation to be added

def handle_festival_completion(event: WorldEvent) -> None:
    """Handle completion of a festival event."""
    # Implementation to be added

def handle_calamity_completion(event: WorldEvent) -> None:
    """Handle completion of a calamity event."""
    # Implementation to be added

def handle_discovery_completion(event: WorldEvent) -> None:
    """Handle completion of a discovery event."""
    # Implementation to be added

def handle_religious_completion(event: WorldEvent) -> None:
    """Handle completion of a religious event."""
    # Implementation to be added

# Random Event Generation

def generate_random_event(world_state: WorldState) -> Optional[WorldEvent]:
    """Generate a random world event based on current state."""
    event_types = ['trade', 'diplomatic', 'festival', 'calamity', 'discovery', 'religious']
    weights = calculate_event_weights(world_state)
    
    if random.random() > 0.1:  # 10% chance of random event
        return None
    
    event_type = random.choices(event_types, weights=weights, k=1)[0]
    event_data = generate_event_data(event_type, world_state)
    
    new_event = WorldEvent(
        type=event_type,
        status='active',
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + calculate_event_duration(event_type),
        data=event_data
    )
    
    db.session.add(new_event)
    db.session.commit()
    
    logger.info(f"Generated random event: {event_type}")
    return new_event

def calculate_event_weights(world_state: WorldState) -> List[float]:
    """Calculate weights for different event types based on world state."""
    # Default weights
    weights = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    
    # Adjust based on world state
    # For example, increase calamity chance if resources are strained
    total_population = sum(r.population for r in world_state.regions)
    total_resources = sum(sum(res['amount'] for res in r.resources) for r in world_state.regions)
    
    if total_population > total_resources:
        weights[3] *= 1.5  # Increase calamity weight
    
    # More diplomatic events if factions have close relationships
    if any(f.has_strong_relationships() for f in world_state.factions):
        weights[1] *= 1.3  # Increase diplomatic weight
    
    return weights

def generate_event_data(event_type: str, world_state: WorldState) -> Dict[str, Any]:
    """Generate appropriate data for an event type."""
    if event_type == 'trade':
        return generate_trade_event_data(world_state)
    elif event_type == 'diplomatic':
        return generate_diplomatic_event_data(world_state)
    # Add other event type generators as needed
    
    # Default simple data
    return {
        'description': f"A {event_type} event has occurred",
        'severity': random.randint(1, 5),
        'affected_regions': [r.id for r in random.sample(world_state.regions, min(2, len(world_state.regions)))]
    }

def generate_trade_event_data(world_state: WorldState) -> Dict[str, Any]:
    """Generate data for a trade event."""
    # Implementation to be added
    return {
        'description': "A trade caravan arrives",
        'resources': {'gold': random.randint(100, 500)},
        'duration': random.randint(3, 7)
    }

def generate_diplomatic_event_data(world_state: WorldState) -> Dict[str, Any]:
    """Generate data for a diplomatic event."""
    # Implementation to be added
    return {
        'description': "Diplomatic envoys arrive",
        'faction_id': random.choice([f.id for f in world_state.factions]),
        'attitude': random.choice(['friendly', 'neutral', 'hostile'])
    }

def calculate_event_duration(event_type: str) -> Any:
    """Calculate appropriate duration for an event type."""
    from datetime import timedelta
    
    if event_type == 'war':
        return timedelta(days=random.randint(10, 30))
    elif event_type == 'trade':
        return timedelta(days=random.randint(3, 7))
    elif event_type == 'diplomatic':
        return timedelta(days=random.randint(1, 5))
    elif event_type == 'festival':
        return timedelta(days=random.randint(1, 3))
    elif event_type == 'calamity':
        return timedelta(days=random.randint(5, 15))
    elif event_type == 'discovery':
        return timedelta(days=random.randint(1, 10))
    elif event_type == 'religious':
        return timedelta(days=random.randint(2, 7))
    else:
        return timedelta(days=random.randint(1, 7))

# Placeholder validation functions
def validate_event_data(event_type: str, data: dict) -> bool:
    """Placeholder validation function."""
    return True

def validate_event_timing(start_time, end_time) -> bool:
    """Placeholder validation function."""
    return True

def validate_event_status(status: str) -> bool:
    """Placeholder validation function."""
    return status in ['active', 'completed', 'cancelled']

def validate_affected_entities(event_type: str, data: dict, entities: dict) -> bool:
    """Placeholder validation function."""
    return True 