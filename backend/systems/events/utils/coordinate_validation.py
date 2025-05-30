"""
Coordinate Validation System

Provides runtime validation for enforcing coordinate system standards.
This helps catch convention violations during development and prevent precision issues.
"""

import logging
import inspect
import functools
import traceback
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, cast
from .coordinates import GlobalCoord, LocalCoord, CoordinateSystem, coordinate_system
from .floating_origin import FloatingOrigin, floating_origin
from . import coordinate_utils as cu

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')
CoordType = Union[GlobalCoord, LocalCoord]
ValidationFunction = Callable[[Any], bool]
ValidationError = Tuple[str, Any]  # (message, value)

# Constants
MAX_ERRORS_LOGGED = 100  # Prevent log flooding
DEFAULT_VALIDATION_CONFIG = {
    "strict_mode": False,  # When True, raises exceptions instead of just logging
    "validate_parameters": True,  # Validate function parameters
    "validate_return_values": True,  # Validate function return values
    "check_for_direct_tuples": True,  # Check for raw tuples used instead of coord objects
    "max_distance_warning": 10000.0,  # Warning threshold for large coordinate values
    "enabled": True,  # Master switch to enable/disable all validation
}

# Global state
_error_count = 0
_validation_config = DEFAULT_VALIDATION_CONFIG.copy()
_registered_validators: Dict[Type, List[ValidationFunction]] = {}
_validation_stats: Dict[str, int] = {
    "total_checks": 0,
    "failed_checks": 0,
    "parameter_errors": 0,
    "return_value_errors": 0,
    "large_coord_warnings": 0,
    "tuple_usage_warnings": 0,
}

def configure_validation(config_updates: Dict[str, Any]) -> None:
    """
    Update the validation configuration.
    
    Args:
        config_updates: Dictionary of configuration values to update
    """
    global _validation_config
    _validation_config.update(config_updates)
    logger.info(f"Coordinate validation configuration updated: {_validation_config}")

def register_validator(target_type: Type[T], validator_func: ValidationFunction) -> None:
    """
    Register a validation function for a specific type.
    
    Args:
        target_type: The type to validate
        validator_func: Function that returns True if valid, False otherwise
    """
    if target_type not in _registered_validators:
        _registered_validators[target_type] = []
    
    _registered_validators[target_type].append(validator_func)
    logger.debug(f"Registered validator for {target_type.__name__}")

def validate_value(value: Any) -> List[ValidationError]:
    """
    Validate a value against registered validators.
    
    Args:
        value: The value to validate
        
    Returns:
        List of validation errors, empty if valid
    """
    global _validation_stats
    
    if not _validation_config["enabled"]:
        return []
    
    _validation_stats["total_checks"] += 1
    errors: List[ValidationError] = []
    
    # Handle None values
    if value is None:
        return []
    
    value_type = type(value)
    
    # Check for coordinate-like tuples that should be GlobalCoord/LocalCoord
    if _validation_config["check_for_direct_tuples"] and isinstance(value, tuple) and len(value) in (2, 3):
        if all(isinstance(x, (int, float)) for x in value):
            errors.append(("Tuple used where coordinate object expected", value))
            _validation_stats["tuple_usage_warnings"] += 1
    
    # Apply specific type validators
    if value_type in _registered_validators:
        for validator in _registered_validators[value_type]:
            try:
                if not validator(value):
                    errors.append((f"Failed validation with {validator.__name__}", value))
                    _validation_stats["failed_checks"] += 1
            except Exception as e:
                errors.append((f"Validator error: {str(e)}", value))
                _validation_stats["failed_checks"] += 1
    
    # Special handling for coordinate types
    if isinstance(value, (GlobalCoord, LocalCoord)):
        # Check for excessively large coordinates
        if abs(value.x) > _validation_config["max_distance_warning"] or \
           abs(value.y) > _validation_config["max_distance_warning"] or \
           abs(value.z) > _validation_config["max_distance_warning"]:
            errors.append((f"Coordinate value exceeds safe threshold: {value}", value))
            _validation_stats["large_coord_warnings"] += 1
    
    return errors

def validate_function_call(func: Callable) -> Callable:
    """
    Decorator to validate function parameters and return values.
    
    Args:
        func: The function to wrap with validation
        
    Returns:
        Wrapped function with validation
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not _validation_config["enabled"]:
            return func(*args, **kwargs)
        
        # Validate parameters
        if _validation_config["validate_parameters"]:
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            for param_name, param_value in bound_args.arguments.items():
                errors = validate_value(param_value)
                if errors:
                    handle_validation_errors(
                        f"Parameter '{param_name}' in {func.__qualname__}",
                        errors
                    )
                    _validation_stats["parameter_errors"] += 1
        
        # Call the original function
        result = func(*args, **kwargs)
        
        # Validate return value
        if _validation_config["validate_return_values"]:
            errors = validate_value(result)
            if errors:
                handle_validation_errors(
                    f"Return value from {func.__qualname__}",
                    errors
                )
                _validation_stats["return_value_errors"] += 1
        
        return result
    
    return wrapper

def validate_coord_type(coord_type: Type[CoordType]) -> Callable:
    """
    Decorator to validate a function returns the specified coordinate type.
    
    Args:
        coord_type: Expected coordinate type (GlobalCoord or LocalCoord)
        
    Returns:
        Function decorator that validates return type
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            if not _validation_config["enabled"] or not _validation_config["validate_return_values"]:
                return result
            
            if not isinstance(result, coord_type):
                error_msg = f"Function {func.__qualname__} should return {coord_type.__name__}, but returned {type(result).__name__}"
                handle_validation_error(error_msg, result)
                _validation_stats["return_value_errors"] += 1
            
            return result
        
        return wrapper
    
    return decorator

def handle_validation_errors(context: str, errors: List[ValidationError]) -> None:
    """
    Handle a list of validation errors based on configuration.
    
    Args:
        context: Context where the errors occurred
        errors: List of validation errors
    """
    global _error_count
    
    for message, value in errors:
        handle_validation_error(f"{context}: {message}", value)

def handle_validation_error(message: str, value: Any) -> None:
    """
    Handle a single validation error based on configuration.
    
    Args:
        message: Error message
        value: The value that failed validation
    """
    global _error_count
    
    if _error_count >= MAX_ERRORS_LOGGED:
        return
    
    _error_count += 1
    stack_trace = "".join(traceback.format_stack()[:-2])
    
    if _validation_config["strict_mode"]:
        raise ValueError(f"Coordinate validation error: {message}\nValue: {value}\n{stack_trace}")
    else:
        logger.warning(f"Coordinate validation warning: {message}\nValue: {value}\nStack trace:\n{stack_trace}")

def get_validation_stats() -> Dict[str, int]:
    """
    Get statistics about validation errors.
    
    Returns:
        Dictionary of validation statistics
    """
    return _validation_stats.copy()

def reset_validation_stats() -> None:
    """Reset all validation statistics to zero."""
    global _validation_stats, _error_count
    
    for key in _validation_stats:
        _validation_stats[key] = 0
    
    _error_count = 0

# Register default validators
def _is_valid_global_coord(coord: GlobalCoord) -> bool:
    """Check if a GlobalCoord is valid."""
    return not (
        coord is None or
        not hasattr(coord, 'x') or
        not hasattr(coord, 'y') or
        not hasattr(coord, 'z') or
        not all(isinstance(v, (int, float)) for v in (coord.x, coord.y, coord.z))
    )

def _is_valid_local_coord(coord: LocalCoord) -> bool:
    """Check if a LocalCoord is valid."""
    return not (
        coord is None or
        not hasattr(coord, 'x') or
        not hasattr(coord, 'y') or
        not hasattr(coord, 'z') or
        not all(isinstance(v, (int, float)) for v in (coord.x, coord.y, coord.z))
    )

# Register built-in validators
register_validator(GlobalCoord, _is_valid_global_coord)
register_validator(LocalCoord, _is_valid_local_coord) 