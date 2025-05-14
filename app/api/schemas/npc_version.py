"""
Schema for NPC version model serialization.
"""

from marshmallow import Schema, fields, validate

class NPCVersionSchema(Schema):
    """Schema for NPC version model."""
    id = fields.Int(dump_only=True)
    npc_id = fields.Int(required=True)
    version_number = fields.Int(required=True)
    code_version_id = fields.Int(allow_none=True)
    
    # Version data
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    level = fields.Int()
    disposition = fields.Str()
    base_disposition = fields.Float()
    level_requirement = fields.Int()
    interaction_cooldown = fields.Int()
    current_location_id = fields.Int(allow_none=True)
    home_location_id = fields.Int(allow_none=True)
    
    # JSON fields
    schedule = fields.List(fields.Dict())
    dialogue_options = fields.Dict()
    behavior_flags = fields.Dict()
    inventory = fields.List(fields.Dict())
    trade_inventory = fields.List(fields.Dict())
    available_quests = fields.List(fields.Int())
    completed_quests = fields.List(fields.Int())
    goals = fields.Dict()
    relationships = fields.Dict()
    memories = fields.List(fields.Dict())
    
    # Change tracking
    change_description = fields.Str(required=True)
    change_type = fields.Str(required=True, validate=validate.OneOf([
        'creation', 'update', 'deletion', 'revert'
    ]))
    changed_fields = fields.List(fields.Str())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class NPCVersionComparisonSchema(Schema):
    """Schema for version comparison results."""
    field = fields.Str(required=True)
    version1 = fields.Raw(required=True)
    version2 = fields.Raw(required=True)

class NPCVersionHistorySchema(Schema):
    """Schema for version history entries."""
    version_number = fields.Int(required=True)
    change_type = fields.Str(required=True)
    change_description = fields.Str(required=True)
    changed_fields = fields.List(fields.Str())
    created_at = fields.DateTime(required=True)
    code_version_id = fields.Int(allow_none=True) 