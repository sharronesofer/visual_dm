"""
World Validation API Interface.

This module provides API interfaces for interacting with the world validation system,
allowing external systems to validate worlds and view validation reports.
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from pathlib import Path

from flask import Blueprint, jsonify, request, current_app
from app.core.models.world import World
from app.core.persistence.world_persistence import WorldPersistenceManager, FileSystemStorageStrategy
from .world_validation import WorldValidator, ValidationResult
from .property_testing import PropertyBasedTesting, PropertyTestResult

logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__, url_prefix='/api/validation')

# Shared validator instance
_validator = None

def get_validator():
    """Get or create a shared validator instance."""
    global _validator
    if _validator is None:
        storage_root = current_app.config.get('WORLD_STORAGE_ROOT', 'data/worlds')
        storage = FileSystemStorageStrategy(storage_root)
        persistence_manager = WorldPersistenceManager(storage)
        _validator = WorldValidator(persistence_manager)
    return _validator

@validation_bp.route('/worlds/<world_id>/validate', methods=['POST'])
def validate_world(world_id):
    """
    Validate a world.
    
    Args:
        world_id: ID of the world to validate
        
    Returns:
        JSON response with validation results
    """
    try:
        # Get validation rules from request
        data = request.get_json() or {}
        rules = data.get('rules')  # Optional list of rule IDs
        
        # Get validator
        validator = get_validator()
        persistence_manager = validator.persistence_manager
        
        # Load the world
        world_dict = persistence_manager.load_world(world_id)
        if not world_dict:
            return jsonify({"error": f"World {world_id} not found"}), 404
        
        world = World.from_dict(world_dict)
        
        # Validate the world
        validation_report = validator.get_validation_report(world, rules)
        
        return jsonify(validation_report)
    
    except Exception as e:
        logger.error(f"Error validating world {world_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@validation_bp.route('/worlds/<world_id>/validate/quick', methods=['GET'])
def quick_validate_world(world_id):
    """
    Perform a quick validation check on a world.
    
    Args:
        world_id: ID of the world to validate
        
    Returns:
        JSON response with simple validation status
    """
    try:
        # Get validator
        validator = get_validator()
        persistence_manager = validator.persistence_manager
        
        # Load the world
        world_dict = persistence_manager.load_world(world_id)
        if not world_dict:
            return jsonify({"error": f"World {world_id} not found"}), 404
        
        world = World.from_dict(world_dict)
        
        # Validate the world
        is_valid = validator.is_world_valid(world)
        
        return jsonify({
            "world_id": world_id,
            "is_valid": is_valid,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error validating world {world_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@validation_bp.route('/worlds/<world_id>/property-test', methods=['POST'])
def property_test_world(world_id):
    """
    Run property-based tests on a world.
    
    Args:
        world_id: ID of the world to test
        
    Returns:
        JSON response with property test results
    """
    try:
        # Get property names from request
        data = request.get_json() or {}
        property_names = data.get('properties')  # Optional list of property names
        
        # Get validator
        validator = get_validator()
        persistence_manager = validator.persistence_manager
        
        # Load the world
        world_dict = persistence_manager.load_world(world_id)
        if not world_dict:
            return jsonify({"error": f"World {world_id} not found"}), 404
        
        world = World.from_dict(world_dict)
        
        # Create property tester
        property_tester = PropertyBasedTesting()
        
        # Run property tests
        test_report = property_tester.get_property_test_report(world)
        
        return jsonify(test_report)
    
    except Exception as e:
        logger.error(f"Error property testing world {world_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@validation_bp.route('/rules', methods=['GET'])
def get_validation_rules():
    """
    Get a list of available validation rules.
    
    Returns:
        JSON response with validation rules
    """
    try:
        # Get validator
        validator = get_validator()
        
        # Get rules
        rules = [
            {
                "id": rule["id"],
                "description": rule["description"]
            }
            for rule in validator.validation_rules
        ]
        
        return jsonify(rules)
    
    except Exception as e:
        logger.error(f"Error getting validation rules: {str(e)}")
        return jsonify({"error": str(e)}), 500

@validation_bp.route('/properties', methods=['GET'])
def get_properties():
    """
    Get a list of available world properties for testing.
    
    Returns:
        JSON response with world properties
    """
    try:
        # Create property tester
        property_tester = PropertyBasedTesting()
        
        # Get properties
        properties = [
            {
                "name": prop.name,
                "description": prop.description
            }
            for prop in property_tester.properties
        ]
        
        return jsonify(properties)
    
    except Exception as e:
        logger.error(f"Error getting world properties: {str(e)}")
        return jsonify({"error": str(e)}), 500

@validation_bp.route('/batch-validate', methods=['POST'])
def batch_validate():
    """
    Validate multiple worlds at once.
    
    Returns:
        JSON response with validation results for each world
    """
    try:
        # Get world IDs from request
        data = request.get_json() or {}
        world_ids = data.get('world_ids', [])
        rules = data.get('rules')  # Optional list of rule IDs
        
        if not world_ids:
            return jsonify({"error": "No world IDs provided"}), 400
        
        # Get validator
        validator = get_validator()
        persistence_manager = validator.persistence_manager
        
        # Validate each world
        results = {}
        for world_id in world_ids:
            try:
                # Load the world
                world_dict = persistence_manager.load_world(world_id)
                if not world_dict:
                    results[world_id] = {"error": f"World {world_id} not found"}
                    continue
                
                world = World.from_dict(world_dict)
                
                # Validate the world
                validation_report = validator.get_validation_report(world, rules)
                results[world_id] = validation_report
                
            except Exception as e:
                logger.error(f"Error validating world {world_id}: {str(e)}")
                results[world_id] = {"error": str(e)}
        
        return jsonify({
            "batch_results": results,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in batch validation: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Helper functions for CLI and programmatic access

def validate_world_cli(world_id: str, rules: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate a world (CLI interface).
    
    Args:
        world_id: ID of the world to validate
        rules: Optional list of rule IDs to apply
        
    Returns:
        Validation report
    """
    try:
        # Create validator with default storage
        storage = FileSystemStorageStrategy('data/worlds')
        persistence_manager = WorldPersistenceManager(storage)
        validator = WorldValidator(persistence_manager)
        
        # Load the world
        world_dict = persistence_manager.load_world(world_id)
        if not world_dict:
            return {"error": f"World {world_id} not found"}
        
        world = World.from_dict(world_dict)
        
        # Validate the world
        validation_report = validator.get_validation_report(world, rules)
        
        return validation_report
    
    except Exception as e:
        logger.error(f"Error validating world {world_id}: {str(e)}")
        return {"error": str(e)}

def property_test_world_cli(world_id: str, properties: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run property-based tests on a world (CLI interface).
    
    Args:
        world_id: ID of the world to test
        properties: Optional list of property names to check
        
    Returns:
        Property test report
    """
    try:
        # Create validator with default storage
        storage = FileSystemStorageStrategy('data/worlds')
        persistence_manager = WorldPersistenceManager(storage)
        
        # Load the world
        world_dict = persistence_manager.load_world(world_id)
        if not world_dict:
            return {"error": f"World {world_id} not found"}
        
        world = World.from_dict(world_dict)
        
        # Create property tester
        property_tester = PropertyBasedTesting()
        
        # Run property tests
        test_report = property_tester.get_property_test_report(world)
        
        return test_report
    
    except Exception as e:
        logger.error(f"Error property testing world {world_id}: {str(e)}")
        return {"error": str(e)} 