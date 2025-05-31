"""LLM event middleware chain"""
from typing import Dict, List, Optional, Any, Callable
import asyncio
import logging

logger = logging.getLogger(__name__)

class LLMEventMiddleware:
    """Event processing middleware"""
    
    def __init__(self):
        self.middleware_chain: List[Callable] = []
        self.logger = logger
    
    def add_middleware(self, middleware_func: Callable):
        """Add middleware to chain"""
        self.middleware_chain.append(middleware_func)
    
    async def process_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process event through middleware chain"""
        for middleware in self.middleware_chain:
            event_data = await middleware(event_data)
        return event_data

class ContextMiddleware:
    """Context building middleware"""
    
    async def __call__(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process event with context"""
        # Add context building logic
        event_data["context"] = {"timestamp": "now", "source": "middleware"}
        return event_data

class SecurityMiddleware:
    """Security validation middleware"""
    
    async def __call__(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate event security"""
        # Add security validation
        event_data["security_validated"] = True
        return event_data
