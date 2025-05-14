from marshmallow import Schema, fields

class ScheduleSchema(Schema):
    id = fields.Int(dump_only=True)
    npc_id = fields.Int(required=True)
    entries = fields.List(fields.Dict())
    metadata = fields.Dict() 