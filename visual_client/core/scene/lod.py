from typing import List, Dict, Any, Optional, Callable, Tuple
import math

# --- LOD Data Structures ---

class LODLevel:
    def __init__(self, level: int, mesh: Any, material: Any, distance: float):
        self.level = level  # 0 = highest detail
        self.mesh = mesh
        self.material = material
        self.distance = distance  # Switch to this LOD at this distance or greater

class LODMetadata:
    def __init__(self, levels: List[LODLevel], bias: float = 1.0):
        self.levels = sorted(levels, key=lambda l: l.level)
        self.bias = bias  # Multiplier for LOD switching distance

    def get_lod_for_distance(self, dist: float) -> LODLevel:
        for level in self.levels:
            if dist < level.distance * self.bias:
                return level
        return self.levels[-1]

class LODObject:
    def __init__(self, object_id: str, position: Tuple[float, float, float], lod_metadata: LODMetadata):
        self.object_id = object_id
        self.position = position
        self.lod_metadata = lod_metadata
        self.current_lod: Optional[LODLevel] = None
        self.transitioning = False
        self.transition_callback: Optional[Callable] = None

    def update_lod(self, player_pos: Tuple[float, float, float]):
        dist = math.sqrt(sum((self.position[i] - player_pos[i]) ** 2 for i in range(3)))
        new_lod = self.lod_metadata.get_lod_for_distance(dist)
        if self.current_lod != new_lod:
            self.start_transition(new_lod)

    def start_transition(self, new_lod: LODLevel):
        self.transitioning = True
        # Placeholder: call transition callback or perform alpha blend/morph
        if self.transition_callback:
            self.transition_callback(self, self.current_lod, new_lod)
        self.current_lod = new_lod
        self.transitioning = False

# --- LOD Manager ---

class LODManager:
    def __init__(self, lod_objects: Optional[List[LODObject]] = None, global_bias: float = 1.0):
        self.lod_objects: Dict[str, LODObject] = {obj.object_id: obj for obj in (lod_objects or [])}
        self.global_bias = global_bias

    def add_object(self, obj: LODObject):
        self.lod_objects[obj.object_id] = obj

    def remove_object(self, object_id: str):
        if object_id in self.lod_objects:
            del self.lod_objects[object_id]

    def update_all(self, player_pos: Tuple[float, float, float]):
        for obj in self.lod_objects.values():
            obj.lod_metadata.bias = self.global_bias
            obj.update_lod(player_pos)

    def set_global_bias(self, bias: float):
        self.global_bias = bias

# --- Integration Points ---
# - Partitioning/streaming: update LODs as chunks are loaded/unloaded
# - Transition hooks: allow custom logic for smooth transitions

# --- Example Usage ---
# lod0 = LODLevel(0, mesh0, mat0, 20.0)
# lod1 = LODLevel(1, mesh1, mat1, 50.0)
# lod2 = LODLevel(2, mesh2, mat2, 100.0)
# meta = LODMetadata([lod0, lod1, lod2])
# obj = LODObject('obj1', (10,10,10), meta)
# manager = LODManager([obj])
# manager.update_all(player_pos=(0,0,0)) 