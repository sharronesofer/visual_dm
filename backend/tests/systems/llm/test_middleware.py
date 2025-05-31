"""Test middleware implementations"""
import pytest
import asyncio
from backend.infrastructure.llm.middleware.event_middleware import LLMEventMiddleware, ContextMiddleware

class TestLLMEventMiddleware:
    """Test event middleware"""
    
    @pytest.fixture
    def middleware(self):
        return LLMEventMiddleware()
    
    @pytest.mark.asyncio
    async def test_process_event_no_middleware(self, middleware):
        """Test event processing without middleware"""
        event_data = {"type": "test_event"}
        result = await middleware.process_event(event_data)
        assert result == event_data
    
    @pytest.mark.asyncio
    async def test_process_event_with_middleware(self, middleware):
        """Test event processing with middleware"""
        context_middleware = ContextMiddleware()
        middleware.add_middleware(context_middleware)
        
        event_data = {"type": "test_event"}
        result = await middleware.process_event(event_data)
        
        assert "context" in result
        assert result["context"]["source"] == "middleware"
