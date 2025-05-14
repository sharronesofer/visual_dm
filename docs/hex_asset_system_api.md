# Hex Asset Management System API Documentation

## Overview

The Hex Asset Management System provides a comprehensive solution for managing, rendering, and optimizing hex-based game assets. This document details the API for each component and provides usage examples.

## Components

### 1. HexAssetManager

Core asset management functionality for loading and organizing hex-based assets.

```python
from visual_client.core.managers.hex_asset_manager import HexAssetManager

# Initialize
manager = HexAssetManager(asset_dir="assets")

# Load an asset
surface = manager.load_hex_image(
    "grass.png",
    "base",
    metadata={"type": "terrain"},
    lazy=False
)

# Generate sprite sheet
sheet_path = manager.generate_sprite_sheet("base")

# Get asset metadata
metadata = manager.get_hex_metadata("grass.png")

# Clear cache
manager.clear_hex_cache()
```

#### Key Methods

- `load_hex_image(path, category, metadata=None, lazy=True, optimize=True, cache=True)`: Load a hex-based image
- `generate_sprite_sheet(category, pattern="*.png", sheet_name="sheet")`: Create sprite sheets
- `get_hex_metadata(path)`: Retrieve asset metadata
- `get_memory_usage(category=None)`: Get memory usage statistics
- `clear_hex_cache(category=None)`: Clear asset cache

### 2. HexAssetMetadataManager

Manages metadata for hex assets, supporting search and filtering.

```python
from visual_client.core.managers.hex_asset_metadata import HexAssetMetadataManager

# Initialize
metadata_manager = HexAssetMetadataManager()

# Add metadata
metadata_manager.add_metadata("grass.png", {
    "category": "base",
    "tags": ["grass", "terrain"],
    "season": "summer"
})

# Search assets
grass_assets = metadata_manager.search({
    "tags": ["grass"],
    "season": "summer"
})
```

#### Key Methods

- `add_metadata(asset_id, metadata)`: Add or update asset metadata
- `get_metadata(asset_id)`: Get metadata for a specific asset
- `search(criteria)`: Search assets by metadata criteria
- `remove_metadata(asset_id)`: Remove asset metadata

### 3. HexAssetCache

Memory-efficient caching system with reference counting.

```python
from visual_client.core.managers.hex_asset_cache import HexAssetCache

# Initialize with 512MB limit
cache = HexAssetCache(
    max_memory_mb=512,
    cleanup_threshold=0.9,
    cleanup_target=0.7
)

# Cache an asset
cache.put("grass.png", surface)

# Retrieve asset
surface = cache.get("grass.png")

# Remove asset
cache.remove("grass.png")
```

#### Key Methods

- `get(asset_id)`: Retrieve an asset from cache
- `put(asset_id, surface, memory_size=None)`: Add asset to cache
- `remove(asset_id)`: Remove asset from cache
- `clear()`: Clear entire cache

### 4. HexSpriteSheet

Manages sprite sheet generation and optimization.

```python
from visual_client.core.managers.hex_sprite_sheet import HexSpriteSheet

# Initialize
sprite_sheet = HexSpriteSheet(
    sheet_size=(2048, 2048),
    sprite_size=(64, 64)
)

# Generate sheet
sheet = sprite_sheet.generate("terrain/base/*.png")

# Extract sprite
sprite = sprite_sheet.get_sprite(0)  # Get first sprite
```

#### Key Methods

- `generate(pattern)`: Generate sprite sheet from images
- `get_sprite(index)`: Extract individual sprite
- `optimize()`: Optimize sprite sheet layout

### 5. HexAssetRenderer

Renders hex-based assets with proper scaling and layering.

```python
from visual_client.core.managers.hex_asset_renderer import HexAssetRenderer

# Initialize
renderer = HexAssetRenderer(
    asset_manager,
    sprite_sheet,
    cache,
    hex_size=64
)

# Render hex tile
renderer.render_hex_tile(
    surface,
    hex_coord=(0, 0),
    terrain_type="grass",
    features=["tree"],
    overlays=["highlight"],
    effects=["rain"],
    scale=1.0
)
```

#### Key Methods

- `render_hex_tile(surface, hex_coord, terrain_type, features=None, overlays=None, effects=None, scale=1.0)`: Render complete hex tile
- `calculate_hex_position(hex_coord, scale=1.0)`: Calculate pixel position

### 6. HexAssetPreviewUI

User interface for browsing and previewing assets.

```python
from visual_client.core.tools.hex_asset_preview_ui import HexAssetPreviewUI

# Initialize
preview_ui = HexAssetPreviewUI(
    asset_manager,
    metadata_manager,
    cache,
    window_size=(1280, 720)
)

# Handle events
preview_ui.handle_event(event)

# Update UI
preview_ui.update(delta_time)

# Draw UI
preview_ui.draw(screen)
```

#### Key Methods

- `handle_event(event)`: Process UI events
- `update(delta_time)`: Update UI state
- `draw(surface)`: Render UI
- `select_asset(asset_id)`: Select asset for preview
- `get_categories()`: Get available asset categories

## Performance Optimization

### Memory Management

1. Configure cache limits based on available memory:
```python
cache = HexAssetCache(
    max_memory_mb=512,  # 512MB limit
    cleanup_threshold=0.9,  # Clean at 90% usage
    cleanup_target=0.7  # Clean until 70% usage
)
```

2. Use lazy loading for large asset sets:
```python
surface = manager.load_hex_image(
    "large_asset.png",
    "terrain",
    lazy=True
)
```

### Rendering Optimization

1. Use sprite sheets for better performance:
```python
sheet_path = manager.generate_sprite_sheet(
    "terrain",
    pattern="*.png",
    sheet_name="terrain_sheet"
)
```

2. Implement view culling:
```python
visible_coords = [(q, r) for q in range(-5, 6) for r in range(-5, 6)]
for coord in visible_coords:
    renderer.render_hex_tile(surface, coord, "grass")
```

## Error Handling

The system uses a centralized error handling approach:

```python
from visual_client.core.error_handler import handle_component_error, ErrorSeverity

try:
    # Attempt operation
    surface = manager.load_hex_image("missing.png", "base")
except Exception as e:
    handle_component_error(
        e,
        "Failed to load asset",
        ErrorSeverity.ERROR,
        component="HexAssetManager"
    )
```

## Best Practices

1. **Asset Organization**
   - Keep assets in appropriate category directories
   - Use consistent naming conventions
   - Include metadata for searchability

2. **Memory Management**
   - Configure cache limits appropriately
   - Use lazy loading for large asset sets
   - Monitor memory usage with `get_memory_usage()`

3. **Performance**
   - Generate sprite sheets for frequently used assets
   - Implement view culling for large maps
   - Use appropriate asset dimensions (64x64 recommended)

4. **Error Handling**
   - Always handle potential errors
   - Use appropriate severity levels
   - Log errors for debugging

## Example: Complete Asset Pipeline

```python
# Initialize components
asset_manager = HexAssetManager("assets")
metadata_manager = HexAssetMetadataManager()
cache = HexAssetCache(max_memory_mb=512)
sprite_sheet = HexSpriteSheet()
renderer = HexAssetRenderer(asset_manager, sprite_sheet, cache)

# Load and cache assets
surface = asset_manager.load_hex_image(
    "grass.png",
    "base",
    metadata={"type": "terrain", "tags": ["grass"]},
    lazy=False
)

# Generate sprite sheets
sheet_path = asset_manager.generate_sprite_sheet("base")

# Render hex grid
for q in range(-5, 6):
    for r in range(-5, 6):
        renderer.render_hex_tile(
            screen,
            (q, r),
            "grass",
            features=["tree"] if (q + r) % 3 == 0 else None
        )

# Clean up
cache.clear()
```

## Troubleshooting

1. **Memory Issues**
   - Check cache configuration
   - Monitor memory usage
   - Use lazy loading
   - Clear cache when appropriate

2. **Rendering Problems**
   - Verify asset dimensions
   - Check layer order
   - Ensure proper scaling
   - Validate hex coordinates

3. **Asset Loading Failures**
   - Verify file paths
   - Check file permissions
   - Validate asset format
   - Monitor error logs

## Future Enhancements

1. **Planned Features**
   - Asset compression
   - Batch rendering
   - Advanced caching strategies
   - Animation support

2. **Performance Improvements**
   - GPU acceleration
   - Dynamic LOD
   - Async loading
   - Memory optimization 