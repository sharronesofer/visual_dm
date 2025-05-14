from marshmallow import Schema, fields

class CombatLogSchema(Schema):
    id = fields.Int(dump_only=True)
    combat_id = fields.Int(required=True)
    round_number = fields.Int()
    turn_number = fields.Int()
    actor_id = fields.Int()
    action = fields.Str()
    result = fields.Dict()
    timestamp = fields.DateTime() 