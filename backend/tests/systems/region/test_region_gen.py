from backend.systems.data.registry import GameDataRegistry
from backend.systems.economy.models import Resource
from backend.systems.data.registry import GameDataRegistry
from backend.systems.economy.models import Resource
from backend.systems.data.registry import GameDataRegistry
from backend.systems.economy.models import Resource
from backend.systems.data.registry import GameDataRegistry
from backend.systems.economy.models import Resource
from backend.systems.data.registry import GameDataRegistry
from backend.systems.economy.models import Resource
from backend.systems.data.registry import GameDataRegistry
from backend.systems.economy.models import Resource
from typing import Any
from typing import List
from typing import Optional
"""
Tests for the region.region_gen module.

This module contains tests for the region generator functionality which
creates regions with appropriate biomes, resources, and features.
"""

import pytest
from unittest.mock import patch, MagicMock
import random
from typing import Dict, List, Any, Tuple, Optional

from backend.systems.region.generators import RegionGenerator
from backend.systems.region.models import (
    RegionMetadata,
    RegionProfile,
    REGION_AREA_SQ_KM,
)
from backend.systems.data import GameDataRegistry


class TestRegionGenerator: pass
    """Tests for the RegionGenerator class."""

    @pytest.fixture
    def mock_data_registry(self): pass
        """Create a mock data registry with test biome data."""
        registry = MagicMock(spec=GameDataRegistry)

        # Set up biome data
        registry.get_land_types.return_value = {
            "forest": {
                "name": "Forest",
                "description": "Dense wooded area",
                "resource_weights": {"wood": 0.8, "herbs": 0.6, "water": 0.6},
                "feature_chances": {"trees": 0.9, "clearing": 0.4, "river": 0.3},
                "temperature_range": (0.3, 0.7),
                "humidity_range": (0.5, 1.0),
                "elevation_range": (0.2, 0.7),
            },
            "plains": {
                "name": "Plains",
                "description": "Flat grasslands",
                "resource_weights": {"herbs": 0.5, "game": 0.7},
                "feature_chances": {"grass": 0.9, "wildflowers": 0.6, "hills": 0.3},
                "temperature_range": (0.3, 0.8),
                "humidity_range": (0.3, 0.6),
                "elevation_range": (0.1, 0.4),
            },
            "mountain": {
                "name": "Mountain",
                "description": "Elevated rocky terrain",
                "resource_weights": {"stone": 0.9, "ore": 0.7},
                "feature_chances": {"peaks": 0.8, "caves": 0.5, "snow": 0.4},
                "temperature_range": (0.0, 0.5),
                "humidity_range": (0.3, 0.7),
                "elevation_range": (0.7, 1.0),
            },
            "desert": {
                "name": "Desert",
                "description": "Arid sandy area",
                "resource_weights": {"sand": 0.9, "minerals": 0.5},
                "feature_chances": {"dunes": 0.8, "oasis": 0.2, "cacti": 0.6},
                "temperature_range": (0.7, 1.0),
                "humidity_range": (0.0, 0.3),
                "elevation_range": (0.1, 0.6),
            },
        }

        # Set up adjacency rules
        registry.get_adjacency_rules.return_value = {
            "forest": ["plains", "mountain"],
            "plains": ["forest", "desert", "mountain"],
            "mountain": ["forest", "plains", "desert"],
            "desert": ["plains", "mountain"],
        }

        return registry

    @pytest.fixture
    def region_generator(self, mock_data_registry): pass
        """Create a RegionGenerator instance with a fixed seed."""
        # Use a fixed seed for deterministic tests
        return RegionGenerator(data_registry=mock_data_registry, seed=12345)

    def test_initialization(self, mock_data_registry): pass
        """Test that the RegionGenerator initializes correctly."""
        # Test with explicit seed
        generator = RegionGenerator(data_registry=mock_data_registry, seed=12345)
        assert generator.seed == 12345
        assert generator.data_registry == mock_data_registry
        assert generator.biomes == mock_data_registry.get_land_types()
        assert generator.adjacency_rules == mock_data_registry.get_adjacency_rules()

        # Test with default seed (should be random)
        with patch("random.randint", return_value=54321) as mock_randint: pass
            generator = RegionGenerator(data_registry=mock_data_registry)
            mock_randint.assert_called_once()
            assert generator.seed == 54321

    def test_generate_region_default(self, region_generator): pass
        """Test generating a region with default parameters."""
        # Set a deterministic seed for random operations
        random.seed(12345)

        # Generate a region
        region = region_generator.generate_region()

        # Check basic properties
        assert region.region_id is not None
        assert region.name is not None
        assert region.coordinates is not None
        assert region.continent_id is not None
        assert region.biome_type in region_generator.biomes
        assert isinstance(region.profile, RegionProfile)
        assert isinstance(region.resources, dict)
        assert isinstance(region.features, list)
        assert region.area_sqkm == REGION_AREA_SQ_KM
        assert isinstance(region.hex_coordinates, list)
        assert len(region.hex_coordinates) > 0
        assert region.seed == 12345
        assert isinstance(region.created_at, str)

        # Check profile values
        assert 0 <= region.profile.temperature <= 1
        assert 0 <= region.profile.humidity <= 1
        assert 0 <= region.profile.elevation <= 1
        assert 0 <= region.profile.ruggedness <= 1

    def test_generate_region_with_params(self, region_generator): pass
        """Test generating a region with specific parameters."""
        # Set custom parameters
        region_id = "r_test123"
        name = "Test Region"
        coordinates = (10, 20)
        continent_id = "c_test456"
        forced_biome = "forest"
        profile_constraints = {
            "temperature": (0.3, 0.5),
            "humidity": (0.6, 0.8),
            "elevation": (0.2, 0.4),
            "ruggedness": (0.1, 0.3),
        }

        # Generate a region
        region = region_generator.generate_region(
            region_id=region_id,
            name=name,
            coordinates=coordinates,
            continent_id=continent_id,
            forced_biome=forced_biome,
            profile_constraints=profile_constraints,
        )

        # Check that parameters were used
        assert region.region_id == region_id
        assert region.name == name
        assert region.coordinates == coordinates
        assert region.continent_id == continent_id
        assert region.biome_type == forced_biome

        # Check that profile constraints were respected
        assert 0.3 <= region.profile.temperature <= 0.5
        assert 0.6 <= region.profile.humidity <= 0.8
        assert 0.2 <= region.profile.elevation <= 0.4
        assert 0.1 <= region.profile.ruggedness <= 0.3

    def test_generate_profile(self, region_generator): pass
        """Test generating environmental profiles for regions."""
        # Set a deterministic seed for random operations
        random.seed(12345)

        # Generate profile with no constraints
        profile = region_generator._generate_profile()

        # Check that values are in the valid range
        assert 0 <= profile.temperature <= 1
        assert 0 <= profile.humidity <= 1
        assert 0 <= profile.elevation <= 1
        assert 0 <= profile.ruggedness <= 1

        # Generate profile with constraints
        constraints = {
            "temperature": (0.2, 0.4),
            "humidity": (0.7, 0.9),
            "elevation": (0.5, 0.6),
            "ruggedness": (0.3, 0.5),
        }

        profile = region_generator._generate_profile(constraints)

        # Check that constraints were respected
        assert 0.2 <= profile.temperature <= 0.4
        assert 0.7 <= profile.humidity <= 0.9
        assert 0.5 <= profile.elevation <= 0.6
        assert 0.3 <= profile.ruggedness <= 0.5

    def test_determine_biome_type(self, region_generator): pass
        """Test determining biome type based on environmental profile."""
        # Create profiles matching different biomes
        forest_profile = RegionProfile(
            temperature=0.5, humidity=0.8, elevation=0.4, ruggedness=0.3
        )
        mountain_profile = RegionProfile(
            temperature=0.3, humidity=0.5, elevation=0.9, ruggedness=0.7
        )
        desert_profile = RegionProfile(
            temperature=0.9, humidity=0.2, elevation=0.3, ruggedness=0.5
        )

        # Determine biome types for each profile
        forest_biome = region_generator._determine_biome_type(forest_profile, [], None)
        mountain_biome = region_generator._determine_biome_type(
            mountain_profile, [], None
        )
        desert_biome = region_generator._determine_biome_type(desert_profile, [], None)

        # Check results
        assert forest_biome == "forest"
        assert mountain_biome == "mountain"
        assert desert_biome == "desert"

        # Test with forced biome
        forced_biome = region_generator._determine_biome_type(
            desert_profile, [], "plains"
        )
        assert forced_biome == "plains"

        # Test with adjacent biomes
        adjacent_biomes = ["desert", "desert", "mountain"]
        biome_with_adjacency = region_generator._determine_biome_type(
            forest_profile, adjacent_biomes, None
        )
        # Adjacency should influence the choice, but we can't predict exactly how
        assert biome_with_adjacency in region_generator.biomes

    def test_generate_resources(self, region_generator): pass
        """Test generating resources based on biome data."""
        # Set a deterministic seed
        random.seed(12345)

        # Test with a specific biome
        biome_data = {
            "resource_weights": {"wood": 0.8, "herbs": 0.6, "water": 0.5, "stone": 0.3}
        }

        resources = region_generator._generate_resources(biome_data)

        # Check that resources were generated based on weights
        assert "wood" in resources
        assert "herbs" in resources
        assert 0 <= resources["wood"] <= 1
        assert 0 <= resources["herbs"] <= 1

        # Resources with higher weights should generally have higher values
        high_weight_resources = [
            k for k, v in biome_data["resource_weights"].items() if v >= 0.6
        ]
        low_weight_resources = [
            k for k, v in biome_data["resource_weights"].items() if v < 0.6
        ]

        # Not always true, but generally true over multiple runs
        high_values = [resources.get(k, 0) for k in high_weight_resources]
        low_values = [resources.get(k, 0) for k in low_weight_resources]

        # This test might occasionally fail due to randomness, but should be generally reliable
        assert sum(high_values) / len(high_values) > sum(low_values) / len(low_values)

        # Test with empty biome data
        empty_resources = region_generator._generate_resources({})
        assert empty_resources == {}

    def test_generate_features(self, region_generator): pass
        """Test generating features based on biome data."""
        # Set a deterministic seed
        random.seed(12345)

        # Test with a specific biome
        biome_data = {
            "name": "Forest",
            "common_features": ["trees", "river", "clearing"],
            "rare_features": ["ancient_ruins", "magical_spring"]
        }

        features = region_generator._generate_features(biome_data)

        # Should always include the biome name
        assert "Forest" in features

        # Should include some common features
        common_in_features = [f for f in features if f in biome_data["common_features"]]
        assert len(common_in_features) >= 1

        # All features should be from the biome data or the biome name
        valid_features = biome_data["common_features"] + biome_data["rare_features"] + ["Forest"]
        assert all(f in valid_features for f in features)

        # Test with empty biome data
        empty_features = region_generator._generate_features({})
        assert "Unknown" in empty_features  # Should include default biome name

    def test_generate_hex_grid(self, region_generator): pass
        """Test generating a hexagonal grid for a region."""
        # Generate hex coordinates for a specific location
        coords = (10, 20)
        hex_coords = region_generator._generate_hex_grid(coords)

        # Check results
        assert len(hex_coords) > 0

        # Hex coordinates should be centered around the region coordinates
        center_x = sum(x for x, _ in hex_coords) / len(hex_coords)
        center_y = sum(y for _, y in hex_coords) / len(hex_coords)

        # Center should be close to the original coordinates
        assert abs(center_x - coords[0]) < 2
        assert abs(center_y - coords[1]) < 2

    def test_get_region_by_coords(self, region_generator): pass
        """Test retrieving a region by coordinates."""
        # Create test regions
        region1 = MagicMock(spec=RegionMetadata)
        region1.coordinates = (0, 0)

        region2 = MagicMock(spec=RegionMetadata)
        region2.coordinates = (1, 1)

        regions = [region1, region2]

        # Get region by existing coordinates
        result = region_generator.get_region_by_coords((0, 0), regions)
        assert result == region1

        # Get region by different existing coordinates
        result = region_generator.get_region_by_coords((1, 1), regions)
        assert result == region2

        # Get region by non-existent coordinates
        result = region_generator.get_region_by_coords((2, 2), regions)
        assert result is None

    def test_integration_region_generation(self, region_generator): pass
        """
        Integration test for the entire region generation process.

        This test verifies that the generate_region method properly
        coordinates all the generation steps.
        """
        # Set a deterministic seed for random operations
        random.seed(12345)

        # Generate a region with explicit parameters
        region = region_generator.generate_region(
            region_id="r_test123",
            name="Test Region",
            coordinates=(10, 20),
            continent_id="c_test456",
            adjacent_biomes=["forest", "plains"],
            profile_constraints={"temperature": (0.4, 0.6), "humidity": (0.5, 0.7)},
        )

        # Check region properties
        assert region.region_id == "r_test123"
        assert region.name == "Test Region"
        assert region.coordinates == (10, 20)
        assert region.continent_id == "c_test456"
        assert region.biome_type in region_generator.biomes

        # Check profile constraints
        assert 0.4 <= region.profile.temperature <= 0.6
        assert 0.5 <= region.profile.humidity <= 0.7

        # Check that resources match the biome
        biome_data = region_generator.biomes.get(region.biome_type, {})
        biome_resources = biome_data.get("resource_weights", {})

        # Resources should generally match biome resources
        for resource in region.resources: pass
            assert resource in biome_resources

        # Check that features match the biome
        biome_common_features = biome_data.get("common_features", [])
        biome_rare_features = biome_data.get("rare_features", [])
        biome_name = biome_data.get("name", "Unknown")
        valid_features = biome_common_features + biome_rare_features + [biome_name]
        for feature in region.features: pass
            assert feature in valid_features
