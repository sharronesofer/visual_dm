"""
Quest System RAG Adapter
Integrates the quest system with the centralized RAG service for enhanced quest generation and management
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.core.rag_client import create_rag_client, RAGClient, QuestRAGAdapter

class QuestRAGService:
    """
    Quest system RAG integration service
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rag_client: Optional[RAGClient] = None
        
    async def initialize(self):
        """Initialize the quest RAG service"""
        try:
            self.rag_client = await create_rag_client('quest', QuestRAGAdapter())
            self.logger.info("Quest RAG service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize quest RAG service: {e}")
            return False
    
    async def enhance_quest_description(
        self, 
        base_description: str,
        quest_type: str,
        context: Dict[str, Any]
    ) -> str:
        """Enhance a quest description with RAG knowledge"""
        if not self.rag_client:
            return base_description
        
        try:
            quest_context = f"Quest type: {quest_type}. {base_description}"
            rag_response = await self.rag_client.enhance_response(
                base_response=base_description,
                context=quest_context,
                context_data=context
            )
            
            return rag_response.content if rag_response.context_used else base_description
            
        except Exception as e:
            self.logger.error(f"Failed to enhance quest description: {e}")
            return base_description
    
    async def generate_quest_suggestions(
        self, 
        location_id: str,
        difficulty: str,
        quest_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate quest suggestions based on location and context"""
        if not self.rag_client:
            return []
        
        try:
            query = f"Quest ideas for location {location_id} with {difficulty} difficulty"
            if quest_type:
                query += f" of type {quest_type}"
            
            context = {
                'location_id': location_id,
                'difficulty': difficulty,
                'quest_type': quest_type
            }
            
            knowledge_entries = await self.rag_client.query(
                query=query,
                context=context,
                categories=['quests', 'locations', 'lore']
            )
            
            suggestions = []
            for entry in knowledge_entries:
                suggestions.append({
                    'content': entry.content,
                    'confidence': entry.confidence,
                    'source': entry.metadata
                })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to generate quest suggestions: {e}")
            return []
    
    async def add_quest_knowledge(
        self, 
        quest_data: Dict[str, Any]
    ) -> bool:
        """Add completed quest data to knowledge base"""
        if not self.rag_client:
            return False
        
        try:
            content = f"Quest: {quest_data.get('title', 'Untitled')}\n"
            content += f"Description: {quest_data.get('description', '')}\n"
            content += f"Type: {quest_data.get('type', 'unknown')}\n"
            content += f"Outcome: {quest_data.get('outcome', 'completed')}"
            
            return await self.rag_client.add_knowledge(
                content=content,
                category='quests',
                metadata={
                    'quest_id': quest_data.get('id'),
                    'quest_type': quest_data.get('type'),
                    'location_id': quest_data.get('location_id'),
                    'difficulty': quest_data.get('difficulty')
                },
                tags=[
                    'quest',
                    quest_data.get('type', 'unknown'),
                    quest_data.get('difficulty', 'unknown')
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add quest knowledge: {e}")
            return False

# Global instance
_quest_rag_service = None

async def get_quest_rag_service() -> QuestRAGService:
    """Get or create the global quest RAG service"""
    global _quest_rag_service
    if _quest_rag_service is None:
        _quest_rag_service = QuestRAGService()
        await _quest_rag_service.initialize()
    return _quest_rag_service 