import unittest
from unittest.mock import Mock
from src.economy.ProfitOptimizationEngine import ProfitOptimizationEngine, RiskProfile

class TestProfitOptimizationEngine(unittest.TestCase):
    def setUp(self):
        self.mock_market = Mock()
        self.mock_market.get_supply.return_value = 100
        self.mock_market.get_demand.return_value = 50
        self.mock_market.get_average_price.return_value = 20.0
        self.engine = ProfitOptimizationEngine(self.mock_market)

    def test_buy_decision_below_threshold(self):
        # Should buy if price is below avg_price
        self.assertTrue(self.engine.make_trade_decision('item1', 15.0, True, {}))

    def test_buy_decision_above_threshold(self):
        # Should not buy if price is above avg_price
        self.assertFalse(self.engine.make_trade_decision('item1', 25.0, True, {}))

    def test_sell_decision_above_threshold(self):
        # Should sell if price is above avg_price
        self.assertTrue(self.engine.make_trade_decision('item1', 25.0, False, {}))

    def test_sell_decision_below_threshold(self):
        # Should not sell if price is below avg_price
        self.assertFalse(self.engine.make_trade_decision('item1', 15.0, False, {}))

    def test_risk_profile_adjustment(self):
        self.engine.set_risk_profile(RiskProfile.AGGRESSIVE)
        self.assertEqual(self.engine.risk_profile, RiskProfile.AGGRESSIVE)
        self.assertAlmostEqual(self.engine.strategy_weights['risk_tolerance'], 1.2)
        self.engine.set_risk_profile(RiskProfile.CONSERVATIVE)
        self.assertAlmostEqual(self.engine.strategy_weights['risk_tolerance'], 0.8)

    def test_competition_awareness(self):
        # If competitor price is lower, engine should use that for buy
        self.engine.update_competition('item1', 10.0)
        self.assertTrue(self.engine.make_trade_decision('item1', 15.0, True, {}))
        # If competitor price is higher, engine should use that for sell
        self.engine.update_competition('item1', 30.0)
        self.assertTrue(self.engine.make_trade_decision('item1', 25.0, False, {}))

    def test_adaptive_learning(self):
        # Simulate a series of good and bad outcomes
        initial_buy = self.engine.strategy_weights['buy_threshold']
        initial_sell = self.engine.strategy_weights['sell_threshold']
        self.engine.adapt_strategy(True, {})  # Good outcome
        self.assertLess(self.engine.strategy_weights['buy_threshold'], initial_buy)
        self.assertGreater(self.engine.strategy_weights['sell_threshold'], initial_sell)
        self.engine.adapt_strategy(False, {})  # Bad outcome
        self.assertGreater(self.engine.strategy_weights['buy_threshold'], initial_buy * (1 - self.engine.learning_rate))
        self.assertLess(self.engine.strategy_weights['sell_threshold'], initial_sell * (1 + self.engine.learning_rate))

if __name__ == '__main__':
    unittest.main() 