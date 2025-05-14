"""Tests for world tick utilities."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.world.world_tick_utils import (
    generate_random_event,
    process_world_events,
    handle_event_completion,
    handle_event_effects
)
from app.models.world_state import WorldState
from app.models.world_event import WorldEvent
from app.models.faction import Faction
from app.models.region import Region
from app.core.enums import RelationshipType

@pytest.fixture
def mock_world_state():
    """Create a mock world state."""
    return Mock(spec=WorldState)

@pytest.fixture
def mock_faction():
    """Create a mock faction."""
    faction = Mock(spec=Faction)
    faction.resources = {
        'military': 100,
        'gold': 1000,
        'research_points': 500
    }
    faction.territories = ['territory1', 'territory2']
    faction.trade_agreements = []
    faction.technologies = []
    faction.military_power = 1.0
    faction.food_production = 1.0
    faction.influence = 1.0
    return faction

@pytest.fixture
def mock_region():
    """Create a mock region."""
    region = Mock(spec=Region)
    region.resources = {
        'wood': {'amount': 100},
        'iron': {'amount': 100}
    }
    region.population = 1000
    region.infrastructure_level = 1.0
    region.prosperity = 50
    region.happiness = 50
    region.cultural_influence = 50
    region.stability = 50
    region.food_production = 1.0
    region.trade_income = 1.0
    region.religious_demographics = {}
    return region

def test_generate_random_event(mock_world_state, mock_faction, mock_region):
    """Test random event generation."""
    with patch('random.choices') as mock_choices, \
         patch('random.choice') as mock_choice, \
         patch('random.random') as mock_random:
        
        # Test war event generation
        mock_choices.return_value = [{'type': 'war_declaration', 'weight': 0.1, 'duration': timedelta(days=30), 'handler': Mock()}]
        mock_choice.return_value = mock_faction
        mock_random.return_value = 0.5
        
        event = generate_random_event(mock_world_state)
        assert event.type == 'war_declaration'
        assert event.status == 'active'
        assert event.data['aggressor_id'] is not None
        assert event.data['defender_id'] is not None
        
        # Test trade event generation
        mock_choices.return_value = [{'type': 'trade_agreement', 'weight': 0.2, 'duration': timedelta(days=180), 'handler': Mock()}]
        mock_choice.return_value = mock_region
        
        event = generate_random_event(mock_world_state)
        assert event.type == 'trade_agreement'
        assert event.status == 'active'
        assert event.data['region1_id'] is not None
        assert event.data['region2_id'] is not None
        
        # Test festival event generation
        mock_choices.return_value = [{'type': 'global_festival', 'weight': 0.2, 'duration': timedelta(days=7), 'handler': Mock()}]
        
        event = generate_random_event(mock_world_state)
        assert event.type == 'global_festival'
        assert event.status == 'active'
        assert len(event.data['participating_regions']) > 0
        assert 'bonuses' in event.data

def test_process_world_events(mock_world_state):
    """Test world event processing."""
    # Create test events
    active_events = [
        Mock(spec=WorldEvent, type='war_declaration', status='active', end_time=datetime.utcnow() + timedelta(days=1)),
        Mock(spec=WorldEvent, type='trade_agreement', status='active', end_time=datetime.utcnow() - timedelta(days=1))
    ]
    
    with patch('app.models.world_event.WorldEvent.query') as mock_query:
        mock_query.filter_by.return_value.all.return_value = active_events
        
        process_world_events(mock_world_state)
        
        # Check that ongoing event was processed
        assert active_events[0].status == 'active'
        
        # Check that expired event was completed
        assert active_events[1].status == 'completed'

def test_handle_war_effects(mock_faction):
    """Test war event effects."""
    event = Mock(spec=WorldEvent)
    event.data = {
        'aggressor_id': 1,
        'defender_id': 2,
        'initial_demands': {'territory': True}
    }
    
    with patch('app.models.faction.Faction.query') as mock_query:
        mock_query.get.side_effect = lambda id: mock_faction
        
        handle_event_effects(event)
        
        # Check resource depletion
        assert mock_faction.resources['military'] < 100
        assert mock_faction.resources['gold'] < 1000

def test_handle_trade_effects(mock_region):
    """Test trade event effects."""
    event = Mock(spec=WorldEvent)
    event.data = {
        'region1_id': 1,
        'region2_id': 2,
        'terms': {
            'resource_exchanges': [
                {
                    'resource1': 'wood',
                    'resource2': 'iron'
                }
            ]
        }
    }
    
    with patch('app.models.region.Region.query') as mock_query:
        mock_query.get.side_effect = lambda id: mock_region
        
        handle_event_effects(event)
        
        # Check resource transfers and prosperity
        assert mock_region.prosperity > 50

def test_handle_festival_effects(mock_region):
    """Test festival event effects."""
    event = Mock(spec=WorldEvent)
    event.data = {
        'participating_regions': [1],
        'bonuses': {
            'prosperity': 0.2,
            'happiness': 0.3,
            'cultural_influence': 0.1
        },
        'special_events': ['grand_feast', 'trade_fair']
    }
    
    with patch('app.models.region.Region.query') as mock_query:
        mock_query.get.side_effect = lambda id: mock_region
        
        handle_event_effects(event)
        
        # Check bonuses applied
        assert mock_region.prosperity > 50
        assert mock_region.happiness > 50
        assert mock_region.cultural_influence > 50
        assert mock_region.food_production > 1.0
        assert mock_region.trade_income > 1.0

def test_handle_calamity_effects(mock_region):
    """Test calamity event effects."""
    event = Mock(spec=WorldEvent)
    event.data = {
        'affected_regions': [1],
        'severity': 0.5,
        'effects': {
            'population_impact': 0.1,
            'infrastructure_damage': 0.2,
            'resource_depletion': 0.15
        }
    }
    
    with patch('app.models.region.Region.query') as mock_query:
        mock_query.get.side_effect = lambda id: mock_region
        
        handle_event_effects(event)
        
        # Check negative effects
        assert mock_region.population < 1000
        assert mock_region.infrastructure_level < 1.0
        assert mock_region.resources['wood']['amount'] < 100

def test_handle_discovery_effects(mock_faction):
    """Test discovery event effects."""
    event = Mock(spec=WorldEvent)
    event.data = {
        'discoverer_faction_id': 1,
        'discovery_type': 'military_innovation',
        'breakthrough_level': 3,
        'benefits': {
            'efficiency_boost': 0.2
        },
        'requirements': {
            'research_cost': 100
        },
        'spread_chance': 0.3
    }
    
    with patch('app.models.faction.Faction.query') as mock_query:
        mock_query.get.side_effect = lambda id: mock_faction
        mock_query.all.return_value = [mock_faction]
        
        handle_event_effects(event)
        
        # Check technology benefits
        assert mock_faction.military_power > 1.0
        assert mock_faction.resources['research_points'] < 500

def test_handle_religious_effects(mock_region):
    """Test religious event effects."""
    event = Mock(spec=WorldEvent)
    event.data = {
        'affected_regions': [1],
        'event_type': 'new_doctrine',
        'intensity': 0.7,
        'effects': {
            'social_stability': 0.2,
            'cultural_change': 0.3,
            'faction_relations': 0.1
        },
        'duration_modifiers': {
            'fervor': 1.1,
            'resistance': 0.2
        }
    }
    
    with patch('app.models.region.Region.query') as mock_query:
        mock_query.get.side_effect = lambda id: mock_region
        
        handle_event_effects(event)
        
        # Check religious effects
        assert mock_region.stability > 50
        assert mock_region.cultural_influence > 50

def test_handle_event_completion():
    """Test event completion handling."""
    events = [
        Mock(spec=WorldEvent, type='war_declaration'),
        Mock(spec=WorldEvent, type='trade_agreement'),
        Mock(spec=WorldEvent, type='diplomatic_crisis'),
        Mock(spec=WorldEvent, type='global_festival'),
        Mock(spec=WorldEvent, type='natural_calamity'),
        Mock(spec=WorldEvent, type='technological_discovery'),
        Mock(spec=WorldEvent, type='religious_movement')
    ]
    
    for event in events:
        handle_event_completion(event)
        assert event.status == 'completed' 