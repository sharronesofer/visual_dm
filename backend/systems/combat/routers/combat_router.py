from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Body

from backend.systems.combat.schemas.combat import CombatStateSchema
from backend.systems.combat.services.combat_service import combat_service, CombatService

router = APIRouter(
    prefix="/combat",
    tags=["Combat"],
)

@router.post("/state", response_model=CombatStateSchema, status_code=status.HTTP_201_CREATED)
def create_combat_state_endpoint(initial_state_data: Optional[Dict] = Body(None)):
    """
    Creates a new combat state. 
    Optionally accepts initial data for the combat setup.
    If no data is provided, a minimal combat state with a new combat_id is created.
    The `Development_Bible.md` mentions `POST /combat/state` to set current combat state. 
    This endpoint serves to initialize/create a new combat instance.
    """
    try:
        combat_state = combat_service.create_new_combat_instance(initial_combat_data=initial_state_data)
        return combat_state
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/state/{combat_id}", response_model=CombatStateSchema)
def get_combat_state_endpoint(combat_id: str):
    """
    Retrieves the current state of a specific combat instance by its ID.
    This aligns with `GET /combat/state` from `Development_Bible.md`, but is made specific by ID.
    """
    combat_state = combat_service.get_combat_state(combat_id)
    if not combat_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat instance not found")
    return combat_state

@router.put("/state/{combat_id}", response_model=CombatStateSchema)
def update_combat_state_endpoint(combat_id: str, combat_state_update: CombatStateSchema):
    """
    Updates an existing combat state by its ID.
    The `Development_Bible.md` mentions `POST /combat/state` to set current combat state. 
    A PUT to a specific combat_id is more RESTful for updates.
    """
    updated_state = combat_service.update_combat_state(combat_id, combat_state_update)
    if not updated_state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat instance not found to update")
    return updated_state

@router.delete("/state/{combat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_combat_state_endpoint(combat_id: str):
    """
    Deletes a combat instance by its ID (e.g., when combat ends).
    """
    success = combat_service.end_combat_instance(combat_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Combat instance not found to delete")
    return

@router.get("/states", response_model=List[CombatStateSchema])
def list_all_combat_states_endpoint():
    """
    Lists all active combat instances. Useful for debugging or an overview.
    """
    return combat_service.list_all_combat_instances() 