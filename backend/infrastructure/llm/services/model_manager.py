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
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "fallback_uses": 0,
            "error_rate": 0.0
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
                # Local Ollama models (primary)
                configs.extend([
                    ModelConfig(
                        name="llama2-13b-chat-local",
                        provider=provider,
                        model_id="llama2:13b-chat",
                        model_type=ModelType.GENERAL,
                        priority=10,
                        concurrent_limit=2,
                        timeout_seconds=provider_config.timeout
                    ),
                    ModelConfig(
                        name="mistral-7b-dialogue-local", 
                        provider=provider,
                        model_id="mistral:7b-instruct",
                        model_type=ModelType.DIALOGUE,
                        priority=9,
                        concurrent_limit=3,
                        timeout_seconds=provider_config.timeout
                    ),
                    ModelConfig(
                        name="codellama-13b-narrative-local",
                        provider=provider,
                        model_id="codellama:13b-instruct",
                        model_type=ModelType.NARRATIVE,
                        priority=8,
                        concurrent_limit=2,
                        timeout_seconds=provider_config.timeout
                    )
                ])
            
            elif provider == LLMProvider.OPENAI:
                # OpenAI cloud models
                configs.append(ModelConfig(
                    name="gpt-4-fallback",
                    provider=provider,
                    model_id="gpt-4",
                    model_type=ModelType.GENERAL,
                    priority=5,
                    cost_per_token=0.00003,
                    concurrent_limit=5,
                    timeout_seconds=provider_config.timeout
                ))
            
            elif provider == LLMProvider.ANTHROPIC:
                # Anthropic cloud models
                configs.append(ModelConfig(
                    name="claude-3-sonnet-fallback",
                    provider=provider,
                    model_id="claude-3-sonnet-20240229",
                    model_type=ModelType.GENERAL,
                    priority=4,
                    cost_per_token=0.000015,
                    concurrent_limit=5,
                    timeout_seconds=provider_config.timeout
                ))
            
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
        await self._check_model_availability()
    
    async def shutdown(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
    
    async def _check_model_availability(self):
        """Check which models are currently available"""
        for name, instance in self.models.items():
            try:
                if instance.config.provider == ModelProvider.LOCAL_OLLAMA:
                    available = await self._check_ollama_model(instance.config.model_id)
                else:
                    available = True  # Assume cloud models are available
                
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
                      exclude_unavailable: bool = True) -> Optional[ModelInstance]:
        """
        Get the best available model for a specific type.
        
        Selection criteria:
        1. Model type match or general compatibility
        2. Availability
        3. Current load (active_requests < concurrent_limit)
        4. Priority score
        5. Performance history
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
            
        # Sort by priority (higher is better), then by load (lower is better)
        candidates.sort(key=lambda x: (
            -x.config.priority,  # Higher priority first
            x.active_requests,   # Lower load first
            x.error_count,       # Fewer errors first
            -x.avg_response_time # Faster response first
        ))
        
        return candidates[0]
    
    async def generate_response(self,
                               prompt: str,
                               model_type: ModelType = ModelType.GENERAL,
                               **kwargs) -> Dict[str, Any]:
        """
        Generate response using the optimal model for the given type.
        
        Args:
            prompt: Input prompt
            model_type: Type of model to use
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response with metadata
        """
        # Get best available model
        model_instance = self.get_best_model(model_type)
        if not model_instance:
            raise Exception(f"No available models for type {model_type}")
        
        # Update model usage stats
        model_instance.active_requests += 1
        model_instance.last_used = time.time()
        
        try:
            # Use infrastructure middleware for request processing
            async def _execute_request(prompt, model_id, **kwargs):
                if model_instance.config.provider == LLMProvider.OLLAMA:
                    return await self._generate_ollama_response(model_id, prompt, **kwargs)
                elif model_instance.config.provider == LLMProvider.OPENAI:
                    return await self._generate_openai_response(model_id, prompt, **kwargs)
                elif model_instance.config.provider == LLMProvider.ANTHROPIC:
                    return await self._generate_anthropic_response(model_id, prompt, **kwargs)
                elif model_instance.config.provider == LLMProvider.PERPLEXITY:
                    return await self._generate_perplexity_response(model_id, prompt, **kwargs)
                else:
                    raise Exception(f"Unsupported provider: {model_instance.config.provider}")
            
            # Process through middleware
            response = await llm_middleware.process_request(
                request_func=lambda p, m, **kw: _execute_request(p, model_instance.config.model_id, **kw),
                prompt=prompt,
                model=model_instance.config.model_id,
                **kwargs
            )
            
            # Update model statistics
            model_instance.total_requests += 1
            if response.get("middleware", {}).get("response_time"):
                response_time = response["middleware"]["response_time"]
                model_instance.avg_response_time = (
                    (model_instance.avg_response_time * (model_instance.total_requests - 1) + response_time) /
                    model_instance.total_requests
                )
            
            # Add model metadata
            response.update({
                "model": model_instance.config.model_id,
                "provider": model_instance.config.provider.value,
                "model_type": model_type.value
            })
            
            return response
            
        except Exception as e:
            model_instance.error_count += 1
            logger.error(f"Error generating response with {model_instance.config.name}: {e}")
            raise e
            
        finally:
            model_instance.active_requests -= 1
    
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
        # Implementation would use OpenAI client
        # This is a placeholder for the actual implementation
        raise NotImplementedError("OpenAI integration not yet implemented")
    
    async def _generate_anthropic_response(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate response using Anthropic API"""
        # Implementation would use Anthropic client
        # This is a placeholder for the actual implementation
        raise NotImplementedError("Anthropic integration not yet implemented")
    
    async def _generate_perplexity_response(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate response using Perplexity API"""
        # Implementation would use Perplexity client
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
                "avg_response_time": instance.avg_response_time,
                "error_count": instance.error_count,
                "error_rate": instance.error_count / max(instance.total_requests, 1),
                "last_used": instance.last_used,
                "provider": instance.config.provider.value,
                "type": instance.config.model_type.value
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