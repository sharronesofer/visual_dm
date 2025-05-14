import unittest
from visual_client.core.managers.region_manager import RegionManager, REGION_SIZE
from visual_client.core.utils.coordinates import GlobalCoord

class TestRegionManager(unittest.TestCase):
    def setUp(self):
        self.manager = RegionManager()

    def test_region_creation_and_lookup(self):
        pos = GlobalCoord(100, 200)
        region = self.manager.get_region_for_entity(pos)
        self.assertIsNotNone(region)
        self.assertEqual(region.region_coord, (0, 0))
        # Test region at a far coordinate
        far_pos = GlobalCoord(3000, 4000)
        far_region = self.manager.get_region_for_entity(far_pos)
        self.assertEqual(far_region.region_coord, (2, 3))

    def test_region_loading_and_unloading(self):
        pos = GlobalCoord(0, 0)
        self.manager.update_player_position(pos)
        loaded = self.manager.get_loaded_regions()
        self.assertIn((0, 0), loaded)
        # Move player far away
        self.manager.update_player_position(GlobalCoord(REGION_SIZE * 5, REGION_SIZE * 5))
        loaded = self.manager.get_loaded_regions()
        self.assertIn((5, 5), loaded)
        self.assertNotIn((0, 0), loaded)  # Should be unloaded

    def test_region_cache_eviction(self):
        # Load more than CACHE_SIZE regions
        for i in range(20):
            self.manager.get_or_create_region((i, 0))
        self.assertLessEqual(len(self.manager.cache), 16)

    def test_entity_registration(self):
        pos = GlobalCoord(100, 100)
        self.manager.register_entity('entity1', pos)
        region = self.manager.get_region_for_entity(pos)
        self.assertIn('entity1', region.entities)
        self.manager.unregister_entity('entity1', pos)
        self.assertNotIn('entity1', region.entities)

    def test_clear(self):
        pos = GlobalCoord(0, 0)
        self.manager.get_or_create_region((0, 0))
        self.manager.clear()
        self.assertEqual(len(self.manager.regions), 0)
        self.assertEqual(len(self.manager.cache), 0) 