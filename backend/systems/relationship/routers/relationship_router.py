"""
Relationship Router
------------------
FastAPI router for relationship system endpoints.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.systems.relationship.relationship_service import RelationshipService
from backend.systems.relationship.relationship_schema import (
    RelationshipResponse,
    RelationshipListResponse,
    RelationshipCreateRequest,
    RelationshipUpdateRequest,
    FactionReputationRequest,
    QuestProgressRequest
)
from backend.core.database import get_db_session
from sqlalchemy.orm import Session

router = APIRouter(prefix="/relationships", tags=["relationships"])

def get_relationship_service(db: Session = Depends(get_db_session)) -> RelationshipService:
    """Dependency for getting a RelationshipService instance."""
    return RelationshipService(db_session=db)

@router.get("/{character_id}", response_model=RelationshipListResponse)
async def get_character_relationships(
    character_id: UUID,
    type: Optional[str] = None,
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Get all relationships for a character, optionally filtered by type.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID to get relationships for
    type: Optional[str]
        Optional filter by relationship type (faction, quest, etc.)
    """
    relationships = service.get_relationships_for_source(character_id, type)
    return RelationshipListResponse.from_db_models(relationships)

@router.get("/{character_id}/factions", response_model=RelationshipListResponse)
async def get_character_faction_relationships(
    character_id: UUID,
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Get all faction relationships for a character.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID to get faction relationships for
    """
    relationships = service.get_character_faction_relationships(character_id)
    return RelationshipListResponse.from_db_models(relationships)

@router.get("/{character_id}/quests", response_model=RelationshipListResponse)
async def get_character_quest_relationships(
    character_id: UUID,
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Get all quest relationships for a character.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID to get quest relationships for
    """
    relationships = service.get_character_quest_relationships(character_id)
    return RelationshipListResponse.from_db_models(relationships)

@router.post("/{character_id}", response_model=RelationshipResponse)
async def create_relationship(
    character_id: UUID,
    request: RelationshipCreateRequest,
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Create a new relationship for a character.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID to create the relationship for
    request: RelationshipCreateRequest
        Relationship creation data
    """
    relationship = service.add_relationship(
        character_id=character_id,
        target_id=request.target_id,
        type=request.type,
        data=request.data
    )
    return RelationshipResponse.from_db_model(relationship)

@router.put("/{character_id}/faction/{faction_id}/reputation", response_model=RelationshipResponse)
async def update_faction_reputation(
    character_id: UUID,
    faction_id: UUID,
    request: FactionReputationRequest,
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Update a character's reputation with a faction.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID to update faction reputation for
    faction_id: UUID
        The faction ID to update reputation with
    request: FactionReputationRequest
        Reputation update data
    """
    try:
        relationship = service.update_faction_reputation(
            character_id=character_id,
            faction_id=faction_id,
            reputation_change=request.reputation_change,
            new_reputation=request.new_reputation,
            new_standing=request.new_standing
        )
        return RelationshipResponse.from_db_model(relationship)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{character_id}/quest/{quest_id}/progress", response_model=RelationshipResponse)
async def update_quest_progress(
    character_id: UUID,
    quest_id: UUID,
    request: QuestProgressRequest,
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Update a character's progress on a quest.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID to update quest progress for
    quest_id: UUID
        The quest ID to update progress on
    request: QuestProgressRequest
        Quest progress update data
    """
    try:
        relationship = service.update_quest_progress(
            character_id=character_id,
            quest_id=quest_id,
            progress=request.progress,
            status=request.status
        )
        return RelationshipResponse.from_db_model(relationship)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tick/daily", response_model=List[Dict[str, Any]])
async def run_daily_relationship_tick(
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Run the daily relationship tick to simulate natural relationship changes over time.
    
    Returns a list of relationships that changed tiers.
    """
    changes = service.run_daily_relationship_tick()
    return changes

@router.put("/{character_id}/npc/{npc_id}/loyalty", response_model=RelationshipResponse)
async def update_npc_loyalty(
    character_id: UUID,
    npc_id: UUID,
    cha_score: int = Query(10, description="Character's Charisma score"),
    context_tags: List[str] = Query(None, description="Optional context tags"),
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Update loyalty between a character and an NPC.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID
    npc_id: UUID
        The NPC ID
    cha_score: int
        Character's Charisma score (influences loyalty)
    context_tags: List[str]
        Optional context tags affecting the relationship
    """
    relationship = service.update_loyalty(
        character_id=character_id,
        npc_id=npc_id,
        cha_score=cha_score,
        context_tags=context_tags
    )
    return RelationshipResponse.from_db_model(relationship)

@router.get("/{character_id}/npc/{npc_id}/betrayal")
async def check_npc_betrayal(
    character_id: UUID,
    npc_id: UUID,
    cha_score: int = Query(10, description="Character's Charisma score"),
    service: RelationshipService = Depends(get_relationship_service)
):
    """
    Check if an NPC will betray a character.
    
    Parameters:
    -----------
    character_id: UUID
        The character ID
    npc_id: UUID
        The NPC ID
    cha_score: int
        Character's Charisma score (influences betrayal check)
    """
    will_betray, reason = service.check_betrayal(
        character_id=character_id,
        npc_id=npc_id,
        cha_score=cha_score
    )
    return {"will_betray": will_betray, "reason": reason} 