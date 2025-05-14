import unittest
import time
from visual_client.core.scene.streaming import ChunkStreamingManager
from visual_client.core.scene.partitioning import SpatialPartitionTree
from visual_client.core.scene.streaming_api import StreamingManager

class TestStreamingAPI(unittest.TestCase):
    def setUp(self):
        bounds = ((0.0, 0.0, 0.0), (100.0, 100.0, 100.0))
        self.partition_tree = SpatialPartitionTree(bounds, max_depth=2, min_size=10.0, is_3d=True)
        self.streaming_manager = ChunkStreamingManager(self.partition_tree, max_workers=2, cache_size=3)
        self.api = StreamingManager.get_instance(self.streaming_manager)

    def tearDown(self):
        self.streaming_manager.stop()
        # Reset singleton for isolation
        StreamingManager._instance = None

    def test_chunk_request_and_status(self):
        self.api.requestChunk('chunk_a', priority=1.0)
        time.sleep(0.1)
        status = self.api.queryChunkStatus('chunk_a')
        self.assertEqual(status, 'loaded')
        self.api.releaseChunk('chunk_a', priority=1.0)
        time.sleep(0.05)
        status = self.api.queryChunkStatus('chunk_a')
        self.assertEqual(status, 'unloaded')

    def test_event_callbacks(self):
        events = []
        self.api.on('onChunkLoaded', lambda key, chunk: events.append(('loaded', key)))
        self.api.on('onChunkUnloaded', lambda key: events.append(('unloaded', key)))
        self.api.requestChunk('chunk_b', priority=1.0)
        time.sleep(0.1)
        self.api.releaseChunk('chunk_b', priority=1.0)
        time.sleep(0.05)
        loaded = any(e[0] == 'loaded' and e[1] == 'chunk_b' for e in events)
        unloaded = any(e[0] == 'unloaded' and e[1] == 'chunk_b' for e in events)
        self.assertTrue(loaded and unloaded)

    def test_get_active_chunks(self):
        self.api.requestChunk('chunk_c', priority=1.0)
        time.sleep(0.1)
        active = self.api.getActiveChunks()
        self.assertIn('chunk_c', active)
        self.api.releaseChunk('chunk_c', priority=1.0)
        time.sleep(0.05)
        active = self.api.getActiveChunks()
        self.assertNotIn('chunk_c', active)

    def test_thread_safety(self):
        # Simulate concurrent requests
        import threading
        results = []
        def req():
            self.api.requestChunk('chunk_d', priority=1.0)
            results.append(self.api.queryChunkStatus('chunk_d'))
        threads = [threading.Thread(target=req) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertTrue(all(r == 'loaded' for r in results))

if __name__ == '__main__':
    unittest.main() 