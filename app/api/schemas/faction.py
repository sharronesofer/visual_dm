from marshmallow import Schema, fields

class FactionSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    alignment = fields.Str()
    influence = fields.Int()
    resources = fields.Dict()
    goals = fields.List(fields.Str())
    traits = fields.Dict()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True) 