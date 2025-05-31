"""Test core LLM functionality"""
import pytest
import asyncio
from backend.infrastructure.llm.core.llm_core import LLMCore
from backend.infrastructure.llm.core.gpt_client import GPTClient

class TestLLMCore:
    """Test LLM core functionality"""
    
    @pytest.fixture
    async def llm_core(self):
        core = LLMCore()
        await core.initialize()
        return core
    
    @pytest.mark.asyncio
    async def test_initialization(self, llm_core):
        """Test LLM core initialization"""
        assert llm_core.initialized is True
    
    @pytest.mark.asyncio
    async def test_process_request(self, llm_core):
        """Test request processing"""
        request = {"prompt": "test prompt"}
        response = await llm_core.process_request(request)
        
        assert "id" in response
        assert "response" in response
        assert "timestamp" in response

class TestGPTClient:
    """Test GPT client functionality"""
    
    def test_client_initialization(self):
        """Test GPT client initialization"""
        client = GPTClient()
        assert client is not None
    
    @pytest.mark.asyncio
    async def test_generate_response_without_api_key(self):
        """Test response generation without API key"""
        client = GPTClient()
        response = await client.generate_response("test prompt")
        # Should handle gracefully without API key
        assert isinstance(response, str)
