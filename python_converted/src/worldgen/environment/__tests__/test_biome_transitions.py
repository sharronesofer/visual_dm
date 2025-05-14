#!/usr/bin/env python3
"""
Test file for biome adjacency rules and transition zones
"""

import unittest
import os
import shutil
import numpy as np

from ..BiomeTypes import BiomeType, BIOME_PARAMETERS, TRANSITION_BIOMES
from ..BiomeAdjacencyMatrix import BiomeAdjacencyMatrix, AdjacencyRuleType
from ..BiomeTransitionGenerator import BiomeCell, BiomeGrid, BiomeTransitionGenerator
from ..BiomeConfigManager import BiomeConfigManager
from ...core.DeterministicRNG import DeterministicRNG


class TestBiomeAdjacencyMatrix(unittest.TestCase):
    """Test cases for the BiomeAdjacencyMatrix class"""
    
    def setUp(self):
        """Set up test environment"""
        self.matrix = BiomeAdjacencyMatrix()
    
    def test_initialization(self):
        """Test initialization with default rules"""
        # Verify all biome combinations have rules
        for biome1 in BiomeType:
            for biome2 in BiomeType:
                if biome1 != biome2:
                    # Should have a rule in both directions
                    self.assertTrue(
                        self.matrix.has_rule(biome1, biome2),
                        f"Missing rule for {biome1.value}-{biome2.value}"
                    )
                    self.assertTrue(
                        self.matrix.has_rule(biome2, biome1),
                        f"Missing rule for {biome2.value}-{biome1.value}"
                    )
    
    def test_compatible_biomes(self):
        """Test compatible biome detection"""
        # Same biome is always compatible
        for biome in BiomeType:
            self.assertTrue(self.matrix.are_compatible(biome, biome))
        
        # Check if known compatible biomes are detected correctly
        self.assertTrue(self.matrix.are_compatible(BiomeType.PLAINS, BiomeType.GRASSLAND))
        
        # Check if transition biomes are compatible with others
        for transition_biome in TRANSITION_BIOMES:
            for other_biome in BiomeType:
                if transition_biome != other_biome:
                    self.assertTrue(
                        self.matrix.are_compatible(transition_biome, other_biome),
                        f"Transition biome {transition_biome.value} should be compatible with {other_biome.value}"
                    )
    
    def test_incompatible_biomes(self):
        """Test incompatible biome detection"""
        # Extreme biomes like desert and tundra should be incompatible
        self.assertFalse(self.matrix.are_compatible(BiomeType.DESERT, BiomeType.TUNDRA))
        
        # Check if transition rules are set for incompatible biomes
        rule = self.matrix.get_rule(BiomeType.DESERT, BiomeType.TUNDRA)
        self.assertEqual(rule.rule_type, AdjacencyRuleType.TRANSITION_NEEDED)
        self.assertGreater(len(rule.transition_biomes), 0)
        self.assertGreater(rule.min_transition_width, 0)
    
    def test_transition_biomes(self):
        """Test transition biome selection"""
        # Get transition biomes for desert-tundra
        transitions = self.matrix.get_transition_biomes(BiomeType.DESERT, BiomeType.TUNDRA)
        
        # Should have multiple transition options
        self.assertGreater(len(transitions), 0)
        
        # All should be valid biomes
        for biome in transitions:
            self.assertIn(biome, BiomeType)
            
        # If grassland or plains is suggested, they should be among the top options
        if BiomeType.GRASSLAND in transitions or BiomeType.PLAINS in transitions:
            self.assertLessEqual(
                min(
                    transitions.index(BiomeType.GRASSLAND) if BiomeType.GRASSLAND in transitions else 999,
                    transitions.index(BiomeType.PLAINS) if BiomeType.PLAINS in transitions else 999
                ),
                2,  # Should be among top 3 choices
                "Grassland/Plains should be preferred transitions"
            )
    
    def test_serialization(self):
        """Test serialization to and from JSON"""
        # Convert to dict
        data = self.matrix.to_dict()
        
        # Should have rules for all biome pairs (minus duplicates)
        total_biomes = len(BiomeType)
        expected_rule_count = total_biomes * (total_biomes - 1) // 2  # n*(n-1)/2
        
        self.assertGreaterEqual(len(data["rules"]), expected_rule_count // 2)
        
        # Recreate from dict
        matrix2 = BiomeAdjacencyMatrix.from_dict(data)
        
        # Check if rules are preserved
        for biome1 in BiomeType:
            for biome2 in BiomeType:
                if biome1 == biome2:
                    continue
                    
                rule1 = self.matrix.get_rule(biome1, biome2)
                rule2 = matrix2.get_rule(biome1, biome2)
                
                self.assertEqual(rule1.rule_type, rule2.rule_type)
                self.assertEqual(rule1.min_transition_width, rule2.min_transition_width)
    
    def test_override_rule(self):
        """Test overriding existing rules"""
        # Original rule
        original = self.matrix.get_rule(BiomeType.DESERT, BiomeType.PLAINS)
        
        # Override
        self.matrix.override_rule(
            BiomeType.DESERT,
            BiomeType.PLAINS,
            AdjacencyRuleType.INCOMPATIBLE
        )
        
        # Check if changed
        new_rule = self.matrix.get_rule(BiomeType.DESERT, BiomeType.PLAINS)
        self.assertEqual(new_rule.rule_type, AdjacencyRuleType.INCOMPATIBLE)
        
        # Should be updated in both directions
        reversed_rule = self.matrix.get_rule(BiomeType.PLAINS, BiomeType.DESERT)
        self.assertEqual(reversed_rule.rule_type, AdjacencyRuleType.INCOMPATIBLE)


class TestBiomeTransitionGenerator(unittest.TestCase):
    """Test cases for the BiomeTransitionGenerator class"""
    
    def setUp(self):
        """Set up test environment"""
        self.rng = DeterministicRNG(seed=12345)
        self.matrix = BiomeAdjacencyMatrix()
        self.generator = BiomeTransitionGenerator(self.matrix, self.rng)
        
        # Create a simple grid with two biomes
        self.grid = BiomeGrid(20, 20)
        
        # Put desert on the left half
        for y in range(20):
            for x in range(10):
                self.grid.cells[y][x] = BiomeCell(
                    x=x, y=y, 
                    biome=BiomeType.DESERT,
                    elevation=200.0,
                    moisture=0.1,
                    temperature=35.0
                )
        
        # Put tundra on the right half
        for y in range(20):
            for x in range(10, 20):
                self.grid.cells[y][x] = BiomeCell(
                    x=x, y=y, 
                    biome=BiomeType.TUNDRA,
                    elevation=200.0,
                    moisture=0.3,
                    temperature=-5.0
                )
    
    def test_distance_map(self):
        """Test distance map generation"""
        distance_map = self.generator._create_distance_map(self.grid, BiomeType.DESERT)
        
        # Distances should be 0 in desert area
        for y in range(20):
            for x in range(10):
                self.assertEqual(distance_map[y][x], 0.0)
        
        # Distances should increase going into tundra area
        min_dist_in_tundra = min(distance_map[y][x] for y in range(20) for x in range(10, 20))
        self.assertGreater(min_dist_in_tundra, 0.0)
        
        # Check that distances increase monotonically from boundary
        for y in range(20):
            for x in range(10, 19):
                self.assertLessEqual(distance_map[y][x], distance_map[y][x+1])
    
    def test_generate_transitions(self):
        """Test generation of transition zones"""
        # Generate transitions
        result_grid = self.generator.generate_transitions(self.grid)
        
        # Should have the same dimensions
        self.assertEqual(result_grid.width, self.grid.width)
        self.assertEqual(result_grid.height, self.grid.height)
        
        # Count transition cells
        transition_count = sum(
            1 for y in range(result_grid.height) 
            for x in range(result_grid.width) 
            if result_grid.cells[y][x].is_transition
        )
        
        # Should have some transition cells
        self.assertGreater(transition_count, 0)
        
        # There should be no direct desert-tundra borders
        for y in range(result_grid.height):
            for x in range(result_grid.width - 1):
                cell1 = result_grid.cells[y][x]
                cell2 = result_grid.cells[y][x + 1]
                
                if (cell1.biome == BiomeType.DESERT and cell2.biome == BiomeType.TUNDRA) or \
                   (cell1.biome == BiomeType.TUNDRA and cell2.biome == BiomeType.DESERT):
                    self.fail("Found direct desert-tundra border which should be impossible")
        
        # Check that transition cells have source biomes set
        for y in range(result_grid.height):
            for x in range(result_grid.width):
                cell = result_grid.cells[y][x]
                if cell.is_transition:
                    self.assertEqual(len(cell.source_biomes), 2)
                    self.assertIn(BiomeType.DESERT, cell.source_biomes)
                    self.assertIn(BiomeType.TUNDRA, cell.source_biomes)
    
    def test_interpolation(self):
        """Test environmental values interpolation"""
        # Get parameters
        desert_params = BIOME_PARAMETERS[BiomeType.DESERT]
        tundra_params = BIOME_PARAMETERS[BiomeType.TUNDRA]
        
        # Test temperature interpolation
        desert_temp = (desert_params.temperature_range[0] + desert_params.temperature_range[1]) / 2
        tundra_temp = (tundra_params.temperature_range[0] + tundra_params.temperature_range[1]) / 2
        
        temp_50_50 = self.generator._interpolate_temperature(
            BiomeType.DESERT, BiomeType.TUNDRA, 0.5
        )
        
        # Should be around the average of desert and tundra temperatures
        self.assertAlmostEqual(temp_50_50, (desert_temp + tundra_temp) / 2, delta=1.0)
        
        # Test moisture interpolation
        desert_moisture = (desert_params.moisture_range[0] + desert_params.moisture_range[1]) / 2
        tundra_moisture = (tundra_params.moisture_range[0] + tundra_params.moisture_range[1]) / 2
        
        moisture_50_50 = self.generator._interpolate_moisture(
            BiomeType.DESERT, BiomeType.TUNDRA, 0.5
        )
        
        # Should be around the average of desert and tundra moisture
        self.assertAlmostEqual(moisture_50_50, (desert_moisture + tundra_moisture) / 2, delta=0.1)


class TestBiomeConfigManager(unittest.TestCase):
    """Test cases for the BiomeConfigManager class"""
    
    def setUp(self):
        """Set up test environment"""
        # Use a temporary directory for configuration files
        self.config_dir = "tmp_test_biome_config"
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config_manager = BiomeConfigManager(config_directory=self.config_dir)
    
    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists(self.config_dir):
            shutil.rmtree(self.config_dir)
    
    def test_initialization(self):
        """Test initialization of config manager"""
        # Config directory should exist
        self.assertTrue(os.path.exists(self.config_dir))
        
        # Should have adjacency matrix
        self.assertIsNotNone(self.config_manager.adjacency_matrix)
    
    def test_save_load_configuration(self):
        """Test saving and loading configuration"""
        # Set a custom transition
        self.config_manager.set_custom_transition(
            "test_region",
            BiomeType.DESERT,
            BiomeType.TUNDRA,
            BiomeType.GRASSLAND,
            width=3
        )
        
        # Set a region override
        self.config_manager.set_region_override(
            "test_region",
            "transitions_enabled",
            True
        )
        
        # Save configuration
        self.assertTrue(self.config_manager.save_configuration())
        
        # Check if files were created
        self.assertTrue(os.path.exists(os.path.join(self.config_dir, "adjacency_matrix.json")))
        self.assertTrue(os.path.exists(os.path.join(self.config_dir, "custom_transitions.json")))
        self.assertTrue(os.path.exists(os.path.join(self.config_dir, "region_overrides.json")))
        
        # Create a new manager and load configuration
        new_manager = BiomeConfigManager(config_directory=self.config_dir)
        self.assertTrue(new_manager.load_configuration())
        
        # Check if custom transition was loaded
        custom = new_manager.get_custom_transition(
            "test_region",
            BiomeType.DESERT,
            BiomeType.TUNDRA
        )
        
        self.assertIsNotNone(custom)
        self.assertEqual(custom["transition_biome"], BiomeType.GRASSLAND.value)
        self.assertEqual(custom["width"], 3)
        
        # Check if region override was loaded
        enabled = new_manager.get_region_override(
            "test_region",
            "transitions_enabled"
        )
        
        self.assertEqual(enabled, True)
    
    def test_transition_biome_selection(self):
        """Test selection of transition biomes with custom rules"""
        # Set a custom transition
        self.config_manager.set_custom_transition(
            "custom_region",
            BiomeType.DESERT,
            BiomeType.TUNDRA,
            BiomeType.OASIS,
            width=2
        )
        
        # Get transition biomes for the custom region
        biomes = self.config_manager.get_transition_biomes(
            BiomeType.DESERT,
            BiomeType.TUNDRA,
            region_id="custom_region"
        )
        
        # Should have exactly one biome (the custom one)
        self.assertEqual(len(biomes), 1)
        self.assertEqual(biomes[0], BiomeType.OASIS)
        
        # Get transition biomes for another region (should use defaults)
        biomes = self.config_manager.get_transition_biomes(
            BiomeType.DESERT,
            BiomeType.TUNDRA,
            region_id="other_region"
        )
        
        # Should have multiple options from the adjacency matrix
        self.assertGreater(len(biomes), 0)
        self.assertNotEqual(biomes[0], BiomeType.OASIS)
    
    def test_transition_width(self):
        """Test transition width calculation with overrides"""
        # Set a region-wide override
        self.config_manager.set_region_override(
            "wide_region",
            "min_transition_width",
            5
        )
        
        # Get width for a specific biome pair in that region
        width = self.config_manager.get_transition_width(
            BiomeType.DESERT,
            BiomeType.TUNDRA,
            region_id="wide_region"
        )
        
        # Should use the region-wide override
        self.assertEqual(width, 5)
        
        # Set a specific biome pair override
        self.config_manager.set_custom_transition(
            "mixed_region",
            BiomeType.DESERT,
            BiomeType.TUNDRA,
            BiomeType.PLAINS,
            width=3
        )
        
        # Get width for that specific pair
        width = self.config_manager.get_transition_width(
            BiomeType.DESERT,
            BiomeType.TUNDRA,
            region_id="mixed_region"
        )
        
        # Should use the specific override
        self.assertEqual(width, 3)
        
        # Get width for a different pair in the same region
        width = self.config_manager.get_transition_width(
            BiomeType.DESERT,
            BiomeType.FOREST,
            region_id="mixed_region"
        )
        
        # Should use the default from adjacency matrix
        self.assertNotEqual(width, 3)
    
    def test_export_template(self):
        """Test exporting a configuration template"""
        template_path = os.path.join(self.config_dir, "template.json")
        
        # Export template
        self.assertTrue(self.config_manager.export_configuration_template(template_path))
        
        # Check if file was created
        self.assertTrue(os.path.exists(template_path))
        
        # Check file content
        with open(template_path, 'r') as f:
            import json
            data = json.load(f)
            
            # Should have documentation
            self.assertIn("documentation", data)
            
            # Should have examples
            self.assertIn("adjacency_rules_examples", data)
            self.assertIn("custom_transitions_examples", data)
            self.assertIn("region_overrides_examples", data)
            
            # Should list available biomes
            self.assertIn("available_biomes", data)
            self.assertEqual(len(data["available_biomes"]), len(BiomeType))


if __name__ == '__main__':
    unittest.main() 