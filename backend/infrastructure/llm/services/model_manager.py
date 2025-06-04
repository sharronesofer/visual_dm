"""
Model Manager for Visual DM LLM System

Handles multiple model providers, load balancing, and failover between local and cloud models.
Supports the hybrid architecture with shared base models and specialized instances.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from contextlib import asynccontextmanager
import aiohttp
import json
import openai
from anthropic import Anthropic

from backend.infrastructure.models import BaseModel
from backend.infrastructure.llm.config.llm_config import llm_config, LLMProvider
from backend.infrastructure.llm.middleware.llm_middleware import llm_middleware
from backend.infrastructure.llm.utils.llm_utils import LLMUtils

logger = logging.getLogger(__name__)

class ModelType(Enum):
    """Model specialization types"""
    GENERAL = "general"
    DIALOGUE = "dialogue"
    NARRATIVE = "narrative"
    WORLD_BUILDING = "world_building"
    CHARACTER = "character"
    QUEST = "quest"

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    provider: LLMProvider
    model_id: str
    model_type: ModelType
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout_seconds: int = 30
    priority: int = 1  # Higher = preferred
    cost_per_token: float = 0.0  # For cost tracking
    concurrent_limit: int = 3

@dataclass
class ModelInstance:
    """Runtime instance of a model"""
    config: ModelConfig
    active_requests: int = 0
    total_requests: int = 0
    total_tokens: int = 0
    avg_response_time: float = 0.0
    error_count: int = 0
    last_used: float = 0.0
    available: bool = True
    cost_tracking: float = 0.0  # Total cost incurred

class ModelManager:
    """
    Manages multiple LLM models with hybrid architecture support.
    
    Features:
    - Local Ollama models as primary
    - Cloud models as fallback  
    - Load balancing across instances
    - Automatic failover
    - Performance monitoring
    - Cost tracking
    """
    
    def __init__(self):
        self.models: Dict[str, ModelInstance] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.openai_client: Optional[openai.AsyncOpenAI] = None
        self.anthropic_client: Optional[Anthropic] = None
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "fallback_uses": 0,
            "error_rate": 0.0,
            "total_cost": 0.0
        }
        
        # Load model configurations from infrastructure
        self._load_model_configs_from_infrastructure()
    
    def _load_model_configs_from_infrastructure(self):
        """Load model configurations from infrastructure"""
        configs = []
        
        # Get enabled providers from infrastructure
        enabled_providers = llm_config.get_enabled_providers()
        
        for provider in enabled_providers:
            provider_config = llm_config.get_provider_config(provider)
            if not provider_config:
                continue
                
            if provider == LLMProvider.OLLAMA:
                # Local Ollama models (highest priority)
                configs.extend([
                    ModelConfig(
                        name="llama2-13b-chat-local",
                        provider=provider,
                        model_id="llama2:13b-chat",
                        model_type=ModelType.GENERAL,
                        priority=10,  # Highest priority
                        concurrent_limit=2,
                        timeout_seconds=provider_config.timeout
                    ),
                    ModelConfig(
                        name="mistral-7b-dialogue-local", 
                        provider=provider,
                        model_id="mistral:7b-instruct",
                        model_type=ModelType.DIALOGUE,
                        priority=10,
                        concurrent_limit=3,
                        timeout_seconds=provider_config.timeout
                    ),
                    ModelConfig(
                        name="codellama-13b-narrative-local",
                        provider=provider,
                        model_id="codellama:13b-instruct",
                        model_type=ModelType.NARRATIVE,
                        priority=10,
                        concurrent_limit=2,
                        timeout_seconds=provider_config.timeout
                    )
                ])
            
            elif provider == LLMProvider.OPENAI:
                # OpenAI cloud models (fallback/backup)
                configs.extend([
                    ModelConfig(
                        name="gpt-4-general",
                        provider=provider,
                        model_id="gpt-4",
                        model_type=ModelType.GENERAL,
                        priority=8,  # High priority fallback
                        cost_per_token=0.00003,
                        concurrent_limit=5,
                        timeout_seconds=provider_config.timeout
                    ),
                    ModelConfig(
                        name="gpt-4-dialogue",
                        provider=provider,
                        model_id="gpt-4",
                        model_type=ModelType.DIALOGUE,
                        priority=8,
                        cost_per_token=0.00003,
                        concurrent_limit=5,
                        timeout_seconds=provider_config.timeout
                    ),
                    ModelConfig(
                        name="gpt-3.5-turbo-general",
                        provider=provider,
                        model_id="gpt-3.5-turbo",
                        model_type=ModelType.GENERAL,
                        priority=6,  # Lower priority fallback
                        cost_per_token=0.000002,
                        concurrent_limit=10,
                        timeout_seconds=provider_config.timeout
                    )
                ])
            
            elif provider == LLMProvider.ANTHROPIC:
                # Anthropic cloud models (fallback)
                configs.extend([
                    ModelConfig(
                        name="claude-3-sonnet-general",
                        provider=provider,
                        model_id="claude-3-sonnet-20240229",
                        model_type=ModelType.GENERAL,
                        priority=7,  # Medium-high priority fallback
                        cost_per_token=0.000015,
                        concurrent_limit=5,
                        timeout_seconds=provider_config.timeout
                    ),
                    ModelConfig(
                        name="claude-3-haiku-fast",
                        provider=provider,
                        model_id="claude-3-haiku-20240307",
                        model_type=ModelType.GENERAL,
                        priority=5,  # Lower cost option
                        cost_per_token=0.00000125,
                        concurrent_limit=10,
                        timeout_seconds=provider_config.timeout
                    )
                ])
            
            elif provider == LLMProvider.PERPLEXITY:
                # Perplexity research models
                configs.append(ModelConfig(
                    name="perplexity-research",
                    provider=provider,
                    model_id="sonar-medium-online",
                    model_type=ModelType.WORLD_BUILDING,
                    priority=6,
                    cost_per_token=0.00002,
                    concurrent_limit=3,
                    timeout_seconds=provider_config.timeout
                ))
        
        # Create model instances
        for config in configs:
            self.models[config.name] = ModelInstance(config=config)
    
    async def initialize(self):
        """Initialize the model manager and check model availability"""
        self.session = aiohttp.ClientSession()
        
        # Initialize OpenAI client if available
        openai_config = llm_config.get_provider_config(LLMProvider.OPENAI)
        if openai_config and openai_config.api_key:
            self.openai_client = openai.AsyncOpenAI(
                api_key=openai_config.api_key,
                base_url=openai_config.base_url
            )
        
        # Initialize Anthropic client if available
        anthropic_config = llm_config.get_provider_config(LLMProvider.ANTHROPIC)
        if anthropic_config and anthropic_config.api_key:
            self.anthropic_client = Anthropic(
                api_key=anthropic_config.api_key,
                base_url=anthropic_config.base_url
            )
        
        await self._check_model_availability()
    
    async def shutdown(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def _check_model_availability(self):
        """Check which models are currently available"""
        for name, instance in self.models.items():
            try:
                if instance.config.provider == LLMProvider.OLLAMA:
                    available = await self._check_ollama_model(instance.config.model_id)
                elif instance.config.provider == LLMProvider.OPENAI:
                    available = self.openai_client is not None
                elif instance.config.provider == LLMProvider.ANTHROPIC:
                    available = self.anthropic_client is not None
                else:
                    available = True  # Assume other cloud models are available
                
                instance.available = available
                if available:
                    logger.info(f"Model {name} is available")
                else:
                    logger.warning(f"Model {name} is not available")
                    
            except Exception as e:
                logger.error(f"Error checking model {name}: {e}")
                instance.available = False
    
    async def _check_ollama_model(self, model_id: str) -> bool:
        """Check if an Ollama model is available"""
        try:
            ollama_host = "http://localhost:11434"
            async with self.session.get(f"{ollama_host}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model['name'] for model in data.get('models', [])]
                    return model_id in models
                return False
        except:
            return False

    def get_best_model(self, 
                      model_type: ModelType = ModelType.GENERAL,
                      exclude_unavailable: bool = True,
                      prefer_local: bool = True) -> Optional[ModelInstance]:
        """
        Get the best available model for a specific type with smart fallback.
        
        Selection criteria:
        1. Availability 
        2. Local preference (if prefer_local=True)
        3. Model type match or general compatibility
        4. Priority score
        5. Current load
        6. Performance history
        """
        candidates = []
        
        for instance in self.models.values():
            # Skip unavailable models if requested
            if exclude_unavailable and not instance.available:
                continue
                
            # Check if model supports the requested type
            if (instance.config.model_type == model_type or 
                instance.config.model_type == ModelType.GENERAL):
                
                # Check if model has capacity
                if instance.active_requests < instance.config.concurrent_limit:
                    candidates.append(instance)
        
        if not candidates:
            return None
        
        # Smart sorting with local preference
        def sort_key(instance):
            # Boost local models if prefer_local is True
            local_bonus = 100 if (prefer_local and instance.config.provider == LLMProvider.OLLAMA) else 0
            
            return (
                -instance.config.priority - local_bonus,  # Higher priority first (negative for descending)
                instance.active_requests,                  # Lower load first
                instance.error_count,                      # Fewer errors first
                -instance.avg_response_time                # Faster response first (negative for descending)
            )
        
        candidates.sort(key=sort_key)
        return candidates[0]

    async def generate_response(self,
                               prompt: str,
                               model_type: ModelType = ModelType.GENERAL,
                               max_retries: int = 2,
                               **kwargs) -> Dict[str, Any]:
        """
        Generate response using the optimal model with automatic fallback.
        
        Args:
            prompt: Input prompt
            model_type: Type of model to use
            max_retries: Number of fallback attempts
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response with metadata
        """
        last_error = None
        attempts = 0
        
        while attempts <= max_retries:
            # Get best available model (prefer local on first attempt)
            prefer_local = attempts == 0
            model_instance = self.get_best_model(model_type, prefer_local=prefer_local)
            
            if not model_instance:
                if attempts == 0:
                    # Try again without local preference
                    model_instance = self.get_best_model(model_type, prefer_local=False)
                
                if not model_instance:
                    raise Exception(f"No available models for type {model_type}")
            
            # Update model usage stats
            model_instance.active_requests += 1
            model_instance.last_used = time.time()
            start_time = time.time()
            
            try:
                # Generate response based on provider
                if model_instance.config.provider == LLMProvider.OLLAMA:
                    response_text = await self._generate_ollama_response(
                        model_instance.config.model_id, prompt, **kwargs
                    )
                elif model_instance.config.provider == LLMProvider.OPENAI:
                    response_text = await self._generate_openai_response(
                        model_instance.config.model_id, prompt, **kwargs
                    )
                elif model_instance.config.provider == LLMProvider.ANTHROPIC:
                    response_text = await self._generate_anthropic_response(
                        model_instance.config.model_id, prompt, **kwargs
                    )
                elif model_instance.config.provider == LLMProvider.PERPLEXITY:
                    response_text = await self._generate_perplexity_response(
                        model_instance.config.model_id, prompt, **kwargs
                    )
                else:
                    raise Exception(f"Unsupported provider: {model_instance.config.provider}")
                
                # Calculate response time and tokens
                response_time = time.time() - start_time
                estimated_tokens = LLMUtils.estimate_tokens(response_text, model_instance.config.model_id)
                cost = LLMUtils.calculate_cost(estimated_tokens, model_instance.config.model_id)
                
                # Update model statistics
                model_instance.total_requests += 1
                model_instance.total_tokens += estimated_tokens
                model_instance.cost_tracking += cost
                model_instance.avg_response_time = (
                    (model_instance.avg_response_time * (model_instance.total_requests - 1) + response_time) /
                    model_instance.total_requests
                )
                
                # Update global stats
                self.stats["total_cost"] += cost
                
                # Build response with metadata
                response = {
                    "response": response_text,
                    "model": model_instance.config.model_id,
                    "provider": model_instance.config.provider.value,
                    "model_type": model_type.value,
                    "tokens_used": estimated_tokens,
                    "cost_usd": cost,
                    "response_time": response_time,
                    "attempt": attempts + 1,
                    "fallback_used": attempts > 0
                }
                
                return response
                
            except Exception as e:
                model_instance.error_count += 1
                last_error = e
                logger.error(f"Error generating response with {model_instance.config.name} (attempt {attempts + 1}): {e}")
                
                # Mark model as temporarily unavailable if too many errors
                if model_instance.error_count > 3:
                    model_instance.available = False
                    logger.warning(f"Marking model {model_instance.config.name} as unavailable due to repeated errors")
                
                attempts += 1
                if attempts <= max_retries:
                    self.stats["fallback_uses"] += 1
                    logger.info(f"Falling back to next available model (attempt {attempts + 1})")
                
            finally:
                model_instance.active_requests -= 1
        
        # All attempts failed
        raise Exception(f"All model attempts failed. Last error: {last_error}")
    
    async def _generate_ollama_response(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate response using Ollama local model"""
        ollama_host = "http://localhost:11434"
        
        payload = {
            "model": model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2048)
            }
        }
        
        async with self.session.post(f"{ollama_host}/api/generate", json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("response", "")
            else:
                raise Exception(f"Ollama API error: {response.status}")
    
    async def _generate_openai_response(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API"""
        if not self.openai_client:
            raise Exception("OpenAI client not initialized")
        
        try:
            # Handle system prompt if provided
            messages = []
            if "system_prompt" in kwargs:
                messages.append({"role": "system", "content": kwargs["system_prompt"]})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.openai_client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                timeout=kwargs.get("timeout", 30)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _generate_anthropic_response(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic API"""
        if not self.anthropic_client:
            raise Exception("Anthropic client not initialized")
        
        try:
            # Anthropic uses a different message format
            system_prompt = kwargs.get("system_prompt", "")
            
            response = await self.anthropic_client.messages.create(
                model=model_id,
                max_tokens=kwargs.get("max_tokens", 2048),
                temperature=kwargs.get("temperature", 0.7),
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def _generate_perplexity_response(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate response using Perplexity API"""
        # Perplexity integration would go here
        # This is a placeholder for the actual implementation
        raise NotImplementedError("Perplexity integration not yet implemented")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get comprehensive model statistics"""
        model_stats = {}
        for name, instance in self.models.items():
            model_stats[name] = {
                "available": instance.available,
                "active_requests": instance.active_requests,
                "total_requests": instance.total_requests,
                "total_tokens": instance.total_tokens,
                "avg_response_time": instance.avg_response_time,
                "error_count": instance.error_count,
                "error_rate": instance.error_count / max(instance.total_requests, 1),
                "last_used": instance.last_used,
                "provider": instance.config.provider.value,
                "type": instance.config.model_type.value,
                "cost_tracking": instance.cost_tracking
            }
        
        return {
            "global_stats": self.stats,
            "model_stats": model_stats
        }

# Singleton instance
_model_manager = None

async def get_model_manager() -> ModelManager:
    """Get the global model manager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
        await _model_manager.initialize()
    return _model_manager 