"""
EntityPositionManager for handling entity positions and velocities during floating origin shifts.
Integrates with RegionManager and FloatingOrigin for seamless world management.

---
Implementation Plan for Batched Spatial Index Updates (Task #352):

- Batching/Deferred Update System:
    - Entity position updates are queued and processed in batches, reducing per-update overhead.
    - Batch size and flush interval are configurable via config.json (spatial_indexing section).
    - Critical updates (e.g., visible or gameplay-relevant entities) are prioritized and flushed immediately.
    - Non-critical updates may be deferred/skipped under high load.
    - Predictive update and spatial locality stubs are included for future optimization.

- Adaptive Thresholds:
    - If the update queue grows too large, the system enters adaptive mode, increasing batch size and flush frequency.
    - When load subsides, settings revert to config values.

- Monitoring/Performance Metrics:
    - Integration with MonitoringManager records flush time, queue size, skipped updates, and other metrics.
    - Metrics are available for in-game monitoring and post-playtest analysis.

- Dynamic Configuration:
    - Settings can be reloaded at runtime (e.g., after config file change) without restarting the system.

- Thread Safety:
    - All critical sections are protected by locks.

- Extensibility:
    - Stubs for predictive updates and spatial locality-aware batching are included for future research/optimization.

Rationale:
- These enhancements ensure the spatial indexing system can handle high-entity movement scenarios efficiently, avoid performance spikes, and provide robust monitoring for tuning and debugging.
---
"""

from typing import Dict, Callable, Tuple, Any, Optional, Set
import threading
import logging
from ..utils.coordinates import GlobalCoord
from ..utils.floating_origin import FloatingOrigin
from .region_manager import RegionManager
import time
from queue import Queue
from .config_manager import ConfigManager
from .monitoring_manager import MonitoringManager

logger = logging.getLogger(__name__)

class EntityInfo:
    """Stores entity position/velocity accessors and metadata."""
    def __init__(self, entity_id: str, get_pos: Callable[[], GlobalCoord], set_pos: Callable[[float, float, float], None],
                 get_vel: Optional[Callable[[], Tuple[float, float, float]]] = None,
                 set_vel: Optional[Callable[[float, float, float], None]] = None,
                 on_region_change: Optional[Callable[[Tuple[int, int]], None]] = None):
        self.entity_id = entity_id
        self.get_pos = get_pos
        self.set_pos = set_pos
        self.get_vel = get_vel
        self.set_vel = set_vel
        self.on_region_change = on_region_change
        self.current_region: Optional[Tuple[int, int]] = None

class EntityPositionManager:
    """
    Manages all entities that require position/velocity updates during origin shifts.
    Handles registration, batch updates, region boundary detection, and debugging.
    Now supports dynamic batching, deferred updates, adaptive thresholds, and performance monitoring.
    
    Thread safety is ensured via locks. Configuration can be reloaded at runtime.
    """
    def __init__(self, region_manager: Optional[RegionManager] = None, floating_origin: Optional[FloatingOrigin] = None, batch_size: int = None, flush_interval: float = None):
        self.region_manager = region_manager or RegionManager()
        self.floating_origin = floating_origin or FloatingOrigin()
        self.entities: Dict[str, EntityInfo] = {}
        self.lock = threading.Lock()
        self._update_queue = Queue()
        # Load config
        self.config_manager = ConfigManager()
        self._load_settings(batch_size, flush_interval)
        self._last_flush = time.time()
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self._batch_update_worker, daemon=True)
        self._monitor_thread.start()
        self._metrics = {'flush_count': 0, 'max_queue': 0, 'last_flush_time': 0.0, 'skipped_updates': 0}
        # Monitoring
        self.monitoring_enabled = self.config_manager.get('spatial_indexing.enable_performance_monitoring', True)
        self.monitoring_manager = MonitoringManager() if self.monitoring_enabled else None
        self._adaptive_mode = False
        self._adaptive_increase_factor = 2
        self._adaptive_threshold = 4 * self.batch_size

    def _load_settings(self, batch_size, flush_interval):
        cfg = self.config_manager.get('spatial_indexing', {})
        self.batch_size = batch_size or cfg.get('batch_size', 128)
        self.flush_interval = flush_interval or cfg.get('flush_interval', 0.05)
        self.update_frequency = cfg.get('update_frequency', 60)

    def reload_settings(self):
        """Reload batching and monitoring settings from config file at runtime."""
        self._load_settings(None, None)
        self.monitoring_enabled = self.config_manager.get('spatial_indexing.enable_performance_monitoring', True)
        if self.monitoring_enabled and not self.monitoring_manager:
            self.monitoring_manager = MonitoringManager()
        elif not self.monitoring_enabled:
            self.monitoring_manager = None
        logger.info(f"EntityPositionManager settings reloaded: batch_size={self.batch_size}, flush_interval={self.flush_interval}, monitoring={self.monitoring_enabled}")

    def register_entity(self, entity_id: str, get_pos: Callable[[], GlobalCoord], set_pos: Callable[[float, float, float], None],
                        get_vel: Optional[Callable[[], Tuple[float, float, float]]] = None,
                        set_vel: Optional[Callable[[float, float, float], None]] = None,
                        on_region_change: Optional[Callable[[Tuple[int, int]], None]] = None):
        logger.info(f"Registering entity {entity_id}")
        info = EntityInfo(entity_id, get_pos, set_pos, get_vel, set_vel, on_region_change)
        with self.lock:
            self.entities[entity_id] = info
        # Assign to region
        pos = get_pos()
        region = self.region_manager.world_to_region_coord(pos)
        info.current_region = region
        self.region_manager.register_entity(entity_id, pos)

    def unregister_entity(self, entity_id: str):
        logger.info(f"Unregistering entity {entity_id}")
        with self.lock:
            info = self.entities.pop(entity_id, None)
        if info:
            self.region_manager.unregister_entity(entity_id, info.get_pos())

    def update_all_for_origin_shift(self, dx: float, dy: float, dz: float):
        logger.info(f"Updating all entities for origin shift: dx={dx}, dy={dy}, dz={dz}")
        with self.lock:
            for info in self.entities.values():
                # Update position
                info.set_pos(-dx, -dy, -dz)
                # Update velocity if applicable
                if info.get_vel and info.set_vel:
                    vx, vy, vz = info.get_vel()
                    info.set_vel(vx, vy, vz)  # No change for velocity in shift, but placeholder for custom logic
                # Check for region boundary crossing
                new_pos = info.get_pos()
                new_region = self.region_manager.world_to_region_coord(new_pos)
                if new_region != info.current_region:
                    self.region_manager.unregister_entity(info.entity_id, new_pos)
                    self.region_manager.register_entity(info.entity_id, new_pos)
                    if info.on_region_change:
                        info.on_region_change(new_region)
                    info.current_region = new_region
                logger.debug(f"Entity {info.entity_id} updated for origin shift to region {new_region}")

    def handle_origin_shift(self, delta: Tuple[float, float, float]):
        """Callback for FloatingOrigin to update all entities."""
        dx, dy, dz = delta
        self.update_all_for_origin_shift(dx, dy, dz)

    def enable_debug(self, enabled: bool = True):
        if enabled:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    def get_registered_entities(self) -> Set[str]:
        with self.lock:
            return set(self.entities.keys())

    def update_entity_position(self, entity_id, dx, dy, dz):
        logger.debug(f"Updating position for entity {entity_id} by ({dx}, {dy}, {dz})")
        # ... existing code ...

    def queue_entity_update(self, entity_id: str, dx: float, dy: float, dz: float, critical: bool = False, predicted: bool = False):
        """Queue an entity position update. Critical entities are prioritized. Predicted updates are for predictive batching."""
        # Predictive update stub (future: use movement trends to pre-queue updates)
        self._update_queue.put((entity_id, dx, dy, dz, critical, predicted))
        qsize = self._update_queue.qsize()
        if qsize > self._metrics['max_queue']:
            self._metrics['max_queue'] = qsize
        # Adaptive threshold: if overloaded, increase batch size or flush faster
        if qsize >= self._adaptive_threshold and not self._adaptive_mode:
            self._adaptive_mode = True
            self.batch_size *= self._adaptive_increase_factor
            self.flush_interval = max(self.flush_interval / self._adaptive_increase_factor, 0.01)
            logger.warning(f"Adaptive mode enabled: batch_size={self.batch_size}, flush_interval={self.flush_interval}")
        elif qsize < self.batch_size and self._adaptive_mode:
            self._adaptive_mode = False
            self._load_settings(None, None)  # Reset to config values
            logger.info(f"Adaptive mode disabled: batch_size={self.batch_size}, flush_interval={self.flush_interval}")
        # Optionally flush immediately for critical entities
        if critical or qsize >= self.batch_size:
            self._flush_update_queue()

    def _batch_update_worker(self):
        """Background worker to flush the update queue at intervals."""
        while not self._stop_event.is_set():
            now = time.time()
            if not self._update_queue.empty() and (now - self._last_flush >= self.flush_interval):
                self._flush_update_queue()
            time.sleep(0.01)

    def _flush_update_queue(self):
        """Flush the update queue and process all pending updates in a batch. Implements multi-level update and spatial locality stubs."""
        updates = []
        while not self._update_queue.empty() and len(updates) < self.batch_size:
            try:
                updates.append(self._update_queue.get_nowait())
            except Exception:
                break
        if not updates:
            return
        start = time.time()
        skipped = 0
        with self.lock:
            # Multi-level update: process critical first, then non-critical, spatial locality stub
            critical_updates = [u for u in updates if u[4]]
            non_critical_updates = [u for u in updates if not u[4]]
            # TODO: In future, sort non_critical_updates by spatial locality or predicted need
            for entity_id, dx, dy, dz, critical, predicted in critical_updates + non_critical_updates:
                if entity_id in self.entities:
                    info = self.entities[entity_id]
                    # Deferred update: non-critical entities may be skipped if system is overloaded
                    if not critical and self._metrics['max_queue'] > 2 * self.batch_size:
                        skipped += 1
                        continue  # Defer non-critical update
                    info.set_pos(dx, dy, dz)
                    # Region/other logic as before
                    new_pos = info.get_pos()
                    new_region = self.region_manager.world_to_region_coord(new_pos)
                    if new_region != info.current_region:
                        self.region_manager.unregister_entity(info.entity_id, new_pos)
                        self.region_manager.register_entity(info.entity_id, new_pos)
                        if info.on_region_change:
                            info.on_region_change(new_region)
                        info.current_region = new_region
                    logger.debug(f"Entity {info.entity_id} batch-updated to region {new_region}")
        self._last_flush = time.time()
        self._metrics['flush_count'] += 1
        self._metrics['last_flush_time'] = self._last_flush - start
        self._metrics['skipped_updates'] += skipped
        if self.monitoring_manager:
            self.monitoring_manager.record_metric('spatial_index_flush_time', self._metrics['last_flush_time'], {'type': 'entity_batch'})
            self.monitoring_manager.record_metric('spatial_index_flush_count', self._metrics['flush_count'])
            self.monitoring_manager.record_metric('spatial_index_max_queue', self._metrics['max_queue'])
            self.monitoring_manager.record_metric('spatial_index_skipped_updates', skipped)
        logger.info(f"Flushed {len(updates)} entity updates in {self._metrics['last_flush_time']:.4f}s (queue max: {self._metrics['max_queue']}, skipped: {skipped})")
        self._metrics['max_queue'] = 0

    def stop_batch_worker(self):
        """Stop the background batch update worker."""
        self._stop_event.set()
        self._monitor_thread.join()

    def get_update_metrics(self):
        """Return current batching/deferred update metrics."""
        metrics = dict(self._metrics)
        if self.monitoring_manager:
            stats = self.monitoring_manager.get_metric_statistics('spatial_index_flush_time')
            metrics['flush_time_stats'] = stats
        return metrics

# For integration/testing
entity_position_manager = EntityPositionManager() 