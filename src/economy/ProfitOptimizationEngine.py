from typing import Dict, List, Any
import random

class RiskProfile:
    CONSERVATIVE = 'conservative'
    BALANCED = 'balanced'
    AGGRESSIVE = 'aggressive'

class TradeHistory:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
    def record(self, trade: Dict[str, Any]):
        self.history.append(trade)
    def get_recent_trades(self, n=10):
        return self.history[-n:]

class ProfitOptimizationEngine:
    """
    AI-driven engine for maximizing NPC profits via market analysis, adaptive strategies, and competition awareness.
    """
    def __init__(self, market_data: Any, risk_profile: str = RiskProfile.BALANCED):
        self.market_data = market_data
        self.risk_profile = risk_profile
        self.trade_history = TradeHistory()
        self.competitor_prices: Dict[str, float] = {}
        self.learning_rate = 0.1
        self.strategy_weights = {
            'buy_threshold': 1.0,
            'sell_threshold': 1.0,
            'risk_tolerance': 1.0
        }

    def analyze_market(self, item_id: str) -> Dict[str, float]:
        supply = self.market_data.get_supply(item_id)
        demand = self.market_data.get_demand(item_id)
        avg_price = self.market_data.get_average_price(item_id)
        return {'supply': supply, 'demand': demand, 'avg_price': avg_price}

    def decide_trade(self, item_id: str, current_price: float, is_buy: bool) -> bool:
        market = self.analyze_market(item_id)
        threshold = self.strategy_weights['buy_threshold'] if is_buy else self.strategy_weights['sell_threshold']
        if is_buy:
            # Buy if price is below threshold * avg_price
            return current_price < threshold * market['avg_price']
        else:
            # Sell if price is above threshold * avg_price
            return current_price > threshold * market['avg_price']

    def update_competition(self, item_id: str, competitor_price: float):
        self.competitor_prices[item_id] = competitor_price

    def adapt_strategy(self, outcome: bool, context: Dict[str, Any]):
        # Simple reinforcement: reward if outcome is good, penalize if not
        if outcome:
            self.strategy_weights['buy_threshold'] *= (1 - self.learning_rate)
            self.strategy_weights['sell_threshold'] *= (1 + self.learning_rate)
        else:
            self.strategy_weights['buy_threshold'] *= (1 + self.learning_rate)
            self.strategy_weights['sell_threshold'] *= (1 - self.learning_rate)

    def set_risk_profile(self, profile: str):
        self.risk_profile = profile
        if profile == RiskProfile.CONSERVATIVE:
            self.strategy_weights['risk_tolerance'] = 0.8
        elif profile == RiskProfile.AGGRESSIVE:
            self.strategy_weights['risk_tolerance'] = 1.2
        else:
            self.strategy_weights['risk_tolerance'] = 1.0

    def make_trade_decision(self, item_id: str, current_price: float, is_buy: bool, context: Dict[str, Any]) -> bool:
        # Incorporate risk tolerance and competition
        competitor_price = self.competitor_prices.get(item_id, current_price)
        adjusted_price = current_price
        if is_buy and competitor_price < current_price:
            adjusted_price = competitor_price
        elif not is_buy and competitor_price > current_price:
            adjusted_price = competitor_price
        # Add randomness for learning
        if random.random() < 0.05 * self.strategy_weights['risk_tolerance']:
            return random.choice([True, False])
        decision = self.decide_trade(item_id, adjusted_price, is_buy)
        self.trade_history.record({'item_id': item_id, 'price': current_price, 'is_buy': is_buy, 'decision': decision})
        self.adapt_strategy(decision, context)
        return decision 