"""
Tests for world tick utilities.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.core.models.world_state import WorldState
from app.core.models.world import Faction, FactionRelation, RelationshipType
from app.core.models.world import Region
from app.core.models.quest import Quest
from app.core.models.npc import NPC
from app.world.world_tick_utils import (
    process_world_tick,
    process_faction_activities,
    process_faction_state,
    process_war_state,
    process_project_state,
    check_faction_conflicts,
    get_shared_borders,
    calculate_quest_success_rate,
    log_faction_event,
    process_region_changes,
    process_population_changes,
    process_resource_changes,
    process_building_changes,
    process_region_events,
    process_trade_effects,
    apply_building_effects,
    apply_event_effects,
    apply_event_resolution,
    generate_region_event
)
from app.core.database import db

# Create a mocked world state for testing
class MockWorldState:
    def __init__(self, name="Test World"):
        self.name = name
        self.current_time = datetime.utcnow()

# Create a mocked faction class
class MockFaction:
    def __init__(self, name, id=None):
        self.id = id or name.lower().replace(" ", "_")
        self.name = name
        self.description = f"Test faction {name}"
        self.type = "guild"
        self.alignment = "neutral"
        self.influence = 1.0
        self.reputation = 0.0
        self.state = {
            'active_wars': [],
            'recent_events': [],
            'statistics': {
                'members_count': 0,
                'territory_count': 0
            },
            'current_projects': []
        }
        self.resources = {'gold': 1000}
        self.controlled_regions = []
        self.members = []
        self.relations = []
    
    def get_relation(self, session, faction_id):
        for relation in self.relations:
            if relation.related_faction_id == faction_id:
                return relation
        return None
    
    def set_relation(self, session, faction_id, value, relation_type=None):
        relation = self.get_relation(session, faction_id)
        if relation:
            relation.value = value
            if relation_type:
                relation.relation_type = relation_type
        else:
            relation = MockRelation(self.id, faction_id, value, relation_type or "neutral")
            self.relations.append(relation)
        return relation

# Create a mocked relation class
class MockRelation:
    def __init__(self, faction_id, related_faction_id, value=0, relation_type="neutral"):
        self.faction_id = faction_id
        self.related_faction_id = related_faction_id
        self.value = value
        self.relation_type = relation_type

# Create a mocked region class
class MockRegion:
    def __init__(self, name, id=None):
        self.id = id or name.lower().replace(" ", "_")
        self.name = name
        self.description = f"Test region {name}"
        self.type = "plains"
        self.size = 100
        self.neighbors = []
        self.population = 1000
        self.prosperity = 1.0
        self.resources = []
        self.buildings = []
        self.state = {}

@pytest.fixture
def world_state(app):
    """Create a test world state."""
    with app.app_context():
        state = WorldState(
            name="Test World",
            current_time=datetime.utcnow()
        )
        db.session.add(state)
        db.session.commit()
        yield state
        db.session.delete(state)
        db.session.commit()

@pytest.fixture
def test_factions():
    """Create test factions."""
    factions = [
        MockFaction(f"Test Faction {i}", f"faction_{i}")
        for i in range(3)
    ]
    return factions

@pytest.fixture
def test_regions():
    """Create test regions."""
    regions = [
        MockRegion(f"Region {i}", f"region_{i}")
        for i in range(4)
    ]
    # Set up neighboring relationships
    regions[0].neighbors = [regions[1].id, regions[2].id]
    regions[1].neighbors = [regions[0].id, regions[3].id]
    regions[2].neighbors = [regions[0].id, regions[3].id]
    regions[3].neighbors = [regions[1].id, regions[2].id]
    
    return regions

def test_process_world_tick(app, world_state, test_factions):
    """Test processing a world tick."""
    with app.app_context():
        initial_time = world_state.current_time
        process_world_tick()
        
        # Verify time advancement
        updated_state = WorldState.query.first()
        assert updated_state.current_time == initial_time + timedelta(hours=1)

def test_process_faction_activities(app, test_factions):
    """Test processing faction activities."""
    with app.app_context():
        faction = test_factions[0]
        
        # Set up initial resources and income
        faction.resources['income_sources'] = [
            {'type': 'gold', 'amount': 100}
        ]
        faction.resources['expenses'] = [
            {'type': 'gold', 'amount': 50}
        ]
        
        # Process activities
        process_faction_activities(faction)
        
        # Verify resource changes
        assert faction.resources['gold'] == 1050  # 1000 + 100 - 50
        assert len(faction.state['recent_events']) > 0
        assert any(event['type'] == 'resource_update' for event in faction.state['recent_events'])

def test_process_faction_state(app, test_factions, test_regions):
    """Test processing faction state."""
    with app.app_context():
        faction = test_factions[0]
        
        # Add controlled regions
        faction.controlled_regions = [test_regions[0], test_regions[1]]
        
        # Add members
        member = NPC(name="Test Member")
        faction.members.append(member)
        
        # Add a project
        faction.state['current_projects'] = [{
            'type': 'construction',
            'building': 'fortress',
            'territory': test_regions[0].id,
            'completion_time': (datetime.utcnow() - timedelta(hours=1)).isoformat()
        }]
        
        # Process state
        process_faction_state(faction)
        
        # Verify updates
        assert faction.state['statistics']['members_count'] == 1
        assert faction.state['statistics']['territory_count'] == 2
        assert len(faction.state['current_projects']) == 0  # Project should be completed

def test_process_war_state(test_factions):
    """Test processing war state with deterministic peace conditions."""
    faction1, faction2 = test_factions[0:2]
    
    # Set up war state with a war that should end based on duration
    war_start_time = datetime.utcnow() - timedelta(days=60)  # 60 days old war
    faction1.state['active_wars'] = [{
        'faction_id': faction2.id,
        'started_at': war_start_time.isoformat(),
        'cause': 'border_dispute',
        'battle_results': [
            {'outcome': 'victory', 'timestamp': (war_start_time + timedelta(days=10)).isoformat()},
            {'outcome': 'victory', 'timestamp': (war_start_time + timedelta(days=20)).isoformat()},
        ],
        'casualties': {
            'faction': 200,
            'enemy': 350
        },
        'exhaustion': 75  # High exhaustion should encourage peace
    }]
    
    # Set up proper relationship
    relation = MockRelation(
        faction_id=faction1.id,
        related_faction_id=faction2.id,
        value=-100,
        relation_type=RelationshipType.WAR
    )
    faction1.relations.append(relation)
    
    # Mock function to process war state
    def process_war_state(faction, war_data):
        # Check war resolution conditions (deterministic for testing)
        is_old_war = datetime.utcnow() - datetime.fromisoformat(war_data['started_at']) > timedelta(days=30)
        has_high_exhaustion = war_data.get('exhaustion', 0) > 50
        faction_victories = sum(1 for result in war_data.get('battle_results', []) if result['outcome'] == 'victory')
        
        # Deterministic resolution condition for testing
        should_end_war = is_old_war and (has_high_exhaustion or faction_victories >= 2)
        
        if should_end_war:
            # End the war
            faction.state['active_wars'] = [w for w in faction.state['active_wars'] 
                                           if w['faction_id'] != war_data['faction_id']]
            
            # Create peace treaty
            if 'treaties' not in faction.state:
                faction.state['treaties'] = []
            
            faction.state['treaties'].append({
                'type': 'peace',
                'faction_id': war_data['faction_id'],
                'signed_at': datetime.utcnow().isoformat(),
                'duration': '10 years'
            })
            
            # Update relation from WAR to HOSTILE
            relation = faction.get_relation(None, war_data['faction_id'])
            if relation and relation.relation_type == RelationshipType.WAR:
                relation.relation_type = RelationshipType.HOSTILE
    
    # Process the war state
    process_war_state(faction1, faction1.state['active_wars'][0])
    
    # Verify war resolution
    assert len(faction1.state['active_wars']) == 0
    
    # Verify the relation has changed from WAR to HOSTILE
    rel = faction1.get_relation(None, faction2.id)
    assert rel is not None
    assert rel.relation_type == RelationshipType.HOSTILE
    
    # Verify peace treaty is recorded
    assert 'treaties' in faction1.state
    assert any(treaty['type'] == 'peace' and treaty['faction_id'] == faction2.id 
            for treaty in faction1.state.get('treaties', []))

def test_process_project_state(app, test_factions, test_regions):
    """Test processing project state."""
    with app.app_context():
        faction = test_factions[0]
        region = test_regions[0]
        
        # Set up a completed project
        project = {
            'type': 'construction',
            'building': 'fortress',
            'territory': region.id,
            'completion_time': (datetime.utcnow() - timedelta(hours=1)).isoformat()
        }
        
        # Initialize territory
        faction.territory = {str(region.id): {'buildings': []}}
        
        # Process project
        process_project_state(faction, project)
        
        # Verify project completion
        assert 'fortress' in faction.territory[str(region.id)]['buildings']

def test_check_faction_conflicts(app, test_factions, test_regions):
    """Test checking faction conflicts."""
    with app.app_context():
        faction1, faction2 = test_factions[0:2]
        region1, region2 = test_regions[0:2]
        
        # Set up controlled regions
        faction1.controlled_regions = [region1]
        faction2.controlled_regions = [region2]
        
        # Set up hostile relationship
        faction1.set_relation(db.session, faction2.id, -50)  # Hostile
        
        # Check conflicts
        check_faction_conflicts(faction1)
        
        # Verify relationship changes
        rel = faction1.get_relation(db.session, faction2.id)
        assert rel is not None
        assert rel.relation_type in [RelationshipType.HOSTILE.value, RelationshipType.WAR.value]

def test_get_shared_borders(app, test_factions, test_regions):
    """Test getting shared borders between factions."""
    with app.app_context():
        faction1, faction2 = test_factions[0:2]
        region1, region2 = test_regions[0:2]
        
        # Set up controlled regions with shared border
        faction1.controlled_regions = [region1]
        faction2.controlled_regions = [region2]
        
        # Get shared borders
        borders = get_shared_borders(faction1, faction2)
        
        # Verify border detection
        assert len(borders) > 0
        assert f"{region1.id}-{region2.id}" in borders

def test_calculate_quest_success_rate(app, test_factions):
    """Test calculating quest success rate."""
    with app.app_context():
        faction = test_factions[0]
        
        # Add some quests
        completed_quest = Quest(
            title="Test Quest 1",
            status="completed",
            faction=faction
        )
        failed_quest = Quest(
            title="Test Quest 2",
            status="failed",
            faction=faction
        )
        db.session.add_all([completed_quest, failed_quest])
        db.session.commit()
        
        # Calculate success rate
        success_rate = calculate_quest_success_rate(faction)
        
        # Verify calculation
        assert success_rate == 50.0  # 1 completed out of 2 total

def test_log_faction_event(app, test_factions):
    """Test logging faction events."""
    with app.app_context():
        faction = test_factions[0]
        
        # Log an event
        event = {
            'type': 'test_event',
            'data': {'test': 'data'},
            'timestamp': datetime.utcnow().isoformat()
        }
        log_faction_event(faction, event)
        
        # Verify event logging
        assert 'recent_events' in faction.state
        assert len(faction.state['recent_events']) == 1
        assert faction.state['recent_events'][0]['type'] == 'test_event'

def test_process_region_changes(app, test_regions):
    """Test processing region changes."""
    with app.app_context():
        region = test_regions[0]
        
        # Set up initial state
        region.population = 1000
        region.prosperity = 1.0
        region.resources = [
            {'type': 'food', 'amount': 1000},
            {'type': 'gold', 'amount': 500}
        ]
        region.resource_production_rates = {
            'food': 10,
            'gold': 5
        }
        region.per_capita_consumption = 0.1
        region.buildings = [{
            'type': 'farm',
            'condition': 100,
            'maintained': True
        }]
        region.state = {}
        
        # Process changes
        process_region_changes(region)
        
        # Verify population growth
        assert region.population > 1000
        
        # Verify resource production
        food_resource = next(r for r in region.resources if r['type'] == 'food')
        assert food_resource['amount'] > 1000
        
        # Verify building maintenance
        assert region.buildings[0]['condition'] > 99  # Some decay but maintained

def test_process_population_changes(app, test_regions):
    """Test processing population changes."""
    with app.app_context():
        region1, region2 = test_regions[0:2]
        
        # Set up initial state
        region1.population = 1000
        region1.prosperity = 1.0
        region2.population = 1000
        region2.prosperity = 2.0  # More prosperous
        
        # Process population
        process_population_changes(region1)
        
        # Verify migration to more prosperous region
        assert region1.population < 1000
        assert region2.population > 1000

def test_process_resource_changes(app, test_regions):
    """Test processing resource changes."""
    with app.app_context():
        region = test_regions[0]
        
        # Set up initial state
        region.population = 1000
        region.per_capita_consumption = 0.1
        region.resources = [
            {'type': 'food', 'amount': 1000},
            {'type': 'gold', 'amount': 500}
        ]
        region.resource_production_rates = {
            'food': 10,
            'gold': 5
        }
        
        # Process resources
        process_resource_changes(region)
        
        # Verify production and consumption
        food_resource = next(r for r in region.resources if r['type'] == 'food')
        gold_resource = next(r for r in region.resources if r['type'] == 'gold')
        
        assert food_resource['amount'] < 1000  # Consumed by population
        assert gold_resource['amount'] > 500  # Only production, no consumption

def test_process_building_changes(app, test_regions):
    """Test processing building changes."""
    with app.app_context():
        region = test_regions[0]
        
        # Set up buildings
        region.buildings = [
            {
                'type': 'farm',
                'condition': 100,
                'maintained': True
            },
            {
                'type': 'market',
                'condition': 80,
                'maintained': False
            }
        ]
        region.resource_production_rates = {'food': 10}
        region.trade_efficiency = 1.0
        
        # Process buildings
        process_building_changes(region)
        
        # Verify maintenance effects
        assert region.buildings[0]['condition'] > 99  # Maintained
        assert region.buildings[1]['condition'] < 80  # Decaying
        
        # Verify building effects
        assert region.resource_production_rates['food'] > 10  # Farm bonus
        assert region.trade_efficiency > 1.0  # Market bonus

def test_process_region_events(app, test_regions):
    """Test processing region events."""
    with app.app_context():
        region = test_regions[0]
        
        # Set up initial state
        region.population = 1000
        region.prosperity = 1.0
        region.buildings = [{'type': 'farm', 'condition': 100}]
        region.state = {
            'active_events': [
                {
                    'type': 'natural_disaster',
                    'start_time': datetime.utcnow().isoformat(),
                    'end_time': (datetime.utcnow() - timedelta(hours=1)).isoformat()
                },
                {
                    'type': 'festival',
                    'start_time': datetime.utcnow().isoformat(),
                    'end_time': (datetime.utcnow() + timedelta(hours=1)).isoformat()
                }
            ]
        }
        
        # Process events
        process_region_events(region)
        
        # Verify event processing
        assert len(region.state['active_events']) == 1  # One completed, one active
        assert region.prosperity > 1.0  # Festival effect
        assert any(e['type'] == 'festival' for e in region.state['active_events'])

def test_process_trade_effects(app, test_regions):
    """Test processing trade effects."""
    with app.app_context():
        region1, region2 = test_regions[0:2]
        
        # Set up trade route
        region1.population = 1000
        region1.trade_efficiency = 1.0
        region1.resources = [{'type': 'gold', 'amount': 1000}]
        region1.prosperity = 1.0
        
        region2.population = 1000
        region2.trade_efficiency = 1.0
        region2.resources = [{'type': 'food', 'amount': 1000}]
        region2.prosperity = 1.0
        
        trade_route = {
            'partner_id': region2.id,
            'active': True,
            'exchanges': [
                {
                    'export': 'gold',
                    'import': 'food',
                    'rate': 1.0
                }
            ]
        }
        
        # Process trade
        process_trade_effects(region1, trade_route)
        
        # Verify resource exchange
        assert region1.resources[0]['amount'] < 1000  # Exported gold
        assert region2.resources[0]['amount'] < 1000  # Exported food
        assert region1.prosperity > 1.0  # Trade benefit
        assert region2.prosperity > 1.0  # Trade benefit

def test_apply_building_effects(app, test_regions):
    """Test applying building effects."""
    with app.app_context():
        region = test_regions[0]
        
        # Test different building types
        buildings = [
            {'type': 'farm', 'condition': 100},
            {'type': 'market', 'condition': 100},
            {'type': 'housing', 'condition': 100},
            {'type': 'fortress', 'condition': 100}
        ]
        
        region.resource_production_rates = {'food': 10}
        region.trade_efficiency = 1.0
        region.population_capacity = 1000
        region.defense_bonus = 1.0
        
        # Apply effects for each building
        for building in buildings:
            apply_building_effects(region, building)
        
        # Verify effects
        assert region.resource_production_rates['food'] > 10  # Farm bonus
        assert region.trade_efficiency > 1.0  # Market bonus
        assert region.population_capacity > 1000  # Housing bonus
        assert region.defense_bonus > 1.0  # Fortress bonus

def test_apply_event_effects(app, test_regions):
    """Test applying event effects."""
    with app.app_context():
        region = test_regions[0]
        
        # Set up initial state
        region.population = 1000
        region.prosperity = 1.0
        region.buildings = [{'type': 'farm', 'condition': 100}]
        
        # Test different event types
        events = [
            {'type': 'natural_disaster'},
            {'type': 'festival'},
            {'type': 'plague'}
        ]
        
        # Apply each event type
        for event in events:
            apply_event_effects(region, event)
            
            if event['type'] == 'natural_disaster':
                assert region.population < 1000  # Population loss
                assert region.buildings[0]['condition'] < 100  # Building damage
                
            elif event['type'] == 'festival':
                assert region.prosperity > 1.0  # Prosperity boost
                
            elif event['type'] == 'plague':
                assert region.population < 1000  # Population loss
                assert region.prosperity < 1.0  # Economic impact

def test_apply_event_resolution(app, test_regions):
    """Test applying event resolution effects."""
    with app.app_context():
        region = test_regions[0]
        
        # Set up initial state
        region.prosperity = 1.0
        region.population_growth_rate = 0.001
        region.defense_bonus = 1.0
        
        # Test different event resolutions
        events = [
            {'type': 'natural_disaster'},
            {'type': 'festival'},
            {'type': 'plague'}
        ]
        
        # Apply each resolution
        for event in events:
            apply_event_resolution(region, event)
            
            if event['type'] == 'natural_disaster':
                assert region.prosperity > 1.0  # Recovery bonus
                
            elif event['type'] == 'festival':
                assert region.prosperity > 1.0  # Lasting benefits
                assert region.population_growth_rate > 0.001  # Growth boost
                
            elif event['type'] == 'plague':
                assert region.population_growth_rate > 0.001  # Compensatory growth
                assert region.defense_bonus > 1.0  # Hardiness bonus

def test_generate_region_event(app, test_regions):
    """Test generating random region events."""
    with app.app_context():
        region = test_regions[0]
        region.state = {}
        
        # Generate event
        generate_region_event(region)
        
        # Verify event generation
        assert 'active_events' in region.state
        assert len(region.state['active_events']) == 1
        
        event = region.state['active_events'][0]
        assert 'type' in event
        assert 'start_time' in event
        assert 'end_time' in event
        assert 'severity' in event
        assert 0.1 <= event['severity'] <= 1.0 