from datetime import datetime
from app.item.models import Item, ItemHistory, ItemEvent
from app.extensions import db

class ItemHistoryEngine:
    @staticmethod
    def log_event(item: Item, event_type: str, event_data: dict = None, owner_id: int = None):
        history = ItemHistory(
            item_id=item.id,
            owner_id=owner_id,
            event_type=event_type,
            event_data=event_data or {},
            timestamp=datetime.utcnow()
        )
        db.session.add(history)
        db.session.commit()

    @staticmethod
    def log_item_event(item: Item, event_type: str, description: str = None):
        event = ItemEvent(
            item_id=item.id,
            event_type=event_type,
            description=description,
            occurred_at=datetime.utcnow()
        )
        db.session.add(event)
        db.session.commit()

    @staticmethod
    def use_item(item: Item, user_id: int = None):
        if item.durability > 0:
            item.durability -= 1
            item.usage_count += 1
            db.session.commit()
            ItemHistoryEngine.log_event(item, 'used', {'usage_count': item.usage_count, 'durability': item.durability}, owner_id=user_id)
            if item.durability == 0:
                ItemHistoryEngine.log_event(item, 'broken', {}, owner_id=user_id)
        else:
            ItemHistoryEngine.log_event(item, 'attempted_use_broken', {}, owner_id=user_id)

    @staticmethod
    def repair_item(item: Item, amount: int = None):
        if amount is None:
            item.durability = item.max_durability
        else:
            item.durability = min(item.max_durability, item.durability + amount)
        db.session.commit()
        ItemHistoryEngine.log_event(item, 'repaired', {'durability': item.durability})

    @staticmethod
    def generate_lore(item: Item) -> str:
        events = ItemHistory.query.filter_by(item_id=item.id).order_by(ItemHistory.timestamp).all()
        lore = [f"Item '{item.name}' history:"]
        for e in events:
            ts = e.timestamp.strftime('%Y-%m-%d')
            if e.event_type == 'used':
                lore.append(f"- Used on {ts} (durability: {e.event_data.get('durability')})")
            elif e.event_type == 'broken':
                lore.append(f"- Broke on {ts}")
            elif e.event_type == 'repaired':
                lore.append(f"- Repaired on {ts} (durability: {e.event_data.get('durability')})")
            elif e.event_type == 'ownership_change':
                lore.append(f"- Ownership changed on {ts} (owner_id: {e.owner_id})")
            else:
                lore.append(f"- {e.event_type} on {ts}")
        return '\n'.join(lore) 