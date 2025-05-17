import unittest
from visual_client.core.scene.partitioning import SpatialPartitionTree, SceneChunk, ChunkMetadata

class TestSpatialPartitionTree(unittest.TestCase):
    def setUp(self):
        # 3D bounds: (min, max)
        self.bounds = ((0.0, 0.0, 0.0), (100.0, 100.0, 100.0))
        self.tree = SpatialPartitionTree(self.bounds, max_depth=3, min_size=10.0, is_3d=True)

    def test_tree_construction(self):
        # Root node should cover the full bounds
        self.assertEqual(self.tree.root.bounds, self.bounds)
        self.assertTrue(self.tree.root.is_leaf or self.tree.root.children is not None)

    def test_entity_insertion_and_query(self):
        entity = {'id': 1}
        pos = (50.0, 50.0, 50.0)
        self.tree.insert_entity(entity, pos)
        # Query a region that includes the entity
        region = ((40.0, 40.0, 40.0), (60.0, 60.0, 60.0))
        chunks = self.tree.query_chunks(region)
        found = any(entity in chunk.entities for chunk in chunks)
        self.assertTrue(found)

    def test_priority_chunks(self):
        # Insert entities at various distances
        for i in range(5):
            pos = (10.0 * i, 10.0 * i, 10.0 * i)
            self.tree.insert_entity({'id': i}, pos)
        player_pos = (0.0, 0.0, 0.0)
        chunks = self.tree.get_priority_chunks(player_pos, max_chunks=3)
        self.assertLessEqual(len(chunks), 3)
        # Chunks should be sorted by distance to player
        dists = [sum((c.center()[j] - player_pos[j]) ** 2 for j in range(3)) for c in chunks]
        self.assertEqual(dists, sorted(dists))

    def test_chunk_contains(self):
        chunk = SceneChunk(((0,0,0), (10,10,10)))
        self.assertTrue(chunk.contains((5,5,5)))
        self.assertFalse(chunk.contains((15,5,5)))

def test_chunk_metadata_state_and_priority():
    meta = ChunkMetadata(dependencies=["a", "b"], load_priority=1.0, streaming_state="unloaded", lod_level=0)
    assert meta.streaming_state == "unloaded"
    meta.set_priority(2.5)
    assert meta.load_priority == 2.5
    meta.set_streaming_state("loading")
    assert meta.streaming_state == "loading"
    meta.set_lod(1)
    assert meta.lod_level == 1

def test_chunk_metadata_dependencies():
    meta = ChunkMetadata(dependencies=["dep1", "dep2"])
    assert "dep1" in meta.dependencies
    meta.dependencies.append("dep3")
    assert "dep3" in meta.dependencies

if __name__ == '__main__':
    unittest.main() 