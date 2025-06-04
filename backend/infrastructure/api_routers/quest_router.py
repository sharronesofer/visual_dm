"""
Quest API Router
Handles HTTP endpoints for quest operations according to Development Bible standards.
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

# Infrastructure imports (database models and schemas)
from backend.infrastructure.databases.quest_models import (
    QuestEntity,
    QuestChainEntity,
    QuestChainProgressEntity,
    CreateQuestRequest,
    UpdateQuestRequest,
    QuestResponse,
    QuestListResponse,
    QuestStepUpdateRequest,
    QuestActionRequest,
    QuestChainResponse,
    CreateQuestChainRequest
)

# Business logic imports (Bible-compliant location)
from backend.systems.quest import (
    QuestBusinessService,
    QuestData,
    CreateQuestData,
    UpdateQuestData,
    QuestStatus,
    QuestDifficulty,
    QuestTheme,
    QuestNotFoundError,
    QuestValidationError,
    QuestConflictError
)

# Infrastructure services
from backend.infrastructure.database import get_db_session
from backend.infrastructure.repositories.quest_repository import QuestRepositoryImpl
from backend.infrastructure.services.quest_validation_service import QuestValidationServiceImpl

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/quests", tags=["quests"])


def get_quest_service(db: Session = Depends(get_db_session)) -> QuestBusinessService:
    """Create quest business service with dependencies"""
    quest_repository = QuestRepositoryImpl(db)
    validation_service = QuestValidationServiceImpl()
    return QuestBusinessService(quest_repository, validation_service)


@router.post("/", response_model=QuestResponse)
async def create_quest(
    request: CreateQuestRequest,
    service: QuestBusinessService = Depends(get_quest_service)
):
    """Create a new quest"""
    try:
        # Convert API request to business data
        create_data = CreateQuestData(
            title=request.title,
            description=request.description,
            difficulty=QuestDifficulty(request.difficulty),
            theme=QuestTheme(request.theme),
            npc_id=request.npc_id,
            location_id=request.location_id,
            level=request.level,
            steps=[step.model_dump() for step in request.steps],
            rewards=request.rewards.model_dump() if request.rewards else None,
            properties=request.properties,
            expires_at=request.expires_at
        )
        
        quest = service.create_quest(create_data)
        
        # Convert business data to API response
        return QuestResponse(
            id=quest.id,
            title=quest.title,
            description=quest.description,
            status=quest.status.value,
            difficulty=quest.difficulty.value,
            theme=quest.theme.value,
            npc_id=quest.npc_id,
            player_id=quest.player_id,
            location_id=quest.location_id,
            level=quest.level,
            steps=[step.to_dict() for step in quest.steps],
            rewards=quest.rewards.to_dict() if quest.rewards else {"gold": 0, "experience": 0, "reputation": {}, "items": [], "special": {}},
            is_main_quest=quest.is_main_quest,
            tags=quest.tags,
            properties=quest.properties,
            created_at=quest.created_at,
            updated_at=quest.updated_at,
            expires_at=quest.expires_at,
            chain_id=quest.chain_id,
            chain_position=quest.chain_position,
            chain_prerequisites=quest.chain_prerequisites,
            chain_unlocks=quest.chain_unlocks,
            is_chain_final=quest.is_chain_final
        )
        
    except QuestValidationError as e:
        logger.warning(f"Quest validation error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except QuestConflictError as e:
        logger.warning(f"Quest conflict error: {e.message}")
        raise HTTPException(status_code=409, detail=e.message)
    except Exception as e:
        logger.error(f"Error creating quest: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create quest")


@router.get("/{quest_id}", response_model=QuestResponse)
async def get_quest(
    quest_id: UUID,
    service: QuestBusinessService = Depends(get_quest_service)
):
    """Get quest by ID"""
    try:
        quest = service.get_quest_by_id(quest_id)
        if not quest:
            raise HTTPException(status_code=404, detail=f"Quest {quest_id} not found")
        
        return QuestResponse(
            id=quest.id,
            title=quest.title,
            description=quest.description,
            status=quest.status.value,
            difficulty=quest.difficulty.value,
            theme=quest.theme.value,
            npc_id=quest.npc_id,
            player_id=quest.player_id,
            location_id=quest.location_id,
            level=quest.level,
            steps=[step.to_dict() for step in quest.steps],
            rewards=quest.rewards.to_dict() if quest.rewards else {"gold": 0, "experience": 0, "reputation": {}, "items": [], "special": {}},
            is_main_quest=quest.is_main_quest,
            tags=quest.tags,
            properties=quest.properties,
            created_at=quest.created_at,
            updated_at=quest.updated_at,
            expires_at=quest.expires_at,
            chain_id=quest.chain_id,
            chain_position=quest.chain_position,
            chain_prerequisites=quest.chain_prerequisites,
            chain_unlocks=quest.chain_unlocks,
            is_chain_final=quest.is_chain_final
        )
        
    except QuestNotFoundError as e:
        logger.warning(f"Quest not found: {e.message}")
        raise HTTPException(status_code=404, detail=e.message)
    except Exception as e:
        logger.error(f"Error getting quest {quest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get quest")


@router.put("/{quest_id}", response_model=QuestResponse)
async def update_quest(
    quest_id: UUID,
    request: UpdateQuestRequest,
    service: QuestBusinessService = Depends(get_quest_service)
):
    """Update quest"""
    try:
        # Convert API request to business data
        update_fields = {}
        if request.title is not None:
            update_fields['title'] = request.title
        if request.description is not None:
            update_fields['description'] = request.description
        if request.status is not None:
            update_fields['status'] = request.status
        if request.difficulty is not None:
            update_fields['difficulty'] = request.difficulty
        if request.theme is not None:
            update_fields['theme'] = request.theme
        if request.npc_id is not None:
            update_fields['npc_id'] = request.npc_id
        if request.player_id is not None:
            update_fields['player_id'] = request.player_id
        if request.location_id is not None:
            update_fields['location_id'] = request.location_id
        if request.level is not None:
            update_fields['level'] = request.level
        if request.steps is not None:
            update_fields['steps'] = [step.model_dump() for step in request.steps]
        if request.rewards is not None:
            update_fields['rewards'] = request.rewards.model_dump()
        if request.properties is not None:
            update_fields['properties'] = request.properties
        if request.expires_at is not None:
            update_fields['expires_at'] = request.expires_at
            
        update_data = UpdateQuestData(**update_fields)
        quest = service.update_quest(quest_id, update_data)
        
        return QuestResponse(
            id=quest.id,
            title=quest.title,
            description=quest.description,
            status=quest.status.value,
            difficulty=quest.difficulty.value,
            theme=quest.theme.value,
            npc_id=quest.npc_id,
            player_id=quest.player_id,
            location_id=quest.location_id,
            level=quest.level,
            steps=[step.to_dict() for step in quest.steps],
            rewards=quest.rewards.to_dict() if quest.rewards else {"gold": 0, "experience": 0, "reputation": {}, "items": [], "special": {}},
            is_main_quest=quest.is_main_quest,
            tags=quest.tags,
            properties=quest.properties,
            created_at=quest.created_at,
            updated_at=quest.updated_at,
            expires_at=quest.expires_at,
            chain_id=quest.chain_id,
            chain_position=quest.chain_position,
            chain_prerequisites=quest.chain_prerequisites,
            chain_unlocks=quest.chain_unlocks,
            is_chain_final=quest.is_chain_final
        )
        
    except QuestNotFoundError as e:
        logger.warning(f"Quest not found: {e.message}")
        raise HTTPException(status_code=404, detail=e.message)
    except QuestValidationError as e:
        logger.warning(f"Quest validation error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error updating quest {quest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update quest")


@router.delete("/{quest_id}")
async def delete_quest(
    quest_id: UUID,
    service: QuestBusinessService = Depends(get_quest_service)
):
    """Delete quest"""
    try:
        success = service.delete_quest(quest_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Quest {quest_id} not found")
        return {"message": "Quest deleted successfully"}
    except QuestNotFoundError as e:
        logger.warning(f"Quest not found: {e.message}")
        raise HTTPException(status_code=404, detail=e.message)
    except QuestValidationError as e:
        logger.warning(f"Quest validation error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error deleting quest {quest_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete quest")


@router.get("/", response_model=QuestListResponse)
async def list_quests(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    service: QuestBusinessService = Depends(get_quest_service)
):
    """List quests with pagination and filters"""
    try:
        quests, total = service.list_quests(page, size, status, search)
        
        has_next = (page * size) < total
        has_prev = page > 1
        
        quest_responses = []
        for quest in quests:
            quest_responses.append(QuestResponse(
                id=quest.id,
                title=quest.title,
                description=quest.description,
                status=quest.status.value,
                difficulty=quest.difficulty.value,
                theme=quest.theme.value,
                npc_id=quest.npc_id,
                player_id=quest.player_id,
                location_id=quest.location_id,
                level=quest.level,
                steps=[step.to_dict() for step in quest.steps],
                rewards=quest.rewards.to_dict() if quest.rewards else {"gold": 0, "experience": 0, "reputation": {}, "items": [], "special": {}},
                is_main_quest=quest.is_main_quest,
                tags=quest.tags,
                properties=quest.properties,
                created_at=quest.created_at,
                updated_at=quest.updated_at,
                expires_at=quest.expires_at,
                chain_id=quest.chain_id,
                chain_position=quest.chain_position,
                chain_prerequisites=quest.chain_prerequisites,
                chain_unlocks=quest.chain_unlocks,
                is_chain_final=quest.is_chain_final
            ))
        
        return QuestListResponse(
            items=quest_responses,
            total=total,
            page=page,
            size=size,
            has_next=has_next,
            has_prev=has_prev
        )
    except Exception as e:
        logger.error(f"Error listing quests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list quests")


@router.get("/player/{player_id}", response_model=List[QuestResponse])
async def get_player_quests(
    player_id: str,
    status: Optional[str] = Query(None),
    service: QuestBusinessService = Depends(get_quest_service)
):
    """Get all quests for a specific player"""
    try:
        quests = service.get_player_quests(player_id, status)
        quest_responses = []
        for quest in quests:
            quest_responses.append(QuestResponse(
                id=quest.id,
                title=quest.title,
                description=quest.description,
                status=quest.status.value,
                difficulty=quest.difficulty.value,
                theme=quest.theme.value,
                npc_id=quest.npc_id,
                player_id=quest.player_id,
                location_id=quest.location_id,
                level=quest.level,
                steps=[step.to_dict() for step in quest.steps],
                rewards=quest.rewards.to_dict() if quest.rewards else {"gold": 0, "experience": 0, "reputation": {}, "items": [], "special": {}},
                is_main_quest=quest.is_main_quest,
                tags=quest.tags,
                properties=quest.properties,
                created_at=quest.created_at,
                updated_at=quest.updated_at,
                expires_at=quest.expires_at,
                chain_id=quest.chain_id,
                chain_position=quest.chain_position,
                chain_prerequisites=quest.chain_prerequisites,
                chain_unlocks=quest.chain_unlocks,
                is_chain_final=quest.is_chain_final
            ))
        return quest_responses
    except Exception as e:
        logger.error(f"Error getting player quests: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get player quests")


@router.post("/{quest_id}/actions")
async def quest_action(
    quest_id: UUID,
    request: QuestActionRequest,
    service: QuestBusinessService = Depends(get_quest_service)
):
    """Perform actions on quests (assign, abandon, complete step, etc.)"""
    try:
        if request.action == "assign" and request.player_id:
            quest = service.assign_quest_to_player(quest_id, request.player_id)
            return {"message": f"Quest assigned to player {request.player_id}", "quest_id": str(quest.id)}
            
        elif request.action == "abandon" and request.player_id:
            quest = service.abandon_quest(quest_id, request.player_id, request.reason or "player_choice")
            return {"message": f"Quest abandoned by player {request.player_id}", "quest_id": str(quest.id)}
            
        elif request.action == "complete_step" and request.player_id and request.step_id:
            quest = service.complete_quest_step(quest_id, request.step_id, request.player_id)
            return {"message": f"Quest step {request.step_id} completed", "quest_id": str(quest.id)}
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action or missing parameters")
            
    except QuestNotFoundError as e:
        logger.warning(f"Quest not found: {e.message}")
        raise HTTPException(status_code=404, detail=e.message)
    except QuestValidationError as e:
        logger.warning(f"Quest validation error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Error performing quest action: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to perform quest action")


@router.get("/statistics/", response_model=dict)
async def get_quest_statistics(
    service: QuestBusinessService = Depends(get_quest_service)
):
    """Get quest system statistics"""
    try:
        return service.get_quest_statistics()
    except Exception as e:
        logger.error(f"Error getting quest statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get quest statistics") 