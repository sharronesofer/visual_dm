"""
Party API
---------
FastAPI router for party-related endpoints.
Replaces the Flask routes in party_routes.py.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from backend.core.database import get_db_session
from backend.systems.character.services.party_service import PartyService
from backend.core.utils.error import NotFoundError, DatabaseError

# Assuming schemas will be created later when needed
# from backend.systems.character.api.schemas import (
#     PartyCreate,
#     PartyResponse,
#     PartyMemberAdd,
#     PartyMemberRemove
# )

router = APIRouter(prefix="/parties", tags=["parties"])

@router.post("/{player_id}")
def create_party(
    player_id: UUID,
    npc_ids: List[UUID],
    db: Session = Depends(get_db_session)
):
    """
    Create a new party with a player and NPCs.
    """
    try:
        service = PartyService(db_session=db)
        party_id = service.create_party(player_id, npc_ids)
        return {"party_id": party_id}
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{party_id}/members/{npc_id}")
def add_to_party(
    party_id: str,
    npc_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Add an NPC to an existing party.
    """
    try:
        service = PartyService(db_session=db)
        result = service.add_to_party(party_id, npc_id)
        if result:
            return {"success": True}
        else:
            return {"success": False, "message": "NPC already in party"}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{party_id}/members/{member_id}")
def remove_from_party(
    party_id: str,
    member_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Remove a member from a party.
    """
    try:
        service = PartyService(db_session=db)
        result = service.remove_from_party(party_id, member_id)
        if result:
            return {"success": True}
        else:
            return {"success": False, "message": "Member not in party"}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{party_id}/level")
def get_party_level(
    party_id: str,
    mode: Optional[str] = "sum",
    db: Session = Depends(get_db_session)
):
    """
    Get the total or average party level.
    """
    try:
        service = PartyService(db_session=db)
        level = service.get_total_party_level(party_id, mode)
        return {"party_id": party_id, "level": level, "mode": mode}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{party_id}/xp/{amount}")
def award_xp_to_party(
    party_id: str,
    amount: int,
    db: Session = Depends(get_db_session)
):
    """
    Award XP to all members of a party.
    """
    try:
        service = PartyService(db_session=db)
        awarded = service.award_xp_to_party(party_id, amount)
        return {"party_id": party_id, "amount": amount, "awarded": awarded}
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/abandon/{npc_id}")
def abandon_party(
    npc_id: UUID,
    db: Session = Depends(get_db_session)
):
    """
    Remove an NPC from any party they're in due to loyalty loss.
    """
    try:
        service = PartyService(db_session=db)
        result = service.abandon_party(npc_id)
        if result:
            return {"success": True}
        else:
            return {"success": False, "message": "NPC not in any party"}
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 