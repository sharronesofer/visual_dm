import math
from typing import List, Tuple, Optional, Dict, Any, Union, Callable
from visual_client.core.utils.coordinate_utils import (
    Vector2, Vector3, vec_distance, global_to_local, local_to_global, COORD_EPSILON
)
from visual_client.core.utils.coordinates import GlobalCoord, LocalCoord

# --- Data Structures ---

class ChunkMetadata:
    """
    Metadata for a chunk, including dependencies, load priority, streaming state, and LOD.
    """
    def __init__(self, dependencies: Optional[List[str]] = None, load_priority: float = 0.0, streaming_state: str = 'unloaded', lod_level: int = 0):
        self.dependencies: List[str] = dependencies or []
        self.load_priority: float = load_priority
        self.streaming_state: str = streaming_state  # 'unloaded', 'loading', 'loaded', 'unloading'
        self.lod_level: int = lod_level  # 0=high, 1=medium, 2=low

    def set_priority(self, priority: float) -> None:
        self.load_priority = priority

    def set_state(self, state: str) -> None:
        self.streaming_state = state

    def set_lod(self, lod_level: int) -> None:
        self.lod_level = lod_level

class SceneChunk:
    """
    Represents a chunk of the scene, with bounds, entities, and metadata.
    """
    def __init__(self, bounds: Tuple[Vector3, Vector3], entities: Optional[List[Any]] = None, metadata: Optional[ChunkMetadata] = None):
        self.bounds: Tuple[Vector3, Vector3] = bounds  # (min, max) in world coordinates
        self.entities: List[Any] = entities or []
        self.metadata: ChunkMetadata = metadata or ChunkMetadata()

    def contains(self, position: Vector3) -> bool:
        (min_b, max_b) = self.bounds
        return all(min_b[i] - COORD_EPSILON <= position[i] <= max_b[i] + COORD_EPSILON for i in range(3))

    def center(self) -> Vector3:
        (min_b, max_b) = self.bounds
        return tuple((min_b[i] + max_b[i]) / 2.0 for i in range(3))

    def set_lod(self, lod_level: int) -> None:
        self.metadata.set_lod(lod_level)

    def set_priority(self, priority: float) -> None:
        self.metadata.set_priority(priority)

    def set_state(self, state: str) -> None:
        self.metadata.set_state(state)

    def add_dependency(self, chunk_key: str) -> None:
        if chunk_key not in self.metadata.dependencies:
            self.metadata.dependencies.append(chunk_key)

    def remove_dependency(self, chunk_key: str) -> None:
        if chunk_key in self.metadata.dependencies:
            self.metadata.dependencies.remove(chunk_key)

# --- Partition Tree (Quadtree/Octree) ---

class SpatialPartitionTree:
    def __init__(self, bounds: Tuple[Vector3, Vector3], max_depth: int = 5, min_size: float = 10.0, is_3d: bool = True):
        self.bounds = bounds
        self.max_depth = max_depth
        self.min_size = min_size
        self.is_3d = is_3d
        self.root = self._create_node(bounds, 0)

    class Node:
        def __init__(self, bounds: Tuple[Vector3, Vector3], depth: int, is_leaf: bool = True):
            self.bounds = bounds
            self.depth = depth
            self.is_leaf = is_leaf
            self.children: Optional[List['SpatialPartitionTree.Node']] = None
            self.chunk: Optional[SceneChunk] = None

    def _create_node(self, bounds: Tuple[Vector3, Vector3], depth: int) -> 'SpatialPartitionTree.Node':
        node = self.Node(bounds, depth)
        if depth >= self.max_depth or self._size(bounds) <= self.min_size:
            node.is_leaf = True
            node.chunk = SceneChunk(bounds)
        else:
            node.is_leaf = False
            node.children = [
                self._create_node(child_bounds, depth + 1)
                for child_bounds in self._subdivide(bounds)
            ]
        return node

    def _size(self, bounds: Tuple[Vector3, Vector3]) -> float:
        min_b, max_b = bounds
        return max(max_b[i] - min_b[i] for i in range(3))

    def _subdivide(self, bounds: Tuple[Vector3, Vector3]) -> List[Tuple[Vector3, Vector3]]:
        min_b, max_b = bounds
        center = tuple((min_b[i] + max_b[i]) / 2.0 for i in range(3))
        if self.is_3d:
            # Octree: 8 children
            return [
                ((x0, y0, z0), (x1, y1, z1))
                for x0, x1 in [(min_b[0], center[0]), (center[0], max_b[0])]
                for y0, y1 in [(min_b[1], center[1]), (center[1], max_b[1])]
                for z0, z1 in [(min_b[2], center[2]), (center[2], max_b[2])]
            ]
        else:
            # Quadtree: 4 children (z is ignored)
            return [
                ((x0, y0, min_b[2]), (x1, y1, max_b[2]))
                for x0, x1 in [(min_b[0], center[0]), (center[0], max_b[0])]
                for y0, y1 in [(min_b[1], center[1]), (center[1], max_b[1])]
            ]

    def insert_entity(self, entity: Any, position: Vector3):
        self._insert_entity_recursive(self.root, entity, position)

    def _insert_entity_recursive(self, node: 'SpatialPartitionTree.Node', entity: Any, position: Vector3):
        if node.is_leaf:
            node.chunk.entities.append(entity)
        else:
            for child in node.children:
                min_b, max_b = child.bounds
                if all(min_b[i] - COORD_EPSILON <= position[i] <= max_b[i] + COORD_EPSILON for i in range(3)):
                    self._insert_entity_recursive(child, entity, position)
                    break

    def query_chunks(self, region: Tuple[Vector3, Vector3]) -> List[SceneChunk]:
        result = []
        self._query_chunks_recursive(self.root, region, result)
        return result

    def _query_chunks_recursive(self, node: 'SpatialPartitionTree.Node', region: Tuple[Vector3, Vector3], result: List[SceneChunk]):
        if node.is_leaf:
            if self._bounds_overlap(node.bounds, region):
                result.append(node.chunk)
        else:
            for child in node.children:
                if self._bounds_overlap(child.bounds, region):
                    self._query_chunks_recursive(child, region, result)

    def _bounds_overlap(self, a: Tuple[Vector3, Vector3], b: Tuple[Vector3, Vector3]) -> bool:
        for i in range(3):
            if a[1][i] < b[0][i] or a[0][i] > b[1][i]:
                return False
        return True

    def get_visible_chunks(self, player_pos: Vector3, view_frustum: Optional[Any] = None, max_distance: float = 1000.0) -> List[SceneChunk]:
        # For now, use a spherical region around the player; view_frustum can be integrated later
        region = (
            tuple(player_pos[i] - max_distance for i in range(3)),
            tuple(player_pos[i] + max_distance for i in range(3))
        )
        return self.query_chunks(region)

    def get_priority_chunks(self, player_pos: Vector3, max_chunks: int = 10) -> List[SceneChunk]:
        visible = self.get_visible_chunks(player_pos)
        visible.sort(key=lambda chunk: vec_distance(chunk.center(), player_pos))
        return visible[:max_chunks]

# --- Integration Points ---
# - Floating origin: use global_to_local/local_to_global for all position queries
# - Spatial indexing: batch entity updates, thread safety, adaptive thresholds (to be integrated in streaming system)

# --- Example Usage ---
# tree = SpatialPartitionTree(bounds=((0,0,0), (1000,1000,1000)), max_depth=6, min_size=20.0, is_3d=True)
# tree.insert_entity(entity, position)
# visible_chunks = tree.get_visible_chunks(player_pos) 