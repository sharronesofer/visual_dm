from typing import List, Dict, Any, Optional, Callable, Tuple
import math
import logging

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

# --- LOD Hardware Tier Configuration ---

class LODConfig:
    # Example recommended values; these can be tuned based on profiling
    TIERS = {
        'low':    {'bias': 1.5, 'distances': [10.0, 30.0, 60.0]},
        'medium': {'bias': 1.0, 'distances': [20.0, 50.0, 100.0]},
        'high':   {'bias': 0.8, 'distances': [30.0, 80.0, 160.0]},
    }

    @staticmethod
    def get_config(tier: str):
        return LODConfig.TIERS.get(tier, LODConfig.TIERS['medium'])

# --- LOD Manager ---

class LODManager:
    def __init__(self, lod_objects: Optional[List[LODObject]] = None, global_bias: float = 1.0, hardware_tier: str = 'medium', debug: bool = False):
        """
        Manages LODObjects and their transitions. Supports runtime debug logging and profiling.
        Args:
            lod_objects: List of LODObject instances to manage.
            global_bias: Bias applied to all LOD calculations.
            hardware_tier: Hardware tier string ('low', 'medium', 'high').
            debug: If True, enables logging of LOD transitions and config changes.
        """
        self.lod_objects = lod_objects or []
        self.global_bias = global_bias
        self.hardware_tier = hardware_tier
        self.debug = debug
        if self.debug:
            logging.info(f"LODManager initialized with hardware_tier={hardware_tier}, global_bias={global_bias}")
        config = LODConfig.get_config(hardware_tier)
        self.default_distances = config['distances']
        self._frame_time_history: List[float] = []
        self._dynamic_lod_active = False
        self._dynamic_lod_hysteresis = 5  # Number of frames to confirm before switching
        self._dynamic_lod_counter = 0
        self._dynamic_lod_last_state = None

    def add_object(self, obj: LODObject):
        """Add a new LODObject to be managed."""
        self.lod_objects.append(obj)
        if self.debug:
            logging.info(f"Added LODObject {obj.object_id}")

    def remove_object(self, object_id: str):
        """Remove an LODObject by its ID."""
        self.lod_objects = [obj for obj in self.lod_objects if obj.object_id != object_id]
        if self.debug:
            logging.info(f"Removed LODObject {object_id}")

    def update_all(self, player_pos: Tuple[float, float, float]):
        """
        Update LOD for all managed objects based on player position.
        Logs LOD transitions if debug is enabled.
        """
        for obj in self.lod_objects:
            old_lod = getattr(obj, 'current_lod', None)
            obj.update_lod(player_pos)
            new_lod = getattr(obj, 'current_lod', None)
            if self.debug and old_lod != new_lod:
                logging.info(f"LOD transition for {obj.object_id}: {old_lod} -> {new_lod} at distance {self._distance(obj.position, player_pos):.2f} (tier={self.hardware_tier}, bias={self.global_bias})")

    def set_global_bias(self, bias: float):
        """Set the global LOD bias and log the change if debug is enabled."""
        self.global_bias = bias
        if self.debug:
            logging.info(f"Global LOD bias set to {bias}")

    def set_hardware_tier(self, tier: str):
        """
        Set the hardware tier and update bias/distances accordingly.
        Logs the change if debug is enabled.
        """
        config = LODConfig.get_config(tier)
        self.hardware_tier = tier
        self.global_bias = config['bias']
        if self.debug:
            logging.info(f"Hardware tier set to {tier}, bias updated to {self.global_bias}")
        # Optionally update all LODMetadata distances
        for obj in self.lod_objects:
            for i, level in enumerate(obj.lod_metadata.levels):
                if i < len(self.default_distances):
                    level.distance = self.default_distances[i]

    def print_lod_summary(self):
        """
        Print a summary of current LODs for all managed objects.
        Useful for debugging and profiling.
        """
        for obj in self.lod_objects:
            lod = getattr(obj, 'current_lod', None)
            print(f"Object {obj.object_id}: LOD={lod}")

    @staticmethod
    def _distance(pos1: Tuple[float, float, float], pos2: Tuple[float, float, float]) -> float:
        """Compute Euclidean distance between two 3D points."""
        return sum((a - b) ** 2 for a, b in zip(pos1, pos2)) ** 0.5

    def update_dynamic_lod(self, frame_time: float, min_fps: float = 30.0, bias_step: float = 0.2, max_bias: float = 2.0, min_bias: float = 0.5):
        """
        Dynamically adjust LOD bias based on recent frame time (ms).
        If frame time exceeds threshold (1/min_fps), increase bias (lower LOD); if well below, decrease bias (raise LOD).
        Uses hysteresis to avoid oscillation.
        Args:
            frame_time: Current frame time in milliseconds.
            min_fps: Minimum target FPS (default 30).
            bias_step: Amount to adjust bias per change.
            max_bias: Maximum allowed bias.
            min_bias: Minimum allowed bias.
        """
        threshold = 1000.0 / min_fps
        self._frame_time_history.append(frame_time)
        if len(self._frame_time_history) > self._dynamic_lod_hysteresis:
            self._frame_time_history.pop(0)
        over_threshold = all(ft > threshold for ft in self._frame_time_history)
        under_threshold = all(ft < threshold * 0.85 for ft in self._frame_time_history)
        if over_threshold and (self._dynamic_lod_last_state != 'over'):
            # Increase bias (lower LOD)
            old_bias = self.global_bias
            self.global_bias = min(self.global_bias + bias_step, max_bias)
            self._dynamic_lod_last_state = 'over'
            if self.debug:
                logging.info(f"[DynamicLOD] Frame time high ({frame_time:.1f}ms > {threshold:.1f}ms). Increasing LOD bias: {old_bias:.2f} -> {self.global_bias:.2f}")
        elif under_threshold and (self._dynamic_lod_last_state != 'under'):
            # Decrease bias (raise LOD)
            old_bias = self.global_bias
            self.global_bias = max(self.global_bias - bias_step, min_bias)
            self._dynamic_lod_last_state = 'under'
            if self.debug:
                logging.info(f"[DynamicLOD] Frame time low ({frame_time:.1f}ms < {threshold*0.85:.1f}ms). Decreasing LOD bias: {old_bias:.2f} -> {self.global_bias:.2f}")

# --- Integration Points ---
# - Partitioning/streaming: update LODs as chunks are loaded/unloaded
# - Transition hooks: allow custom logic for smooth transitions

# --- Example Usage ---
# lod0 = LODLevel(0, mesh0, mat0, 20.0)
# lod1 = LODLevel(1, mesh1, mat1, 50.0)
# lod2 = LODLevel(2, mesh2, mat2, 100.0)
# meta = LODMetadata([lod0, lod1, lod2])
# obj = LODObject('obj1', (10,10,10), meta)
# manager = LODManager([obj], hardware_tier='low')
# manager.update_all(player_pos=(0,0,0))
# manager.set_hardware_tier('high')  # Dynamically adjust for new hardware 

# --- Test Utility for Profiling and Debugging ---
def test_lod_manager_debug():
    """
    Test utility to simulate LOD transitions and print debug output.
    Usage: Call this function in __main__ or a test script to verify LODManager profiling features.
    """
    # Example LOD levels
    levels = [
        LODLevel(level=0, mesh=None, material=None, distance=10.0),
        LODLevel(level=1, mesh=None, material=None, distance=30.0),
        LODLevel(level=2, mesh=None, material=None, distance=60.0),
    ]
    metadata = LODMetadata(levels=levels, bias=1.0)
    # Create objects at different positions
    objs = [
        LODObject(object_id=f"obj_{i}", position=(i*20.0, 0.0, 0.0), lod_metadata=metadata) for i in range(3)
    ]
    # Instantiate manager with debug enabled
    manager = LODManager(lod_objects=objs, hardware_tier='medium', debug=True)
    # Simulate player movement
    for player_x in [0.0, 15.0, 35.0, 55.0]:
        print(f"\nPlayer at x={player_x}")
        manager.update_all((player_x, 0.0, 0.0))
        manager.print_lod_summary()

# Uncomment to run test utility
# if __name__ == "__main__":
#     test_lod_manager_debug() 