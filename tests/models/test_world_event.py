"""Tests for the WorldEvent model."""

import pytest
from datetime import datetime, timedelta
from app.models.world_event import WorldEvent

@pytest.fixture
def sample_event_data():
    """Create sample event data."""
    return {
        'type': 'war_declaration',
        'status': 'active',
        'end_time': (datetime.utcnow() + timedelta(days=30)).isoformat(),
        'data': {
            'aggressor_id': 1,
            'defender_id': 2,
            'initial_demands': {'territory': True}
        }
    }

def test_world_event_creation():
    """Test WorldEvent creation."""
    event = WorldEvent(
        type='war_declaration',
        status='active',
        end_time=datetime.utcnow() + timedelta(days=30),
        data={'aggressor_id': 1, 'defender_id': 2}
    )
    
    assert event.type == 'war_declaration'
    assert event.status == 'active'
    assert event.data == {'aggressor_id': 1, 'defender_id': 2}
    assert event.start_time is not None
    assert event.end_time is not None

def test_world_event_to_dict(sample_event_data):
    """Test conversion to dictionary."""
    event = WorldEvent.from_dict(sample_event_data)
    event_dict = event.to_dict()
    
    assert event_dict['type'] == sample_event_data['type']
    assert event_dict['status'] == sample_event_data['status']
    assert event_dict['data'] == sample_event_data['data']
    assert isinstance(event_dict['start_time'], str)
    assert isinstance(event_dict['end_time'], str)

def test_world_event_from_dict(sample_event_data):
    """Test creation from dictionary."""
    event = WorldEvent.from_dict(sample_event_data)
    
    assert event.type == sample_event_data['type']
    assert event.status == sample_event_data['status']
    assert event.data == sample_event_data['data']
    assert isinstance(event.start_time, datetime)
    assert isinstance(event.end_time, datetime)

def test_world_event_expiration():
    """Test event expiration."""
    # Create an expired event
    expired_event = WorldEvent(
        type='trade_agreement',
        end_time=datetime.utcnow() - timedelta(days=1)
    )
    assert expired_event.is_expired() is True
    
    # Create a future event
    future_event = WorldEvent(
        type='trade_agreement',
        end_time=datetime.utcnow() + timedelta(days=1)
    )
    assert future_event.is_expired() is False
    
    # Create an event with no end time
    endless_event = WorldEvent(type='trade_agreement')
    assert endless_event.is_expired() is False

def test_world_event_active_status():
    """Test active status checks."""
    # Active and not expired
    active_event = WorldEvent(
        type='diplomatic_crisis',
        status='active',
        end_time=datetime.utcnow() + timedelta(days=1)
    )
    assert active_event.is_active() is True
    
    # Active but expired
    expired_event = WorldEvent(
        type='diplomatic_crisis',
        status='active',
        end_time=datetime.utcnow() - timedelta(days=1)
    )
    assert expired_event.is_active() is False
    
    # Not active
    completed_event = WorldEvent(
        type='diplomatic_crisis',
        status='completed',
        end_time=datetime.utcnow() + timedelta(days=1)
    )
    assert completed_event.is_active() is False

def test_world_event_status_changes():
    """Test status change methods."""
    event = WorldEvent(type='global_festival')
    
    event.complete()
    assert event.status == 'completed'
    
    event = WorldEvent(type='global_festival')
    event.cancel()
    assert event.status == 'cancelled'

def test_world_event_duration_extension():
    """Test duration extension."""
    event = WorldEvent(
        type='natural_calamity',
        end_time=datetime.utcnow() + timedelta(days=7)
    )
    original_end = event.end_time
    
    event.extend(timedelta(days=3))
    assert event.end_time == original_end + timedelta(days=3)

def test_world_event_data_update():
    """Test data update method."""
    event = WorldEvent(
        type='technological_discovery',
        data={'discoverer_faction_id': 1}
    )
    
    event.update_data({'breakthrough_level': 3})
    assert event.data == {
        'discoverer_faction_id': 1,
        'breakthrough_level': 3
    }

def test_world_event_duration_calculations():
    """Test duration calculations."""
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=10)
    
    event = WorldEvent(
        type='religious_movement',
        end_time=end_time
    )
    
    # Test get_duration
    duration = event.get_duration()
    assert isinstance(duration, timedelta)
    assert duration.days == 10
    
    # Test get_remaining_time
    remaining = event.get_remaining_time()
    assert isinstance(remaining, timedelta)
    assert remaining.days <= 10
    
    # Test get_completion_percentage
    percentage = event.get_completion_percentage()
    assert isinstance(percentage, float)
    assert 0 <= percentage <= 100

def test_world_event_affected_entities():
    """Test affected entities retrieval."""
    # Test war declaration
    war_event = WorldEvent(
        type='war_declaration',
        data={'aggressor_id': 1, 'defender_id': 2}
    )
    war_affected = war_event.get_affected_entities()
    assert war_affected['factions'] == [1, 2]
    
    # Test trade agreement
    trade_event = WorldEvent(
        type='trade_agreement',
        data={'region1_id': 3, 'region2_id': 4}
    )
    trade_affected = trade_event.get_affected_entities()
    assert trade_affected['regions'] == [3, 4]
    
    # Test festival
    festival_event = WorldEvent(
        type='global_festival',
        data={'participating_regions': [5, 6, 7]}
    )
    festival_affected = festival_event.get_affected_entities()
    assert festival_affected['regions'] == [5, 6, 7]
    
    # Test discovery
    discovery_event = WorldEvent(
        type='technological_discovery',
        data={'discoverer_faction_id': 8}
    )
    discovery_affected = discovery_event.get_affected_entities()
    assert discovery_affected['factions'] == [8]

def test_world_event_null_handling():
    """Test handling of null values."""
    event = WorldEvent(type='diplomatic_crisis')
    
    # Test duration calculations with no end time
    assert event.get_duration() is None
    assert event.get_remaining_time() is None
    assert event.get_completion_percentage() is None
    
    # Test affected entities with missing data
    affected = event.get_affected_entities()
    assert all(len(entities) == 0 for entities in affected.values())
    
    # Test extend with no end time
    event.extend(timedelta(days=1))
    assert event.end_time is None

def test_world_event_edge_cases():
    """Test edge cases."""
    # Test very short duration
    short_event = WorldEvent(
        type='natural_calamity',
        end_time=datetime.utcnow() + timedelta(seconds=1)
    )
    assert short_event.get_completion_percentage() <= 100
    
    # Test very long duration
    long_event = WorldEvent(
        type='religious_movement',
        end_time=datetime.utcnow() + timedelta(days=3650)
    )
    assert long_event.get_completion_percentage() >= 0
    
    # Test data update with empty dict
    empty_event = WorldEvent(type='diplomatic_crisis')
    empty_event.update_data({})
    assert empty_event.data == {} 