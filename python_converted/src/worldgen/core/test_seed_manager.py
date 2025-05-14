"""
Unit tests for the SeedManager class
"""
import unittest
import sys
import os
import json
from typing import Dict, Any

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from python_converted.src.worldgen.core.seed_manager import SeedManager, SeedInfo

class TestSeedManager(unittest.TestCase):
    """Test cases for SeedManager class"""
    
    def setUp(self):
        """Set up test cases"""
        self.master_seed = 12345
        self.seed_manager = SeedManager(master_seed=self.master_seed)
    
    def test_master_seed_initialization(self):
        """Test that the SeedManager is initialized with the correct master seed"""
        master_info = self.seed_manager.get_master_seed()
        self.assertEqual(master_info.value, self.master_seed)
        self.assertEqual(master_info.name, "master")
        self.assertIsNone(master_info.parent_name)
    
    def test_auto_generated_master_seed(self):
        """Test that the SeedManager generates a master seed when none is provided"""
        auto_manager = SeedManager()
        master_info = auto_manager.get_master_seed()
        self.assertIsNotNone(master_info.value)
        self.assertGreater(master_info.value, 0)
    
    def test_seed_registration(self):
        """Test registering a new seed"""
        seed_value = 54321
        seed_name = "test_seed"
        
        seed_info = self.seed_manager.register_seed(seed_value, seed_name)
        
        self.assertEqual(seed_info.value, seed_value)
        self.assertEqual(seed_info.name, seed_name)
        self.assertIsNone(seed_info.parent_name)
        
        # Verify we can retrieve it
        retrieved_value = self.seed_manager.get_seed(seed_name)
        self.assertEqual(retrieved_value, seed_value)
        
        retrieved_info = self.seed_manager.get_seed_info(seed_name)
        self.assertEqual(retrieved_info.value, seed_value)
        self.assertEqual(retrieved_info.name, seed_name)
    
    def test_seed_registration_with_parent(self):
        """Test registering a new seed with a parent"""
        parent_value = 11111
        parent_name = "parent_seed"
        self.seed_manager.register_seed(parent_value, parent_name)
        
        child_value = 22222
        child_name = "child_seed"
        child_info = self.seed_manager.register_seed(child_value, child_name, parent_name=parent_name)
        
        self.assertEqual(child_info.value, child_value)
        self.assertEqual(child_info.name, child_name)
        self.assertEqual(child_info.parent_name, parent_name)
        
        # Verify the parent-child relationship is tracked
        children = self.seed_manager.get_child_seeds(parent_name)
        self.assertIn(child_name, children)
    
    def test_duplicate_seed_name_raises_error(self):
        """Test that registering a duplicate seed name raises an error"""
        seed_name = "duplicate_test"
        self.seed_manager.register_seed(12345, seed_name)
        
        with self.assertRaises(ValueError):
            self.seed_manager.register_seed(67890, seed_name)
    
    def test_retrieve_nonexistent_seed_raises_error(self):
        """Test that trying to retrieve a non-existent seed raises an error"""
        with self.assertRaises(KeyError):
            self.seed_manager.get_seed("nonexistent_seed")
            
        with self.assertRaises(KeyError):
            self.seed_manager.get_seed_info("nonexistent_seed")
    
    def test_seed_derivation(self):
        """Test deriving a new seed from a parent seed"""
        # Derive from the master seed
        derived_name = "derived_seed"
        derived_value = self.seed_manager.derive_seed(derived_name)
        
        # Verify it's registered correctly
        self.assertEqual(self.seed_manager.get_seed(derived_name), derived_value)
        derived_info = self.seed_manager.get_seed_info(derived_name)
        self.assertEqual(derived_info.value, derived_value)
        self.assertEqual(derived_info.name, derived_name)
        self.assertEqual(derived_info.parent_name, "master")
        
        # Verify determinism - deriving the same seed name from the same parent
        # should produce the same value
        manager2 = SeedManager(master_seed=self.master_seed)
        derived_value2 = manager2.derive_seed(derived_name)
        self.assertEqual(derived_value, derived_value2)
    
    def test_hierarchical_seed_derivation(self):
        """Test multi-level seed derivation"""
        # Create a chain of derived seeds
        level1_name = "level1"
        level1_value = self.seed_manager.derive_seed(level1_name)
        
        level2_name = "level2"
        level2_value = self.seed_manager.derive_seed(level2_name, parent_name=level1_name)
        
        level3_name = "level3"
        level3_value = self.seed_manager.derive_seed(level3_name, parent_name=level2_name)
        
        # Verify the values and relationships
        self.assertEqual(self.seed_manager.get_seed(level1_name), level1_value)
        self.assertEqual(self.seed_manager.get_seed(level2_name), level2_value)
        self.assertEqual(self.seed_manager.get_seed(level3_name), level3_value)
        
        level3_info = self.seed_manager.get_seed_info(level3_name)
        self.assertEqual(level3_info.parent_name, level2_name)
        
        # Verify the hierarchy tracking
        level1_children = self.seed_manager.get_child_seeds(level1_name)
        self.assertIn(level2_name, level1_children)
        
        level2_children = self.seed_manager.get_child_seeds(level2_name)
        self.assertIn(level3_name, level2_children)
    
    def test_deriving_from_nonexistent_parent_raises_error(self):
        """Test that deriving from a non-existent parent raises an error"""
        with self.assertRaises(ValueError):
            self.seed_manager.derive_seed("test_seed", parent_name="nonexistent_parent")
    
    def test_duplicate_derived_seed_name_raises_error(self):
        """Test that deriving a seed with a duplicate name raises an error"""
        seed_name = "duplicate_derived"
        self.seed_manager.derive_seed(seed_name)
        
        with self.assertRaises(ValueError):
            self.seed_manager.derive_seed(seed_name)
    
    def test_deterministic_derivation(self):
        """Test that seed derivation is deterministic"""
        # Create the same seed hierarchy in two different managers
        manager1 = SeedManager(master_seed=12345)
        manager2 = SeedManager(master_seed=12345)
        
        # Create identical derivation paths
        seed1 = manager1.derive_seed("level1")
        child1 = manager1.derive_seed("level2", parent_name="level1")
        
        seed2 = manager2.derive_seed("level1")
        child2 = manager2.derive_seed("level2", parent_name="level1")
        
        # Verify they produce identical results
        self.assertEqual(seed1, seed2)
        self.assertEqual(child1, child2)
        
        # Different paths should produce different results
        alt_child1 = manager1.derive_seed("alt_level2", parent_name="level1")
        alt_child2 = manager2.derive_seed("alt_level2", parent_name="level1")
        
        self.assertEqual(alt_child1, alt_child2)  # Same between managers
        self.assertNotEqual(child1, alt_child1)  # Different from other path
    
    def test_seed_export_and_import(self):
        """Test exporting and importing seed history"""
        # Create a complex seed hierarchy
        self.seed_manager.derive_seed("region")
        self.seed_manager.derive_seed("terrain", parent_name="region")
        self.seed_manager.derive_seed("vegetation", parent_name="region")
        self.seed_manager.derive_seed("mountains", parent_name="terrain")
        self.seed_manager.derive_seed("rivers", parent_name="terrain")
        
        # Export the seed history
        history = self.seed_manager.export_seed_history()
        
        # Create a new manager and import the history
        new_manager = SeedManager(master_seed=99999)  # Different master seed
        new_manager.import_seed_history(history)
        
        # Verify the master seed was correctly imported
        self.assertEqual(new_manager.get_master_seed().value, self.master_seed)
        
        # Verify all seeds were imported correctly
        seed_names = ["region", "terrain", "vegetation", "mountains", "rivers"]
        for name in seed_names:
            # The values should match between managers
            self.assertEqual(
                self.seed_manager.get_seed(name),
                new_manager.get_seed(name)
            )
            
            # The parent relationships should match
            original_info = self.seed_manager.get_seed_info(name)
            imported_info = new_manager.get_seed_info(name)
            self.assertEqual(original_info.parent_name, imported_info.parent_name)
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies during import"""
        # Create a history with a circular dependency
        circular_history = {
            "master_seed": 12345,
            "seeds": {
                "master": {
                    "value": 12345,
                    "parent": None,
                    "timestamp": 0,
                    "context": {}
                },
                "a": {
                    "value": 11111,
                    "parent": "b",
                    "timestamp": 0,
                    "context": {}
                },
                "b": {
                    "value": 22222,
                    "parent": "a",
                    "timestamp": 0,
                    "context": {}
                }
            }
        }
        
        # Import should raise a ValueError
        with self.assertRaises(ValueError):
            manager = SeedManager()
            manager.import_seed_history(circular_history)
    
    def test_invalid_history_format_raises_error(self):
        """Test that importing an invalid history format raises an error"""
        invalid_history = {"invalid": "format"}
        
        with self.assertRaises(ValueError):
            manager = SeedManager()
            manager.import_seed_history(invalid_history)
    
    def test_seed_with_context(self):
        """Test registering a seed with context information"""
        context = {
            "purpose": "terrain_generation",
            "parameters": {
                "resolution": 256,
                "octaves": 8
            }
        }
        
        seed_name = "terrain_with_context"
        seed_info = self.seed_manager.register_seed(54321, seed_name, context=context)
        
        # Verify the context was stored
        self.assertEqual(seed_info.context, context)
        
        # Verify the context is preserved when retrieving
        retrieved_info = self.seed_manager.get_seed_info(seed_name)
        self.assertEqual(retrieved_info.context, context)
        
        # Verify context is preserved in export/import
        history = self.seed_manager.export_seed_history()
        new_manager = SeedManager()
        new_manager.import_seed_history(history)
        
        imported_info = new_manager.get_seed_info(seed_name)
        self.assertEqual(imported_info.context, context)

if __name__ == '__main__':
    unittest.main() 