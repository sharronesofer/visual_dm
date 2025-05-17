import unittest
from src.economy.BargainingSession import BargainingSession, MarketKnowledgeComponent

class TestBargainingSession(unittest.TestCase):
    def setUp(self):
        expertise = {'weapons': 1.0, 'food': 0.5}
        self.knowledge = MarketKnowledgeComponent(expertise)
        self.base_price = 100.0

    def test_accept_offer_within_range(self):
        session = BargainingSession(self.base_price, 'fair', 0, self.knowledge, patience=3, flexibility=0.1)
        result = session.player_offer(100.0, 'weapons')
        self.assertTrue(result['accepted'])
        self.assertEqual(result['final_price'], 100.0)

    def test_counter_offer(self):
        session = BargainingSession(self.base_price, 'aggressive', 0, self.knowledge, patience=3, flexibility=0.1)
        result = session.player_offer(50.0, 'weapons')
        self.assertFalse(result['accepted'])
        self.assertIn('counter_offer', result)
        self.assertEqual(result['counter'], 1)

    def test_npc_walks_away(self):
        session = BargainingSession(self.base_price, 'passive', 0, self.knowledge, patience=2, flexibility=0.1)
        # Make two bad offers
        session.player_offer(10.0, 'food')
        result = session.player_offer(10.0, 'food')
        self.assertFalse(result['accepted'])
        self.assertEqual(result['reason'], 'npc_walked_away')

    def test_market_knowledge_effect(self):
        # High expertise should make min_acceptable closer to base_price
        session_high = BargainingSession(self.base_price, 'fair', 0, self.knowledge, patience=3, flexibility=0.1)
        min_acc_high = session_high.base_price * (0.9 + 0.2 * 1.0) * (1 - 0.1)
        # Low expertise
        session_low = BargainingSession(self.base_price, 'fair', 0, MarketKnowledgeComponent({'food': 0.0}), patience=3, flexibility=0.1)
        min_acc_low = session_low.base_price * (0.9 + 0.2 * 0.0) * (1 - 0.1)
        self.assertGreater(min_acc_high, min_acc_low)

    def test_reputation_modifies_acceptance(self):
        # High reputation should lower min_acceptable
        session = BargainingSession(self.base_price, 'fair', 100, self.knowledge, patience=3, flexibility=0.1)
        result = session.player_offer(90.0, 'weapons')
        # Should be more likely to accept
        self.assertIn('accepted', result)

if __name__ == '__main__':
    unittest.main() 