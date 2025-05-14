"""
Game state schemas for request/response validation and Swagger documentation.
"""

from marshmallow import Schema, fields, validate
from datetime import datetime

class GameSettingsSchema(Schema):
    """Schema for game settings."""
    difficulty = fields.Str(
        required=True,
        validate=validate.OneOf(['easy', 'normal', 'hard']),
        metadata={
            "description": "Game difficulty level",
            "example": "normal"
        }
    )
    permadeath = fields.Bool(
        required=True,
        metadata={
            "description": "Whether permadeath is enabled",
            "example": False
        }
    )
    tutorial = fields.Bool(
        required=True,
        metadata={
            "description": "Whether tutorial is enabled",
            "example": True
        }
    )

class GameStatsSchema(Schema):
    """Schema for game statistics."""
    playtime = fields.Int(
        required=True,
        metadata={
            "description": "Total playtime in seconds",
            "example": 3600
        }
    )
    quests_completed = fields.Int(
        required=True,
        metadata={
            "description": "Number of completed quests",
            "example": 5
        }
    )
    battles_won = fields.Int(
        required=True,
        metadata={
            "description": "Number of battles won",
            "example": 10
        }
    )

class GameStateSchema(Schema):
    """Schema for game state."""
    user_id = fields.Str(
        required=True,
        metadata={
            "description": "ID of the user",
            "example": "user_123"
        }
    )
    character_id = fields.Str(
        required=True,
        metadata={
            "description": "ID of the active character",
            "example": "char_123"
        }
    )
    session_id = fields.Str(
        dump_only=True,
        metadata={
            "description": "Unique session identifier",
            "example": "session_20240315_123456"
        }
    )
    start_time = fields.DateTime(
        dump_only=True,
        metadata={
            "description": "Session start time",
            "example": "2024-03-15T12:34:56Z"
        }
    )
    status = fields.Str(
        required=True,
        validate=validate.OneOf(['active', 'paused', 'completed']),
        metadata={
            "description": "Current game status",
            "example": "active"
        }
    )
    current_location = fields.Str(
        required=True,
        metadata={
            "description": "Current location in the game world",
            "example": "starting_town"
        }
    )
    quest_log = fields.List(
        fields.Str(),
        metadata={
            "description": "List of active quest IDs",
            "example": ["quest_123", "quest_456"]
        }
    )
    inventory = fields.List(
        fields.Str(),
        metadata={
            "description": "List of inventory item IDs",
            "example": ["item_123", "item_456"]
        }
    )
    stats = fields.Nested(
        GameStatsSchema,
        metadata={
            "description": "Game statistics"
        }
    )
    settings = fields.Nested(
        GameSettingsSchema,
        metadata={
            "description": "Game settings"
        }
    )

class StartGameRequestSchema(Schema):
    """Schema for start game request."""
    user_id = fields.Str(
        required=True,
        metadata={
            "description": "ID of the user starting the game",
            "example": "user_123"
        }
    )
    character_id = fields.Str(
        required=True,
        metadata={
            "description": "ID of the character to play",
            "example": "char_123"
        }
    )

class StartGameResponseSchema(Schema):
    """Schema for start game response."""
    success = fields.Bool(
        required=True,
        metadata={
            "description": "Whether the operation was successful",
            "example": True
        }
    )
    session_id = fields.Str(
        required=True,
        metadata={
            "description": "Unique session identifier",
            "example": "session_20240315_123456"
        }
    )
    session_data = fields.Nested(
        GameStateSchema,
        metadata={
            "description": "Initial game state data"
        }
    )

class EndGameRequestSchema(Schema):
    """Schema for end game request."""
    session_id = fields.Str(
        required=True,
        metadata={
            "description": "ID of the session to end",
            "example": "session_20240315_123456"
        }
    )

class EndGameResponseSchema(Schema):
    """Schema for end game response."""
    success = fields.Bool(
        required=True,
        metadata={
            "description": "Whether the operation was successful",
            "example": True
        }
    )
    session_summary = fields.Nested(
        GameStateSchema,
        metadata={
            "description": "Final game state data"
        }
    ) 