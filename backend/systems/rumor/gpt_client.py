"""
Deprecated GPT client - redirects to the centralized implementation.

This module provides backward compatibility for code that still imports the
GPT client from the rumor system. All functionality is redirected to the 
centralized implementation in backend.core.ai.gpt_client.

This module will be removed in a future version.
"""

import warnings
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.core.ai.gpt_client import (
    GPTClient as CoreGPTClient,
    GPTRequest as CoreGPTRequest,
    GPTResponse as CoreGPTResponse,
    GPTMessage,
    MessageRole,
    GPTModel
)

# Configure deprecation warning
warnings.warn(
    "The backend.systems.rumor.gpt_client module is deprecated. "
    "Use backend.core.ai.gpt_client instead.",
    DeprecationWarning,
    stacklevel=2
)

# Export everything from the centralized module for compatibility
__all__ = [
    'GPTClient',
    'GPTRequest',
    'GPTResponse'
]

class GPTRequest(BaseModel):
    """
    Deprecated GPTRequest - maps to centralized implementation.
    
    This maintains the original interface of the rumor system's GPT client
    but converts to the format required by the centralized implementation.
    """
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    model: str = "gpt-4.1-nano"
    
    def to_core_request(self) -> CoreGPTRequest:
        """Convert to the centralized GPTRequest format."""
        return CoreGPTRequest.simple(
            prompt=self.prompt,
            model=self.model,
            system_prompt=None
        )

class GPTResponse(BaseModel):
    """
    Deprecated GPTResponse - maps to centralized implementation.
    
    This maintains the original interface of the rumor system's GPT client
    but receives data from the centralized implementation's response format.
    """
    text: str
    usage: Optional[Dict[str, Any]] = None
    raw: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_core_response(cls, response: CoreGPTResponse) -> 'GPTResponse':
        """Create a compatible response from the centralized format."""
        return cls(
            text=response.text,
            usage=response.usage,
            raw=response.raw
        )

class GPTClient:
    """
    Deprecated GPTClient - redirects to centralized implementation.
    
    This maintains the original interface of the rumor system's GPT client
    but delegates all functionality to the centralized implementation.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize by creating a centralized client."""
        self.core_client = CoreGPTClient(api_key=api_key, base_url=base_url)
        warnings.warn(
            "Using deprecated GPTClient from rumor system. "
            "Update imports to use backend.core.ai.gpt_client",
            DeprecationWarning,
            stacklevel=2
        )
    
    async def complete(self, req: GPTRequest) -> GPTResponse:
        """
        Complete a prompt using the centralized implementation.
        
        Args:
            req: The GPTRequest in the old format
            
        Returns:
            GPTResponse in the old format but processed by the centralized client
        """
        core_req = req.to_core_request()
        core_resp = await self.core_client.complete(core_req)
        return GPTResponse.from_core_response(core_resp) 