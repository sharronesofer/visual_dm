from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
import pytest
import tempfile
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

# Safe imports with fallbacks
try:
    from backend.systems.region.models import (
        RegionSchema,
        RegionCreationSchema,
        CoordinateSchema,
        HexCoordinateSchema,
        RegionMetadata,
        ContinentMetadata
    )
except ImportError:
    # Create mock classes if not available
    class RegionSchema:
        pass
    
    class RegionCreationSchema:
        pass
    
    class CoordinateSchema:
        pass
    
    class HexCoordinateSchema:
        pass
    
    class RegionMetadata:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class ContinentMetadata:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

try:
    from backend.systems.region.repository import RegionRepository
except ImportError:
    class RegionRepository:
        pass

try:
    from backend.systems.region.service import RegionService
except ImportError:
    class RegionService:
        pass

try:
    from backend.systems.region.world_generator import WorldGenerator
except ImportError:
    class WorldGenerator:
        pass

try:
    from backend.systems.region.generators import RegionGenerator, ContinentGenerator
except ImportError:
    class RegionGenerator:
        pass
    
    class ContinentGenerator:
        pass

try:
    from backend.systems.region.models import Region, RegionType
except ImportError:
    class Region:
        pass
    
    class RegionType:
        pass

try:
    from backend.systems.data import GameDataRegistry
except ImportError:
    # Create mock if not available
    class GameDataRegistry:
        def __init__(self):
            pass
        
        def get_data(self, key):
            return {}
        
        def load_all(self):
            pass
        
        def get_raw_json_data(self, key):
            return {}

@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary directory for data files."""
    data_dir = tmp_path / "data"
    regions_dir = data_dir / "regions"
    region_maps_dir = data_dir / "region_maps"
    questlogs_dir = data_dir / "questlogs"
    
    regions_dir.mkdir(parents=True)
    region_maps_dir.mkdir(parents=True)
    questlogs_dir.mkdir(parents=True)
    
    return str(data_dir)

@pytest.fixture
def mock_game_data_registry():
    """Create a mock GameDataRegistry."""
    mock_registry = Mock(spec=GameDataRegistry)
    
    # Mock config data
    mock_registry.get_data.return_value = {
        "biomes": {
            "Plains": {"name": "Plains", "elevation_range": (0.2, 0.5), "humidity_range": (0.3, 0.6), "temperature_range": (0.4, 0.7)},
            "Forest": {"name": "Forest", "elevation_range": (0.3, 0.6), "humidity_range": (0.6, 0.9), "temperature_range": (0.3, 0.6)},
            "Desert": {"name": "Desert", "elevation_range": (0.1, 0.4), "humidity_range": (0.0, 0.3), "temperature_range": (0.7, 1.0)},
            "Mountain": {"name": "Mountain", "elevation_range": (0.7, 1.0), "humidity_range": (0.2, 0.5), "temperature_range": (0.2, 0.5)},
            "Water": {"name": "Water", "elevation_range": (0.0, 0.1), "humidity_range": (0.8, 1.0), "temperature_range": (0.3, 0.6)}
        },
        "adjacency_rules": {
            "rules": [
                {"biomes": ["Plains", "Forest"], "rule_type": "compatible"},
                {"biomes": ["Plains", "Desert"], "rule_type": "compatible"},
                {"biomes": ["Forest", "Mountain"], "rule_type": "compatible"},
                {"biomes": ["Desert", "Mountain"], "rule_type": "compatible"},
                {"biomes": ["Water", "Plains"], "rule_type": "compatible"},
                {"biomes": ["Water", "Forest"], "rule_type": "compatible"},
                {"biomes": ["Desert", "Forest"], "rule_type": "transition_needed", "transition": "Plains"},
                {"biomes": ["Water", "Desert"], "rule_type": "transition_needed", "transition": "Plains"}
            ]
        }
    }
    
    mock_registry.load_all = Mock()
    mock_registry.get_raw_json_data.return_value = mock_registry.get_data.return_value
    
    return mock_registry

@pytest.fixture
def mock_region_repository():
    """Create a mock RegionRepository."""
    mock_repo = Mock(spec=RegionRepository)
    
    # Mock data for regions
    regions = {
        "r_12345678": {
            "id": "r_12345678",
            "name": "Test Region 1",
            "continent_id": "c_87654321",
            "coordinates": {"x": 0, "y": 0},
            "biome": "Plains",
            "elevation": 0.3,
            "temperature": 0.5,
            "humidity": 0.4,
            "features": ["hill", "river"],
            "resources": {"wood": 0.8, "stone": 0.5, "food": 0.7},
            "pois": [
                {
                    "type": "city",
                    "coordinates": {"x": 0.1, "y": 0.1},
                    "size": 1.0,
                    "name": "Test City"
                }
            ],
            "created_at": "2023-01-01T00:00:00",
            "last_updated": "2023-01-01T00:00:00"
        },
        "r_23456789": {
            "id": "r_23456789",
            "name": "Test Region 2",
            "continent_id": "c_87654321",
            "coordinates": {"x": 1, "y": 0},
            "biome": "Forest",
            "elevation": 0.4,
            "temperature": 0.4,
            "humidity": 0.7,
            "features": ["dense_forest", "lake"],
            "resources": {"wood": 1.0, "stone": 0.3, "food": 0.5},
            "pois": [
                {
                    "type": "village",
                    "coordinates": {"x": 1.1, "y": 0.1},
                    "size": 0.5,
                    "name": "Test Village"
                }
            ],
            "created_at": "2023-01-01T00:00:00",
            "last_updated": "2023-01-01T00:00:00"
        }
    }
    
    # Mock the repository methods
    mock_repo.get_region_by_id = lambda region_id: regions.get(region_id)
    mock_repo.list_all_regions = lambda: list(regions.values())
    mock_repo.get_regions_by_continent = lambda continent_id: [
        region for region in regions.values() 
        if region.get("continent_id") == continent_id
    ]
    
    def mock_create_region(region_data):
        region_id = region_data.get("id", "r_new")
        regions[region_id] = region_data
        return region_data
    
    mock_repo.create_region = mock_create_region
    
    def mock_update_region(region_id, data):
        if region_id not in regions:
            return None
        regions[region_id] = {**regions[region_id], **data}
        return regions[region_id]
    
    mock_repo.update_region = mock_update_region
    mock_repo.delete_region = lambda region_id: region_id in regions
    
    # Mock map tiles
    mock_repo.get_region_map_tiles = lambda region_id: {
        "0,0": {"tags": ["plains"], "poi": None},
        "0,1": {"tags": ["plains", "hill"], "poi": None},
        "1,0": {"tags": ["plains"], "poi": "city"}
    }
    
    mock_repo.save_region_map_tiles = lambda region_id, tiles: True
    
    return mock_repo


@pytest.fixture
def sample_region_data():
    """Return sample region data for testing."""
    return {
        "id": "r_test123",
        "name": "Test Region",
        "continent_id": "c_test123",
        "coordinates": {"x": 2, "y": 3},
        "biome": "Plains",
        "elevation": 0.3,
        "temperature": 0.5,
        "humidity": 0.4,
        "features": ["hill", "river"],
        "resources": {"wood": 0.8, "stone": 0.5, "food": 0.7},
        "pois": [
            {
                "type": "city",
                "coordinates": {"x": 2.1, "y": 3.1},
                "size": 1.0,
                "name": "Test City"
            }
        ]
    }


@pytest.fixture
def sample_continent_metadata():
    """Return sample continent metadata for testing."""
    return ContinentMetadata(
        continent_id="c_test123",
        name="Test Continent",
        region_coordinates=[(0, 0), (1, 0), (0, 1)],
        region_ids=["r_12345678", "r_23456789", "r_34567890"],
        origin=(0, 0),
        boundary={"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1},
        seed=12345,
        created_at="2023-01-01T00:00:00"
    )


@pytest.fixture
def sample_region_metadata():
    """Return sample region metadata for testing."""
    return RegionMetadata(
        region_id="r_12345678",
        name="Test Region",
        continent_id="c_test123",
        coordinates=(0, 0),
        biome_type="Plains",
        elevation_profile=0.3,
        temperature_profile=0.5,
        humidity_profile=0.4,
        resource_potentials={"wood": 0.8, "stone": 0.5, "food": 0.7},
        poi_data=[
            {"type": "city", "coordinates": (0.1, 0.1), "size": 1.0, "name": "Test City"}
        ],
        generated_features=["hill", "river"],
        seed=12345
    )


@pytest.fixture
def mock_world_generator(mock_game_data_registry, mock_region_repository):
    """Create a mock WorldGenerator."""
    with patch("backend.systems.region.worldgen.WorldGenerator", autospec=True) as MockWorldGen:
        mock_generator = MockWorldGen.return_value
        
        # Set up continents attribute
        continent_metadata = ContinentMetadata(
            continent_id="c_87654321",
            name="Test Continent",
            region_coordinates=[(0, 0), (1, 0)],
            region_ids=["r_12345678", "r_23456789"],
            origin=(0, 0),
            boundary={"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 0},
            seed=12345,
            created_at="2023-01-01T00:00:00"
        )
        
        mock_generator.continents = {"c_87654321": continent_metadata}
        mock_generator.world_metadata = {
            "seed": 12345,
            "continent_count": 1,
            "region_count": 2,
            "continents": ["c_87654321"],
            "generated_at": "2023-01-01T00:00:00"
        }
        
        # Mock methods
        mock_generator.generate_world.return_value = {
            "seed": 12345,
            "continent_count": 1,
            "region_count": 2,
            "continents": ["c_87654321"]
        }
        
        mock_generator.load_world_data.return_value = {
            "seed": 12345,
            "continent_count": 1,
            "region_count": 2,
            "continents": ["c_87654321"]
        }
        
        mock_generator.get_continent_by_id.return_value = continent_metadata
        
        mock_generator.get_regions_by_continent.return_value = [
            RegionMetadata(
                region_id="r_12345678",
                name="Test Region 1",
                continent_id="c_87654321",
                coordinates=(0, 0),
                biome_type="Plains",
                elevation_profile=0.3,
                temperature_profile=0.5,
                humidity_profile=0.4,
                resource_potentials={"wood": 0.8, "stone": 0.5, "food": 0.7},
                poi_data=[
                    {"type": "city", "coordinates": (0.1, 0.1), "size": 1.0, "name": "Test City"}
                ],
                generated_features=["hill", "river"],
                seed=12345
            ),
            RegionMetadata(
                region_id="r_23456789",
                name="Test Region 2",
                continent_id="c_87654321",
                coordinates=(1, 0),
                biome_type="Forest",
                elevation_profile=0.4,
                temperature_profile=0.4,
                humidity_profile=0.7,
                resource_potentials={"wood": 1.0, "stone": 0.3, "food": 0.5},
                poi_data=[
                    {"type": "village", "coordinates": (1.1, 0.1), "size": 0.5, "name": "Test Village"}
                ],
                generated_features=["dense_forest", "lake"],
                seed=12345
            )
        ]
        
        # Set up continent_generator
        mock_generator.continent_generator = Mock()
        mock_generator.continent_generator.get_continent_area.return_value = 150.0
        mock_generator.continent_generator.get_continent_dimensions.return_value = {
            "width": 10, "height": 15
        }
        
        return mock_generator


@pytest.fixture
def mock_region_service(mock_world_generator, mock_game_data_registry):
    """Create a mock RegionService with mocked components."""
    with patch("backend.systems.region.service.RegionService", autospec=True) as MockService:
        service = MockService.return_value
        service.world_generator = mock_world_generator
        service.data_registry = mock_game_data_registry
        service.world_initialized = True
        
        # Set up method return values
        service.initialize.return_value = {
            "status": "success",
            "message": "Loaded existing world data",
            "world_data": mock_world_generator.load_world_data.return_value
        }
        
        service.get_world_metadata.return_value = {
            "status": "success",
            "metadata": mock_world_generator.world_metadata
        }
        
        service.get_all_continents.return_value = {
            "status": "success",
            "continents": [
                {
                    "continent_id": "c_87654321",
                    "name": "Test Continent",
                    "region_count": 2,
                    "boundary": {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 0},
                    "area_sqkm": 150.0
                }
            ]
        }
        
        service.get_continent.return_value = {
            "status": "success",
            "continent": {
                "continent_id": "c_87654321",
                "name": "Test Continent",
                "region_count": 2,
                "boundary": {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 0},
                "area_sqkm": 150.0,
                "dimensions": {"width": 10, "height": 15},
                "region_coordinates": [(0, 0), (1, 0)],
                "biome_distribution": {"Plains": 1, "Forest": 1}
            }
        }
        
        return service 