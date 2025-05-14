import unittest
import time
from visual_client.core.scene.partitioning import SpatialPartitionTree
from visual_client.core.scene.streaming import ChunkStreamingManager

class TestChunkStreamingManager(unittest.TestCase):
    def setUp(self):
        bounds = ((0.0, 0.0, 0.0), (100.0, 100.0, 100.0))
        self.partition_tree = SpatialPartitionTree(bounds, max_depth=2, min_size=10.0, is_3d=True)
        self.manager = ChunkStreamingManager(self.partition_tree, max_workers=2, cache_size=3)

    def tearDown(self):
        self.manager.stop()

    def test_chunk_load_and_cache(self):
        loaded = []
        def cb(chunk):
            loaded.append(chunk)
        self.manager.request_chunk_load('chunk_a', priority=1.0, callback=cb)
        self.manager.request_chunk_load('chunk_b', priority=2.0, callback=cb)
        self.manager.request_chunk_load('chunk_c', priority=3.0, callback=cb)
        time.sleep(0.2)  # Allow time for async loads
        self.assertEqual(len(loaded), 3)
        self.assertEqual(len(self.manager.cache), 3)

    def test_lru_eviction(self):
        self.manager.request_chunk_load('chunk_1', priority=1.0)
        self.manager.request_chunk_load('chunk_2', priority=2.0)
        self.manager.request_chunk_load('chunk_3', priority=3.0)
        time.sleep(0.2)
        self.manager.request_chunk_load('chunk_4', priority=4.0)
        time.sleep(0.1)
        self.assertLessEqual(len(self.manager.cache), 3)
        # Oldest chunk should be evicted
        self.assertNotIn('chunk_1', self.manager.cache.keys())

    def test_critical_chunk_protection(self):
        self.manager.set_critical_chunks(['chunk_x'])
        self.manager.request_chunk_load('chunk_x', priority=1.0)
        self.manager.request_chunk_load('chunk_y', priority=2.0)
        self.manager.request_chunk_load('chunk_z', priority=3.0)
        time.sleep(0.2)
        self.manager.request_chunk_unload('chunk_x', priority=0.1)
        time.sleep(0.1)
        self.assertIn('chunk_x', self.manager.cache.keys())

    def test_memory_budget_adjustment(self):
        self.manager.set_memory_budget(2)
        self.manager.request_chunk_load('chunk_a', priority=1.0)
        self.manager.request_chunk_load('chunk_b', priority=2.0)
        self.manager.request_chunk_load('chunk_c', priority=3.0)
        time.sleep(0.2)
        self.assertLessEqual(len(self.manager.cache), 2)

if __name__ == '__main__':
    unittest.main() 