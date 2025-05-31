"""GPT API client implementation"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import openai

from backend.infrastructure.models import BaseModel

logger = logging.getLogger(__name__)

class GPTClient:
    """OpenAI GPT API client"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        if api_key:
            openai.api_key = api_key
    
    async def generate_response(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Generate response from GPT"""
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT API error: {e}")
            return "Error generating response"
