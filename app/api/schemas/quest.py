from marshmallow import Schema, fields, validate
from datetime import datetime

class QuestSchema(Schema):
    """
    Marshmallow schema for serializing Quest model.
    Matches the standardized type system and model fields.
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf([
        'not_started', 'in_progress', 'completed', 'failed'
    ]))
    objectives = fields.List(fields.Dict(), required=True)
    rewards = fields.Dict()
    requirements = fields.Dict()
    is_main_quest = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    party_id = fields.Int(allow_none=True) 