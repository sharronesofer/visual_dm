import unittest
from visual_client.core.scene.lod import LODLevel, LODMetadata, LODObject, LODManager

class TestLODSystem(unittest.TestCase):
    def setUp(self):
        self.lod0 = LODLevel(0, 'mesh0', 'mat0', 20.0)
        self.lod1 = LODLevel(1, 'mesh1', 'mat1', 50.0)
        self.lod2 = LODLevel(2, 'mesh2', 'mat2', 100.0)
        self.meta = LODMetadata([self.lod0, self.lod1, self.lod2])
        self.obj = LODObject('obj1', (0,0,0), self.meta)
        self.manager = LODManager([self.obj])

    def test_lod_selection(self):
        # Closest: should select LOD0
        self.obj.update_lod((0,0,0))
        self.assertEqual(self.obj.current_lod, self.lod0)
        # Mid distance: should select LOD1
        self.obj.update_lod((30,0,0))
        self.assertEqual(self.obj.current_lod, self.lod1)
        # Far: should select LOD2
        self.obj.update_lod((100,0,0))
        self.assertEqual(self.obj.current_lod, self.lod2)

    def test_lod_transition_callback(self):
        transitions = []
        def cb(obj, old_lod, new_lod):
            transitions.append((old_lod, new_lod))
        self.obj.transition_callback = cb
        self.obj.update_lod((0,0,0))
        self.obj.update_lod((60,0,0))
        self.assertTrue(any(t[1] == self.lod2 for t in transitions))

    def test_manager_update_all(self):
        obj2 = LODObject('obj2', (100,0,0), self.meta)
        self.manager.add_object(obj2)
        self.manager.update_all((0,0,0))
        self.assertEqual(self.obj.current_lod, self.lod0)
        self.assertEqual(obj2.current_lod, self.lod2)

    def test_global_bias(self):
        self.manager.set_global_bias(0.5)
        self.manager.update_all((15,0,0))
        # With bias 0.5, LOD1 threshold is 25, so at 15 should still be LOD0
        self.assertEqual(self.obj.current_lod, self.lod0)
        self.manager.set_global_bias(2.0)
        self.manager.update_all((30,0,0))
        # With bias 2.0, LOD1 threshold is 100, so at 30 should still be LOD0
        self.assertEqual(self.obj.current_lod, self.lod0)

if __name__ == '__main__':
    unittest.main() 