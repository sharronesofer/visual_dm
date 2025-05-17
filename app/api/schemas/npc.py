from marshmallow import Schema, fields, validate

class NPCSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    level = fields.Int()
    disposition = fields.Str()
    base_disposition = fields.Float()
    level_requirement = fields.Int()
    interaction_cooldown = fields.Int()
    last_interaction = fields.DateTime(allow_none=True)
    current_location_id = fields.Int(allow_none=True)
    home_location_id = fields.Int(allow_none=True)
    schedule = fields.List(fields.Dict())
    dialogue_options = fields.Dict()
    behavior_flags = fields.Dict()
    inventory = fields.List(fields.Dict())
    gold = fields.Int()
    trade_inventory = fields.List(fields.Dict())
    available_quests = fields.List(fields.Int())
    completed_quests = fields.List(fields.Int())
    combat_stats_id = fields.Int(allow_none=True)
    goals = fields.Dict()
    relationships = fields.Dict()
    memories = fields.List(fields.Dict())

class SpellSchema(Schema):
    """
    Marshmallow schema for serializing Spell model.
    Matches the standardized type system and model fields.
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    spell_type = fields.Str(validate=validate.OneOf([
        'offensive', 'defensive', 'utility', 'healing'
    ]))
    mana_cost = fields.Float()
    cooldown = fields.Float()
    effects = fields.Dict()
    requirements = fields.Dict()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    owner_id = fields.Int(allow_none=True)

class MagicModelSchema(Schema):
    """
    Marshmallow schema for serializing MagicModel.
    Matches the standardized type system and model fields.
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    magic_type = fields.Str(validate=validate.OneOf([
        'elemental', 'arcane', 'divine', 'dark', 'light'
    ]))
    power = fields.Float()
    cost = fields.Float()
    effects = fields.Dict()
    requirements = fields.Dict()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    owner_id = fields.Int(allow_none=True) 