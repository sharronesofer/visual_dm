"""
Schemas for version control related models.
"""

from marshmallow import Schema, fields, post_dump, validate
from datetime import datetime

class LocationVersionSchema(Schema):
    """Schema for LocationVersion model."""
    id = fields.Int(dump_only=True)
    location_id = fields.Int(required=True)
    version_number = fields.Int(required=True)
    data = fields.Dict(required=True)
    change_type = fields.Str(required=True)
    change_reason = fields.Str(required=True)
    changed_by = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    
    @post_dump
    def format_dates(self, data, **kwargs):
        """Format datetime fields to ISO format."""
        if 'created_at' in data and data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        return data

class LocationChangeLogSchema(Schema):
    """Schema for LocationChangeLog model."""
    id = fields.Int(dump_only=True)
    version_id = fields.Int(required=True)
    field_name = fields.Str(required=True)
    old_value = fields.Raw(allow_none=True)
    new_value = fields.Raw(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    
    @post_dump
    def format_dates(self, data, **kwargs):
        """Format datetime fields to ISO format."""
        if 'created_at' in data and data['created_at']:
            data['created_at'] = data['created_at'].isoformat()
        return data

class VersionControlSchema(Schema):
    """
    Marshmallow schema for serializing VersionControl model.
    Matches the standardized type system and model fields.
    """
    id = fields.Int(dump_only=True)
    version = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    version_type = fields.Str(validate=validate.OneOf([
        'migration', 'feature', 'bugfix', 'release'
    ]))
    metadata = fields.Dict()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True) 