"""Conversation management service"""
from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.llm.repositories.conversation_repository import ConversationRepository

logger = logging.getLogger(__name__)

class ConversationService:
    """Conversation lifecycle management"""
    
    def __init__(self):
        self.conversation_repo = ConversationRepository()
        self.logger = logger
    
    async def start_conversation(self, initial_data: Dict[str, Any]) -> str:
        """Start new conversation"""
        conversation_id = await self.conversation_repo.create_conversation(initial_data)
        self.logger.info(f"Started conversation: {conversation_id}")
        return conversation_id
    
    async def add_message(self, conversation_id: str, message: str, role: str = "user") -> str:
        """Add message to conversation"""
        message_data = {"message": message, "role": role}
        message_id = await self.conversation_repo.add_message(conversation_id, message_data)
        return message_id
