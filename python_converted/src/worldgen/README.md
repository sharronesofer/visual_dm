# World Generation System (Python)

This directory contains the Python implementation of the Visual DM World Generation System, converted from the original TypeScript implementation.

## Overview

The World Generation System provides a deterministic and extensible framework for creating procedural game worlds with consistent results. It includes:

- Core infrastructure for deterministic random generation
- Procedural and template-based region generators
- Validation systems for ensuring coherent regions
- Pipeline architecture for flexible generation processes

## Migration Details

This code was migrated from TypeScript to Python as part of the transition to a computer-local distribution via platforms like Steam. The migration involved:

1. Converting TypeScript interfaces to Python abstract base classes and Protocol classes
2. Converting TypeScript-specific constructs to Python equivalents
3. Implementing proper Python module structure with `__init__.py` files
4. Adapting to Python's type hinting system

### Implementation Notes

- TypeScript interfaces were converted to either Abstract Base Classes (ABC) or Protocol classes
- TypeScript enums were converted to Python Enum classes
- camelCase methods were converted to snake_case to follow Python conventions
- JavaScript array methods (map, filter, etc.) were converted to Python list comprehensions
- TypeScript-specific type annotations were converted to Python type hints

## Directory Structure

```
worldgen/
├── __init__.py                 # Main module exports
├── core/                       # Core components
│   ├── __init__.py
│   ├── DeterministicRNG.py     # Random number generator
│   ├── GenerationPipeline.py   # Pipeline architecture
│   ├── GeneratorRegistry.py    # Registry for generators
│   └── IWorldGenerator.py      # Core interfaces and types
├── region/                     # Region generators
│   ├── __init__.py
│   ├── BaseRegionGenerator.py
│   ├── HandcraftedRegionGenerator.py
│   ├── ProceduralRegionGenerator.py
│   ├── RegionGeneratorFactory.py
│   └── RegionGeneratorInterfaces.py
└── validation/                 # Validation components
    ├── __init__.py
    ├── RegionValidationRules.py
    └── RegionValidator.py
```

## Usage

The World Generation System can be used as follows:

```python
from worldgen import (
    DeterministicRNG, 
    GeneratorRegistry, 
    RegionGeneratorFactory, 
    RegionGeneratorOptions
)

# Create a random number generator with a seed
rng = DeterministicRNG(seed=12345)

# Create a registry and factory
registry = GeneratorRegistry()
factory = RegionGeneratorFactory(registry)

# Register built-in generators
factory.register_default_generators()

# Generate a procedural region
options = RegionGeneratorOptions(
    width=64,
    height=64,
    seed=12345,
    region_type="forest",
    terrain_complexity=0.7
)

# Get a procedural generator and generate a region
generator = registry.get_generator("procedural")
result = generator.generate(options)

if result.success:
    region = result.region
    print(f"Generated region '{region.name}' with {len(region.cells)} cells")
else:
    print(f"Generation failed: {result.error}")
```

## Deterministic Generation

A key feature of the system is its deterministic generation - the same seed will always produce the same results, ensuring consistent world generation across runs and platforms.

The main source of randomness is the `DeterministicRNG` class, which implements a custom random number generator with the ability to create child generators with derived seeds.

## Further Development

Future development plans include:

1. Adding more region types and biomes
2. Implementing more sophisticated terrain generation algorithms
3. Adding support for multi-region world generation
4. Improving performance with Numpy and optimized algorithms

## License

This code is part of the Visual DM project and is subject to the same licensing terms. 