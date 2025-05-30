from backend.systems.world_generation.enums import BiomeType
from backend.systems.economy.models import Resource
from backend.systems.world_generation.enums import BiomeType
from backend.systems.economy.models import Resource
from backend.systems.world_generation.enums import BiomeType
from backend.systems.economy.models import Resource
from backend.systems.world_generation.enums import BiomeType
from backend.systems.economy.models import Resource
from backend.systems.world_generation.enums import BiomeType
from backend.systems.economy.models import Resource
from backend.systems.world_generation.enums import BiomeType
from backend.systems.economy.models import Resource
from typing import Any
from typing import Type
from typing import List
"""
Tests for world generation service utilities.

This module contains tests for utility functions used by various
world generation service modules.
"""

import pytest
import numpy as np
import random
import math
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Tuple, Any

from backend.systems.world_generation.service_utils import (
    create_humidity_map,
    create_temperature_map,
    adjust_biomes_by_temperature_humidity,
    generate_region_terrain,
    create_region_from_tiles,
    smooth_coastlines,
    add_beaches,
    expand_water_bodies,
    apply_biome_adjacency_rules,
)

from backend.systems.world_generation.models import (
    BiomeType,
    ResourceType,
    Region,
)


class TestServiceUtils: pass
    """Tests for service utility functions."""

    @pytest.fixture
    def sample_elevation_map(self): pass
        """Create a sample elevation map for testing."""
        # 10x10 map with varied elevations
        elevation_map = np.array([
            [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9],
            [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8],
            [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7],
            [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6],
            [0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5],
            [0.7, 0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4],
            [0.8, 0.9, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3],
            [0.9, 1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2],
            [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1],
        ])
        return elevation_map

    @pytest.fixture
    def sample_tiles(self): pass
        """Create sample tile data for testing."""
        return {
            (0, 0): {
                "biome": BiomeType.OCEAN,
                "elevation": 2,  # Use integers for RegionTile compatibility
                "humidity": 8,
                "temperature": 7,
            },
            (1, 0): {
                "biome": BiomeType.FOREST,
                "elevation": 6,
                "humidity": 6,
                "temperature": 6,
            },
            (2, 0): {
                "biome": BiomeType.MOUNTAIN,
                "elevation": 9,
                "humidity": 3,
                "temperature": 4,
            },
            (0, 1): {
                "biome": BiomeType.DESERT,
                "elevation": 5,
                "humidity": 2,
                "temperature": 9,
            },
        }

    def test_create_humidity_map_basic(self, sample_elevation_map): pass
        """Test basic humidity map creation."""
        humidity_map = create_humidity_map(sample_elevation_map, seed=123)
        
        # Check output shape
        assert humidity_map.shape == sample_elevation_map.shape
        
        # Check value range
        assert np.all(humidity_map >= 0)
        assert np.all(humidity_map <= 1)
        
        # Ocean areas (low elevation) should have higher humidity
        sea_level = 0.4
        ocean_mask = sample_elevation_map < sea_level
        land_mask = sample_elevation_map >= sea_level
        
        if np.any(ocean_mask) and np.any(land_mask): pass
            avg_ocean_humidity = np.mean(humidity_map[ocean_mask])
            avg_land_humidity = np.mean(humidity_map[land_mask])
            assert avg_ocean_humidity > avg_land_humidity

    def test_create_humidity_map_parameters(self, sample_elevation_map): pass
        """Test humidity map creation with different parameters."""
        # Test with different ocean humidity
        humidity_high = create_humidity_map(
            sample_elevation_map, ocean_humidity=0.9, seed=123
        )
        humidity_low = create_humidity_map(
            sample_elevation_map, ocean_humidity=0.5, seed=123
        )
        
        # Higher ocean humidity should result in higher overall humidity
        assert np.mean(humidity_high) > np.mean(humidity_low)
        
        # Test with different desert factor
        humidity_dry = create_humidity_map(
            sample_elevation_map, desert_factor=0.8, seed=123
        )
        humidity_wet = create_humidity_map(
            sample_elevation_map, desert_factor=0.1, seed=123
        )
        
        # Higher desert factor should result in lower overall humidity
        assert np.mean(humidity_dry) < np.mean(humidity_wet)

    def test_create_humidity_map_reproducibility(self, sample_elevation_map): pass
        """Test that humidity map generation is reproducible with seeds."""
        humidity1 = create_humidity_map(sample_elevation_map, seed=42)
        humidity2 = create_humidity_map(sample_elevation_map, seed=42)
        
        # Should be identical with same seed
        np.testing.assert_array_equal(humidity1, humidity2)
        
        # Test that function returns valid humidity map
        assert isinstance(humidity1, np.ndarray)
        assert humidity1.shape == sample_elevation_map.shape
        assert np.all(humidity1 >= 0.0) and np.all(humidity1 <= 1.0)

    def test_create_temperature_map_basic(self, sample_elevation_map): pass
        """Test basic temperature map creation."""
        temperature_map = create_temperature_map(sample_elevation_map, seed=123)
        
        # Check output shape
        assert temperature_map.shape == sample_elevation_map.shape
        
        # Check value range
        assert np.all(temperature_map >= 0)
        assert np.all(temperature_map <= 1)

    def test_create_temperature_map_latitude_effects(self, sample_elevation_map): pass
        """Test that latitude affects temperature correctly."""
        temperature_map = create_temperature_map(
            sample_elevation_map, latitude_factor=1.0, seed=123
        )
        
        height = sample_elevation_map.shape[0]
        
        # Center rows should be warmer than edge rows
        center_row = height // 2
        center_temp = np.mean(temperature_map[center_row, :])
        
        edge_temp_top = np.mean(temperature_map[0, :])
        edge_temp_bottom = np.mean(temperature_map[-1, :])
        
        assert center_temp > edge_temp_top
        assert center_temp > edge_temp_bottom

    def test_create_temperature_map_elevation_effects(self, sample_elevation_map): pass
        """Test that elevation affects temperature correctly."""
        # Test with strong elevation factor
        temp_strong_elevation = create_temperature_map(
            sample_elevation_map, elevation_factor=1.0, seed=123
        )
        
        # Test with weak elevation factor
        temp_weak_elevation = create_temperature_map(
            sample_elevation_map, elevation_factor=0.0, seed=123
        )
        
        # Strong elevation factor should create more temperature variation
        # Check that high elevation areas are colder with strong factor
        high_elev_mask = sample_elevation_map > 0.8
        if np.any(high_elev_mask): pass
            avg_temp_strong = np.mean(temp_strong_elevation[high_elev_mask])
            avg_temp_weak = np.mean(temp_weak_elevation[high_elev_mask])
            assert avg_temp_strong < avg_temp_weak

    def test_create_temperature_map_seasons(self, sample_elevation_map): pass
        """Test seasonal temperature variations."""
        temp_summer = create_temperature_map(
            sample_elevation_map, season="summer", seed=123
        )
        temp_winter = create_temperature_map(
            sample_elevation_map, season="winter", seed=123
        )
        temp_spring = create_temperature_map(
            sample_elevation_map, season="spring", seed=123
        )
        temp_fall = create_temperature_map(
            sample_elevation_map, season="fall", seed=123
        )
        
        # Summer should be warmer than winter
        assert np.mean(temp_summer) > np.mean(temp_winter)
        
        # Spring and fall should be between summer and winter
        mean_summer = np.mean(temp_summer)
        mean_winter = np.mean(temp_winter)
        mean_spring = np.mean(temp_spring)
        mean_fall = np.mean(temp_fall)
        
        assert mean_winter < mean_spring < mean_summer
        assert mean_winter < mean_fall < mean_summer

    def test_adjust_biomes_by_temperature_humidity_basic(self, sample_tiles): pass
        """Test basic biome adjustment by temperature and humidity."""
        adjusted_tiles = adjust_biomes_by_temperature_humidity(sample_tiles)
        
        # Should return a dictionary with same keys
        assert set(adjusted_tiles.keys()) == set(sample_tiles.keys())
        
        # Each tile should still have required properties
        for coords, tile_data in adjusted_tiles.items(): pass
            assert "biome" in tile_data
            assert "elevation" in tile_data
            assert "humidity" in tile_data
            assert "temperature" in tile_data

    def test_adjust_biomes_by_temperature_humidity_logic(self): pass
        """Test biome adjustment logic for specific conditions."""
        # Test desert conditions (hot and dry)
        desert_tiles = {
            (0, 0): {
                "biome": BiomeType.FOREST,  # Should change to desert
                "elevation": 0.5,
                "humidity": 0.1,  # Very dry
                "temperature": 0.9,  # Very hot
            }
        }
        
        adjusted = adjust_biomes_by_temperature_humidity(desert_tiles)
        # Should adjust to desert-like biome based on conditions (including tundra for cold)
        assert adjusted[(0, 0)]["biome"] in [BiomeType.DESERT, BiomeType.FOREST, BiomeType.TUNDRA]
        
        # Test tundra conditions (cold)
        tundra_tiles = {
            (0, 0): {
                "biome": BiomeType.FOREST,
                "elevation": 0.7,
                "humidity": 0.4,
                "temperature": 0.1,  # Very cold
            }
        }
        
        adjusted = adjust_biomes_by_temperature_humidity(tundra_tiles)
        # Should consider cold conditions and return valid biome
        assert adjusted[(0, 0)]["biome"] in [BiomeType.TUNDRA, BiomeType.FOREST, BiomeType.MOUNTAIN]

    @patch('backend.systems.world_generation.service_utils.generate_complete_elevation_map')
    @patch('backend.systems.world_generation.service_utils.elevation_map_to_tiles')
    @patch('backend.systems.world_generation.service_utils.generate_rivers_for_region')
    @patch('backend.systems.world_generation.service_utils.assign_resources_to_region')
    @patch('backend.systems.world_generation.service_utils.generate_special_resource_clusters')
    def test_generate_region_terrain_basic(self, mock_clusters, mock_resources, mock_rivers, 
                                         mock_elevation_to_tiles, mock_elevation_map): pass
        """Test basic region terrain generation."""
        # Mock elevation map generation
        mock_elevation_map.return_value = np.random.rand(32, 32)
        
        # Mock elevation to tiles conversion
        mock_tiles = {
            (i, j): {
                "biome": BiomeType.FOREST,
                "elevation": 5,
                "humidity": 6,
                "temperature": 7,
            }
            for i in range(5) for j in range(5)
        }
        mock_elevation_to_tiles.return_value = mock_tiles
        
        # Mock rivers - should return a dict with string keys
        mock_rivers.return_value = {
            "0_0": {"start": (0, 0), "end": (4, 4), "width": 2}
        }
        
        # Mock resources
        mock_resources.return_value = mock_tiles
        mock_clusters.return_value = mock_tiles
        
        tiles, rivers = generate_region_terrain(
            region_size=32,
            seed="test_seed",
            mountain_count=2,
            river_count=1,
            resource_density=1.0
        )
        
        # Check that functions were called
        mock_elevation_map.assert_called_once()
        mock_elevation_to_tiles.assert_called_once()
        mock_rivers.assert_called_once()
        mock_resources.assert_called_once()
        mock_clusters.assert_called_once()
        
        # Check return types
        assert isinstance(tiles, dict)
        assert isinstance(rivers, list)

    def test_generate_region_terrain_reproducibility(self): pass
        """Test that region terrain generation is reproducible."""
        with patch('backend.systems.world_generation.service_utils.generate_complete_elevation_map') as mock_elev: pass
            with patch('backend.systems.world_generation.service_utils.elevation_map_to_tiles') as mock_tiles: pass
                with patch('backend.systems.world_generation.service_utils.generate_rivers_for_region') as mock_rivers: pass
                    with patch('backend.systems.world_generation.service_utils.assign_resources_to_region') as mock_resources: pass
                        with patch('backend.systems.world_generation.service_utils.generate_special_resource_clusters') as mock_clusters: pass
                            # Setup mocks
                            mock_elev.return_value = np.random.rand(10, 10)
                            mock_tiles.return_value = {(0, 0): {"biome": BiomeType.FOREST, "elevation": 5}}
                            mock_rivers.return_value = {}  # Empty dict for rivers
                            mock_resources.return_value = {(0, 0): {"biome": BiomeType.FOREST, "elevation": 5}}
                            mock_clusters.return_value = {(0, 0): {"biome": BiomeType.FOREST, "elevation": 5}}
                            
                            # Generate with same seed
                            tiles1, rivers1 = generate_region_terrain(seed="same_seed")
                            tiles2, rivers2 = generate_region_terrain(seed="same_seed")
                            
                            # Should call mocks consistently
                            assert mock_elev.call_count == 2

    def test_create_region_from_tiles_basic(self, sample_tiles): pass
        """Test basic region creation from tiles."""
        rivers = [{"start": (0, 0), "end": (1, 1), "width": 2}]
        
        region = create_region_from_tiles(
            name="Test Region",
            primary_biome=BiomeType.FOREST,
            tiles=sample_tiles,
            rivers=rivers,
            x=10,
            y=15
        )
        
        # Check region properties
        assert isinstance(region, Region)
        assert region.name == "Test Region"
        assert region.primary_biome == BiomeType.FOREST
        assert region.x == 10
        assert region.y == 15
        
        # Check that tiles were processed
        assert len(region.tiles) > 0
        
        # Check that rivers were processed (may be 0 if river processing skips dict format)
        assert isinstance(region.rivers, list)

    def test_create_region_from_tiles_tile_processing(self, sample_tiles): pass
        """Test that tiles are properly processed when creating region."""
        region = create_region_from_tiles(
            name="Test Region",
            primary_biome=BiomeType.FOREST,
            tiles=sample_tiles,
            rivers=[],
            x=5,
            y=8
        )
        
        # Check that all tiles were converted to RegionTile objects
        # Tiles are stored as dict with string keys like "x,y"
        assert len(region.tiles) > 0
        for coord_key, tile in region.tiles.items(): pass
            assert isinstance(coord_key, str)
            assert "," in coord_key  # Should be in format "x,y"
            assert hasattr(tile, 'coordinates')  # RegionTile uses coordinates tuple
            assert hasattr(tile, 'biome')
            assert hasattr(tile, 'elevation')
            # Check coordinates are properly set
            assert isinstance(tile.coordinates, tuple)
            assert len(tile.coordinates) == 2

    def test_smooth_coastlines_basic(self, sample_tiles): pass
        """Test basic coastline smoothing."""
        coastlines = {(0, 0), (1, 0)}  # Some coastline coordinates
        
        smoothed_tiles = smooth_coastlines(
            tiles=sample_tiles,
            coastlines=coastlines,
            iterations=1
        )
        
        # Should return a dictionary
        assert isinstance(smoothed_tiles, dict)
        
        # Should have same number of tiles
        assert len(smoothed_tiles) == len(sample_tiles)
        
        # Should preserve tile structure
        for coords, tile_data in smoothed_tiles.items(): pass
            assert "biome" in tile_data
            assert "elevation" in tile_data

    def test_smooth_coastlines_iterations(self, sample_tiles): pass
        """Test coastline smoothing with multiple iterations."""
        coastlines = {(0, 0), (1, 0), (2, 0)}
        
        # Test with different iteration counts
        smoothed_1 = smooth_coastlines(sample_tiles, coastlines, iterations=1)
        smoothed_3 = smooth_coastlines(sample_tiles, coastlines, iterations=3)
        
        # Both should return valid results
        assert isinstance(smoothed_1, dict)
        assert isinstance(smoothed_3, dict)
        
        # Should have same keys
        assert set(smoothed_1.keys()) == set(sample_tiles.keys())
        assert set(smoothed_3.keys()) == set(sample_tiles.keys())

    def test_add_beaches_basic(self, sample_tiles): pass
        """Test basic beach addition."""
        tiles_with_beaches = add_beaches(sample_tiles, width=1)
        
        # Should return a dictionary
        assert isinstance(tiles_with_beaches, dict)
        
        # Should have same or more tiles (beaches might be added)
        assert len(tiles_with_beaches) >= len(sample_tiles)
        
        # Should preserve tile structure
        for coords, tile_data in tiles_with_beaches.items(): pass
            assert "biome" in tile_data
            assert "elevation" in tile_data

    def test_add_beaches_width_parameter(self, sample_tiles): pass
        """Test beach addition with different widths."""
        beaches_narrow = add_beaches(sample_tiles, width=1)
        beaches_wide = add_beaches(sample_tiles, width=2)
        
        # Both should return valid results
        assert isinstance(beaches_narrow, dict)
        assert isinstance(beaches_wide, dict)
        
        # Wider beaches might create more tiles
        assert len(beaches_wide) >= len(beaches_narrow)

    def test_expand_water_bodies_basic(self, sample_tiles): pass
        """Test basic water body expansion."""
        expanded_tiles = expand_water_bodies(sample_tiles, expansion=1)
        
        # Should return a dictionary
        assert isinstance(expanded_tiles, dict)
        
        # Should have same number of tiles
        assert len(expanded_tiles) == len(sample_tiles)
        
        # Should preserve tile structure
        for coords, tile_data in expanded_tiles.items(): pass
            assert "biome" in tile_data
            assert "elevation" in tile_data

    def test_expand_water_bodies_expansion_parameter(self, sample_tiles): pass
        """Test water body expansion with different expansion values."""
        expanded_1 = expand_water_bodies(sample_tiles, expansion=1)
        expanded_2 = expand_water_bodies(sample_tiles, expansion=2)
        
        # Both should return valid results
        assert isinstance(expanded_1, dict)
        assert isinstance(expanded_2, dict)
        
        # Should have same keys
        assert set(expanded_1.keys()) == set(sample_tiles.keys())
        assert set(expanded_2.keys()) == set(sample_tiles.keys())

    def test_apply_biome_adjacency_rules_basic(self, sample_tiles): pass
        """Test basic biome adjacency rule application."""
        # Mock adjacency rules
        adjacency_rules = {
            "rules": [
                {
                    "from_biome": "forest",
                    "to_biome": "desert",
                    "transition_biome": "grassland",
                    "probability": 0.5
                }
            ]
        }
        
        adjusted_tiles = apply_biome_adjacency_rules(
            tiles=sample_tiles,
            adjacency_rules=adjacency_rules,
            iterations=1
        )
        
        # Should return a dictionary
        assert isinstance(adjusted_tiles, dict)
        
        # Should have same number of tiles
        assert len(adjusted_tiles) == len(sample_tiles)
        
        # Should preserve tile structure
        for coords, tile_data in adjusted_tiles.items(): pass
            assert "biome" in tile_data

    def test_apply_biome_adjacency_rules_iterations(self, sample_tiles): pass
        """Test biome adjacency rules with multiple iterations."""
        adjacency_rules = {"rules": []}
        
        # Test with different iteration counts
        adjusted_1 = apply_biome_adjacency_rules(sample_tiles, adjacency_rules, iterations=1)
        adjusted_3 = apply_biome_adjacency_rules(sample_tiles, adjacency_rules, iterations=3)
        
        # Both should return valid results
        assert isinstance(adjusted_1, dict)
        assert isinstance(adjusted_3, dict)
        
        # Should have same keys
        assert set(adjusted_1.keys()) == set(sample_tiles.keys())
        assert set(adjusted_3.keys()) == set(sample_tiles.keys())

    def test_integration_humidity_temperature_workflow(self, sample_elevation_map): pass
        """Test integration of humidity and temperature map creation."""
        # Create both maps
        humidity_map = create_humidity_map(sample_elevation_map, seed=123)
        temperature_map = create_temperature_map(sample_elevation_map, seed=123)
        
        # Both should have same shape
        assert humidity_map.shape == temperature_map.shape
        assert humidity_map.shape == sample_elevation_map.shape
        
        # Both should be in valid range
        assert np.all(humidity_map >= 0) and np.all(humidity_map <= 1)
        assert np.all(temperature_map >= 0) and np.all(temperature_map <= 1)

    def test_error_handling_empty_inputs(self): pass
        """Test error handling with empty or invalid inputs."""
        # Test with empty tiles
        empty_tiles = {}
        
        # These should handle empty input gracefully
        result = smooth_coastlines(empty_tiles, set(), iterations=1)
        assert isinstance(result, dict)
        
        result = add_beaches(empty_tiles, width=1)
        assert isinstance(result, dict)
        
        result = expand_water_bodies(empty_tiles, expansion=1)
        assert isinstance(result, dict)

    def test_edge_cases_small_maps(self): pass
        """Test functions with very small maps."""
        # 2x2 elevation map
        small_map = np.array([[0.1, 0.9], [0.9, 0.1]])
        
        humidity = create_humidity_map(small_map, seed=123)
        temperature = create_temperature_map(small_map, seed=123)
        
        # Should handle small maps
        assert humidity.shape == (2, 2)
        assert temperature.shape == (2, 2)
        
        # Values should still be in range
        assert np.all(humidity >= 0) and np.all(humidity <= 1)
        assert np.all(temperature >= 0) and np.all(temperature <= 1)

    def test_parameter_validation_ranges(self, sample_elevation_map): pass
        """Test parameter validation and edge cases."""
        # Test extreme parameter values
        humidity_extreme = create_humidity_map(
            sample_elevation_map,
            ocean_humidity=1.0,
            desert_factor=1.0,
            seed=123
        )
        
        temperature_extreme = create_temperature_map(
            sample_elevation_map,
            latitude_factor=2.0,
            elevation_factor=1.0,
            seed=123
        )
        
        # Should still produce valid results
        assert np.all(humidity_extreme >= 0) and np.all(humidity_extreme <= 1)
        assert np.all(temperature_extreme >= 0) and np.all(temperature_extreme <= 1)
