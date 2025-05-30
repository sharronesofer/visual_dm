"""
Tests for the region.continent module.

This module contains tests for continent generator functionality which
creates continent structures with region coordinates.
"""

import pytest
from unittest.mock import patch, MagicMock
import random
from datetime import datetime

from backend.systems.region.generators import ContinentGenerator
from backend.systems.region.models import ContinentMetadata, CONTINENT_SIZE_RANGE


class TestContinentGenerator:
    """Tests for the ContinentGenerator class."""

    @pytest.fixture
    def continent_generator(self):
        """Create a ContinentGenerator instance with a fixed seed."""
        # Use a fixed seed for deterministic tests
        return ContinentGenerator(seed=12345)

    def test_initialization(self):
        """Test that the ContinentGenerator initializes correctly."""
        # Test with explicit seed
        generator = ContinentGenerator(seed=12345)
        assert generator.seed == 12345

        # Test with default seed (should be random)
        with patch("random.randint", return_value=54321) as mock_randint:
            generator = ContinentGenerator()
            mock_randint.assert_called_once()
            assert generator.seed == 54321

    def test_generate_continent_default(self, continent_generator):
        """Test generating a continent with default parameters."""
        # Set a deterministic seed for random operations
        random.seed(12345)

        # Generate a continent
        continent = continent_generator.generate_continent()

        # Check basic properties
        assert continent.continent_id.startswith("c_")
        assert len(continent.continent_id) > 3
        assert continent.name.startswith("Continent")
        assert len(continent.region_coordinates) >= CONTINENT_SIZE_RANGE[0]
        assert len(continent.region_coordinates) <= CONTINENT_SIZE_RANGE[1]
        assert len(continent.region_ids) == len(continent.region_coordinates)
        assert all(region_id.startswith("r_") for region_id in continent.region_ids)
        assert continent.seed == 12345
        assert isinstance(continent.created_at, str)

        # Check that the boundary is calculated correctly
        assert isinstance(continent.boundary, dict)
        assert "min_x" in continent.boundary
        assert "max_x" in continent.boundary
        assert "min_y" in continent.boundary
        assert "max_y" in continent.boundary

        # Check that the boundary encompasses all region coordinates
        for x, y in continent.region_coordinates:
            assert continent.boundary["min_x"] <= x <= continent.boundary["max_x"]
            assert continent.boundary["min_y"] <= y <= continent.boundary["max_y"]

    def test_generate_continent_with_params(self, continent_generator):
        """Test generating a continent with specific parameters."""
        # Set custom parameters
        continent_id = "c_test123"
        continent_name = "Test Continent"
        origin = (5, 5)
        size = 15

        # Generate a continent
        continent = continent_generator.generate_continent(
            continent_id=continent_id,
            continent_name=continent_name,
            origin=origin,
            size=size,
        )

        # Check that parameters were used
        assert continent.continent_id == continent_id
        assert continent.name == continent_name
        assert continent.origin == origin
        assert len(continent.region_coordinates) == size

        # Check that origin is included in coordinates
        assert origin in continent.region_coordinates

    def test_random_walk_continent(self, continent_generator):
        """Test the random walk algorithm for continent generation."""
        # Set a deterministic seed for random operations
        random.seed(12345)

        # Generate continent using random walk
        origin = (0, 0)
        size = 20
        region_coords = continent_generator._random_walk_continent(origin, size)

        # Check results
        assert len(region_coords) == size
        assert origin in region_coords

        # Check that all coordinates are connected (each has at least one neighbor)
        for coord in region_coords:
            # Get all possible neighbors
            neighbors = [
                (coord[0] + 1, coord[1]),  # East
                (coord[0] + 1, coord[1] - 1),  # Northeast
                (coord[0], coord[1] - 1),  # Northwest
                (coord[0] - 1, coord[1]),  # West
                (coord[0] - 1, coord[1] + 1),  # Southwest
                (coord[0], coord[1] + 1),  # Southeast
            ]

            # Check that at least one neighbor is in region_coords
            assert any(
                n in region_coords for n in neighbors
            ), f"Coordinate {coord} has no neighbors"

    def test_calculate_boundary(self, continent_generator):
        """Test boundary calculation for a set of coordinates."""
        # Test with a simple set of coordinates
        coords = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 3), (-1, -2)]

        boundary = continent_generator._calculate_boundary(coords)

        # Check results
        assert boundary["min_x"] == -1
        assert boundary["max_x"] == 2
        assert boundary["min_y"] == -2
        assert boundary["max_y"] == 3

        # Test with empty coordinates
        empty_boundary = continent_generator._calculate_boundary([])
        assert empty_boundary == {"min_x": 0, "max_x": 0, "min_y": 0, "max_y": 0}

    def test_is_region_in_continent(self, continent_generator):
        """Test checking if a region is in a continent."""
        # Create a continent
        continent = MagicMock(spec=ContinentMetadata)
        continent.region_coordinates = [(0, 0), (1, 0), (0, 1), (1, 1)]

        # Test with coordinates in the continent
        assert continent_generator.is_region_in_continent((0, 0), continent) is True
        assert continent_generator.is_region_in_continent((1, 1), continent) is True

        # Test with coordinates not in the continent
        assert continent_generator.is_region_in_continent((2, 2), continent) is False
        assert continent_generator.is_region_in_continent((-1, 0), continent) is False

    def test_get_continent_area(self, continent_generator):
        """Test calculating the area of a continent."""
        # Create a continent with a known number of regions
        continent = MagicMock(spec=ContinentMetadata)
        continent.region_coordinates = [(i, 0) for i in range(10)]  # 10 regions

        # Calculate area
        area = continent_generator.get_continent_area(continent)

        # Each region is 39 sq km, so 10 regions = 390 sq km
        assert area == 10 * 39.0

    def test_get_continent_dimensions(self, continent_generator):
        """Test calculating the dimensions of a continent."""
        # Create a continent with a known boundary
        continent = MagicMock(spec=ContinentMetadata)
        continent.boundary = {"min_x": 0, "max_x": 9, "min_y": 0, "max_y": 4}

        # Calculate dimensions
        width_km, height_km = continent_generator.get_continent_dimensions(continent)

        # Width is 10 regions (0-9 inclusive), height is 5 regions (0-4 inclusive)
        # Region size is sqrt(39) km
        expected_region_size_km = 6.244997998398398  # sqrt(39)
        assert width_km == pytest.approx(10 * expected_region_size_km)
        assert height_km == pytest.approx(5 * expected_region_size_km)

    def test_generate_continent_integration(self, continent_generator):
        """
        Integration test for the entire continent generation process.

        This test verifies that the generate_continent method properly
        coordinates all the generation steps.
        """
        # Set a deterministic seed for random operations
        random.seed(12345)

        # Generate a continent with custom parameters
        continent = continent_generator.generate_continent(
            continent_name="Test Continent", origin=(0, 0), size=30
        )

        # Check the result
        assert continent.name == "Test Continent"
        assert continent.origin == (0, 0)
        assert len(continent.region_coordinates) == 30
        assert len(continent.region_ids) == 30
        assert continent.seed == 12345

        # Test get_continent_area and get_continent_dimensions
        area = continent_generator.get_continent_area(continent)
        width_km, height_km = continent_generator.get_continent_dimensions(continent)

        # Area should be 30 regions * 39 sq km
        assert area == 30 * 39.0

        # Dimensions should be consistent with the boundary
        boundary_width = continent.boundary["max_x"] - continent.boundary["min_x"] + 1
        boundary_height = continent.boundary["max_y"] - continent.boundary["min_y"] + 1
        expected_region_size_km = 6.244997998398398  # sqrt(39)

        assert width_km == pytest.approx(boundary_width * expected_region_size_km)
        assert height_km == pytest.approx(boundary_height * expected_region_size_km)
