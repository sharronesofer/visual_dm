import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from backend.utils.gpt_client import GPTClient, GPTConfig, GPTResponse
from backend.utils.dialogue_generation_service import DialogueGenerationService

# Test data
TEST_PROMPT = "Hello, how are you?"
TEST_CONTEXT = ["You are a helpful assistant."]
TEST_CONFIG = {"model": "gpt-3.5-turbo", "temperature": 0.7, "max_tokens": 100}
MOCK_RESPONSE = {
    "text": "I'm doing well, thank you for asking!",
    "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    "error": None,
    "raw": {"choices": [{"message": {"content": "I'm doing well, thank you for asking!"}}]}
}

@pytest.fixture
def mock_gpt_client():
    """Create a mock GPT client for testing"""
    client = AsyncMock(spec=GPTClient)
    client.generate_completion = AsyncMock(return_value=MOCK_RESPONSE)
    return client

@pytest.fixture
def dialogue_service(mock_gpt_client):
    """Create a DialogueGenerationService with a mock client"""
    return DialogueGenerationService(mock_gpt_client, TEST_CONFIG)

@pytest.mark.asyncio
async def test_generate_dialogue_success(dialogue_service, mock_gpt_client):
    """Test successful dialogue generation with async/await pattern"""
    # Call the service
    response = await dialogue_service.generate_dialogue(TEST_PROMPT, TEST_CONTEXT)
    
    # Verify the client was called correctly
    mock_gpt_client.generate_completion.assert_called_once_with(
        TEST_PROMPT, 
        TEST_CONTEXT,
        TEST_CONFIG
    )
    
    # Verify the response was passed through
    assert response == MOCK_RESPONSE
    assert response["text"] == "I'm doing well, thank you for asking!"

@pytest.mark.asyncio
async def test_generate_dialogue_with_config_override(dialogue_service, mock_gpt_client):
    """Test dialogue generation with config overrides"""
    # Custom config to override defaults
    custom_config = {"temperature": 0.9, "max_tokens": 50}
    expected_config = {**TEST_CONFIG, **custom_config}
    
    # Call with custom config
    await dialogue_service.generate_dialogue(TEST_PROMPT, TEST_CONTEXT, custom_config)
    
    # Verify merged config was used
    mock_gpt_client.generate_completion.assert_called_once()
    call_args = mock_gpt_client.generate_completion.call_args[0]
    assert call_args[0] == TEST_PROMPT
    assert call_args[1] == TEST_CONTEXT
    assert call_args[2]["temperature"] == 0.9
    assert call_args[2]["max_tokens"] == 50
    assert call_args[2]["model"] == "gpt-3.5-turbo"  # From default config

@pytest.mark.asyncio
async def test_generate_dialogue_empty_context(dialogue_service, mock_gpt_client):
    """Test dialogue generation with empty context"""
    # Call with no context
    await dialogue_service.generate_dialogue(TEST_PROMPT)
    
    # Verify empty list was passed
    mock_gpt_client.generate_completion.assert_called_once()
    call_args = mock_gpt_client.generate_completion.call_args[0]
    assert call_args[1] == []

@pytest.mark.asyncio
async def test_generate_dialogue_api_error(dialogue_service, mock_gpt_client):
    """Test error handling when API returns an error"""
    # Mock API error
    error_response = {
        "text": "",
        "error": "API Error: 429 Too Many Requests",
        "raw": None,
        "usage": None
    }
    mock_gpt_client.generate_completion.return_value = error_response
    
    # Call should not raise exception
    response = await dialogue_service.generate_dialogue(TEST_PROMPT)
    
    # Verify error was propagated
    assert response["error"] == "API Error: 429 Too Many Requests"
    assert response["text"] == ""

@pytest.mark.asyncio
async def test_generate_dialogue_exception(dialogue_service, mock_gpt_client):
    """Test exception handling in generate_dialogue"""
    # Mock client to raise exception
    mock_gpt_client.generate_completion.side_effect = Exception("Network error")
    
    # Should handle exception and return error response
    response = await dialogue_service.generate_dialogue(TEST_PROMPT)
    
    # Verify error was captured
    assert response["error"] == "Network error"
    assert response["text"] == ""
    assert isinstance(response["raw"], Exception)

@pytest.mark.asyncio
async def test_multiple_concurrent_requests(dialogue_service, mock_gpt_client):
    """Test handling multiple concurrent requests"""
    # Different responses for different calls
    responses = [
        {"text": "Response 1", "error": None},
        {"text": "Response 2", "error": None},
        {"text": "Response 3", "error": None}
    ]
    
    mock_gpt_client.generate_completion.side_effect = lambda *args, **kwargs: asyncio.sleep(0.1).then(lambda: responses.pop(0))
    
    # Make concurrent requests
    tasks = [
        dialogue_service.generate_dialogue("Prompt 1"),
        dialogue_service.generate_dialogue("Prompt 2"),
        dialogue_service.generate_dialogue("Prompt 3")
    ]
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    # Verify all completed
    assert len(results) == 3
    assert mock_gpt_client.generate_completion.call_count == 3

# Run tests with: pytest -v backend/tests/test_dialogue_generation.py 