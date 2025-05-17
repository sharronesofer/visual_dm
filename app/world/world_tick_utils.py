"""
World tick utilities for processing world state changes.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import DatabaseError
from app.core.database import db
from app.core.models.character import Character
from app.core.models.user import User
from app.core.models.party import Party
from app.core.models.world import Region, Faction
from app.core.models.quest import Quest
from app.core.models.spell import Spell
from app.core.models.inventory import InventoryItem
from app.core.models.combat import CombatStats
from app.core.models.save import SaveGame
from app.core.models.world_state import WorldState
from app.core.models.world_event import WorldEvent
from app.core.models.npc import NPC
from app.core.models.point_of_interest import PointOfInterest
from app.core.utils.error_utils import ValidationError, NotFoundError
from datetime import datetime, timedelta
import random
from app.core.enums import RelationshipType
from app.core.logging import logger
from app.validation.world_event_validation import (
    validate_event_data,
    validate_event_timing,
    validate_event_status,
    validate_affected_entities
)

def validate_world_state(world_state: WorldState) -> bool:
    """Validate the world state for consistency.
    
    Args:
        world_state: The world state to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Check basic world state properties
        if not world_state.id or not world_state.name:
            logger.error("Invalid world state: Missing required fields")
            return False
            
        # Validate time progression
        if world_state.current_time > datetime.utcnow():
            logger.error("Invalid world state: Future time detected")
            return False
            
        # Validate regions
        for region in world_state.regions:
            if not validate_region_state(region):
                return False
                
        # Validate factions
        for faction in world_state.factions:
            if not validate_faction_state(faction):
                return False
                
        # Validate active events
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
    """Validate a region's state for consistency.
    
    Args:
        region: The region to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Check basic region properties
        if not region.id or not region.name:
            logger.error(f"Invalid region {region.id}: Missing required fields")
            return False
            
        # Validate population
        if region.population < 0:
            logger.error(f"Invalid region {region.id}: Negative population")
            return False
            
        # Validate resources
        for resource in region.resources:
            if resource['amount'] < 0:
                logger.error(f"Invalid region {region.id}: Negative resource amount")
                return False
                
        # Validate infrastructure
        if region.infrastructure_level < 0 or region.infrastructure_level > 100:
            logger.error(f"Invalid region {region.id}: Infrastructure level out of range")
            return False
            
        # Validate buildings
        for building in region.buildings:
            if building['condition'] < 0 or building['condition'] > 100:
                logger.error(f"Invalid region {region.id}: Building condition out of range")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error validating region state: {str(e)}")
        return False

def validate_faction_state(faction: Faction) -> bool:
    """Validate a faction's state for consistency.
    
    Args:
        faction: The faction to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Check basic faction properties
        if not faction.id or not faction.name:
            logger.error(f"Invalid faction {faction.id}: Missing required fields")
            return False
            
        # Validate resources
        for resource in faction.resources:
            if resource['amount'] < 0:
                logger.error(f"Invalid faction {faction.id}: Negative resource amount")
                return False
                
        # Validate relationships
        for relationship in faction.relationships:
            if relationship.value < -100 or relationship.value > 100:
                logger.error(f"Invalid faction {faction.id}: Relationship value out of range")
                return False
                
        # Validate influence
        if faction.influence < 0 or faction.influence > 100:
            logger.error(f"Invalid faction {faction.id}: Influence out of range")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating faction state: {str(e)}")
        return False

def process_world_tick(world_state: WorldState) -> None:
    """Process a world tick, updating all world state components.
    
    Args:
        world_state: The world state to update
    """
    try:
        # Validate world state before processing
        if not validate_world_state(world_state):
            raise ValueError("Invalid world state")
            
        # Process faction activities
        for faction in world_state.factions:
            process_faction_activities(faction)
            
        # Process region changes
        for region in world_state.regions:
            process_region_changes(region)
            
        # Generate and process events
        event = generate_random_event(world_state)
        if event:
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
    pass

def process_faction_activities(faction: Faction):
    """Process activities for a single faction."""
    try:
        # Update resources based on income and expenses
        resource_changes = faction.update_resources()
        if resource_changes:
            log_faction_event(faction, {
                'type': 'resource_update',
                'changes': resource_changes,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Process relationships and apply decay
        faction.decay_relations(db.session)
        
        # Update goals and check completion/failure
        goal_changes = faction.update_goals()
        if goal_changes:
            log_faction_event(faction, {
                'type': 'goal_update',
                'changes': goal_changes,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Generate new goals if needed
            if goal_changes.get('completed') or goal_changes.get('failed'):
                new_goal = faction._generate_new_goal()
                if new_goal:
                    faction.goals['current'].append(new_goal)
        
        # Process faction state
        process_faction_state(faction)
        
        # Check for potential conflicts
        check_faction_conflicts(faction)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to process faction activities: {str(e)}")

def process_faction_state(faction: Faction):
    """Update faction state based on current conditions."""
    # Update statistics
    faction.state['statistics'].update({
        'members_count': len(faction.members),
        'territory_count': len(faction.controlled_regions),
        'quest_success_rate': calculate_quest_success_rate(faction)
    })
    
    # Process active wars
    for war in faction.state['active_wars']:
        process_war_state(faction, war)
    
    # Process ongoing projects
    for project in faction.state['current_projects']:
        process_project_state(faction, project)
    
    # Trim recent events list to keep only last 100 events
    if len(faction.state['recent_events']) > 100:
        faction.state['recent_events'] = faction.state['recent_events'][-100:]

def process_war_state(faction: Faction, war: Dict[str, Any]):
    """Process the state of an ongoing war."""
    try:
        enemy_faction = Faction.query.get(war['faction_id'])
        if not enemy_faction:
            faction.state['active_wars'].remove(war)
            return
            
        # Check for peace conditions
        if faction._check_peace_conditions(enemy_faction.id):
            faction.state['active_wars'].remove(war)
            faction.trigger_event_relation_change(db.session, enemy_faction.id, 'peace_treaty')
            
    except Exception as e:
        print(f"Error processing war state: {str(e)}")

def process_project_state(faction: Faction, project: Dict[str, Any]):
    """Process the state of an ongoing project."""
    try:
        if 'completion_time' in project and datetime.fromisoformat(project['completion_time']) <= datetime.utcnow():
            # Complete the project
            faction.state['current_projects'].remove(project)
            
            # Apply project effects
            if project['type'] == 'construction':
                # Add building to territory
                territory = project.get('territory')
                if territory:
                    faction.territory[territory]['buildings'].append(project['building'])
                    
            elif project['type'] == 'research':
                # Add technology or bonus
                faction.resources['special_resources'][project['technology']] = project.get('bonus', 1.0)
                
            # Log completion
            log_faction_event(faction, {
                'type': 'project_completed',
                'project': project,
                'timestamp': datetime.utcnow().isoformat()
            })
            
    except Exception as e:
        print(f"Error processing project state: {str(e)}")

def check_faction_conflicts(faction: Faction):
    """Check for potential conflicts with other factions."""
    try:
        other_factions = Faction.query.filter(Faction.id != faction.id).all()
        for other in other_factions:
            rel = faction.get_relation(db.session, other.id)
            if not rel:
                continue
                
            # Check for territory conflicts
            shared_borders = get_shared_borders(faction, other)
            if shared_borders and rel.relation_type in [RelationshipType.HOSTILE.value, RelationshipType.WAR.value]:
                # Chance of border skirmish
                if random.random() < 0.2:  # 20% chance
                    faction.trigger_event_relation_change(db.session, other.id, 'skirmish')
                    
            # Check for trade opportunities
            if rel.relation_type not in [RelationshipType.WAR.value] and faction._check_trade_conditions(other.id):
                if 'trade_partners' not in faction.relationships:
                    faction.relationships['trade_partners'] = []
                if other.id not in faction.relationships['trade_partners']:
                    faction.relationships['trade_partners'].append(other.id)
                    faction.trigger_event_relation_change(db.session, other.id, 'trade_agreement')
                    
    except Exception as e:
        print(f"Error checking faction conflicts: {str(e)}")

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
        print(f"Error getting shared borders: {str(e)}")
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
        print(f"Error calculating quest success rate: {str(e)}")
        return 0.0

def log_faction_event(faction: Faction, event: Dict[str, Any]):
    """Log an event in the faction's recent events."""
    try:
        if 'recent_events' not in faction.state:
            faction.state['recent_events'] = []
        faction.state['recent_events'].append(event)
    except Exception as e:
        print(f"Error logging faction event: {str(e)}")

def process_region_changes(region: Region):
    """Process changes for a single region."""
    try:
        # Update population
        process_population_changes(region)
        
        # Update resources
        process_resource_changes(region)
        
        # Update buildings and infrastructure
        process_building_changes(region)
        
        # Process events and effects
        process_region_events(region)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        raise DatabaseError(f"Failed to process region changes: {str(e)}")

def process_population_changes(region: Region):
    """Process population changes in a region."""
    try:
        # Natural growth
        growth_rate = 0.001  # 0.1% per tick
        region.population = int(region.population * (1 + growth_rate))
        
        # Migration effects
        for neighbor in region.get_neighbors():
            if neighbor.prosperity > region.prosperity * 1.5:
                # Emigration to more prosperous regions
                migrants = int(region.population * 0.01)  # 1% migration
                region.population -= migrants
                neighbor.population += migrants
                
        # Minimum population check
        region.population = max(region.population, 100)
        
    except Exception as e:
        print(f"Error processing population changes: {str(e)}")

def process_resource_changes(region: Region):
    """Process resource changes in a region."""
    try:
        # Resource production
        for resource in region.resources:
            if resource['type'] in region.resource_production_rates:
                rate = region.resource_production_rates[resource['type']]
                resource['amount'] += rate
                
        # Resource consumption
        population_consumption = region.population * region.per_capita_consumption
        for resource in region.resources:
            if resource['type'] == 'food':
                resource['amount'] = max(0, resource['amount'] - population_consumption)
                
        # Trade effects
        if hasattr(region, 'trade_routes'):
            for route in region.trade_routes:
                if route['active']:
                    process_trade_effects(region, route)
                    
    except Exception as e:
        print(f"Error processing resource changes: {str(e)}")

def process_building_changes(region: Region):
    """Process changes to buildings and infrastructure."""
    try:
        # Building maintenance
        for building in region.buildings:
            if building['condition'] > 0:
                # Natural decay
                building['condition'] -= 0.1  # 0.1% decay per tick
                
                # Repair if maintained
                if building['maintained']:
                    repair_rate = 0.5  # 0.5% repair per tick
                    building['condition'] = min(100, building['condition'] + repair_rate)
                    
            # Building effects
            apply_building_effects(region, building)
            
    except Exception as e:
        print(f"Error processing building changes: {str(e)}")

def process_region_events(region: Region):
    """Process active events and their effects on the region."""
    try:
        current_time = datetime.utcnow()
        
        # Process active events
        if 'active_events' in region.state:
            completed_events = []
            for event in region.state['active_events']:
                if event['end_time'] and datetime.fromisoformat(event['end_time']) <= current_time:
                    completed_events.append(event)
                    apply_event_resolution(region, event)
                else:
                    apply_event_effects(region, event)
                    
            # Remove completed events
            region.state['active_events'] = [
                event for event in region.state['active_events']
                if event not in completed_events
            ]
            
        # Generate random events
        if random.random() < 0.05:  # 5% chance per tick
            generate_region_event(region)
            
    except Exception as e:
        print(f"Error processing region events: {str(e)}")

def process_trade_effects(region: Region, trade_route: Dict[str, Any]):
    """Process effects of an active trade route."""
    try:
        partner_region = Region.query.get(trade_route['partner_id'])
        if not partner_region:
            return
            
        # Calculate trade volume
        base_volume = min(
            region.population,
            partner_region.population
        ) * 0.001  # 0.1% of smaller population
        
        # Apply modifiers
        volume = base_volume * (
            1 +
            region.trade_efficiency +
            partner_region.trade_efficiency
        )
        
        # Exchange resources
        for exchange in trade_route['exchanges']:
            export_resource = next(
                (r for r in region.resources if r['type'] == exchange['export']),
                None
            )
            import_resource = next(
                (r for r in partner_region.resources if r['type'] == exchange['import']),
                None
            )
            
            if export_resource and import_resource:
                trade_amount = min(
                    export_resource['amount'] * 0.1,  # Max 10% of available
                    volume * exchange['rate']
                )
                
                export_resource['amount'] -= trade_amount
                import_resource['amount'] += trade_amount
                
                # Update prosperity based on trade
                region.prosperity += trade_amount * 0.01
                partner_region.prosperity += trade_amount * 0.01
                
    except Exception as e:
        print(f"Error processing trade effects: {str(e)}")

def apply_building_effects(region: Region, building: Dict[str, Any]):
    """Apply effects of a building to the region."""
    try:
        if building['condition'] <= 0:
            return
            
        effect_power = building['condition'] / 100.0
        
        if building['type'] == 'farm':
            # Increase food production
            if 'food' in region.resource_production_rates:
                region.resource_production_rates['food'] *= (1 + 0.1 * effect_power)
                
        elif building['type'] == 'market':
            # Improve trade efficiency
            region.trade_efficiency += 0.05 * effect_power
            
        elif building['type'] == 'housing':
            # Increase population capacity
            region.population_capacity += int(100 * effect_power)
            
        elif building['type'] == 'fortress':
            # Improve defense
            region.defense_bonus += 0.2 * effect_power
            
    except Exception as e:
        print(f"Error applying building effects: {str(e)}")

def apply_event_effects(region: Region, event: Dict[str, Any]):
    """Apply ongoing effects of an active event."""
    try:
        if event['type'] == 'natural_disaster':
            # Reduce population and damage buildings
            region.population = int(region.population * 0.99)  # 1% loss per tick
            for building in region.buildings:
                building['condition'] -= 1.0  # 1% damage per tick
                
        elif event['type'] == 'festival':
            # Increase prosperity and population growth
            region.prosperity += 0.1
            region.population = int(region.population * 1.001)  # +0.1% growth
            
        elif event['type'] == 'plague':
            # Severe population loss and economic impact
            region.population = int(region.population * 0.98)  # 2% loss per tick
            region.prosperity -= 0.2
            
    except Exception as e:
        print(f"Error applying event effects: {str(e)}")

def apply_event_resolution(region: Region, event: Dict[str, Any]):
    """Apply final effects when an event ends."""
    try:
        if event['type'] == 'natural_disaster':
            # Recovery phase
            region.prosperity += 0.5  # Recovery bonus
            
        elif event['type'] == 'festival':
            # Lasting benefits
            region.prosperity += 1.0
            region.population_growth_rate += 0.001  # Permanent small boost
            
        elif event['type'] == 'plague':
            # Aftermath effects
            region.population_growth_rate += 0.002  # Compensatory growth
            region.defense_bonus += 0.1  # Survived population is hardier
            
    except Exception as e:
        print(f"Error applying event resolution: {str(e)}")

def generate_region_event(region: Region):
    """Generate a random event for the region."""
    try:
        event_types = [
            'natural_disaster',
            'festival',
            'plague',
            'trade_boom',
            'bandit_raid'
        ]
        
        event_type = random.choice(event_types)
        duration = timedelta(days=random.randint(1, 7))
        
        event = {
            'type': event_type,
            'start_time': datetime.utcnow().isoformat(),
            'end_time': (datetime.utcnow() + duration).isoformat(),
            'severity': random.uniform(0.1, 1.0)
        }
        
        if 'active_events' not in region.state:
            region.state['active_events'] = []
            
        region.state['active_events'].append(event)
        
    except Exception as e:
        print(f"Error generating region event: {str(e)}")

def generate_random_event(world_state: WorldState):
    """Generate a random world event."""
    try:
        event_types = [
            {
                'type': 'war_declaration',
                'weight': 0.1,
                'duration': timedelta(days=random.randint(30, 90)),
                'handler': generate_war_event
            },
            {
                'type': 'trade_agreement',
                'weight': 0.2,
                'duration': timedelta(days=random.randint(180, 365)),
                'handler': generate_trade_event
            },
            {
                'type': 'diplomatic_crisis',
                'weight': 0.15,
                'duration': timedelta(days=random.randint(7, 30)),
                'handler': generate_diplomatic_event
            },
            {
                'type': 'global_festival',
                'weight': 0.2,
                'duration': timedelta(days=random.randint(3, 7)),
                'handler': generate_festival_event
            },
            {
                'type': 'natural_calamity',
                'weight': 0.1,
                'duration': timedelta(days=random.randint(1, 14)),
                'handler': generate_calamity_event
            },
            {
                'type': 'technological_discovery',
                'weight': 0.15,
                'duration': timedelta(days=random.randint(90, 180)),
                'handler': generate_discovery_event
            },
            {
                'type': 'religious_movement',
                'weight': 0.1,
                'duration': timedelta(days=random.randint(30, 90)),
                'handler': generate_religious_event
            }
        ]
        
        # Select event type based on weights
        weights = [e['weight'] for e in event_types]
        selected_event = random.choices(event_types, weights=weights)[0]
        
        # Generate event data
        event_data = selected_event['handler'](world_state)
        if not event_data:
            return
            
        # Create world event
        event = WorldEvent(
            type=selected_event['type'],
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow() + selected_event['duration'],
            status='active',
            data=event_data
        )
        
        db.session.add(event)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error generating random event: {str(e)}")

def generate_war_event(world_state: WorldState) -> Dict[str, Any]:
    """Generate a war declaration event between factions."""
    try:
        # Get all factions
        factions = Faction.query.all()
        if len(factions) < 2:
            return None
            
        # Find factions with hostile relations
        hostile_pairs = []
        for f1 in factions:
            for f2 in factions:
                if f1.id >= f2.id:
                    continue
                    
                rel = f1.get_relation(db.session, f2.id)
                if rel and rel.relation_type == RelationshipType.HOSTILE.value:
                    hostile_pairs.append((f1, f2))
                    
        if not hostile_pairs:
            return None
            
        # Select random hostile pair
        faction1, faction2 = random.choice(hostile_pairs)
        
        # Generate war data
        return {
            'aggressor_id': faction1.id,
            'defender_id': faction2.id,
            'cause': random.choice([
                'border_dispute',
                'resource_conflict',
                'ideological_differences',
                'revenge',
                'expansion'
            ]),
            'initial_demands': {
                'territory': random.choice([True, False]),
                'resources': random.choice([True, False]),
                'subjugation': random.choice([True, False])
            }
        }
        
    except Exception as e:
        print(f"Error generating war event: {str(e)}")
        return None

def generate_trade_event(world_state: WorldState) -> Dict[str, Any]:
    """Generate a trade agreement event between regions."""
    try:
        # Get all regions
        regions = Region.query.all()
        if len(regions) < 2:
            return None
            
        # Find regions with complementary resources
        trade_pairs = []
        for r1 in regions:
            for r2 in regions:
                if r1.id >= r2.id:
                    continue
                    
                r1_resources = set(r['type'] for r in r1.resources)
                r2_resources = set(r['type'] for r in r2.resources)
                
                if r1_resources and r2_resources and r1_resources != r2_resources:
                    trade_pairs.append((r1, r2))
                    
        if not trade_pairs:
            return None
            
        # Select random trade pair
        region1, region2 = random.choice(trade_pairs)
        
        # Generate trade agreement
        return {
            'region1_id': region1.id,
            'region2_id': region2.id,
            'terms': {
                'duration_days': random.randint(180, 365),
                'resource_exchanges': [
                    {
                        'resource1': random.choice([r['type'] for r in region1.resources]),
                        'resource2': random.choice([r['type'] for r in region2.resources]),
                        'rate': round(random.uniform(0.8, 1.2), 2)
                    }
                ],
                'tariffs': round(random.uniform(0.05, 0.15), 2)
            }
        }
        
    except Exception as e:
        print(f"Error generating trade event: {str(e)}")
        return None

def generate_diplomatic_event(world_state: WorldState) -> Dict[str, Any]:
    """Generate a diplomatic crisis event."""
    try:
        # Get all factions
        factions = Faction.query.all()
        if len(factions) < 2:
            return None
            
        # Select random factions
        faction1, faction2 = random.sample(factions, 2)
        
        crisis_types = [
            'espionage_discovered',
            'diplomatic_insult',
            'broken_promise',
            'cultural_conflict',
            'assassination_attempt'
        ]
        
        return {
            'faction1_id': faction1.id,
            'faction2_id': faction2.id,
            'crisis_type': random.choice(crisis_types),
            'severity': round(random.uniform(0.3, 1.0), 2),
            'resolution_options': [
                'diplomatic_talks',
                'economic_sanctions',
                'military_threats',
                'public_apology'
            ]
        }
        
    except Exception as e:
        print(f"Error generating diplomatic event: {str(e)}")
        return None

def generate_festival_event(world_state: WorldState) -> Dict[str, Any]:
    """Generate a global festival event."""
    try:
        festival_types = [
            'harvest_celebration',
            'peace_jubilee',
            'cultural_exchange',
            'magical_convergence',
            'historical_commemoration'
        ]
        
        participating_regions = []
        for region in Region.query.all():
            if random.random() < 0.7:  # 70% chance to participate
                participating_regions.append(region.id)
                
        if not participating_regions:
            return None
            
        return {
            'festival_type': random.choice(festival_types),
            'participating_regions': participating_regions,
            'bonuses': {
                'prosperity': round(random.uniform(0.1, 0.3), 2),
                'happiness': round(random.uniform(0.2, 0.4), 2),
                'cultural_influence': round(random.uniform(0.1, 0.2), 2)
            },
            'special_events': random.sample([
                'grand_feast',
                'tournament',
                'artistic_performances',
                'magical_displays',
                'trade_fair'
            ], k=random.randint(1, 3))
        }
        
    except Exception as e:
        print(f"Error generating festival event: {str(e)}")
        return None

def generate_calamity_event(world_state: WorldState) -> Dict[str, Any]:
    """Generate a natural calamity event."""
    try:
        calamity_types = [
            'earthquake',
            'flood',
            'drought',
            'plague',
            'magical_disturbance'
        ]
        
        # Select random regions for impact
        affected_regions = []
        center_region = random.choice(Region.query.all())
        affected_regions.append(center_region.id)
        
        # Spread to neighboring regions
        for neighbor_id in center_region.neighbors:
            if random.random() < 0.6:  # 60% chance to spread
                affected_regions.append(neighbor_id)
                
        return {
            'calamity_type': random.choice(calamity_types),
            'epicenter_region_id': center_region.id,
            'affected_regions': affected_regions,
            'severity': round(random.uniform(0.3, 1.0), 2),
            'effects': {
                'population_impact': round(random.uniform(0.05, 0.2), 2),
                'infrastructure_damage': round(random.uniform(0.1, 0.4), 2),
                'resource_depletion': round(random.uniform(0.1, 0.3), 2)
            },
            'required_resources': {
                'gold': random.randint(1000, 5000),
                'materials': random.randint(500, 2000)
            }
        }
        
    except Exception as e:
        print(f"Error generating calamity event: {str(e)}")
        return None

def generate_discovery_event(world_state: WorldState) -> Dict[str, Any]:
    """Generate a technological discovery event."""
    try:
        discovery_types = [
            'military_innovation',
            'agricultural_advancement',
            'magical_breakthrough',
            'architectural_innovation',
            'alchemical_discovery'
        ]
        
        # Select random faction as discoverer
        discoverer = random.choice(Faction.query.all())
        
        return {
            'discovery_type': random.choice(discovery_types),
            'discoverer_faction_id': discoverer.id,
            'breakthrough_level': random.randint(1, 5),
            'benefits': {
                'efficiency_boost': round(random.uniform(0.1, 0.3), 2),
                'resource_bonus': round(random.uniform(0.1, 0.2), 2),
                'prestige_gain': round(random.uniform(0.2, 0.4), 2)
            },
            'requirements': {
                'research_cost': random.randint(1000, 5000),
                'implementation_time': random.randint(30, 90)
            },
            'spread_chance': round(random.uniform(0.1, 0.3), 2)
        }
        
    except Exception as e:
        print(f"Error generating discovery event: {str(e)}")
        return None

def generate_religious_event(world_state: WorldState) -> Dict[str, Any]:
    """Generate a religious movement event."""
    try:
        event_types = [
            'new_doctrine',
            'divine_manifestation',
            'heretical_movement',
            'religious_reform',
            'spiritual_awakening'
        ]
        
        # Select random regions for movement spread
        origin_region = random.choice(Region.query.all())
        affected_regions = [origin_region.id]
        
        # Calculate spread to other regions
        for region in Region.query.all():
            if region.id != origin_region.id and random.random() < 0.4:  # 40% spread chance
                affected_regions.append(region.id)
                
        return {
            'event_type': random.choice(event_types),
            'origin_region_id': origin_region.id,
            'affected_regions': affected_regions,
            'intensity': round(random.uniform(0.3, 1.0), 2),
            'effects': {
                'social_stability': round(random.uniform(-0.2, 0.2), 2),
                'cultural_change': round(random.uniform(0.1, 0.3), 2),
                'faction_relations': round(random.uniform(-0.2, 0.2), 2)
            },
            'duration_modifiers': {
                'fervor': round(random.uniform(0.8, 1.2), 2),
                'resistance': round(random.uniform(0.1, 0.4), 2)
            }
        }
        
    except Exception as e:
        print(f"Error generating religious event: {str(e)}")
        return None

def process_world_events(world_state: WorldState) -> None:
    """Process all active world events."""
    try:
        current_time = datetime.utcnow()
        active_events = WorldEvent.query.filter_by(status='active').all()
        
        for event in active_events:
            # Check if event has expired
            if event.end_time and event.end_time <= current_time:
                handle_event_completion(event)
                continue
                
            # Process ongoing event effects
            handle_event_effects(event)
            
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error processing world events: {str(e)}")

def handle_event_completion(event: WorldEvent) -> None:
    """Handle the completion of a world event."""
    try:
        event.status = 'completed'
        
        if event.type == 'war_declaration':
            handle_war_completion(event)
        elif event.type == 'trade_agreement':
            handle_trade_completion(event)
        elif event.type == 'diplomatic_crisis':
            handle_diplomatic_completion(event)
        elif event.type == 'global_festival':
            handle_festival_completion(event)
        elif event.type == 'natural_calamity':
            handle_calamity_completion(event)
        elif event.type == 'technological_discovery':
            handle_discovery_completion(event)
        elif event.type == 'religious_movement':
            handle_religious_completion(event)
            
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Error handling event completion: {str(e)}")

def handle_event_effects(event: WorldEvent) -> None:
    """Handle the ongoing effects of an active world event."""
    try:
        if event.type == 'war_declaration':
            handle_war_effects(event)
        elif event.type == 'trade_agreement':
            handle_trade_effects(event)
        elif event.type == 'diplomatic_crisis':
            handle_diplomatic_effects(event)
        elif event.type == 'global_festival':
            handle_festival_effects(event)
        elif event.type == 'natural_calamity':
            handle_calamity_effects(event)
        elif event.type == 'technological_discovery':
            handle_discovery_effects(event)
        elif event.type == 'religious_movement':
            handle_religious_effects(event)
            
    except Exception as e:
        print(f"Error handling event effects: {str(e)}")

def handle_war_effects(event: WorldEvent) -> None:
    """Handle ongoing effects of a war event."""
    data = event.data
    try:
        aggressor = Faction.query.get(data['aggressor_id'])
        defender = Faction.query.get(data['defender_id'])
        
        if not aggressor or not defender:
            return
            
        # Update military resources
        for faction in [aggressor, defender]:
            faction.resources['military'] = max(0, faction.resources.get('military', 100) - 5)
            faction.resources['gold'] = max(0, faction.resources.get('gold', 1000) - 100)
            
        # Random battle outcomes
        if random.random() < 0.1:  # 10% chance for major battle
            winner = random.choice([aggressor, defender])
            loser = defender if winner == aggressor else aggressor
            
            # Apply battle effects
            winner.resources['military'] = max(0, winner.resources.get('military', 100) - 10)
            loser.resources['military'] = max(0, loser.resources.get('military', 100) - 20)
            
            # Territory changes
            if data['initial_demands'].get('territory') and random.random() < 0.3:
                if loser.territories:
                    territory = random.choice(loser.territories)
                    loser.territories.remove(territory)
                    winner.territories.append(territory)
                    
    except Exception as e:
        print(f"Error handling war effects: {str(e)}")

def handle_trade_effects(event: WorldEvent) -> None:
    """Handle ongoing effects of a trade agreement."""
    data = event.data
    try:
        region1 = Region.query.get(data['region1_id'])
        region2 = Region.query.get(data['region2_id'])
        
        if not region1 or not region2:
            return
            
        for exchange in data['terms']['resource_exchanges']:
            # Transfer resources between regions
            r1_amount = region1.resources.get(exchange['resource1'], 0)
            r2_amount = region2.resources.get(exchange['resource2'], 0)
            
            transfer_amount = min(10, r1_amount)  # Max 10 units per tick
            if transfer_amount > 0:
                region1.resources[exchange['resource1']] -= transfer_amount
                region2.resources[exchange['resource1']] += transfer_amount
                
            transfer_amount = min(10, r2_amount)
            if transfer_amount > 0:
                region2.resources[exchange['resource2']] -= transfer_amount
                region1.resources[exchange['resource2']] += transfer_amount
                
        # Apply prosperity bonuses
        region1.prosperity += 0.01
        region2.prosperity += 0.01
        
    except Exception as e:
        print(f"Error handling trade effects: {str(e)}")

def handle_diplomatic_effects(event: WorldEvent) -> None:
    """Handle ongoing effects of a diplomatic crisis."""
    data = event.data
    try:
        faction1 = Faction.query.get(data['faction1_id'])
        faction2 = Faction.query.get(data['faction2_id'])
        
        if not faction1 or not faction2:
            return
            
        # Deteriorate relations
        current_relation = faction1.get_relation(db.session, faction2.id)
        if current_relation:
            decay = data['severity'] * 0.1
            current_relation.value = max(-100, min(100, current_relation.value - decay))
            
        # Impact on trade and diplomacy
        if random.random() < data['severity']:
            # Cancel some trade agreements
            for agreement in faction1.trade_agreements:
                if agreement.partner_id == faction2.id and random.random() < 0.2:
                    agreement.status = 'cancelled'
                    
    except Exception as e:
        print(f"Error handling diplomatic effects: {str(e)}")

def handle_festival_effects(event: WorldEvent) -> None:
    """Handle ongoing effects of a festival event."""
    data = event.data
    try:
        for region_id in data['participating_regions']:
            region = Region.query.get(region_id)
            if not region:
                continue
                
            # Apply festival bonuses
            region.prosperity += data['bonuses']['prosperity'] * 0.1
            region.happiness += data['bonuses']['happiness'] * 0.1
            region.cultural_influence += data['bonuses']['cultural_influence'] * 0.1
            
            # Special event effects
            if 'grand_feast' in data['special_events']:
                region.food_production *= 1.1
            if 'trade_fair' in data['special_events']:
                region.trade_income *= 1.2
                
    except Exception as e:
        print(f"Error handling festival effects: {str(e)}")

def handle_calamity_effects(event: WorldEvent) -> None:
    """Handle ongoing effects of a natural calamity."""
    data = event.data
    try:
        for region_id in data['affected_regions']:
            region = Region.query.get(region_id)
            if not region:
                continue
                
            # Apply calamity effects
            severity = data['severity']
            region.population = int(region.population * (1 - data['effects']['population_impact'] * 0.1))
            region.infrastructure_level *= (1 - data['effects']['infrastructure_damage'] * 0.1)
            
            # Resource depletion
            for resource in region.resources:
                resource['amount'] *= (1 - data['effects']['resource_depletion'] * 0.1)
                
            # Recovery costs
            if region.resources.get('gold', 0) >= 100:
                region.resources['gold'] -= 100  # Recovery costs
                region.infrastructure_level *= 1.01  # Small recovery
                
    except Exception as e:
        print(f"Error handling calamity effects: {str(e)}")

def handle_discovery_effects(event: WorldEvent) -> None:
    """Handle ongoing effects of a technological discovery."""
    data = event.data
    try:
        discoverer = Faction.query.get(data['discoverer_faction_id'])
        if not discoverer:
            return
            
        # Apply ongoing benefits
        if discoverer.resources.get('research_points', 0) >= data['requirements']['research_cost']:
            discoverer.resources['research_points'] -= data['requirements']['research_cost']
            
            # Apply technology benefits
            if data['discovery_type'] == 'military_innovation':
                discoverer.military_power *= (1 + data['benefits']['efficiency_boost'])
            elif data['discovery_type'] == 'agricultural_advancement':
                discoverer.food_production *= (1 + data['benefits']['efficiency_boost'])
                
            # Technology spread
            if random.random() < data['spread_chance']:
                for faction in Faction.query.all():
                    if faction.id != discoverer.id and random.random() < 0.3:
                        faction.technologies.append(data['discovery_type'])
                        
    except Exception as e:
        print(f"Error handling discovery effects: {str(e)}")

def handle_religious_effects(event: WorldEvent) -> None:
    """Handle ongoing effects of a religious movement."""
    data = event.data
    try:
        for region_id in data['affected_regions']:
            region = Region.query.get(region_id)
            if not region:
                continue
                
            # Apply religious effects
            intensity = data['intensity'] * data['duration_modifiers']['fervor']
            
            # Social stability changes
            region.stability += data['effects']['social_stability'] * 0.1
            
            # Cultural influence
            region.cultural_influence += data['effects']['cultural_change'] * 0.1
            
            # Faction relation changes
            if random.random() < intensity:
                for faction in Faction.query.all():
                    if faction.primary_religion == data['event_type']:
                        faction.influence += 0.1
                    else:
                        faction.influence -= 0.05
                        
    except Exception as e:
        print(f"Error handling religious effects: {str(e)}")

def handle_war_completion(event: WorldEvent) -> None:
    """Handle the completion of a war event."""
    data = event.data
    try:
        aggressor = Faction.query.get(data['aggressor_id'])
        defender = Faction.query.get(data['defender_id'])
        
        if not aggressor or not defender:
            return
            
        # Determine winner based on military power
        aggressor_power = aggressor.resources.get('military', 0)
        defender_power = defender.resources.get('military', 0)
        
        winner = aggressor if aggressor_power > defender_power else defender
        loser = defender if winner == aggressor else aggressor
        
        # Apply peace terms
        if data['initial_demands'].get('territory'):
            if loser.territories:
                territory = random.choice(loser.territories)
                loser.territories.remove(territory)
                winner.territories.append(territory)
                
        if data['initial_demands'].get('resources'):
            resource_amount = min(1000, loser.resources.get('gold', 0))
            loser.resources['gold'] = max(0, loser.resources.get('gold', 0) - resource_amount)
            winner.resources['gold'] = winner.resources.get('gold', 0) + resource_amount
            
        # Update relations
        relation = aggressor.get_relation(db.session, defender.id)
        if relation:
            relation.value = -50  # Set to very negative after war
            
    except Exception as e:
        print(f"Error handling war completion: {str(e)}")

def handle_trade_completion(event: WorldEvent) -> None:
    """Handle the completion of a trade agreement."""
    data = event.data
    try:
        region1 = Region.query.get(data['region1_id'])
        region2 = Region.query.get(data['region2_id'])
        
        if not region1 or not region2:
            return
            
        # Calculate final prosperity gains
        region1.prosperity = min(100, region1.prosperity + 5)
        region2.prosperity = min(100, region2.prosperity + 5)
        
        # Establish long-term trade relations
        if random.random() < 0.3:  # 30% chance for permanent trade route
            trade_route = TradeRoute(
                region1_id=region1.id,
                region2_id=region2.id,
                efficiency=round(random.uniform(0.8, 1.2), 2)
            )
            db.session.add(trade_route)
            
    except Exception as e:
        print(f"Error handling trade completion: {str(e)}")

def handle_diplomatic_completion(event: WorldEvent) -> None:
    """Handle the completion of a diplomatic crisis."""
    data = event.data
    try:
        faction1 = Faction.query.get(data['faction1_id'])
        faction2 = Faction.query.get(data['faction2_id'])
        
        if not faction1 or not faction2:
            return
            
        # Resolve crisis
        resolution_type = random.choice(data['resolution_options'])
        
        if resolution_type == 'diplomatic_talks':
            # Improve relations slightly
            relation = faction1.get_relation(db.session, faction2.id)
            if relation:
                relation.value = min(100, relation.value + 10)
                
        elif resolution_type == 'economic_sanctions':
            # Reduce trade efficiency
            for route in faction1.trade_routes:
                if route.partner_id == faction2.id:
                    route.efficiency *= 0.8
                    
    except Exception as e:
        print(f"Error handling diplomatic completion: {str(e)}")

def handle_festival_completion(event: WorldEvent) -> None:
    """Handle the completion of a festival event."""
    data = event.data
    try:
        for region_id in data['participating_regions']:
            region = Region.query.get(region_id)
            if not region:
                continue
                
            # Apply permanent bonuses
            region.prosperity = min(100, region.prosperity + 2)
            region.happiness = min(100, region.happiness + 3)
            region.cultural_influence = min(100, region.cultural_influence + 1)
            
            # Generate historical record
            historical_event = HistoricalEvent(
                region_id=region.id,
                type='festival',
                description=f"The {data['festival_type']} brought great joy and prosperity to the region.",
                importance=round(random.uniform(0.3, 0.7), 2)
            )
            db.session.add(historical_event)
            
    except Exception as e:
        print(f"Error handling festival completion: {str(e)}")

def handle_calamity_completion(event: WorldEvent) -> None:
    """Handle the completion of a natural calamity."""
    data = event.data
    try:
        for region_id in data['affected_regions']:
            region = Region.query.get(region_id)
            if not region:
                continue
                
            # Start recovery phase
            recovery_event = WorldEvent(
                type='recovery_phase',
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow() + timedelta(days=90),
                status='active',
                data={
                    'region_id': region.id,
                    'calamity_type': data['calamity_type'],
                    'recovery_rate': round(random.uniform(0.01, 0.05), 3)
                }
            )
            db.session.add(recovery_event)
            
            # Historical record
            historical_event = HistoricalEvent(
                region_id=region.id,
                type='calamity',
                description=f"The region endured a devastating {data['calamity_type']}.",
                importance=round(random.uniform(0.6, 0.9), 2)
            )
            db.session.add(historical_event)
            
    except Exception as e:
        print(f"Error handling calamity completion: {str(e)}")

def handle_discovery_completion(event: WorldEvent) -> None:
    """Handle the completion of a technological discovery."""
    data = event.data
    try:
        discoverer = Faction.query.get(data['discoverer_faction_id'])
        if not discoverer:
            return
            
        # Add technology permanently
        discoverer.technologies.append({
            'type': data['discovery_type'],
            'level': data['breakthrough_level'],
            'discovered_at': datetime.utcnow().isoformat()
        })
        
        # Apply permanent bonuses
        if data['discovery_type'] == 'military_innovation':
            discoverer.military_power *= 1.1
        elif data['discovery_type'] == 'agricultural_advancement':
            discoverer.food_production *= 1.1
            
        # Historical record
        historical_event = HistoricalEvent(
            faction_id=discoverer.id,
            type='discovery',
            description=f"A breakthrough in {data['discovery_type']} was achieved.",
            importance=round(random.uniform(0.5, 0.8), 2)
        )
        db.session.add(historical_event)
        
    except Exception as e:
        print(f"Error handling discovery completion: {str(e)}")

def handle_religious_completion(event: WorldEvent) -> None:
    """Handle the completion of a religious movement."""
    data = event.data
    try:
        for region_id in data['affected_regions']:
            region = Region.query.get(region_id)
            if not region:
                continue
                
            # Permanent cultural changes
            region.cultural_influence = min(100, region.cultural_influence + 5)
            
            # Update regional religion stats
            if data['event_type'] in region.religious_demographics:
                region.religious_demographics[data['event_type']] += 10
            else:
                region.religious_demographics[data['event_type']] = 10
                
            # Normalize religious demographics
            total = sum(region.religious_demographics.values())
            region.religious_demographics = {
                k: (v / total) * 100 
                for k, v in region.religious_demographics.items()
            }
            
            # Historical record
            historical_event = HistoricalEvent(
                region_id=region.id,
                type='religious',
                description=f"The {data['event_type']} movement transformed the spiritual landscape.",
                importance=round(random.uniform(0.4, 0.7), 2)
            )
            db.session.add(historical_event)
            
    except Exception as e:
        print(f"Error handling religious completion: {str(e)}") 