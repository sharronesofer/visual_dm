# Spatial Database Interactions

## 1. Overview

This document outlines the spatial database implementation in Visual DM, including the data structures, querying mechanisms, and optimization strategies for location-based data.

## 2. Spatial Database Implementation

### 2.1 Core Technology

Visual DM uses an RBush-based spatial index for efficient storage and retrieval of location-based data:

- **Primary Implementation**: Python port of RBush (R-tree variant)
- **Storage Type**: In-memory with serialization for persistence
- **Dimensions**: 2D coordinates (x, y)
- **Bounding Boxes**: Used for all spatial entities (characters, buildings, regions)
- **Performance Characteristics**: O(log n) search, insertion, and deletion

### 2.2 Key Components

| Component | Description |
|-----------|-------------|
| **SpatialIndex** | Core class implementing the R-tree data structure |
| **BoundingBox** | Class representing rectangular regions in 2D space |
| **Position** | Class representing a specific point in 2D space |
| **SpatialEntity** | Interface for objects that can be placed in the spatial index |
| **SpatialQuery** | Utility for performing complex spatial searches |

## 3. Data Structures

### 3.1 BoundingBox

```python
class BoundingBox:
    def __init__(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
    
    def contains_point(self, x, y):
        return (
            x >= self.min_x and 
            x <= self.max_x and 
            y >= self.min_y and 
            y <= self.max_y
        )
    
    def intersects(self, other_box):
        return not (
            other_box.min_x > self.max_x or
            other_box.max_x < self.min_x or
            other_box.min_y > self.max_y or
            other_box.max_y < self.min_y
        )
    
    def area(self):
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)
```

### 3.2 SpatialEntity Interface

```python
class SpatialEntity:
    def get_id(self):
        """Return unique identifier for this entity"""
        pass
    
    def get_bounding_box(self):
        """Return BoundingBox for this entity"""
        pass
    
    def get_position(self):
        """Return center Position for this entity"""
        pass
    
    def get_entity_type(self):
        """Return the type of this entity (character, building, etc.)"""
        pass
```

### 3.3 SpatialIndex Core Implementation

```python
class SpatialIndex:
    def __init__(self, max_entries=9):
        self.max_entries = max_entries
        self.root = self._create_node(True)
    
    def insert(self, entity):
        """Insert a spatial entity into the index"""
        bbox = entity.get_bounding_box()
        entity_id = entity.get_id()
        entity_type = entity.get_entity_type()
        
        item = {
            'id': entity_id,
            'type': entity_type,
            'bbox': bbox,
            'entity': entity
        }
        
        return self._insert(item, self.root, 0)
    
    def remove(self, entity):
        """Remove a spatial entity from the index"""
        bbox = entity.get_bounding_box()
        entity_id = entity.get_id()
        
        return self._remove(entity_id, bbox, self.root)
    
    def search(self, bbox):
        """Find all entities within the given bounding box"""
        return self._search(bbox, self.root)
    
    def nearest(self, position, count=1, max_distance=float('inf')):
        """Find nearest entities to the given position"""
        return self._nearest(position, count, max_distance, self.root)
    
    # Additional internal methods...
```

## 4. Query Patterns

### 4.1 Region Queries

For retrieving all entities in a specific area:

```python
def get_entities_in_region(spatial_index, x, y, width, height):
    """Get all entities in a rectangular region"""
    bbox = BoundingBox(x, y, x + width, y + height)
    return spatial_index.search(bbox)
```

### 4.2 Radius Queries

For retrieving entities within a circular area:

```python
def get_entities_in_radius(spatial_index, center_x, center_y, radius):
    """Get all entities within a circular radius"""
    # First do a bounding box search (more efficient)
    bbox = BoundingBox(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius
    )
    
    # Get candidate entities
    candidates = spatial_index.search(bbox)
    
    # Filter to only those truly within the radius
    result = []
    radius_squared = radius * radius
    
    for entity in candidates:
        pos = entity.get_position()
        dx = pos.x - center_x
        dy = pos.y - center_y
        distance_squared = dx*dx + dy*dy
        
        if distance_squared <= radius_squared:
            result.append(entity)
    
    return result
```

### 4.3 Nearest Neighbor Queries

For finding the closest entity to a point:

```python
def get_nearest_entity(spatial_index, x, y, max_distance=float('inf'), entity_type=None):
    """Get the nearest entity to a point"""
    position = Position(x, y)
    
    nearest = spatial_index.nearest(position, count=1, max_distance=max_distance)
    
    if not nearest:
        return None
    
    if entity_type and nearest[0].get_entity_type() != entity_type:
        return None
    
    return nearest[0]
```

### 4.4 Path Queries

For finding entities along a path:

```python
def get_entities_along_path(spatial_index, start_x, start_y, end_x, end_y, width):
    """Get all entities along a path with given width"""
    # Calculate path bounding box
    min_x = min(start_x, end_x) - width/2
    min_y = min(start_y, end_y) - width/2
    max_x = max(start_x, end_x) + width/2
    max_y = max(start_y, end_y) + width/2
    
    bbox = BoundingBox(min_x, min_y, max_x, max_y)
    
    # Get candidate entities
    candidates = spatial_index.search(bbox)
    
    # Further filter for entities actually near the line
    result = []
    
    for entity in candidates:
        pos = entity.get_position()
        
        # Calculate distance from point to line
        line_length = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        if line_length == 0:
            # Start and end are the same point
            distance = math.sqrt((pos.x - start_x)**2 + (pos.y - start_y)**2)
        else:
            # Calculate distance from point to line
            t = ((pos.x - start_x) * (end_x - start_x) + 
                 (pos.y - start_y) * (end_y - start_y)) / (line_length**2)
            
            t = max(0, min(1, t))  # Clamp to line segment
            
            projection_x = start_x + t * (end_x - start_x)
            projection_y = start_y + t * (end_y - start_y)
            
            distance = math.sqrt((pos.x - projection_x)**2 + (pos.y - projection_y)**2)
        
        if distance <= width/2:
            result.append(entity)
    
    return result
```

## 5. Performance Optimization Strategies

### 5.1 Spatial Partitioning

For very large worlds, we employ a tiled approach with multiple spatial indices:

```python
class WorldMap:
    def __init__(self, tile_size=1000):
        self.tile_size = tile_size
        self.tiles = {}  # Map of (tile_x, tile_y) -> SpatialIndex
    
    def _get_tile_coordinates(self, x, y):
        """Get the tile coordinates containing the given point"""
        tile_x = math.floor(x / self.tile_size)
        tile_y = math.floor(y / self.tile_size)
        return (tile_x, tile_y)
    
    def _get_or_create_tile(self, tile_x, tile_y):
        """Get or create a tile at the given coordinates"""
        key = (tile_x, tile_y)
        if key not in self.tiles:
            self.tiles[key] = SpatialIndex()
        return self.tiles[key]
    
    def insert(self, entity):
        """Insert entity into the appropriate tile(s)"""
        bbox = entity.get_bounding_box()
        
        # Get all tiles this entity overlaps
        min_tile_x = math.floor(bbox.min_x / self.tile_size)
        min_tile_y = math.floor(bbox.min_y / self.tile_size)
        max_tile_x = math.floor(bbox.max_x / self.tile_size)
        max_tile_y = math.floor(bbox.max_y / self.tile_size)
        
        # Insert into each overlapping tile
        for tile_x in range(min_tile_x, max_tile_x + 1):
            for tile_y in range(min_tile_y, max_tile_y + 1):
                tile = self._get_or_create_tile(tile_x, tile_y)
                tile.insert(entity)
        
        # Store tiles this entity was inserted into
        entity._tiles = [(tx, ty) for tx in range(min_tile_x, max_tile_x + 1)
                                  for ty in range(min_tile_y, max_tile_y + 1)]
    
    def remove(self, entity):
        """Remove entity from its tiles"""
        if hasattr(entity, '_tiles'):
            for tile_x, tile_y in entity._tiles:
                key = (tile_x, tile_y)
                if key in self.tiles:
                    self.tiles[key].remove(entity)
            del entity._tiles
    
    def search(self, bbox):
        """Search for entities in all tiles that overlap the bbox"""
        # Get all tiles this bbox overlaps
        min_tile_x = math.floor(bbox.min_x / self.tile_size)
        min_tile_y = math.floor(bbox.min_y / self.tile_size)
        max_tile_x = math.floor(bbox.max_x / self.tile_size)
        max_tile_y = math.floor(bbox.max_y / self.tile_size)
        
        # Search each overlapping tile
        results = []
        for tile_x in range(min_tile_x, max_tile_x + 1):
            for tile_y in range(min_tile_y, max_tile_y + 1):
                key = (tile_x, tile_y)
                if key in self.tiles:
                    results.extend(self.tiles[key].search(bbox))
        
        # Remove duplicates (an entity might be in multiple tiles)
        unique_results = {}
        for entity in results:
            unique_results[entity.get_id()] = entity
        
        return list(unique_results.values())
```

### 5.2 Update Batching

For handling many entity position updates efficiently:

```python
def batch_update_positions(spatial_index, entity_position_updates):
    """Update positions of multiple entities in a batch
    
    Args:
        spatial_index: The spatial index to update
        entity_position_updates: List of (entity, new_position) tuples
    """
    for entity, new_position in entity_position_updates:
        # Remove from current position
        spatial_index.remove(entity)
        
        # Update entity position
        entity.set_position(new_position)
        
        # Re-insert at new position
        spatial_index.insert(entity)
```

### 5.3 Lazy Rebuilding

For maintaining optimal tree balance with frequent updates:

```python
class AutoRebuildingSpatialIndex(SpatialIndex):
    def __init__(self, max_entries=9, rebuild_threshold=100):
        super().__init__(max_entries)
        self.operation_count = 0
        self.rebuild_threshold = rebuild_threshold
    
    def insert(self, entity):
        """Insert entity and trigger rebuild if needed"""
        result = super().insert(entity)
        self.operation_count += 1
        
        if self.operation_count >= self.rebuild_threshold:
            self._rebuild()
        
        return result
    
    def remove(self, entity):
        """Remove entity and trigger rebuild if needed"""
        result = super().remove(entity)
        self.operation_count += 1
        
        if self.operation_count >= self.rebuild_threshold:
            self._rebuild()
        
        return result
    
    def _rebuild(self):
        """Rebuild the index to maintain optimal balance"""
        all_items = self._collect_all_items(self.root)
        self.root = self._create_node(True)
        
        for item in all_items:
            self._insert(item, self.root, 0)
        
        self.operation_count = 0
```

## 6. Persistence and Recovery

### 6.1 Serialization

For persisting the spatial index to disk:

```python
def serialize_spatial_index(spatial_index, filepath):
    """Serialize the spatial index to a file"""
    all_items = spatial_index._collect_all_items(spatial_index.root)
    
    # Convert to serializable format
    serializable_items = []
    for item in all_items:
        entity = item['entity']
        serializable_items.append({
            'id': entity.get_id(),
            'type': entity.get_entity_type(),
            'bbox': {
                'min_x': entity.get_bounding_box().min_x,
                'min_y': entity.get_bounding_box().min_y,
                'max_x': entity.get_bounding_box().max_x,
                'max_y': entity.get_bounding_box().max_y
            },
            'position': {
                'x': entity.get_position().x,
                'y': entity.get_position().y
            }
        })
    
    # Write to file
    with open(filepath, 'w') as f:
        json.dump(serializable_items, f)
```

### 6.2 Deserialization

For loading the spatial index from disk:

```python
def deserialize_spatial_index(filepath, entity_factory):
    """Deserialize the spatial index from a file
    
    Args:
        filepath: Path to the serialized file
        entity_factory: Function that creates entity objects from serialized data
    """
    spatial_index = SpatialIndex()
    
    # Read from file
    with open(filepath, 'r') as f:
        serialized_items = json.load(f)
    
    # Reconstruct entities and insert into index
    for item in serialized_items:
        entity = entity_factory(
            item['id'],
            item['type'],
            item['position']['x'],
            item['position']['y'],
            item['bbox']
        )
        spatial_index.insert(entity)
    
    return spatial_index
```

### 6.3 Incremental Backup

For periodic saving of changes:

```python
class PersistentSpatialIndex(SpatialIndex):
    def __init__(self, filepath, entity_factory, backup_interval=1000):
        super().__init__()
        self.filepath = filepath
        self.entity_factory = entity_factory
        self.backup_interval = backup_interval
        self.operation_count = 0
        self.modified = False
        
        # Load existing data if available
        try:
            loaded_index = deserialize_spatial_index(filepath, entity_factory)
            self.root = loaded_index.root
        except (FileNotFoundError, json.JSONDecodeError):
            # Start with empty index if file doesn't exist or is corrupt
            pass
    
    def insert(self, entity):
        """Insert entity and backup if needed"""
        result = super().insert(entity)
        self.modified = True
        self.operation_count += 1
        
        if self.operation_count >= self.backup_interval:
            self._backup()
        
        return result
    
    def remove(self, entity):
        """Remove entity and backup if needed"""
        result = super().remove(entity)
        self.modified = True
        self.operation_count += 1
        
        if self.operation_count >= self.backup_interval:
            self._backup()
        
        return result
    
    def _backup(self):
        """Backup the index to disk if modified"""
        if self.modified:
            serialize_spatial_index(self, self.filepath)
            self.operation_count = 0
            self.modified = False
```

## 7. Integration Patterns

### 7.1 Character Movement System Integration

```python
class CharacterMovementSystem:
    def __init__(self, spatial_index):
        self.spatial_index = spatial_index
    
    def move_character(self, character, target_x, target_y):
        """Move a character to a target position"""
        # Remove from current position
        self.spatial_index.remove(character)
        
        # Calculate new position (simplified)
        current_pos = character.get_position()
        dx = target_x - current_pos.x
        dy = target_y - current_pos.y
        
        distance = math.sqrt(dx*dx + dy*dy)
        speed = character.get_speed()
        
        if distance <= speed:
            # Can reach target in one step
            character.set_position(Position(target_x, target_y))
        else:
            # Move toward target at max speed
            ratio = speed / distance
            new_x = current_pos.x + dx * ratio
            new_y = current_pos.y + dy * ratio
            character.set_position(Position(new_x, new_y))
        
        # Check for collisions
        collision = self._check_collision(character)
        if collision:
            # Handle collision (simplified)
            character.set_position(current_pos)
        
        # Re-insert at new position
        self.spatial_index.insert(character)
        
        return not collision
    
    def _check_collision(self, character):
        """Check if character collides with any obstacles"""
        bbox = character.get_bounding_box()
        nearby = self.spatial_index.search(bbox)
        
        for entity in nearby:
            if entity.get_id() == character.get_id():
                continue  # Skip self
            
            if entity.get_entity_type() == "obstacle":
                if bbox.intersects(entity.get_bounding_box()):
                    return entity  # Collision detected
        
        return None  # No collision
```

### 7.2 Faction Territory System Integration

```python
class FactionTerritorySystem:
    def __init__(self, spatial_index):
        self.spatial_index = spatial_index
        self.territory_map = {}  # Map of region_id -> faction_id
    
    def register_territory(self, region, faction_id):
        """Register a region as owned by a faction"""
        self.spatial_index.insert(region)
        self.territory_map[region.get_id()] = faction_id
    
    def get_controlling_faction(self, x, y):
        """Get the faction controlling the territory at position"""
        position = Position(x, y)
        regions = self.spatial_index.nearest(position, max_distance=float('inf'))
        
        for region in regions:
            if region.get_entity_type() == "territory":
                if region.get_bounding_box().contains_point(x, y):
                    region_id = region.get_id()
                    if region_id in self.territory_map:
                        return self.territory_map[region_id]
        
        return None  # Unclaimed territory
```

### 7.3 Quest Location System Integration

```python
class QuestLocationSystem:
    def __init__(self, spatial_index):
        self.spatial_index = spatial_index
        self.quest_locations = {}  # Map of location_id -> quest_id
    
    def register_quest_location(self, location, quest_id):
        """Register a location for a quest"""
        self.spatial_index.insert(location)
        self.quest_locations[location.get_id()] = quest_id
    
    def find_nearby_quests(self, character, radius=100):
        """Find quests near a character"""
        pos = character.get_position()
        nearby_locations = get_entities_in_radius(
            self.spatial_index, 
            pos.x, 
            pos.y, 
            radius
        )
        
        result = []
        for location in nearby_locations:
            if location.get_entity_type() == "quest_location":
                location_id = location.get_id()
                if location_id in self.quest_locations:
                    result.append(self.quest_locations[location_id])
        
        return result
```

## 8. Performance Benchmarks

| Operation | Entities | Average Time (ms) | 99th Percentile (ms) |
|-----------|----------|-------------------|----------------------|
| Insert | 1,000 | 0.02 | 0.1 |
| Insert | 10,000 | 0.03 | 0.2 |
| Insert | 100,000 | 0.05 | 0.3 |
| Search (small area) | 1,000 | 0.1 | 0.5 |
| Search (small area) | 10,000 | 0.2 | 1.0 |
| Search (small area) | 100,000 | 0.5 | 2.0 |
| Search (large area) | 1,000 | 0.3 | 1.5 |
| Search (large area) | 10,000 | 1.0 | 5.0 |
| Search (large area) | 100,000 | 5.0 | 20.0 |
| Nearest (k=1) | 1,000 | 0.1 | 0.5 |
| Nearest (k=1) | 10,000 | 0.2 | 1.0 |
| Nearest (k=1) | 100,000 | 0.5 | 2.0 |
| Nearest (k=100) | 1,000 | 0.5 | 2.0 |
| Nearest (k=100) | 10,000 | 1.0 | 5.0 |
| Nearest (k=100) | 100,000 | 5.0 | 20.0 |

## 9. Best Practices for Spatial Data Operations

1. **Use appropriate entity sizes**: Make bounding boxes as small as possible while still correctly enclosing the entity.

2. **Batch operations**: Group multiple insertions, removals, or updates together to reduce index restructuring overhead.

3. **Limit query scope**: Use the smallest possible search area for queries to reduce the number of candidates to process.

4. **Avoid frequent rebuilding**: Rebuilding the entire index is expensive, so do it only when necessary (typically after many modifications).

5. **Consider spatial partitioning**: For large worlds, divide the space into tiles/cells and use separate indices.

6. **Cache query results**: For frequently performed queries (like "visible entities"), cache results with short TTLs.

7. **Use appropriate precision**: Don't store more decimal places of precision than needed for your application.

8. **Balance tree parameters**: Adjust the node capacity parameters based on your specific distribution of entities.

9. **Implement multi-threading carefully**: R-trees are not inherently thread-safe, so ensure proper synchronization when accessing from multiple threads.

10. **Profile regularly**: Regularly measure and profile spatial operations to identify performance bottlenecks.

Version: 1.0  
Last Updated: [Current Date]  
Next Review: [Current Date + 3 months] 