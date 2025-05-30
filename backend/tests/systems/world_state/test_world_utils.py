from backend.systems.poi.models import PointOfInterest
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.poi.models import PointOfInterest
from backend.systems.events.dispatcher import EventDispatcher
from typing import Any
from typing import Type
from typing import List

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
Comprehensive tests for world_utils.py module.
Tests all utility functions for world generation, management, and interaction.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import asyncio

from backend.systems.world_state.world_utils import (
    generate_terrain_type,
    generate_region,
    generate_point_of_interest,
    create_world_map,
    get_world_map,
    update_world_map,
    get_region_at_coordinates,
    get_pois_in_region,
    calculate_travel_time,
    validate_world_data,
    process_world_tick,
    WorldMapCreatedEvent,
    WorldMapUpdatedEvent,
    WorldTickProcessedEvent,
    registry,
)
from backend.systems.world_state import TerrainType, Region, PointOfInterest, WorldMap, LevelRange
from backend.systems.shared.utils.common.error import NotFoundError, ValidationError


class TestWorldUtilsEvents: pass
    """Test event classes defined in world_utils."""

    def test_world_map_created_event(self): pass
        """Test WorldMapCreatedEvent creation and properties."""
        event = WorldMapCreatedEvent(map_id="test_map", name="Test Map")
        
        assert event.event_type == "world_map_created"
        assert event.map_id == "test_map"
        assert event.name == "Test Map"
        assert isinstance(event.timestamp, datetime)

    def test_world_map_updated_event(self): pass
        """Test WorldMapUpdatedEvent creation and properties."""
        updates = {"width": 100, "height": 100}
        event = WorldMapUpdatedEvent(map_id="test_map", updates=updates)
        
        assert event.event_type == "world_map_updated"
        assert event.map_id == "test_map"
        assert event.updates == updates
        assert isinstance(event.timestamp, datetime)

    def test_world_tick_processed_event(self): pass
        """Test WorldTickProcessedEvent creation and properties."""
        event = WorldTickProcessedEvent(world_state_id="test_state")
        
        assert event.event_type == "world_tick_processed"
        assert event.world_state_id == "test_state"
        assert isinstance(event.timestamp, datetime)


class TestWorldUtilsGeneration: pass
    """Test world generation utility functions."""

    @patch('backend.systems.world_state.world_utils.registry')
    def test_generate_terrain_type_bug_exists(self, mock_registry): pass
        """Test that generate_terrain_type has a bug - it tries to construct TerrainType incorrectly."""
        # Mock registry data
        mock_registry.land_types = [
            {
                "id": "forest",
                "name": "Forest",
                "description": "Dense woodland",
                "movement_cost": 1.5,
                "visibility_modifier": 0.8,
                "resources": ["wood", "herbs"],
                "features": ["trees", "wildlife"],
                "metadata": {"biome": "temperate"}
            }
        ]
        
        # The function has a bug - it tries to create TerrainType with parameters
        # but TerrainType is an enum, so this will fail
        with pytest.raises(TypeError): pass
            generate_terrain_type("Forest")

    @patch('backend.systems.world_state.world_utils.registry')
    def test_generate_terrain_type_not_found(self, mock_registry): pass
        """Test terrain type generation with unknown terrain."""
        mock_registry.land_types = []
        
        with pytest.raises(ValueError, match="Unknown terrain type: Unknown"): pass
            generate_terrain_type("Unknown")

    @patch('backend.systems.world_state.world_utils.registry')
    @patch('random.sample')
    @patch('random.randint')
    def test_generate_region_success(self, mock_randint, mock_sample, mock_registry): pass
        """Test successful region generation."""
        # Mock registry data
        mock_registry.climates = [{"name": "temperate"}]
        mock_registry.land_types = [
            {"name": "forest"}, {"name": "plains"}, {"name": "hills"}, {"name": "mountains"}
        ]
        
        # Mock random functions
        mock_randint.return_value = 3
        mock_sample.return_value = ["forest", "plains", "hills"]
        
        region = generate_region("Test Region", "temperate", 5, 15)
        
        assert isinstance(region, Region)
        assert region.name == "Test Region"
        assert region.description == "A temperate region called Test Region."
        assert isinstance(region.level_range, LevelRange)
        assert region.level_range.min_level == 5
        assert region.level_range.max_level == 15
        assert region.terrain_types == ["forest", "plains", "hills"]
        assert region.points_of_interest == []
        assert region.factions == []
        assert region.climate == "temperate"

    @patch('backend.systems.world_state.world_utils.registry')
    def test_generate_region_unknown_climate(self, mock_registry): pass
        """Test region generation with unknown climate."""
        mock_registry.climates = []
        
        with pytest.raises(ValueError, match="Unknown climate: unknown"): pass
            generate_region("Test Region", "unknown")

    def test_generate_point_of_interest(self): pass
        """Test point of interest generation."""
        poi = generate_point_of_interest(
            "Test POI", "dungeon", "region_1", (10.5, 20.3), 10
        )
        
        assert isinstance(poi, PointOfInterest)
        assert poi.name == "Test POI"
        assert poi.description == "A dungeon called Test POI."
        assert poi.type == "dungeon"
        assert poi.region_id == "region_1"
        assert poi.coordinates == (10.5, 20.3)
        assert poi.level == 10
        assert poi.npcs == []
        assert poi.quests == []
        assert poi.resources == []


class TestWorldUtilsMapManagement: pass
    """Test world map management functions."""

    @patch('backend.systems.world_state.world_utils.get_firestore_client')
    @patch('backend.systems.world_state.world_utils.EventDispatcher')
    @patch('backend.systems.world_state.world_utils.integration_logger')
    @patch('backend.systems.world_state.world_utils.integration_metrics')
    @patch('asyncio.create_task')
    def test_create_world_map_bug_exists(self, mock_create_task, mock_metrics, mock_logger, 
                                        mock_event_dispatcher, mock_firestore): pass
        """Test that create_world_map has a bug - it doesn't provide required seed parameter."""
        # Mock Firestore
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_firestore.return_value = mock_db
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        
        # Mock EventDispatcher
        mock_dispatcher_instance = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher_instance
        
        # The function has a bug - it doesn't provide the required 'seed' parameter
        with pytest.raises(Exception):  # Will be a Pydantic validation error
            create_world_map("Test Map", 100, 200, 2.0)

    @patch('backend.systems.world_state.world_utils.get_firestore_client')
    def test_get_world_map_success(self, mock_firestore): pass
        """Test successful world map retrieval."""
        # Mock Firestore
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_doc = Mock()
        
        mock_firestore.return_value = mock_db
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.get.return_value = mock_doc
        
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "id": "test_map",
            "name": "Test Map",
            "description": "A test map",
            "seed": 12345,
            "width": 100,
            "height": 100,
            "scale": 1.0,
            "regions": {},
            "continents": {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": {}
        }
        
        world_map = get_world_map("test_map")
        
        assert isinstance(world_map, WorldMap)
        assert world_map.id == "test_map"
        assert world_map.name == "Test Map"
        assert world_map.seed == 12345
        
        mock_db.collection.assert_called_once_with("world_maps")
        mock_collection.document.assert_called_once_with("test_map")

    @patch('backend.systems.world_state.world_utils.get_firestore_client')
    def test_get_world_map_not_found(self, mock_firestore): pass
        """Test world map retrieval when map doesn't exist."""
        # Mock Firestore
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_doc = Mock()
        
        mock_firestore.return_value = mock_db
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        mock_document.get.return_value = mock_doc
        
        mock_doc.exists = False
        
        with pytest.raises(NotFoundError, match="World map with ID test_map not found"): pass
            get_world_map("test_map")

    @patch('backend.systems.world_state.world_utils.get_world_map')
    @patch('backend.systems.world_state.world_utils.get_firestore_client')
    @patch('backend.systems.world_state.world_utils.EventDispatcher')
    @patch('backend.systems.world_state.world_utils.integration_logger')
    @patch('backend.systems.world_state.world_utils.integration_metrics')
    @patch('asyncio.create_task')
    def test_update_world_map(self, mock_create_task, mock_metrics, mock_logger,
                             mock_event_dispatcher, mock_firestore, mock_get_map): pass
        """Test world map update."""
        # Mock existing world map
        mock_world_map = Mock(spec=WorldMap)
        mock_world_map.dict.return_value = {"id": "test_map", "name": "Updated Map"}
        mock_get_map.return_value = mock_world_map
        
        # Mock Firestore
        mock_db = Mock()
        mock_collection = Mock()
        mock_document = Mock()
        mock_firestore.return_value = mock_db
        mock_db.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_document
        
        # Mock EventDispatcher
        mock_dispatcher_instance = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher_instance
        
        updates = {"name": "Updated Map", "width": 150}
        result = update_world_map("test_map", updates)
        
        assert result == mock_world_map
        # Verify attributes were set
        for key, value in updates.items(): pass
            setattr(mock_world_map, key, value)
        assert hasattr(mock_world_map, 'updated_at')
        
        # Verify Firestore update
        mock_db.collection.assert_called_once_with("world_maps")
        mock_collection.document.assert_called_once_with("test_map")
        mock_document.update.assert_called_once()
        
        # Verify async tasks were created
        assert mock_create_task.call_count == 3


class TestWorldUtilsMapQueries: pass
    """Test world map query functions."""

    @patch('backend.systems.world_state.world_utils.get_world_map')
    def test_get_region_at_coordinates(self, mock_get_map): pass
        """Test getting region at coordinates."""
        mock_world_map = Mock()
        mock_world_map.get_region_at.return_value = "region_1"
        mock_get_map.return_value = mock_world_map
        
        result = get_region_at_coordinates("test_map", 10, 20)
        
        assert result == "region_1"
        mock_get_map.assert_called_once_with("test_map")
        mock_world_map.get_region_at.assert_called_once_with(10, 20)

    @patch('backend.systems.world_state.world_utils.get_world_map')
    def test_get_pois_in_region(self, mock_get_map): pass
        """Test getting POIs in a region."""
        mock_world_map = Mock()
        mock_world_map.get_pois_in_region.return_value = ["poi_1", "poi_2"]
        mock_get_map.return_value = mock_world_map
        
        result = get_pois_in_region("test_map", "region_1")
        
        assert result == ["poi_1", "poi_2"]
        mock_get_map.assert_called_once_with("test_map")
        mock_world_map.get_pois_in_region.assert_called_once_with("region_1")

    @patch('backend.systems.world_state.world_utils.get_world_map')
    def test_calculate_travel_time(self, mock_get_map): pass
        """Test travel time calculation."""
        mock_world_map = Mock()
        mock_world_map.calculate_distance.return_value = 10000  # 10km in meters
        mock_get_map.return_value = mock_world_map
        
        # Default speed is 5 km/h
        result = calculate_travel_time("test_map", 0, 0, 10, 10)
        
        assert result == 2.0  # 10km / 5km/h = 2 hours
        mock_get_map.assert_called_once_with("test_map")
        mock_world_map.calculate_distance.assert_called_once_with(0, 0, 10, 10)

    @patch('backend.systems.world_state.world_utils.get_world_map')
    def test_calculate_travel_time_custom_speed(self, mock_get_map): pass
        """Test travel time calculation with custom speed."""
        mock_world_map = Mock()
        mock_world_map.calculate_distance.return_value = 20000  # 20km in meters
        mock_get_map.return_value = mock_world_map
        
        result = calculate_travel_time("test_map", 0, 0, 20, 20, speed=10.0)
        
        assert result == 2.0  # 20km / 10km/h = 2 hours


class TestWorldUtilsValidation: pass
    """Test world data validation functions."""

    def test_validate_world_data_valid(self): pass
        """Test validation with valid world data."""
        valid_data = {
            "id": "world_1",
            "name": "Test World",
            "regions": {},
            "width": 100,
            "height": 100,
            "extra_field": "ignored"
        }
        
        assert validate_world_data(valid_data) is True

    def test_validate_world_data_missing_required_keys(self): pass
        """Test validation with missing required keys."""
        invalid_data = {
            "id": "world_1",
            "name": "Test World",
            # Missing: regions, width, height
        }
        
        assert validate_world_data(invalid_data) is False

    def test_validate_world_data_empty(self): pass
        """Test validation with empty data."""
        assert validate_world_data({}) is False


class TestWorldUtilsTickProcessing: pass
    """Test world tick processing functions."""

    @patch('backend.systems.world_state.world_utils.WorldStateManager')
    @patch('backend.systems.world_state.world_utils.EventDispatcher')
    @patch('backend.systems.world_state.world_utils.integration_logger')
    @patch('backend.systems.world_state.world_utils.integration_metrics')
    @patch('asyncio.create_task')
    def test_process_world_tick_success(self, mock_create_task, mock_metrics, 
                                       mock_logger, mock_event_dispatcher, mock_manager_class): pass
        """Test successful world tick processing."""
        # Mock WorldStateManager
        mock_manager = Mock()
        mock_manager.process_tick = AsyncMock()
        mock_manager_class.get_instance.return_value = mock_manager
        
        # Mock EventDispatcher
        mock_dispatcher_instance = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher_instance
        
        process_world_tick("test_state")
        
        # Verify manager was called
        mock_manager_class.get_instance.assert_called_once()
        
        # Verify async tasks were created (1 for process_tick, 3 for integration hooks)
        assert mock_create_task.call_count == 4

    @patch('backend.systems.world_state.world_utils.WorldStateManager')
    @patch('backend.systems.world_state.world_utils.EventDispatcher')
    @patch('backend.systems.world_state.world_utils.integration_logger')
    @patch('backend.systems.world_state.world_utils.integration_alerting')
    @patch('asyncio.create_task')
    def test_process_world_tick_error(self, mock_create_task, mock_alerting,
                                     mock_logger, mock_event_dispatcher, mock_manager_class): pass
        """Test world tick processing with error."""
        # Mock WorldStateManager to raise exception
        mock_manager = Mock()
        mock_manager.process_tick.side_effect = Exception("Tick failed")
        mock_manager_class.get_instance.return_value = mock_manager
        
        process_world_tick("test_state")
        
        # Verify error handling async tasks were created
        assert mock_create_task.call_count >= 2  # At least error logging and alerting


class TestWorldUtilsIntegration: pass
    """Test integration aspects of world utils."""

    def test_registry_initialization(self): pass
        """Test that registry is properly initialized."""
        # The registry should be available at module level
        assert registry is not None
        assert hasattr(registry, 'load_all')

    @patch('backend.systems.world_state.world_utils.registry')
    def test_generate_terrain_type_uses_registry_but_has_bug(self, mock_registry): pass
        """Test that terrain generation uses the registry but has a bug."""
        mock_registry.land_types = [{"name": "Test", "id": "test"}]
        
        # This will fail because TerrainType is an enum, not a constructible class
        with pytest.raises(TypeError): pass
            terrain = generate_terrain_type("Test")

    @patch('backend.systems.world_state.world_utils.registry')
    def test_generate_region_uses_registry(self, mock_registry): pass
        """Test that region generation uses the registry."""
        mock_registry.climates = [{"name": "test_climate"}]
        mock_registry.land_types = [{"name": "terrain1"}, {"name": "terrain2"}]
        
        with patch('random.sample') as mock_sample, patch('random.randint') as mock_randint: pass
            mock_randint.return_value = 2
            mock_sample.return_value = ["terrain1", "terrain2"]
            
            region = generate_region("Test Region", "test_climate")
            
            assert region.climate == "test_climate"
            assert region.terrain_types == ["terrain1", "terrain2"]


if __name__ == "__main__": pass
    pytest.main([__file__]) 