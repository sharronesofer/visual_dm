"""
LLM Infrastructure Utilities

Shared utilities for LLM operations across all systems including:
- Response validation and sanitization
- Token counting and cost calculation
- Performance monitoring helpers
- Error handling and retry logic
- Caching utilities
"""

import re
import time
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class LLMUtils:
    """Shared utilities for LLM infrastructure operations"""
    
    @staticmethod
    def sanitize_response(response: str) -> str:
        """
        Sanitize LLM response for safe usage.
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Sanitized response text
        """
        if not response:
            return ""
        
        # Remove potential harmful content
        sanitized = response.strip()
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove potential injection attempts
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Limit length to prevent abuse
        max_length = 10000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        
        return sanitized
    
    @staticmethod
    def estimate_tokens(text: str, model_type: str = "gpt") -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            model_type: Type of model for estimation
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Rough estimation: ~4 characters per token for most models
        if model_type.lower() in ["gpt", "openai"]:
            return len(text) // 4
        elif model_type.lower() in ["claude", "anthropic"]:
            return len(text) // 4
        else:
            # Default estimation
            return len(text) // 4
    
    @staticmethod
    def calculate_cost(tokens: int, model_name: str, operation: str = "generation") -> float:
        """
        Calculate cost for LLM operation.
        
        Args:
            tokens: Number of tokens
            model_name: Name of the model
            operation: Type of operation (generation, embedding, etc.)
            
        Returns:
            Estimated cost in USD
        """
        # Cost per 1K tokens (approximate rates)
        cost_rates = {
            "gpt-4": {"generation": 0.03, "input": 0.01},
            "gpt-3.5-turbo": {"generation": 0.002, "input": 0.001},
            "claude-3-sonnet": {"generation": 0.015, "input": 0.003},
            "claude-3-haiku": {"generation": 0.00125, "input": 0.00025},
            "ollama": {"generation": 0.0, "input": 0.0},  # Local models are free
        }
        
        model_key = model_name.lower()
        for key in cost_rates:
            if key in model_key:
                rate = cost_rates[key].get(operation, cost_rates[key].get("generation", 0.0))
                return (tokens / 1000) * rate
        
        return 0.0  # Unknown model, assume free
    
    @staticmethod
    def generate_cache_key(prompt: str, model: str, **kwargs) -> str:
        """
        Generate cache key for LLM request.
        
        Args:
            prompt: Input prompt
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            Cache key string
        """
        # Create deterministic key from inputs
        key_data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        
        # Sort keys for consistency
        key_string = str(sorted(key_data.items()))
        
        # Generate hash
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @staticmethod
    def validate_response_structure(response: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate LLM response structure.
        
        Args:
            response: Response dictionary
            required_fields: List of required field names
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(response, dict):
            return False
        
        for field in required_fields:
            if field not in response:
                logger.warning(f"Missing required field in LLM response: {field}")
                return False
        
        return True
    
    @staticmethod
    async def retry_with_backoff(
        func,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0
    ):
        """
        Retry function with exponential backoff.
        
        Args:
            func: Async function to retry
            max_retries: Maximum number of retries
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Backoff multiplier
            
        Returns:
            Function result or raises last exception
        """
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    break
                
                delay = min(base_delay * (backoff_factor ** attempt), max_delay)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
        
        raise last_exception
    
    @staticmethod
    def format_performance_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format performance metrics for monitoring.
        
        Args:
            metrics: Raw metrics dictionary
            
        Returns:
            Formatted metrics
        """
        formatted = {
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(metrics.get("response_time", 0) * 1000, 2),
            "token_count": metrics.get("tokens", 0),
            "cost_usd": round(metrics.get("cost", 0), 6),
            "model": metrics.get("model", "unknown"),
            "provider": metrics.get("provider", "unknown"),
            "success": metrics.get("success", False),
            "error": metrics.get("error"),
            "cache_hit": metrics.get("cache_hit", False)
        }
        
        return formatted
    
    @staticmethod
    def extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM response text.
        
        Args:
            response: LLM response text
            
        Returns:
            Parsed JSON dictionary or None
        """
        try:
            # Try direct JSON parsing first
            import json
            return json.loads(response)
        except:
            pass
        
        # Try to find JSON in text
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response)
        
        for match in matches:
            try:
                import json
                return json.loads(match)
            except:
                continue
        
        return None
    
    @staticmethod
    def truncate_prompt(prompt: str, max_tokens: int, model_type: str = "gpt") -> str:
        """
        Truncate prompt to fit within token limit.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum token limit
            model_type: Model type for token estimation
            
        Returns:
            Truncated prompt
        """
        estimated_tokens = LLMUtils.estimate_tokens(prompt, model_type)
        
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Calculate approximate character limit
        chars_per_token = 4
        max_chars = max_tokens * chars_per_token
        
        if len(prompt) <= max_chars:
            return prompt
        
        # Truncate with ellipsis
        truncated = prompt[:max_chars - 3] + "..."
        return truncated 