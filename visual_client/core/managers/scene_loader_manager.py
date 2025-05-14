"""
Asynchronous Scene Loader Manager for background scene loading and progress tracking.
Integrates with SceneManager, LoadingManager, and supports progressive loading.

# SceneLoaderManager Developer Documentation

## Overview
SceneLoaderManager provides asynchronous, background scene loading for games and visualization systems. It manages scene loading in a background thread, reports progress to the LoadingManager for UI feedback, and supports callbacks and robust error handling.

## Usage Example

### Integration
1. Instantiate SceneLoaderManager after SceneManager and LoadingManager:

    scene_loader_manager = SceneLoaderManager(scene_manager, loading_manager)
    scene_manager.set_scene_loader_manager(scene_loader_manager)

2. To load a scene asynchronously:

    scene_manager.load_scene_async("scene_id", priority=1, callback=on_scene_loaded)

### Callback Signature
The callback receives:
    callback(success: bool, error: Optional[Exception] = None)

- success: True if the scene loaded successfully, False otherwise
- error: Exception instance if loading failed, else None

### Progress Reporting
- Progress is reported to LoadingManager using a unique id ("scene_{scene_id}").
- UI should call LoadingManager.draw_loading(...) to display progress bars/spinners.

### Error Handling
- All errors are logged with detailed diagnostics (timing, memory usage, exception info).
- On error, progress is set to 100% and the callback is called with success=False and error set.

### Best Practices
- Always set the SceneLoaderManager on your SceneManager to enable async loading.
- Use callbacks to update game state/UI after scene transitions.
- Monitor logs for diagnostics and performance analysis.
- For stress testing, rapidly queue multiple scene loads and verify all callbacks and progress updates.

## Save/Restore Integration
- Use get_state() to serialize the current queue and progress for saving.
- Use set_state(state) to restore the queue and progress after loading.
- Use cancel_all() to halt all background loads before saving or during shutdown.
"""

import threading
import time
from queue import Queue, PriorityQueue
from typing import Callable, Dict, List, Optional, Any
from .loading_manager import LoadingManager
from .scene_manager import SceneManager
from .robust_scene_manager import RobustSceneManager
from ..scene.streaming import ChunkStreamingManager
import logging
import os
import psutil
from concurrent.futures import ThreadPoolExecutor
from visual_client.core.events.scene_events import SceneEventType

class SceneLoaderManager:
    def __init__(self, 
                 scene_manager: SceneManager,
                 loading_manager: LoadingManager,
                 chunk_streaming_manager: Optional[ChunkStreamingManager] = None,
                 max_workers: int = 4):
        self.scene_manager = scene_manager
        self.loading_manager = loading_manager
        self.chunk_streaming_manager = chunk_streaming_manager
        self.load_queue = PriorityQueue()
        self.progress: Dict[str, float] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.lock = threading.Lock()
        self.running = True
        self.logger = logging.getLogger(__name__)
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers, thread_name_prefix="SceneLoaderWorker")
        self._start_workers()
        # Diagnostics/event hooks
        try:
            from visual_client.core.events.scene_events import SceneEventSystem
            self.event_system = SceneEventSystem.get_instance()
        except Exception:
            self.event_system = None

    def _start_workers(self):
        for _ in range(self.max_workers):
            self.executor.submit(self._worker)
        self.logger.info(f"[SceneLoaderManager] Started thread pool with {self.max_workers} workers.")

    def queue_scene_load(self, scene_id: str, priority: int = 1, callback: Optional[Callable] = None):
        with self.lock:
            self.load_queue.put((priority, scene_id))
            if callback:
                self.callbacks.setdefault(scene_id, []).append(callback)
            self.progress[scene_id] = 0.0
            self.loading_manager.start_loading(
                id=f"scene_{scene_id}",
                total=100,
                description=f"Loading scene {scene_id}",
                show_progress=True,
                show_spinner=True
            )
        self.logger.info(f"[SceneLoaderManager] Queued scene '{scene_id}' (queue size: {self.load_queue.qsize()})")

    def _worker(self):
        while self.running:
            try:
                if not self.load_queue.empty():
                    priority, scene_id = self.load_queue.get()
                    self.logger.info(f"[SceneLoaderManager] Worker {threading.current_thread().name} picked scene '{scene_id}' (queue size: {self.load_queue.qsize()})")
                    self._load_scene_async(scene_id)
                else:
                    time.sleep(0.05)
            except Exception as e:
                self.logger.error(f"SceneLoaderManager worker error: {e}", exc_info=True)
                time.sleep(0.1)

    def _load_scene_async(self, scene_id: str):
        start_time = time.time()
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        thread_name = threading.current_thread().name
        self.logger.info(f"[SceneLoaderManager] Starting async load for scene '{scene_id}' on thread '{thread_name}'. Memory before: {mem_before} bytes.")
        if self.event_system:
            self.event_system.emit_scene_event(
                SceneEventType.SCENE_PRELOADED,
                scene_id=scene_id,
                data={"thread": thread_name, "mem_before": mem_before}
            )
        try:
            # Step 1: Preload assets (background)
            self.progress[scene_id] = 10.0
            self.loading_manager.update_progress(f"scene_{scene_id}", 10)
            self.scene_manager.preload_scene(scene_id, priority=0)
            self.progress[scene_id] = 30.0
            self.loading_manager.update_progress(f"scene_{scene_id}", 30)
            # Step 2: Progressive/partial loading if supported
            if self.chunk_streaming_manager:
                chunk_keys = self._get_initial_chunk_keys(scene_id)
                loaded_chunks = []
                for i, chunk_key in enumerate(chunk_keys):
                    self.chunk_streaming_manager.request_chunk_load(
                        chunk_key, priority=1.0,
                        callback=lambda chunk: loaded_chunks.append(chunk)
                    )
                    self.progress[scene_id] = 30.0 + 40.0 * (i+1)/len(chunk_keys)
                    self.loading_manager.update_progress(f"scene_{scene_id}", int(self.progress[scene_id]))
                while len(loaded_chunks) < len(chunk_keys):
                    time.sleep(0.01)
            self.progress[scene_id] = 70.0
            self.loading_manager.update_progress(f"scene_{scene_id}", 70)
            # Step 3: Activate scene
            activated = self.scene_manager.activate_scene(scene_id)
            self.progress[scene_id] = 90.0
            self.loading_manager.update_progress(f"scene_{scene_id}", 90)
            # Step 4: Finalize, cleanup, notify
            self.progress[scene_id] = 100.0
            self.loading_manager.update_progress(f"scene_{scene_id}", 100)
            self.loading_manager._complete_loading(f"scene_{scene_id}")
            if self.event_system:
                self.event_system.emit_scene_event(
                    SceneEventType.SCENE_ACTIVATED,
                    scene_id=scene_id,
                    data={"duration": time.time() - start_time}
                )
            if scene_id in self.callbacks:
                for cb in self.callbacks[scene_id]:
                    if activated:
                        cb(success=True)
                    else:
                        cb(success=False, error=Exception(f"Scene '{scene_id}' failed to activate (not registered or error during activation)."))
                del self.callbacks[scene_id]
            duration = time.time() - start_time
            mem_after = process.memory_info().rss
            self.logger.info(f"[SceneLoaderManager] Scene '{scene_id}' loaded successfully in {duration:.2f}s. Memory after: {mem_after} bytes. Delta: {mem_after - mem_before} bytes.")
        except Exception as e:
            duration = time.time() - start_time
            mem_after = process.memory_info().rss
            self.logger.error(f"[SceneLoaderManager] Error loading scene '{scene_id}' after {duration:.2f}s. Memory after: {mem_after} bytes. Delta: {mem_after - mem_before} bytes. Error: {e}", exc_info=True)
            self.progress[scene_id] = 100.0
            self.loading_manager.update_progress(f"scene_{scene_id}", 100)
            self.loading_manager._complete_loading(f"scene_{scene_id}")
            if self.event_system:
                self.event_system.emit_scene_event(
                    SceneEventType.SCENE_ERROR,
                    scene_id=scene_id,
                    data={"error": str(e), "duration": duration}
                )
            print(f"Error loading scene {scene_id}: {e}")
            if scene_id in self.callbacks:
                for cb in self.callbacks[scene_id]:
                    cb(success=False, error=e)
                del self.callbacks[scene_id]

    def _get_initial_chunk_keys(self, scene_id: str) -> List[str]:
        # Placeholder: derive chunk keys for the scene
        # In a real system, this would query the partition tree or scene manifest
        return [f"{scene_id}_chunk_{i}" for i in range(3)]

    def shutdown(self):
        self.running = False
        self.executor.shutdown(wait=True)

    def get_state(self) -> dict:
        """Serialize the current load queue and progress for saving."""
        with self.lock:
            queue_list = list(self.load_queue.queue)
            return {
                "queue": queue_list,
                "progress": dict(self.progress),
            }

    def set_state(self, state: dict) -> None:
        """Restore the load queue and progress from a saved state."""
        with self.lock:
            self.load_queue.queue.clear()
            for item in state.get("queue", []):
                self.load_queue.put(item)
            self.progress = dict(state.get("progress", {}))

    def cancel_all(self) -> None:
        """Cancel all pending scene loads and clear the queue."""
        with self.lock:
            while not self.load_queue.empty():
                self.load_queue.get()
            self.progress.clear()
            self.callbacks.clear()
        self.logger.info("[SceneLoaderManager] All pending scene loads cancelled.") 