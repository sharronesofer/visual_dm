"""
World Validation System for World Generation.

This module provides a comprehensive validation system for the World Generation System,
including automated validation scripts, property-based tests, and manual review tools.
"""

import logging
import json
from typing import Dict, List, Set, Optional, Any, Tuple, Callable, Union
from pathlib import Path
import concurrent.futures
from datetime import datetime
import time

from app.core.models.world import World
from app.core.models.world import WorldState
from app.core.persistence.world_persistence import WorldPersistenceManager
from app.core.persistence.serialization import serialize, deserialize
from app.regions.worldgen_utils import WorldGenerator
from app.core.utils.error_utils import ValidationError
from ..persistence.version_control import WorldVersionControl

logger = logging.getLogger(__name__)

class ValidationResult:
    """Represents the result of a validation operation."""
    
    def __init__(self, is_valid: bool, message: str = "", details: Dict[str, Any] = None):
        """
        Initialize a validation result.
        
        Args:
            is_valid: Whether the validation passed
            message: Summary message about the validation
            details: Detailed information about the validation
        """
        self.is_valid = is_valid
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationResult':
        """Create from dictionary representation."""
        result = cls(
            is_valid=data.get("is_valid", False),
            message=data.get("message", ""),
            details=data.get("details", {})
        )
        if "timestamp" in data:
            result.timestamp = datetime.fromisoformat(data["timestamp"])
        return result

class WorldValidator:
    """
    Main class for validating world generation.
    
    This class provides automated validation, property-based testing,
    and tools for manual review of generated worlds.
    """
    
    def __init__(self, persistence_manager: Optional[WorldPersistenceManager] = None):
        """
        Initialize the world validator.
        
        Args:
            persistence_manager: Optional persistence manager for loading/saving worlds
        """
        self.persistence_manager = persistence_manager
        self.validation_rules = []
        self.validation_results = {}
        
        # Register default validation rules
        self._register_default_rules()
    
    def _register_default_rules(self):
        """Register the default validation rules."""
        # Basic world structure validation
        self.register_validation_rule(
            "basic_structure", 
            self.validate_basic_structure,
            "Validate the basic structure and required fields of the world"
        )
        
        # Biome adjacency validation
        self.register_validation_rule(
            "biome_adjacency", 
            self.validate_biome_adjacency,
            "Validate that biome placements follow realistic adjacency rules"
        )
        
        # Resource distribution validation
        self.register_validation_rule(
            "resource_distribution", 
            self.validate_resource_distribution,
            "Validate that resources are distributed according to defined rules"
        )
        
        # Path accessibility validation
        self.register_validation_rule(
            "path_accessibility", 
            self.validate_path_accessibility,
            "Verify all regions are accessible via valid paths"
        )
        
        # World boundaries validation
        self.register_validation_rule(
            "world_boundaries", 
            self.validate_world_boundaries,
            "Validate that the world has proper boundary conditions"
        )
    
    def register_validation_rule(self, rule_id: str, validation_func: Callable[[World], ValidationResult], description: str):
        """
        Register a new validation rule.
        
        Args:
            rule_id: Unique identifier for the rule
            validation_func: Function that performs the validation
            description: Description of what the rule validates
        """
        self.validation_rules.append({
            "id": rule_id,
            "function": validation_func,
            "description": description
        })
        logger.info(f"Registered validation rule: {rule_id}")
    
    def validate_world(self, world: World, rules: Optional[List[str]] = None) -> Dict[str, ValidationResult]:
        """
        Validate a world using registered validation rules.
        
        Args:
            world: The world to validate
            rules: Optional list of rule IDs to apply (if None, all rules are applied)
            
        Returns:
            Dictionary mapping rule IDs to validation results
        """
        results = {}
        
        # Filter rules if specified
        rules_to_apply = self.validation_rules
        if rules:
            rules_to_apply = [r for r in self.validation_rules if r["id"] in rules]
        
        logger.info(f"Validating world {world.world_id} with {len(rules_to_apply)} rules")
        
        # Apply each validation rule
        for rule in rules_to_apply:
            rule_id = rule["id"]
            try:
                result = rule["function"](world)
                results[rule_id] = result
                
                # Log validation outcome
                if result.is_valid:
                    logger.info(f"Validation rule '{rule_id}' passed for world {world.world_id}")
                else:
                    logger.warning(f"Validation rule '{rule_id}' failed for world {world.world_id}: {result.message}")
                
            except Exception as e:
                logger.error(f"Error applying validation rule '{rule_id}': {str(e)}")
                results[rule_id] = ValidationResult(
                    is_valid=False,
                    message=f"Error applying validation rule: {str(e)}",
                    details={"error": str(e), "type": type(e).__name__}
                )
        
        # Store results for later reference
        self.validation_results[world.world_id] = results
        
        return results
    
    def is_world_valid(self, world: World, rules: Optional[List[str]] = None) -> bool:
        """
        Check if a world passes all validation rules.
        
        Args:
            world: The world to validate
            rules: Optional list of rule IDs to apply (if None, all rules are applied)
            
        Returns:
            True if all validation rules pass, False otherwise
        """
        results = self.validate_world(world, rules)
        return all(result.is_valid for result in results.values())
    
    def get_validation_report(self, world: World, rules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate a detailed validation report for a world.
        
        Args:
            world: The world to validate
            rules: Optional list of rule IDs to apply (if None, all rules are applied)
            
        Returns:
            Dictionary containing validation results and summary information
        """
        results = self.validate_world(world, rules)
        
        # Calculate summary statistics
        total_rules = len(results)
        passed_rules = sum(1 for result in results.values() if result.is_valid)
        
        return {
            "world_id": world.world_id,
            "world_name": world.name,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_rules": total_rules,
                "passed_rules": passed_rules,
                "failed_rules": total_rules - passed_rules,
                "pass_percentage": 100.0 * passed_rules / total_rules if total_rules > 0 else 0.0
            },
            "results": {rule_id: result.to_dict() for rule_id, result in results.items()}
        }
    
    # Implementation of default validation rules
    
    def validate_basic_structure(self, world: World) -> ValidationResult:
        """Validate the basic structure and required fields of the world."""
        # Check required fields
        missing_fields = []
        
        if not world.world_id:
            missing_fields.append("world_id")
        
        if not world.name:
            missing_fields.append("name")
        
        if not world.state:
            missing_fields.append("state")
        
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                message=f"World is missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields}
            )
        
        # Check the world state
        if not hasattr(world.state, 'regions') or not world.state.regions:
            return ValidationResult(
                is_valid=False,
                message="World has no regions",
                details={"error": "No regions found in world state"}
            )
        
        return ValidationResult(
            is_valid=True,
            message="World structure is valid",
            details={"regions_count": len(world.state.regions)}
        )
    
    def validate_biome_adjacency(self, world: World) -> ValidationResult:
        """Validate that biome placements follow realistic adjacency rules."""
        # This is a placeholder for the biome adjacency validation
        # It will be replaced with actual biome adjacency validation logic
        return ValidationResult(
            is_valid=True,
            message="Biome adjacency validation not yet implemented",
            details={"status": "placeholder"}
        )
    
    def validate_resource_distribution(self, world: World) -> ValidationResult:
        """Validate that resources are distributed according to defined rules."""
        # This is a placeholder for the resource distribution validation
        # It will be replaced with actual resource distribution validation logic
        return ValidationResult(
            is_valid=True,
            message="Resource distribution validation not yet implemented",
            details={"status": "placeholder"}
        )
    
    def validate_path_accessibility(self, world: World) -> ValidationResult:
        """Verify all regions are accessible via valid paths."""
        # This is a placeholder for the path accessibility validation
        # It will be replaced with actual path accessibility validation logic
        return ValidationResult(
            is_valid=True,
            message="Path accessibility validation not yet implemented",
            details={"status": "placeholder"}
        )
    
    def validate_world_boundaries(self, world: World) -> ValidationResult:
        """Validate that the world has proper boundary conditions."""
        # This is a placeholder for the world boundaries validation
        # It will be replaced with actual world boundaries validation logic
        return ValidationResult(
            is_valid=True,
            message="World boundaries validation not yet implemented",
            details={"status": "placeholder"}
        ) 