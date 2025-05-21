import unittest
import tempfile
import shutil
import asyncio
from backend.app.core.world_state.world_state_manager import WorldStateManager, StateCategory, WorldRegion

class TestWorldStateManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        WorldStateManager._instance = None
        self.manager = WorldStateManager(storage_path=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        WorldStateManager._instance = None

    async def test_set_and_get(self):
        await self.manager.set("population.city1", 1000, category=StateCategory.POLITICAL, region=WorldRegion.CENTRAL)
        val = await self.manager.get("population.city1")
        self.assertEqual(val, 1000)
        # Test default
        missing = await self.manager.get("does.not.exist", default=42)
        self.assertEqual(missing, 42)

    async def test_delete(self):
        await self.manager.set("foo.bar", 123)
        deleted = await self.manager.delete("foo.bar")
        self.assertTrue(deleted)
        val = await self.manager.get("foo.bar")
        self.assertIsNone(val)
        # Deleting non-existent key
        deleted2 = await self.manager.delete("not.there")
        self.assertFalse(deleted2)

    async def test_query(self):
        await self.manager.set("a", 1, category=StateCategory.POLITICAL, region=WorldRegion.CENTRAL, tags=["x"])
        await self.manager.set("b", 2, category=StateCategory.POLITICAL, region=WorldRegion.CENTRAL, tags=["y"])
        await self.manager.set("c", 3, category=StateCategory.ECONOMIC, region=WorldRegion.EASTERN, tags=["x"])
        # Query by category
        res = await self.manager.query(category=StateCategory.POLITICAL)
        self.assertIn("a", res)
        self.assertIn("b", res)
        self.assertNotIn("c", res)
        # Query by region
        res2 = await self.manager.query(region=WorldRegion.EASTERN)
        self.assertIn("c", res2)
        # Query by tag
        res3 = await self.manager.query(tags=["x"])
        self.assertIn("a", res3)
        self.assertIn("c", res3)
        # Query by prefix
        res4 = await self.manager.query(prefix="a")
        self.assertIn("a", res4)
        self.assertNotIn("b", res4)

    async def test_get_history_and_metadata(self):
        await self.manager.set("hist.test", 1)
        await self.manager.set("hist.test", 2)
        hist = await self.manager.get_history("hist.test")
        self.assertGreaterEqual(len(hist), 2)
        meta = await self.manager.get_state_metadata("hist.test")
        self.assertIsInstance(meta, dict)
        self.assertEqual(meta["key"], "hist.test")

    def test_sync_methods(self):
        self.manager.set_sync("sync.key", 99)
        val = self.manager.get_sync("sync.key")
        self.assertEqual(val, 99)
        missing = self.manager.get_sync("not.sync", default=123)
        self.assertEqual(missing, 123) 
