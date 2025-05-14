import threading
import heapq
import time
from concurrent.futures import ThreadPoolExecutor, Future
from collections import OrderedDict
from typing import Any, Callable, Dict, List, Optional, Tuple
from visual_client.core.scene.partitioning import SpatialPartitionTree, SceneChunk
from visual_client.core.events.scene_event_system import SceneEventSystem
from visual_client.core.events.scene_events import SceneEventType

# --- LRU Cache for Chunks ---
class LRUChunkCache:
    def __init__(self, max_chunks: int = 64):
        self.max_chunks = max_chunks
        self.cache: OrderedDict[str, SceneChunk] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[SceneChunk]:
        with self.lock:
            chunk = self.cache.get(key)
            if chunk:
                self.cache.move_to_end(key)
            return chunk

    def put(self, key: str, chunk: SceneChunk):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = chunk
            if len(self.cache) > self.max_chunks:
                self.cache.popitem(last=False)

    def remove(self, key: str):
        with self.lock:
            if key in self.cache:
                del self.cache[key]

    def keys(self):
        with self.lock:
            return list(self.cache.keys())

    def __len__(self):
        with self.lock:
            return len(self.cache)

# --- Priority Queue for Chunk Requests ---
class ChunkRequest:
    def __init__(self, priority: float, chunk_key: str, action: str, callback: Optional[Callable] = None):
        self.priority = priority
        self.chunk_key = chunk_key
        self.action = action  # 'load' or 'unload'
        self.callback = callback
        self.timestamp = time.time()
    def __lt__(self, other):
        return self.priority < other.priority

class ChunkRequestQueue:
    def __init__(self):
        self.heap: List[ChunkRequest] = []
        self.lock = threading.Lock()

    def push(self, req: ChunkRequest):
        with self.lock:
            heapq.heappush(self.heap, req)

    def pop(self) -> Optional[ChunkRequest]:
        with self.lock:
            if self.heap:
                return heapq.heappop(self.heap)
            return None

    def reprioritize(self, key: str, new_priority: float):
        with self.lock:
            for req in self.heap:
                if req.chunk_key == key:
                    req.priority = new_priority
            heapq.heapify(self.heap)

    def cancel(self, key: str):
        with self.lock:
            self.heap = [req for req in self.heap if req.chunk_key != key]
            heapq.heapify(self.heap)

    def __len__(self):
        with self.lock:
            return len(self.heap)

# --- Asynchronous Chunk Loader ---
class ChunkStreamingManager:
    def __init__(self, partition_tree: SpatialPartitionTree, max_workers: int = 4, cache_size: int = 64):
        self.partition_tree = partition_tree
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache = LRUChunkCache(max_chunks=cache_size)
        self.request_queue = ChunkRequestQueue()
        self.memory_budget = cache_size  # Number of chunks
        self.critical_chunk_keys: set = set()
        self.running = True
        self.lock = threading.Lock()
        self.event_system = SceneEventSystem.get_instance()
        self.memory_warning_callback = None
        self.memory_critical_callback = None
        self._start_worker_thread()

    def set_memory_warning_callback(self, callback: Callable):
        self.memory_warning_callback = callback

    def set_memory_critical_callback(self, callback: Callable):
        self.memory_critical_callback = callback

    def _start_worker_thread(self):
        t = threading.Thread(target=self._worker_loop, daemon=True)
        t.start()

    def _worker_loop(self):
        while self.running:
            req = self.request_queue.pop()
            if req:
                if req.action == 'load':
                    future = self.executor.submit(self._load_chunk, req.chunk_key)
                    if req.callback:
                        future.add_done_callback(lambda f: req.callback(f.result()))
                elif req.action == 'unload':
                    self._unload_chunk(req.chunk_key)
            else:
                time.sleep(0.01)
            self._check_memory_usage()

    def _load_chunk(self, chunk_key: str) -> SceneChunk:
        # Simulate loading delay
        time.sleep(0.05)
        chunk = self.cache.get(chunk_key)
        if not chunk:
            # In a real system, load from disk/network or generate
            chunk = SceneChunk(bounds=((0,0,0),(1,1,1)))  # Placeholder
            self.cache.put(chunk_key, chunk)
            self.event_system.emit_scene_event(
                SceneEventType.TERRAIN_LOADED,
                scene_id=None,
                data={"chunk_key": chunk_key}
            )
        return chunk

    def _unload_chunk(self, chunk_key: str):
        if chunk_key not in self.critical_chunk_keys:
            self.cache.remove(chunk_key)
            self.event_system.emit_scene_event(
                SceneEventType.TERRAIN_UNLOADED,
                scene_id=None,
                data={"chunk_key": chunk_key}
            )

    def request_chunk_load(self, chunk_key: str, priority: float, callback: Optional[Callable] = None):
        self.request_queue.push(ChunkRequest(priority, chunk_key, 'load', callback))

    def request_chunk_unload(self, chunk_key: str, priority: float):
        self.request_queue.push(ChunkRequest(priority, chunk_key, 'unload'))

    def set_critical_chunks(self, keys: List[str]):
        with self.lock:
            self.critical_chunk_keys = set(keys)

    def set_memory_budget(self, chunk_count: int):
        with self.lock:
            self.memory_budget = chunk_count
            self.cache.max_chunks = chunk_count

    def _check_memory_usage(self):
        usage = len(self.cache)
        if usage > self.memory_budget * 0.95 and self.memory_critical_callback:
            self.memory_critical_callback(usage)
        elif usage > self.memory_budget * 0.8 and self.memory_warning_callback:
            self.memory_warning_callback(usage)

    def stop(self):
        self.running = False
        self.executor.shutdown(wait=False)

# --- Example Usage ---
# partition_tree = SpatialPartitionTree(bounds=((0,0,0),(1000,1000,1000)), max_depth=6, min_size=20.0, is_3d=True)
# streaming_manager = ChunkStreamingManager(partition_tree)
# streaming_manager.request_chunk_load('chunk_0_0_0', priority=1.0) 