"""
World Validation System for World Generation.

This package provides a comprehensive validation system for the World Generation System,
including automated validation scripts, property-based tests, and manual review tools.
"""

from app.core.validation.world_validation import WorldValidator, ValidationResult
from app.core.validation.property_testing import PropertyBasedTesting, PropertyTestResult, WorldProperty
from app.core.validation.biome_validation import (
    validate_biome_adjacency,
    validate_thermal_consistency,
    validate_elevation_consistency,
    validate_biome_distribution,
    validate_river_continuity
)
from app.core.validation.validation_api import (
    validation_bp,
    validate_world_cli,
    property_test_world_cli
)

__all__ = [
    "WorldValidator",
    "ValidationResult",
    "PropertyBasedTesting",
    "PropertyTestResult",
    "WorldProperty",
    "validate_biome_adjacency",
    "validate_thermal_consistency",
    "validate_elevation_consistency",
    "validate_biome_distribution",
    "validate_river_continuity",
    "validation_bp",
    "validate_world_cli",
    "property_test_world_cli"
] 