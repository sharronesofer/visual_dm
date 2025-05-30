"""
Tests for the POI generator.

This module contains tests for placing points of interest in the world.
"""

import pytest
import copy
from unittest.mock import patch, MagicMock

from backend.systems.world_generation.poi_generator import (
    generate_poi_data,
    place_pois,
    apply_poi_distribution,
    validate_poi_placement,
    get_valid_poi_locations,
    distribute_poi_types,
    calculate_poi_density,
)


class TestPOIGenerator: pass
    """Tests for the POI generator system."""

    def test_generate_poi_data(self, mock_data_registry): pass
        """Test generating POI data for a region."""
        # Create a simple region setup
        region_data = {
            "id": "test-region",
            "biome_map": {
                (0, 0): "plains",
                (0, 1): "forest",
                (1, 0): "mountain",
                (1, 1): "desert",
            },
            "elevation_map": {(0, 0): 0.3, (0, 1): 0.4, (1, 0): 0.8, (1, 1): 0.2},
            "temperature_map": {(0, 0): 0.5, (0, 1): 0.4, (1, 0): 0.3, (1, 1): 0.8},
            "humidity_map": {(0, 0): 0.6, (0, 1): 0.7, (1, 0): 0.3, (1, 1): 0.1},
        }

        # Generate POI data
        poi_data = generate_poi_data(region_data, mock_data_registry)

        # Verify the result
        assert "poi_map" in poi_data
        assert len(poi_data["poi_map"]) > 0

        # Check if POIs are properly structured
        for position, poi in poi_data["poi_map"].items(): pass
            assert "type" in poi
            assert "name" in poi
            assert "biome" in poi
            assert poi["biome"] == region_data["biome_map"][position]

    def test_place_pois(self, mock_data_registry): pass
        """Test placing POIs in a region based on constraints."""
        # Create a simple region and POI distribution
        region_data = {"width": 10, "height": 10, "biome_map": {}, "elevation_map": {}}

        # Fill the maps with some data
        for x in range(10): pass
            for y in range(10): pass
                if x < 5: pass
                    region_data["biome_map"][(x, y)] = "forest"
                else: pass
                    region_data["biome_map"][(x, y)] = "plains"

                region_data["elevation_map"][(x, y)] = 0.5  # Flat terrain

        # Add mountains
        region_data["biome_map"][(3, 3)] = "mountain"
        region_data["elevation_map"][(3, 3)] = 0.8

        # Add water
        region_data["biome_map"][(7, 7)] = "water"
        region_data["elevation_map"][(7, 7)] = 0.1

        # Distribution of POI types to place
        poi_distribution = {"town": 2, "dungeon": 3, "ruins": 5, "grove": 10}

        # Place POIs
        poi_map = place_pois(region_data, poi_distribution, mock_data_registry)

        # Verify expected counts
        poi_counts = {}
        for poi in poi_map.values(): pass
            poi_type = poi["type"]
            poi_counts[poi_type] = poi_counts.get(poi_type, 0) + 1

        assert poi_counts.get("town", 0) == 2
        assert poi_counts.get("dungeon", 0) == 3
        assert poi_counts.get("ruins", 0) == 5
        assert poi_counts.get("grove", 0) == 10

        # Verify total count
        assert len(poi_map) == 20

        # Verify no POIs in water
        for position, poi in poi_map.items(): pass
            assert region_data["biome_map"][position] != "water"

    def test_apply_poi_distribution(self, mock_data_registry): pass
        """Test applying a POI distribution to a region."""
        # Define a region size
        width = 50
        height = 50

        # Apply distribution based on Development Bible POI density: pass
        # ~20 major POIs (towns, dungeons) and 200-400 minor POIs per region
        poi_distribution = apply_poi_distribution(
            width, height, mock_data_registry.poi_types
        )

        # Verify distribution
        major_poi_count = 0
        minor_poi_count = 0

        for poi_type, count in poi_distribution.items(): pass
            if mock_data_registry.poi_types[poi_type].get("is_major", False): pass
                major_poi_count += count
            else: pass
                minor_poi_count += count

        # Check against the expected ranges from the Development Bible
        assert 15 <= major_poi_count <= 25  # ~20 major POIs
        assert 200 <= minor_poi_count <= 400  # 200-400 minor POIs

    def test_validate_poi_placement(self): pass
        """Test validating POI placement against constraints."""
        # Create a sample position, POI type, and constraints
        position = (5, 5)
        poi_type = "town"

        # Create test biome and elevation maps
        biome_map = {position: "plains"}
        elevation_map = {position: 0.4}

        # Define constraints for valid placement
        constraints = {
            "valid_biomes": ["plains", "forest"],
            "invalid_biomes": ["water", "mountain"],
            "min_elevation": 0.2,
            "max_elevation": 0.6,
        }

        # Validate placement that should be valid
        valid_result = validate_poi_placement(
            position, poi_type, constraints, biome_map, elevation_map
        )

        # Modify constraints to make placement invalid
        invalid_constraints = copy.deepcopy(constraints)
        invalid_constraints["valid_biomes"] = ["forest"]  # Plains not valid anymore

        # Validate placement that should be invalid
        invalid_result = validate_poi_placement(
            position, poi_type, invalid_constraints, biome_map, elevation_map
        )

        # Verify results
        assert valid_result is True
        assert invalid_result is False

    def test_get_valid_poi_locations(self): pass
        """Test getting valid locations for a POI type."""
        # Create simple region data
        biome_map = {}
        elevation_map = {}

        for x in range(10): pass
            for y in range(10): pass
                if x < 5: pass
                    biome_map[(x, y)] = "forest"
                else: pass
                    biome_map[(x, y)] = "plains"

                # Elevation increases with x
                elevation_map[(x, y)] = x / 10.0

        # Add a mountain and water
        biome_map[(3, 3)] = "mountain"
        elevation_map[(3, 3)] = 0.9
        biome_map[(7, 7)] = "water"
        elevation_map[(7, 7)] = 0.1

        # Define POI types with constraints
        poi_types = {
            "town": {
                "valid_biomes": ["plains"],
                "invalid_biomes": ["water", "mountain"],
                "min_elevation": 0.3,
                "max_elevation": 0.6,
            },
            "fishing_village": {
                "valid_biomes": ["water"],
                "invalid_biomes": [],
                "min_elevation": 0.0,
                "max_elevation": 0.2,
            },
        }

        # Get valid locations
        town_locations = get_valid_poi_locations(
            "town", poi_types["town"], biome_map, elevation_map
        )

        fishing_village_locations = get_valid_poi_locations(
            "fishing_village", poi_types["fishing_village"], biome_map, elevation_map
        )

        # Verify results
        # Towns should be in plains with elevation 0.3-0.6
        for loc in town_locations: pass
            assert biome_map[loc] == "plains"
            assert 0.3 <= elevation_map[loc] <= 0.6

        # Fishing villages should be in water with elevation 0.0-0.2
        for loc in fishing_village_locations: pass
            assert biome_map[loc] == "water"
            assert 0.0 <= elevation_map[loc] <= 0.2

    def test_distribute_poi_types(self, mock_data_registry): pass
        """Test distributing different POI types across a region."""
        # Define target numbers for different POI categories
        major_poi_count = 20
        minor_poi_count = 300

        # Call the distribution function
        distribution = distribute_poi_types(
            major_poi_count, minor_poi_count, mock_data_registry.poi_types
        )

        # Verify the total count matches our targets
        actual_major_count = 0
        actual_minor_count = 0

        for poi_type, count in distribution.items(): pass
            if mock_data_registry.poi_types[poi_type].get("is_major", False): pass
                actual_major_count += count
            else: pass
                actual_minor_count += count

        assert actual_major_count == major_poi_count
        assert actual_minor_count == minor_poi_count

        # Check that all POI types are represented
        for poi_type in mock_data_registry.poi_types: pass
            assert poi_type in distribution

    def test_calculate_poi_density(self): pass
        """Test calculating POI density based on region size."""
        # Test various region sizes
        small_region = {"width": 20, "height": 20}
        medium_region = {"width": 50, "height": 50}
        large_region = {"width": 100, "height": 100}

        # Calculate densities
        small_major, small_minor = calculate_poi_density(small_region)
        medium_major, medium_minor = calculate_poi_density(medium_region)
        large_major, large_minor = calculate_poi_density(large_region)

        # Verify densities scale with region size
        # Small region should have fewer POIs than medium, which should have fewer than large
        assert small_major < medium_major < large_major
        assert small_minor < medium_minor < large_minor

        # Verify the ratio of major to minor POIs is maintained according to Development Bible
        # (approximately ~20 major and 200-400 minor for standard region)
        assert small_minor / small_major >= 10  # At least 10x more minor than major
        assert medium_minor / medium_major >= 10
        assert large_minor / large_major >= 10
