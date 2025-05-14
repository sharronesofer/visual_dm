"""
World state schemas for request/response validation and Swagger documentation.
"""

from marshmallow import Schema, fields, validate
from datetime import datetime

class WorldStateSchema(Schema):
    """Schema for world state data."""
    time = fields.DateTime(dump_only=True, metadata={
        "description": "Current in-game time",
        "example": "2024-03-15T12:34:56Z"
    })
    weather = fields.Dict(metadata={
        "description": "Current weather conditions",
        "example": {
            "condition": "clear",
            "temperature": 20,
            "wind_speed": 5,
            "precipitation": 0
        }
    })
    active_events = fields.List(fields.Dict(), metadata={
        "description": "Currently active world events",
        "example": [
            {
                "id": "event_123",
                "type": "festival",
                "location": "starting_town",
                "duration": 3600
            }
        ]
    })
    faction_states = fields.Dict(metadata={
        "description": "Current state of world factions",
        "example": {
            "faction_123": {
                "influence": 75,
                "disposition": "friendly"
            }
        }
    })
    region_states = fields.Dict(metadata={
        "description": "Current state of world regions",
        "example": {
            "region_123": {
                "control": "faction_123",
                "stability": 85,
                "threat_level": "low"
            }
        }
    })

class WorldTickResponseSchema(Schema):
    """Schema for world tick response."""
    success = fields.Bool(required=True, metadata={
        "description": "Whether the operation was successful",
        "example": True
    })
    world_state = fields.Nested(WorldStateSchema, required=True)
    tick_time = fields.DateTime(required=True, metadata={
        "description": "When the tick was processed",
        "example": "2024-03-15T12:34:56Z"
    })

class WorldStateUpdateSchema(Schema):
    """Schema for updating world state."""
    weather = fields.Dict(metadata={
        "description": "Weather conditions to update",
        "example": {
            "condition": "rainy",
            "temperature": 15
        }
    })
    active_events = fields.List(fields.Dict(), metadata={
        "description": "Events to add or update",
        "example": [
            {
                "type": "invasion",
                "location": "border_town"
            }
        ]
    })
    faction_states = fields.Dict(metadata={
        "description": "Faction states to update",
        "example": {
            "faction_123": {
                "influence": 80
            }
        }
    })
    region_states = fields.Dict(metadata={
        "description": "Region states to update",
        "example": {
            "region_123": {
                "stability": 70
            }
        }
    })

class WorldStateResponseSchema(Schema):
    """Schema for world state response."""
    success = fields.Bool(required=True, metadata={
        "description": "Whether the operation was successful",
        "example": True
    })
    world_state = fields.Nested(WorldStateSchema, required=True)

class ErrorResponseSchema(Schema):
    """Schema for error responses."""
    success = fields.Bool(required=True, metadata={
        "description": "Always False for error responses",
        "example": False
    })
    message = fields.Str(required=True, metadata={
        "description": "Error message describing what went wrong",
        "example": "Error processing world tick"
    }) 