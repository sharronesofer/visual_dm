"""
Test module for region generators

This module tests the various region generator implementations and
the integration with the deterministic RNG system.
"""
import unittest
import sys
import os
import time
from typing import Dict, Any

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from python_converted.src.worldgen.core.IWorldGenerator import (
    RegionGeneratorOptions, GeneratorType
)
from python_converted.src.worldgen.core.simple_test import DeterministicRNG, ISeedConfig
from python_converted.src.worldgen.core.seed_manager import SeedManager
from python_converted.src.worldgen.region.BaseRegionGenerator import BaseRegionGenerator
from python_converted.src.worldgen.region.ProceduralRegionGenerator import ProceduralRegionGenerator
from python_converted.src.worldgen.region.HandcraftedRegionGenerator import (
    HandcraftedRegionGenerator, HandcraftedRegionGeneratorOptions
)
from python_converted.src.worldgen.region.RegionGeneratorFactory import RegionGeneratorFactory

class TestRegionGenerators(unittest.TestCase):
    """Test cases for region generator implementations"""
    
    def setUp(self):
        """Set up test cases"""
        # Create a seed manager with a fixed seed for deterministic testing
        self.seed_manager = SeedManager(master_seed=12345)
        
        # Create basic generation options
        self.options = RegionGeneratorOptions(
            width=16,
            height=16,
            seed=self.seed_manager.get_master_seed().value,
            region_type="test_region"
        )
        
        # Create generator instances
        self.procedural_generator = ProceduralRegionGenerator()
        self.handcrafted_generator = HandcraftedRegionGenerator()
        
        # Create the factory
        self.factory = RegionGeneratorFactory()
    
    def test_generator_types(self):
        """Test that generators report the correct types"""
        self.assertEqual(self.procedural_generator.get_type(), GeneratorType.PROCEDURAL)
        self.assertEqual(self.handcrafted_generator.get_type(), GeneratorType.HANDCRAFTED)
    
    def test_procedural_generation(self):
        """Test that procedural generation works and produces valid regions"""
        # Generate a region
        result = self.procedural_generator.generate(self.options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertIsNotNone(result.region)
        
        # Check basic region properties
        region = result.region
        self.assertEqual(region.width, self.options.width)
        self.assertEqual(region.height, self.options.height)
        self.assertGreater(len(region.cells), 0)
        
        # Check that cells are properly initialized
        for cell in region.cells:
            self.assertGreaterEqual(cell.x, 0)
            self.assertLess(cell.x, region.width)
            self.assertGreaterEqual(cell.y, 0)
            self.assertLess(cell.y, region.height)
            self.assertIsNotNone(cell.terrain_type)
            self.assertGreaterEqual(cell.elevation, 0.0)
            self.assertLessEqual(cell.elevation, 1.0)
    
    def test_handcrafted_generation(self):
        """Test that handcrafted generation works and produces valid regions"""
        # Create handcrafted options
        handcrafted_options = HandcraftedRegionGeneratorOptions(
            template_id="sample_template",  # This should be created automatically
            width=16,
            height=16,
            seed=self.seed_manager.get_master_seed().value
        )
        
        # Generate a region
        result = self.handcrafted_generator.generate(handcrafted_options)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertIsNotNone(result.region)
        
        # Check basic region properties
        region = result.region
        self.assertEqual(region.width, handcrafted_options.width)
        self.assertEqual(region.height, handcrafted_options.height)
        self.assertGreater(len(region.cells), 0)
        self.assertGreater(len(region.points_of_interest), 0)
        self.assertGreater(len(region.resources), 0)
    
    def test_factory_registration(self):
        """Test that the factory correctly registers and retrieves generators"""
        # The factory should already have the built-in generators registered
        self.assertIsNotNone(self.factory.get_generator('procedural'))
        self.assertIsNotNone(self.factory.get_generator('handcrafted'))
        
        # Check getting by type
        self.assertIsNotNone(self.factory.get_generator_by_type(GeneratorType.PROCEDURAL))
        self.assertIsNotNone(self.factory.get_generator_by_type(GeneratorType.HANDCRAFTED))
        
        # Register a custom generator
        class CustomGenerator(BaseRegionGenerator):
            def get_type(self) -> GeneratorType:
                return GeneratorType.HYBRID
                
            def get_capabilities(self) -> Dict[str, Any]:
                return {"custom": True}
                
            def _generate_region(self, options, rng):
                # Use the procedural generator for simplicity
                return self.factory.get_generator('procedural').generate(options).region
        
        custom_generator = CustomGenerator()
        self.factory.register_generator('custom', custom_generator)
        
        # Check it was registered
        self.assertIsNotNone(self.factory.get_generator('custom'))
        self.assertEqual(self.factory.get_generator('custom').get_type(), GeneratorType.HYBRID)
    
    def test_factory_convenience_methods(self):
        """Test that the factory convenience methods work correctly"""
        # Test procedural generation
        result = self.factory.create_procedural_region(self.options)
        self.assertTrue(result.success)
        
        # Test handcrafted generation
        handcrafted_options = HandcraftedRegionGeneratorOptions(
            template_id="sample_template",
            width=16,
            height=16,
            seed=self.seed_manager.get_master_seed().value
        )
        result = self.factory.create_handcrafted_region(handcrafted_options)
        self.assertTrue(result.success)
    
    def test_deterministic_generation(self):
        """Test that generation is deterministic with the same seed"""
        # Generate a region
        result1 = self.procedural_generator.generate(self.options)
        
        # Create a new generator instance with the same options
        new_generator = ProceduralRegionGenerator()
        result2 = new_generator.generate(self.options)
        
        # The regions should have the same structure (though not the same object)
        self.assertEqual(len(result1.region.cells), len(result2.region.cells))
        
        # Check that cell terrain types match
        for i in range(len(result1.region.cells)):
            cell1 = result1.region.cells[i]
            cell2 = result2.region.cells[i]
            self.assertEqual(cell1.terrain_type, cell2.terrain_type)
            self.assertEqual(cell1.biome, cell2.biome)
    
    def test_different_seeds_produce_different_results(self):
        """Test that different seeds produce different regions"""
        # Generate a region with the first seed
        result1 = self.procedural_generator.generate(self.options)
        
        # Create new options with a different seed
        options2 = RegionGeneratorOptions(
            width=16,
            height=16,
            seed=self.seed_manager.get_master_seed().value + 1,  # Different seed
            region_type="test_region"
        )
        result2 = self.procedural_generator.generate(options2)
        
        # Check if there are differences in the terrain
        different_cells = 0
        for i in range(len(result1.region.cells)):
            cell1 = result1.region.cells[i]
            cell2 = result2.region.cells[i]
            if cell1.terrain_type != cell2.terrain_type or cell1.biome != cell2.biome:
                different_cells += 1
        
        # With different seeds, at least some cells should be different
        self.assertGreater(different_cells, 0)
    
    def test_generator_integration_with_seed_manager(self):
        """Test that the generators integrate correctly with the seed manager"""
        # Create a specific seed manager for this test
        test_seed_manager = SeedManager(master_seed=54321)
        
        # Create a new generator
        test_generator = ProceduralRegionGenerator()
        test_generator.seed_manager = test_seed_manager
        
        # Create options with the seed from the seed manager
        test_options = RegionGeneratorOptions(
            width=16,
            height=16,
            seed=test_seed_manager.get_master_seed().value,
            region_type="test_integration"
        )
        
        # Generate a region
        result = test_generator.generate(test_options)
        
        # Verify the result
        self.assertTrue(result.success)
        
        # Check that the seed in the metadata matches what we set
        self.assertEqual(result.metadata.get("seed"), test_options.seed)

if __name__ == '__main__':
    unittest.main() 