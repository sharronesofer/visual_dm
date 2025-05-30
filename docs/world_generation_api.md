# World Generation API Documentation

## Overview

The Visual DM World Generation API provides a clean, simple interface for creating procedurally generated worlds. This API is designed to hide the complexity of the underlying implementation while still providing powerful customization options.

The API allows you to:

- Generate worlds with sensible default settings
- Customize every aspect of world generation
- Generate worlds asynchronously
- Save and load worlds to/from files
- Subscribe to world generation events
- Analyze world data

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [API Reference](#api-reference)
  - [World Generation](#world-generation)
  - [World Management](#world-management)
  - [Event System](#event-system)
  - [Analysis](#analysis)
- [Data Structures](#data-structures)
- [Default Settings](#default-settings)
- [Examples](#examples)

## Installation

The World Generation API is part of the Visual DM package. No additional installation is required if you're already using Visual DM.

## Basic Usage

Here's a simple example of generating a world and saving it to a file:

```python
from backend.systems.world_generation.api import generate_world, save_world

# Generate a world with default settings
world = generate_world(seed=12345)

# Save the world to a file
save_world(world, "my_world.json")
```

For more advanced usage, you can customize world generation settings:

```python
from backend.systems.world_generation.api import generate_custom_world

# Generate a custom world
world = generate_custom_world(
    seed=67890,
    size="large",
    elevation_settings={
        "mountain_density": 0.7,
        "smoothing_iterations": 4
    },
    river_settings={
        "num_rivers": 5,
        "max_river_length": 100
    }
)
```

## API Reference

### World Generation

#### `generate_world(seed=None, size="medium", regions=1, name="Generated World")`

Generates a world with default settings.

**Parameters:**

- `seed` (int, optional): Random seed for world generation. If None, a random seed is used.
- `size` (str or int): World size, either a string ("tiny", "small", "medium", "large", "huge") or an integer representing the size in tiles.
- `regions` (int): Number of regions to generate.
- `name` (str): Name for the generated world.

**Returns:**

- A dictionary containing the generated world data.

**Example:**

```python
# Generate a medium-sized world with a specific seed
world = generate_world(seed=12345)

# Generate a large world with a random seed
world = generate_world(size="large")

# Generate a world with a specific size in tiles
world = generate_world(size=400)
```

#### `generate_world_async(seed=None, size="medium", regions=1, name="Generated World")`

Asynchronous version of `generate_world()`, with the same parameters and defaults.

**Example:**

```python
import asyncio
from backend.systems.world_generation.api import generate_world_async

async def generate():
    world = await generate_world_async(seed=12345)
    return world
    
world = asyncio.run(generate())
```

#### `generate_custom_world(...)`

Generates a world with custom settings.

**Parameters:**

- `seed` (int, optional): Random seed for world generation.
- `size` (str or int): World size.
- `regions` (int): Number of regions to generate.
- `name` (str): Name for the generated world.
- `elevation_settings` (dict, optional): Dictionary of elevation generation settings.
- `biome_settings` (dict, optional): Dictionary of biome placement settings.
- `river_settings` (dict, optional): Dictionary of river generation settings.
- `resource_settings` (dict, optional): Dictionary of resource distribution settings.
- `climate_settings` (dict, optional): Dictionary of climate system settings.
- `adjacency_rules` (dict, optional): Dictionary of biome adjacency rules.
- `region_layout` (str): Layout algorithm for multiple regions ("linear", "grid", "spiral").

**Returns:**

- A dictionary containing the generated world data.

**Example:**

```python
# Generate a world with custom river settings
world = generate_custom_world(
    seed=12345,
    river_settings={
        "num_rivers": 10,
        "max_river_length": 100,
        "tributary_chance": 0.5
    }
)
```

#### `generate_custom_world_async(...)`

Asynchronous version of `generate_custom_world()`, with the same parameters and options.

### World Management

#### `save_world(world_data, path)`

Saves a world to a file.

**Parameters:**

- `world_data` (dict): World data to save.
- `path` (str): Path where to save the world.

**Returns:**

- Boolean indicating success (True) or failure (False).

**Example:**

```python
# Generate and save a world
world = generate_world(seed=12345)
save_world(world, "my_world.json")
```

#### `load_world(path)`

Loads a world from a file.

**Parameters:**

- `path` (str): Path to the world file (JSON format).

**Returns:**

- The loaded world data as a dictionary.

**Example:**

```python
# Load a world from a file
world = load_world("my_world.json")
```

### Event System

#### `subscribe_to_world_events(event_type, handler)`

Subscribes to world generation events.

**Parameters:**

- `event_type` (str or WorldGenerationEventType): Type of events to subscribe to.
- `handler` (function): Function to call when an event of this type occurs.

**Example:**

```python
from backend.systems.world_generation.events import WorldGenerationEventType

# Subscribe to generation completed events
def on_generation_completed(event):
    print(f"World generation completed in {event.elapsed_time} seconds")
    
subscribe_to_world_events(
    WorldGenerationEventType.GENERATION_COMPLETED, 
    on_generation_completed
)
```

Available event types:

- `GENERATION_STARTED`: Emitted when world generation begins
- `GENERATION_COMPLETED`: Emitted when world generation completes successfully
- `GENERATION_FAILED`: Emitted when world generation fails
- `GENERATION_PROGRESS`: Emitted to indicate generation progress
- `PHASE_STARTED`: Emitted when a generation phase starts
- `PHASE_COMPLETED`: Emitted when a generation phase completes
- `PHASE_FAILED`: Emitted when a generation phase fails
- `COMPONENT_STARTED`: Emitted when a generation component starts
- `COMPONENT_COMPLETED`: Emitted when a generation component completes
- `COMPONENT_FAILED`: Emitted when a generation component fails
- `WORLD_SAVED`: Emitted when a generated world is saved
- `WORLD_LOADED`: Emitted when a world is loaded

### Analysis

#### `get_world_info(world_data)`

Gets summary information about a world.

**Parameters:**

- `world_data` (dict): World data.

**Returns:**

- Dictionary with summary information about the world.

**Example:**

```python
# Get information about a world
world = load_world("my_world.json")
info = get_world_info(world)
print(f"World name: {info['name']}")
print(f"Number of regions: {info['regions']}")
```

The returned dictionary includes:

- Basic metadata: name, seed, version, author, creation date, description
- Region count
- Tile counts: total, land, water, rivers
- Land percentage
- Biome distribution
- Resource distribution

## Data Structures

### World Data

The world data dictionary contains:

- `metadata`: General world information
  - `name`: World name
  - `seed`: Generation seed
  - `version`: Data format version
  - `author`: Creator name
  - `creation_date`: When the world was created
  - `description`: World description
- `regions`: Dictionary of regions
  - Key: Region ID (e.g., "0_0")
  - Value: Region data
    - `coordinates`: Region position
    - `size`: Region size in tiles
    - `tiles`: Dictionary of tiles
      - Key: Tile ID (e.g., "5_10")
      - Value: Tile data
        - `biome`: Biome type
        - `elevation`: Elevation value
        - `coordinates`: Tile position
        - `temperature`: Temperature value
        - `humidity`: Humidity value
        - `resources`: List of resources
- `settings`: Generation settings

### Tile Data

Each tile has the following data:

- `biome`: Biome type (string, e.g., "forest", "mountain", "ocean")
- `elevation`: Height value (0-10, where 0 is ocean level)
- `coordinates`: Position in the region (x, y)
- `walkable`: Whether the tile can be traversed
- `temperature`: Temperature value
- `humidity`: Humidity value
- `resources`: List of resources on this tile

## Default Settings

The API uses sensible defaults for world generation:

### World Sizes

- `tiny`: 128×128 tiles
- `small`: 256×256 tiles
- `medium`: 512×512 tiles (default)
- `large`: 1024×1024 tiles
- `huge`: 2048×2048 tiles

### Default Generation Settings

```python
DEFAULT_SETTINGS = {
    "elevation_settings": {
        "mountain_density": 0.3,
        "hill_density": 0.5,
        "plain_density": 0.7,
        "smoothing_iterations": 3,
        "ocean_percentage": 0.6
    },
    "biome_settings": {
        "use_temperature": True,
        "use_humidity": True,
        "transition_chance": 0.3
    },
    "river_settings": {
        "num_rivers": 3,
        "max_river_length": 75,
        "tributary_chance": 0.3,
        "meander_factor": 0.4
    },
    "resource_settings": {
        "resource_density": 0.5,
        "resource_clustering": 0.7,
        "rare_resource_chance": 0.1
    },
    "climate_settings": {
        "temperature_noise_scale": 0.1,
        "humidity_noise_scale": 0.15,
        "elevation_temperature_factor": 0.7
    }
}
```

## Examples

For complete examples of using the World Generation API, see the [examples/world_generation_example.py](../examples/world_generation_example.py) file.

Here are some additional examples:

### Listening to Generation Progress

```python
from backend.systems.world_generation.api import generate_world_async, subscribe_to_world_events
from backend.systems.world_generation.events import WorldGenerationEventType
import asyncio

# Progress update handler
def on_progress(event):
    print(f"Progress: {event.progress * 100:.1f}% - Phase: {event.current_phase}")

# Subscribe to progress events
subscribe_to_world_events(WorldGenerationEventType.GENERATION_PROGRESS, on_progress)

# Generate world asynchronously
async def generate():
    world = await generate_world_async(seed=12345)
    return world

# Run generation
world = asyncio.run(generate())
```

### Creating a Desert World

```python
from backend.systems.world_generation.api import generate_custom_world

# Create a desert world
desert_world = generate_custom_world(
    seed=42,
    name="Desert World",
    climate_settings={
        "temperature_noise_scale": 0.05,  # More uniform temperature
        "base_temperature": 0.8,  # Very hot
        "humidity_noise_scale": 0.1,
        "base_humidity": 0.1  # Very dry
    },
    biome_settings={
        "desert_chance": 0.8,  # High chance of desert
        "use_temperature": True,
        "use_humidity": True
    },
    river_settings={
        "num_rivers": 1,  # Few rivers
        "tributary_chance": 0.1  # Few tributaries
    }
)
```

### Creating an Archipelago

```python
from backend.systems.world_generation.api import generate_custom_world

# Create an archipelago world
archipelago_world = generate_custom_world(
    seed=789,
    name="Archipelago",
    elevation_settings={
        "ocean_percentage": 0.85,  # Mostly ocean
        "mountain_density": 0.7,   # Islands tend to be mountainous
        "noise_scale": 0.05,       # More fragmented landmasses
        "island_factor": 0.8       # Preference for islands
    }
)
``` 