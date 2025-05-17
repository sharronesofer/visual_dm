from typing import Dict, Any
import random

class MarketKnowledgeComponent:
    """
    Represents an NPC's knowledge/expertise in different item categories, affecting price accuracy.
    """
    def __init__(self, expertise: Dict[str, float]):
        # expertise: category -> accuracy (0.0-1.0)
        self.expertise = expertise
    def get_accuracy(self, category: str) -> float:
        return self.expertise.get(category, 0.5)

class BargainingSession:
    """
    Manages a bargaining session between player and NPC, using personality, reputation, and market knowledge.
    """
    def __init__(self, base_price: float, npc_personality: str, player_reputation: float, market_knowledge: MarketKnowledgeComponent, patience: int = 3, flexibility: float = 0.1):
        self.base_price = base_price
        self.npc_personality = npc_personality
        self.player_reputation = player_reputation
        self.market_knowledge = market_knowledge
        self.patience = patience
        self.flexibility = flexibility
        self.counter = 0
        self.last_offer = base_price
        self.success = False

    def player_offer(self, offer: float, item_category: str) -> Dict[str, Any]:
        accuracy = self.market_knowledge.get_accuracy(item_category)
        fair_value = self.base_price * (0.9 + 0.2 * accuracy)  # More knowledge = closer to true value
        min_acceptable = fair_value * (1 - self.flexibility)
        max_acceptable = fair_value * (1 + self.flexibility)
        # Modify by personality
        if self.npc_personality == 'aggressive':
            min_acceptable *= 1.05
        elif self.npc_personality == 'passive':
            min_acceptable *= 0.95
        # Modify by reputation
        if self.player_reputation > 75:
            min_acceptable *= 0.95
        elif self.player_reputation < -50:
            min_acceptable *= 1.10
        # Bargaining logic
        self.counter += 1
        if min_acceptable <= offer <= max_acceptable:
            self.success = True
            self.last_offer = offer
            return {'accepted': True, 'final_price': offer, 'counter': self.counter}
        elif self.counter >= self.patience:
            # NPC walks away
            self.success = False
            return {'accepted': False, 'reason': 'npc_walked_away', 'counter': self.counter}
        else:
            # Counter-offer
            direction = 1 if offer < min_acceptable else -1
            adjustment = abs(offer - fair_value) * self.flexibility * random.uniform(0.5, 1.0)
            counter_offer = self.last_offer + direction * adjustment
            self.last_offer = counter_offer
            return {'accepted': False, 'counter_offer': counter_offer, 'counter': self.counter} 