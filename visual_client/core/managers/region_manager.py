"""
RegionManager for large-scale world environments with floating origin support.
Handles region/chunk division, loading/unloading, caching, and integration with coordinate systems.
"""

from typing import Tuple, Dict, Optional, Set, Any, Callable
from collections import OrderedDict
import threading
import logging
from ..utils.coordinates import GlobalCoord, LocalCoord, coordinate_system
from ..utils.floating_origin import FloatingOrigin
from visual_client.core.events.scene_events import SceneEventSystem, SceneEventType

logger = logging.getLogger(__name__)

REGION_SIZE = 1024  # Size of each region in world units (can be tuned)
CACHE_SIZE = 16     # Number of regions to keep in LRU cache

class Region:
    """Represents a world region/chunk."""
    def __init__(self, region_coord: Tuple[int, int]):
        self.region_coord: Tuple[int, int] = region_coord  # (rx, ry)
        self.entities: Set[str] = set()   # Entity IDs in this region
        self.loaded: bool = False
        self.data: Dict[str, Any] = {}    # Arbitrary region data/metadata

    def load(self) -> None:
        self.loaded = True
        logger.debug(f"Region {self.region_coord} loaded.")

    def unload(self) -> None:
        self.loaded = False
        self.entities.clear()
        self.data.clear()
        logger.debug(f"Region {self.region_coord} unloaded.")

class RegionManager:
    """
    Manages world regions/chunks, loading/unloading, caching, and integration with floating origin and event system.
    
    - Handles region transitions as player moves, triggering floating origin updates as needed.
    - Prefetches adjacent regions and unloads distant ones for performance.
    - Maintains an LRU cache of loaded regions for memory efficiency.
    """
    def __init__(self, floating_origin: Optional[FloatingOrigin] = None):
        self.floating_origin: FloatingOrigin = floating_origin or FloatingOrigin()
        self.regions: Dict[Tuple[int, int], Region] = {}
        self.cache: OrderedDict[Tuple[int, int], Region] = OrderedDict()
        self.lock = threading.Lock()
        self.active_region: Optional[Tuple[int, int]] = None
        self.event_system = SceneEventSystem.get_instance()

    def world_to_region_coord(self, pos: GlobalCoord) -> Tuple[int, int]:
        """Convert global world position to region coordinates."""
        rx = int(pos.x // REGION_SIZE)
        ry = int(pos.y // REGION_SIZE)
        return (rx, ry)

    def get_or_create_region(self, region_coord: Tuple[int, int]) -> Region:
        with self.lock:
            if region_coord in self.regions:
                region = self.regions[region_coord]
            else:
                region = Region(region_coord)
                self.regions[region_coord] = region
                self.event_system.emit_scene_event(
                    SceneEventType.REGION_ENTERED,
                    scene_id=None,
                    data={"region_coord": region_coord}
                )
            # LRU cache update
            self.cache[region_coord] = region
            self.cache.move_to_end(region_coord)
            if len(self.cache) > CACHE_SIZE:
                oldest = next(iter(self.cache))
                self.cache[oldest].unload()
                self.event_system.emit_scene_event(
                    SceneEventType.REGION_EXITED,
                    scene_id=None,
                    data={"region_coord": oldest}
                )
                del self.cache[oldest]
            return region

    def update_player_position(self, player_pos: GlobalCoord) -> None:
        """Update region management based on player position."""
        region_coord = self.world_to_region_coord(player_pos)
        if region_coord != self.active_region:
            self._handle_region_transition(region_coord)
        # Prefetch adjacent regions
        self._prefetch_adjacent_regions(region_coord)
        # Unload distant regions
        self._unload_distant_regions(region_coord)

    def _handle_region_transition(self, new_region: Tuple[int, int]) -> None:
        logger.info(f"Transitioning to region {new_region}")
        self.active_region = new_region
        region = self.get_or_create_region(new_region)
        if not region.loaded:
            region.load()
            self.event_system.emit_scene_event(
                SceneEventType.REGION_ENTERED,
                scene_id=None,
                data={"region_coord": new_region}
            )
        # Optionally trigger floating origin shift if needed
        player_global = self.floating_origin.coord_system.origin.get_origin()
        self.floating_origin.update_player_position(player_global)

    def _prefetch_adjacent_regions(self, center: Tuple[int, int]) -> None:
        # Load current and 8 neighbors (3x3 grid)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                coord = (center[0] + dx, center[1] + dy)
                region = self.get_or_create_region(coord)
                if not region.loaded:
                    region.load()
                    self.event_system.emit_scene_event(
                        SceneEventType.REGION_ENTERED,
                        scene_id=None,
                        data={"region_coord": coord}
                    )

    def _unload_distant_regions(self, center: Tuple[int, int]) -> None:
        # Unload regions outside a 3x3 grid
        keep = set((center[0] + dx, center[1] + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1])
        with self.lock:
            for coord, region in list(self.regions.items()):
                if coord not in keep:
                    region.unload()
                    self.event_system.emit_scene_event(
                        SceneEventType.REGION_EXITED,
                        scene_id=None,
                        data={"region_coord": coord}
                    )

    def get_loaded_regions(self) -> Set[Tuple[int, int]]:
        return {coord for coord, region in self.regions.items() if region.loaded}

    def get_region_for_entity(self, entity_pos: GlobalCoord) -> Region:
        region_coord = self.world_to_region_coord(entity_pos)
        return self.get_or_create_region(region_coord)

    def register_entity(self, entity_id: str, entity_pos: GlobalCoord) -> None:
        region = self.get_region_for_entity(entity_pos)
        region.entities.add(entity_id)

    def unregister_entity(self, entity_id: str, entity_pos: GlobalCoord) -> None:
        region = self.get_region_for_entity(entity_pos)
        region.entities.discard(entity_id)

    def clear(self) -> None:
        with self.lock:
            for region in self.regions.values():
                region.unload()
            self.regions.clear()
            self.cache.clear()

    def load_region(self, region_coord: Tuple[int, int]) -> None:
        logger.info(f"Loading region {region_coord}")
        region = self.get_or_create_region(region_coord)
        if not region.loaded:
            region.load()
            self.event_system.emit_scene_event(
                SceneEventType.REGION_ENTERED,
                scene_id=None,
                data={"region_coord": region_coord}
            )

    def unload_region(self, region_coord: Tuple[int, int]) -> None:
        logger.info(f"Unloading region {region_coord}")
        if region_coord in self.regions:
            region = self.regions[region_coord]
            if region.loaded:
                region.unload()
                self.event_system.emit_scene_event(
                    SceneEventType.REGION_EXITED,
                    scene_id=None,
                    data={"region_coord": region_coord}
                )

    def migrate_entity(self, entity_id: str, from_region: Tuple[int, int], to_region: Tuple[int, int]) -> None:
        logger.debug(f"Migrating entity {entity_id} from {from_region} to {to_region}")
        if from_region in self.regions:
            self.regions[from_region].entities.discard(entity_id)
        region = self.get_or_create_region(to_region)
        region.entities.add(entity_id)

    def on_boundary_cross(self, entity_id: str, old_region: Tuple[int, int], new_region: Tuple[int, int]) -> None:
        logger.info(f"Entity {entity_id} crossed from {old_region} to {new_region}")
        self.migrate_entity(entity_id, old_region, new_region)
        self.event_system.emit_scene_event(
            SceneEventType.BOUNDARY_CROSSED,
            scene_id=None,
            data={"entity_id": entity_id, "from": old_region, "to": new_region}
        )

# For integration/testing
region_manager = RegionManager() 