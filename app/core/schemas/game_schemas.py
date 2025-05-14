"""
Core game system schemas for request/response validation and Swagger documentation.
"""

from marshmallow import Schema, fields, validate
from enum import Enum

class NPCTypeEnum(str, Enum):
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    GUARD = "guard"
    TRAINER = "trainer"
    CIVILIAN = "civilian"
    ENEMY = "enemy"

class QuestTypeEnum(str, Enum):
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    WEEKLY = "weekly"
    EVENT = "event"

class QuestStatusEnum(str, Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    HIDDEN = "hidden"

class NPCSchema(Schema):
    """Schema for NPC data."""
    id = fields.Int(dump_only=True, metadata={"description": "Unique identifier for the NPC"})
    name = fields.Str(required=True, metadata={"description": "Name of the NPC"})
    type = fields.Enum(NPCTypeEnum, required=True, metadata={"description": "Type of NPC"})
    level = fields.Int(metadata={"description": "Level of the NPC"})
    disposition = fields.Float(metadata={"description": "NPC's disposition towards the player"})
    dialogue_options = fields.Dict(metadata={"description": "Available dialogue options"})
    inventory = fields.List(fields.Dict(), metadata={"description": "NPC's inventory"})
    available_quests = fields.List(fields.Int(), metadata={"description": "List of available quest IDs"})
    location = fields.Nested("LocationSchema", only=("id", "name"), metadata={"description": "NPC's current location"})

class QuestSchema(Schema):
    """Schema for quest data."""
    id = fields.Int(dump_only=True, metadata={"description": "Unique identifier for the quest"})
    title = fields.Str(required=True, metadata={"description": "Quest title"})
    description = fields.Str(required=True, metadata={"description": "Quest description"})
    type = fields.Enum(QuestTypeEnum, required=True, metadata={"description": "Type of quest"})
    status = fields.Enum(QuestStatusEnum, metadata={"description": "Current quest status"})
    level_requirement = fields.Int(metadata={"description": "Required level to start quest"})
    experience_reward = fields.Int(metadata={"description": "Experience points reward"})
    gold_reward = fields.Int(metadata={"description": "Gold reward"})
    item_rewards = fields.List(fields.Dict(), metadata={"description": "List of item rewards"})
    prerequisites = fields.List(fields.Int(), metadata={"description": "List of prerequisite quest IDs"})
    objectives = fields.List(fields.Dict(), metadata={"description": "List of quest objectives"})
    location = fields.Nested("LocationSchema", only=("id", "name"), metadata={"description": "Quest location"})
    npc = fields.Nested(NPCSchema, only=("id", "name"), metadata={"description": "Quest giver NPC"})

class LocationSchema(Schema):
    """Schema for location data."""
    id = fields.Int(dump_only=True, metadata={"description": "Unique identifier for the location"})
    name = fields.Str(required=True, metadata={"description": "Location name"})
    description = fields.Str(metadata={"description": "Location description"})
    coordinates = fields.Dict(metadata={"description": "Location coordinates"})
    type = fields.Str(metadata={"description": "Type of location"})
    npcs = fields.List(fields.Nested(NPCSchema, only=("id", "name")), metadata={"description": "NPCs at this location"})
    quests = fields.List(fields.Nested(QuestSchema, only=("id", "title")), metadata={"description": "Available quests at this location"})

class WorldStateSchema(Schema):
    """Schema for world state data."""
    time = fields.DateTime(metadata={"description": "Current in-game time"})
    season = fields.Str(metadata={"description": "Current season"})
    weather = fields.Dict(metadata={"description": "Current weather conditions"})
    active_events = fields.List(fields.Dict(), metadata={"description": "Currently active world events"})
    faction_relations = fields.Dict(metadata={"description": "Current faction relationships"}) 