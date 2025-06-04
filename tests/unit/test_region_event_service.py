"""
Unit tests for Region Event Business Service
Tests event creation and management logic
"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime
from unittest.mock import Mock

from backend.systems.region.services.event_service import RegionEventBusinessService
from backend.systems.region.models import RegionMetadata, RegionProfile, ClimateType, DangerLevel


@pytest.fixture
def sample_region():
    """Create a sample region for testing"""
    return RegionMetadata(
        id=uuid4(),
        name="Test Region",
        description="A test region",
        region_type="wilderness",
        profile=RegionProfile(
            dominant_biome="temperate_forest",
            climate=ClimateType.TEMPERATE,
            soil_fertility=0.7,
            water_availability=0.8,
            precipitation=600.0,
            humidity=0.6,
            elevation=100.0
        ),
        population=1000,
        hex_coordinates=[],
        danger_level=DangerLevel.SAFE,
        continent_id=uuid4()
    )


@pytest.fixture
def event_service():
    """Create event service instance"""
    return RegionEventBusinessService()


class TestRegionEventBusinessService:
    """Test RegionEventBusinessService event creation"""
    
    def test_create_region_created_event(self, event_service, sample_region):
        """Test creation of region_created event"""
        event = event_service.create_region_created_event(sample_region)
        
        assert event["event_type"] == "region_created"
        assert event["region_id"] == str(sample_region.id)
        assert event["region_name"] == sample_region.name
        assert event["region_type"] == sample_region.region_type
        assert event["dominant_biome"] == sample_region.profile.dominant_biome
        assert event["climate"] == sample_region.profile.climate.value
        assert event["population"] == sample_region.population
        assert event["continent_id"] == str(sample_region.continent_id)
        assert "timestamp" in event
        assert isinstance(event["timestamp"], datetime)
    
    def test_create_region_updated_event(self, event_service, sample_region):
        """Test creation of region_updated event"""
        event = event_service.create_region_updated_event(sample_region)
        
        assert event["event_type"] == "region_updated"
        assert event["region_id"] == str(sample_region.id)
        assert event["region_name"] == sample_region.name
        assert "timestamp" in event
        assert isinstance(event["timestamp"], datetime)
    
    def test_create_region_deleted_event(self, event_service):
        """Test creation of region_deleted event"""
        region_id = uuid4()
        event = event_service.create_region_deleted_event(region_id)
        
        assert event["event_type"] == "region_deleted"
        assert event["region_id"] == str(region_id)
        assert "timestamp" in event
        assert isinstance(event["timestamp"], datetime)
    
    def test_create_territory_claimed_event(self, event_service):
        """Test creation of territory_claimed event"""
        region_id = uuid4()
        character_id = uuid4()
        
        event = event_service.create_territory_claimed_event(
            region_id=region_id,
            character_id=character_id,
            territory_name="New Territory"
        )
        
        assert event["event_type"] == "territory_claimed"
        assert event["region_id"] == str(region_id)
        assert event["character_id"] == str(character_id)
        assert event["territory_name"] == "New Territory"
        assert "timestamp" in event
    
    def test_create_resource_discovered_event(self, event_service):
        """Test creation of resource_discovered event"""
        region_id = uuid4()
        
        event = event_service.create_resource_discovered_event(
            region_id=region_id,
            resource_type="iron_ore",
            quantity=100,
            quality="high"
        )
        
        assert event["event_type"] == "resource_discovered"
        assert event["region_id"] == str(region_id)
        assert event["resource_type"] == "iron_ore"
        assert event["quantity"] == 100
        assert event["quality"] == "high"
        assert "timestamp" in event
    
    def test_create_environmental_change_event(self, event_service):
        """Test creation of environmental_change event"""
        region_id = uuid4()
        
        event = event_service.create_environmental_change_event(
            region_id=region_id,
            change_type="climate_shift",
            old_value="temperate",
            new_value="arid",
            cause="magical_influence"
        )
        
        assert event["event_type"] == "environmental_change"
        assert event["region_id"] == str(region_id)
        assert event["change_type"] == "climate_shift"
        assert event["old_value"] == "temperate"
        assert event["new_value"] == "arid"
        assert event["cause"] == "magical_influence"
        assert "timestamp" in event
    
    def test_create_character_entered_region_event(self, event_service):
        """Test creation of character_entered_region event"""
        region_id = uuid4()
        character_id = uuid4()
        
        event = event_service.create_character_entered_region_event(
            region_id=region_id,
            character_id=character_id,
            character_name="Test Character"
        )
        
        assert event["event_type"] == "character_entered_region"
        assert event["region_id"] == str(region_id)
        assert event["character_id"] == str(character_id)
        assert event["character_name"] == "Test Character"
        assert "timestamp" in event
    
    def test_create_world_generation_event(self, event_service):
        """Test creation of world_generation event"""
        event = event_service.create_world_generation_event(
            generation_type="new_continent",
            seed="test_seed_123",
            parameters={"size": "large", "climate": "varied"}
        )
        
        assert event["event_type"] == "world_generation"
        assert event["generation_type"] == "new_continent"
        assert event["seed"] == "test_seed_123"
        assert event["parameters"]["size"] == "large"
        assert event["parameters"]["climate"] == "varied"
        assert "timestamp" in event
    
    def test_add_event_to_history(self, event_service, sample_region):
        """Test adding events to local history"""
        # Initially, history should be empty
        assert len(event_service.event_history) == 0
        
        # Create and add event
        event = event_service.create_region_created_event(sample_region)
        assert len(event_service.event_history) == 1
        assert event_service.event_history[0] == event
    
    def test_get_event_history_all(self, event_service, sample_region):
        """Test getting all event history"""
        # Create multiple events
        event1 = event_service.create_region_created_event(sample_region)
        event2 = event_service.create_region_updated_event(sample_region)
        
        history = event_service.get_event_history()
        assert len(history) == 2
        assert event1 in history
        assert event2 in history
    
    def test_get_event_history_filtered(self, event_service, sample_region):
        """Test getting filtered event history"""
        # Create different types of events
        region_id = sample_region.id
        event_service.create_region_created_event(sample_region)
        event_service.create_region_updated_event(sample_region)
        event_service.create_territory_claimed_event(region_id, uuid4(), "Territory")
        
        # Filter by event type
        created_events = event_service.get_event_history(event_type="region_created")
        assert len(created_events) == 1
        assert created_events[0]["event_type"] == "region_created"
        
        # Filter by region ID
        region_events = event_service.get_event_history(region_id=region_id)
        assert len(region_events) == 3  # All events are for this region
        
        # Filter by both
        specific_events = event_service.get_event_history(
            event_type="territory_claimed",
            region_id=region_id
        )
        assert len(specific_events) == 1
        assert specific_events[0]["event_type"] == "territory_claimed"
    
    def test_get_event_history_with_limit(self, event_service, sample_region):
        """Test event history pagination"""
        # Create multiple events
        for _ in range(5):
            event_service.create_region_created_event(sample_region)
        
        # Test limit
        limited_history = event_service.get_event_history(limit=3)
        assert len(limited_history) == 3
        
        # Test limit greater than available
        all_history = event_service.get_event_history(limit=10)
        assert len(all_history) == 5
    
    def test_event_history_size_management(self, event_service, sample_region):
        """Test that event history doesn't grow beyond limit"""
        max_size = event_service.max_history_size
        
        # Create more events than the max size
        for i in range(max_size + 10):
            event_service.create_region_created_event(sample_region)
        
        # History should be limited to max_size
        assert len(event_service.event_history) == max_size
        
        # Oldest events should be removed (FIFO)
        history = event_service.get_event_history()
        assert len(history) == max_size
    
    def test_event_timestamps_are_recent(self, event_service, sample_region):
        """Test that event timestamps are created correctly"""
        before_creation = datetime.now()
        event = event_service.create_region_created_event(sample_region)
        after_creation = datetime.now()
        
        # Timestamp should be between before and after
        assert before_creation <= event["timestamp"] <= after_creation
    
    def test_event_structure_consistency(self, event_service, sample_region):
        """Test that all events have consistent base structure"""
        events = [
            event_service.create_region_created_event(sample_region),
            event_service.create_region_updated_event(sample_region),
            event_service.create_region_deleted_event(sample_region.id),
            event_service.create_territory_claimed_event(sample_region.id, uuid4(), "Territory"),
            event_service.create_resource_discovered_event(sample_region.id, "gold", 50, "high"),
            event_service.create_environmental_change_event(sample_region.id, "test", "old", "new", "magic"),
            event_service.create_character_entered_region_event(sample_region.id, uuid4(), "Character"),
            event_service.create_world_generation_event("test", "seed", {})
        ]
        
        # All events should have these base fields
        for event in events:
            assert "event_type" in event
            assert "timestamp" in event
            assert isinstance(event["timestamp"], datetime)
            assert isinstance(event["event_type"], str)
    
    def test_region_events_have_region_id(self, event_service, sample_region):
        """Test that region-specific events have region_id"""
        region_events = [
            event_service.create_region_created_event(sample_region),
            event_service.create_region_updated_event(sample_region),
            event_service.create_region_deleted_event(sample_region.id),
            event_service.create_territory_claimed_event(sample_region.id, uuid4(), "Territory"),
            event_service.create_resource_discovered_event(sample_region.id, "gold", 50, "high"),
            event_service.create_environmental_change_event(sample_region.id, "test", "old", "new", "magic"),
            event_service.create_character_entered_region_event(sample_region.id, uuid4(), "Character")
        ]
        
        for event in region_events:
            assert "region_id" in event
            assert event["region_id"] == str(sample_region.id)
    
    def test_clear_event_history(self, event_service, sample_region):
        """Test clearing event history"""
        # Add some events
        event_service.create_region_created_event(sample_region)
        event_service.create_region_updated_event(sample_region)
        
        assert len(event_service.event_history) == 2
        
        # Clear history
        event_service.clear_event_history()
        assert len(event_service.event_history) == 0
        
        # New events should still work
        event_service.create_region_created_event(sample_region)
        assert len(event_service.event_history) == 1 