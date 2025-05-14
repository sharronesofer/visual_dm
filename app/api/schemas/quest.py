from marshmallow import Schema, fields

class QuestSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str()
    status = fields.Str()
    progress = fields.Dict()
    assigned_npc_id = fields.Int(allow_none=True)
    assigned_player_id = fields.Int(allow_none=True)
    rewards = fields.List(fields.Dict())
    requirements = fields.List(fields.Dict())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True) 