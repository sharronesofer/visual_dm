# Python Migration Guide

## Overview

This document provides a comprehensive guide for developers working with the Visual DM project after its migration from TypeScript to Python. The migration was completed as part of Task #676, which built on the Python-based asset management system established in Task #581.

## Migration Results

The TypeScript to Python migration process successfully converted approximately 1,550+ TypeScript files to Python code with proper type annotations. The conversion preserved the core functionality, relationships, and architecture of the codebase while adapting it to Python idioms and patterns.

## Key Components in the New Python Architecture

- **Type System**: TypeScript interfaces are now implemented as Python classes with type annotations
- **Module Structure**: Directory organization is maintained but uses Python package conventions with `__init__.py` files
- **Enums**: TypeScript enums are converted to Python's Enum class (from the enum module)
- **Model Classes**: Models maintain their structure but use Python conventions and type hints

## Development Guidelines

### Python Style and Structure

1. **PEP 8 Compliance**: Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines:
   - Use snake_case for function and variable names
   - Use CamelCase for class names
   - Maximum line length of 88 characters (we use Black as the formatter)
   - Proper docstrings for all modules, classes, and functions

2. **Imports Organization**:
   - Standard library imports first
   - Third-party library imports second
   - Local application imports third
   - Sort alphabetically within each group

3. **Type Hints**:
   - All function parameters and return values should use type annotations
   - Use the `typing` module for complex types (Dict, List, Optional, etc.)
   - For self-referential types, use string literals (e.g., `"MyClass"` instead of `MyClass`)

### Testing

1. **pytest**: All tests should be written using pytest
   - Tests should be in the `tests/` directory mirroring the module structure
   - Use fixtures for test setup
   - Use parametrization for testing multiple similar cases

2. **Type Checking**:
   - Use mypy for static type checking
   - Run `mypy --ignore-missing-imports` on your code before committing

3. **Code Quality**:
   - Use flake8 for linting
   - Use pylint for more in-depth code analysis
   - Use Black for code formatting

## Migration Differences

### Key Differences from TypeScript

1. **Duck Typing vs. Static Typing**:
   - Python is duck-typed, so some explicit type checking that was done in TypeScript may not be necessary
   - However, we use type hints throughout the codebase to maintain similar benefits of static typing

2. **Property Access**:
   - Python does not have native property access syntax like TypeScript
   - Properties are now implemented using @property decorators where needed

3. **Default Parameters**:
   - Python handles default parameters differently - be aware that mutable default parameters are evaluated only once at function definition

4. **Optional Types**:
   - In TypeScript: `parameter?: string` or `parameter: string | undefined`
   - In Python: `parameter: Optional[str] = None`

5. **Classes vs Interfaces**:
   - TypeScript interfaces are now Python classes with attribute type annotations
   - Implementation inheritance replaces interface implementation

## Converting Additional Code

If you need to convert more TypeScript files to Python, use the provided tools:

1. **Automatic Conversion**:
   ```bash
   python scripts/ts2py.py --input <typescript_file> --output <python_file>
   ```

2. **Post-Processing Fixes**:
   ```bash
   python scripts/fix_py_conversions.py --dir <directory_with_python_files>
   ```

3. **Integration with Existing Code**:
   ```bash
   python scripts/integrate_py_modules.py --source-dir <converted_files> --target-dir <backend_directory>
   ```

4. **Testing Converted Modules**:
   ```bash
   python scripts/test_converted_modules.py --modules-dir <modules_directory>
   ```

## Common Migration Challenges

1. **Import Resolution**: If modules cannot be found, verify that:
   - All necessary `__init__.py` files are in place
   - The import path is correctly adapted for Python
   - The module hierarchy matches the directory structure

2. **Type Compatibility**: Type errors usually arise from:
   - Missing or incorrect type annotations
   - Using `None` where an actual value is expected
   - Using a specific type where Union is required

3. **Class Structure**: When classes don't behave as expected:
   - Verify that class attributes have correct type annotations
   - Check that class methods include `self` parameter
   - Ensure constructors are properly converted to `__init__` methods

4. **Module Organization**: If module organization is confusing:
   - Python uses `__init__.py` files to define packages
   - Use relative imports (`.module`) for closely related modules
   - Use absolute imports for modules in different packages

## Example: TypeScript to Python Conversion

### TypeScript (Before):

```typescript
export interface Building {
  id: string;
  name: string;
  floors: number;
  isActive?: boolean;
}

export enum BuildingType {
  RESIDENTIAL = 'residential',
  COMMERCIAL = 'commercial',
  INDUSTRIAL = 'industrial'
}

export class BuildingManager {
  private buildings: Building[] = [];

  constructor() {}

  addBuilding(building: Building): void {
    this.buildings.push(building);
  }

  getBuilding(id: string): Building | undefined {
    return this.buildings.find(b => b.id === id);
  }
}
```

### Python (After):

```python
from typing import List, Optional
from enum import Enum

class Building:
    id: str
    name: str
    floors: int
    isActive: Optional[bool] = None

class BuildingType(Enum):
    RESIDENTIAL = 'residential'
    COMMERCIAL = 'commercial'
    INDUSTRIAL = 'industrial'

class BuildingManager:
    def __init__(self):
        self.buildings: List[Building] = []
    
    def add_building(self, building: Building) -> None:
        self.buildings.append(building)
    
    def get_building(self, id: str) -> Optional[Building]:
        for b in self.buildings:
            if b.id == id:
                return b
        return None
```

## Additional Resources

- [Python Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [Python Best Practices](https://docs.python-guide.org/)
- [Type Checking in Python](https://realpython.com/python-type-checking/)
- [Python Documentation](https://docs.python.org/3/)
- [Internal Project Documentation](./typescript_to_python_migration_plan.md)
- [Migration Report](./migration/typescript_to_python_migration_summary.md)

## Contact

For questions about the migration or Python implementation, please contact the backend team or refer to the migration documentation in the `docs/migration/` directory. 