"""
Relationship Schemas
-------------------
API/DTO schemas for the relationship system.
"""
from typing import Dict, Any, Optional, List
from uuid import UUID
from pydantic import BaseModel

from backend.systems.relationship.relationship_model import RelationshipType, RelationshipInDB

class RelationshipResponse(BaseModel):
    """API response model for a single relationship."""
    id: UUID
    source_id: UUID
    target_id: UUID
    type: RelationshipType
    data: Dict[str, Any]
    created_at: str
    updated_at: str

    @classmethod
    def from_db_model(cls, db_model: RelationshipInDB) -> "RelationshipResponse":
        """Convert a database model to an API response model."""
        return cls(
            id=db_model.id,
            source_id=db_model.source_id,
            target_id=db_model.target_id,
            type=db_model.type,
            data=db_model.data,
            created_at=db_model.created_at.isoformat(),
            updated_at=db_model.updated_at.isoformat()
        )

class RelationshipListResponse(BaseModel):
    """API response model for a list of relationships."""
    items: List[RelationshipResponse]
    count: int

    @classmethod
    def from_db_models(cls, db_models: List[RelationshipInDB]) -> "RelationshipListResponse":
        """Convert a list of database models to an API response model."""
        return cls(
            items=[RelationshipResponse.from_db_model(model) for model in db_models],
            count=len(db_models)
        )

class RelationshipCreateRequest(BaseModel):
    """API request model for creating a relationship."""
    target_id: UUID
    type: RelationshipType
    data: Optional[Dict[str, Any]] = None

class RelationshipUpdateRequest(BaseModel):
    """API request model for updating a relationship."""
    data: Dict[str, Any]

class FactionReputationRequest(BaseModel):
    """API request model for updating faction reputation."""
    reputation_change: Optional[int] = None
    new_reputation: Optional[int] = None
    new_standing: Optional[str] = None

class QuestProgressRequest(BaseModel):
    """API request model for updating quest progress."""
    progress: Optional[float] = None
    status: Optional[str] = None 