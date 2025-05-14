# TypeScript to Python Conversion for Steam

This demonstration shows the conversion of TypeScript code to Python, which is useful for deploying games and applications on Steam.

## Conversion System Components

The conversion system consists of three main scripts:

1. **ts2py.py** - The main conversion script that transforms TypeScript syntax to Python
   - Handles classes, interfaces, and type annotations
   - Converts TypeScript types to Python type hints
   - Transforms syntax patterns to their Python equivalents
   - Basic conversion that preserves most of the structure

2. **fix_python_conversion.py** - Post-processing script to improve the converted code
   - Fixes variable naming (camelCase to snake_case)
   - Adjusts boolean values (true/false to True/False)
   - Improves string formatting
   - Adds appropriate imports and fixes import statements
   - Creates proper class docstrings

3. **convert_project.py** - Coordinator script for full project conversion
   - Creates proper package structure including __init__.py files
   - Handles file copying and directory organization
   - Manages Python requirements and dependencies
   - Creates entry points for the Python application
   - Preserves non-TypeScript assets

## Demonstration

The demo in this directory shows the successful conversion of TypeScript classes to Python:

- `HexCell.ts` → `HexCell.py`: A basic cell in a hexagonal grid system
- `RegionMap.ts` → `RegionMap.py`: A collection of cells that form a region
- `demo.py`: A script showing the converted code in action

## How to Run the Demo

```bash
python demo.py
```

The demo creates cells and regions, demonstrates their behavior, and displays their properties.

## Common Conversion Patterns

- TypeScript interfaces → Python classes or type hints
- TypeScript enums → Python Enum classes
- TypeScript classes → Python classes with type annotations
- getters/setters → Python @property decorators
- camelCase methods → snake_case methods
- TypeScript types → Python type hints
- Array<T> → List[T]
- Map<K,V> → Dict[K,V]

## Limitations and Considerations

- Some TypeScript features require manual adjustment (decorators, complex generics)
- React components need special handling (not shown in this demo)
- UI code often needs adaptation to work with Python UI frameworks
- Performance-critical code may require additional optimization
- Browser-specific APIs need to be replaced with Python equivalents

## Complete Project Conversion

To convert a complete project, use:

```bash
python convert_project.py /path/to/ts/project --output-dir /path/to/output
```

Followed by:

```bash
python fix_python_conversion.py /path/to/output
```

This creates a ready-to-use Python project that maintains the functionality of the original TypeScript code while adapting to Python's syntax and conventions. 