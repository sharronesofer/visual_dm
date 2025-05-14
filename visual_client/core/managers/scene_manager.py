"""
Scene management system with aggressive memory management.

NOTE: This module is floating origin aware. All rendering and (future) physics systems must use local coordinates relative to the current floating origin. Integration points for physics engines are stubbed and documented below.
"""

import pygame
import logging
import time
import gc
import os
import psutil
from threading import Thread, Lock
from queue import Queue, PriorityQueue
from typing import Dict, List, Set, Tuple, Optional, Any, Callable, Union
from enum import Enum, auto
from pathlib import Path
from .error_handler import handle_component_error, ErrorSeverity
from .asset_manager import AssetManager
from visual_client.core.events.scene_events import SceneEventSystem, SceneEventType, SceneEvent, create_event

logger = logging.getLogger(__name__)

class AssetPriority(Enum):
    """Priority levels for asset management."""
    CRITICAL = 0    # Core assets that should never be unloaded
    HIGH = 1        # Important assets actively used in scene
    MEDIUM = 2      # Assets that might be used soon
    LOW = 3         # Background assets not actively used
    CACHE = 4       # Assets kept only in cache for quick reloading

class UnloadStrategy(Enum):
    """Strategies for asset unloading."""
    TIME_BASED = auto()      # Unload based on time since last use
    DISTANCE_BASED = auto()  # Unload based on distance from player/camera
    PRIORITY_BASED = auto()  # Unload based on asset priority
    MEMORY_PRESSURE = auto() # Unload based on system memory pressure
    COMBINED = auto()        # Use a combination of strategies

class MemoryThreshold:
    """Memory usage thresholds for triggering actions."""
    WARNING = 0.75   # 75% of budget - issue warning
    CRITICAL = 0.85  # 85% of budget - aggressive unloading
    EMERGENCY = 0.95 # 95% of budget - emergency measures

class SceneAsset:
    """Represents an asset used in a scene with metadata for memory management."""
    
    def __init__(
        self,
        asset_id: str,
        asset_type: str,
        asset: Any,
        size: int,
        priority: AssetPriority = AssetPriority.MEDIUM,
        scene_id: Optional[str] = None
    ):
        """Initialize a scene asset.
        
        Args:
            asset_id: Unique identifier for the asset
            asset_type: Type of asset (texture, model, sound, etc.)
            asset: The actual asset object
            size: Size of the asset in bytes
            priority: Asset priority for unloading decisions
            scene_id: ID of the scene using this asset
        """
        self.asset_id = asset_id
        self.asset_type = asset_type
        self.asset = asset
        self.size = size
        self.priority = priority
        self.scene_id = scene_id
        self.last_used = time.time()
        self.ref_count = 1
        self.position = (0, 0)  # Position in world space (if applicable)
        self.loaded = True
        self.unload_callback = None
        
    def use(self) -> None:
        """Mark the asset as used, updating last used time."""
        self.last_used = time.time()
        
    def increment_ref(self) -> int:
        """Increment reference count and return new count."""
        self.ref_count += 1
        return self.ref_count
        
    def decrement_ref(self) -> int:
        """Decrement reference count and return new count."""
        if self.ref_count > 0:
            self.ref_count -= 1
        return self.ref_count
    
    def set_position(self, x: float, y: float) -> None:
        """Set asset position for distance-based unloading."""
        self.position = (x, y)
    
    def get_time_since_use(self) -> float:
        """Get time in seconds since last use."""
        return time.time() - self.last_used
    
    def set_unload_callback(self, callback: Callable) -> None:
        """Set callback to be called when asset is unloaded."""
        self.unload_callback = callback
    
    def unload(self) -> bool:
        """Unload the asset to free memory.
        
        Returns:
            bool: True if unloaded successfully, False if couldn't unload
        """
        if not self.loaded or self.ref_count > 0:
            return False
            
        try:
            if self.unload_callback:
                self.unload_callback(self.asset_id, self.asset)
            
            self.asset = None
            self.loaded = False
            return True
        except Exception as e:
            logger.error(f"Failed to unload asset {self.asset_id}: {e}")
            return False
            
    def reload(self, asset: Any) -> bool:
        """Reload the asset if it was unloaded.
        
        Args:
            asset: The reloaded asset
            
        Returns:
            bool: True if reloaded successfully
        """
        if self.loaded:
            return False
            
        self.asset = asset
        self.loaded = True
        self.last_used = time.time()
        return True

class MemoryBudget:
    """Manages memory budget and tracking for scene assets."""
    
    def __init__(self, total_budget_mb: float = 0):
        """Initialize memory budget.
        
        Args:
            total_budget_mb: Total memory budget in MB (0 for auto-detect)
        """
        self.lock = Lock()
        
        # Auto-detect system memory if not specified
        if total_budget_mb <= 0:
            system_memory = psutil.virtual_memory().total
            # Use 25% of system memory by default
            total_budget_mb = system_memory / (1024 * 1024) * 0.25
            
        self.total_budget = total_budget_mb * 1024 * 1024  # Convert to bytes
        self.used_memory = 0
        self.peak_memory = 0
        self.asset_sizes: Dict[str, int] = {}
        self.per_scene_usage: Dict[str, int] = {}
        self.per_type_usage: Dict[str, int] = {}
        self.warning_callbacks: List[Callable] = []
        self.critical_callbacks: List[Callable] = []
        
    def register_asset(self, asset_id: str, scene_id: str, asset_type: str, size: int) -> None:
        """Register an asset and its memory usage.
        
        Args:
            asset_id: Asset identifier
            scene_id: Scene identifier
            asset_type: Type of asset
            size: Size of asset in bytes
        """
        with self.lock:
            self.asset_sizes[asset_id] = size
            self.used_memory += size
            
            # Update scene usage
            if scene_id not in self.per_scene_usage:
                self.per_scene_usage[scene_id] = 0
            self.per_scene_usage[scene_id] += size
            
            # Update type usage
            if asset_type not in self.per_type_usage:
                self.per_type_usage[asset_type] = 0
            self.per_type_usage[asset_type] += size
            
            # Update peak memory
            if self.used_memory > self.peak_memory:
                self.peak_memory = self.used_memory
                
            # Check thresholds
            self._check_thresholds()
                
    def unregister_asset(self, asset_id: str, scene_id: str, asset_type: str) -> int:
        """Unregister an asset and free its memory allocation.
        
        Args:
            asset_id: Asset identifier
            scene_id: Scene identifier
            asset_type: Type of asset
            
        Returns:
            int: Amount of memory freed in bytes
        """
        with self.lock:
            if asset_id not in self.asset_sizes:
                return 0
                
            size = self.asset_sizes[asset_id]
            self.used_memory -= size
            
            # Update scene usage
            if scene_id in self.per_scene_usage:
                self.per_scene_usage[scene_id] = max(0, self.per_scene_usage[scene_id] - size)
                
            # Update type usage
            if asset_type in self.per_type_usage:
                self.per_type_usage[asset_type] = max(0, self.per_type_usage[asset_type] - size)
                
            del self.asset_sizes[asset_id]
            return size
            
    def get_usage_fraction(self) -> float:
        """Get fraction of memory budget used (0.0 to 1.0)."""
        with self.lock:
            return self.used_memory / self.total_budget if self.total_budget > 0 else 0
            
    def get_memory_pressure(self) -> float:
        """Get memory pressure (0.0 to 1.0) based on system memory."""
        system_memory = psutil.virtual_memory()
        return system_memory.percent / 100.0
        
    def register_warning_callback(self, callback: Callable) -> None:
        """Register callback for warning threshold."""
        self.warning_callbacks.append(callback)
        
    def register_critical_callback(self, callback: Callable) -> None:
        """Register callback for critical threshold."""
        self.critical_callbacks.append(callback)
        
    def get_scene_usage(self, scene_id: str) -> int:
        """Get memory usage for a specific scene in bytes."""
        with self.lock:
            return self.per_scene_usage.get(scene_id, 0)
            
    def get_type_usage(self, asset_type: str) -> int:
        """Get memory usage for a specific asset type in bytes."""
        with self.lock:
            return self.per_type_usage.get(asset_type, 0)
            
    def get_usage_report(self) -> Dict[str, Any]:
        """Get detailed memory usage report."""
        with self.lock:
            return {
                "total_budget_mb": self.total_budget / (1024 * 1024),
                "used_memory_mb": self.used_memory / (1024 * 1024),
                "peak_memory_mb": self.peak_memory / (1024 * 1024),
                "usage_fraction": self.get_usage_fraction(),
                "asset_count": len(self.asset_sizes),
                "per_scene_usage_mb": {
                    scene: usage / (1024 * 1024)
                    for scene, usage in self.per_scene_usage.items()
                },
                "per_type_usage_mb": {
                    asset_type: usage / (1024 * 1024)
                    for asset_type, usage in self.per_type_usage.items()
                }
            }
            
    def _check_thresholds(self) -> None:
        """Check memory thresholds and trigger callbacks if needed."""
        usage_fraction = self.get_usage_fraction()
        
        if usage_fraction >= MemoryThreshold.CRITICAL:
            for callback in self.critical_callbacks:
                try:
                    callback(usage_fraction)
                except Exception as e:
                    logger.error(f"Error in critical memory callback: {e}")
                    
        elif usage_fraction >= MemoryThreshold.WARNING:
            for callback in self.warning_callbacks:
                try:
                    callback(usage_fraction)
                except Exception as e:
                    logger.error(f"Error in warning memory callback: {e}")

class SceneManager:
    """
    Manages scenes with aggressive memory management, asset reference counting, unloading strategies, and LOD-aware asset management.
    Integrates with chunk streaming and asset LOD systems.
    """
    
    def __init__(
        self,
        asset_manager: Optional[AssetManager] = None,
        memory_budget_mb: float = 0,
        streaming_enabled: bool = True,
        auto_unload: bool = True
    ):
        """Initialize the scene manager.
        
        Args:
            asset_manager: Asset manager for loading assets
            memory_budget_mb: Memory budget in MB (0 for auto-detect)
            streaming_enabled: Whether to enable asset streaming
            auto_unload: Whether to automatically unload unused assets
        """
        # Initialize managers
        self.asset_manager = asset_manager
        self.memory_budget = MemoryBudget(memory_budget_mb)
        
        # Scene management
        self.scenes: Dict[str, Dict[str, Any]] = {}
        self.active_scene: Optional[str] = None
        self.preloaded_scenes: Set[str] = set()
        self.scene_assets: Dict[str, Dict[str, SceneAsset]] = {}  # scene_id -> {asset_id -> asset}
        self.global_assets: Dict[str, SceneAsset] = {}  # Shared across scenes
        
        # Asset reference tracking
        self.asset_references: Dict[str, Set[str]] = {}  # asset_id -> set of scene_ids
        
        # Memory management
        self.streaming_enabled = streaming_enabled
        self.auto_unload = auto_unload
        self.unload_strategy = UnloadStrategy.COMBINED
        self.time_threshold = 60  # Seconds of inactivity before unloading
        self.asset_queue = PriorityQueue()  # Priority queue for asset loading
        
        # Legacy event callbacks (for backward compatibility)
        self.event_callbacks: Dict[str, List[Callable]] = {}
        
        # Initialize Event System integration
        self.event_system = SceneEventSystem.get_instance()
        
        # Initialize worker threads
        self.loading_thread: Optional[Thread] = None
        self.unloading_thread: Optional[Thread] = None
        self.monitoring_thread: Optional[Thread] = None
        self.running = False
        self.thread_lock = Lock()
        
        # Register callbacks
        self.memory_budget.register_warning_callback(self._on_memory_warning)
        self.memory_budget.register_critical_callback(self._on_memory_critical)
        
        # Start memory management
        self._start_worker_threads()
        
        logger.info("Scene Manager initialized")
        
        self.scene_loader_manager = None  # type: Optional[Any]
        self.lod_thresholds = (200.0, 600.0)  # (high/med, med/low)

    def _start_worker_threads(self) -> None:
        """Start worker threads for asset loading and unloading."""
        self.running = True
        
        # Start loading thread
        self.loading_thread = Thread(target=self._loading_worker, daemon=True)
        self.loading_thread.start()
        
        # Start unloading thread
        if self.auto_unload:
            self.unloading_thread = Thread(target=self._unloading_worker, daemon=True)
            self.unloading_thread.start()
            
        # Start monitoring thread
        self.monitoring_thread = Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        
        logger.debug("Scene Manager worker threads started")
    
    def register_scene(self, scene_id: str, scene_data: Dict[str, Any]) -> None:
        """Register a scene with the scene manager.
        
        Args:
            scene_id: Unique identifier for the scene
            scene_data: Scene configuration data
        """
        try:
            if scene_id in self.scenes:
                logger.warning(f"Scene {scene_id} already registered, updating")
                
            # Initialize scene asset tracking
            if scene_id not in self.scene_assets:
                self.scene_assets[scene_id] = {}
                
            # Store scene configuration
            self.scenes[scene_id] = scene_data
            
            # Initialize asset manifest if provided
            if "asset_manifest" in scene_data:
                self._register_scene_assets(scene_id, scene_data["asset_manifest"])
                
            logger.info(f"Registered scene: {scene_id}")
            
            # Emit scene registered event
            self.event_system.emit_scene_event(
                SceneEventType.SCENE_REGISTERED,
                scene_id=scene_id,
                data={"scene_data": scene_data}
            )
            
        except Exception as e:
            handle_component_error(
                "SceneManager",
                "register_scene",
                e,
                ErrorSeverity.ERROR,
                {"scene_id": scene_id}
            )
    
    def unregister_scene(self, scene_id: str) -> None:
        """Unregister a scene from the scene manager.
        
        Args:
            scene_id: Scene identifier to unregister
        """
        try:
            if scene_id not in self.scenes:
                logger.warning(f"Scene {scene_id} not registered")
                return
                
            # Unload scene assets
            self._unload_scene_assets(scene_id)
            
            # Clean up tracking
            if scene_id in self.scene_assets:
                del self.scene_assets[scene_id]
                
            if scene_id in self.preloaded_scenes:
                self.preloaded_scenes.remove(scene_id)
                
            # Remove scene configuration
            scene_data = self.scenes[scene_id]
            del self.scenes[scene_id]
            
            logger.info(f"Unregistered scene: {scene_id}")
            
            # Emit scene unregistered event
            self.event_system.emit_scene_event(
                SceneEventType.SCENE_UNREGISTERED,
                scene_id=scene_id,
                data={"scene_data": scene_data}
            )
            
        except Exception as e:
            handle_component_error(
                "SceneManager",
                "unregister_scene",
                e,
                ErrorSeverity.ERROR,
                {"scene_id": scene_id}
            )
    
    def preload_scene(self, scene_id: str, priority: int = 1) -> None:
        """Preload a scene's assets in the background.
        
        Args:
            scene_id: Scene identifier to preload
            priority: Loading priority (lower is higher priority)
        """
        try:
            if scene_id not in self.scenes:
                logger.warning(f"Scene {scene_id} not registered")
                return
                
            scene_data = self.scenes[scene_id]
            
            # Check if scene has an asset manifest
            if "asset_manifest" in scene_data:
                manifest = scene_data["asset_manifest"]
                
                # Queue assets for loading
                for asset_type, assets in manifest.items():
                    for asset_info in assets:
                        asset_id = asset_info["id"]
                        asset_priority = priority
                        
                        # Queue for loading
                        self.asset_queue.put((asset_priority, (scene_id, asset_id, asset_type, asset_info)))
                
            # Mark scene as preloaded
            self.preloaded_scenes.add(scene_id)
            
            logger.info(f"Preloading scene: {scene_id}")
            
            # Emit scene preloaded event
            self.event_system.emit_scene_event(
                SceneEventType.SCENE_PRELOADED,
                scene_id=scene_id,
                data={"priority": priority}
            )
            
        except Exception as e:
            handle_component_error(
                "SceneManager",
                "preload_scene",
                e,
                ErrorSeverity.ERROR,
                {"scene_id": scene_id}
            )
    
    def activate_scene(self, scene_id: str) -> bool:
        """Activate a scene, making it the current active scene.
        
        Args:
            scene_id: Scene identifier to activate
            
        Returns:
            bool: True if scene activated successfully
        """
        try:
            if scene_id not in self.scenes:
                logger.warning(f"Scene {scene_id} not registered")
                return False
                
            # Deactivate current scene
            if self.active_scene:
                self._on_scene_deactivated(self.active_scene)
                
            # Set new active scene
            prev_scene = self.active_scene
            self.active_scene = scene_id
            
            # Ensure scene assets are loaded
            if scene_id not in self.preloaded_scenes:
                self.preload_scene(scene_id, priority=0)  # Highest priority
                
            # Trigger activated event
            self._on_scene_activated(scene_id, prev_scene)
            
            logger.info(f"Activated scene: {scene_id}")
            return True
            
        except Exception as e:
            handle_component_error(
                "SceneManager",
                "activate_scene",
                e,
                ErrorSeverity.ERROR,
                {"scene_id": scene_id}
            )
            return False
    
    def get_active_scene(self) -> Optional[str]:
        """Get the current active scene ID."""
        return self.active_scene
    
    def get_scene_data(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """Get scene configuration data.
        
        Args:
            scene_id: Scene identifier
            
        Returns:
            Optional[Dict[str, Any]]: Scene data or None if not found
        """
        return self.scenes.get(scene_id)
    
    def register_event_callback(self, event_name: str, callback: Callable) -> None:
        """Register a callback for scene events (legacy method).
        
        Args:
            event_name: Event name ('scene_activated', 'scene_deactivated', etc.)
            callback: Function to call when event occurs
            
        Note:
            This method is maintained for backward compatibility.
            New code should use the event_system directly.
        """
        if event_name not in self.event_callbacks:
            self.event_callbacks[event_name] = []
            
        self.event_callbacks[event_name].append(callback)
        
        # Map legacy event names to new event types
        if event_name == "scene_activated":
            self.event_system.register_global_listener(
                SceneEventType.SCENE_ACTIVATED,
                lambda event: callback(event.scene_id)
            )
        elif event_name == "scene_deactivated":
            self.event_system.register_global_listener(
                SceneEventType.SCENE_DEACTIVATED,
                lambda event: callback(event.scene_id)
            )
        
    def unregister_event_callback(self, event_name: str, callback: Callable) -> None:
        """Unregister a callback for scene events (legacy method).
        
        Args:
            event_name: Event name
            callback: Callback to remove
            
        Note:
            This method is maintained for backward compatibility.
            New code should use the event_system directly.
        """
        if event_name in self.event_callbacks:
            if callback in self.event_callbacks[event_name]:
                self.event_callbacks[event_name].remove(callback)
        
        # Note: Unfortunately, we can't easily unregister from the event_system
        # because the lambda creates a new function object. This is a limitation
        # of this legacy adapter.

    def _on_memory_warning(self, usage_fraction: float) -> None:
        """Callback for memory warning threshold."""
        logger.warning(f"Memory usage warning: {usage_fraction:.2f}")
        
        # Emit memory warning event
        self.event_system.emit_scene_event(
            SceneEventType.MEMORY_WARNING,
            source="MemoryBudget",
            data={"usage_fraction": usage_fraction}
        )

    def _on_memory_critical(self, usage_fraction: float) -> None:
        """Callback for memory critical threshold."""
        logger.critical(f"Memory usage critical: {usage_fraction:.2f}")
        
        # Emit memory critical event
        self.event_system.emit_scene_event(
            SceneEventType.MEMORY_CRITICAL,
            source="MemoryBudget",
            data={"usage_fraction": usage_fraction},
            immediate=True  # Critical events bypass the queue
        )

    def _on_scene_activated(self, new_scene: str, old_scene: Optional[str]) -> None:
        """Callback for scene activation."""
        if old_scene:
            self._on_scene_deactivated(old_scene)
        
        # Legacy callback handling
        if new_scene in self.event_callbacks:
            for callback in self.event_callbacks[new_scene]:
                try:
                    callback(new_scene)
                except Exception as e:
                    logger.error(f"Error in scene activation callback: {e}")
        
        # Emit scene activated event
        self.event_system.emit_scene_event(
            SceneEventType.SCENE_ACTIVATED,
            scene_id=new_scene,
            data={"previous_scene": old_scene}
        )

    def _on_scene_deactivated(self, scene_id: str) -> None:
        """Callback for scene deactivation."""
        # Legacy callback handling
        if scene_id in self.event_callbacks:
            for callback in self.event_callbacks[scene_id]:
                try:
                    callback(scene_id)
                except Exception as e:
                    logger.error(f"Error in scene deactivation callback: {e}")
        
        # Emit scene deactivated event
        self.event_system.emit_scene_event(
            SceneEventType.SCENE_DEACTIVATED,
            scene_id=scene_id
        )

    def _loading_worker(self) -> None:
        """Worker thread for asset loading."""
        while self.running:
            try:
                priority, (scene_id, asset_id, asset_type, asset_info) = self.asset_queue.get()
                self._load_asset(scene_id, asset_id, asset_type, asset_info)
            except Exception as e:
                logger.error(f"Error in loading worker: {e}")
                time.sleep(1)

    def _unloading_worker(self) -> None:
        """Worker thread for asset unloading."""
        while self.running:
            try:
                self._unload_assets()
            except Exception as e:
                logger.error(f"Error in unloading worker: {e}")
                time.sleep(1)

    def _monitoring_worker(self) -> None:
        """Worker thread for monitoring memory usage."""
        while self.running:
            try:
                self._check_memory_usage()
            except Exception as e:
                logger.error(f"Error in monitoring worker: {e}")
                time.sleep(1)

    def _load_asset(self, scene_id: str, asset_id: str, asset_type: str, asset_info: Dict[str, Any]) -> None:
        """Load an asset for a scene, update reference count and memory budget."""
        try:
            # LOD-aware loading if metadata present
            lod_level = asset_info.get("lod_level", 0)
            asset = None
            if asset_type == "image" and hasattr(self.asset_manager, "load_image_lod"):
                asset = self.asset_manager.load_image_lod(asset_id, lod_level=lod_level)
            else:
                asset = self.asset_manager.load_image(asset_id)
            if asset:
                self.scene_assets[scene_id][asset_id] = SceneAsset(asset_id, asset_type, asset, asset_info["size"])
                self.memory_budget.register_asset(asset_id, scene_id, asset_type, asset_info["size"])
                logger.info(f"Loaded asset: {asset_id}")
                # Reference counting
                self.scene_assets[scene_id][asset_id].increment_ref()
                # Emit asset loaded event if successful
                self.event_system.emit_scene_event(
                    SceneEventType.ASSET_LOADED,
                    scene_id=scene_id,
                    data={
                        "asset_id": asset_id,
                        "asset_type": asset_type
                    }
                )
            else:
                logger.warning(f"Failed to load asset: {asset_id}")
        except Exception as e:
            logger.error(f"Error loading asset {asset_id}: {e}")

    def _unload_assets(self) -> None:
        """Unload assets based on the current strategy, update reference counts and memory budget."""
        try:
            if self.unload_strategy == UnloadStrategy.TIME_BASED:
                self._unload_time_based()
            elif self.unload_strategy == UnloadStrategy.DISTANCE_BASED:
                self._unload_distance_based()
            elif self.unload_strategy == UnloadStrategy.PRIORITY_BASED:
                self._unload_priority_based()
            elif self.unload_strategy == UnloadStrategy.MEMORY_PRESSURE:
                self._unload_memory_pressure()
            elif self.unload_strategy == UnloadStrategy.COMBINED:
                self._unload_combined()
        except Exception as e:
            logger.error(f"Error in unloading assets: {e}")

    def _unload_time_based(self) -> None:
        """Unload assets based on time since last use."""
        current_time = time.time()
        for scene_id, assets in self.scene_assets.items():
            for asset_id, asset in list(assets.items()):
                if current_time - asset.last_used > self.time_threshold and asset.ref_count == 0:
                    if asset.unload():
                        self.memory_budget.unregister_asset(asset_id, scene_id, asset.asset_type)
                        logger.info(f"Unloaded asset (time-based): {asset_id}")

    def _unload_distance_based(self) -> None:
        """Unload assets based on distance from player/camera."""
        # Placeholder: integrate with player position and asset position
        pass

    def _unload_priority_based(self) -> None:
        """Unload assets based on asset priority."""
        # Placeholder: sort by priority and unload lowest
        pass

    def _unload_memory_pressure(self) -> None:
        """Unload assets based on system memory pressure."""
        # Placeholder: check memory budget and unload as needed
        pass

    def _unload_combined(self) -> None:
        """Unload assets based on a combination of strategies."""
        # Placeholder: combine above strategies
        pass

    def _check_memory_usage(self) -> None:
        """Check memory usage and trigger actions if thresholds are exceeded."""
        usage_fraction = self.memory_budget.get_usage_fraction()
        
        if usage_fraction >= MemoryThreshold.CRITICAL:
            self._unload_assets()
        elif usage_fraction >= MemoryThreshold.WARNING:
            self._on_memory_warning(usage_fraction)

    def _register_scene_assets(self, scene_id: str, asset_manifest: Dict[str, List[Dict[str, Any]]]) -> None:
        """Register assets for a scene."""
        for asset_info in asset_manifest:
            asset_id = asset_info["id"]
            asset_type = asset_info["type"]
            size = asset_info["size"]
            priority = asset_info["priority"]
            self.scene_assets[scene_id][asset_id] = SceneAsset(asset_id, asset_type, None, size, priority, scene_id)
            self.memory_budget.register_asset(asset_id, scene_id, asset_type, size)
            logger.info(f"Registered asset: {asset_id}")

    def _unload_scene_assets(self, scene_id: str) -> None:
        """Unload all assets for a scene."""
        if scene_id in self.scene_assets:
            for asset_id, asset in list(self.scene_assets[scene_id].items()):
                asset.unload()
                self.memory_budget.unregister_asset(asset_id, scene_id, asset.asset_type)
                
                # Emit asset unloaded event
                self.event_system.emit_scene_event(
                    SceneEventType.ASSET_UNLOADED,
                    scene_id=scene_id,
                    data={
                        "asset_id": asset_id,
                        "asset_type": asset.asset_type
                    }
                )
                
            self.scene_assets[scene_id].clear()
            logger.info(f"Unloaded all assets for scene: {scene_id}")
        else:
            logger.warning(f"No assets found for scene: {scene_id}")

    def get_asset(self, asset_id: str, scene_id: Optional[str] = None) -> Optional[Any]:
        """Get an asset by ID, optionally within a specific scene.
        
        Args:
            asset_id: Asset identifier
            scene_id: Optional scene identifier to limit search
            
        Returns:
            Optional[Any]: Asset or None if not found
        """
        # Check if this is a scene-specific request
        if scene_id is not None:
            if scene_id in self.scene_assets and asset_id in self.scene_assets[scene_id]:
                asset_obj = self.scene_assets[scene_id][asset_id]
                asset_obj.use()  # Mark as used
                return asset_obj.asset if asset_obj.loaded else None
        
        # Check global assets
        if asset_id in self.global_assets:
            asset_obj = self.global_assets[asset_id]
            asset_obj.use()  # Mark as used
            return asset_obj.asset if asset_obj.loaded else None
            
        # Check all scenes if scene_id not specified
        if scene_id is None:
            for scene_assets in self.scene_assets.values():
                if asset_id in scene_assets:
                    asset_obj = scene_assets[asset_id]
                    asset_obj.use()  # Mark as used
                    return asset_obj.asset if asset_obj.loaded else None
                    
        return None
    
    def register_global_asset(
        self,
        asset_id: str,
        asset_type: str,
        asset: Any,
        size: int,
        priority: AssetPriority = AssetPriority.CRITICAL
    ) -> None:
        """Register a global asset shared across all scenes.
        
        Args:
            asset_id: Asset identifier
            asset_type: Type of asset
            asset: Asset object
            size: Size in bytes
            priority: Asset priority
        """
        try:
            # Create asset object
            asset_obj = SceneAsset(
                asset_id=asset_id,
                asset_type=asset_type,
                asset=asset,
                size=size,
                priority=priority
            )
            
            # Store in global assets
            self.global_assets[asset_id] = asset_obj
            
            # Register with memory budget
            self.memory_budget.register_asset(asset_id, "global", asset_type, size)
            
            logger.debug(f"Registered global asset: {asset_id}")
            
        except Exception as e:
            handle_component_error(
                "SceneManager",
                "register_global_asset",
                e,
                ErrorSeverity.ERROR,
                {"asset_id": asset_id}
            )
    
    def unregister_global_asset(self, asset_id: str) -> None:
        """Unregister a global asset.
        
        Args:
            asset_id: Asset identifier
        """
        try:
            if asset_id in self.global_assets:
                asset_obj = self.global_assets[asset_id]
                
                # Unregister from memory budget
                self.memory_budget.unregister_asset(asset_id, "global", asset_obj.asset_type)
                
                # Remove from global assets
                del self.global_assets[asset_id]
                
                logger.debug(f"Unregistered global asset: {asset_id}")
                
        except Exception as e:
            handle_component_error(
                "SceneManager",
                "unregister_global_asset",
                e,
                ErrorSeverity.ERROR,
                {"asset_id": asset_id}
            )
    
    def set_asset_priority(self, asset_id: str, priority: AssetPriority, scene_id: Optional[str] = None) -> bool:
        """Set an asset's priority for memory management.
        
        Args:
            asset_id: Asset identifier
            priority: New priority level
            scene_id: Optional scene to limit the search
            
        Returns:
            bool: True if priority was updated, False if asset not found
        """
        # Try to find in specified scene
        if scene_id is not None:
            if scene_id in self.scene_assets and asset_id in self.scene_assets[scene_id]:
                self.scene_assets[scene_id][asset_id].priority = priority
                self.event_system.emit_scene_event(
                    SceneEventType.ASSET_PRIORITY_CHANGED,
                    scene_id=scene_id,
                    data={
                        "asset_id": asset_id,
                        "priority": priority.value
                    }
                )
                return True
                
        # Try to find in global assets
        if asset_id in self.global_assets:
            self.global_assets[asset_id].priority = priority
            self.event_system.emit_scene_event(
                SceneEventType.ASSET_PRIORITY_CHANGED,
                scene_id="global",
                data={
                    "asset_id": asset_id,
                    "priority": priority.value
                }
            )
            return True
            
        # Try to find in any scene
        if scene_id is None:
            for scene_assets in self.scene_assets.values():
                if asset_id in scene_assets:
                    scene_assets[asset_id].priority = priority
                    self.event_system.emit_scene_event(
                        SceneEventType.ASSET_PRIORITY_CHANGED,
                        scene_id=scene_id,
                        data={
                            "asset_id": asset_id,
                            "priority": priority.value
                        }
                    )
                    return True
                    
        return False
    
    def set_unload_strategy(self, strategy: UnloadStrategy) -> None:
        """Set the strategy used for unloading assets.
        
        Args:
            strategy: Unload strategy to use
        """
        self.unload_strategy = strategy
        logger.info(f"Asset unload strategy set to: {strategy.name}")
    
    def set_time_threshold(self, seconds: int) -> None:
        """Set the time threshold for unloading assets.
        
        Args:
            seconds: Seconds of inactivity before unloading
        """
        self.time_threshold = seconds
        logger.info(f"Asset unload time threshold set to: {seconds}s")
    
    def get_memory_usage_report(self) -> Dict[str, Any]:
        """Get a report of memory usage statistics.
        
        Returns:
            Dict[str, Any]: Memory usage report
        """
        return self.memory_budget.get_usage_report()
    
    def force_garbage_collection(self) -> None:
        """Force Python garbage collection to free memory."""
        collected = gc.collect()
        logger.info(f"Forced garbage collection: {collected} objects collected")
    
    def shutdown(self) -> None:
        """Shut down the scene manager."""
        try:
            # Stop running
            self.running = False
            
            # Wait for threads to exit
            if self.loading_thread and self.loading_thread.is_alive():
                self.loading_thread.join(timeout=1.0)
                
            if self.unloading_thread and self.unloading_thread.is_alive():
                self.unloading_thread.join(timeout=1.0)
                
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=1.0)
                
            # Unload all assets
            for scene_id in list(self.scenes.keys()):
                self.unregister_scene(scene_id)
                
            for asset_id in list(self.global_assets.keys()):
                self.unregister_global_asset(asset_id)
                
            # Clear references
            self.scenes.clear()
            self.scene_assets.clear()
            self.global_assets.clear()
            self.preloaded_scenes.clear()
            self.asset_references.clear()
            self.event_callbacks.clear()
            
            # Force garbage collection
            self.force_garbage_collection()
            
            logger.info("Scene Manager shut down")
            
        except Exception as e:
            logger.error(f"Error shutting down Scene Manager: {e}", exc_info=True)

    def on_origin_shift(self, shift_delta: Tuple[float, float, float]) -> None:
        """
        Hook for floating origin shift events. Update all physics objects and scene state as needed.
        Args:
            shift_delta: The (dx, dy, dz) shift applied to the origin.
        """
        # TODO: Integrate with physics engine (e.g., PyBullet, Unity, or custom)
        # For each physics object:
        #   - Update position by shift_delta
        #   - Update velocities if needed
        #   - Ensure collision and simulation stability
        # This method should be called by the FloatingOrigin system on every origin shift.
        pass 

    def set_scene_loader_manager(self, loader_manager: Any) -> None:
        """Set the SceneLoaderManager for async scene loading."""
        self.scene_loader_manager = loader_manager 

    def load_scene_async(self, scene_id: str, priority: int = 1, callback: Optional[Callable] = None):
        """Begin asynchronous scene loading using the SceneLoaderManager if set."""
        if self.scene_loader_manager:
            self.scene_loader_manager.queue_scene_load(scene_id, priority=priority, callback=callback)
        else:
            # Fallback: synchronous activation
            success = self.activate_scene(scene_id)
            if callback:
                callback(success=success)

    def get_asset_lod(self, asset_id: str, position: Tuple[float, float], player_pos: Tuple[float, float]) -> Optional[Any]:
        """Get asset at appropriate LOD based on distance to player."""
        distance = ((position[0] - player_pos[0]) ** 2 + (position[1] - player_pos[1]) ** 2) ** 0.5
        lod = self.asset_manager.select_lod_level(distance, self.lod_thresholds)
        return self.asset_manager.load_image_lod(asset_id, lod) 