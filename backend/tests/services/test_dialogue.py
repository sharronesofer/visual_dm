import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import time
import json
from typing import Dict, Any, List

from backend.app.services.dialogue.gpt_client import GPTClient, GPTConfig, GPTResponse, GPTUsageStats
from backend.app.services.dialogue.dialogue_generation_service import DialogueGenerationService
from backend.app.services.dialogue.response_cache_manager import ResponseCacheManager, CacheEntry
from backend.app.services.dialogue.conversation_context_manager import (
    ConversationContextManager, 
    ContextManagerConfig,
    InMemoryContextStorage
)
from backend.app.services.dialogue.types import ConversationTurn, DialogueRole

# Test data
TEST_PROMPT = "Hello, how are you?"
TEST_SYSTEM_MESSAGE = "You are a helpful assistant."
TEST_CONVERSATION = [
    {"role": "system", "content": TEST_SYSTEM_MESSAGE, "timestamp": int(time.time() * 1000)},
    {"role": "user", "content": "Hi, what can you do?", "timestamp": int(time.time() * 1000)},
    {"role": "assistant", "content": "I can help answer questions.", "timestamp": int(time.time() * 1000)}
]
TEST_CONFIG = {"model": "gpt-3.5-turbo", "temperature": 0.7, "maxTokens": 100}
MOCK_API_RESPONSE = {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": int(time.time()),
    "model": "gpt-3.5-turbo",
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "I'm doing well, thank you for asking!"
            },
            "index": 0,
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 10,
        "total_tokens": 20
    }
}
MOCK_GPT_RESPONSE = {
    "text": "I'm doing well, thank you for asking!",
    "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    "error": None,
    "raw": MOCK_API_RESPONSE
}

@pytest.fixture
def mock_aiohttp_session():
    """Create a mock aiohttp ClientSession."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=MOCK_API_RESPONSE)
    mock_response.__aenter__.return_value = mock_response
    mock_session.post.return_value = mock_response
    return mock_session

@pytest.fixture
def gpt_client(mock_aiohttp_session):
    """Create a GPTClient with mocked session."""
    with patch('aiohttp.ClientSession', return_value=mock_aiohttp_session):
        client = GPTClient({
            "apiKey": "fake-api-key",
            "rateLimit": 60,
            "maxRetries": 3
        })
        yield client

@pytest.fixture
def dialogue_service(gpt_client):
    """Create a DialogueGenerationService with the GPT client."""
    return DialogueGenerationService(gpt_client, TEST_CONFIG)

@pytest.fixture
def response_cache():
    """Create a ResponseCacheManager for testing."""
    return ResponseCacheManager({
        "maxSize": 100,
        "expiryMs": 3600000  # 1 hour
    })

@pytest.fixture
def context_manager():
    """Create a ConversationContextManager for testing."""
    return ConversationContextManager({
        "maxTokens": 2000,
        "maxTurns": 10
    })

class TestGPTClient:
    @pytest.mark.asyncio
    async def test_generate_completion(self, gpt_client, mock_aiohttp_session):
        """Test basic API call to generate a completion."""
        messages = [{"role": "user", "content": TEST_PROMPT}]
        response = await gpt_client.generate_completion(messages, TEST_CONFIG)
        
        # Verify API was called correctly
        mock_aiohttp_session.post.assert_called_once()
        assert response["text"] == "I'm doing well, thank you for asking!"
        assert response["usage"]["total_tokens"] == 20
        assert response["error"] is None
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, gpt_client):
        """Test that rate limiting works."""
        # Override rate limit to 2 requests per second
        gpt_client.options["rateLimit"] = 2
        
        # Make 3 requests quickly
        start_time = time.time()
        messages = [{"role": "user", "content": TEST_PROMPT}]
        tasks = [
            gpt_client.generate_completion(messages, TEST_CONFIG),
            gpt_client.generate_completion(messages, TEST_CONFIG),
            gpt_client.generate_completion(messages, TEST_CONFIG)
        ]
        
        # Wait for all to complete
        await asyncio.gather(*tasks)
        elapsed_time = time.time() - start_time
        
        # Should take at least 1 second (first 2 immediately, 3rd after delay)
        assert elapsed_time >= 1.0
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, gpt_client, mock_aiohttp_session):
        """Test handling of API errors."""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.__aenter__.return_value = mock_response
        mock_response.json = AsyncMock(return_value={"error": {"message": "Rate limit exceeded"}})
        mock_aiohttp_session.post.return_value = mock_response
        
        # Make request
        messages = [{"role": "user", "content": TEST_PROMPT}]
        response = await gpt_client.generate_completion(messages, TEST_CONFIG)
        
        # Should contain error
        assert response["error"] is not None
        assert "Rate limit" in response["error"]
        assert response["text"] == ""

class TestDialogueGenerationService:
    @pytest.mark.asyncio
    async def test_generate_dialogue(self, dialogue_service, gpt_client):
        """Test basic dialogue generation."""
        with patch.object(gpt_client, 'generate_completion', return_value=MOCK_GPT_RESPONSE):
            response = await dialogue_service.generate_dialogue(TEST_PROMPT, [TEST_SYSTEM_MESSAGE])
            
            # Verify response
            assert response["text"] == "I'm doing well, thank you for asking!"
            assert response["metadata"]["tokensUsed"] == 20
            assert response["metadata"]["model"] == "gpt-3.5-turbo"
    
    @pytest.mark.asyncio
    async def test_generate_dialogue_with_conversation(self, dialogue_service, gpt_client):
        """Test dialogue generation with conversation history."""
        with patch.object(gpt_client, 'generate_completion', return_value=MOCK_GPT_RESPONSE):
            response = await dialogue_service.generate_dialogue_with_history(
                TEST_CONVERSATION, TEST_CONFIG
            )
            
            # Verify dialogue was generated
            assert response["text"] == "I'm doing well, thank you for asking!"
            assert response["metadata"]["tokensUsed"] == 20
    
    @pytest.mark.asyncio
    async def test_error_handling(self, dialogue_service, gpt_client):
        """Test error handling in service."""
        error_response = {
            "text": "",
            "error": "API Error: Rate limit exceeded",
            "usage": None,
            "raw": None
        }
        with patch.object(gpt_client, 'generate_completion', return_value=error_response):
            response = await dialogue_service.generate_dialogue(TEST_PROMPT)
            
            # Should include error info
            assert response["success"] is False
            assert "Rate limit exceeded" in response["error"]
            assert response["text"] == ""

class TestResponseCacheManager:
    def test_add_and_get_cache_entry(self, response_cache):
        """Test adding and retrieving cache entries."""
        key = "test-key"
        entry = CacheEntry(
            key=key,
            response="Test response",
            metadata={
                "tokensUsed": 10,
                "responseTimeMs": 100,
                "model": "gpt-3.5-turbo",
                "additional": {}
            },
            timestamp=int(time.time() * 1000)
        )
        
        # Add to cache
        response_cache.add(key, entry)
        
        # Retrieve from cache
        cached = response_cache.get(key)
        assert cached is not None
        assert cached["response"] == "Test response"
        assert cached["metadata"]["tokensUsed"] == 10
    
    def test_cache_miss(self, response_cache):
        """Test cache miss behavior."""
        result = response_cache.get("non-existent-key")
        assert result is None
    
    def test_cache_expiry(self, response_cache):
        """Test that cache entries expire."""
        # Override expiry to 100ms for testing
        response_cache.config["expiryMs"] = 100
        
        key = "expiring-key"
        entry = CacheEntry(
            key=key,
            response="Expires quickly",
            metadata={
                "tokensUsed": 10,
                "responseTimeMs": 100,
                "model": "gpt-3.5-turbo",
                "additional": {}
            },
            timestamp=int(time.time() * 1000)
        )
        
        # Add to cache
        response_cache.add(key, entry)
        
        # Should be in cache initially
        assert response_cache.get(key) is not None
        
        # Wait for expiry
        time.sleep(0.2)
        
        # Should be gone now
        assert response_cache.get(key) is None
    
    def test_get_analytics(self, response_cache):
        """Test analytics tracking."""
        # Add some entries and do some lookups
        response_cache.add("key1", CacheEntry(
            key="key1",
            response="Response 1",
            metadata={"tokensUsed": 10, "responseTimeMs": 100, "model": "gpt-3.5-turbo", "additional": {}},
            timestamp=int(time.time() * 1000)
        ))
        
        # Some hits
        response_cache.get("key1")
        response_cache.get("key1")
        
        # Some misses
        response_cache.get("missing1")
        
        # Check analytics
        analytics = response_cache.get_analytics()
        assert analytics["hits"] == 2
        assert analytics["misses"] == 1
        assert analytics["mostFrequent"]["key1"] == 2

class TestConversationContextManager:
    @pytest.mark.asyncio
    async def test_add_and_get_turns(self, context_manager):
        """Test adding and retrieving conversation turns."""
        conversation_id = "test-conversation"
        
        # Add some turns
        await context_manager.add_turn(conversation_id, {
            "role": "user", 
            "content": "Hello",
            "timestamp": int(time.time() * 1000)
        })
        await context_manager.add_turn(conversation_id, {
            "role": "assistant", 
            "content": "Hi there!",
            "timestamp": int(time.time() * 1000)
        })
        
        # Get all turns
        turns = await context_manager.get_turns(conversation_id)
        assert len(turns) == 2
        assert turns[0]["role"] == "user"
        assert turns[1]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_get_formatted_context(self, context_manager):
        """Test getting formatted context for API."""
        conversation_id = "test-context"
        
        # Add system message and turns
        await context_manager.add_turn(conversation_id, {
            "role": "system",
            "content": TEST_SYSTEM_MESSAGE,
            "timestamp": int(time.time() * 1000)
        })
        await context_manager.add_turn(conversation_id, {
            "role": "user",
            "content": "Hello",
            "timestamp": int(time.time() * 1000)
        })
        
        # Get formatted context
        context = await context_manager.get_context(conversation_id)
        assert len(context) == 2
        assert context[0]["role"] == "system"
        assert context[0]["content"] == TEST_SYSTEM_MESSAGE
    
    @pytest.mark.asyncio
    async def test_turn_limit_enforcement(self, context_manager):
        """Test that max turns limit is enforced."""
        # Set max turns to 3
        context_manager.config["maxTurns"] = 3
        conversation_id = "limited-conversation"
        
        # Add 4 turns
        for i in range(4):
            await context_manager.add_turn(conversation_id, {
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Turn {i}",
                "timestamp": int(time.time() * 1000)
            })
        
        # Should only keep most recent 3
        turns = await context_manager.get_turns(conversation_id)
        assert len(turns) == 3
        assert turns[0]["content"] == "Turn 1"  # Should have pruned Turn 0
    
    @pytest.mark.asyncio
    async def test_clear_conversation(self, context_manager):
        """Test clearing a conversation."""
        conversation_id = "to-be-cleared"
        
        # Add some turns
        await context_manager.add_turn(conversation_id, {
            "role": "user", 
            "content": "This will be cleared",
            "timestamp": int(time.time() * 1000)
        })
        
        # Clear the conversation
        await context_manager.clear_conversation(conversation_id)
        
        # Should be empty
        turns = await context_manager.get_turns(conversation_id)
        assert len(turns) == 0 