from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
from backend.systems.data.registry import GameDataRegistry
from typing import Any
from typing import List
"""
Tests for the region.worldgen module.

This module contains tests for world generator functionality which
creates continents, regions, and POIs.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
import random
from typing import Dict, Tuple, List, Any

from backend.systems.region.world_generator import WorldGenerator
from backend.systems.data import GameDataRegistry


class TestWorldGenerator:
    """Tests for the WorldGenerator class."""

    @pytest.fixture
    def mock_data_registry(self):
        """Create a mock data registry."""
        registry = MagicMock(spec=GameDataRegistry)
        registry.biomes = {
            "forest": {
                "name": "Forest",
                "min_temperature": 0.3,
                "max_temperature": 0.7,
                "min_humidity": 0.5,
                "max_humidity": 1.0,
                "min_elevation": 0.2,
                "max_elevation": 0.8,
            },
            "plains": {
                "name": "Plains",
                "min_temperature": 0.3,
                "max_temperature": 0.7,
                "min_humidity": 0.3,
                "max_humidity": 0.6,
                "min_elevation": 0.1,
                "max_elevation": 0.5,
            },
            "mountain": {
                "name": "Mountain",
                "min_temperature": 0.0,
                "max_temperature": 0.5,
                "min_humidity": 0.3,
                "max_humidity": 0.8,
                "min_elevation": 0.6,
                "max_elevation": 1.0,
            },
            "desert": {
                "name": "Desert",
                "min_temperature": 0.7,
                "max_temperature": 1.0,
                "min_humidity": 0.0,
                "max_humidity": 0.3,
                "min_elevation": 0.1,
                "max_elevation": 0.6,
            },
            "tundra": {
                "name": "Tundra",
                "min_temperature": 0.0,
                "max_temperature": 0.3,
                "min_humidity": 0.3,
                "max_humidity": 0.6,
                "min_elevation": 0.1,
                "max_elevation": 0.5,
            },
        }
        registry.resources = {
            "wood": {"name": "Wood", "biome_weights": {"forest": 0.8, "plains": 0.4}},
            "stone": {
                "name": "Stone",
                "biome_weights": {"mountain": 0.9, "plains": 0.5},
            },
            "water": {
                "name": "Water",
                "biome_weights": {"forest": 0.6, "plains": 0.5, "desert": 0.1},
            },
        }
        
        # Add missing methods
        registry.get_land_types.return_value = registry.biomes
        registry.get_poi_name_templates = MagicMock(return_value={})
        
        return registry

    @pytest.fixture
    def world_generator(self, mock_data_registry, temp_data_dir):
        """Create a WorldGenerator instance with controlled seed."""
        # Use a fixed seed for deterministic tests
        return WorldGenerator(
            data_registry=mock_data_registry, seed=12345, data_dir=temp_data_dir
        )

    @patch("os.makedirs")
    def test_initialization(self, mock_makedirs, mock_data_registry, temp_data_dir):
        """Test that the WorldGenerator initializes correctly."""
        generator = WorldGenerator(
            data_registry=mock_data_registry, seed=12345, data_dir=temp_data_dir
        )

        # Check that the seed was set and generators were initialized
        assert generator.seed == 12345
        assert generator.data_registry == mock_data_registry
        assert generator.continent_generator is not None
        assert generator.region_generator is not None

        # Check that the data directories were set correctly
        assert generator.data_dir == temp_data_dir
        assert generator.world_data_dir == os.path.join(temp_data_dir, "world")

        # Check that the directories were created
        mock_makedirs.assert_called_with(generator.world_data_dir, exist_ok=True)

    @patch("backend.systems.region.generators.ContinentGenerator.generate_continent")
    @patch("backend.systems.region.generators.RegionGenerator.generate_region")
    @patch("random.uniform")
    def test_generate_world(
        self,
        mock_uniform,
        mock_generate_region,
        mock_generate_continent,
        world_generator,
    ):
        """Test generating a complete world."""
        # Set up mock continents
        continents = []
        for i in range(2):
            continent = MagicMock()
            continent.continent_id = f"c_test{i}"
            continent.region_coordinates = [(i, 0), (i, 1)]
            continent.region_ids = [f"r_test{i}_0", f"r_test{i}_1"]
            continent.boundary = {
                "min_x": i - 0.5,
                "max_x": i + 0.5,
                "min_y": -0.5,
                "max_y": 1.5
            }
            continents.append(continent)

        mock_generate_continent.side_effect = continents

        # Set up mock regions
        regions = []
        for i in range(4):
            region = MagicMock()
            region.region_id = f"r_test{i//2}_{i%2}"
            region.coordinates = (i // 2, i % 2)
            region.biome_type = "forest" if i % 2 == 0 else "plains"
            regions.append(region)

        mock_generate_region.side_effect = regions

        # Control random values for POI generation
        mock_uniform.return_value = 0.25

        # Generate the world
        with patch.object(world_generator, "_save_world_data") as mock_save:
            result = world_generator.generate_world(continent_count=2)

        # Check that continents and regions were generated
        assert mock_generate_continent.call_count == 2
        assert mock_generate_region.call_count == 4

        # Check that world metadata was updated correctly
        assert result["continent_count"] == 2
        assert result["region_count"] == 4
        assert "updated_at" in result

        # Check that world data was saved
        mock_save.assert_called_once()

        # Check that continents and regions were stored
        assert len(world_generator.continents) == 2
        assert len(world_generator.regions) == 4
        assert "c_test0" in world_generator.continents
        assert "c_test1" in world_generator.continents
        assert "r_test0_0" in world_generator.regions
        assert "r_test0_1" in world_generator.regions
        assert "r_test1_0" in world_generator.regions
        assert "r_test1_1" in world_generator.regions

    def test_get_adjacent_coordinates(self, world_generator):
        """Test getting adjacent coordinates."""
        coords = (10, 20)

        # Get adjacent coordinates using the hex neighbors function
        from backend.systems.region.models import get_hex_neighbors
        adjacent = get_hex_neighbors(coords)

        # Check the result - hex neighbors have 6 directions
        assert len(adjacent) == 6
        # Check that all coordinates are adjacent to the original
        for adj_coord in adjacent:
            x_diff = abs(adj_coord[0] - coords[0])
            y_diff = abs(adj_coord[1] - coords[1])
            assert x_diff <= 1 and y_diff <= 1

    def test_create_profile_constraints(self, world_generator):
        """Test creating profile constraints for a region."""
        # Set a deterministic seed
        random.seed(12345)

        coords = (10, 20)
        continent_boundary = {"min_x": 0, "max_x": 20, "min_y": 0, "max_y": 40}
        base_constraints = {}

        # Create profile constraints
        constraints = world_generator._create_profile_constraints(
            coords, continent_boundary, base_constraints
        )

        # Check that all expected constraint types are present
        assert "temperature" in constraints
        assert "humidity" in constraints
        assert "elevation" in constraints
        assert "ruggedness" in constraints

        # Check that constraints are within valid ranges
        temp_min, temp_max = constraints["temperature"]
        assert 0 <= temp_min <= temp_max <= 1

        humid_min, humid_max = constraints["humidity"]
        assert 0 <= humid_min <= humid_max <= 1

        elev_min, elev_max = constraints["elevation"]
        assert 0 <= elev_min <= elev_max <= 1

        rug_min, rug_max = constraints["ruggedness"]
        assert 0 <= rug_min <= rug_max <= 1

    def test_generate_pois_for_region(self, world_generator):
        """Test generating POIs for a region."""
        # Set a deterministic seed
        random.seed(12345)
        
        # Set up mock region
        region = MagicMock()
        region.region_id = "r_test123"
        region.biome_type = "forest"
        region.coordinates = (10, 20)

        # Set up existing regions
        existing_regions = {}

        # Generate POIs
        pois = world_generator._generate_pois_for_region(region, existing_regions)

        # Check result - should have 1 major POI (MAJOR_POIS_PER_REGION = 1)
        assert len(pois) >= 1
        
        # Check that POI IDs and coordinates are set
        for i, poi in enumerate(pois):
            assert poi.poi_id.startswith("poi_")
            assert poi.poi_id.endswith(str(i))
            assert poi.coordinates[0] != poi.coordinates[1]  # Coordinates should be different
            assert poi.poi_type in ["city", "town", "village", "dungeon", "outpost", "metropolis"]
            assert poi.category in ["social", "combat", "neutral"]
            assert poi.population >= 0

    @patch("os.makedirs")
    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_save_world_data(
        self, mock_file, mock_json_dump, mock_makedirs, world_generator
    ):
        """Test saving world data to disk."""
        # Add some test data
        world_generator.world_metadata = {
            "seed": 12345,
            "continent_count": 2,
            "region_count": 4,
        }

        continent1 = MagicMock()
        continent1.continent_id = "c_test1"
        continent2 = MagicMock()
        continent2.continent_id = "c_test2"
        world_generator.continents = {"c_test1": continent1, "c_test2": continent2}

        region1 = MagicMock()
        region1.region_id = "r_test1"
        region2 = MagicMock()
        region2.region_id = "r_test2"
        world_generator.regions = {"r_test1": region1, "r_test2": region2}

        # Save the world data
        world_generator._save_world_data()

        # Check that directories were created
        mock_makedirs.assert_any_call(
            os.path.join(world_generator.world_data_dir, "continents"), exist_ok=True
        )
        mock_makedirs.assert_any_call(
            os.path.join(world_generator.world_data_dir, "regions"), exist_ok=True
        )

        # Check that files were opened
        expected_files = [
            os.path.join(world_generator.world_data_dir, "world_metadata.json"),
            os.path.join(world_generator.world_data_dir, "continents", "c_test1.json"),
            os.path.join(world_generator.world_data_dir, "continents", "c_test2.json"),
            os.path.join(world_generator.world_data_dir, "regions", "r_test1.json"),
            os.path.join(world_generator.world_data_dir, "regions", "r_test2.json"),
        ]

        assert mock_file.call_count == 5
        opened_files = [args[0] for args, _ in mock_file.call_args_list]
        assert set(opened_files) == set(expected_files)

        # Check that json.dump was called for each file
        assert mock_json_dump.call_count == 5

    def test_integration_world_generation(self, world_generator, temp_data_dir):
        """
        Integration test for world generation.

        This test actually runs the world generation process and checks
        that all components are generated and saved correctly.
        """
        # Generate a small world
        result = world_generator.generate_world(continent_count=1)

        # Check world metadata
        assert result["continent_count"] == 1
        assert result["region_count"] > 0
        assert result["seed"] == 12345

        # Check that continents and regions were created
        assert len(world_generator.continents) == 1
        assert len(world_generator.regions) > 0

        # Check that files were created
        world_metadata_path = os.path.join(
            temp_data_dir, "world", "world_metadata.json"
        )
        assert os.path.exists(world_metadata_path)

        # Check continent files
        continent_id = list(world_generator.continents.keys())[0]
        continent_path = os.path.join(
            temp_data_dir, "world", "continents", f"{continent_id}.json"
        )
        assert os.path.exists(continent_path)

        # Check region files
        region_id = list(world_generator.regions.keys())[0]
        region_path = os.path.join(
            temp_data_dir, "world", "regions", f"{region_id}.json"
        )
        assert os.path.exists(region_path)

        # Check file contents
        with open(world_metadata_path, "r") as f:
            world_data = json.load(f)
            assert world_data["seed"] == 12345
            assert world_data["continent_count"] == 1
            assert world_data["region_count"] > 0

        with open(continent_path, "r") as f:
            continent_data = json.load(f)
            assert continent_data["continent_id"] == continent_id
            assert "name" in continent_data
            assert "region_coordinates" in continent_data
            assert "region_ids" in continent_data

        with open(region_path, "r") as f:
            region_data = json.load(f)
            assert region_data["region_id"] == region_id
            assert "name" in region_data
            assert "biome_type" in region_data
            assert "coordinates" in region_data
