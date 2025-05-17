from typing import Dict, List, Callable, Any
import time

class Item:
    def __init__(self, item_id: str, quantity: int, decay_rate: float = 0.0, created_at: float = None):
        self.item_id = item_id
        self.quantity = quantity
        self.decay_rate = decay_rate  # per hour
        self.created_at = created_at or time.time()

    def decay(self, current_time: float) -> int:
        hours_passed = (current_time - self.created_at) / 3600
        decayed = int(self.quantity * (1 - self.decay_rate) ** hours_passed)
        return max(decayed, 0)

class InventoryProfile:
    def __init__(self, storage_limit: int, item_types: List[str], decay_rates: Dict[str, float]):
        self.storage_limit = storage_limit
        self.item_types = item_types
        self.decay_rates = decay_rates

class InventoryObserver:
    def __init__(self):
        self.callbacks: List[Callable[[str, Any], None]] = []
    def register(self, callback: Callable[[str, Any], None]):
        self.callbacks.append(callback)
    def notify(self, event: str, data: Any):
        for cb in self.callbacks:
            cb(event, data)

class NPCInventoryManager:
    """
    Manages NPC inventories with storage limits, item decay, specialized profiles, and restocking behaviors.
    """
    def __init__(self, profile_factory: Callable[[str], InventoryProfile]):
        self.inventories: Dict[str, List[Item]] = {}
        self.profiles: Dict[str, InventoryProfile] = {}
        self.profile_factory = profile_factory
        self.observer = InventoryObserver()
        self.last_restock: Dict[str, float] = {}

    def create_inventory(self, npc_id: str, npc_type: str):
        profile = self.profile_factory(npc_type)
        self.profiles[npc_id] = profile
        self.inventories[npc_id] = []
        self.last_restock[npc_id] = time.time()

    def add_item(self, npc_id: str, item_id: str, quantity: int):
        profile = self.profiles[npc_id]
        current_total = sum(item.quantity for item in self.inventories[npc_id])
        if current_total + quantity > profile.storage_limit:
            raise ValueError("Storage limit exceeded")
        decay_rate = profile.decay_rates.get(item_id, 0.0)
        self.inventories[npc_id].append(Item(item_id, quantity, decay_rate))
        self.observer.notify('item_added', {'npc_id': npc_id, 'item_id': item_id, 'quantity': quantity})

    def decay_items(self, npc_id: str):
        now = time.time()
        for item in self.inventories[npc_id]:
            item.quantity = item.decay(now)
        self.inventories[npc_id] = [item for item in self.inventories[npc_id] if item.quantity > 0]

    def restock(self, npc_id: str, market_conditions: Dict[str, float]):
        profile = self.profiles[npc_id]
        now = time.time()
        if now - self.last_restock[npc_id] < 3600:  # restock every hour
            return
        for item_type in profile.item_types:
            if not any(item.item_id == item_type for item in self.inventories[npc_id]):
                quantity = int(market_conditions.get(item_type, 10))
                self.add_item(npc_id, item_type, quantity)
        self.last_restock[npc_id] = now
        self.observer.notify('restocked', {'npc_id': npc_id})

    def get_inventory(self, npc_id: str) -> List[Item]:
        return self.inventories.get(npc_id, [])

    def register_observer(self, callback: Callable[[str, Any], None]):
        self.observer.register(callback) 