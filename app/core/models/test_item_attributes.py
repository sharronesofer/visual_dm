import pytest
from app.core.models.item import AttributeContainer, Item

def test_attribute_assignment():
    ac = AttributeContainer({'damage': 10, 'weight': 2.5})
    assert ac.get('damage') == 10
    ac.set('damage', 15)
    assert ac.get('damage') == 15
    assert ac['weight'] == 2.5
    ac['weight'] = 3.0
    assert ac['weight'] == 3.0

def test_attribute_inheritance():
    parent = AttributeContainer({'rarity': 'rare', 'value': 100})
    child = AttributeContainer({'damage': 5}, parent=parent)
    assert child.get('damage') == 5
    assert child.get('rarity') == 'rare'
    assert child.get('value') == 100

def test_attribute_composition():
    comp1 = AttributeContainer({'fire': 10})
    comp2 = AttributeContainer({'ice': 5})
    ac = AttributeContainer({'damage': 7}, compositions=[comp1, comp2])
    assert ac.get('damage') == 7
    assert ac.get('fire') == 10
    assert ac.get('ice') == 5

def test_attribute_validation():
    ac = AttributeContainer({'damage': 10, 'weight': 2.5, 'rarity': 'common'})
    schema = {
        'damage': {'type': int, 'min': 0, 'max': 100, 'required': True},
        'weight': {'type': float, 'min': 0.0, 'max': 50.0, 'required': True},
        'rarity': {'type': str, 'allowed': ['common', 'rare'], 'required': True}
    }
    assert ac.validate(schema) is True
    # Test required
    ac2 = AttributeContainer({'damage': 10})
    with pytest.raises(ValueError):
        ac2.validate(schema)
    # Test type
    ac3 = AttributeContainer({'damage': 'high', 'weight': 2.5, 'rarity': 'common'})
    with pytest.raises(TypeError):
        ac3.validate(schema)
    # Test min/max
    ac4 = AttributeContainer({'damage': -1, 'weight': 2.5, 'rarity': 'common'})
    with pytest.raises(ValueError):
        ac4.validate(schema)
    # Test allowed
    ac5 = AttributeContainer({'damage': 10, 'weight': 2.5, 'rarity': 'epic'})
    with pytest.raises(ValueError):
        ac5.validate(schema)

def test_attribute_serialization():
    ac = AttributeContainer({'damage': 10, 'weight': 2.5})
    d = ac.to_dict()
    assert d == {'damage': 10, 'weight': 2.5}
    ac2 = AttributeContainer.from_dict(d)
    assert ac2.get('damage') == 10
    assert ac2.get('weight') == 2.5

def test_item_template_creation():
    item = Item.create_from_template('basic_weapon')
    assert item.name == 'Basic Sword'
    assert item.type == 'weapon'
    assert item.stats['damage'] == 5
    assert item.stats['durability'] == 100
    assert item.properties['effects'] == []
    # Override
    item2 = Item.create_from_template('basic_weapon', overrides={'name': 'Epic Sword', 'stats': {'damage': 50}})
    assert item2.name == 'Epic Sword'
    assert item2.stats['damage'] == 50
    # Serialization
    d = item2.to_dict()
    assert d['name'] == 'Epic Sword'
    assert d['attributes']['damage'] == 50
    assert d['attributes']['durability'] == 100 