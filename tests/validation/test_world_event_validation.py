"""Tests for world event validation."""

import pytest
from datetime import datetime, timedelta
from jsonschema import ValidationError
from app.validation.world_event_validation import (
    validate_event_data,
    validate_event_timing,
    validate_event_status,
    validate_affected_entities,
    validate_event_creation,
    validate_event_update,
    validate_event_completion
)

@pytest.fixture
def sample_entities():
    """Sample entities for testing."""
    return {
        'factions': [1, 2, 3],
        'regions': [1, 2, 3, 4, 5],
        'npcs': [1, 2, 3, 4]
    }

@pytest.fixture
def sample_war_data():
    """Sample war event data."""
    return {
        'aggressor_id': 1,
        'defender_id': 2,
        'initial_demands': {
            'territory': True,
            'resources': False,
            'vassalization': False
        }
    }

@pytest.fixture
def sample_trade_data():
    """Sample trade event data."""
    return {
        'region1_id': 1,
        'region2_id': 2,
        'terms': {
            'resource_exchanges': [
                {'resource1': 'iron', 'resource2': 'gold'}
            ]
        }
    }

@pytest.fixture
def sample_diplomatic_data():
    """Sample diplomatic event data."""
    return {
        'faction1_id': 1,
        'faction2_id': 2,
        'crisis_type': 'border_dispute',
        'severity': 0.7,
        'resolution_options': ['negotiate', 'threaten']
    }

@pytest.fixture
def sample_festival_data():
    """Sample festival event data."""
    return {
        'participating_regions': [1, 2, 3],
        'bonuses': {
            'prosperity': 0.2,
            'happiness': 0.3,
            'cultural_influence': 0.1
        },
        'special_events': ['feast', 'tournament']
    }

@pytest.fixture
def sample_calamity_data():
    """Sample calamity event data."""
    return {
        'affected_regions': [1, 2],
        'severity': 0.8,
        'effects': {
            'population_impact': -0.2,
            'infrastructure_damage': -0.3,
            'resource_depletion': -0.4
        }
    }

@pytest.fixture
def sample_discovery_data():
    """Sample discovery event data."""
    return {
        'discoverer_faction_id': 1,
        'discovery_type': 'metallurgy',
        'breakthrough_level': 3,
        'benefits': {'efficiency_boost': 0.2},
        'requirements': {'research_cost': 100},
        'spread_chance': 0.4
    }

@pytest.fixture
def sample_religious_data():
    """Sample religious event data."""
    return {
        'affected_regions': [1, 2, 3],
        'event_type': 'reformation',
        'intensity': 0.6,
        'effects': {
            'social_stability': -0.1,
            'cultural_change': 0.3,
            'faction_relations': -0.2
        },
        'duration_modifiers': {
            'fervor': 0.7,
            'resistance': 0.3
        }
    }

def test_validate_event_data_war():
    """Test war event data validation."""
    # Valid data
    valid_data = {
        'aggressor_id': 1,
        'defender_id': 2,
        'initial_demands': {'territory': True}
    }
    validate_event_data('war_declaration', valid_data)
    
    # Invalid data - missing required field
    invalid_data = {'aggressor_id': 1}
    with pytest.raises(ValidationError):
        validate_event_data('war_declaration', invalid_data)
        
    # Invalid data - wrong type
    invalid_data = {
        'aggressor_id': 'not_an_integer',
        'defender_id': 2
    }
    with pytest.raises(ValidationError):
        validate_event_data('war_declaration', invalid_data)

def test_validate_event_data_trade():
    """Test trade event data validation."""
    # Valid data
    valid_data = {
        'region1_id': 1,
        'region2_id': 2,
        'terms': {
            'resource_exchanges': [
                {'resource1': 'iron', 'resource2': 'gold'}
            ]
        }
    }
    validate_event_data('trade_agreement', valid_data)
    
    # Invalid data - missing terms
    invalid_data = {
        'region1_id': 1,
        'region2_id': 2
    }
    with pytest.raises(ValidationError):
        validate_event_data('trade_agreement', invalid_data)

def test_validate_event_timing():
    """Test event timing validation."""
    now = datetime.utcnow()
    
    # Valid timing
    validate_event_timing(now, now + timedelta(days=1))
    
    # Invalid timing - end before start
    with pytest.raises(ValidationError):
        validate_event_timing(now, now - timedelta(days=1))
        
    # Valid timing - no end time
    validate_event_timing(now, None)

def test_validate_event_status():
    """Test event status validation."""
    # Valid statuses
    validate_event_status('active')
    validate_event_status('completed')
    validate_event_status('cancelled')
    
    # Invalid status
    with pytest.raises(ValidationError):
        validate_event_status('invalid_status')

def test_validate_affected_entities(sample_entities):
    """Test affected entities validation."""
    # Valid war event
    war_data = {'aggressor_id': 1, 'defender_id': 2}
    validate_affected_entities('war_declaration', war_data, sample_entities)
    
    # Invalid war event - non-existent faction
    invalid_war_data = {'aggressor_id': 999, 'defender_id': 1}
    with pytest.raises(ValidationError):
        validate_affected_entities('war_declaration', invalid_war_data, sample_entities)
        
    # Valid festival event
    festival_data = {'participating_regions': [1, 2, 3]}
    validate_affected_entities('global_festival', festival_data, sample_entities)
    
    # Invalid festival event - non-existent region
    invalid_festival_data = {'participating_regions': [999]}
    with pytest.raises(ValidationError):
        validate_affected_entities('global_festival', invalid_festival_data, sample_entities)

def test_validate_event_creation(sample_entities, sample_war_data):
    """Test event creation validation."""
    now = datetime.utcnow()
    
    # Valid creation
    validate_event_creation(
        'war_declaration',
        sample_war_data,
        now,
        now + timedelta(days=30),
        'active',
        sample_entities
    )
    
    # Invalid creation - wrong status
    with pytest.raises(ValidationError):
        validate_event_creation(
            'war_declaration',
            sample_war_data,
            now,
            now + timedelta(days=30),
            'invalid_status',
            sample_entities
        )
        
    # Invalid creation - invalid timing
    with pytest.raises(ValidationError):
        validate_event_creation(
            'war_declaration',
            sample_war_data,
            now,
            now - timedelta(days=30),
            'active',
            sample_entities
        )

def test_validate_event_update(sample_entities, sample_war_data):
    """Test event update validation."""
    # Valid update
    old_data = sample_war_data.copy()
    new_data = {'initial_demands': {'resources': True}}
    validate_event_update('war_declaration', old_data, new_data, sample_entities)
    
    # Invalid update - invalid faction
    invalid_new_data = {'aggressor_id': 999}
    with pytest.raises(ValidationError):
        validate_event_update('war_declaration', old_data, invalid_new_data, sample_entities)

def test_validate_event_completion():
    """Test event completion validation."""
    # Valid war completion
    war_data = {
        'aggressor_id': 1,
        'defender_id': 2,
        'outcome': 'aggressor_victory'
    }
    validate_event_completion('war_declaration', war_data)
    
    # Invalid war completion - missing outcome
    invalid_war_data = {
        'aggressor_id': 1,
        'defender_id': 2
    }
    with pytest.raises(ValidationError):
        validate_event_completion('war_declaration', invalid_war_data)
        
    # Valid diplomatic crisis completion
    crisis_data = {
        'faction1_id': 1,
        'faction2_id': 2,
        'resolution': 'peaceful'
    }
    validate_event_completion('diplomatic_crisis', crisis_data)
    
    # Invalid diplomatic crisis completion - missing resolution
    invalid_crisis_data = {
        'faction1_id': 1,
        'faction2_id': 2
    }
    with pytest.raises(ValidationError):
        validate_event_completion('diplomatic_crisis', invalid_crisis_data)

def test_validate_complex_events(
    sample_entities,
    sample_trade_data,
    sample_diplomatic_data,
    sample_festival_data,
    sample_calamity_data,
    sample_discovery_data,
    sample_religious_data
):
    """Test validation of complex event types."""
    now = datetime.utcnow()
    
    # Test trade agreement
    validate_event_creation(
        'trade_agreement',
        sample_trade_data,
        now,
        now + timedelta(days=180),
        'active',
        sample_entities
    )
    
    # Test diplomatic crisis
    validate_event_creation(
        'diplomatic_crisis',
        sample_diplomatic_data,
        now,
        now + timedelta(days=30),
        'active',
        sample_entities
    )
    
    # Test festival
    validate_event_creation(
        'global_festival',
        sample_festival_data,
        now,
        now + timedelta(days=7),
        'active',
        sample_entities
    )
    
    # Test calamity
    validate_event_creation(
        'natural_calamity',
        sample_calamity_data,
        now,
        now + timedelta(days=14),
        'active',
        sample_entities
    )
    
    # Test discovery
    validate_event_creation(
        'technological_discovery',
        sample_discovery_data,
        now,
        now + timedelta(days=365),
        'active',
        sample_entities
    )
    
    # Test religious movement
    validate_event_creation(
        'religious_movement',
        sample_religious_data,
        now,
        now + timedelta(days=90),
        'active',
        sample_entities
    )

def test_edge_cases(sample_entities):
    """Test edge cases and boundary conditions."""
    now = datetime.utcnow()
    
    # Test minimum duration
    validate_event_timing(now, now + timedelta(seconds=1))
    
    # Test maximum severity
    calamity_data = {
        'affected_regions': [1],
        'severity': 1.0,
        'effects': {'population_impact': -1.0}
    }
    validate_event_data('natural_calamity', calamity_data)
    
    # Test invalid severity
    invalid_calamity_data = {
        'affected_regions': [1],
        'severity': 1.1,
        'effects': {'population_impact': -1.0}
    }
    with pytest.raises(ValidationError):
        validate_event_data('natural_calamity', invalid_calamity_data)
    
    # Test empty arrays
    festival_data = {
        'participating_regions': [],
        'bonuses': {
            'prosperity': 0.1
        }
    }
    validate_event_data('global_festival', festival_data)
    
    # Test null values
    discovery_data = {
        'discoverer_faction_id': 1,
        'discovery_type': 'metallurgy',
        'benefits': None
    }
    with pytest.raises(ValidationError):
        validate_event_data('technological_discovery', discovery_data) 