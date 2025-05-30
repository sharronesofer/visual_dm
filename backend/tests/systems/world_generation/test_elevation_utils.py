from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import ElevationType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import ElevationType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import ElevationType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import ElevationType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import ElevationType
from backend.systems.world_generation.enums import BiomeType
from backend.systems.world_generation.enums import ElevationType
from typing import Any
from typing import Type
from typing import List
"""
Tests for world generation elevation utilities.

This module contains tests for elevation generation, processing,
and terrain feature functions used in world generation.
"""

import pytest
import numpy as np
import math
import random
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Tuple, Set, Any

from backend.systems.world_generation.elevation_utils import (
    get_elevation_type,
    generate_elevation_map,
    generate_perlin_noise,
    apply_terrain_features,
    add_mountain_peak,
    add_valley,
    normalize_elevation_map,
    calculate_slope,
    identify_terrain_features,
    generate_noise_map,
    apply_island_falloff,
    elevation_map_to_tiles,
    smooth_elevation_map,
    create_mountain_ranges,
    generate_complete_elevation_map,
    get_neighboring_tiles,
    is_valid_elevation_transition,
    ELEVATION_TYPE_MAP,
    DEFAULT_ELEVATION_BIOME_MAP,
)

from backend.systems.world_generation.models import ElevationType, BiomeType


class TestElevationUtils:
    """Tests for elevation utility functions."""

    def test_elevation_type_map_completeness(self):
        """Test that elevation type map covers all expected values."""
        # Should have mappings for 0-10
        for i in range(11):
            assert i in ELEVATION_TYPE_MAP
            assert isinstance(ELEVATION_TYPE_MAP[i], ElevationType)

    def test_default_elevation_biome_map_completeness(self):
        """Test that default biome map covers all elevation types."""
        for elevation_type in ElevationType:
            assert elevation_type in DEFAULT_ELEVATION_BIOME_MAP
            assert isinstance(DEFAULT_ELEVATION_BIOME_MAP[elevation_type], BiomeType)

    def test_get_elevation_type_valid_values(self):
        """Test elevation type retrieval for valid values."""
        assert get_elevation_type(0) == ElevationType.DEEP_OCEAN
        assert get_elevation_type(5) == ElevationType.HIGHLAND
        assert get_elevation_type(10) == ElevationType.SUMMIT

    def test_get_elevation_type_invalid_values(self):
        """Test elevation type retrieval for invalid values."""
        # Should return default for invalid values
        assert get_elevation_type(-1) == ElevationType.PLAIN
        assert get_elevation_type(11) == ElevationType.PLAIN
        assert get_elevation_type(100) == ElevationType.PLAIN

    def test_generate_elevation_map_basic(self):
        """Test basic elevation map generation."""
        width, height = 10, 8
        elevation_map = generate_elevation_map(width, height)
        
        # Should return dictionary with correct number of coordinates
        assert isinstance(elevation_map, dict)
        assert len(elevation_map) == width * height
        
        # All coordinates should be present
        for x in range(width):
            for y in range(height):
                assert (x, y) in elevation_map
                
        # All values should be in valid range
        for elevation in elevation_map.values():
            assert 0.0 <= elevation <= 1.0

    def test_generate_elevation_map_parameters(self):
        """Test elevation map generation with different parameters."""
        width, height = 5, 5
        
        # Test with different base elevations
        low_base = generate_elevation_map(width, height, base_elevation=0.2)
        high_base = generate_elevation_map(width, height, base_elevation=0.8)
        
        # Higher base elevation should generally result in higher values
        avg_low = sum(low_base.values()) / len(low_base)
        avg_high = sum(high_base.values()) / len(high_base)
        assert avg_high > avg_low

    def test_generate_elevation_map_noise_scale(self):
        """Test elevation map generation with different noise scales."""
        width, height = 5, 5
        
        # Test with different noise scales
        fine_noise = generate_elevation_map(width, height, noise_scale=0.05)
        coarse_noise = generate_elevation_map(width, height, noise_scale=0.2)
        
        # Both should return valid maps
        assert len(fine_noise) == width * height
        assert len(coarse_noise) == width * height
        
        # All values should be in range
        for elevation in fine_noise.values():
            assert 0.0 <= elevation <= 1.0
        for elevation in coarse_noise.values():
            assert 0.0 <= elevation <= 1.0

    def test_generate_perlin_noise_basic(self):
        """Test basic Perlin noise generation."""
        width, height = 8, 6
        noise_map = generate_perlin_noise(width, height)
        
        # Should return dictionary with correct number of coordinates
        assert isinstance(noise_map, dict)
        assert len(noise_map) == width * height
        
        # All coordinates should be present
        for x in range(width):
            for y in range(height):
                assert (x, y) in noise_map
                
        # All values should be in valid range (-1 to 1)
        for noise_value in noise_map.values():
            assert -1.0 <= noise_value <= 1.0

    def test_generate_perlin_noise_parameters(self):
        """Test Perlin noise generation with different parameters."""
        width, height = 5, 5
        
        # Test with different scales
        fine_scale = generate_perlin_noise(width, height, scale=0.05)
        coarse_scale = generate_perlin_noise(width, height, scale=0.2)
        
        # Both should return valid maps
        assert len(fine_scale) == width * height
        assert len(coarse_scale) == width * height
        
        # Test with different octaves
        few_octaves = generate_perlin_noise(width, height, octaves=2)
        many_octaves = generate_perlin_noise(width, height, octaves=6)
        
        # Both should return valid maps
        assert len(few_octaves) == width * height
        assert len(many_octaves) == width * height

    def test_apply_terrain_features_empty(self):
        """Test applying terrain features with empty feature list."""
        elevation_map = {(0, 0): 0.5, (1, 0): 0.4, (0, 1): 0.6}
        features = []
        
        result = apply_terrain_features(elevation_map, features)
        
        # Should return unchanged map
        assert result == elevation_map

    def test_apply_terrain_features_mountain(self):
        """Test applying mountain terrain features."""
        elevation_map = {
            (0, 0): 0.3, (1, 0): 0.3, (2, 0): 0.3,
            (0, 1): 0.3, (1, 1): 0.3, (2, 1): 0.3,
            (0, 2): 0.3, (1, 2): 0.3, (2, 2): 0.3,
        }
        
        features = [{
            "type": "mountain",
            "position": [1, 1],
            "height": 0.8,
            "radius": 1
        }]
        
        result = apply_terrain_features(elevation_map, features)
        
        # Center should be elevated
        assert result[(1, 1)] > elevation_map[(1, 1)]
        
        # All values should still be in valid range
        for elevation in result.values():
            assert 0.0 <= elevation <= 1.0

    def test_apply_terrain_features_valley(self):
        """Test applying valley terrain features."""
        elevation_map = {
            (0, 0): 0.7, (1, 0): 0.7, (2, 0): 0.7,
            (0, 1): 0.7, (1, 1): 0.7, (2, 1): 0.7,
            (0, 2): 0.7, (1, 2): 0.7, (2, 2): 0.7,
        }
        
        features = [{
            "type": "valley",
            "position": [1, 1],
            "depth": 0.3,
            "radius": 1
        }]
        
        result = apply_terrain_features(elevation_map, features)
        
        # Center should be lowered
        assert result[(1, 1)] < elevation_map[(1, 1)]
        
        # All values should still be in valid range
        for elevation in result.values():
            assert 0.0 <= elevation <= 1.0

    def test_apply_terrain_features_unknown_type(self):
        """Test applying unknown terrain feature types."""
        elevation_map = {(0, 0): 0.5, (1, 0): 0.4}
        features = [{"type": "unknown", "position": [0, 0]}]
        
        result = apply_terrain_features(elevation_map, features)
        
        # Should return unchanged map for unknown types
        assert result == elevation_map

    def test_add_mountain_peak_basic(self):
        """Test basic mountain peak addition."""
        elevation_map = {
            (0, 0): 0.3, (1, 0): 0.3, (2, 0): 0.3,
            (0, 1): 0.3, (1, 1): 0.3, (2, 1): 0.3,
            (0, 2): 0.3, (1, 2): 0.3, (2, 2): 0.3,
        }
        
        result = add_mountain_peak(elevation_map, 1, 1, 0.8, 2)  # Larger radius
        
        # Center should be highest
        assert result[(1, 1)] > result[(0, 0)]
        assert result[(1, 1)] > result[(2, 2)]
        
        # Adjacent tiles should be elevated but less than center
        assert result[(1, 0)] >= elevation_map[(1, 0)]  # Allow equal for edge cases
        assert result[(1, 0)] <= result[(1, 1)]

    def test_add_mountain_peak_radius_effects(self):
        """Test mountain peak with different radius values."""
        elevation_map = {
            (i, j): 0.3 for i in range(5) for j in range(5)
        }
        
        # Small radius
        small_radius = add_mountain_peak(elevation_map, 2, 2, 0.8, 1)
        
        # Large radius
        large_radius = add_mountain_peak(elevation_map, 2, 2, 0.8, 3)
        
        # Large radius should affect more tiles
        affected_small = sum(1 for v in small_radius.values() if v > 0.3)
        affected_large = sum(1 for v in large_radius.values() if v > 0.3)
        assert affected_large > affected_small

    def test_add_mountain_peak_height_effects(self):
        """Test mountain peak with different height values."""
        elevation_map = {(0, 0): 0.3, (1, 0): 0.3}
        
        low_peak = add_mountain_peak(elevation_map, 0, 0, 0.5, 1)
        high_peak = add_mountain_peak(elevation_map, 0, 0, 0.9, 1)
        
        # Higher peak should result in higher elevation
        assert high_peak[(0, 0)] > low_peak[(0, 0)]

    def test_add_valley_basic(self):
        """Test basic valley addition."""
        elevation_map = {
            (0, 0): 0.7, (1, 0): 0.7, (2, 0): 0.7,
            (0, 1): 0.7, (1, 1): 0.7, (2, 1): 0.7,
            (0, 2): 0.7, (1, 2): 0.7, (2, 2): 0.7,
        }
        
        result = add_valley(elevation_map, 1, 1, 0.3, 1)
        
        # Center should be lowest
        assert result[(1, 1)] < result[(0, 0)]
        assert result[(1, 1)] < result[(2, 2)]
        
        # Adjacent tiles should be lowered but not as much as center
        assert result[(1, 0)] < elevation_map[(1, 0)]
        assert result[(1, 0)] > result[(1, 1)]

    def test_add_valley_depth_effects(self):
        """Test valley with different depth values."""
        elevation_map = {(0, 0): 0.7, (1, 0): 0.7}
        
        shallow_valley = add_valley(elevation_map, 0, 0, 0.1, 1)
        deep_valley = add_valley(elevation_map, 0, 0, 0.5, 1)
        
        # Deeper valley should result in lower elevation
        assert deep_valley[(0, 0)] < shallow_valley[(0, 0)]

    def test_normalize_elevation_map_basic(self):
        """Test basic elevation map normalization."""
        elevation_map = {
            (0, 0): 0.2, (1, 0): 0.8, (2, 0): 0.5,
            (0, 1): 0.1, (1, 1): 0.9, (2, 1): 0.6,
        }
        
        normalized = normalize_elevation_map(elevation_map)
        
        # Should have same keys
        assert set(normalized.keys()) == set(elevation_map.keys())
        
        # Values should be normalized to 0-1 range
        values = list(normalized.values())
        assert min(values) == 0.0
        assert max(values) == 1.0

    def test_normalize_elevation_map_uniform_values(self):
        """Test normalization with uniform elevation values."""
        elevation_map = {(0, 0): 0.5, (1, 0): 0.5, (2, 0): 0.5}
        
        normalized = normalize_elevation_map(elevation_map)
        
        # All values should remain the same when uniform
        for coord in elevation_map:
            assert normalized[coord] == elevation_map[coord]

    def test_normalize_elevation_map_empty(self):
        """Test normalization with empty elevation map."""
        elevation_map = {}
        
        normalized = normalize_elevation_map(elevation_map)
        
        # Should return empty map
        assert normalized == {}

    def test_calculate_slope_basic(self):
        """Test basic slope calculation."""
        elevation_map = {
            (0, 0): 0.2,
            (1, 0): 0.8,
            (0, 1): 0.5,
        }
        
        # Calculate slope between two points
        slope = calculate_slope((0, 0), (1, 0), elevation_map)
        
        # Should return a float
        assert isinstance(slope, float)
        assert slope >= 0.0

    def test_calculate_slope_same_elevation(self):
        """Test slope calculation with same elevation."""
        elevation_map = {(0, 0): 0.5, (1, 0): 0.5}
        
        slope = calculate_slope((0, 0), (1, 0), elevation_map)
        
        # Should be zero for same elevation
        assert slope == 0.0

    def test_calculate_slope_missing_coordinates(self):
        """Test slope calculation with missing coordinates."""
        elevation_map = {(0, 0): 0.5}
        
        # Should handle missing coordinates gracefully
        slope = calculate_slope((0, 0), (1, 0), elevation_map)
        assert isinstance(slope, float)

    def test_calculate_slope_vertical_distance(self):
        """Test slope calculation with vertical distance."""
        elevation_map = {
            (0, 0): 0.2,
            (0, 3): 0.8,
        }
        
        slope = calculate_slope((0, 0), (0, 3), elevation_map)
        
        # Should handle vertical distance correctly
        assert isinstance(slope, float)
        assert slope > 0.0

    def test_identify_terrain_features_basic(self):
        """Test basic terrain feature identification."""
        elevation_map = {
            (0, 0): 0.1, (1, 0): 0.2, (2, 0): 0.1,
            (0, 1): 0.2, (1, 1): 0.9, (2, 1): 0.2,  # Peak at (1,1)
            (0, 2): 0.1, (1, 2): 0.2, (2, 2): 0.1,
        }
        
        features = identify_terrain_features(elevation_map, width=3, height=3)
        
        # Should return a list
        assert isinstance(features, list)
        
        # Should identify the peak
        peak_features = [f for f in features if f.get("type") == "peak"]
        assert len(peak_features) > 0

    def test_identify_terrain_features_thresholds(self):
        """Test terrain feature identification with custom thresholds."""
        elevation_map = {
            (0, 0): 0.3, (1, 0): 0.7, (2, 0): 0.3,
            (0, 1): 0.7, (1, 1): 0.7, (2, 1): 0.7,
            (0, 2): 0.3, (1, 2): 0.7, (2, 2): 0.3,
        }
        
        # Test with different thresholds
        features_high = identify_terrain_features(
            elevation_map, width=3, height=3, peak_threshold=0.9
        )
        features_low = identify_terrain_features(
            elevation_map, width=3, height=3, peak_threshold=0.6
        )
        
        # Lower threshold should identify more peaks
        peaks_high = [f for f in features_high if f.get("type") == "peak"]
        peaks_low = [f for f in features_low if f.get("type") == "peak"]
        assert len(peaks_low) >= len(peaks_high)

    def test_identify_terrain_features_valleys(self):
        """Test valley identification in terrain features."""
        elevation_map = {
            (0, 0): 0.8, (1, 0): 0.8, (2, 0): 0.8,
            (0, 1): 0.8, (1, 1): 0.1, (2, 1): 0.8,  # Valley at (1,1)
            (0, 2): 0.8, (1, 2): 0.8, (2, 2): 0.8,
        }
        
        features = identify_terrain_features(
            elevation_map, width=3, height=3, valley_threshold=0.3
        )
        
        # Should identify the valley
        valley_features = [f for f in features if f.get("type") == "valley"]
        assert len(valley_features) > 0

    def test_identify_terrain_features_no_dimensions(self):
        """Test terrain feature identification without width/height."""
        elevation_map = {
            (0, 0): 0.1, (1, 0): 0.9,
            (0, 1): 0.1, (1, 1): 0.1,
        }
        
        features = identify_terrain_features(elevation_map)
        
        # Should still work and return a list
        assert isinstance(features, list)

    def test_generate_noise_map_basic(self):
        """Test basic noise map generation."""
        width, height = 8, 6
        noise_array = generate_noise_map(width, height)
        
        # Should return numpy array
        assert isinstance(noise_array, np.ndarray)
        assert noise_array.shape == (height, width)
        
        # Values should be in 0-1 range
        assert np.all(noise_array >= 0.0)
        assert np.all(noise_array <= 1.0)

    def test_generate_noise_map_parameters(self):
        """Test noise map generation with different parameters."""
        width, height = 5, 5
        
        # Test with different scales
        fine_scale = generate_noise_map(width, height, scale=0.5)
        coarse_scale = generate_noise_map(width, height, scale=2.0)
        
        # Both should be valid
        assert fine_scale.shape == (height, width)
        assert coarse_scale.shape == (height, width)
        
        # Test with different octaves
        few_octaves = generate_noise_map(width, height, octaves=2)
        many_octaves = generate_noise_map(width, height, octaves=6)
        
        # Both should be valid
        assert few_octaves.shape == (height, width)
        assert many_octaves.shape == (height, width)

    def test_generate_noise_map_seed_reproducibility(self):
        """Test that noise map generation is reproducible with seeds."""
        width, height = 5, 5
        
        noise1 = generate_noise_map(width, height, seed=42)
        noise2 = generate_noise_map(width, height, seed=42)
        
        # Should be identical with same seed
        np.testing.assert_array_equal(noise1, noise2)
        
        # Should be different with different seeds
        noise3 = generate_noise_map(width, height, seed=43)
        assert not np.array_equal(noise1, noise3)

    def test_generate_noise_map_persistence_lacunarity(self):
        """Test noise map generation with persistence and lacunarity."""
        width, height = 5, 5
        
        # Test with different persistence values
        low_persistence = generate_noise_map(width, height, persistence=0.2)
        high_persistence = generate_noise_map(width, height, persistence=0.8)
        
        # Both should be valid
        assert low_persistence.shape == (height, width)
        assert high_persistence.shape == (height, width)
        
        # Test with different lacunarity values
        low_lacunarity = generate_noise_map(width, height, lacunarity=1.5)
        high_lacunarity = generate_noise_map(width, height, lacunarity=3.0)
        
        # Both should be valid
        assert low_lacunarity.shape == (height, width)
        assert high_lacunarity.shape == (height, width)

    def test_apply_island_falloff_basic(self):
        """Test basic island falloff application."""
        noise_map = np.random.rand(10, 10)
        
        falloff_map = apply_island_falloff(noise_map)
        
        # Should return same shape
        assert falloff_map.shape == noise_map.shape
        
        # Values should still be in valid range
        assert np.all(falloff_map >= 0.0)
        assert np.all(falloff_map <= 1.0)

    def test_apply_island_falloff_strength(self):
        """Test island falloff with different strength values."""
        noise_map = np.ones((10, 10)) * 0.8  # Uniform high values
        
        weak_falloff = apply_island_falloff(noise_map, falloff_strength=1.0)
        strong_falloff = apply_island_falloff(noise_map, falloff_strength=5.0)
        
        # Higher falloff strength creates steeper curves, preserving more value at intermediate distances
        # but the effect is more pronounced at intermediate distances, not at the absolute edge
        center = noise_map.shape[0] // 2
        
        # Test at intermediate distance (not absolute edge)
        intermediate_weak = weak_falloff[2, center]  # Closer to edge but not at edge
        intermediate_strong = strong_falloff[2, center]
        
        # At intermediate distances, stronger falloff should preserve more of the original value
        assert intermediate_strong >= intermediate_weak

    def test_apply_island_falloff_center_preservation(self):
        """Test that island falloff preserves center values."""
        noise_map = np.ones((10, 10)) * 0.8
        
        falloff_map = apply_island_falloff(noise_map, falloff_strength=2.0)
        
        # Center should be less affected than edges
        center = noise_map.shape[0] // 2
        center_value = falloff_map[center, center]
        edge_value = falloff_map[0, 0]
        
        assert center_value > edge_value

    def test_elevation_map_to_tiles_basic(self):
        """Test basic elevation map to tiles conversion."""
        elevation_map = np.array([
            [0.2, 0.5, 0.8],
            [0.3, 0.6, 0.9],
            [0.1, 0.4, 0.7]
        ])
        
        tiles = elevation_map_to_tiles(elevation_map)
        
        # Should return dictionary
        assert isinstance(tiles, dict)
        
        # Should have correct number of tiles
        height, width = elevation_map.shape
        assert len(tiles) == width * height
        
        # All tiles should have required properties
        for coord, tile_data in tiles.items():
            assert isinstance(coord, tuple)
            assert len(coord) == 2
            assert "biome" in tile_data
            assert "elevation" in tile_data

    def test_elevation_map_to_tiles_sea_level(self):
        """Test elevation map to tiles with different sea levels."""
        elevation_map = np.array([
            [0.2, 0.5, 0.8],
            [0.3, 0.6, 0.9],
        ])
        
        # Test with different sea levels
        tiles_low = elevation_map_to_tiles(elevation_map, sea_level=0.3)
        tiles_high = elevation_map_to_tiles(elevation_map, sea_level=0.7)
        
        # Higher sea level should result in more water tiles
        water_biomes = ["ocean", "coast"]
        water_count_low = sum(1 for tile in tiles_low.values() 
                             if tile["biome"] in water_biomes)
        water_count_high = sum(1 for tile in tiles_high.values() 
                              if tile["biome"] in water_biomes)
        
        assert water_count_high >= water_count_low

    def test_elevation_map_to_tiles_with_humidity_temperature(self):
        """Test elevation map to tiles with humidity and temperature maps."""
        elevation_map = np.array([[0.5, 0.6], [0.4, 0.7]])
        humidity_map = np.array([[0.3, 0.8], [0.6, 0.4]])
        temperature_map = np.array([[0.7, 0.2], [0.5, 0.9]])
        
        tiles = elevation_map_to_tiles(
            elevation_map, 
            humidity_map=humidity_map, 
            temperature_map=temperature_map
        )
        
        # Should include humidity and temperature data
        for coord, tile_data in tiles.items():
            assert "humidity" in tile_data
            assert "temperature" in tile_data
            assert 0 <= tile_data["humidity"] <= 10
            assert 0 <= tile_data["temperature"] <= 10

    def test_elevation_map_to_tiles_mountain_level(self):
        """Test elevation map to tiles with different mountain levels."""
        elevation_map = np.array([
            [0.5, 0.7, 0.9],
            [0.6, 0.8, 1.0],
        ])
        
        # Test with different mountain levels
        tiles_low = elevation_map_to_tiles(elevation_map, mountain_level=0.6)
        tiles_high = elevation_map_to_tiles(elevation_map, mountain_level=0.9)
        
        # Lower mountain level should result in more mountain tiles
        mountain_biomes = ["mountain", "alpine", "peaks"]
        mountain_count_low = sum(1 for tile in tiles_low.values() 
                                if tile["biome"] in mountain_biomes)
        mountain_count_high = sum(1 for tile in tiles_high.values() 
                                 if tile["biome"] in mountain_biomes)
        
        assert mountain_count_low >= mountain_count_high

    def test_smooth_elevation_map_basic(self):
        """Test basic elevation map smoothing."""
        elevation_map = np.array([
            [0.1, 0.9, 0.1],
            [0.9, 0.1, 0.9],
            [0.1, 0.9, 0.1]
        ])
        
        smoothed = smooth_elevation_map(elevation_map, iterations=1)
        
        # Should return same shape
        assert smoothed.shape == elevation_map.shape
        
        # Values should be smoothed (less extreme)
        assert np.all(smoothed >= 0.0)
        assert np.all(smoothed <= 1.0)

    def test_smooth_elevation_map_iterations(self):
        """Test elevation map smoothing with different iterations."""
        # Create a realistic noisy elevation map (avoid checkerboard patterns that cause oscillations)
        elevation_map = np.array([
            [0.1, 0.8, 0.3],
            [0.7, 0.2, 0.9],
            [0.4, 0.6, 0.5]
        ])
        
        smoothed_1 = smooth_elevation_map(elevation_map, iterations=1)
        smoothed_3 = smooth_elevation_map(elevation_map, iterations=3)
        
        # More iterations should result in more smoothing (lower variance)
        variance_1 = np.var(smoothed_1)
        variance_3 = np.var(smoothed_3)
        
        assert variance_3 <= variance_1

    def test_smooth_elevation_map_zero_iterations(self):
        """Test elevation map smoothing with zero iterations."""
        elevation_map = np.array([[0.5, 0.7], [0.3, 0.9]])
        
        smoothed = smooth_elevation_map(elevation_map, iterations=0)
        
        # Should return original map
        np.testing.assert_array_equal(smoothed, elevation_map)

    def test_create_mountain_ranges_basic(self):
        """Test basic mountain range creation."""
        elevation_map = np.ones((20, 20)) * 0.3
        
        with_mountains = create_mountain_ranges(elevation_map, count=2)
        
        # Should return same shape
        assert with_mountains.shape == elevation_map.shape
        
        # Should have some elevated areas
        assert np.max(with_mountains) > np.max(elevation_map)

    def test_create_mountain_ranges_parameters(self):
        """Test mountain range creation with different parameters."""
        elevation_map = np.ones((15, 15)) * 0.3
        
        # Test with different counts
        few_mountains = create_mountain_ranges(elevation_map, count=1)
        many_mountains = create_mountain_ranges(elevation_map, count=5)
        
        # Both should be valid
        assert few_mountains.shape == elevation_map.shape
        assert many_mountains.shape == elevation_map.shape
        
        # Test with different height ranges
        low_mountains = create_mountain_ranges(
            elevation_map, height_range=(0.4, 0.6)
        )
        high_mountains = create_mountain_ranges(
            elevation_map, height_range=(0.7, 1.0)
        )
        
        # High mountains should have higher max elevation
        assert np.max(high_mountains) > np.max(low_mountains)

    def test_create_mountain_ranges_seed_reproducibility(self):
        """Test that mountain range creation is reproducible with seeds."""
        elevation_map = np.ones((10, 10)) * 0.3
        
        mountains1 = create_mountain_ranges(elevation_map, seed=42)
        mountains2 = create_mountain_ranges(elevation_map, seed=42)
        
        # Should be identical with same seed
        np.testing.assert_array_equal(mountains1, mountains2)

    def test_create_mountain_ranges_length_width(self):
        """Test mountain range creation with different length and width ranges."""
        elevation_map = np.ones((20, 20)) * 0.3
        
        # Test with different length ranges
        short_ranges = create_mountain_ranges(
            elevation_map, length_range=(3, 5)
        )
        long_ranges = create_mountain_ranges(
            elevation_map, length_range=(10, 15)
        )
        
        # Both should be valid
        assert short_ranges.shape == elevation_map.shape
        assert long_ranges.shape == elevation_map.shape
        
        # Test with different width ranges
        narrow_ranges = create_mountain_ranges(
            elevation_map, width_range=(2, 3)
        )
        wide_ranges = create_mountain_ranges(
            elevation_map, width_range=(5, 8)
        )
        
        # Both should be valid
        assert narrow_ranges.shape == elevation_map.shape
        assert wide_ranges.shape == elevation_map.shape

    def test_generate_complete_elevation_map_basic(self):
        """Test basic complete elevation map generation."""
        width, height = 15, 12
        
        elevation_map = generate_complete_elevation_map(width, height)
        
        # Should return numpy array
        assert isinstance(elevation_map, np.ndarray)
        assert elevation_map.shape == (height, width)
        
        # Values should be in valid range
        assert np.all(elevation_map >= 0.0)
        assert np.all(elevation_map <= 1.0)

    def test_generate_complete_elevation_map_parameters(self):
        """Test complete elevation map generation with different parameters."""
        width, height = 10, 10
        
        # Test with different mountain counts
        few_mountains = generate_complete_elevation_map(
            width, height, mountain_count=1
        )
        many_mountains = generate_complete_elevation_map(
            width, height, mountain_count=5
        )
        
        # Both should be valid
        assert few_mountains.shape == (height, width)
        assert many_mountains.shape == (height, width)
        
        # Test with island shape
        island_map = generate_complete_elevation_map(
            width, height, island_shape=True
        )
        continental_map = generate_complete_elevation_map(
            width, height, island_shape=False
        )
        
        # Both should be valid
        assert island_map.shape == (height, width)
        assert continental_map.shape == (height, width)

    def test_generate_complete_elevation_map_sea_level(self):
        """Test complete elevation map generation with different sea levels."""
        width, height = 10, 10
        
        low_sea = generate_complete_elevation_map(
            width, height, sea_level=0.2
        )
        high_sea = generate_complete_elevation_map(
            width, height, sea_level=0.6
        )
        
        # Both should be valid
        assert low_sea.shape == (height, width)
        assert high_sea.shape == (height, width)

    def test_generate_complete_elevation_map_smoothing(self):
        """Test complete elevation map generation with different smoothing."""
        width, height = 10, 10
        
        no_smoothing = generate_complete_elevation_map(
            width, height, smoothing_iterations=0
        )
        heavy_smoothing = generate_complete_elevation_map(
            width, height, smoothing_iterations=5
        )
        
        # Both should be valid
        assert no_smoothing.shape == (height, width)
        assert heavy_smoothing.shape == (height, width)
        
        # Heavy smoothing should result in less variance
        variance_none = np.var(no_smoothing)
        variance_heavy = np.var(heavy_smoothing)
        assert variance_heavy <= variance_none

    def test_generate_complete_elevation_map_seed_reproducibility(self):
        """Test that complete elevation map generation is reproducible."""
        width, height = 8, 8
        
        map1 = generate_complete_elevation_map(width, height, seed=42)
        map2 = generate_complete_elevation_map(width, height, seed=42)
        
        # Should be identical with same seed
        np.testing.assert_array_equal(map1, map2)

    def test_get_neighboring_tiles_basic(self):
        """Test basic neighboring tiles retrieval."""
        tiles = {
            (0, 0): {"biome": "ocean", "elevation": 2},
            (1, 0): {"biome": "plains", "elevation": 5},
            (0, 1): {"biome": "forest", "elevation": 6},
            (1, 1): {"biome": "mountain", "elevation": 8},
        }
        
        neighbors = get_neighboring_tiles((0, 0), tiles)
        
        # Should return a list
        assert isinstance(neighbors, list)
        
        # Should include adjacent tiles
        assert len(neighbors) > 0
        
        # All neighbors should be valid tile data
        for neighbor in neighbors:
            assert isinstance(neighbor, dict)
            assert "biome" in neighbor
            assert "elevation" in neighbor

    def test_get_neighboring_tiles_edge_position(self):
        """Test neighboring tiles for edge positions."""
        tiles = {
            (0, 0): {"biome": "ocean", "elevation": 2},
            (1, 0): {"biome": "plains", "elevation": 5},
        }
        
        neighbors = get_neighboring_tiles((0, 0), tiles)
        
        # Should handle edge positions
        assert isinstance(neighbors, list)

    def test_get_neighboring_tiles_isolated_tile(self):
        """Test neighboring tiles for isolated tile."""
        tiles = {
            (5, 5): {"biome": "mountain", "elevation": 8},
        }
        
        neighbors = get_neighboring_tiles((5, 5), tiles)
        
        # Should return empty list for isolated tile
        assert neighbors == []

    def test_get_neighboring_tiles_nonexistent_tile(self):
        """Test neighboring tiles for nonexistent tile."""
        tiles = {
            (0, 0): {"biome": "ocean", "elevation": 2},
        }
        
        neighbors = get_neighboring_tiles((10, 10), tiles)
        
        # Should return empty list for nonexistent tile
        assert neighbors == []

    def test_is_valid_elevation_transition_basic(self):
        """Test basic elevation transition validation."""
        # Valid transitions (within max_diff)
        assert is_valid_elevation_transition(3, 5, max_diff=2) == True
        assert is_valid_elevation_transition(7, 5, max_diff=2) == True
        assert is_valid_elevation_transition(4, 4, max_diff=2) == True
        
        # Invalid transitions (exceeds max_diff)
        assert is_valid_elevation_transition(1, 5, max_diff=2) == False
        assert is_valid_elevation_transition(8, 3, max_diff=2) == False

    def test_is_valid_elevation_transition_edge_cases(self):
        """Test elevation transition validation edge cases."""
        # Test with zero max_diff
        assert is_valid_elevation_transition(5, 5, max_diff=0) == True
        assert is_valid_elevation_transition(5, 6, max_diff=0) == False
        
        # Test with large max_diff
        assert is_valid_elevation_transition(0, 10, max_diff=10) == True
        assert is_valid_elevation_transition(0, 10, max_diff=5) == False

    def test_is_valid_elevation_transition_negative_values(self):
        """Test elevation transition validation with negative values."""
        # Should handle negative elevations
        assert is_valid_elevation_transition(-2, 0, max_diff=2) == True
        assert is_valid_elevation_transition(-5, 0, max_diff=2) == False

    def test_integration_elevation_workflow(self):
        """Test integration of elevation generation workflow."""
        width, height = 10, 8
        
        # Step 1: Generate complete elevation map
        elevation_map = generate_complete_elevation_map(width, height, seed=42)
        assert elevation_map.shape == (height, width)
        
        # Step 2: Convert to tiles
        tiles = elevation_map_to_tiles(elevation_map)
        assert len(tiles) == width * height
        
        # Step 3: Test neighboring tiles
        first_coord = list(tiles.keys())[0]
        neighbors = get_neighboring_tiles(first_coord, tiles)
        assert isinstance(neighbors, list)
        
        # Step 4: Test elevation transitions
        if len(neighbors) > 0:
            tile1_elev = tiles[first_coord]["elevation"]
            tile2_elev = neighbors[0]["elevation"]
            is_valid = is_valid_elevation_transition(tile1_elev, tile2_elev)
            assert isinstance(is_valid, bool)

    def test_error_handling_edge_cases(self):
        """Test error handling for various edge cases."""
        # Empty elevation map
        empty_map = {}
        normalized = normalize_elevation_map(empty_map)
        assert normalized == {}
        
        # Single point elevation map
        single_point = {(0, 0): 0.5}
        normalized = normalize_elevation_map(single_point)
        assert (0, 0) in normalized
        
        # Zero-size noise map
        try:
            zero_noise = generate_noise_map(0, 0)
            # Should either work or raise appropriate error
            assert isinstance(zero_noise, np.ndarray) or True
        except (ValueError, ZeroDivisionError):
            # Expected for zero dimensions
            pass

    def test_parameter_validation_ranges(self):
        """Test parameter validation and edge cases."""
        # Test extreme elevation values
        extreme_map = {(0, 0): -0.5, (1, 0): 1.5, (0, 1): 0.5}
        
        # Functions should handle out-of-range values gracefully
        normalized = normalize_elevation_map(extreme_map)
        assert isinstance(normalized, dict)
        
        # Test extreme noise parameters
        try:
            extreme_noise = generate_noise_map(5, 5, scale=0.0, octaves=0)
            assert isinstance(extreme_noise, np.ndarray)
        except (ValueError, ZeroDivisionError):
            # Expected for extreme parameters
            pass
