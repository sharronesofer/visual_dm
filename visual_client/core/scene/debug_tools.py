import logging
from typing import List, Dict, Any

class ChunkVisualizer:
    def __init__(self):
        self.logger = logging.getLogger('ChunkVisualizer')
        self.enabled = True

    def show_boundaries(self, chunks: List[Any]):
        if not self.enabled:
            return
        for chunk in chunks:
            self.logger.info(f"Chunk bounds: {chunk.bounds} | State: {getattr(chunk.metadata, 'streaming_state', 'unknown')}")

    def show_memory_usage(self, chunk_cache: Any):
        if not self.enabled:
            return
        usage = len(chunk_cache)
        self.logger.info(f"Loaded chunks: {usage}")
        # Optionally, add per-chunk memory stats if available

    def show_heatmap(self, access_counts: Dict[str, int]):
        if not self.enabled:
            return
        for chunk_key, count in access_counts.items():
            self.logger.info(f"Chunk {chunk_key}: access count = {count}")

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

# --- Example Usage ---
# visualizer = ChunkVisualizer()
# visualizer.show_boundaries(chunks)
# visualizer.show_memory_usage(chunk_cache)
# visualizer.show_heatmap({'chunk_0_0_0': 10, 'chunk_0_0_1': 5}) 