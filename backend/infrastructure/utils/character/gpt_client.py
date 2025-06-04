import os
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel

class GPTRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    model: str = "gpt-4.1-nano"

class GPTResponse(BaseModel):
    text: str
    usage: Optional[Dict[str, Any]] = None
    raw: Optional[Dict[str, Any]] = None

class GPTClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or "https://api.openai.com/v1/chat/completions"

    async def complete(self, req: GPTRequest) -> GPTResponse:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": req.model,
            "messages": [{"role": "user", "content": req.prompt}],
            "max_tokens": req.max_tokens,
            "temperature": req.temperature
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.base_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return GPTResponse(text=text, usage=data.get("usage"), raw=data) 
