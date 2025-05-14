"""Data models for search functionality."""

from typing import Dict, List, Optional, Any, TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    """Types of game entities that can be searched."""
    NPC = "npc"
    ITEM = "item"
    LOCATION = "location"
    QUEST = "quest"
    FACTION = "faction"

class FacetType(str, Enum):
    """Types of facets supported by the search system."""
    TERMS = "terms"  # Categorical facets
    RANGE = "range"  # Numeric/date range facets
    NESTED = "nested"  # Nested/hierarchical facets

class FacetConfig(BaseModel):
    """Configuration for a facet field."""
    name: str
    field: str
    type: FacetType
    display_name: str
    size: int = 10
    min_doc_count: int = 1
    ranges: Optional[List[Dict[str, Any]]] = None  # For range facets
    nested_path: Optional[str] = None  # For nested facets
    order: Optional[Dict[str, str]] = None  # For custom ordering

class EntityMapping(BaseModel):
    """Base mapping configuration for an entity type."""
    type: EntityType
    mappings: Dict[str, Any]
    facets: List[FacetConfig]

# Entity-specific mappings
NPC_MAPPING = EntityMapping(
    type=EntityType.NPC,
    mappings={
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword", "normalizer": "lowercase"}
                }
            },
            "description": {"type": "text", "analyzer": "game_analyzer"},
            "personality": {"type": "keyword", "normalizer": "lowercase"},
            "faction": {"type": "keyword", "normalizer": "lowercase"},
            "location": {"type": "keyword", "normalizer": "lowercase"},
            "level": {"type": "integer"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "tags": {"type": "keyword", "normalizer": "lowercase"}
        }
    },
    facets=[
        FacetConfig(
            name="personality",
            field="personality",
            type=FacetType.TERMS,
            display_name="Personality"
        ),
        FacetConfig(
            name="faction",
            field="faction",
            type=FacetType.TERMS,
            display_name="Faction"
        ),
        FacetConfig(
            name="location",
            field="location",
            type=FacetType.TERMS,
            display_name="Location"
        ),
        FacetConfig(
            name="level",
            field="level",
            type=FacetType.RANGE,
            display_name="Level",
            ranges=[
                {"from": 0, "to": 10, "key": "Novice"},
                {"from": 10, "to": 20, "key": "Intermediate"},
                {"from": 20, "to": 30, "key": "Advanced"},
                {"from": 30, "to": None, "key": "Expert"}
            ]
        )
    ]
)

ITEM_MAPPING = EntityMapping(
    type=EntityType.ITEM,
    mappings={
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword", "normalizer": "lowercase"}
                }
            },
            "description": {"type": "text", "analyzer": "game_analyzer"},
            "type": {"type": "keyword", "normalizer": "lowercase"},
            "rarity": {"type": "keyword", "normalizer": "lowercase"},
            "value": {"type": "integer"},
            "level_req": {"type": "integer"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "tags": {"type": "keyword", "normalizer": "lowercase"},
            "stats": {
                "type": "nested",
                "properties": {
                    "name": {"type": "keyword"},
                    "value": {"type": "float"}
                }
            }
        }
    },
    facets=[
        FacetConfig(
            name="type",
            field="type",
            type=FacetType.TERMS,
            display_name="Type"
        ),
        FacetConfig(
            name="rarity",
            field="rarity",
            type=FacetType.TERMS,
            display_name="Rarity",
            order={"_key": "asc"}
        ),
        FacetConfig(
            name="value",
            field="value",
            type=FacetType.RANGE,
            display_name="Value",
            ranges=[
                {"to": 100, "key": "Cheap"},
                {"from": 100, "to": 1000, "key": "Moderate"},
                {"from": 1000, "to": 10000, "key": "Expensive"},
                {"from": 10000, "key": "Legendary"}
            ]
        ),
        FacetConfig(
            name="level_req",
            field="level_req",
            type=FacetType.RANGE,
            display_name="Required Level",
            ranges=[
                {"to": 10, "key": "Beginner"},
                {"from": 10, "to": 30, "key": "Intermediate"},
                {"from": 30, "key": "Advanced"}
            ]
        ),
        FacetConfig(
            name="stats",
            field="stats",
            type=FacetType.NESTED,
            display_name="Stats",
            nested_path="stats"
        )
    ]
)

LOCATION_MAPPING = EntityMapping(
    type=EntityType.LOCATION,
    mappings={
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword", "normalizer": "lowercase"}
                }
            },
            "description": {"type": "text", "analyzer": "game_analyzer"},
            "region": {"type": "keyword", "normalizer": "lowercase"},
            "terrain": {"type": "keyword", "normalizer": "lowercase"},
            "level_range": {
                "type": "integer_range",
                "fields": {
                    "min": {"type": "integer"},
                    "max": {"type": "integer"}
                }
            },
            "coordinates": {"type": "geo_point"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "tags": {"type": "keyword", "normalizer": "lowercase"}
        }
    },
    facets=[
        FacetConfig(
            name="region",
            field="region",
            type=FacetType.TERMS,
            display_name="Region"
        ),
        FacetConfig(
            name="terrain",
            field="terrain",
            type=FacetType.TERMS,
            display_name="Terrain"
        ),
        FacetConfig(
            name="level_range",
            field="level_range",
            type=FacetType.RANGE,
            display_name="Level Range",
            ranges=[
                {"to": 10, "key": "Starter"},
                {"from": 10, "to": 30, "key": "Mid-Level"},
                {"from": 30, "key": "High-Level"}
            ]
        )
    ]
)

QUEST_MAPPING = EntityMapping(
    type=EntityType.QUEST,
    mappings={
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "game_analyzer",
                "fields": {
                    "keyword": {"type": "keyword", "normalizer": "lowercase"}
                }
            },
            "description": {"type": "text", "analyzer": "game_analyzer"},
            "difficulty": {"type": "keyword", "normalizer": "lowercase"},
            "type": {"type": "keyword", "normalizer": "lowercase"},
            "level_req": {"type": "integer"},
            "rewards": {
                "type": "nested",
                "properties": {
                    "type": {"type": "keyword"},
                    "amount": {"type": "integer"},
                    "item_id": {"type": "keyword"}
                }
            },
            "prerequisites": {"type": "keyword"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
            "tags": {"type": "keyword", "normalizer": "lowercase"}
        }
    },
    facets=[
        FacetConfig(
            name="difficulty",
            field="difficulty",
            type=FacetType.TERMS,
            display_name="Difficulty"
        ),
        FacetConfig(
            name="type",
            field="type",
            type=FacetType.TERMS,
            display_name="Type"
        ),
        FacetConfig(
            name="level_req",
            field="level_req",
            type=FacetType.RANGE,
            display_name="Required Level",
            ranges=[
                {"to": 10, "key": "Beginner"},
                {"from": 10, "to": 30, "key": "Intermediate"},
                {"from": 30, "key": "Advanced"}
            ]
        ),
        FacetConfig(
            name="rewards",
            field="rewards",
            type=FacetType.NESTED,
            display_name="Rewards",
            nested_path="rewards"
        )
    ]
)

# Map entity types to their mappings
ENTITY_MAPPINGS = {
    EntityType.NPC: NPC_MAPPING,
    EntityType.ITEM: ITEM_MAPPING,
    EntityType.LOCATION: LOCATION_MAPPING,
    EntityType.QUEST: QUEST_MAPPING,
    EntityType.FACTION: EntityMapping(
        type=EntityType.FACTION,
        mappings={
            "properties": {
                "id": {"type": "keyword"},
                "name": {
                    "type": "text",
                    "analyzer": "game_analyzer",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "description": {
                    "type": "text",
                    "analyzer": "game_analyzer"
                },
                "faction_type": {"type": "keyword"},
                "status": {"type": "keyword"},
                "influence": {"type": "float"},
                "resources": {
                    "type": "object",
                    "enabled": True
                },
                "territory": {
                    "type": "object",
                    "enabled": True
                },
                "traits": {
                    "type": "object",
                    "enabled": True
                },
                "tags": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"}
            }
        },
        facets=[
            FacetConfig(
                name="faction_type",
                field="faction_type",
                type=FacetType.TERMS,
                display_name="Faction Type",
                size=10
            ),
            FacetConfig(
                name="status",
                field="status",
                type=FacetType.TERMS,
                display_name="Status",
                size=5
            ),
            FacetConfig(
                name="influence",
                field="influence",
                type=FacetType.RANGE,
                display_name="Influence",
                ranges=[
                    {"to": 25, "key": "Minor"},
                    {"from": 25, "to": 50, "key": "Notable"},
                    {"from": 50, "to": 75, "key": "Major"},
                    {"from": 75, "key": "Dominant"}
                ]
            ),
            FacetConfig(
                name="tags",
                field="tags",
                type=FacetType.TERMS,
                display_name="Tags",
                size=20
            )
        ]
    )
}

class FacetValue(BaseModel):
    """A single facet value with its count."""
    value: Any
    count: int
    selected: bool = False

class FacetResult(BaseModel):
    """Results for a single facet."""
    name: str
    field: str
    type: FacetType
    values: List[FacetValue]

T = TypeVar("T")

class SearchResult(BaseModel, Generic[T]):
    """Search results with pagination and facets."""
    total: int
    page: int
    page_size: int
    results: List[T]
    facets: Optional[Dict[str, List[FacetValue]]] = None
    took_ms: Optional[int] = None
    max_score: Optional[float] = None 