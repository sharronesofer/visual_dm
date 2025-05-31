"""Test repository implementations"""
import pytest
import asyncio
from backend.infrastructure.llm.repositories.gpt_repository import GPTRepository
from backend.infrastructure.llm.repositories.conversation_repository import ConversationRepository

class TestGPTRepository:
    """Test GPT repository"""
    
    @pytest.fixture
    def gpt_repo(self):
        return GPTRepository()
    
    @pytest.mark.asyncio
    async def test_save_request(self, gpt_repo):
        """Test saving GPT request"""
        request_data = {"prompt": "test", "model": "gpt-3.5-turbo"}
        request_id = await gpt_repo.save_request(request_data)
        assert isinstance(request_id, str)
        assert len(request_id) > 0
    
    @pytest.mark.asyncio
    async def test_get_usage_stats(self, gpt_repo):
        """Test usage statistics"""
        stats = await gpt_repo.get_usage_stats()
        assert "total_requests" in stats
        assert "total_tokens" in stats

class TestConversationRepository:
    """Test conversation repository"""
    
    @pytest.fixture
    def conversation_repo(self):
        return ConversationRepository()
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, conversation_repo):
        """Test conversation creation"""
        conversation_data = {"user_id": "test_user"}
        conversation_id = await conversation_repo.create_conversation(conversation_data)
        assert isinstance(conversation_id, str)
        assert len(conversation_id) > 0
