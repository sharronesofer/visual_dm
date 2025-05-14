"""Tests for the WorldState class."""

import pytest
from datetime import datetime, timedelta
from app.core.models.world_state import WorldState
from app.core.models.time_system import TimeSystem, TimeEvent, TimeScale
from app.core.models.season_system import SeasonSystem
from app.core.models.weather_system import WeatherSystem
from app.core.models.npc_activity_system import NPCActivitySystem
from app.core.enums import TimeOfDay, Season, Weather
from app.utils.constants import SEASON_DURATION, WEATHER_CHANGE_INTERVAL

@pytest.fixture
def world_state():
    """Create a fresh WorldState instance for each test."""
    return WorldState()

def test_world_state_initialization(world_state):
    """Test that WorldState initializes all systems properly."""
    assert world_state.time_system is not None
    assert world_state.season_system is not None
    assert world_state.weather_system is not None
    assert world_state.npc_activity_system is not None
    assert world_state.current_time is not None
    assert world_state.time_scale == TimeScale.NORMAL

def test_time_progression(world_state):
    """Test that time progresses correctly and affects all systems."""
    initial_time = world_state.current_time
    initial_season = world_state.current_season
    initial_weather = world_state.current_weather
    
    # Progress time by 1 game day
    world_state.update(timedelta(days=1))
    
    assert world_state.current_time > initial_time
    assert world_state.time_system.get_time_of_day() is not None
    
    # Verify systems were updated
    assert world_state.season_system.last_update == world_state.current_time
    assert world_state.weather_system.last_update == world_state.current_time
    assert world_state.npc_activity_system.last_update == world_state.current_time

def test_season_transitions(world_state):
    """Test that seasons change appropriately."""
    initial_season = world_state.current_season
    
    # Progress time by one season
    world_state.update(SEASON_DURATION)
    
    assert world_state.current_season != initial_season
    # Verify season affects weather probabilities
    assert world_state.weather_system.get_weather_probabilities() != {}

def test_weather_changes(world_state):
    """Test weather system integration."""
    initial_weather = world_state.current_weather
    
    # Progress time to trigger weather change
    world_state.update(WEATHER_CHANGE_INTERVAL)
    
    # Weather might or might not change, but system should update
    assert world_state.weather_system.last_update == world_state.current_time
    assert world_state.current_weather is not None

def test_npc_activities(world_state):
    """Test NPC activity system integration."""
    # Add test NPCs
    npc_ids = ["npc1", "npc2"]
    for npc_id in npc_ids:
        world_state.npc_activity_system.add_npc(npc_id)
    
    # Progress time to trigger NPC updates
    world_state.update(timedelta(hours=1))
    
    # Verify NPCs were updated
    for npc_id in npc_ids:
        npc_state = world_state.npc_activity_system.get_npc_state(npc_id)
        assert npc_state is not None
        assert npc_state.last_update == world_state.current_time

def test_event_handling(world_state):
    """Test event system integration."""
    # Add test event
    event_data = {"type": "test_event", "target": "npc1"}
    event_time = world_state.current_time + timedelta(hours=1)
    event_id = world_state.add_event(
        event_type="test",
        trigger_time=event_time,
        data=event_data
    )
    
    # Verify event was added
    assert event_id in world_state.get_pending_events()
    
    # Progress time to trigger event
    world_state.update(timedelta(hours=1))
    
    # Verify event was processed
    assert event_id not in world_state.get_pending_events()
    assert event_id in world_state.get_completed_events()

def test_recurring_events(world_state):
    """Test recurring event handling."""
    event_data = {"type": "recurring_test", "target": "npc1"}
    event_time = world_state.current_time + timedelta(hours=1)
    event_id = world_state.add_event(
        event_type="test",
        trigger_time=event_time,
        data=event_data,
        recurring=True,
        recurrence_interval=timedelta(hours=2)
    )
    
    # Progress time through multiple recurrences
    for _ in range(3):
        world_state.update(timedelta(hours=2))
        # Event should still be pending due to recurrence
        assert event_id in world_state.get_pending_events()

def test_state_persistence(world_state):
    """Test state serialization and deserialization."""
    # Set up initial state
    world_state.update(timedelta(days=1))
    initial_state = world_state.to_dict()
    
    # Create new instance from state
    new_world_state = WorldState.from_dict(initial_state)
    
    # Verify state was restored correctly
    assert new_world_state.current_time == world_state.current_time
    assert new_world_state.current_season == world_state.current_season
    assert new_world_state.current_weather == world_state.current_weather
    assert len(new_world_state.get_pending_events()) == len(world_state.get_pending_events())

def test_system_interactions(world_state):
    """Test interactions between different systems."""
    # Add test NPC
    npc_id = "test_npc"
    world_state.npc_activity_system.add_npc(npc_id)
    
    # Progress through different times of day
    for _ in range(24):
        world_state.update(timedelta(hours=1))
        npc_state = world_state.npc_activity_system.get_npc_state(npc_id)
        
        # Verify NPC behavior is affected by time of day
        current_time_of_day = world_state.time_system.get_time_of_day()
        assert npc_state.current_activity is not None
        
        # Verify weather affects NPC behavior
        current_weather = world_state.current_weather
        if current_weather in [Weather.RAIN, Weather.STORM]:
            assert "INDOORS" in npc_state.current_activity.upper()

def test_error_handling(world_state):
    """Test error handling in WorldState."""
    # Test invalid time scale
    with pytest.raises(ValueError):
        world_state.set_time_scale(-1.0)
    
    # Test invalid event data
    with pytest.raises(ValueError):
        world_state.add_event(
            event_type="test",
            trigger_time=world_state.current_time - timedelta(hours=1),  # Past time
            data={}
        )
    
    # Test invalid recurring event
    with pytest.raises(ValueError):
        world_state.add_event(
            event_type="test",
            trigger_time=world_state.current_time + timedelta(hours=1),
            data={},
            recurring=True,  # Recurring but no interval
            recurrence_interval=None
        )

def test_performance(world_state):
    """Test performance with many entities and events."""
    # Add many NPCs
    for i in range(100):
        world_state.npc_activity_system.add_npc(f"npc_{i}")
    
    # Add many events
    for i in range(100):
        world_state.add_event(
            event_type="test",
            trigger_time=world_state.current_time + timedelta(hours=i),
            data={"type": "test_event", "target": f"npc_{i}"}
        )
    
    # Measure time for update
    import time
    start_time = time.time()
    world_state.update(timedelta(days=1))
    end_time = time.time()
    
    # Update should complete in reasonable time (adjust threshold as needed)
    assert end_time - start_time < 1.0  # Should complete in less than 1 second 