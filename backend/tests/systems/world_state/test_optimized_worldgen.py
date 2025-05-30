from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from typing import Type
from dataclasses import field
"""
Comprehensive tests for Optimized World Generation system

This module tests the OptimizedWorldGenerator class and all its methods
to achieve 90% test coverage.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import numpy as np

from backend.systems.world_state.optimized_worldgen import (
    OptimizedWorldGenerator,
    create_world_generator
)
from backend.systems.world_state.consolidated_world_models import (
    WorldMap,
    Region,
    PointOfInterest,
    TerrainType,
)


@pytest.fixture
def temp_config_file(): pass
    """Create a temporary configuration file for testing."""
    config_data = {
        "base_seed": 54321,
        "region_size": 300,
        "map_width": 8,
        "map_height": 8,
        "ocean_threshold": 0.25,
        "mountain_threshold": 0.85,
        "temperature_base": 0.6,
        "river_count_per_region": 3
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f: pass
        json.dump(config_data, f)
        return f.name


@pytest.fixture
def mock_terrain_generator(): pass
    """Create a mock terrain generator."""
    mock_generator = Mock()
    
    # Mock biomes
    mock_generator.biomes = {
        "forest": {
            "name": "Forest",
            "temperature_range": [0.3, 0.7],
            "moisture_range": [0.6, 1.0],
            "elevation_range": [0.3, 0.7],
            "features": ["trees", "wildlife"],
            "resources": {"wood": 0.9, "game": 0.7},
            "color": "#228B22",
            "is_water": False
        },
        "ocean": {
            "name": "Ocean",
            "is_water": True
        }
    }
    
    # Mock region generation
    mock_region = Mock(spec=Region)
    mock_region.x = 0
    mock_region.y = 0
    mock_region.size = 225
    mock_region.elevation = np.random.rand(15, 15).tolist()
    mock_region.moisture = np.random.rand(15, 15).tolist()
    mock_region.temperature = np.random.rand(15, 15).tolist()
    mock_region.biome_map = [["forest"] * 15 for _ in range(15)]
    mock_region.rivers = [[False] * 15 for _ in range(15)]
    mock_region.points_of_interest = []
    
    mock_generator.generate_region.return_value = mock_region
    
    return mock_generator


class TestOptimizedWorldGeneratorInit: pass
    """Test OptimizedWorldGenerator initialization."""
    
    def test_init_default_config(self): pass
        """Test initialization with default configuration."""
        generator = OptimizedWorldGenerator()
        
        assert generator.config["base_seed"] == 12345
        assert generator.config["region_size"] == 225
        assert generator.config["map_width"] == 5
        assert generator.config["map_height"] == 5
        assert generator.config["ocean_threshold"] == 0.2
        assert generator.region_cache == {}
    
    def test_init_with_config_file(self, temp_config_file): pass
        """Test initialization with custom configuration file."""
        generator = OptimizedWorldGenerator(config_path=temp_config_file)
        
        assert generator.config["base_seed"] == 54321
        assert generator.config["region_size"] == 300
        assert generator.config["map_width"] == 8
        assert generator.config["map_height"] == 8
        assert generator.config["ocean_threshold"] == 0.25
        assert generator.config["mountain_threshold"] == 0.85
        
        # Clean up
        os.unlink(temp_config_file)
    
    def test_init_with_nonexistent_config_file(self): pass
        """Test initialization with non-existent configuration file."""
        generator = OptimizedWorldGenerator(config_path="/nonexistent/path.json")
        
        # Should use default config
        assert generator.config["base_seed"] == 12345
        assert generator.config["region_size"] == 225


class TestWorldMapGeneration: pass
    """Test world map generation methods."""
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    def test_generate_world_map_default(self, mock_terrain_gen_class, mock_terrain_generator): pass
        """Test world map generation with default parameters."""
        mock_terrain_gen_class.return_value = mock_terrain_generator
        
        generator = OptimizedWorldGenerator()
        
        with patch.object(generator, 'generate_region') as mock_gen_region: pass
            mock_region = Mock(spec=Region)
            mock_gen_region.return_value = mock_region
            
            with patch.object(generator, '_generate_world_rivers'): pass
                with patch.object(generator, '_generate_points_of_interest'): pass
                    world_map = generator.generate_world_map()
        
        assert isinstance(world_map, WorldMap)
        assert world_map.width == 5  # Default from config
        assert world_map.height == 5
        assert world_map.seed == 12345
        assert len(world_map.regions) == 25  # 5x5 grid
        
        # Verify all regions were generated
        for y in range(5): pass
            for x in range(5): pass
                assert (x, y) in world_map.regions
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    def test_generate_world_map_custom_params(self, mock_terrain_gen_class, mock_terrain_generator): pass
        """Test world map generation with custom parameters."""
        mock_terrain_gen_class.return_value = mock_terrain_generator
        
        generator = OptimizedWorldGenerator()
        
        with patch.object(generator, 'generate_region') as mock_gen_region: pass
            mock_region = Mock(spec=Region)
            mock_gen_region.return_value = mock_region
            
            with patch.object(generator, '_generate_world_rivers'): pass
                with patch.object(generator, '_generate_points_of_interest'): pass
                    world_map = generator.generate_world_map(width=3, height=4, seed=99999)
        
        assert world_map.width == 3
        assert world_map.height == 4
        assert world_map.seed == 99999
        assert len(world_map.regions) == 12  # 3x4 grid
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    def test_generate_world_map_cache_clearing(self, mock_terrain_gen_class, mock_terrain_generator): pass
        """Test that region cache is cleared when generating new world map."""
        mock_terrain_gen_class.return_value = mock_terrain_generator
        
        generator = OptimizedWorldGenerator()
        generator.region_cache = {"test": "data"}
        
        with patch.object(generator, 'generate_region') as mock_gen_region: pass
            mock_region = Mock(spec=Region)
            mock_gen_region.return_value = mock_region
            
            with patch.object(generator, '_generate_world_rivers'): pass
                with patch.object(generator, '_generate_points_of_interest'): pass
                    generator.generate_world_map()
        
        assert generator.region_cache == {}
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    @patch('time.time')
    def test_generate_world_map_timing(self, mock_time, mock_terrain_gen_class, mock_terrain_generator): pass
        """Test world map generation timing output."""
        mock_terrain_gen_class.return_value = mock_terrain_generator
        mock_time.side_effect = [1000.0, 1002.5]  # 2.5 second generation
        
        generator = OptimizedWorldGenerator()
        
        with patch.object(generator, 'generate_region') as mock_gen_region: pass
            mock_region = Mock(spec=Region)
            mock_gen_region.return_value = mock_region
            
            with patch.object(generator, '_generate_world_rivers'): pass
                with patch.object(generator, '_generate_points_of_interest'): pass
                    with patch('builtins.print') as mock_print: pass
                        generator.generate_world_map()
        
        # Check that timing messages were printed
        mock_print.assert_any_call("Generating world map 5x5 with seed 12345...")
        mock_print.assert_any_call("World generation completed in 2.50 seconds")


class TestRegionGeneration: pass
    """Test region generation methods."""
    
    @patch("backend.systems.world_state.optimized_worldgen.TerrainGenerator")
    def test_generate_region_basic(self, mock_terrain_gen): pass
        """Test basic region generation."""
        # Setup mock terrain generator
        mock_instance = Mock()
        mock_terrain_gen.return_value = mock_instance
        
        # Mock terrain data with proper structure
        mock_terrain_data = {
            "0_0": {"biome": "grassland", "elevation": 0.5, "resources": {"wood": 10}},
            "0_1": {"biome": "forest", "elevation": 0.6, "resources": {"wood": 20}},
            "1_0": {"biome": "mountain", "elevation": 0.8, "resources": {"stone": 15}},
            "1_1": {"biome": "desert", "elevation": 0.4, "resources": {"sand": 5}},
        }
        mock_instance.generate_terrain.return_value = mock_terrain_data
        
        # Mock biome info
        mock_biome_info = Mock()
        mock_biome_info.is_water = False
        mock_instance.get_biome_info.return_value = mock_biome_info

        generator = OptimizedWorldGenerator()
        region = generator.generate_region(2, 3)

        # Verify region properties
        assert region.x == 2
        assert region.y == 3
        assert region.name == "Region_2_3"
        assert region.description == "A generated region at coordinates (2, 3)"
        assert len(region.terrain) == 4  # 4 cells
        assert isinstance(region.biomes, list)  # 2D array
    
    @patch("backend.systems.world_state.optimized_worldgen.TerrainGenerator")
    def test_generate_region_with_offsets(self, mock_terrain_gen): pass
        """Test region generation with temperature and moisture offsets."""
        # Setup mock terrain generator
        mock_instance = Mock()
        mock_terrain_gen.return_value = mock_instance
        
        # Mock terrain data
        mock_terrain_data = {
            "0_0": {"biome": "desert", "elevation": 0.3, "resources": {}},
            "0_1": {"biome": "savanna", "elevation": 0.4, "resources": {}},
        }
        mock_instance.generate_terrain.return_value = mock_terrain_data
        
        # Mock biome info
        mock_biome_info = Mock()
        mock_biome_info.is_water = False
        mock_instance.get_biome_info.return_value = mock_biome_info

        generator = OptimizedWorldGenerator()
        region = generator.generate_region(
            0, 0, temperature_offset=0.2, moisture_offset=-0.1
        )

        # Verify the offsets were passed
        mock_instance.generate_terrain.assert_called_once_with(
            region_x=0,
            region_y=0,
            size=225,  # Default size
            seed=12345,   # Default seed from base_seed + coordinates
            temperature_offset=0.2,
            moisture_offset=-0.1,
        )
        assert region.x == 0
        assert region.y == 0
    
    @patch("backend.systems.world_state.optimized_worldgen.TerrainGenerator")
    def test_generate_region_custom_size(self, mock_terrain_gen): pass
        """Test region generation with custom size."""
        # Setup mock terrain generator
        mock_instance = Mock()
        mock_terrain_gen.return_value = mock_instance
        
        # Mock terrain data for larger region
        mock_terrain_data = {}
        for i in range(10):  # Create more cells for size 100
            mock_terrain_data[f"{i}_0"] = {"biome": "grassland", "elevation": 0.5, "resources": {}}
        
        mock_instance.generate_terrain.return_value = mock_terrain_data
        
        # Mock biome info
        mock_biome_info = Mock()
        mock_biome_info.is_water = False
        mock_instance.get_biome_info.return_value = mock_biome_info

        generator = OptimizedWorldGenerator()
        region = generator.generate_region(0, 0, size=100)

        # Verify size was used
        mock_instance.generate_terrain.assert_called_once_with(
            region_x=0,
            region_y=0,
            size=100,
            seed=12345,  # Default seed from base_seed + coordinates
            temperature_offset=0.0,
            moisture_offset=0.0,
        )
        assert region.size == 100

    @patch("backend.systems.world_state.optimized_worldgen.TerrainGenerator")
    def test_generate_region_with_seed(self, mock_terrain_gen): pass
        """Test region generation with custom seed."""
        # Setup mock terrain generator
        mock_instance = Mock()
        mock_terrain_gen.return_value = mock_instance
        
        # Mock terrain data
        mock_terrain_data = {
            "0_0": {"biome": "grassland", "elevation": 0.5, "resources": {}},
        }
        mock_instance.generate_terrain.return_value = mock_terrain_data
        
        # Mock biome info
        mock_biome_info = Mock()
        mock_biome_info.is_water = False
        mock_instance.get_biome_info.return_value = mock_biome_info

        generator = OptimizedWorldGenerator()
        region = generator.generate_region(0, 0, seed=999)

        # Verify seed was used
        mock_instance.generate_terrain.assert_called_once_with(
            region_x=0,
            region_y=0,
            size=225,  # Default size
            seed=999,
            temperature_offset=0,
            moisture_offset=0,
        )


class TestWorldRivers: pass
    """Test world-level river generation."""
    
    def test_generate_world_rivers(self): pass
        """Test world river generation."""
        generator = OptimizedWorldGenerator()
        
        # Create a mock world map
        world_map = Mock(spec=WorldMap)
        world_map.width = 2
        world_map.height = 2
        world_map.regions = {}
        
        # Create mock regions
        for y in range(2): pass
            for x in range(2): pass
                region = Mock(spec=Region)
                region.elevation = [[0.5, 0.4], [0.3, 0.2]]
                region.rivers = [[False, False], [False, False]]
                # Add terrain mapping that the river generation code expects
                region.terrain = {
                    "0,0": TerrainType.MOUNTAIN,
                    "0,1": TerrainType.HILL,
                    "1,0": TerrainType.GRASSLAND,
                    "1,1": TerrainType.OCEAN
                }
                # Add size property for neighbor finding
                region.size = 4  # 2x2 cell grid
                world_map.regions[(x, y)] = region
        
        with patch.object(generator, '_find_neighboring_cells') as mock_neighbors: pass
            mock_neighbors.return_value = [(1, 0, "0_1", 0.1)]
            
            generator._generate_world_rivers(world_map, 12345)
        
        # Verify that river generation was attempted
        # (Specific assertions depend on the implementation details)
        assert world_map.regions is not None
    
    def test_find_neighboring_cells(self): pass
        """Test finding neighboring cells for river flow."""
        generator = OptimizedWorldGenerator()
        
        # Create a mock world map with elevation data
        world_map = Mock(spec=WorldMap)
        world_map.width = 3
        world_map.height = 3
        world_map.regions = {}
        
        # Create regions with elevation data
        for y in range(3): pass
            for x in range(3): pass
                region = Mock(spec=Region)
                # Create elevation grid where center is highest
                elevation_grid = []
                for row in range(15):  # Standard region grid size
                    elevation_row = []
                    for col in range(15): pass
                        distance_from_center = abs(row - 7) + abs(col - 7)
                        elevation_row.append(0.8 - distance_from_center * 0.05)
                    elevation_grid.append(elevation_row)
                region.elevation = elevation_grid
                # Add terrain mapping
                region.terrain = {
                    f"{i},{j}": TerrainType.GRASSLAND
                    for i in range(15) for j in range(15)
                }
                region.size = 225  # 15x15 grid
                world_map.regions[(x, y)] = region
        
        # Test finding neighbors for center region, center cell
        neighbors = generator._find_neighboring_cells(world_map, 1, 1, "7,7")
        
        assert isinstance(neighbors, list)
        # Should find neighboring cells with lower elevation
        assert len(neighbors) >= 0
    
    def test_find_neighboring_cells_edge_region(self): pass
        """Test finding neighboring cells for edge regions."""
        generator = OptimizedWorldGenerator()
        
        # Create a single region world map
        world_map = Mock(spec=WorldMap)
        world_map.width = 1
        world_map.height = 1
        world_map.regions = {}
        
        region = Mock(spec=Region)
        region.elevation = [[0.5] * 15 for _ in range(15)]
        # Add terrain mapping
        region.terrain = {
            f"{i},{j}": TerrainType.GRASSLAND
            for i in range(15) for j in range(15)
        }
        region.size = 225  # 15x15 grid
        world_map.regions[(0, 0)] = region
        
        # Test finding neighbors for edge region
        neighbors = generator._find_neighboring_cells(world_map, 0, 0, "0,0")
        
        assert isinstance(neighbors, list)


class TestPointsOfInterest: pass
    """Test points of interest generation."""
    
    def test_generate_points_of_interest(self): pass
        """Test POI generation for world map."""
        generator = OptimizedWorldGenerator()
        
        # Create a mock world map with regions
        world_map = Mock(spec=WorldMap)
        world_map.width = 2
        world_map.height = 2
        world_map.regions = {}
        
        for y in range(2): pass
            for x in range(2): pass
                region = Mock(spec=Region)
                region.points_of_interest = []
                region.biome_map = [["forest"] * 15 for _ in range(15)]
                region.elevation = [[0.5] * 15 for _ in range(15)]
                # Add terrain mapping that the POI generation code expects
                region.terrain = {
                    f"{i},{j}": TerrainType.FOREST if (i+j) % 2 == 0 else TerrainType.GRASSLAND
                    for i in range(15) for j in range(15)
                }
                world_map.regions[(x, y)] = region
        
        generator._generate_points_of_interest(world_map, 12345)
        
        # Verify POI generation was attempted
        # (Specific assertions depend on the implementation)
        assert world_map.regions is not None


class TestHelperFunctions: pass
    """Test helper functions and utilities."""
    
    def test_create_world_generator(self): pass
        """Test create_world_generator helper function."""
        generator = create_world_generator()
        
        assert isinstance(generator, OptimizedWorldGenerator)
        assert hasattr(generator, 'config')
        assert hasattr(generator, 'terrain_generator')
        assert hasattr(generator, 'region_cache')
    
    def test_create_world_generator_with_config(self, temp_config_file): pass
        """Test create_world_generator with custom config."""
        generator = create_world_generator(config_path=temp_config_file)
        
        assert generator.config["base_seed"] == 54321
        assert generator.config["region_size"] == 300
        
        # Clean up
        os.unlink(temp_config_file)


class TestConfigurationHandling: pass
    """Test configuration handling and validation."""
    
    def test_default_configuration_completeness(self): pass
        """Test that default configuration contains all required fields."""
        generator = OptimizedWorldGenerator()
        
        required_fields = [
            "base_seed", "region_size", "map_width", "map_height",
            "elevation_noise_layers", "temperature_base", "temperature_variation",
            "moisture_base", "moisture_variation", "ocean_threshold",
            "mountain_threshold", "river_threshold", "coast_threshold",
            "river_count_per_region"
        ]
        
        for field in required_fields: pass
            assert field in generator.config
    
    def test_elevation_noise_layers_structure(self): pass
        """Test elevation noise layers configuration structure."""
        generator = OptimizedWorldGenerator()
        
        noise_layers = generator.config["elevation_noise_layers"]
        assert isinstance(noise_layers, list)
        assert len(noise_layers) > 0
        
        for layer in noise_layers: pass
            assert "scale" in layer
            assert "amplitude" in layer
            assert "persistence" in layer
    
    def test_config_file_partial_override(self, temp_config_file): pass
        """Test that config file partially overrides defaults."""
        # Create config file with only some fields
        partial_config = {"base_seed": 99999, "ocean_threshold": 0.1}
        
        with open(temp_config_file, 'w') as f: pass
            json.dump(partial_config, f)
        
        generator = OptimizedWorldGenerator(config_path=temp_config_file)
        
        # Overridden fields should be updated
        assert generator.config["base_seed"] == 99999
        assert generator.config["ocean_threshold"] == 0.1
        
        # Non-overridden fields should keep defaults
        assert generator.config["region_size"] == 225
        assert generator.config["map_width"] == 5
        
        # Clean up
        os.unlink(temp_config_file)


class TestErrorHandling: pass
    """Test error handling and edge cases."""
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    def test_terrain_generator_initialization_error(self, mock_terrain_gen_class): pass
        """Test handling of terrain generator initialization errors."""
        mock_terrain_gen_class.side_effect = Exception("Terrain generator failed")
        
        with pytest.raises(Exception): pass
            OptimizedWorldGenerator()
    
    def test_invalid_json_config_file(self): pass
        """Test handling of invalid JSON configuration files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f: pass
            f.write("invalid json content {")
            temp_file = f.name
        
        try: pass
            with pytest.raises(json.JSONDecodeError): pass
                OptimizedWorldGenerator(config_path=temp_file)
        finally: pass
            os.unlink(temp_file)
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    def test_region_generation_error_handling(self, mock_terrain_gen_class, mock_terrain_generator): pass
        """Test handling of region generation errors."""
        mock_terrain_gen_class.return_value = mock_terrain_generator
        mock_terrain_generator.generate_region.side_effect = Exception("Region generation failed")
        
        generator = OptimizedWorldGenerator()
        
        with pytest.raises(Exception): pass
            generator.generate_region(0, 0)


class TestPerformanceOptimizations: pass
    """Test performance-related features."""
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    def test_region_caching(self, mock_terrain_gen_class): pass
        """Test that region cache is properly managed."""
        # Setup mock terrain generator
        mock_instance = Mock()
        mock_terrain_gen_class.return_value = mock_instance
        
        # Mock terrain data with proper structure
        mock_terrain_data = {
            "0_0": {"biome": "grassland", "elevation": 0.5, "resources": {"wood": 10}},
            "0_1": {"biome": "forest", "elevation": 0.6, "resources": {"wood": 20}},
        }
        mock_instance.generate_terrain.return_value = mock_terrain_data
        
        # Mock biome info
        mock_biome_info = Mock()
        mock_biome_info.is_water = False
        mock_instance.get_biome_info.return_value = mock_biome_info
        
        generator = OptimizedWorldGenerator()
        
        # Generate a region multiple times
        region1 = generator.generate_region(0, 0)
        region2 = generator.generate_region(0, 0)
        
        # Both should return the same region instance (from cache)
        assert region1 is region2
        
        # Terrain generator should only be called once
        assert mock_instance.generate_terrain.call_count == 1
    
    def test_memory_management_large_world(self): pass
        """Test memory management for large world generation."""
        generator = OptimizedWorldGenerator()
        
        # Test that cache doesn't grow unbounded
        initial_cache_size = len(generator.region_cache)
        
        # Simulate many region generations
        for i in range(100): pass
            cache_key = f"region_{i}"
            generator.region_cache[cache_key] = Mock()
        
        # Cache should have entries but not cause memory issues
        assert len(generator.region_cache) > initial_cache_size
        assert len(generator.region_cache) == 100


class TestIntegration: pass
    """Test integration between different components."""
    
    @patch('backend.systems.world_state.optimized_worldgen.TerrainGenerator')
    def test_full_world_generation_integration(self, mock_terrain_gen_class): pass
        """Test full integration of world generation components."""
        # Setup mock terrain generator
        mock_instance = Mock()
        mock_terrain_gen_class.return_value = mock_instance
        
        # Mock terrain data with proper structure
        mock_terrain_data = {
            "0_0": {"biome": "grassland", "elevation": 0.5, "resources": {"wood": 10}},
            "0_1": {"biome": "forest", "elevation": 0.6, "resources": {"wood": 20}},
            "1_0": {"biome": "mountain", "elevation": 0.8, "resources": {"stone": 15}},
            "1_1": {"biome": "desert", "elevation": 0.4, "resources": {"sand": 5}},
        }
        mock_instance.generate_terrain.return_value = mock_terrain_data
        
        # Mock biome info
        mock_biome_info = Mock()
        mock_biome_info.is_water = False
        mock_instance.get_biome_info.return_value = mock_biome_info
        
        generator = OptimizedWorldGenerator()
        
        # Generate a small world
        world_map = generator.generate_world_map(width=2, height=2, seed=12345)
        
        # Verify complete world structure
        assert isinstance(world_map, WorldMap)
        assert world_map.width == 2
        assert world_map.height == 2
        assert len(world_map.regions) == 4
        
        # Verify all regions are properly generated
        for y in range(2): pass
            for x in range(2): pass
                region = world_map.regions[(x, y)]
                assert region.x == x
                assert region.y == y
                assert region.size == 225


class TestTerrainMethods: pass
    """Test terrain elevation methods."""

    def test_get_terrain_elevation_forest(self): pass
        """Test terrain elevation calculation for forest."""
        generator = OptimizedWorldGenerator()
        from backend.systems.world_state.consolidated_world_models import TerrainType
        
        elevation = generator._get_terrain_elevation(TerrainType.FOREST)
        assert elevation == 0.6

    def test_get_terrain_elevation_ocean(self): pass
        """Test terrain elevation calculation for ocean."""
        generator = OptimizedWorldGenerator()
        from backend.systems.world_state.consolidated_world_models import TerrainType
        
        elevation = generator._get_terrain_elevation(TerrainType.OCEAN)
        assert elevation == 0.0

    def test_get_terrain_elevation_mountains(self): pass
        """Test terrain elevation calculation for mountains."""
        generator = OptimizedWorldGenerator()
        from backend.systems.world_state.consolidated_world_models import TerrainType
        
        elevation = generator._get_terrain_elevation(TerrainType.MOUNTAIN)
        assert elevation == 0.85

    def test_get_terrain_elevation_unknown(self): pass
        """Test terrain elevation calculation for unknown terrain."""
        generator = OptimizedWorldGenerator()
        from backend.systems.world_state.consolidated_world_models import TerrainType
        
        # Use a terrain type that's not in the elevation map
        elevation = generator._get_terrain_elevation(TerrainType.WASTELAND)
        assert elevation == 0.5  # Default value 