import random
from app.item.models import Item, EnhancementMaterial, ItemHistory
from app.extensions import db

class EnhancementEngine:
    @staticmethod
    def enhance_item(item: Item, material: EnhancementMaterial, user_id: int = None) -> dict:
        # Calculate success probability based on item level and material rarity
        base_success = 0.7 - (item.enhancement_level * 0.1)
        rarity_bonus = {
            'common': 0.0,
            'uncommon': 0.05,
            'rare': 0.1,
            'epic': 0.15,
            'legendary': 0.2
        }
        success_chance = max(0.05, base_success + rarity_bonus.get(material.rarity, 0.0))
        result = {'success': False, 'new_level': item.enhancement_level, 'used_material': material.name}
        # Simulate enhancement attempt
        if random.random() < success_chance:
            item.enhancement_level += 1
            result['success'] = True
            result['new_level'] = item.enhancement_level
            EnhancementEngine._log_history(item, user_id, 'enhancement_success', material)
        else:
            EnhancementEngine._log_history(item, user_id, 'enhancement_failure', material)
        db.session.commit()
        return result

    @staticmethod
    def _log_history(item, user_id, event_type, material):
        history = ItemHistory(
            item_id=item.id,
            owner_id=user_id,
            event_type='enhancement',
            enhancement_event_type=event_type,
            materials_used=[material.name],
            event_data={'enhancement_level': item.enhancement_level},
        )
        db.session.add(history) 