"""GPT client service"""
from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.llm.core.gpt_client import GPTClient
from backend.infrastructure.llm.repositories.gpt_repository import GPTRepository

logger = logging.getLogger(__name__)

class GPTClientService:
    """GPT API integration service"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.gpt_client = GPTClient(api_key)
        self.gpt_repo = GPTRepository()
        self.logger = logger
    
    async def generate_response(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Generate response from GPT"""
        try:
            response = await self.gpt_client.generate_response(prompt, model)
            
            # Save request/response
            await self.gpt_repo.save_request({"prompt": prompt, "model": model})
            await self.gpt_repo.save_response({"response": response})
            
            return response
        except Exception as e:
            self.logger.error(f"GPT client service error: {e}")
            raise
