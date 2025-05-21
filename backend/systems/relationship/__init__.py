"""
Relationship System
------------------
Module for managing all entity-to-entity relationships in the game,
including character to faction, quest, and character to character relationships.
"""

from backend.systems.relationship.relationship_model import (
    RelationshipType,
    RelationshipBase,
    RelationshipCreate,
    RelationshipUpdate,
    RelationshipInDB
)
from backend.systems.relationship.relationship_service import RelationshipService
from backend.systems.relationship.relationship_schema import (
    RelationshipResponse,
    RelationshipListResponse,
    RelationshipCreateRequest,
    RelationshipUpdateRequest,
    FactionReputationRequest,
    QuestProgressRequest
)

# Import routers for API registration
from backend.systems.relationship.routers.relationship_router import router as relationship_router

__all__ = [
    # Models
    'RelationshipType',
    'RelationshipBase',
    'RelationshipCreate',
    'RelationshipUpdate',
    'RelationshipInDB',
    
    # Service
    'RelationshipService',
    
    # Schemas
    'RelationshipResponse',
    'RelationshipListResponse',
    'RelationshipCreateRequest',
    'RelationshipUpdateRequest',
    'FactionReputationRequest',
    'QuestProgressRequest',
    
    # Routers
    'relationship_router'
]
