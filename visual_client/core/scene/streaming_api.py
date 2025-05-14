import threading
from typing import Callable, Dict, List, Optional, Any
from visual_client.core.scene.streaming import ChunkStreamingManager

class StreamingManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self, streaming_manager: Optional[ChunkStreamingManager] = None):
        if StreamingManager._instance is not None:
            raise Exception("Use StreamingManager.get_instance()")
        self.streaming_manager = streaming_manager
        self.event_callbacks = {
            'onChunkLoaded': [],
            'onChunkUnloaded': [],
            'onChunkStateChanged': []
        }
        self.active_chunks: set = set()
        self.status_lock = threading.Lock()

    @classmethod
    def get_instance(cls, streaming_manager: Optional[ChunkStreamingManager] = None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = StreamingManager(streaming_manager)
            return cls._instance

    def requestChunk(self, chunk_key: str, priority: float = 1.0):
        def on_loaded(chunk):
            with self.status_lock:
                self.active_chunks.add(chunk_key)
            self._fire_event('onChunkLoaded', chunk_key, chunk)
            self._fire_event('onChunkStateChanged', chunk_key, 'loaded')
        self.streaming_manager.request_chunk_load(chunk_key, priority, callback=on_loaded)

    def releaseChunk(self, chunk_key: str, priority: float = 1.0):
        self.streaming_manager.request_chunk_unload(chunk_key, priority)
        with self.status_lock:
            if chunk_key in self.active_chunks:
                self.active_chunks.remove(chunk_key)
        self._fire_event('onChunkUnloaded', chunk_key)
        self._fire_event('onChunkStateChanged', chunk_key, 'unloaded')

    def queryChunkStatus(self, chunk_key: str) -> str:
        with self.status_lock:
            return 'loaded' if chunk_key in self.active_chunks else 'unloaded'

    def getActiveChunks(self) -> List[str]:
        with self.status_lock:
            return list(self.active_chunks)

    def on(self, event: str, callback: Callable):
        if event in self.event_callbacks:
            self.event_callbacks[event].append(callback)
        else:
            raise ValueError(f"Unknown event: {event}")

    def _fire_event(self, event: str, *args, **kwargs):
        for cb in self.event_callbacks.get(event, []):
            cb(*args, **kwargs)

# --- Example Usage ---
# streaming_manager = ChunkStreamingManager(partition_tree)
# api = StreamingManager.get_instance(streaming_manager)
# api.on('onChunkLoaded', lambda key, chunk: print(f"Loaded: {key}"))
# api.requestChunk('chunk_0_0_0', priority=1.0) 