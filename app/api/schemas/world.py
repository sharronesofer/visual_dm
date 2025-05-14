from marshmallow import Schema, fields

class WorldSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    current_era = fields.Str()
    global_tension = fields.Int()
    major_events = fields.List(fields.Int())
    kingdom_count = fields.Int()
    last_major_shift = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True) 