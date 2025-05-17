"""
API Definition for Visual DM

This module defines the RESTful API structure for the Visual DM application,
establishing resource URLs, HTTP methods, and response format standards.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic
from pydantic import BaseModel, Field
from datetime import datetime
import json

# Define standard response formats

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response format"""
    items: List[T]
    total: int
    page: int
    page_size: int
    next_page: Optional[str] = None
    prev_page: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error: str
    error_code: str
    details: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class LinkRelation(str, Enum):
    """HATEOAS link relations"""
    SELF = "self"
    NEXT = "next"
    PREV = "prev"
    FIRST = "first"
    LAST = "last"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RELATED = "related"


class Link(BaseModel):
    """HATEOAS link"""
    href: str
    rel: LinkRelation
    method: str = "GET"


class ResourceResponse(BaseModel, Generic[T]):
    """Base response format for all resources with HATEOAS links"""
    data: T
    links: List[Link]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# API Resource Structure

class APIVersion(str, Enum):
    """API versions"""
    V1 = "v1"
    V2 = "v2"  # For future use


class ResourceType(str, Enum):
    """Core resource types in the API"""
    WORLD = "worlds"
    NPC = "npcs"
    QUEST = "quests"
    COMBAT = "combat"
    LOCATION = "locations"
    ITEM = "items"
    FACTION = "factions"
    USER = "users"
    AUTH = "auth"
    CHARACTER = "characters"


# API URL patterns and conventions
API_URL_PATTERN = {
    # Root API
    "base": "/api/{version}",
    
    # Resource collections
    "collection": "/api/{version}/{resource}",
    
    # Individual resources
    "resource": "/api/{version}/{resource}/{id}",
    
    # Nested collections
    "nested_collection": "/api/{version}/{parent_resource}/{parent_id}/{child_resource}",
    
    # Nested resources
    "nested_resource": "/api/{version}/{parent_resource}/{parent_id}/{child_resource}/{child_id}",
    
    # Actions on resources
    "resource_action": "/api/{version}/{resource}/{id}/{action}",
    
    # Batch operations
    "batch": "/api/{version}/{resource}/batch",
}

# HTTP Method mapping to CRUD operations
HTTP_METHODS = {
    "GET": "Retrieve resource(s)",
    "POST": "Create a new resource",
    "PUT": "Replace a resource completely",
    "PATCH": "Modify a resource partially",
    "DELETE": "Remove a resource",
}

# Query parameter conventions
QUERY_PARAMETERS = {
    "filter": "Filter resources by field values (e.g., filter[name]=test)",
    "sort": "Sort resources by fields (e.g., sort=name,-created_at)",
    "page": "Page number for pagination",
    "page_size": "Number of items per page",
    "cursor": "Cursor for pagination",
    "fields": "Specify fields to include in response (e.g., fields=id,name)",
    "expand": "Expand related resources (e.g., expand=creator,comments)",
    "q": "General search query parameter",
}

# Standard response status codes
STATUS_CODES = {
    # Success responses
    200: "OK - Standard response for successful HTTP requests",
    201: "Created - Request fulfilled and new resource created",
    204: "No Content - Request fulfilled but no response body",
    
    # Client error responses
    400: "Bad Request - Request cannot be fulfilled due to bad syntax",
    401: "Unauthorized - Authentication is required and has failed",
    403: "Forbidden - Server understood but refuses to authorize",
    404: "Not Found - Requested resource could not be found",
    409: "Conflict - Request could not be completed due to conflict",
    422: "Unprocessable Entity - Request well-formed but semantically incorrect",
    
    # Server error responses
    500: "Internal Server Error - Generic server-side error",
    503: "Service Unavailable - Server is not ready to handle the request",
}

# Resource structure definitions
RESOURCE_STRUCTURE = {
    ResourceType.WORLD: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.WORLD), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.WORLD, id="{world_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.WORLD, id="{world_id}", action="state"), "methods": ["GET", "PATCH"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.WORLD, id="{world_id}", action="calendar"), "methods": ["GET", "PATCH"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.WORLD, id="{world_id}", action="events"), "methods": ["GET", "POST"]},
        ],
        "related": [ResourceType.FACTION, ResourceType.LOCATION, ResourceType.NPC, ResourceType.QUEST]
    },
    
    ResourceType.NPC: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.NPC), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.NPC, id="{npc_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.NPC, id="{npc_id}", action="relationships"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.NPC, id="{npc_id}", action="schedule"), "methods": ["GET", "PUT"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.NPC, id="{npc_id}", action="memory"), "methods": ["GET"]},
        ],
        "related": [ResourceType.WORLD, ResourceType.LOCATION, ResourceType.FACTION, ResourceType.QUEST, ResourceType.ITEM]
    },
    
    ResourceType.QUEST: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.QUEST), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.QUEST, id="{quest_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.QUEST, id="{quest_id}", action="stages"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.QUEST, id="{quest_id}", action="progress"), "methods": ["GET", "PATCH"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.QUEST, id="{quest_id}", action="rewards"), "methods": ["GET", "PUT"]},
        ],
        "related": [ResourceType.WORLD, ResourceType.NPC, ResourceType.LOCATION, ResourceType.ITEM]
    },
    
    ResourceType.COMBAT: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.COMBAT), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}", action="start"), "methods": ["POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}", action="end"), "methods": ["POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}", action="next-turn"), "methods": ["POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}", action="combatants"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}", action="terrain"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}", action="attack"), "methods": ["POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.COMBAT, id="{combat_id}", action="combat-log"), "methods": ["GET"]},
        ],
        "related": [ResourceType.CHARACTER, ResourceType.NPC, ResourceType.LOCATION]
    },
    
    ResourceType.LOCATION: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.LOCATION), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.LOCATION, id="{location_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.LOCATION, id="{location_id}", action="state"), "methods": ["GET", "PATCH"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.LOCATION, id="{location_id}", action="npcs"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.LOCATION, id="{location_id}", action="encounters"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.LOCATION, id="{location_id}", action="resources"), "methods": ["GET", "PATCH"]},
        ],
        "related": [ResourceType.WORLD, ResourceType.NPC, ResourceType.QUEST, ResourceType.ITEM]
    },
    
    ResourceType.ITEM: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.ITEM), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.ITEM, id="{item_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.ITEM, id="{item_id}", action="properties"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.ITEM, id="{item_id}", action="history"), "methods": ["GET"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.ITEM, id="{item_id}", action="enhance"), "methods": ["POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.ITEM, id="{item_id}", action="repair"), "methods": ["POST"]},
        ],
        "related": [ResourceType.CHARACTER, ResourceType.NPC, ResourceType.LOCATION]
    },
    
    ResourceType.FACTION: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.FACTION), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.FACTION, id="{faction_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.FACTION, id="{faction_id}", action="relationships"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.FACTION, id="{faction_id}", action="members"), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.FACTION, id="{faction_id}", action="resources"), "methods": ["GET", "PATCH"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.FACTION, id="{faction_id}", action="territory"), "methods": ["GET", "PATCH"]},
        ],
        "related": [ResourceType.WORLD, ResourceType.NPC, ResourceType.LOCATION]
    },
    
    ResourceType.CHARACTER: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.CHARACTER), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.CHARACTER, id="{character_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.CHARACTER, id="{character_id}", action="inventory"), "methods": ["GET", "POST", "PUT"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.CHARACTER, id="{character_id}", action="stats"), "methods": ["GET", "PATCH"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.CHARACTER, id="{character_id}", action="abilities"), "methods": ["GET", "POST", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.CHARACTER, id="{character_id}", action="quests"), "methods": ["GET", "POST", "DELETE"]},
        ],
        "related": [ResourceType.USER, ResourceType.ITEM, ResourceType.QUEST, ResourceType.LOCATION, ResourceType.FACTION, ResourceType.COMBAT]
    },
    
    ResourceType.USER: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.USER), "methods": ["GET", "POST"]},
            {"path": API_URL_PATTERN["resource"].format(version=APIVersion.V1, resource=ResourceType.USER, id="{user_id}"), "methods": ["GET", "PUT", "PATCH", "DELETE"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.USER, id="{user_id}", action="characters"), "methods": ["GET"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.USER, id="{user_id}", action="settings"), "methods": ["GET", "PATCH"]},
            {"path": API_URL_PATTERN["resource_action"].format(version=APIVersion.V1, resource=ResourceType.USER, id="{user_id}", action="worlds"), "methods": ["GET"]},
        ],
        "related": [ResourceType.CHARACTER, ResourceType.WORLD]
    },
    
    ResourceType.AUTH: {
        "endpoints": [
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.AUTH) + "/login", "methods": ["POST"]},
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.AUTH) + "/logout", "methods": ["POST"]},
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.AUTH) + "/refresh", "methods": ["POST"]},
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.AUTH) + "/register", "methods": ["POST"]},
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.AUTH) + "/reset-password", "methods": ["POST"]},
            {"path": API_URL_PATTERN["collection"].format(version=APIVersion.V1, resource=ResourceType.AUTH) + "/verify-email", "methods": ["POST"]},
        ],
        "related": [ResourceType.USER]
    }
}

def get_resource_endpoints(resource_type: ResourceType) -> List[Dict[str, Any]]:
    """Get all endpoints for a specific resource type"""
    return RESOURCE_STRUCTURE.get(resource_type, {}).get("endpoints", [])

def get_related_resources(resource_type: ResourceType) -> List[ResourceType]:
    """Get related resources for a specific resource type"""
    return RESOURCE_STRUCTURE.get(resource_type, {}).get("related", []) 