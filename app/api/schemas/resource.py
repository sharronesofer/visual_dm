from marshmallow import Schema, fields

class ResourceSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    amount = fields.Float()
    price = fields.Float()
    region_id = fields.Int(allow_none=True)
    faction_id = fields.Int(allow_none=True)
    last_updated = fields.Str() 