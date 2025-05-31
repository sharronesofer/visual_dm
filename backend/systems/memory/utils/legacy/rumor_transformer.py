from .gpt_client import GPTClient, GPTRequest
from .prompt_manager import RumorPromptManager
from typing import Dict, Any
import logging

class RumorTransformer:
    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client

    async def transform_rumor(self, event: str, rumor: str, traits: str, distortion_level: float) -> str:
        prompt = RumorPromptManager.build_prompt(event, rumor, traits, distortion_level)
        req = GPTRequest(prompt=prompt)
        try:
            resp = await self.gpt_client.complete(req)
            return resp.text.strip()
        except Exception as e:
            logging.error(f"Rumor transformation failed: {e}")
            # Fallback: simple distortion
            return f"[Distorted] {rumor}" 
