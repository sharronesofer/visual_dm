"""
In-memory market data store for backward compatibility and testing.
Implements the same interface as the repository layer for seamless switching.
"""
from typing import List, Dict, Optional

class InMemoryMarketItemStore:
    def __init__(self):
        self.items: Dict[int, dict] = {}

    def get_by_id(self, id: int) -> Optional[dict]:
        return self.items.get(id)

    def get_all(self) -> List[dict]:
        return list(self.items.values())

    def create(self, obj_in: dict) -> dict:
        self.items[obj_in["id"]] = obj_in
        return obj_in

    def update(self, id: int, obj_in: dict) -> Optional[dict]:
        if id in self.items:
            self.items[id].update(obj_in)
            return self.items[id]
        return None

    def delete(self, id: int) -> bool:
        return self.items.pop(id, None) is not None

# Repeat for TradeOffer, Transaction, PriceHistory as needed 