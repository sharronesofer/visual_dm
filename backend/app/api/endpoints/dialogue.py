from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import time

from ...services.dialogue import GPTClient, DialogueGenerationService, GPTResponse, GPTConfig
from ...services.dialogue import ResponseCacheManager, ConversationContextManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dialogue", tags=["dialogue"])

# Dependency to get GPTClient instance
def get_gpt_client():
    """Returns the GPTClient instance."""
    # TODO: Get API key from environment/config
    api_key = "YOUR_API_KEY_HERE"  # Replace with actual API key sourcing logic
    return GPTClient({
        "apiKey": api_key,
        "rateLimit": 60,
        "maxRetries": 3
    })

# Dependency to get DialogueGenerationService
def get_dialogue_service():
    """Returns the DialogueGenerationService instance."""
    client = get_gpt_client()
    default_config: GPTConfig = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "maxTokens": 512
    }
    return DialogueGenerationService(client, default_config)

# Dependency to get ResponseCacheManager
def get_cache_manager():
    """Returns the ResponseCacheManager instance."""
    return ResponseCacheManager({
        "maxSize": 1000,
        "expiryMs": 5 * 60 * 1000  # 5 minutes
    })

# Dependency to get ConversationContextManager
def get_context_manager():
    """Returns the ConversationContextManager instance."""
    return ConversationContextManager({
        "maxTokens": 1024,
        "maxTurns": 10
    })

# Request models
class DialogueRequest(BaseModel):
    prompt: str
    context: List[str] = []
    config: Optional[Dict[str, Any]] = None
    conversationId: Optional[str] = None

# Response models
class DialogueResponse(BaseModel):
    text: str
    usage: Optional[Dict[str, int]] = None
    cacheHit: bool = False
    responseTimeMs: int
    error: Optional[str] = None

@router.post("/generate", response_model=DialogueResponse)
async def generate_dialogue(
    request: DialogueRequest,
    dialogue_service: DialogueGenerationService = Depends(get_dialogue_service),
    cache_manager: ResponseCacheManager = Depends(get_cache_manager),
):
    """
    Generate dialogue based on prompt and context.
    Handles caching and error handling.
    """
    start_time = time.time()
    
    # Check cache first
    cached_response = cache_manager.get(request.prompt, request.context)
    if cached_response:
        return DialogueResponse(
            text=cached_response,
            cacheHit=True,
            responseTimeMs=int((time.time() - start_time) * 1000)
        )
    
    # Generate new response
    try:
        response = await dialogue_service.generate_dialogue(
            request.prompt, 
            request.context, 
            request.config
        )
        
        # Check for error
        if 'error' in response and response['error']:
            logger.error(f"Error generating dialogue: {response['error']}")
            return DialogueResponse(
                text="",
                error=response['error'],
                responseTimeMs=int((time.time() - start_time) * 1000)
            )
        
        # Cache successful response
        if 'text' in response and response['text']:
            metadata = {
                "tokensUsed": response.get('usage', {}).get('total_tokens', 0),
                "responseTimeMs": int((time.time() - start_time) * 1000),
                "model": request.config.get('model', 'gpt-3.5-turbo') if request.config else 'gpt-3.5-turbo',
                "additional": {}
            }
            cache_manager.set(request.prompt, request.context, response['text'], metadata)
        
        return DialogueResponse(
            text=response.get('text', ''),
            usage=response.get('usage'),
            cacheHit=False,
            responseTimeMs=int((time.time() - start_time) * 1000)
        )
    except Exception as e:
        logger.exception(f"Unhandled exception in dialogue generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dialogue: {str(e)}"
        )

@router.post("/clearCache")
async def clear_cache(
    cache_manager: ResponseCacheManager = Depends(get_cache_manager),
):
    """Clear the response cache."""
    cache_manager.clear()
    return {"status": "success", "message": "Cache cleared successfully"}

@router.get("/cacheStats")
async def get_cache_stats(
    cache_manager: ResponseCacheManager = Depends(get_cache_manager),
):
    """Get cache statistics."""
    stats = cache_manager.get_analytics()
    return stats 