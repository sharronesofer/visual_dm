"""
Property-Based Testing for World Generation System.

This module provides a property-based testing framework for validating world generation.
It ensures that generated worlds maintain certain invariants and properties across
different generation parameters.
"""

import random
import logging
from typing import Dict, List, Optional, Any, Tuple, Callable, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
import json

from app.core.models.world import World
from app.regions.worldgen_utils import WorldGenerator
from .world_validation import ValidationResult

logger = logging.getLogger(__name__)

@dataclass
class PropertyTestResult:
    """Result of a property-based test."""
    property_name: str
    is_valid: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "property_name": self.property_name,
            "is_valid": self.is_valid,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyTestResult':
        """Create from dictionary representation."""
        result = cls(
            property_name=data.get("property_name", "unknown"),
            is_valid=data.get("is_valid", False),
            message=data.get("message", ""),
            details=data.get("details", {})
        )
        if "timestamp" in data:
            result.timestamp = datetime.fromisoformat(data["timestamp"])
        return result

@dataclass
class PropertyTestCase:
    """A test case for property-based testing."""
    world_id: str
    seed: int
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "world_id": self.world_id,
            "seed": self.seed,
            "parameters": self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PropertyTestCase':
        """Create from dictionary representation."""
        return cls(
            world_id=data.get("world_id", ""),
            seed=data.get("seed", 0),
            parameters=data.get("parameters", {})
        )

class WorldProperty:
    """
    A property that a world should satisfy.
    
    Properties are predicates that check whether a world satisfies
    certain invariants. They are used in property-based testing to
    ensure that generated worlds maintain expected characteristics.
    """
    
    def __init__(self, name: str, property_func: Callable[[World], Tuple[bool, str, Dict[str, Any]]],
                 description: str = ""):
        """
        Initialize a world property.
        
        Args:
            name: Name of the property
            property_func: Function that tests the property
            description: Description of what the property tests
        """
        self.name = name
        self.property_func = property_func
        self.description = description
    
    def check(self, world: World) -> PropertyTestResult:
        """
        Check if a world satisfies this property.
        
        Args:
            world: The world to check
            
        Returns:
            Result of the property test
        """
        try:
            is_valid, message, details = self.property_func(world)
            return PropertyTestResult(
                property_name=self.name,
                is_valid=is_valid,
                message=message,
                details=details
            )
        except Exception as e:
            logger.error(f"Error checking property '{self.name}': {str(e)}")
            return PropertyTestResult(
                property_name=self.name,
                is_valid=False,
                message=f"Error checking property: {str(e)}",
                details={"error": str(e), "type": type(e).__name__}
            )

class PropertyBasedTesting:
    """
    Framework for property-based testing of world generation.
    
    This class provides functionality for defining world properties,
    generating test cases, and running property tests to ensure that
    generated worlds maintain expected invariants.
    """
    
    def __init__(self, world_generator: Optional[WorldGenerator] = None):
        """
        Initialize the property-based testing framework.
        
        Args:
            world_generator: Optional world generator for creating test worlds
        """
        self.world_generator = world_generator or WorldGenerator()
        self.properties: List[WorldProperty] = []
        self.test_cases: List[PropertyTestCase] = []
        self.test_results: Dict[str, Dict[str, PropertyTestResult]] = {}
        
        # Register default properties
        self._register_default_properties()
    
    def _register_default_properties(self):
        """Register default world properties."""
        # Consistency across regeneration
        self.register_property(
            "regeneration_consistency",
            self.check_regeneration_consistency,
            "World generation is deterministic with the same seed"
        )
        
        # Biome distribution
        self.register_property(
            "biome_distribution",
            self.check_biome_distribution,
            "Biomes are distributed according to expected distributions"
        )
        
        # Resource consistency
        self.register_property(
            "resource_consistency",
            self.check_resource_consistency,
            "Resources are consistent with their biome types"
        )
        
        # World connectivity
        self.register_property(
            "world_connectivity",
            self.check_world_connectivity,
            "All regions in the world are connected"
        )
        
        # Terrain variety
        self.register_property(
            "terrain_variety",
            self.check_terrain_variety,
            "World has sufficient variety of terrain types"
        )
    
    def register_property(self, name: str, property_func: Callable[[World], Tuple[bool, str, Dict[str, Any]]],
                          description: str = ""):
        """
        Register a new world property.
        
        Args:
            name: Name of the property
            property_func: Function that tests the property
            description: Description of what the property tests
        """
        self.properties.append(WorldProperty(name, property_func, description))
        logger.info(f"Registered world property: {name}")
    
    def generate_test_cases(self, count: int, parameter_ranges: Dict[str, Any] = None) -> List[PropertyTestCase]:
        """
        Generate test cases with random parameters.
        
        Args:
            count: Number of test cases to generate
            parameter_ranges: Optional ranges for parameters
            
        Returns:
            List of generated test cases
        """
        if parameter_ranges is None:
            parameter_ranges = {
                "size": (50, 500),
                "complexity": (0.1, 1.0),
                "region_density": (0.1, 0.9),
                "feature_density": (0.1, 0.9)
            }
        
        test_cases = []
        for _ in range(count):
            # Generate random parameters within specified ranges
            parameters = {}
            for param_name, param_range in parameter_ranges.items():
                if isinstance(param_range, tuple) and len(param_range) == 2:
                    min_val, max_val = param_range
                    if isinstance(min_val, int) and isinstance(max_val, int):
                        parameters[param_name] = random.randint(min_val, max_val)
                    else:
                        parameters[param_name] = random.uniform(min_val, max_val)
                elif isinstance(param_range, list):
                    parameters[param_name] = random.choice(param_range)
            
            # Generate a random seed
            seed = random.randint(0, 1000000)
            
            # Create a test case
            test_case = PropertyTestCase(
                world_id=f"test_world_{seed}",
                seed=seed,
                parameters=parameters
            )
            
            test_cases.append(test_case)
        
        # Store the generated test cases
        self.test_cases.extend(test_cases)
        
        return test_cases
    
    def run_property_tests(self, world: World) -> Dict[str, PropertyTestResult]:
        """
        Run all registered property tests on a world.
        
        Args:
            world: The world to test
            
        Returns:
            Dictionary mapping property names to test results
        """
        results = {}
        
        logger.info(f"Running {len(self.properties)} property tests on world {world.world_id}")
        
        for prop in self.properties:
            result = prop.check(world)
            results[prop.name] = result
            
            # Log result
            if result.is_valid:
                logger.info(f"Property '{prop.name}' passed for world {world.world_id}")
            else:
                logger.warning(f"Property '{prop.name}' failed for world {world.world_id}: {result.message}")
        
        # Store results
        self.test_results[world.world_id] = results
        
        return results
    
    def are_properties_satisfied(self, world: World, property_names: Optional[List[str]] = None) -> bool:
        """
        Check if a world satisfies all specified properties.
        
        Args:
            world: The world to test
            property_names: Optional list of property names to check (if None, all properties are checked)
            
        Returns:
            True if all specified properties are satisfied, False otherwise
        """
        results = self.run_property_tests(world)
        
        # Filter results if property names are specified
        if property_names:
            results = {name: result for name, result in results.items() if name in property_names}
        
        return all(result.is_valid for result in results.values())
    
    def get_property_test_report(self, world: World) -> Dict[str, Any]:
        """
        Generate a detailed report of property tests for a world.
        
        Args:
            world: The world to test
            
        Returns:
            Dictionary containing test results and summary information
        """
        results = self.run_property_tests(world)
        
        # Calculate summary statistics
        total_properties = len(results)
        passed_properties = sum(1 for result in results.values() if result.is_valid)
        
        return {
            "world_id": world.world_id,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_properties": total_properties,
                "passed_properties": passed_properties,
                "failed_properties": total_properties - passed_properties,
                "pass_percentage": 100.0 * passed_properties / total_properties if total_properties > 0 else 0.0
            },
            "results": {name: result.to_dict() for name, result in results.items()}
        }
    
    def find_minimal_failing_case(self, property_name: str, max_iterations: int = 100) -> Optional[Tuple[PropertyTestCase, World]]:
        """
        Find a minimal test case that fails a specific property.
        
        Args:
            property_name: Name of the property to test
            max_iterations: Maximum number of iterations for shrinking
            
        Returns:
            Tuple of the minimal test case and the corresponding world, or None if no failing case is found
        """
        # Generate random test cases
        test_cases = self.generate_test_cases(10)
        
        # Find a failing test case
        failing_case = None
        failing_world = None
        
        for test_case in test_cases:
            # Generate a world with the test case parameters
            try:
                world = self._generate_world_from_test_case(test_case)
                
                # Run the specific property test
                property_obj = next((p for p in self.properties if p.name == property_name), None)
                if not property_obj:
                    logger.error(f"Property '{property_name}' not found")
                    return None
                
                result = property_obj.check(world)
                
                if not result.is_valid:
                    failing_case = test_case
                    failing_world = world
                    break
            except Exception as e:
                logger.error(f"Error generating world for test case: {str(e)}")
        
        if not failing_case:
            logger.info(f"No failing case found for property '{property_name}'")
            return None
        
        logger.info(f"Found failing case for property '{property_name}', attempting to minimize")
        
        # Try to minimize the failing case
        current_case = failing_case
        current_world = failing_world
        
        for _ in range(max_iterations):
            # Try to reduce the parameters
            smaller_case = self._shrink_test_case(current_case)
            
            if smaller_case == current_case:
                # No further reduction possible
                break
            
            # Check if the smaller case still fails
            try:
                smaller_world = self._generate_world_from_test_case(smaller_case)
                property_obj = next((p for p in self.properties if p.name == property_name), None)
                result = property_obj.check(smaller_world)
                
                if not result.is_valid:
                    # The smaller case still fails, use it as the new current case
                    current_case = smaller_case
                    current_world = smaller_world
                    logger.info(f"Found smaller failing case for property '{property_name}'")
            except Exception as e:
                logger.error(f"Error testing smaller case: {str(e)}")
        
        return (current_case, current_world)
    
    def _generate_world_from_test_case(self, test_case: PropertyTestCase) -> World:
        """Generate a world from a test case."""
        # Set the random seed
        random.seed(test_case.seed)
        
        # Create a world generator with the seed
        generator = WorldGenerator(seed=test_case.seed)
        
        # Generate a world based on the test case parameters
        # This is a simplified placeholder implementation
        # In a real implementation, this would use the world generator to create a complete world
        
        # For now, we create a minimal world structure
        world = World(
            name=f"Test World {test_case.seed}",
            world_id=test_case.world_id
        )
        
        # Apply parameters to the world
        # This would be replaced with actual world generation code
        
        return world
    
    def _shrink_test_case(self, test_case: PropertyTestCase) -> PropertyTestCase:
        """
        Try to shrink a test case by reducing parameter values.
        
        Args:
            test_case: The test case to shrink
            
        Returns:
            A smaller test case, or the same test case if no further reduction is possible
        """
        # Copy the parameters
        new_params = test_case.parameters.copy()
        
        # Try to reduce each parameter
        for param_name, param_value in test_case.parameters.items():
            if isinstance(param_value, (int, float)) and param_value > 0:
                # Try to halve the value
                new_params[param_name] = param_value / 2
        
        # Create a new test case with the reduced parameters
        return PropertyTestCase(
            world_id=test_case.world_id,
            seed=test_case.seed,
            parameters=new_params
        )
    
    # Implementation of default property checks
    
    def check_regeneration_consistency(self, world: World) -> Tuple[bool, str, Dict[str, Any]]:
        """Check that world generation is deterministic with the same seed."""
        # This is a placeholder for the regeneration consistency check
        # It will be replaced with actual consistency check logic
        return (
            True,
            "Regeneration consistency check not yet implemented",
            {"status": "placeholder"}
        )
    
    def check_biome_distribution(self, world: World) -> Tuple[bool, str, Dict[str, Any]]:
        """Check that biomes are distributed according to expected distributions."""
        # This is a placeholder for the biome distribution check
        # It will be replaced with actual biome distribution check logic
        return (
            True,
            "Biome distribution check not yet implemented",
            {"status": "placeholder"}
        )
    
    def check_resource_consistency(self, world: World) -> Tuple[bool, str, Dict[str, Any]]:
        """Check that resources are consistent with their biome types."""
        # This is a placeholder for the resource consistency check
        # It will be replaced with actual resource consistency check logic
        return (
            True,
            "Resource consistency check not yet implemented",
            {"status": "placeholder"}
        )
    
    def check_world_connectivity(self, world: World) -> Tuple[bool, str, Dict[str, Any]]:
        """Check that all regions in the world are connected."""
        # This is a placeholder for the world connectivity check
        # It will be replaced with actual world connectivity check logic
        return (
            True,
            "World connectivity check not yet implemented",
            {"status": "placeholder"}
        )
    
    def check_terrain_variety(self, world: World) -> Tuple[bool, str, Dict[str, Any]]:
        """Check that the world has sufficient variety of terrain types."""
        # This is a placeholder for the terrain variety check
        # It will be replaced with actual terrain variety check logic
        return (
            True,
            "Terrain variety check not yet implemented",
            {"status": "placeholder"}
        ) 