from marshmallow import Schema, fields, validate

class ResourceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    amount = fields.Float()
    price = fields.Float()
    region_id = fields.Int(allow_none=True)
    faction_id = fields.Int(allow_none=True)
    last_updated = fields.Str()

class InventoryItemSchema(Schema):
    """
    Marshmallow schema for serializing InventoryItem/InventoryModel.
    Matches the standardized type system and model fields.
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    category = fields.Str(validate=validate.OneOf([
        'weapon', 'armor', 'consumable', 'quest', 'misc'
    ]))
    value = fields.Int(allow_none=True)
    weight = fields.Float(allow_none=True)
    stack_size = fields.Int()
    max_stack = fields.Int()
    properties = fields.Dict()
    requirements = fields.Dict()
    is_equippable = fields.Bool()
    is_consumable = fields.Bool()
    is_quest_item = fields.Bool()
    owner_id = fields.Int(allow_none=True)
    item_id = fields.Int(allow_none=True) 