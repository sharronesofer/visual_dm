import unittest
from unittest.mock import Mock
from src.economy.PriceNegotiationService import (
    PriceNegotiationService,
    AggressiveNegotiationStyle,
    PassiveNegotiationStyle,
    FairNegotiationStyle,
    SimpleReputationModifier,
    ReputationTracker
)

class TestPriceNegotiationService(unittest.TestCase):
    def setUp(self):
        self.mock_market = Mock()
        self.mock_market.get_supply.return_value = 100
        self.mock_market.get_demand.return_value = 50
        self.mock_market.get_local_market_factor.return_value = 1.0
        self.reputation_tracker = ReputationTracker()
        self.negotiation_styles = {
            'aggressive': AggressiveNegotiationStyle(),
            'passive': PassiveNegotiationStyle(),
            'fair': FairNegotiationStyle()
        }
        self.rep_modifier = SimpleReputationModifier()
        self.service = PriceNegotiationService(
            market_condition=self.mock_market,
            reputation_modifier=self.rep_modifier,
            negotiation_style_factory=self.negotiation_styles,
            reputation_tracker=self.reputation_tracker
        )

    def test_base_price_calculation(self):
        price = self.service.calculate_base_price(
            item_id='item1',
            item_base_value=100.0,
            rarity_multiplier=1.5,
            location='market1'
        )
        expected = 100.0 * 1.5 * (100/50) * 1.0
        self.assertAlmostEqual(price, expected)

    def test_aggressive_negotiation(self):
        price = self.service.negotiate_price(
            item_id='item1',
            item_base_value=100.0,
            rarity_multiplier=1.0,
            location='market1',
            npc_personality='aggressive',
            player_id='player1'
        )
        # Aggressive style: offer = base_price * 1.2, rep = 1.0
        base = self.service.calculate_base_price('item1', 100.0, 1.0, 'market1')
        self.assertAlmostEqual(price, base * 1.2)

    def test_passive_negotiation(self):
        price = self.service.negotiate_price(
            item_id='item1',
            item_base_value=100.0,
            rarity_multiplier=1.0,
            location='market1',
            npc_personality='passive',
            player_id='player1'
        )
        base = self.service.calculate_base_price('item1', 100.0, 1.0, 'market1')
        self.assertAlmostEqual(price, base * 0.95)

    def test_fair_negotiation(self):
        price = self.service.negotiate_price(
            item_id='item1',
            item_base_value=100.0,
            rarity_multiplier=1.0,
            location='market1',
            npc_personality='fair',
            player_id='player1'
        )
        base = self.service.calculate_base_price('item1', 100.0, 1.0, 'market1')
        self.assertAlmostEqual(price, base)

    def test_reputation_discount(self):
        self.reputation_tracker.update_reputation('player1', 100)
        price = self.service.negotiate_price(
            item_id='item1',
            item_base_value=100.0,
            rarity_multiplier=1.0,
            location='market1',
            npc_personality='fair',
            player_id='player1'
        )
        base = self.service.calculate_base_price('item1', 100.0, 1.0, 'market1')
        self.assertAlmostEqual(price, base * 0.90)

    def test_reputation_penalty(self):
        self.reputation_tracker.update_reputation('player1', -100)
        price = self.service.negotiate_price(
            item_id='item1',
            item_base_value=100.0,
            rarity_multiplier=1.0,
            location='market1',
            npc_personality='fair',
            player_id='player1'
        )
        base = self.service.calculate_base_price('item1', 100.0, 1.0, 'market1')
        self.assertAlmostEqual(price, base * 1.15)

if __name__ == '__main__':
    unittest.main() 