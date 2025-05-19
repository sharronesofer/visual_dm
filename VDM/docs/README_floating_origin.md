# Floating Origin System

## Overview

The Floating Origin system solves precision issues in large-scale world environments by dynamically shifting the coordinate system's origin as the player moves through the world. This approach maintains floating-point precision for all entities, regardless of their absolute position in the world.

## Why Use Floating Origin?

In large game worlds, floating-point precision issues can cause visual artifacts and physics anomalies when entities are far from the origin. The Floating Origin system addresses this by:

- Maintaining high precision for all entities
- Supporting effectively unlimited world sizes
- Preventing jittering, physics glitches, and rendering artifacts
- Simplifying physics and collision calculations

## Core Components

The system consists of three main components:

1. **CoordinateSystem**: Manages the global-to-local coordinate mapping
2. **FloatingOrigin**: Tracks entities and handles origin shifts
3. **GlobalCoord/LocalCoord**: Specialized coordinate types

## Usage

### Basic Setup

```python
from visual_client.core.utils.floating_origin import floating_origin
from visual_client.core.utils.coordinates import GlobalCoord

# Register an entity
floating_origin.register_entity(
    entity_id="player",
    position_getter=player.get_position,
    position_setter=player.set_position
)

# Update player position and check if shift occurred
position = GlobalCoord(10000, 20000, 0)
shift_occurred = floating_origin.update_player_position(position)
```

### Entity Registration

Entities must implement two methods:

1. **position_getter**: Returns the entity's global position as a `GlobalCoord`
2. **position_setter**: Accepts delta movements `(dx, dy, dz)` to apply during shifts

```python
class GameObject:
    def __init__(self, x, y, z):
        self.position = (x, y, z)
    
    def get_position(self):
        return GlobalCoord(*self.position)
    
    def set_position(self, dx, dy, dz):
        x, y, z = self.position
        self.position = (x + dx, y + dy, z + dz)
```

### Batch Operations

For better performance when handling many entities:

```python
# Batch register entities
entities = [
    ("entity1", entity1.get_position, entity1.set_position),
    ("entity2", entity2.get_position, entity2.set_position),
    # ...
]
floating_origin.batch_register_entities(entities, group="enemies")

# Unregister an entire group
floating_origin.unregister_group("enemies")
```

### Coordinate Conversions

Convert between global and local coordinates:

```python
# Convert global to local coordinates
global_pos = GlobalCoord(10000, 20000, 0)
local_pos = floating_origin.get_local_position(global_pos)

# Convert local to global coordinates
local_pos = LocalCoord(100, 200, 0)
global_pos = floating_origin.get_global_position(local_pos)
```

### Performance Monitoring

Monitor the performance of the floating origin system:

```python
# Enable debug mode for detailed logging
floating_origin.enable_debug(True)

# Get performance metrics
metrics = floating_origin.get_metrics()
print(f"Total shifts: {metrics['shift_count']}")
print(f"Average shift time: {metrics['avg_shift_time']*1000:.2f}ms")

# Get full serialized state
state = floating_origin.serialize_state()
```

## Origin Shift Thresholds

The system automatically triggers shifts when the player moves beyond the `SHIFT_THRESHOLD` distance from the current origin (default: 1000 units). This threshold can be adjusted in `coordinates.py`.

## Entity Groups

Entities can be organized into groups for easier management:

```python
# Register entity in a specific group
floating_origin.register_entity("entity1", get_pos, set_pos, group="enemies")

# Get information about entity groups
group_info = floating_origin.get_entity_groups()
print(group_info)  # {"enemies": 10, "npcs": 5, ...}
```

## Benchmarking

The system includes a benchmarking utility to evaluate performance with different entity counts:

```bash
python -m visual_client.core.utils.floating_origin_benchmark --counts=100,1000,10000 --shifts=20 --plot
```

## Examples

For a complete implementation example, see `visual_client/examples/floating_origin_example.py`.

## Best Practices

1. **Register entities early**: Register entities as soon as they're created
2. **Use entity groups**: Organize entities into logical groups for better management
3. **Prioritize player updates**: Always update the player position first
4. **Monitor performance**: Use metrics to identify performance bottlenecks
5. **Use batch operations**: Use batch_register_entities for better performance
6. **Consider threading**: For large entity counts, consider implementing threaded updates

## Technical Details

### Origin Shift Process

When a shift occurs:

1. The player's position is used as the new origin
2. The offset between the old and new origins is calculated
3. All registered entities are updated with negative offset values
4. The coordinate system's internal origin is updated
5. Metrics and history are recorded

### Performance Characteristics

- Entity updates are O(n) with the number of entities
- Registration and unregistration are O(1) operations
- Coordinate conversions are O(1)
- Memory usage is minimal (a few bytes per entity)

## Configuration

The system has configurable parameters:

- `SHIFT_THRESHOLD`: Distance from origin before a shift is triggered (default: 1000.0 units)
- `MAX_SAFE_COORDINATE`: Maximum coordinate value before potential precision issues (default: 100000.0 units)
- `COORD_EPSILON`: Epsilon for float comparisons (default: 1e-10)

## Integration Points

To fully integrate the floating origin system with the game:

1. **Entity System**: Register all dynamic entities with the floating origin system
2. **Terrain System**: Modify terrain loading to use local coordinates
3. **Renderer**: Update to use local coordinates for all rendering
4. **Physics**: Adapt physics calculations to work with local coordinates

## Debug Tools

Enable debug mode to log origin shifts and performance metrics:

```python
floating_origin.enable_debug(True)
```

## Testing

Comprehensive unit tests are available in `visual_client/tests/test_floating_origin.py`.

## Integration with Rendering and Physics Systems

- **Rendering:**
  - All rendering code must use local coordinates (relative to the current floating origin) for all draw calls, camera calculations, and scene graph transforms.
  - Use the provided coordinate conversion utilities (`global_to_local`, `local_to_global`, `world_to_screen`, `screen_to_world`) to ensure all positions are floating origin aware.
  - **Never use global coordinates directly in rendering code.**
  - Update all modules (e.g., renderers, viewport managers) to use local coordinates for maximum precision and stability.

- **Physics:**
  - All physics objects must use local coordinates for positions, velocities, and forces.
  - On every origin shift, update all physics objects by the shift delta to maintain simulation stability.
  - Stub methods are provided in the scene manager for integrating with external physics engines (e.g., Unity, PyBullet). Implement these hooks to update all physics objects on origin shift events.
  - **Never use global coordinates directly in physics code.**

## Debug Visualization and Precision Safeguards

- Enable debug mode to log origin shifts, performance metrics, and precision warnings:

```python
floating_origin.enable_debug(True)
```

- Use debug overlays or logs to visualize when entities approach precision limits or when an origin shift is triggered.
- The system will automatically trigger a shift before floating-point precision issues can occur (see `SHIFT_THRESHOLD` in `coordinates.py`).
- If you see jitter, artifacts, or simulation instability, check for accidental use of global coordinates in rendering or physics.

## Troubleshooting

- **Symptom:** Visual jitter or physics instability at large distances.
  - **Cause:** Rendering or physics code is using global coordinates instead of local coordinates.
  - **Solution:** Refactor code to use `get_local_position()` for all world positions in rendering and physics systems.

- **Symptom:** Entities not updating correctly after an origin shift.
  - **Cause:** Entity not registered with the floating origin system, or missing `set_position` implementation.
  - **Solution:** Ensure all dynamic entities are registered and implement the required interface.

## Integration with World Generation and AI Systems

- World generation code should be aware of region boundaries and coordinate system alignment.
- When spawning entities or generating terrain, always use the current local origin for placement.
- AI pathfinding and navigation should use local coordinates for all calculations.
- For multiplayer synchronization, always convert positions to global coordinates before network transmission, and back to local on receipt.

## Performance Considerations

- **Stress Testing:**
  - Simulate thousands of entities and rapid origin shifts to ensure the system remains performant and stable.
  - Use the provided benchmarking utility and extend tests to cover edge cases and high-entity-count scenarios.

- **Debugging Tips:**
  - Enable debug mode in the floating origin system to log all origin shifts and performance metrics.
  - Use the debug utility functions to visualize local/global positions, region boundaries, and entity states.
  - Monitor logs for warnings about precision, performance, or integration issues. 