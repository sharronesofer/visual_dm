"""
Memory System API Routes.

This module provides REST API endpoints for memory management operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.systems.memory.services.memory_manager_core import MemoryManager
from backend.systems.memory.memory_categories import MemoryCategory
from backend.systems.memory.summarization_styles import get_summarization_styles


# Request/Response Models
class MemoryCreateRequest(BaseModel):
    npc_id: str
    content: str
    memory_type: str = "regular"
    categories: Optional[List[str]] = None
    importance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class MemoryResponse(BaseModel):
    id: str
    npc_id: str
    content: str
    summary: str
    memory_type: str
    categories: List[str]
    importance: float
    created_at: str
    access_count: int
    last_accessed: Optional[str]
    saliency: float
    metadata: Dict[str, Any]


class InteractionRequest(BaseModel):
    npc_id: str
    interaction_data: Dict[str, Any]
    context: Optional[str] = None


class LongTermMemoryRequest(BaseModel):
    npc_id: str
    memory_updates: Dict[str, Any]
    context: Optional[str] = None


class BeliefEvaluationRequest(BaseModel):
    npc_id: str
    belief_context: str
    evaluation_criteria: Optional[Dict[str, Any]] = None


# Create router
router = APIRouter(prefix="/memory", tags=["memory"])


@router.post("/create", response_model=MemoryResponse)
async def create_memory(request: MemoryCreateRequest):
    """Create a new memory for an NPC."""
    try:
        memory_manager = MemoryManager.get_instance()
        
        memory = await memory_manager.create_memory(
            npc_id=request.npc_id,
            content=request.content,
            memory_type=request.memory_type,
            categories=request.categories,
            importance=request.importance,
            metadata=request.metadata
        )
        
        return MemoryResponse(**memory.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create memory: {str(e)}")


@router.get("/recent/{npc_id}")
async def get_recent_memory(
    npc_id: str,
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    memory_type: Optional[str] = Query(None)
):
    """Get recent memories for an NPC."""
    try:
        memory_manager = MemoryManager.get_instance()
        
        # Get all memories for the NPC
        memories = await memory_manager.get_memories_by_npc(npc_id)
        
        # Filter by category if specified
        if category:
            memories = [m for m in memories if category in m.categories]
        
        # Filter by memory type if specified
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        # Sort by creation time (most recent first) and limit
        memories.sort(key=lambda m: m.created_at, reverse=True)
        recent_memories = memories[:limit]
        
        return [MemoryResponse(**memory.to_dict()) for memory in recent_memories]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent memories: {str(e)}")


@router.delete("/clear/{npc_id}")
async def clear_npc_memory(
    npc_id: str,
    memory_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    confirm: bool = Query(False)
):
    """Clear memories for an NPC (with optional filtering)."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Must set confirm=true to clear memories")
    
    try:
        memory_manager = MemoryManager.get_instance()
        
        # Get memories to clear
        memories = await memory_manager.get_memories_by_npc(npc_id)
        
        # Apply filters
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        if category:
            memories = [m for m in memories if category in m.categories]
        
        # Clear the filtered memories
        cleared_count = 0
        for memory in memories:
            await memory_manager.delete_memory(memory.memory_id)
            cleared_count += 1
        
        return {"cleared_count": cleared_count, "npc_id": npc_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear memories: {str(e)}")


@router.post("/interaction")
async def store_npc_interaction(request: InteractionRequest):
    """Store an interaction as a memory."""
    try:
        memory_manager = MemoryManager.get_instance()
        
        # Extract relevant information from interaction data
        content = request.interaction_data.get('content', 'Interaction occurred')
        participants = request.interaction_data.get('participants', [])
        interaction_type = request.interaction_data.get('type', 'general')
        
        # Create memory content
        memory_content = f"Interaction: {content}"
        if participants:
            memory_content += f" (with {', '.join(participants)})"
        
        # Determine categories based on interaction type
        categories = ['interaction']
        if interaction_type == 'conversation':
            categories.append('conversation')
        elif interaction_type == 'combat':
            categories.extend(['event', 'trauma'])
        elif interaction_type == 'trade':
            categories.append('event')
        
        # Create the memory
        memory = await memory_manager.create_memory(
            npc_id=request.npc_id,
            content=memory_content,
            categories=categories,
            metadata={
                'interaction_data': request.interaction_data,
                'context': request.context,
                'interaction_type': interaction_type
            }
        )
        
        return MemoryResponse(**memory.to_dict())
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to store interaction: {str(e)}")


@router.put("/long-term")
async def update_npc_long_term_memory(request: LongTermMemoryRequest):
    """Update long-term memory patterns for an NPC."""
    try:
        memory_manager = MemoryManager.get_instance()
        
        # Get existing memories
        memories = await memory_manager.get_memories_by_npc(request.npc_id)
        
        # Apply updates based on memory_updates
        updated_memories = []
        for memory in memories:
            # Check if this memory should be updated
            should_update = False
            importance_delta = 0.0
            
            # Example update logic - can be enhanced
            for update_key, update_value in request.memory_updates.items():
                if update_key in memory.content.lower():
                    should_update = True
                    importance_delta += update_value.get('importance_change', 0.0)
            
            if should_update:
                # Update memory importance
                await memory_manager.update_memory_importance(
                    memory.memory_id, 
                    importance_delta
                )
                updated_memories.append(memory.memory_id)
        
        return {
            "npc_id": request.npc_id,
            "updated_memories": updated_memories,
            "context": request.context
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update long-term memory: {str(e)}")


@router.post("/evaluate-beliefs")
async def evaluate_beliefs(request: BeliefEvaluationRequest):
    """Evaluate NPC beliefs based on memory context."""
    try:
        memory_manager = MemoryManager.get_instance()
        
        # Get belief-related memories
        memories = await memory_manager.get_memories_by_category(
            request.npc_id, 
            'belief'
        )
        
        # Also get identity and core memories
        identity_memories = await memory_manager.get_memories_by_category(
            request.npc_id, 
            'identity'
        )
        core_memories = await memory_manager.get_memories_by_type(
            request.npc_id, 
            'core'
        )
        
        all_relevant_memories = memories + identity_memories + core_memories
        
        # Evaluate beliefs based on context
        belief_evaluation = {
            "npc_id": request.npc_id,
            "belief_context": request.belief_context,
            "relevant_memories": len(all_relevant_memories),
            "beliefs": []
        }
        
        # Extract beliefs from memories
        for memory in all_relevant_memories:
            if any(keyword in memory.content.lower() for keyword in ['believe', 'think', 'value', 'principle']):
                belief_evaluation["beliefs"].append({
                    "memory_id": memory.memory_id,
                    "content": memory.content,
                    "importance": memory.importance,
                    "saliency": memory.get_current_saliency()
                })
        
        return belief_evaluation
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate beliefs: {str(e)}")


@router.get("/summarization-styles")
async def get_summarization_styles_endpoint():
    """Get available memory summarization styles."""
    try:
        styles = get_summarization_styles()
        return {"summarization_styles": styles}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summarization styles: {str(e)}")


@router.get("/search/{npc_id}")
async def search_memories(
    npc_id: str,
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    category: Optional[str] = Query(None),
    min_relevance: float = Query(0.1, ge=0.0, le=1.0)
):
    """Search memories by content relevance."""
    try:
        memory_manager = MemoryManager.get_instance()
        
        # Get all memories for the NPC
        memories = await memory_manager.get_memories_by_npc(npc_id)
        
        # Filter by category if specified
        if category:
            memories = [m for m in memories if category in m.categories]
        
        # Calculate relevance scores and filter
        relevant_memories = []
        for memory in memories:
            from backend.systems.memory.saliency_scoring import calculate_memory_relevance
            relevance = calculate_memory_relevance(memory.to_dict(), query)
            
            if relevance >= min_relevance:
                memory_dict = memory.to_dict()
                memory_dict['relevance'] = relevance
                relevant_memories.append(memory_dict)
        
        # Sort by relevance and limit
        relevant_memories.sort(key=lambda m: m['relevance'], reverse=True)
        
        return {
            "query": query,
            "npc_id": npc_id,
            "total_found": len(relevant_memories),
            "memories": relevant_memories[:limit]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search memories: {str(e)}")


@router.get("/categories")
async def get_memory_categories():
    """Get all available memory categories."""
    try:
        from backend.systems.memory.memory_categories import get_all_categories, get_category_info
        
        categories = []
        for category in get_all_categories():
            info = get_category_info(category)
            categories.append({
                "value": category.value,
                "display_name": info.display_name,
                "description": info.description,
                "default_importance": info.default_importance,
                "decay_modifier": info.decay_modifier,
                "is_permanent": info.is_permanent
            })
        
        return {"categories": categories}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


# Export the router
__all__ = ["router"]
