"""
Enhanced LLM Service for Visual DM

Provides high-level interface for all AI content generation using the hybrid model architecture.
Integrates with the model manager for optimal model selection and performance.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
import time

from backend.infrastructure.llm.services.model_manager import (
    get_model_manager, ModelManager, ModelType
)
from backend.infrastructure.llm.services.prompt_service import PromptService
from backend.infrastructure.models import BaseModel

logger = logging.getLogger(__name__)

class GenerationContext(Enum):
    """Different contexts for content generation"""
    DIALOGUE = "dialogue"
    NARRATIVE = "narrative"
    WORLD_BUILDING = "world_building"
    CHARACTER_CREATION = "character_creation"
    QUEST_GENERATION = "quest_generation"
    SYSTEM_RESPONSE = "system_response"

class LLMService:
    """
    High-level service for AI content generation using hybrid model architecture.
    
    Features:
    - Context-aware model selection
    - Prompt template management
    - Response caching
    - Performance monitoring
    - Fallback handling
    """
    
    def __init__(self):
        self.model_manager: Optional[ModelManager] = None
        self.prompt_service = PromptService()
        self.response_cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
        # Context to model type mapping
        self.context_model_mapping = {
            GenerationContext.DIALOGUE: ModelType.DIALOGUE,
            GenerationContext.NARRATIVE: ModelType.NARRATIVE,
            GenerationContext.WORLD_BUILDING: ModelType.WORLD_BUILDING,
            GenerationContext.CHARACTER_CREATION: ModelType.CHARACTER,
            GenerationContext.QUEST_GENERATION: ModelType.QUEST,
            GenerationContext.SYSTEM_RESPONSE: ModelType.GENERAL
        }
    
    async def initialize(self):
        """Initialize the LLM service and model manager"""
        self.model_manager = await get_model_manager()
        await self.prompt_service.initialize()
    
    async def generate_content(self,
                              prompt: str,
                              context: GenerationContext = GenerationContext.SYSTEM_RESPONSE,
                              template_vars: Optional[Dict[str, Any]] = None,
                              cache_key: Optional[str] = None,
                              **kwargs) -> Dict[str, Any]:
        """
        Generate content using the optimal model for the given context.
        
        Args:
            prompt: The input prompt or template name
            context: Generation context to determine optimal model
            template_vars: Variables for prompt template substitution
            cache_key: Optional cache key for response caching
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing generated content and metadata
        """
        if not self.model_manager:
            await self.initialize()
        
        # Check cache first
        if cache_key:
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_response
        
        # Process prompt template if needed
        if template_vars:
            processed_prompt = self.prompt_service.process_template(prompt, template_vars)
        else:
            processed_prompt = prompt
        
        # Determine optimal model type
        model_type = self.context_model_mapping.get(context, ModelType.GENERAL)
        
        try:
            # Generate response using model manager
            response_data = await self.model_manager.generate_response(
                prompt=processed_prompt,
                model_type=model_type,
                **kwargs
            )
            
            # Enhance response with service-level metadata
            enhanced_response = {
                **response_data,
                "context": context.value,
                "timestamp": time.time(),
                "cached": False
            }
            
            # Cache the response if cache key provided
            if cache_key:
                self._cache_response(cache_key, enhanced_response)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error generating content for context {context}: {e}")
            raise e
    
    async def generate_dialogue(self,
                               character_name: str,
                               player_message: str,
                               character_context: Optional[Dict[str, Any]] = None,
                               conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate dynamic dialogue for an NPC character.
        
        Args:
            character_name: Name of the character speaking
            player_message: What the player said
            character_context: Character personality, background, etc.
            conversation_history: Previous messages in the conversation
            
        Returns:
            Generated dialogue response
        """
        template_vars = {
            "character_name": character_name,
            "player_message": player_message,
            "character_context": character_context or {},
            "conversation_history": conversation_history or []
        }
        
        result = await self.generate_content(
            prompt="dialogue_response_template",
            context=GenerationContext.DIALOGUE,
            template_vars=template_vars,
            temperature=0.8,  # Higher temperature for creative dialogue
            max_tokens=300
        )
        
        return result["response"]
    
    async def generate_narrative_description(self,
                                           location_name: str,
                                           time_of_day: str,
                                           weather: str,
                                           context_details: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate atmospheric narrative description for a location.
        
        Args:
            location_name: Name of the location
            time_of_day: Current time context
            weather: Weather conditions
            context_details: Additional contextual information
            
        Returns:
            Generated narrative description
        """
        template_vars = {
            "location_name": location_name,
            "time_of_day": time_of_day,
            "weather": weather,
            "context_details": context_details or {}
        }
        
        result = await self.generate_content(
            prompt="narrative_description_template",
            context=GenerationContext.NARRATIVE,
            template_vars=template_vars,
            temperature=0.7,
            max_tokens=500
        )
        
        return result["response"]
    
    async def generate_quest_content(self,
                                   quest_type: str,
                                   difficulty: str,
                                   location: str,
                                   player_level: int) -> Dict[str, str]:
        """
        Generate dynamic quest content including title, description, and objectives.
        
        Args:
            quest_type: Type of quest (combat, exploration, social, etc.)
            difficulty: Difficulty level
            location: Quest location
            player_level: Player's current level
            
        Returns:
            Dict containing quest title, description, and objectives
        """
        template_vars = {
            "quest_type": quest_type,
            "difficulty": difficulty,
            "location": location,
            "player_level": player_level
        }
        
        result = await self.generate_content(
            prompt="quest_generation_template",
            context=GenerationContext.QUEST_GENERATION,
            template_vars=template_vars,
            temperature=0.6,
            max_tokens=800
        )
        
        # Parse the response to extract different quest components
        response_text = result["response"]
        
        # Simple parsing - in production, this would be more sophisticated
        lines = response_text.split('\n')
        quest_data = {
            "title": "Generated Quest",
            "description": response_text,
            "objectives": ["Complete the quest"]
        }
        
        # Try to extract structured data if the model formatted it properly
        for line in lines:
            if line.startswith("Title:"):
                quest_data["title"] = line.replace("Title:", "").strip()
            elif line.startswith("Description:"):
                quest_data["description"] = line.replace("Description:", "").strip()
            elif line.startswith("Objectives:"):
                quest_data["objectives"] = [line.replace("Objectives:", "").strip()]
        
        return quest_data
    
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment and emotional tone of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict containing sentiment scores
        """
        template_vars = {
            "text_to_analyze": text
        }
        
        result = await self.generate_content(
            prompt="sentiment_analysis_template",
            context=GenerationContext.SYSTEM_RESPONSE,
            template_vars=template_vars,
            temperature=0.1,  # Low temperature for analytical tasks
            max_tokens=200
        )
        
        # Parse sentiment analysis result
        try:
            # Assume the model returns JSON-formatted sentiment data
            sentiment_data = json.loads(result["response"])
            return sentiment_data
        except:
            # Fallback if parsing fails
            return {
                "positive": 0.5,
                "negative": 0.5,
                "neutral": 0.5,
                "confidence": 0.1
            }
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if still valid"""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                cached_data["cached"] = True
                return cached_data
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response_data: Dict[str, Any]):
        """Cache a response with timestamp"""
        self.response_cache[cache_key] = {
            **response_data,
            "timestamp": time.time()
        }
        
        # Simple cache size management
        if len(self.response_cache) > 1000:
            # Remove oldest entries
            sorted_keys = sorted(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k]["timestamp"]
            )
            for key in sorted_keys[:100]:  # Remove oldest 100 entries
                del self.response_cache[key]
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status and metrics"""
        if not self.model_manager:
            return {"status": "not_initialized"}
        
        model_stats = self.model_manager.get_model_stats()
        
        return {
            "status": "active",
            "cache_size": len(self.response_cache),
            "cache_hit_rate": model_stats["global_stats"].get("cache_hits", 0) / max(model_stats["global_stats"].get("total_requests", 1), 1),
            "model_stats": model_stats,
            "supported_contexts": [context.value for context in GenerationContext]
        }

# Global service instance
_llm_service = None

async def get_llm_service() -> LLMService:
    """Get the global LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
        await _llm_service.initialize()
    return _llm_service
