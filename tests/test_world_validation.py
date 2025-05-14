"""
Tests for the World Validation System.

This module contains unit tests for the world validation system,
validating the correctness of validation rules and property-based testing.
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
import random

from app.core.models.world import World, WorldState
from app.regions.worldgen_utils import WorldGenerator
from app.core.persistence.world_persistence import WorldPersistenceManager, FileSystemStorageStrategy
from app.core.validation.world_validation import WorldValidator, ValidationResult
from app.core.validation.property_testing import PropertyBasedTesting, PropertyTestResult, WorldProperty

class TestValidationResult(unittest.TestCase):
    """Test the ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating a ValidationResult."""
        result = ValidationResult(is_valid=True, message="Test passed", details={"key": "value"})
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.message, "Test passed")
        self.assertEqual(result.details, {"key": "value"})
        self.assertIsNotNone(result.timestamp)
    
    def test_validation_result_serialization(self):
        """Test serializing a ValidationResult to a dictionary."""
        result = ValidationResult(is_valid=False, message="Test failed", details={"reason": "error"})
        
        result_dict = result.to_dict()
        
        self.assertFalse(result_dict["is_valid"])
        self.assertEqual(result_dict["message"], "Test failed")
        self.assertEqual(result_dict["details"], {"reason": "error"})
        self.assertIsNotNone(result_dict["timestamp"])
    
    def test_validation_result_deserialization(self):
        """Test deserializing a ValidationResult from a dictionary."""
        data = {
            "is_valid": True,
            "message": "Test passed",
            "details": {"key": "value"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = ValidationResult.from_dict(data)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.message, "Test passed")
        self.assertEqual(result.details, {"key": "value"})
        self.assertIsNotNone(result.timestamp)

class TestWorldValidator(unittest.TestCase):
    """Test the WorldValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = WorldValidator()
        
        # Create a mock world
        self.mock_world = self._create_mock_world()
    
    def _create_mock_world(self):
        """Create a mock world for testing."""
        world = MagicMock(spec=World)
        world.world_id = "test_world_id"
        world.name = "Test World"
        
        # Mock world state
        state = MagicMock(spec=WorldState)
        
        # Mock regions
        region1 = MagicMock()
        region1.id = "region1"
        region1.name = "Region 1"
        region1.terrain_types = ["plains", "forest"]
        
        region2 = MagicMock()
        region2.id = "region2"
        region2.name = "Region 2"
        region2.terrain_types = ["mountains", "tundra"]
        
        state.regions = [region1, region2]
        
        # Set up connections between regions
        state.connections = [
            {"region1": "region1", "region2": "region2"}
        ]
        
        world.state = state
        
        return world
    
    def test_validator_initialization(self):
        """Test initializing a WorldValidator."""
        self.assertGreater(len(self.validator.validation_rules), 0)
        self.assertEqual(len(self.validator.validation_results), 0)
    
    def test_register_validation_rule(self):
        """Test registering a new validation rule."""
        # Define a test validation rule
        def test_rule(world):
            return ValidationResult(is_valid=True, message="Test rule passed")
        
        # Register the rule
        initial_rule_count = len(self.validator.validation_rules)
        self.validator.register_validation_rule("test_rule", test_rule, "Test validation rule")
        
        # Check that the rule was registered
        self.assertEqual(len(self.validator.validation_rules), initial_rule_count + 1)
        
        # Find the registered rule
        registered_rule = next((r for r in self.validator.validation_rules if r["id"] == "test_rule"), None)
        self.assertIsNotNone(registered_rule)
        self.assertEqual(registered_rule["description"], "Test validation rule")
    
    def test_validate_world(self):
        """Test validating a world."""
        # Validate the mock world
        results = self.validator.validate_world(self.mock_world)
        
        # Check that results were returned for all rules
        self.assertEqual(len(results), len(self.validator.validation_rules))
        
        # Check that the results were stored
        self.assertIn(self.mock_world.world_id, self.validator.validation_results)
    
    def test_validate_world_with_specific_rules(self):
        """Test validating a world with specific rules."""
        # Validate the mock world with only the basic structure rule
        results = self.validator.validate_world(self.mock_world, ["basic_structure"])
        
        # Check that only one result was returned
        self.assertEqual(len(results), 1)
        self.assertIn("basic_structure", results)
    
    def test_is_world_valid(self):
        """Test checking if a world is valid."""
        # Set up a validation rule that always passes
        def always_pass(world):
            return ValidationResult(is_valid=True, message="Always pass")
        
        # Set up a validation rule that always fails
        def always_fail(world):
            return ValidationResult(is_valid=False, message="Always fail")
        
        # Create a validator with these rules
        validator = WorldValidator()
        validator.validation_rules = []
        validator.register_validation_rule("always_pass", always_pass, "Always pass")
        validator.register_validation_rule("always_fail", always_fail, "Always fail")
        
        # Test with all rules (should fail because one rule fails)
        self.assertFalse(validator.is_world_valid(self.mock_world))
        
        # Test with only the passing rule
        self.assertTrue(validator.is_world_valid(self.mock_world, ["always_pass"]))
        
        # Test with only the failing rule
        self.assertFalse(validator.is_world_valid(self.mock_world, ["always_fail"]))
    
    def test_get_validation_report(self):
        """Test generating a validation report."""
        # Generate a report for the mock world
        report = self.validator.get_validation_report(self.mock_world)
        
        # Check the report structure
        self.assertEqual(report["world_id"], self.mock_world.world_id)
        self.assertEqual(report["world_name"], self.mock_world.name)
        self.assertIn("timestamp", report)
        self.assertIn("summary", report)
        self.assertIn("results", report)
        
        # Check the summary
        summary = report["summary"]
        self.assertEqual(summary["total_rules"], len(self.validator.validation_rules))
        self.assertIn("passed_rules", summary)
        self.assertIn("failed_rules", summary)
        self.assertIn("pass_percentage", summary)
        
        # Check the results
        results = report["results"]
        self.assertEqual(len(results), len(self.validator.validation_rules))
    
    def test_validate_basic_structure(self):
        """Test the basic structure validation rule."""
        # Test with a valid world
        result = self.validator.validate_basic_structure(self.mock_world)
        self.assertTrue(result.is_valid)
        
        # Test with a world missing required fields
        invalid_world = MagicMock(spec=World)
        invalid_world.world_id = "test_world_id"
        invalid_world.name = ""  # Empty name
        invalid_world.state = None  # No state
        
        result = self.validator.validate_basic_structure(invalid_world)
        self.assertFalse(result.is_valid)
        self.assertIn("name", result.details["missing_fields"])
        self.assertIn("state", result.details["missing_fields"])
        
        # Test with a world with no regions
        invalid_world = MagicMock(spec=World)
        invalid_world.world_id = "test_world_id"
        invalid_world.name = "Test World"
        invalid_world.state = MagicMock(spec=WorldState)
        invalid_world.state.regions = []
        
        result = self.validator.validate_basic_structure(invalid_world)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.message, "World has no regions")

class TestPropertyBasedTesting(unittest.TestCase):
    """Test the PropertyBasedTesting class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.property_tester = PropertyBasedTesting()
        
        # Create a mock world
        self.mock_world = self._create_mock_world()
    
    def _create_mock_world(self):
        """Create a mock world for testing."""
        world = MagicMock(spec=World)
        world.world_id = "test_world_id"
        world.name = "Test World"
        
        # Mock world state
        state = MagicMock(spec=WorldState)
        
        # Mock regions
        region1 = MagicMock()
        region1.id = "region1"
        region1.name = "Region 1"
        region1.biome = "plains"
        
        region2 = MagicMock()
        region2.id = "region2"
        region2.name = "Region 2"
        region2.biome = "forest"
        
        region3 = MagicMock()
        region3.id = "region3"
        region3.name = "Region 3"
        region3.biome = "mountains"
        
        state.regions = [region1, region2, region3]
        
        world.state = state
        
        return world
    
    def test_property_tester_initialization(self):
        """Test initializing a PropertyBasedTesting."""
        self.assertGreater(len(self.property_tester.properties), 0)
        self.assertEqual(len(self.property_tester.test_cases), 0)
        self.assertEqual(len(self.property_tester.test_results), 0)
    
    def test_register_property(self):
        """Test registering a new world property."""
        # Define a test property
        def test_property(world):
            return (True, "Test property passed", {"key": "value"})
        
        # Register the property
        initial_property_count = len(self.property_tester.properties)
        self.property_tester.register_property("test_property", test_property, "Test world property")
        
        # Check that the property was registered
        self.assertEqual(len(self.property_tester.properties), initial_property_count + 1)
        
        # Find the registered property
        registered_property = next((p for p in self.property_tester.properties if p.name == "test_property"), None)
        self.assertIsNotNone(registered_property)
        self.assertEqual(registered_property.description, "Test world property")
    
    def test_generate_test_cases(self):
        """Test generating test cases."""
        # Generate test cases
        count = 5
        test_cases = self.property_tester.generate_test_cases(count)
        
        # Check that the correct number of test cases were generated
        self.assertEqual(len(test_cases), count)
        
        # Check that the test cases have the expected structure
        for test_case in test_cases:
            self.assertIsNotNone(test_case.world_id)
            self.assertIsNotNone(test_case.seed)
            self.assertIsInstance(test_case.parameters, dict)
    
    def test_run_property_tests(self):
        """Test running property tests on a world."""
        # Run property tests
        results = self.property_tester.run_property_tests(self.mock_world)
        
        # Check that results were returned for all properties
        self.assertEqual(len(results), len(self.property_tester.properties))
        
        # Check that the results were stored
        self.assertIn(self.mock_world.world_id, self.property_tester.test_results)
    
    def test_are_properties_satisfied(self):
        """Test checking if a world satisfies properties."""
        # Set up a property that always passes
        def always_pass(world):
            return (True, "Always pass", {})
        
        # Set up a property that always fails
        def always_fail(world):
            return (False, "Always fail", {})
        
        # Create a property tester with these properties
        property_tester = PropertyBasedTesting()
        property_tester.properties = []
        property_tester.register_property("always_pass", always_pass, "Always pass")
        property_tester.register_property("always_fail", always_fail, "Always fail")
        
        # Test with all properties (should fail because one property fails)
        self.assertFalse(property_tester.are_properties_satisfied(self.mock_world))
        
        # Test with only the passing property
        self.assertTrue(property_tester.are_properties_satisfied(self.mock_world, ["always_pass"]))
        
        # Test with only the failing property
        self.assertFalse(property_tester.are_properties_satisfied(self.mock_world, ["always_fail"]))
    
    def test_get_property_test_report(self):
        """Test generating a property test report."""
        # Generate a report for the mock world
        report = self.property_tester.get_property_test_report(self.mock_world)
        
        # Check the report structure
        self.assertEqual(report["world_id"], self.mock_world.world_id)
        self.assertIn("timestamp", report)
        self.assertIn("summary", report)
        self.assertIn("results", report)
        
        # Check the summary
        summary = report["summary"]
        self.assertEqual(summary["total_properties"], len(self.property_tester.properties))
        self.assertIn("passed_properties", summary)
        self.assertIn("failed_properties", summary)
        self.assertIn("pass_percentage", summary)
        
        # Check the results
        results = report["results"]
        self.assertEqual(len(results), len(self.property_tester.properties))

if __name__ == '__main__':
    unittest.main() 