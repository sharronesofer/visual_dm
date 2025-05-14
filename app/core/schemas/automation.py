"""
Schema definitions for automation-related requests and responses.
"""

from marshmallow import Schema, fields, validate
from datetime import datetime

class JobSchema(Schema):
    """Schema for job information."""
    id = fields.String(required=True)
    name = fields.String(allow_none=True)
    next_run_time = fields.DateTime(allow_none=True)
    trigger = fields.String(required=True)
    paused = fields.Boolean(required=True)

class TaskSchema(Schema):
    """Schema for task information."""
    id = fields.String(required=True)
    status = fields.String(
        required=True,
        validate=validate.OneOf(['pending', 'running', 'completed', 'failed', 'cancelled'])
    )
    priority = fields.String(
        required=True,
        validate=validate.OneOf(['critical', 'high', 'normal', 'low', 'background'])
    )
    created_at = fields.DateTime(required=True)
    scheduled_for = fields.DateTime(allow_none=True)
    retry_count = fields.Integer(required=True)
    max_retries = fields.Integer(required=True)
    error = fields.String(allow_none=True)
    result = fields.Dict(allow_none=True)

class TaskSubmitSchema(Schema):
    """Schema for task submission."""
    function = fields.String(required=True)
    args = fields.List(fields.Raw(), missing=[])
    kwargs = fields.Dict(keys=fields.String(), values=fields.Raw(), missing={})
    priority = fields.String(
        missing='normal',
        validate=validate.OneOf(['critical', 'high', 'normal', 'low', 'background'])
    )
    max_retries = fields.Integer(missing=3, validate=validate.Range(min=0))
    scheduled_for = fields.DateTime(allow_none=True)

class TaskStatusSchema(Schema):
    """Schema for task status updates."""
    status = fields.String(required=True)
    message = fields.String(required=True)

class ScheduledJobSchema(Schema):
    """Schema for scheduled job information."""
    status = fields.String(required=True)
    job = fields.Nested(JobSchema, allow_none=True)
    message = fields.String(allow_none=True)

class JobTriggerSchema(Schema):
    """Schema for job trigger configuration."""
    function = fields.String(required=True)
    trigger = fields.String(
        required=True,
        validate=validate.OneOf(['date', 'interval', 'cron'])
    )
    trigger_args = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        required=True,
        description=(
            'Arguments for the trigger. Examples:\n'
            '- date: {"run_date": "2024-03-20T15:30:00"}\n'
            '- interval: {"weeks": 1, "days": 2, "hours": 3}\n'
            '- cron: {"year": "*", "month": "*/2", "day": "1", "hour": "5"}'
        )
    ) 