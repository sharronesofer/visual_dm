"""
NPC System RAG Adapter
Integrates the NPC system with the centralized RAG service for enhanced NPC generation and behavior
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.core.rag_client import create_rag_client, RAGClient, NPCRAGAdapter

class NPCRAGService:
    """
    NPC system RAG integration service
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rag_client: Optional[RAGClient] = None
        
    async def initialize(self):
        """Initialize the NPC RAG service"""
        try:
            self.rag_client = await create_rag_client('npc', NPCRAGAdapter())
            self.logger.info("NPC RAG service initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize NPC RAG service: {e}")
            return False
    
    async def enhance_npc_personality(
        self, 
        base_personality: Dict[str, Any],
        npc_type: str,
        location_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance NPC personality with knowledge-based traits"""
        if not self.rag_client:
            return base_personality
        
        try:
            context_query = f"NPC personality traits for {npc_type} in {location_context.get('region', 'unknown region')}"
            
            knowledge_entries = await self.rag_client.query(
                query=context_query,
                context={
                    'npc_type': npc_type,
                    **location_context
                },
                categories=['npcs', 'characters', 'locations']
            )
            
            enhanced_personality = dict(base_personality)
            
            # Extract personality insights from knowledge
            for entry in knowledge_entries:
                if 'personality' in entry.content.lower():
                    # Add knowledge-based personality modifications
                    enhanced_personality['knowledge_influenced_traits'] = enhanced_personality.get('knowledge_influenced_traits', [])
                    enhanced_personality['knowledge_influenced_traits'].append({
                        'trait': entry.content[:100],  # First 100 chars as trait summary
                        'confidence': entry.confidence,
                        'source': entry.category
                    })
            
            return enhanced_personality
            
        except Exception as e:
            self.logger.error(f"Failed to enhance NPC personality: {e}")
            return base_personality
    
    async def generate_npc_backstory(
        self, 
        npc_data: Dict[str, Any],
        location_id: str
    ) -> str:
        """Generate knowledge-enhanced backstory for an NPC"""
        if not self.rag_client:
            return "A mysterious individual with an unknown past."
        
        try:
            profession = npc_data.get('profession', 'unknown')
            name = npc_data.get('name', 'unnamed')
            
            context_query = f"Backstory elements for {profession} named {name} in location {location_id}"
            
            knowledge_entries = await self.rag_client.query(
                query=context_query,
                context={
                    'npc_id': npc_data.get('id'),
                    'profession': profession,
                    'location_id': location_id
                },
                categories=['npcs', 'locations', 'lore', 'history']
            )
            
            if knowledge_entries:
                # Generate backstory incorporating relevant knowledge
                backstory_elements = []
                for entry in knowledge_entries[:3]:  # Use top 3 most relevant
                    backstory_elements.append(entry.content)
                
                # Simple backstory template (could be enhanced with LLM)
                backstory = f"{name} is a {profession} who "
                backstory += " and ".join(backstory_elements[:2])
                return backstory
            else:
                return f"{name} is a {profession} with a mysterious past."
                
        except Exception as e:
            self.logger.error(f"Failed to generate NPC backstory: {e}")
            return "A mysterious individual with an unknown past."
    
    async def get_npc_dialogue_knowledge(
        self, 
        npc_id: str,
        topic: str
    ) -> List[Dict[str, Any]]:
        """Get knowledge for NPC dialogue on a specific topic"""
        if not self.rag_client:
            return []
        
        try:
            # Query across multiple systems for comprehensive knowledge
            knowledge_entries = await self.rag_client.cross_system_query(
                query=f"NPC {npc_id} knowledge about {topic}",
                systems=['npc', 'dialogue', 'lore', 'faction', 'quest'],
                context={'npc_id': npc_id, 'topic': topic}
            )
            
            dialogue_knowledge = []
            for entry in knowledge_entries:
                dialogue_knowledge.append({
                    'content': entry.content,
                    'category': entry.category,
                    'system': entry.system,
                    'confidence': entry.confidence,
                    'tags': entry.tags
                })
            
            return dialogue_knowledge
            
        except Exception as e:
            self.logger.error(f"Failed to get NPC dialogue knowledge: {e}")
            return []
    
    async def learn_npc_behavior(
        self, 
        npc_id: str,
        behavior_data: Dict[str, Any]
    ) -> bool:
        """Learn from NPC behavior and add to knowledge base"""
        if not self.rag_client:
            return False
        
        try:
            behavior_content = f"NPC {npc_id} behavior: "
            behavior_content += f"Action: {behavior_data.get('action', 'unknown')}, "
            behavior_content += f"Context: {behavior_data.get('context', 'none')}, "
            behavior_content += f"Result: {behavior_data.get('result', 'unknown')}"
            
            return await self.rag_client.add_knowledge(
                content=behavior_content,
                category='npcs',
                metadata={
                    'npc_id': npc_id,
                    'behavior_type': behavior_data.get('action'),
                    'location_id': behavior_data.get('location_id'),
                    'timestamp': datetime.now().isoformat()
                },
                tags=[
                    'behavior',
                    npc_id,
                    behavior_data.get('action', 'unknown')
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to learn NPC behavior: {e}")
            return False
    
    async def add_npc_profile(
        self, 
        npc_data: Dict[str, Any]
    ) -> bool:
        """Add NPC profile to knowledge base"""
        if not self.rag_client:
            return False
        
        try:
            profile_content = f"NPC Profile: {npc_data.get('name', 'Unnamed')}\n"
            profile_content += f"Profession: {npc_data.get('profession', 'Unknown')}\n"
            profile_content += f"Location: {npc_data.get('location_id', 'Unknown')}\n"
            profile_content += f"Personality: {npc_data.get('personality', {})}\n"
            
            if 'backstory' in npc_data:
                profile_content += f"Backstory: {npc_data['backstory']}\n"
            
            return await self.rag_client.add_knowledge(
                content=profile_content,
                category='npcs',
                metadata={
                    'npc_id': npc_data.get('id'),
                    'profession': npc_data.get('profession'),
                    'location_id': npc_data.get('location_id'),
                    'created_at': datetime.now().isoformat()
                },
                tags=[
                    'npc_profile',
                    npc_data.get('profession', 'unknown'),
                    npc_data.get('id', 'unknown')
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to add NPC profile: {e}")
            return False

# Global instance
_npc_rag_service = None

async def get_npc_rag_service() -> NPCRAGService:
    """Get or create the global NPC RAG service"""
    global _npc_rag_service
    if _npc_rag_service is None:
        _npc_rag_service = NPCRAGService()
        await _npc_rag_service.initialize()
    return _npc_rag_service 