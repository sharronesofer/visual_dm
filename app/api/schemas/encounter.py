from marshmallow import Schema, fields

class EncounterSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    is_active = fields.Bool()
    round_number = fields.Int()
    status = fields.Str()
    initiative_order = fields.List(fields.Int())
    current_turn = fields.Int()
    environment = fields.Dict()
    effects = fields.Dict()
    log = fields.List(fields.Dict())
    location_id = fields.Int(required=True)
    participants = fields.List(fields.Dict())
    actions = fields.List(fields.Dict())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True) 