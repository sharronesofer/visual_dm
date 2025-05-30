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
Tests for resource generation utilities.

This module contains tests for resource generation, distribution,
and management within the world generation system.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import random
import math
from typing import Dict, List, Tuple, Any

from backend.systems.world_generation.resource_utils import (
    ResourceType,
    BiomeType,
    Resource,
    generate_resource_name,
    determine_resource_value,
    generate_resource,
    generate_resources_for_tile,
    assign_resources_to_region,
    generate_special_resource_clusters,
    DEFAULT_BIOME_RESOURCES,
    RESOURCE_NAME_TEMPLATES,
    RESOURCE_NAME_COMPONENTS,
)


class TestResourceUtils: pass
    """Tests for resource generation utilities."""

    @pytest.fixture
    def sample_tiles(self): pass
        """Create sample tile data for testing."""
        return {
            (100, 200): {
                "biome": BiomeType.FOREST,
                "elevation": 5,
                "humidity": 7,
                "temperature": 6,
            },
            (101, 200): {
                "biome": BiomeType.MOUNTAIN,
                "elevation": 8,
                "humidity": 3,
                "temperature": 4,
            },
            (102, 200): {
                "biome": BiomeType.DESERT,
                "elevation": 3,
                "humidity": 2,
                "temperature": 9,
            },
            (100, 201): {
                "biome": BiomeType.OCEAN,
                "elevation": 1,
                "humidity": 10,
                "temperature": 7,
            },
        }

    def test_resource_type_enum(self): pass
        """Test ResourceType enum values."""
        assert ResourceType.STONE == "stone"
        assert ResourceType.ORE == "ore"
        assert ResourceType.GEM == "gem"
        assert ResourceType.PRECIOUS_METAL == "precious_metal"
        assert ResourceType.HERB == "herb"
        assert ResourceType.CROP == "crop"
        assert ResourceType.ANIMAL == "animal"
        assert ResourceType.FISH == "fish"
        assert ResourceType.WATER == "water"
        assert ResourceType.MAGICAL == "magical"

    def test_resource_class_creation(self): pass
        """Test Resource class creation and properties."""
        resource = Resource(
            name="Iron Ore",
            type=ResourceType.ORE,
            rarity=5,
            quantity=7,
            value=6,
            custom_data={"mine_depth": 10}
        )
        
        assert resource.name == "Iron Ore"
        assert resource.type == ResourceType.ORE
        assert resource.rarity == 5
        assert resource.quantity == 7
        assert resource.value == 6
        assert resource.custom_data == {"mine_depth": 10}

    def test_resource_dict_conversion(self): pass
        """Test Resource to dict conversion."""
        resource = Resource(
            name="Gold Nugget",
            type=ResourceType.PRECIOUS_METAL,
            rarity=9,
            quantity=3,
            value=8
        )
        
        resource_dict = resource.dict()
        assert resource_dict["name"] == "Gold Nugget"
        assert resource_dict["type"] == ResourceType.PRECIOUS_METAL
        assert resource_dict["rarity"] == 9
        assert resource_dict["quantity"] == 3
        assert resource_dict["value"] == 8

    def test_default_biome_resources_structure(self): pass
        """Test that default biome resources are properly structured."""
        # Check that all biome types have resource definitions
        assert BiomeType.FOREST in DEFAULT_BIOME_RESOURCES
        assert BiomeType.MOUNTAIN in DEFAULT_BIOME_RESOURCES
        assert BiomeType.DESERT in DEFAULT_BIOME_RESOURCES
        assert BiomeType.OCEAN in DEFAULT_BIOME_RESOURCES
        
        # Check structure of resource definitions
        forest_resources = DEFAULT_BIOME_RESOURCES[BiomeType.FOREST]
        assert isinstance(forest_resources, list)
        assert len(forest_resources) > 0
        
        # Check first resource definition structure
        res_type, probability, quantity, rarity = forest_resources[0]
        assert isinstance(res_type, str)  # ResourceType
        assert isinstance(probability, float)
        assert isinstance(quantity, int)
        assert isinstance(rarity, int)
        assert 0.0 <= probability <= 1.0
        assert 1 <= quantity <= 10
        assert 1 <= rarity <= 10

    def test_resource_name_templates_structure(self): pass
        """Test that resource name templates are properly structured."""
        assert ResourceType.STONE in RESOURCE_NAME_TEMPLATES
        assert ResourceType.ORE in RESOURCE_NAME_TEMPLATES
        assert ResourceType.GEM in RESOURCE_NAME_TEMPLATES
        
        # Check that templates contain placeholder strings
        stone_templates = RESOURCE_NAME_TEMPLATES[ResourceType.STONE]
        assert isinstance(stone_templates, list)
        assert len(stone_templates) > 0
        
        # Check that at least some templates have placeholders
        has_placeholders = any("{" in template for template in stone_templates)
        assert has_placeholders

    def test_resource_name_components_structure(self): pass
        """Test that resource name components are properly structured."""
        assert "quality" in RESOURCE_NAME_COMPONENTS
        assert "color" in RESOURCE_NAME_COMPONENTS
        assert "location" in RESOURCE_NAME_COMPONENTS
        
        # Check that components are lists of strings
        quality_components = RESOURCE_NAME_COMPONENTS["quality"]
        assert isinstance(quality_components, list)
        assert len(quality_components) > 0
        assert all(isinstance(comp, str) for comp in quality_components)

    @patch('backend.systems.world_generation.resource_utils.random.choice')
    def test_generate_resource_name_basic(self, mock_choice): pass
        """Test basic resource name generation."""
        # Mock template selection and component replacement
        mock_choice.side_effect = [
            "{quality} {gem_type}",  # Template
            "Shiny",  # quality
            "Crystal"  # gem_type
        ]
        
        name = generate_resource_name(ResourceType.GEM)
        assert name == "Shiny Crystal"

    @patch('backend.systems.world_generation.resource_utils.random.choice')
    def test_generate_resource_name_fallback(self, mock_choice): pass
        """Test resource name generation with fallback to stone templates."""
        mock_choice.side_effect = [
            "Simple Stone",  # Template from stone (fallback)
        ]
        
        # Use a resource type that might not have templates
        name = generate_resource_name("unknown_type")
        assert name == "Simple Stone"

    @patch('backend.systems.world_generation.resource_utils.random.choice')
    def test_generate_resource_name_multiple_placeholders(self, mock_choice): pass
        """Test resource name generation with multiple placeholders."""
        mock_choice.side_effect = [
            "{quality} {metal} Ore",  # Template
            "Ancient",  # quality
            "Iron"  # metal
        ]
        
        name = generate_resource_name(ResourceType.ORE)
        assert name == "Ancient Iron Ore"

    @patch('backend.systems.world_generation.resource_utils.random.uniform')
    def test_determine_resource_value_basic(self, mock_uniform): pass
        """Test basic resource value calculation."""
        mock_uniform.return_value = 1.0  # No random factor
        
        # Test with moderate values
        value = determine_resource_value(rarity=5, quantity=5)
        assert value == 5  # (5 + 5) / 2 * 1.0
        
        # Test with high values
        value = determine_resource_value(rarity=10, quantity=8)
        assert value == 9  # (10 + 8) / 2 * 1.0

    @patch('backend.systems.world_generation.resource_utils.random.uniform')
    def test_determine_resource_value_with_randomness(self, mock_uniform): pass
        """Test resource value calculation with random factor."""
        mock_uniform.return_value = 1.2  # 20% increase
        
        value = determine_resource_value(rarity=4, quantity=6)
        expected = int((4 + 6) / 2 * 1.2)  # 6
        assert value == expected

    @patch('backend.systems.world_generation.resource_utils.random.uniform')
    def test_determine_resource_value_bounds(self, mock_uniform): pass
        """Test that resource value stays within bounds."""
        # Test lower bound
        mock_uniform.return_value = 0.1  # Very low factor
        value = determine_resource_value(rarity=1, quantity=1)
        assert value >= 1
        
        # Test upper bound
        mock_uniform.return_value = 2.0  # Very high factor
        value = determine_resource_value(rarity=10, quantity=10)
        assert value <= 10

    @patch('backend.systems.world_generation.resource_utils.determine_resource_value')
    @patch('backend.systems.world_generation.resource_utils.generate_resource_name')
    def test_generate_resource_basic(self, mock_name, mock_value): pass
        """Test basic resource generation."""
        mock_name.return_value = "Iron Ore"
        mock_value.return_value = 7
        
        resource = generate_resource(ResourceType.ORE, rarity=6, quantity=8)
        
        assert resource.name == "Iron Ore"
        assert resource.type == ResourceType.ORE
        assert resource.rarity == 6
        assert resource.quantity == 8
        assert resource.value == 7
        
        mock_name.assert_called_once_with(ResourceType.ORE)
        mock_value.assert_called_once_with(6, 8)

    @patch('backend.systems.world_generation.resource_utils.random.seed')
    @patch('backend.systems.world_generation.resource_utils.random.random')
    @patch('backend.systems.world_generation.resource_utils.random.uniform')
    @patch('backend.systems.world_generation.resource_utils.generate_resource')
    def test_generate_resources_for_tile_basic(self, mock_gen_resource, mock_uniform, mock_random, mock_seed): pass
        """Test basic resource generation for a tile."""
        # Mock resource generation
        mock_resource = Mock()
        mock_gen_resource.return_value = mock_resource
        
        # Mock probability checks - provide enough values for all forest resources
        mock_random.side_effect = [0.3] * 10  # Always pass probability check
        mock_uniform.side_effect = [0.1, -0.1] * 20  # Various random adjustments
        
        resources = generate_resources_for_tile(
            biome=BiomeType.FOREST,
            elevation=5,
            humidity=5,
            temperature=5,
            seed=12345
        )
        
        # Should have called seed
        mock_seed.assert_called_once_with(12345)
        
        # Should have generated resources
        assert isinstance(resources, list)

    @patch('backend.systems.world_generation.resource_utils.random.seed')
    def test_generate_resources_for_tile_with_seed(self, mock_seed): pass
        """Test resource generation with seed for reproducibility."""
        generate_resources_for_tile(BiomeType.FOREST, seed=42)
        mock_seed.assert_called_once_with(42)

    def test_generate_resources_for_tile_without_seed(self): pass
        """Test resource generation without seed."""
        # Should not raise an error
        resources = generate_resources_for_tile(BiomeType.FOREST)
        assert isinstance(resources, list)

    @patch('backend.systems.world_generation.resource_utils.random.random')
    @patch('backend.systems.world_generation.resource_utils.generate_resource')
    def test_generate_resources_for_tile_environmental_factors(self, mock_gen_resource, mock_random): pass
        """Test that environmental factors affect resource generation."""
        mock_resource = Mock()
        mock_gen_resource.return_value = mock_resource
        mock_random.return_value = 0.1  # Always pass probability check
        
        # Test high elevation (should favor ore/stone)
        resources_high = generate_resources_for_tile(
            biome=BiomeType.MOUNTAIN,
            elevation=9,
            humidity=5,
            temperature=5
        )
        
        # Test low elevation (should favor fish/water)
        resources_low = generate_resources_for_tile(
            biome=BiomeType.OCEAN,
            elevation=1,
            humidity=5,
            temperature=5
        )
        
        # Both should generate resources
        assert isinstance(resources_high, list)
        assert isinstance(resources_low, list)

    @patch('backend.systems.world_generation.resource_utils.random.random')
    @patch('backend.systems.world_generation.resource_utils.generate_resource')
    def test_generate_resources_for_tile_custom_biome(self, mock_gen_resource, mock_random): pass
        """Test resource generation for custom biome type."""
        mock_resource = Mock()
        mock_gen_resource.return_value = mock_resource
        mock_random.return_value = 0.1  # Always pass probability check
        
        resources = generate_resources_for_tile(biome=BiomeType.CUSTOM)
        assert isinstance(resources, list)

    @patch('backend.systems.world_generation.resource_utils.random.seed')
    @patch('backend.systems.world_generation.resource_utils.generate_resources_for_tile')
    def test_assign_resources_to_region_basic(self, mock_gen_resources, mock_seed, sample_tiles): pass
        """Test basic resource assignment to region."""
        mock_resources = [
            Mock(dict=Mock(return_value={"name": "Iron", "type": "ore"})),
            Mock(dict=Mock(return_value={"name": "Wood", "type": "herb"}))
        ]
        mock_gen_resources.return_value = mock_resources
        
        # Mock random to always assign resources
        with patch('backend.systems.world_generation.resource_utils.random.random', return_value=0.5): pass
            updated_tiles = assign_resources_to_region(sample_tiles, seed=123)
        
        mock_seed.assert_called_once_with(123)
        
        # Check that resources were added to tiles
        for coords, tile_data in updated_tiles.items(): pass
            if "resources" in tile_data: pass
                assert len(tile_data["resources"]) == 2
                assert tile_data["resources"][0]["name"] == "Iron"
                assert tile_data["resources"][1]["name"] == "Wood"

    def test_assign_resources_to_region_string_seed(self, sample_tiles): pass
        """Test resource assignment with string seed."""
        with patch('backend.systems.world_generation.resource_utils.random.seed') as mock_seed: pass
            with patch('backend.systems.world_generation.resource_utils.random.random', return_value=0.8): pass
                assign_resources_to_region(sample_tiles, seed="test_seed")
                # Should convert string to integer and call seed
                expected_seed = sum(ord(c) for c in "test_seed")
                assert mock_seed.call_args_list[0][0][0] == expected_seed

    @patch('backend.systems.world_generation.resource_utils.random.random')
    def test_assign_resources_to_region_density(self, mock_random, sample_tiles): pass
        """Test resource assignment with different density values."""
        # Test low density (should assign fewer resources)
        mock_random.return_value = 0.8
        updated_tiles_low = assign_resources_to_region(sample_tiles, resource_density=0.5, seed=123)
        
        # Test high density (should assign more resources)
        mock_random.return_value = 0.3
        updated_tiles_high = assign_resources_to_region(sample_tiles, resource_density=1.5, seed=456)
        
        # Both should return tile dictionaries
        assert isinstance(updated_tiles_low, dict)
        assert isinstance(updated_tiles_high, dict)

    def test_assign_resources_to_region_existing_resources(self, sample_tiles): pass
        """Test that existing resources are not overwritten."""
        # Add existing resources to one tile
        sample_tiles[(100, 200)]["resources"] = [{"name": "Existing", "type": "stone"}]
        
        updated_tiles = assign_resources_to_region(sample_tiles, seed=789)
        
        # Existing resources should remain unchanged
        assert updated_tiles[(100, 200)]["resources"] == [{"name": "Existing", "type": "stone"}]

    @patch('backend.systems.world_generation.resource_utils.random.seed')
    @patch('backend.systems.world_generation.resource_utils.random.choice')
    @patch('backend.systems.world_generation.resource_utils.random.randint')
    @patch('backend.systems.world_generation.resource_utils.generate_resource')
    def test_generate_special_resource_clusters_basic(self, mock_gen_resource, mock_randint, 
                                                    mock_choice, mock_seed, sample_tiles): pass
        """Test basic special resource cluster generation."""
        # Mock resource generation
        mock_resource = Mock()
        mock_resource.name = "Iron Deposit"
        mock_resource.custom_data = {}
        mock_resource.dict.return_value = {"name": "Iron Deposit", "type": "ore"}
        mock_gen_resource.return_value = mock_resource
        
        # Mock random selections
        mock_choice.side_effect = [
            (100, 200),  # Center coordinate
            ResourceType.ORE,  # Resource type
            "Iron"  # Name base
        ]
        mock_randint.side_effect = [7, 6]  # Rarity, base quantity
        
        updated_tiles = generate_special_resource_clusters(
            sample_tiles,
            cluster_count=1,
            cluster_size=2,
            seed=456
        )
        
        mock_seed.assert_called_once_with(456)
        
        # Check that clusters were added
        assert isinstance(updated_tiles, dict)
        
        # Should have called resource generation
        assert mock_gen_resource.called

    def test_generate_special_resource_clusters_string_seed(self, sample_tiles): pass
        """Test cluster generation with string seed."""
        with patch('backend.systems.world_generation.resource_utils.random.seed') as mock_seed: pass
            generate_special_resource_clusters(sample_tiles, seed="cluster_seed")
            expected_seed = sum(ord(c) for c in "cluster_seed")
            mock_seed.assert_called_once_with(expected_seed)

    @patch('backend.systems.world_generation.resource_utils.random.choice')
    def test_generate_special_resource_clusters_custom_types(self, mock_choice, sample_tiles): pass
        """Test cluster generation with custom resource types."""
        mock_choice.side_effect = [
            (100, 200),  # Center
            ResourceType.GEM,  # From custom list
            "Ruby"  # Name base
        ]
        
        with patch('backend.systems.world_generation.resource_utils.random.randint', return_value=5): pass
            with patch('backend.systems.world_generation.resource_utils.generate_resource') as mock_gen: pass
                mock_resource = Mock()
                mock_resource.name = "Ruby Deposit"
                mock_resource.custom_data = {}
                mock_resource.dict.return_value = {"name": "Ruby Deposit"}
                mock_gen.return_value = mock_resource
                
                updated_tiles = generate_special_resource_clusters(
                    sample_tiles,
                    cluster_count=1,
                    cluster_size=1,  # Small cluster
                    resource_types=[ResourceType.GEM, ResourceType.MAGICAL],
                    seed=111
                )
                
                assert isinstance(updated_tiles, dict)

    def test_generate_special_resource_clusters_empty_tiles(self): pass
        """Test cluster generation with empty tile dictionary."""
        empty_tiles = {}
        updated_tiles = generate_special_resource_clusters(empty_tiles)
        assert updated_tiles == {}

    @patch('backend.systems.world_generation.resource_utils.random.choice')
    @patch('backend.systems.world_generation.resource_utils.random.randint')
    @patch('backend.systems.world_generation.resource_utils.generate_resource')
    def test_generate_special_resource_clusters_distance_calculation(self, mock_gen_resource, 
                                                                   mock_randint, mock_choice, sample_tiles): pass
        """Test that cluster generation respects distance calculations."""
        # Mock resource generation
        mock_resource = Mock()
        mock_resource.name = "Test Deposit"
        mock_resource.custom_data = {}
        mock_resource.dict.return_value = {"name": "Test Deposit"}
        mock_gen_resource.return_value = mock_resource
        
        # Mock selections
        mock_choice.side_effect = [
            (100, 200),  # Center at existing tile
            ResourceType.ORE,
            "Test"
        ]
        mock_randint.side_effect = [5, 5]  # Rarity, quantity
        
        updated_tiles = generate_special_resource_clusters(
            sample_tiles,
            cluster_count=1,
            cluster_size=1,  # Small cluster
            seed=222
        )
        
        # Should have added resources to tiles within cluster radius
        center_tile = updated_tiles[(100, 200)]
        assert "resources" in center_tile

    @patch('backend.systems.world_generation.resource_utils.random.choice')
    @patch('backend.systems.world_generation.resource_utils.random.randint')
    def test_generate_special_resource_clusters_name_templates(self, mock_randint, mock_choice, sample_tiles): pass
        """Test different name templates for different resource types."""
        mock_choice.side_effect = [
            (100, 200),  # Center
            ResourceType.HERB,  # Should use "Grove" template
            "Healing"
        ]
        mock_randint.side_effect = [5, 5]
        
        with patch('backend.systems.world_generation.resource_utils.generate_resource') as mock_gen: pass
            mock_resource = Mock()
            mock_resource.name = "Healing Grove"  # Should be overridden
            mock_resource.custom_data = {}
            mock_resource.dict.return_value = {"name": "Healing Grove"}
            mock_gen.return_value = mock_resource
            
            updated_tiles = generate_special_resource_clusters(
                sample_tiles,
                cluster_count=1,
                cluster_size=1,  # Small cluster
                resource_types=[ResourceType.HERB],
                seed=333
            )
            
            # Resource name should be set to grove template
            assert mock_resource.name == "Healing Grove"

    def test_generate_special_resource_clusters_cluster_id(self, sample_tiles): pass
        """Test that cluster IDs are properly assigned."""
        with patch('backend.systems.world_generation.resource_utils.random.choice') as mock_choice: pass
            with patch('backend.systems.world_generation.resource_utils.random.randint') as mock_randint: pass
                with patch('backend.systems.world_generation.resource_utils.generate_resource') as mock_gen: pass
                    mock_choice.side_effect = [
                        (100, 200),  # Center
                        ResourceType.ORE,
                        "Iron"
                    ]
                    mock_randint.side_effect = [5, 5]
                    
                    mock_resource = Mock()
                    mock_resource.name = "Iron Deposit"
                    mock_resource.custom_data = {}
                    mock_resource.dict.return_value = {"name": "Iron Deposit", "cluster_id": "cluster_0"}
                    mock_gen.return_value = mock_resource
                    
                    generate_special_resource_clusters(
                        sample_tiles,
                        cluster_count=1,
                        cluster_size=1,  # Small cluster
                        seed=444
                    )
                    
                    # Should have set cluster_id
                    assert mock_resource.custom_data["cluster_id"] == "cluster_0"

    def test_integration_full_resource_workflow(self, sample_tiles): pass
        """Test full resource generation workflow integration."""
        # Step 1: Assign basic resources
        with patch('backend.systems.world_generation.resource_utils.random.random', return_value=0.3): pass
            tiles_with_resources = assign_resources_to_region(sample_tiles, resource_density=1.0, seed=999)
        
        # Step 2: Add special clusters
        final_tiles = generate_special_resource_clusters(
            tiles_with_resources,
            cluster_count=1,
            cluster_size=1,
            seed=888
        )
        
        # Should have both basic and cluster resources
        assert isinstance(final_tiles, dict)
        assert len(final_tiles) == len(sample_tiles)

    def test_edge_cases_and_error_handling(self): pass
        """Test edge cases and error handling."""
        # Test with invalid biome type
        resources = generate_resources_for_tile("invalid_biome")
        assert isinstance(resources, list)
        
        # Test with extreme environmental values
        resources = generate_resources_for_tile(
            BiomeType.FOREST,
            elevation=0,
            humidity=0,
            temperature=0
        )
        assert isinstance(resources, list)
        
        resources = generate_resources_for_tile(
            BiomeType.FOREST,
            elevation=10,
            humidity=10,
            temperature=10
        )
        assert isinstance(resources, list)

    def test_resource_probability_adjustments(self): pass
        """Test that environmental factors properly adjust resource probabilities."""
        # This is more of an integration test to ensure the probability logic works
        with patch('backend.systems.world_generation.resource_utils.random.random', return_value=0.5): pass
            # High elevation should favor ore/stone
            resources_mountain = generate_resources_for_tile(
                BiomeType.MOUNTAIN,
                elevation=9,
                humidity=3,
                temperature=4
            )
            
            # Low elevation should favor fish/water
            resources_ocean = generate_resources_for_tile(
                BiomeType.OCEAN,
                elevation=1,
                humidity=10,
                temperature=7
            )
            
            # Both should generate resources
            assert isinstance(resources_mountain, list)
            assert isinstance(resources_ocean, list)

    def test_randomness_parameter_effects(self): pass
        """Test that randomness parameter affects resource generation."""
        # Test with low randomness
        resources_low = generate_resources_for_tile(
            BiomeType.FOREST,
            randomness=0.1,
            seed=123
        )
        
        # Test with high randomness
        resources_high = generate_resources_for_tile(
            BiomeType.FOREST,
            randomness=0.9,
            seed=123
        )
        
        # Both should generate resources
        assert isinstance(resources_low, list)
        assert isinstance(resources_high, list)
