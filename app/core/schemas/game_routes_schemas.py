"""
Game route schemas for request/response validation and Swagger documentation.
"""

from marshmallow import Schema, fields, validate
from datetime import datetime

class GameSessionSchema(Schema):
    """Schema for game session data."""
    session_id = fields.Str(dump_only=True, metadata={
        "description": "Unique identifier for the game session",
        "example": "session_20240315_123456"
    })
    user_id = fields.Str(required=True, metadata={
        "description": "ID of the user starting the session",
        "example": "user_123"
    })
    character_id = fields.Str(required=True, metadata={
        "description": "ID of the character being played",
        "example": "char_123"
    })
    start_time = fields.DateTime(dump_only=True, metadata={
        "description": "When the session started",
        "example": "2024-03-15T12:34:56Z"
    })
    status = fields.Str(
        dump_only=True,
        validate=validate.OneOf(['active', 'paused', 'completed']),
        metadata={
            "description": "Current status of the session",
            "example": "active"
        }
    )
    current_location = fields.Str(dump_only=True, metadata={
        "description": "Current location in the game world",
        "example": "starting_town"
    })
    quest_log = fields.List(fields.Dict(), dump_only=True, metadata={
        "description": "List of active quests",
        "example": []
    })
    inventory = fields.List(fields.Dict(), dump_only=True, metadata={
        "description": "Current inventory items",
        "example": []
    })
    stats = fields.Dict(dump_only=True, metadata={
        "description": "Current session statistics",
        "example": {
            "playtime": 0,
            "quests_completed": 0,
            "battles_won": 0
        }
    })

class StartGameRequestSchema(Schema):
    """Schema for starting a new game session."""
    user_id = fields.Str(required=True, metadata={
        "description": "ID of the user starting the game",
        "example": "user_123"
    })
    character_id = fields.Str(required=True, metadata={
        "description": "ID of the character to play",
        "example": "char_123"
    })
    settings = fields.Dict(metadata={
        "description": "Optional game settings",
        "example": {
            "difficulty": "normal",
            "permadeath": False,
            "tutorial": True
        }
    })

class StartGameResponseSchema(Schema):
    """Schema for start game response."""
    success = fields.Bool(required=True, metadata={
        "description": "Whether the operation was successful",
        "example": True
    })
    session_id = fields.Str(required=True, metadata={
        "description": "ID of the created game session",
        "example": "session_20240315_123456"
    })
    session_data = fields.Nested(GameSessionSchema, required=True)

class EndGameRequestSchema(Schema):
    """Schema for ending a game session."""
    session_id = fields.Str(required=True, metadata={
        "description": "ID of the session to end",
        "example": "session_20240315_123456"
    })

class EndGameResponseSchema(Schema):
    """Schema for end game response."""
    success = fields.Bool(required=True, metadata={
        "description": "Whether the operation was successful",
        "example": True
    })
    session_summary = fields.Nested(GameSessionSchema, required=True)

class GameStatusResponseSchema(Schema):
    """Schema for game status response."""
    success = fields.Bool(required=True, metadata={
        "description": "Whether the operation was successful",
        "example": True
    })
    game_state = fields.Nested(GameSessionSchema, required=True)

class ErrorResponseSchema(Schema):
    """Schema for error responses."""
    success = fields.Bool(required=True, metadata={
        "description": "Always False for error responses",
        "example": False
    })
    message = fields.Str(required=True, metadata={
        "description": "Error message describing what went wrong",
        "example": "Session not found"
    }) 