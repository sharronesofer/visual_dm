import unittest
from unittest.mock import patch
from src.economy.NPCInventoryManager import NPCInventoryManager, InventoryProfile

class TestNPCInventoryManager(unittest.TestCase):
    def setUp(self):
        def profile_factory(npc_type):
            if npc_type == 'merchant':
                return InventoryProfile(storage_limit=100, item_types=['apple', 'sword'], decay_rates={'apple': 0.1, 'sword': 0.0})
            return InventoryProfile(storage_limit=50, item_types=['apple'], decay_rates={'apple': 0.2})
        self.manager = NPCInventoryManager(profile_factory)
        self.npc_id = 'npc1'
        self.manager.create_inventory(self.npc_id, 'merchant')

    def test_add_item_within_limit(self):
        self.manager.add_item(self.npc_id, 'apple', 10)
        self.assertEqual(len(self.manager.get_inventory(self.npc_id)), 1)

    def test_add_item_exceeds_limit(self):
        self.manager.add_item(self.npc_id, 'apple', 90)
        with self.assertRaises(ValueError):
            self.manager.add_item(self.npc_id, 'sword', 20)

    @patch('time.time', return_value=10000)
    def test_decay_items(self, mock_time):
        self.manager.add_item(self.npc_id, 'apple', 10)
        # Simulate 10 hours later
        with patch('time.time', return_value=10000 + 36000):
            self.manager.decay_items(self.npc_id)
            items = self.manager.get_inventory(self.npc_id)
            self.assertTrue(all(item.quantity <= 10 for item in items))

    def test_specialized_inventory_profile(self):
        self.assertEqual(self.manager.profiles[self.npc_id].storage_limit, 100)
        self.assertIn('apple', self.manager.profiles[self.npc_id].item_types)
        self.assertIn('sword', self.manager.profiles[self.npc_id].item_types)

    @patch('time.time', return_value=10000)
    def test_restock_behavior(self, mock_time):
        # Remove all items
        self.manager.inventories[self.npc_id] = []
        # Simulate market conditions
        market_conditions = {'apple': 5, 'sword': 2}
        # Force last_restock to a time far in the past
        self.manager.last_restock[self.npc_id] = 0
        with patch('time.time', return_value=10000 + 4000):
            self.manager.restock(self.npc_id, market_conditions)
            items = self.manager.get_inventory(self.npc_id)
            self.assertTrue(any(item.item_id == 'apple' for item in items))
            self.assertTrue(any(item.item_id == 'sword' for item in items))

if __name__ == '__main__':
    unittest.main() 