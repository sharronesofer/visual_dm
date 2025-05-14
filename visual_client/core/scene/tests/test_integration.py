import unittest
from visual_client.core.scene.streaming import ChunkStreamingManager
from visual_client.core.scene.partitioning import SpatialPartitionTree
from visual_client.core.scene.streaming_api import StreamingManager
from visual_client.core.scene.debug_tools import ChunkVisualizer
from visual_client.core.scene.editor_tools import SceneEditorTools

class TestStreamingIntegration(unittest.TestCase):
    def setUp(self):
        bounds = ((0.0, 0.0, 0.0), (100.0, 100.0, 100.0))
        self.partition_tree = SpatialPartitionTree(bounds, max_depth=2, min_size=10.0, is_3d=True)
        self.streaming_manager = ChunkStreamingManager(self.partition_tree, max_workers=2, cache_size=3)
        self.api = StreamingManager.get_instance(self.streaming_manager)
        self.visualizer = ChunkVisualizer()
        self.editor_tools = SceneEditorTools(self.api, self.visualizer)

    def tearDown(self):
        self.streaming_manager.stop()
        StreamingManager._instance = None

    def test_editor_manual_chunk_load_unload(self):
        self.editor_tools.manual_load_chunk('chunk_x', priority=1.0)
        import time; time.sleep(0.1)
        active = self.api.getActiveChunks()
        self.assertIn('chunk_x', active)
        self.editor_tools.manual_unload_chunk('chunk_x', priority=1.0)
        time.sleep(0.05)
        active = self.api.getActiveChunks()
        self.assertNotIn('chunk_x', active)

    def test_editor_diagnostics(self):
        self.editor_tools.manual_load_chunk('chunk_y', priority=1.0)
        import time; time.sleep(0.1)
        self.editor_tools.show_streaming_diagnostics()
        # No assertion: just ensure no exceptions and logs are produced

    def test_partitioning_tool_hook(self):
        called = []
        def cb():
            called.append(True)
        self.editor_tools.partitioning_tool(cb)
        self.assertTrue(called)

if __name__ == '__main__':
    unittest.main() 