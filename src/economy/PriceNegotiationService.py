from abc import ABC, abstractmethod
from typing import Protocol, List, Dict, Any

class IMarketCondition(Protocol):
    def get_supply(self, item_id: str) -> float:
        ...
    def get_demand(self, item_id: str) -> float:
        ...
    def get_local_market_factor(self, item_id: str, location: str) -> float:
        ...

class INegotiationStyle(ABC):
    @abstractmethod
    def calculate_offer(self, base_price: float, context: Dict[str, Any]) -> float:
        pass
    @abstractmethod
    def respond_to_offer(self, offer: float, context: Dict[str, Any]) -> bool:
        pass

class IReputationModifier(Protocol):
    def get_reputation_adjustment(self, reputation: float) -> float:
        ...

class ReputationTracker:
    """
    Tracks and updates reputation values for NPCs or factions.
    """
    def __init__(self):
        self.reputation: Dict[str, float] = {}

    def get_reputation(self, entity_id: str) -> float:
        return self.reputation.get(entity_id, 0.0)

    def update_reputation(self, entity_id: str, delta: float):
        self.reputation[entity_id] = self.get_reputation(entity_id) + delta

class AggressiveNegotiationStyle(INegotiationStyle):
    def calculate_offer(self, base_price: float, context: Dict[str, Any]) -> float:
        # Low flexibility, low patience, high risk tolerance
        return base_price * 1.2
    def respond_to_offer(self, offer: float, context: Dict[str, Any]) -> bool:
        # Only accept offers close to their own
        return offer >= context.get('min_acceptable', 0.95 * context['base_price'])

class PassiveNegotiationStyle(INegotiationStyle):
    def calculate_offer(self, base_price: float, context: Dict[str, Any]) -> float:
        # High flexibility, high patience, low risk tolerance
        return base_price * 0.95
    def respond_to_offer(self, offer: float, context: Dict[str, Any]) -> bool:
        return offer >= context.get('min_acceptable', 0.85 * context['base_price'])

class FairNegotiationStyle(INegotiationStyle):
    def calculate_offer(self, base_price: float, context: Dict[str, Any]) -> float:
        # Balanced parameters
        return base_price
    def respond_to_offer(self, offer: float, context: Dict[str, Any]) -> bool:
        return offer >= context.get('min_acceptable', 0.90 * context['base_price'])

class SimpleReputationModifier(IReputationModifier):
    def get_reputation_adjustment(self, reputation: float) -> float:
        if reputation > 75:
            return 0.90  # 10% discount for high reputation
        elif reputation < -50:
            return 1.15  # 15% markup for bad reputation
        else:
            return 1.0

class PriceNegotiationService:
    """
    Handles price calculation and negotiation logic for NPC trading.
    """
    def __init__(
        self,
        market_condition: IMarketCondition,
        reputation_modifier: IReputationModifier,
        negotiation_style_factory: Dict[str, INegotiationStyle],
        reputation_tracker: ReputationTracker
    ):
        self.market_condition = market_condition
        self.reputation_modifier = reputation_modifier
        self.negotiation_style_factory = negotiation_style_factory
        self.reputation_tracker = reputation_tracker

    def calculate_base_price(
        self,
        item_id: str,
        item_base_value: float,
        rarity_multiplier: float,
        location: str
    ) -> float:
        supply = self.market_condition.get_supply(item_id)
        demand = self.market_condition.get_demand(item_id)
        local_factor = self.market_condition.get_local_market_factor(item_id, location)
        if demand == 0:
            demand = 1e-3  # Prevent division by zero
        base_price = item_base_value * rarity_multiplier * (supply / demand) * local_factor
        return max(base_price, 0.01)

    def get_negotiation_style(self, personality: str) -> INegotiationStyle:
        return self.negotiation_style_factory.get(personality, FairNegotiationStyle())

    def negotiate_price(
        self,
        item_id: str,
        item_base_value: float,
        rarity_multiplier: float,
        location: str,
        npc_personality: str,
        player_id: str
    ) -> float:
        base_price = self.calculate_base_price(item_id, item_base_value, rarity_multiplier, location)
        reputation = self.reputation_tracker.get_reputation(player_id)
        rep_adjustment = self.reputation_modifier.get_reputation_adjustment(reputation)
        negotiation_style = self.get_negotiation_style(npc_personality)
        context = {
            'base_price': base_price,
            'min_acceptable': base_price * 0.85  # Example threshold
        }
        offer = negotiation_style.calculate_offer(base_price, context)
        final_price = offer * rep_adjustment
        return max(final_price, 0.01) 