"""Test service implementations"""
import pytest
import asyncio
from backend.infrastructure.llm.services.llm_service import LLMService
from backend.infrastructure.llm.services.conversation_service import ConversationService

class TestLLMService:
    """Test main LLM service"""
    
    @pytest.fixture
    def llm_service(self):
        return LLMService()
    
    @pytest.mark.asyncio
    async def test_process_llm_request(self, llm_service):
        """Test LLM request processing"""
        request_data = {"prompt": "test prompt"}
        response = await llm_service.process_llm_request(request_data)
        
        assert isinstance(response, dict)
        assert "id" in response

class TestConversationService:
    """Test conversation service"""
    
    @pytest.fixture
    def conversation_service(self):
        return ConversationService()
    
    @pytest.mark.asyncio
    async def test_start_conversation(self, conversation_service):
        """Test starting conversation"""
        initial_data = {"user_id": "test_user"}
        conversation_id = await conversation_service.start_conversation(initial_data)
        assert isinstance(conversation_id, str)
        assert len(conversation_id) > 0
