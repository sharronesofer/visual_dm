"""
Quest API routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from typing import List, Dict, Any, Optional
import logging

from .utils import QuestValidator
from .database import QuestRepository
from .manager import QuestStateManager
from .models import Quest, QuestStep
from backend.core.utils.error import ValidationError, NotFoundError
from backend.core.utils.firebase_utils import get_collection

router = APIRouter(prefix="/quests", tags=["quests"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[Quest])
async def get_quests(
    player_id: Optional[str] = Query(None, description="Filter quests by player ID"),
    npc_id: Optional[str] = Query(None, description="Filter quests by NPC ID"),
    status: Optional[str] = Query(None, description="Filter quests by status")
):
    """Get all quests matching the provided filters."""
    try:
        if player_id:
            return QuestRepository.get_quests_by_player(player_id)
        elif npc_id:
            return QuestRepository.get_quests_by_npc(npc_id)
        elif status:
            return QuestRepository.get_active_quests_by_status(status)
        else:
            # Default: get all quests (could be limited/paginated in a real app)
            return get_collection('quests')
    except Exception as e:
        logger.error(f"Error getting quests: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching quests: {str(e)}")


@router.get("/{quest_id}", response_model=Quest)
async def get_quest(quest_id: str = Path(..., description="The ID of the quest to retrieve")):
    """Get a specific quest by ID."""
    try:
        QuestValidator.validate_quest_id(quest_id)
        quest = QuestRepository.get_quest(quest_id)
        if not quest:
            raise HTTPException(status_code=404, detail=f"Quest {quest_id} not found")
        return quest
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting quest {quest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching quest: {str(e)}")


@router.post("/", response_model=Dict[str, str])
async def create_quest(quest: Quest = Body(..., description="The quest data")):
    """Create a new quest."""
    try:
        # Convert Pydantic model to dict
        quest_data = quest.dict()
        
        # Validate the quest data
        QuestValidator.validate_quest_data(quest_data)
        
        # Create the quest
        quest_id = QuestRepository.create_quest(quest_data)
        return {"id": quest_id, "message": "Quest created successfully"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating quest: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating quest: {str(e)}")


@router.put("/{quest_id}", response_model=Dict[str, str])
async def update_quest(
    quest_id: str = Path(..., description="The ID of the quest to update"),
    quest_data: Dict[str, Any] = Body(..., description="The updated quest data")
):
    """Update an existing quest."""
    try:
        QuestValidator.validate_quest_id(quest_id)
        QuestValidator.validate_quest_data(quest_data)
        
        # Ensure quest exists
        existing_quest = QuestRepository.get_quest(quest_id)
        if not existing_quest:
            raise HTTPException(status_code=404, detail=f"Quest {quest_id} not found")
        
        # Update the quest
        QuestRepository.update_quest(quest_id, quest_data)
        return {"message": f"Quest {quest_id} updated successfully"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating quest {quest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating quest: {str(e)}")


@router.delete("/{quest_id}", response_model=Dict[str, str])
async def delete_quest(quest_id: str = Path(..., description="The ID of the quest to delete")):
    """Delete a quest."""
    try:
        QuestValidator.validate_quest_id(quest_id)
        
        # Ensure quest exists
        existing_quest = QuestRepository.get_quest(quest_id)
        if not existing_quest:
            raise HTTPException(status_code=404, detail=f"Quest {quest_id} not found")
        
        # Delete the quest
        QuestRepository.delete_quest(quest_id)
        return {"message": f"Quest {quest_id} deleted successfully"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting quest {quest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting quest: {str(e)}")


@router.post("/{quest_id}/progress", response_model=Dict[str, Any])
async def update_quest_progress(
    quest_id: str = Path(..., description="The ID of the quest to update"),
    step_id: int = Query(..., description="The step ID to update"),
    completed: bool = Query(..., description="Whether the step is completed")
):
    """Update progress on a quest step."""
    try:
        QuestValidator.validate_quest_id(quest_id)
        
        # Ensure quest exists
        quest = QuestRepository.get_quest(quest_id)
        if not quest:
            raise HTTPException(status_code=404, detail=f"Quest {quest_id} not found")
        
        # Update step status
        quest_manager = QuestStateManager()
        updated_quest = quest_manager.update_step_status(quest_id, step_id, completed)
        
        return {
            "message": f"Quest {quest_id} step {step_id} updated successfully",
            "quest": updated_quest
        }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating quest {quest_id} progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating quest progress: {str(e)}")


@router.get("/journal/{player_id}", response_model=List[Dict[str, Any]])
async def get_player_journal(player_id: str = Path(..., description="The player ID")):
    """Get all journal entries for a player."""
    try:
        journal_entries = QuestRepository.get_journal_entries(player_id)
        return journal_entries
    except Exception as e:
        logger.error(f"Error getting journal entries for player {player_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching journal entries: {str(e)}")


@router.post("/journal", response_model=Dict[str, str])
async def create_journal_entry(entry_data: Dict[str, Any] = Body(..., description="The journal entry data")):
    """Create a new journal entry."""
    try:
        # Create the journal entry
        entry_id = QuestRepository.create_journal_entry(entry_data)
        return {"id": entry_id, "message": "Journal entry created successfully"}
    except Exception as e:
        logger.error(f"Error creating journal entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating journal entry: {str(e)}")


@router.get("/arc/{player_id}", response_model=Dict[str, Any])
async def get_player_arc(player_id: str = Path(..., description="The player ID")):
    """Get a player's story arc."""
    try:
        arc = QuestRepository.get_player_arc(player_id)
        if not arc:
            raise HTTPException(status_code=404, detail=f"Arc for player {player_id} not found")
        return arc
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting arc for player {player_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching player arc: {str(e)}")


@router.put("/arc/{player_id}", response_model=Dict[str, str])
async def update_player_arc(
    player_id: str = Path(..., description="The player ID"),
    arc_data: Dict[str, Any] = Body(..., description="The updated arc data")
):
    """Update a player's story arc."""
    try:
        # Save the arc
        QuestRepository.save_player_arc(player_id, arc_data)
        return {"message": f"Arc for player {player_id} updated successfully"}
    except Exception as e:
        logger.error(f"Error updating arc for player {player_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating player arc: {str(e)}") 