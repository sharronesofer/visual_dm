# Coordinate Validation Guide

This guide explains how to use the coordinate validation tools and comply with the coordinate system standards in the Visual DM project.

## Table of Contents

1. [Introduction](#introduction)
2. [The Coordinate System Standards](#the-coordinate-system-standards)
3. [Runtime Validation Tools](#runtime-validation-tools)
4. [Static Analysis Tools](#static-analysis-tools)
5. [CI/CD Integration](#cicd-integration)
6. [Common Patterns and Best Practices](#common-patterns-and-best-practices)
7. [Troubleshooting](#troubleshooting)

## Introduction

The Visual DM project uses a standardized coordinate system to ensure consistency across all game systems and prevent floating-point precision issues in large-scale world environments. This system includes:

- Two coordinate types: `GlobalCoord` and `LocalCoord`
- A floating origin system to maintain numerical precision
- Utilities for coordinate transformations and operations
- Validation tools to enforce these standards

This guide will help you understand the tools available for validating coordinate usage and how to comply with the project's coordinate standards.

## The Coordinate System Standards

### Key Classes

- **GlobalCoord**: Represents absolute positions in the world. These can grow large as the world expands.
- **LocalCoord**: Represents positions relative to the current origin. These remain small to maintain precision.
- **CoordinateSystem**: Manages conversions between global and local coordinates.
- **FloatingOrigin**: Manages entity registration and origin shifts to maintain precision.

### Key Guidelines

1. **Always use the appropriate coordinate type**:
   - Use `GlobalCoord` for world positions
   - Use `LocalCoord` for positions relative to the current origin

2. **Use the coordinate_utils module for operations**:
   - Avoid raw tuples for positions, use proper coordinate objects
   - Use the utility functions for vector operations (add, subtract, lerp, etc.)
   - Use the provided conversion functions instead of manual conversions

3. **Be aware of precision limits**:
   - Avoid creating coordinates with extremely large values (> 10000 by default)
   - Use the floating origin system to maintain precision in large worlds

4. **Proper function signatures**:
   - Include type hints for coordinate parameters and return values
   - Follow naming conventions that indicate the coordinate type being returned

## Runtime Validation Tools

The `coordinate_validation` module provides runtime validation to catch coordinate system violations during development.

### Basic Usage

```python
from visual_client.core.utils import coordinate_validation as cv

# Configure validation (optional, uses defaults if not called)
cv.configure_validation({
    "strict_mode": False,        # When True, raises exceptions instead of logging warnings
    "validate_parameters": True, # Validate function parameters 
    "validate_return_values": True, # Validate function return values
    "check_for_direct_tuples": True, # Check for raw tuples instead of coord objects
    "max_distance_warning": 10000.0, # Warning threshold for large coordinates
    "enabled": True,             # Master switch to enable/disable validation
})

# Validate a single value
errors = cv.validate_value(my_coordinate)
if errors:
    print(f"Validation errors: {errors}")

# Decorate functions to validate parameters and return values
@cv.validate_function_call
def my_function(pos: GlobalCoord, value: float) -> GlobalCoord:
    # Function implementation...
    return result_coord

# Validate specific return type
@cv.validate_coord_type(GlobalCoord)
def get_world_position() -> GlobalCoord:
    # Function implementation...
    return world_pos

# Get validation statistics
stats = cv.get_validation_stats()
print(f"Validation stats: {stats}")
```

### Key Decorators

- `@validate_function_call`: Validates all parameters and return values of a function.
- `@validate_coord_type(CoordType)`: Ensures a function returns the specified coordinate type.

### Configuration Options

The `configure_validation` function accepts a dictionary with these options:
- `strict_mode` (bool): When True, validation errors raise exceptions instead of just logging warnings.
- `validate_parameters` (bool): Whether to validate function parameters.
- `validate_return_values` (bool): Whether to validate function return values.
- `check_for_direct_tuples` (bool): Check for raw tuples used instead of coordinate objects.
- `max_distance_warning` (float): Warning threshold for large coordinate values.
- `enabled` (bool): Master switch to enable/disable validation.

## Static Analysis Tools

The project includes a static analysis tool (`scripts/coordinate_static_analysis.py`) that can detect coordinate system issues in your code without running it.

### Running the Static Analysis Tool

```bash
# Basic usage (analyze current directory)
python scripts/coordinate_static_analysis.py

# Analyze specific directories
python scripts/coordinate_static_analysis.py visual_client/core/

# Get a summary report
python scripts/coordinate_static_analysis.py --summary visual_client/

# Output results to a file
python scripts/coordinate_static_analysis.py --output=results.txt visual_client/

# Use strict mode (exit with error code on any issues)
python scripts/coordinate_static_analysis.py --strict visual_client/

# Exclude test files
python scripts/coordinate_static_analysis.py --exclude-pattern="**/test_*.py" visual_client/
```

### What It Checks

The static analysis tool checks for:

- Raw tuples used where coordinate objects should be used
- Missing type hints for coordinate-related functions
- Inconsistent naming conventions for coordinate-handling functions
- Extremely large coordinate values that might cause precision issues
- Improper use of coordinate conversion functions
- Functions returning raw tuples instead of proper coordinate objects

## CI/CD Integration

The project includes a GitHub Actions workflow (`.github/workflows/coordinate-validation.yml`) that runs the coordinate validation tools automatically.

### What the CI Workflow Does

1. **Static Analysis**:
   - Runs the static analysis tool on all Python files in the project
   - Reports issues in PR comments
   - Uploads analysis results as a build artifact

2. **Runtime Validation Tests**:
   - Runs unit tests for the coordinate validation system
   - Performs runtime validation on key modules
   - Fails the build if validation errors are found

### Viewing and Acting on CI Results

- Review PR comments to see any issues found by the static analysis tool
- Download the build artifacts for detailed analysis results
- Fix any reported issues before merging

## Common Patterns and Best Practices

### Vector Operations

```python
# ✅ DO: Use coordinate_utils for vector operations
from visual_client.core.utils import coordinate_utils as cu

# Add vectors
result_pos = cu.vec_add(position1, position2)

# Linear interpolation between positions
lerp_pos = cu.vec_lerp(start_pos, end_pos, t)

# ❌ DON'T: Perform manual vector operations
result_x = position1[0] + position2[0]
result_y = position1[1] + position2[1]
result_pos = (result_x, result_y)
```

### Coordinate Conversions

```python
# ✅ DO: Use proper conversion methods
from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord
from visual_client.core.utils import coordinate_utils as cu

# Convert between coordinate types
local_pos = coordinate_system.global_to_local(global_pos)
global_pos = coordinate_system.local_to_global(local_pos)

# Convert to/from tuples
global_pos = cu.tuple_to_global((x, y, z))
pos_tuple = cu.global_to_tuple(global_pos)

# ❌ DON'T: Perform manual conversions
global_pos = GlobalCoord(local_pos.x + origin_x, local_pos.y + origin_y, local_pos.z + origin_z)
pos_tuple = (global_pos.x, global_pos.y, global_pos.z)
```

### Type Hints and Function Signatures

```python
# ✅ DO: Include proper type hints
from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord

def get_player_position() -> GlobalCoord:
    """Return the player's current global position as a GlobalCoord object.\n\nBest practice: Always return a proper GlobalCoord, not a tuple.\nExample:\n    return player.position\n"""
    # Implementation would retrieve the player's position from the game state
    return player.position

def move_entity(entity_id: str, position: GlobalCoord) -> None:
    """Move the specified entity to the given global position.\n\nBest practice: Validate the position using coordinate_validation, update the entity's position in the world state, and trigger any necessary event hooks.\nExample:\n    errors = cv.validate_value(position)\n    if errors:\n        raise ValueError(f"Invalid position: {errors}")\n    world_state.update_entity_position(entity_id, position)\n"""
    # Implementation would update the entity's position in the world state
    pass

# ❌ DON'T: Use generic types for coordinates
def get_player_position() -> tuple:
    # TODO: Return player position as a tuple
    pass

def move_entity(entity_id: str, position) -> None:
    # TODO: Implement entity movement logic
    pass
```

### Registering with the Floating Origin System

```python
# ✅ DO: Register entities with the floating origin system
from visual_client.core.utils.floating_origin import floating_origin

class MyEntity:
    def __init__(self, entity_id, position):
        self.entity_id = entity_id
        self.position = position
        # Register with floating origin system
        floating_origin.register_entity(
            entity_id,
            self.get_position,
            self.set_position_delta
        )
    
    def get_position(self) -> GlobalCoord:
        return self.position
    
    def set_position_delta(self, dx, dy, dz) -> None:
        self.position.x += dx
        self.position.y += dy
        self.position.z += dz
```

## Troubleshooting

### Common Issues and Solutions

#### "Tuple used where coordinate object expected"

**Problem**: You're using a raw tuple instead of a `GlobalCoord` or `LocalCoord` object.

**Solution**: Use the appropriate coordinate class:
```python
# Instead of
position = (10, 20, 0)

# Use
from visual_client.core.utils.coordinates import GlobalCoord
position = GlobalCoord(10, 20, 0)
```

#### "Large coordinate value may cause precision issues"

**Problem**: You're using very large values in coordinate objects, which might cause floating-point precision issues.

**Solution**: 
- Check if your calculations are correct
- Consider using the floating origin system
- Adjust scaling if needed

#### "Function should return GlobalCoord but returns raw tuple"

**Problem**: A function is returning a tuple instead of a coordinate object.

**Solution**: Convert the result to the appropriate coordinate type:
```python
# Instead of
def get_position():
    return (x, y, z)

# Use
def get_position() -> GlobalCoord:
    return GlobalCoord(x, y, z)
```

#### Validation is too strict for a specific case

**Problem**: You have a legitimate need to use raw tuples or large coordinates in a specific case.

**Solution**: Temporarily disable validation for that specific code block:
```python
# Save current configuration
prev_config = cv._validation_config.copy()

# Disable validation for this code block
cv.configure_validation({"enabled": False})

# Your code that breaks validation rules
position = (1000000, 2000000, 0)  # Very large coordinates

# Restore previous configuration
cv.configure_validation(prev_config)
```

### Getting Help

If you encounter persistent issues with the coordinate validation system:

1. Check this guide and the API documentation
2. Look at the test files for examples of correct usage
3. Ask for help in the team's communication channels
4. File an issue in the project repository

## Conclusion

By following these guidelines and using the provided validation tools, you'll help maintain the integrity of the coordinate system across the Visual DM project. This ensures consistent behavior, prevents precision-related bugs, and makes the codebase more maintainable. 