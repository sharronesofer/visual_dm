# Python Templates for TypeScript Migration

This directory contains template files to use during and after the TypeScript to Python migration process. These templates ensure consistency in the converted codebase and help developers maintain Python best practices.

## Available Templates

### Module Template

The `module_template.py` file demonstrates:

- Proper module structure and organization
- Python class implementation with type annotations
- Enum implementation
- Property usage with getters and setters
- Dataclass usage for simple data structures
- Function implementation with proper annotations
- Documentation using docstrings

Use this template when creating new Python modules or as a reference when converting TypeScript files to ensure adherence to the project's Python coding standards.

### Unit Test Template

The `test_template.py` file demonstrates:

- pytest structure and organization
- Testing classes and methods
- Using fixtures for test data
- Testing with type annotations
- Patterns for testing common migration scenarios

Use this template when creating tests for your converted Python modules.

## Usage

1. Copy the appropriate template file to your target location
2. Rename the file and update its contents to match your specific module
3. Ensure you follow the structure and patterns demonstrated in the template
4. Add proper docstrings and type annotations
5. Remove any example code that doesn't apply to your module

## Best Practices

When using these templates, remember:

1. Always include proper docstrings for modules, classes, methods, and functions
2. Use type annotations for all parameters and return values
3. Follow PEP 8 style guidelines
4. Organize imports according to the project standards
5. Use dataclasses for simple data structures when appropriate
6. Implement properties using decorators rather than getter/setter methods
7. Write comprehensive unit tests for all functionality

The templates are designed to demonstrate these best practices in context. 