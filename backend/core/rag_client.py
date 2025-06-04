"""
RAG Client Library
Provides standardized interface for systems to interact with the centralized RAG service
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod

from .rag_service import CrossSystemRAGService, KnowledgeEntry, RAGResponse, get_rag_service

class SystemRAGAdapter(ABC):
    """Abstract base class for system-specific RAG adapters"""
    
    def __init__(self, system_name: str):
        self.system_name = system_name
        self.logger = logging.getLogger(f"{__name__}.{system_name}")
    
    @abstractmethod
    async def preprocess_query(self, query: str, context: Dict[str, Any]) -> str:
        """Preprocess query for system-specific needs"""
        pass
    
    @abstractmethod
    async def postprocess_response(self, response: RAGResponse, context: Dict[str, Any]) -> RAGResponse:
        """Postprocess RAG response for system-specific formatting"""
        pass
    
    @abstractmethod
    def get_relevant_categories(self, context: Dict[str, Any]) -> List[str]:
        """Get relevant knowledge categories for this query"""
        pass

class DialogueRAGAdapter(SystemRAGAdapter):
    """RAG adapter for dialogue system"""
    
    def __init__(self):
        super().__init__("dialogue")
    
    async def preprocess_query(self, query: str, context: Dict[str, Any]) -> str:
        """Add dialogue-specific context to query"""
        npc_id = context.get('npc_id', '')
        location = context.get('location', '')
        
        enhanced_query = f"Dialogue context for NPC {npc_id} at {location}: {query}"
        return enhanced_query
    
    async def postprocess_response(self, response: RAGResponse, context: Dict[str, Any]) -> RAGResponse:
        """Format response for dialogue use"""
        # Add dialogue-specific formatting
        if response.context_used:
            response.content += f"\n[Knowledge confidence: {response.confidence:.2f}]"
        return response
    
    def get_relevant_categories(self, context: Dict[str, Any]) -> List[str]:
        """Get categories relevant to dialogue"""
        base_categories = ['dialogue', 'characters', 'lore']
        
        # Add context-specific categories
        if context.get('faction_id'):
            base_categories.append('factions')
        if context.get('quest_id'):
            base_categories.append('quests')
        if context.get('location'):
            base_categories.append('locations')
            
        return base_categories

class QuestRAGAdapter(SystemRAGAdapter):
    """RAG adapter for quest system"""
    
    def __init__(self):
        super().__init__("quest")
    
    async def preprocess_query(self, query: str, context: Dict[str, Any]) -> str:
        """Add quest-specific context to query"""
        quest_type = context.get('quest_type', '')
        difficulty = context.get('difficulty', '')
        
        enhanced_query = f"Quest information ({quest_type}, {difficulty}): {query}"
        return enhanced_query
    
    async def postprocess_response(self, response: RAGResponse, context: Dict[str, Any]) -> RAGResponse:
        """Format response for quest use"""
        # Add quest-specific metadata
        response.metadata = getattr(response, 'metadata', {})
        response.metadata['quest_relevant'] = True
        return response
    
    def get_relevant_categories(self, context: Dict[str, Any]) -> List[str]:
        """Get categories relevant to quests"""
        return ['quests', 'characters', 'locations', 'factions', 'items', 'lore']

class NPCRAGAdapter(SystemRAGAdapter):
    """RAG adapter for NPC system"""
    
    def __init__(self):
        super().__init__("npc")
    
    async def preprocess_query(self, query: str, context: Dict[str, Any]) -> str:
        """Add NPC-specific context to query"""
        npc_type = context.get('npc_type', '')
        profession = context.get('profession', '')
        
        enhanced_query = f"NPC information ({npc_type}, {profession}): {query}"
        return enhanced_query
    
    async def postprocess_response(self, response: RAGResponse, context: Dict[str, Any]) -> RAGResponse:
        """Format response for NPC use"""
        return response
    
    def get_relevant_categories(self, context: Dict[str, Any]) -> List[str]:
        """Get categories relevant to NPCs"""
        return ['npcs', 'characters', 'dialogue', 'factions', 'locations']

class MagicRAGAdapter(SystemRAGAdapter):
    """RAG adapter for magic system"""
    
    def __init__(self):
        super().__init__("magic")
    
    async def preprocess_query(self, query: str, context: Dict[str, Any]) -> str:
        """Add magic-specific context to query"""
        spell_school = context.get('spell_school', '')
        magic_level = context.get('magic_level', '')
        
        enhanced_query = f"Magic system ({spell_school}, level {magic_level}): {query}"
        return enhanced_query
    
    async def postprocess_response(self, response: RAGResponse, context: Dict[str, Any]) -> RAGResponse:
        """Format response for magic use"""
        return response
    
    def get_relevant_categories(self, context: Dict[str, Any]) -> List[str]:
        """Get categories relevant to magic"""
        return ['magic', 'rules', 'lore', 'characters', 'items']

class RAGClient:
    """
    Simplified client interface for systems to interact with RAG service
    """
    
    def __init__(self, system_name: str, adapter: Optional[SystemRAGAdapter] = None):
        self.system_name = system_name
        self.adapter = adapter
        self.logger = logging.getLogger(f"{__name__}.{system_name}")
        self.rag_service = None
        
        # Default adapters
        self.default_adapters = {
            'dialogue': DialogueRAGAdapter(),
            'quest': QuestRAGAdapter(),
            'npc': NPCRAGAdapter(),
            'magic': MagicRAGAdapter()
        }
    
    async def initialize(self):
        """Initialize the RAG client"""
        self.rag_service = await get_rag_service()
        
        # Use default adapter if none provided
        if not self.adapter and self.system_name in self.default_adapters:
            self.adapter = self.default_adapters[self.system_name]
            await self.rag_service.register_adapter(self.system_name, self.adapter)
    
    async def add_knowledge(
        self, 
        content: str, 
        category: str, 
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        confidence: float = 1.0
    ) -> bool:
        """Add knowledge entry for this system"""
        if not self.rag_service:
            await self.initialize()
        
        entry = KnowledgeEntry(
            id=f"{self.system_name}_{datetime.now().isoformat()}_{hash(content)}",
            content=content,
            category=category,
            system=self.system_name,
            metadata=metadata or {},
            timestamp=datetime.now(),
            confidence=confidence,
            tags=tags or []
        )
        
        return await self.rag_service.add_knowledge(entry)
    
    async def query(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None,
        categories: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> List[KnowledgeEntry]:
        """Query knowledge for this system"""
        if not self.rag_service:
            await self.initialize()
        
        context = context or {}
        
        # Use adapter to preprocess query
        processed_query = query
        if self.adapter:
            processed_query = await self.adapter.preprocess_query(query, context)
            
            # Get relevant categories from adapter if not specified
            if not categories:
                categories = self.adapter.get_relevant_categories(context)
        
        return await self.rag_service.retrieve_knowledge(
            query=processed_query,
            systems=[self.system_name],
            categories=categories,
            max_results=max_results
        )
    
    async def enhance_response(
        self, 
        base_response: str, 
        context: str,
        context_data: Optional[Dict[str, Any]] = None,
        categories: Optional[List[str]] = None
    ) -> RAGResponse:
        """Enhance a response with RAG knowledge"""
        if not self.rag_service:
            await self.initialize()
        
        context_data = context_data or {}
        
        # Use adapter to get relevant categories if not specified
        if not categories and self.adapter:
            categories = self.adapter.get_relevant_categories(context_data)
        
        response = await self.rag_service.enhance_response(
            base_response=base_response,
            context=context,
            system=self.system_name,
            categories=categories
        )
        
        # Use adapter to postprocess response
        if self.adapter:
            response = await self.adapter.postprocess_response(response, context_data)
        
        return response
    
    async def cross_system_query(
        self, 
        query: str, 
        systems: List[str],
        context: Optional[Dict[str, Any]] = None,
        categories: Optional[List[str]] = None
    ) -> List[KnowledgeEntry]:
        """Query knowledge across multiple systems"""
        if not self.rag_service:
            await self.initialize()
        
        return await self.rag_service.retrieve_knowledge(
            query=query,
            systems=systems,
            categories=categories
        )
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get statistics for this system's knowledge"""
        if not self.rag_service:
            await self.initialize()
        
        all_stats = await self.rag_service.get_statistics()
        return {
            'system': self.system_name,
            'entries': all_stats['collections'].get(self.system_name, 0),
            'total_systems': len(all_stats['collections']),
            'rag_initialized': all_stats['initialized']
        }

class RAGKnowledgeManager:
    """
    Utility class for managing knowledge across all systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rag_service = None
    
    async def initialize(self):
        """Initialize the knowledge manager"""
        self.rag_service = await get_rag_service()
    
    async def bulk_add_knowledge(self, entries: List[KnowledgeEntry]) -> Dict[str, int]:
        """Add multiple knowledge entries"""
        if not self.rag_service:
            await self.initialize()
        
        results = {'success': 0, 'failed': 0}
        
        for entry in entries:
            success = await self.rag_service.add_knowledge(entry)
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
        
        return results
    
    async def import_from_file(self, file_path: str, system: str, category: str) -> Dict[str, int]:
        """Import knowledge from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split content into chunks (simple approach)
            chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
            
            entries = []
            for i, chunk in enumerate(chunks):
                entry = KnowledgeEntry(
                    id=f"{system}_{category}_{i}",
                    content=chunk,
                    category=category,
                    system=system,
                    metadata={'source_file': file_path},
                    timestamp=datetime.now()
                )
                entries.append(entry)
            
            return await self.bulk_add_knowledge(entries)
            
        except Exception as e:
            self.logger.error(f"Failed to import from file {file_path}: {e}")
            return {'success': 0, 'failed': 1}
    
    async def export_system_knowledge(self, system: str, output_file: str) -> bool:
        """Export all knowledge for a system to a file"""
        if not self.rag_service:
            await self.initialize()
        
        try:
            # This would require implementing an export method in the RAG service
            # For now, just log the intent
            self.logger.info(f"Export functionality not yet implemented for {system}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to export knowledge for {system}: {e}")
            return False
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get statistics across all systems"""
        if not self.rag_service:
            await self.initialize()
        
        return await self.rag_service.get_statistics()

# Convenience functions for quick access
async def create_rag_client(system_name: str, adapter: Optional[SystemRAGAdapter] = None) -> RAGClient:
    """Create and initialize a RAG client for a system"""
    client = RAGClient(system_name, adapter)
    await client.initialize()
    return client

async def quick_query(system: str, query: str, context: Optional[Dict[str, Any]] = None) -> List[KnowledgeEntry]:
    """Quick query function for simple use cases"""
    client = await create_rag_client(system)
    return await client.query(query, context)

async def quick_enhance(
    system: str, 
    base_response: str, 
    context: str,
    context_data: Optional[Dict[str, Any]] = None
) -> RAGResponse:
    """Quick response enhancement function"""
    client = await create_rag_client(system)
    return await client.enhance_response(base_response, context, context_data) 