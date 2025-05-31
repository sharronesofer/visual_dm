"""LLM API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.llm.services.llm_service import LLMService
from backend.infrastructure.llm.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/llm", tags=["llm"])

# Dependency injection
async def get_llm_service() -> LLMService:
    return LLMService()

async def get_conversation_service() -> ConversationService:
    return ConversationService()

@router.post("/generate")
async def generate_response(
    request_data: Dict[str, Any],
    llm_service: LLMService = Depends(get_llm_service)
):
    """Generate LLM response"""
    try:
        response = await llm_service.process_llm_request(request_data)
        return response
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation")
async def start_conversation(
    initial_data: Dict[str, Any],
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Start new conversation"""
    try:
        conversation_id = await conversation_service.start_conversation(initial_data)
        return {"conversation_id": conversation_id}
    except Exception as e:
        logger.error(f"API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "llm"}
