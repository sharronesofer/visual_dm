from marshmallow import Schema, fields

class RelationshipSchema(Schema):
    id = fields.Int(dump_only=True)
    source_npc_id = fields.Int(required=True)
    target_npc_id = fields.Int(required=True)
    value = fields.Float()
    type = fields.Str()
    metadata = fields.Dict() 