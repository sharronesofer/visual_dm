"""Prompt management service"""
from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.llm.repositories.prompt_repository import PromptRepository

logger = logging.getLogger(__name__)

class PromptService:
    """Dynamic prompt generation and management"""
    
    def __init__(self):
        self.prompt_repo = PromptRepository()
        self.logger = logger
    
    async def generate_prompt(self, template_id: str, variables: Dict[str, Any]) -> str:
        """Generate prompt from template"""
        template = await self.prompt_repo.get_prompt_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
        
        # Template processing logic
        return template.get("content", "").format(**variables)
    
    async def create_template(self, template_data: Dict[str, Any]) -> str:
        """Create new prompt template"""
        template_id = await self.prompt_repo.save_prompt_template(template_data)
        return template_id
