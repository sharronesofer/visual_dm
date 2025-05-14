"""
Optimized mesh generation system for buildings.
Implements spatial partitioning and geometry batching for improved performance.
"""

from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
import numpy as np
from collections import defaultdict
import logging
from app.core.profiling.building_profiler import building_profiler

logger = logging.getLogger(__name__)

@dataclass
class AABB:
    """Axis-aligned bounding box."""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    def intersects(self, other: 'AABB') -> bool:
        """Check if this AABB intersects with another."""
        return (
            self.min_x <= other.max_x and self.max_x >= other.min_x and
            self.min_y <= other.max_y and self.max_y >= other.min_y and
            self.min_z <= other.max_z and self.max_z >= other.min_z
        )

class OctreeNode:
    """Octree node for spatial partitioning."""
    
    def __init__(self, bounds: AABB, max_depth: int = 8, max_elements: int = 32):
        self.bounds = bounds
        self.max_depth = max_depth
        self.max_elements = max_elements
        self.depth = 0
        self.children: List[Optional[OctreeNode]] = [None] * 8
        self.elements: List[Tuple[AABB, int]] = []  # (AABB, element_index)
    
    def insert(self, element: Tuple[AABB, int], depth: int = 0) -> None:
        """Insert an element into the octree."""
        if depth >= self.max_depth or len(self.elements) < self.max_elements:
            self.elements.append(element)
            return
        
        if not self.children[0]:  # Lazy child creation
            self._split()
        
        # Insert into appropriate children
        for child in self.children:
            if child and element[0].intersects(child.bounds):
                child.insert(element, depth + 1)
    
    def query(self, bounds: AABB) -> Set[int]:
        """Query elements that intersect with the given bounds."""
        result = set()
        
        # Check elements at this node
        for element_bounds, element_index in self.elements:
            if bounds.intersects(element_bounds):
                result.add(element_index)
        
        # Check children
        if self.children[0]:
            for child in self.children:
                if child and bounds.intersects(child.bounds):
                    result.update(child.query(bounds))
        
        return result
    
    def _split(self) -> None:
        """Split this node into eight children."""
        center_x = (self.bounds.min_x + self.bounds.max_x) / 2
        center_y = (self.bounds.min_y + self.bounds.max_y) / 2
        center_z = (self.bounds.min_z + self.bounds.max_z) / 2
        
        # Create eight children
        for i in range(8):
            x_min = self.bounds.min_x if (i & 1) == 0 else center_x
            y_min = self.bounds.min_y if (i & 2) == 0 else center_y
            z_min = self.bounds.min_z if (i & 4) == 0 else center_z
            x_max = center_x if (i & 1) == 0 else self.bounds.max_x
            y_max = center_y if (i & 2) == 0 else self.bounds.max_y
            z_max = center_z if (i & 4) == 0 else self.bounds.max_z
            
            self.children[i] = OctreeNode(
                AABB(x_min, y_min, z_min, x_max, y_max, z_max),
                self.max_depth,
                self.max_elements
            )

class GeometryBatch:
    """Manages batched geometry for efficient rendering."""
    
    def __init__(self, material_id: str):
        self.material_id = material_id
        self.vertices: List[np.ndarray] = []
        self.indices: List[np.ndarray] = []
        self.vertex_offset = 0
    
    def add_geometry(self, vertices: np.ndarray, indices: np.ndarray) -> None:
        """Add geometry to the batch."""
        self.vertices.append(vertices)
        # Adjust indices for the current vertex offset
        adjusted_indices = indices + self.vertex_offset
        self.indices.append(adjusted_indices)
        self.vertex_offset += len(vertices)
    
    def finalize(self) -> Tuple[np.ndarray, np.ndarray]:
        """Finalize the batch and return combined geometry."""
        combined_vertices = np.concatenate(self.vertices, axis=0)
        combined_indices = np.concatenate(self.indices, axis=0)
        return combined_vertices, combined_indices

@building_profiler.track_component("mesh_generation")
class OptimizedMeshGenerator:
    """Generates optimized meshes for buildings."""
    
    def __init__(self):
        self.octree: Optional[OctreeNode] = None
        self.batches: Dict[str, GeometryBatch] = {}
        
        # Reusable geometry for common shapes
        self.cube_vertices = np.array([
            # Front face
            [-0.5, -0.5,  0.5],
            [ 0.5, -0.5,  0.5],
            [ 0.5,  0.5,  0.5],
            [-0.5,  0.5,  0.5],
            # Back face
            [-0.5, -0.5, -0.5],
            [ 0.5, -0.5, -0.5],
            [ 0.5,  0.5, -0.5],
            [-0.5,  0.5, -0.5],
        ])
        
        self.cube_indices = np.array([
            # Front
            0, 1, 2, 2, 3, 0,
            # Right
            1, 5, 6, 6, 2, 1,
            # Back
            5, 4, 7, 7, 6, 5,
            # Left
            4, 0, 3, 3, 7, 4,
            # Top
            3, 2, 6, 6, 7, 3,
            # Bottom
            4, 5, 1, 1, 0, 4
        ])
    
    @building_profiler.track_component("spatial_partitioning")
    def initialize_spatial_partitioning(self, bounds: AABB) -> None:
        """Initialize the spatial partitioning structure."""
        self.octree = OctreeNode(bounds)
    
    @building_profiler.track_component("geometry_batching")
    def add_to_batch(
        self,
        vertices: np.ndarray,
        indices: np.ndarray,
        material_id: str
    ) -> None:
        """Add geometry to the appropriate batch."""
        if material_id not in self.batches:
            self.batches[material_id] = GeometryBatch(material_id)
        self.batches[material_id].add_geometry(vertices, indices)
    
    @building_profiler.track_component("mesh_generation")
    def generate_building_mesh(
        self,
        rooms: List[Dict],
        lod: int
    ) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
        """Generate optimized building mesh with LOD support."""
        # Initialize spatial partitioning
        bounds = self._calculate_building_bounds(rooms)
        self.initialize_spatial_partitioning(bounds)
        
        # Process each room
        for room_index, room in enumerate(rooms):
            room_bounds = AABB(
                room['x'], 0, room['y'],
                room['x'] + room['width'], room['height'], room['y'] + room['length']
            )
            
            # Check for potential collisions
            colliding_rooms = self.octree.query(room_bounds) if self.octree else set()
            
            # Generate room geometry based on LOD
            if lod == 1:
                # Basic geometry - just floors and simple walls
                self._generate_basic_room(room, room_index)
            else:
                # Detailed geometry with proper wall segments and openings
                self._generate_detailed_room(room, room_index, colliding_rooms)
            
            # Add room to spatial index
            self.octree.insert((room_bounds, room_index))
        
        # Finalize all batches
        result = {}
        for material_id, batch in self.batches.items():
            result[material_id] = batch.finalize()
        
        return result
    
    def _calculate_building_bounds(self, rooms: List[Dict]) -> AABB:
        """Calculate the overall building bounds."""
        if not rooms:
            return AABB(0, 0, 0, 1, 1, 1)
        
        min_x = min(room['x'] for room in rooms)
        min_y = 0
        min_z = min(room['y'] for room in rooms)
        max_x = max(room['x'] + room['width'] for room in rooms)
        max_y = max(room.get('height', 3) for room in rooms)  # Default height of 3
        max_z = max(room['y'] + room['length'] for room in rooms)
        
        return AABB(min_x, min_y, min_z, max_x, max_y, max_z)
    
    @building_profiler.track_component("basic_geometry")
    def _generate_basic_room(self, room: Dict, room_index: int) -> None:
        """Generate basic room geometry for LOD 1."""
        # Scale and position the floor
        floor_vertices = self.cube_vertices.copy()
        floor_vertices *= [room['width'], 0.1, room['length']]  # Thin floor
        floor_vertices += [room['x'] + room['width']/2, 0, room['y'] + room['length']/2]
        
        # Add to floor batch
        self.add_to_batch(floor_vertices, self.cube_indices, 'floor')
        
        # Simple walls if needed
        wall_height = room.get('height', 3)
        if wall_height > 0:
            # Front and back walls
            for z in [room['y'], room['y'] + room['length']]:
                wall_vertices = self.cube_vertices.copy()
                wall_vertices *= [room['width'], wall_height, 0.1]  # Thin wall
                wall_vertices += [room['x'] + room['width']/2, wall_height/2, z]
                self.add_to_batch(wall_vertices, self.cube_indices, 'wall')
            
            # Left and right walls
            for x in [room['x'], room['x'] + room['width']]:
                wall_vertices = self.cube_vertices.copy()
                wall_vertices *= [0.1, wall_height, room['length']]  # Thin wall
                wall_vertices += [x, wall_height/2, room['y'] + room['length']/2]
                self.add_to_batch(wall_vertices, self.cube_indices, 'wall')
    
    @building_profiler.track_component("detailed_geometry")
    def _generate_detailed_room(
        self,
        room: Dict,
        room_index: int,
        colliding_rooms: Set[int]
    ) -> None:
        """Generate detailed room geometry for LOD 2+."""
        # Generate floor with proper materials and texturing
        floor_vertices = self._generate_floor_geometry(room)
        floor_indices = self._generate_floor_indices(len(floor_vertices))
        self.add_to_batch(floor_vertices, floor_indices, f"floor_{room.get('type', 'default')}")
        
        # Generate walls with openings for doors and windows
        wall_segments = self._generate_wall_segments(room, colliding_rooms)
        for segment in wall_segments:
            vertices, indices = self._generate_wall_geometry(segment)
            self.add_to_batch(vertices, indices, f"wall_{room.get('type', 'default')}")
        
        # Generate ceiling if needed
        if room.get('height', 3) > 0:
            ceiling_vertices = self._generate_ceiling_geometry(room)
            ceiling_indices = self._generate_ceiling_indices(len(ceiling_vertices))
            self.add_to_batch(ceiling_vertices, ceiling_indices, f"ceiling_{room.get('type', 'default')}")
    
    def _generate_floor_geometry(self, room: Dict) -> np.ndarray:
        """Generate detailed floor geometry with proper UVs and materials."""
        # Implementation would include proper UV mapping and material properties
        # For now, return basic geometry
        vertices = self.cube_vertices.copy()
        vertices *= [room['width'], 0.1, room['length']]
        vertices += [room['x'] + room['width']/2, 0, room['y'] + room['length']/2]
        return vertices
    
    def _generate_floor_indices(self, vertex_count: int) -> np.ndarray:
        """Generate indices for floor geometry."""
        return self.cube_indices.copy()
    
    def _generate_wall_segments(
        self,
        room: Dict,
        colliding_rooms: Set[int]
    ) -> List[Dict]:
        """Generate wall segments accounting for doors and windows."""
        # This would include logic for creating wall segments that account for
        # openings and connections to other rooms
        # For now, return basic segments
        segments = []
        wall_height = room.get('height', 3)
        
        # Add four wall segments (simplified)
        segments.extend([
            {
                'start': [room['x'], room['y']],
                'end': [room['x'] + room['width'], room['y']],
                'height': wall_height
            },
            {
                'start': [room['x'] + room['width'], room['y']],
                'end': [room['x'] + room['width'], room['y'] + room['length']],
                'height': wall_height
            },
            {
                'start': [room['x'] + room['width'], room['y'] + room['length']],
                'end': [room['x'], room['y'] + room['length']],
                'height': wall_height
            },
            {
                'start': [room['x'], room['y'] + room['length']],
                'end': [room['x'], room['y']],
                'height': wall_height
            }
        ])
        
        return segments
    
    def _generate_wall_geometry(self, segment: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """Generate geometry for a wall segment."""
        # Calculate wall dimensions
        start = np.array(segment['start'])
        end = np.array(segment['end'])
        direction = end - start
        length = np.linalg.norm(direction)
        direction = direction / length
        
        # Create wall vertices
        vertices = self.cube_vertices.copy()
        vertices *= [length, segment['height'], 0.1]  # Thin wall
        
        # Rotate and position wall
        angle = np.arctan2(direction[1], direction[0])
        rotation_matrix = np.array([
            [np.cos(angle), 0, -np.sin(angle)],
            [0, 1, 0],
            [np.sin(angle), 0, np.cos(angle)]
        ])
        
        vertices = np.dot(vertices, rotation_matrix.T)
        vertices += [
            (start[0] + end[0]) / 2,
            segment['height'] / 2,
            (start[1] + end[1]) / 2
        ]
        
        return vertices, self.cube_indices.copy()
    
    def _generate_ceiling_geometry(self, room: Dict) -> np.ndarray:
        """Generate ceiling geometry."""
        vertices = self.cube_vertices.copy()
        vertices *= [room['width'], 0.1, room['length']]  # Thin ceiling
        vertices += [
            room['x'] + room['width']/2,
            room.get('height', 3),
            room['y'] + room['length']/2
        ]
        return vertices 