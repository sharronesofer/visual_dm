import random
from datetime import datetime
from app.item.models import Item, EnchantmentType, MagicalEffect, ItemEnchantment, Rarity
from app.extensions import db

RARITY_WEIGHTS = [
    (Rarity.COMMON.value, 0.5),
    (Rarity.UNCOMMON.value, 0.25),
    (Rarity.RARE.value, 0.15),
    (Rarity.EPIC.value, 0.07),
    (Rarity.LEGENDARY.value, 0.03)
]

class MagicalItemGenerator:
    def __init__(self):
        pass

    def generate_magical_item(self, item: Item) -> Item:
        rarity = self._choose_rarity()
        enchantment_type = self._choose_enchantment_type()
        effect = self._choose_effect(enchantment_type)
        magnitude = self._scale_magnitude(effect, rarity)
        item_enchantment = ItemEnchantment(
            item_id=item.id,
            enchantment_type_id=enchantment_type.id,
            effect_id=effect.id,
            magnitude=magnitude,
            rarity=rarity,
            applied_at=datetime.utcnow()
        )
        db.session.add(item_enchantment)
        db.session.commit()
        return item

    def _choose_rarity(self):
        population, weights = zip(*RARITY_WEIGHTS)
        return random.choices(population, weights=weights)[0]

    def _choose_enchantment_type(self):
        types = EnchantmentType.query.all()
        return random.choice(types)

    def _choose_effect(self, enchantment_type):
        allowed_ids = enchantment_type.allowed_effects or []
        if allowed_ids:
            effects = MagicalEffect.query.filter(MagicalEffect.id.in_(allowed_ids)).all()
        else:
            effects = MagicalEffect.query.all()
        return random.choice(effects)

    def _scale_magnitude(self, effect, rarity):
        min_val, max_val = (effect.magnitude_range or [1, 10])
        rarity_scale = {
            Rarity.COMMON.value: 1.0,
            Rarity.UNCOMMON.value: 1.2,
            Rarity.RARE.value: 1.5,
            Rarity.EPIC.value: 2.0,
            Rarity.LEGENDARY.value: 3.0
        }
        base = random.randint(min_val, max_val)
        return int(base * rarity_scale.get(rarity, 1.0)) 