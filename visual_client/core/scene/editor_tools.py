import logging
from typing import List, Any, Callable
from visual_client.core.scene.debug_tools import ChunkVisualizer
from visual_client.core.scene.streaming_api import StreamingManager

class SceneEditorTools:
    def __init__(self, streaming_api: StreamingManager, visualizer: ChunkVisualizer):
        self.streaming_api = streaming_api
        self.visualizer = visualizer
        self.logger = logging.getLogger('SceneEditorTools')

    def visualize_chunks(self):
        active_chunk_keys = self.streaming_api.getActiveChunks()
        # In a real editor, fetch chunk objects by key; here, just log keys
        self.logger.info(f"Active chunks: {active_chunk_keys}")
        # Optionally, call self.visualizer.show_boundaries(chunks)

    def manual_load_chunk(self, chunk_key: str, priority: float = 1.0):
        self.logger.info(f"Manually loading chunk: {chunk_key}")
        self.streaming_api.requestChunk(chunk_key, priority)

    def manual_unload_chunk(self, chunk_key: str, priority: float = 1.0):
        self.logger.info(f"Manually unloading chunk: {chunk_key}")
        self.streaming_api.releaseChunk(chunk_key, priority)

    def show_streaming_diagnostics(self):
        active_chunks = self.streaming_api.getActiveChunks()
        self.logger.info(f"Streaming diagnostics: {len(active_chunks)} chunks loaded.")
        # Optionally, show memory usage, queue size, etc.

    def partitioning_tool(self, partition_callback: Callable):
        # Tool for content creators to partition scenes
        self.logger.info("Running partitioning tool for scene content.")
        partition_callback()

# --- Example Usage ---
# editor_tools = SceneEditorTools(streaming_api, visualizer)
# editor_tools.visualize_chunks()
# editor_tools.manual_load_chunk('chunk_0_0_0')
# editor_tools.show_streaming_diagnostics() 