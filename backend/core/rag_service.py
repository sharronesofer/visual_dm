"""
Core RAG (Retrieval-Augmented Generation) Service
Provides centralized knowledge management and retrieval for all game systems
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from pathlib import Path

# Vector database and embeddings
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logging.warning("RAG dependencies not available. Install chromadb and sentence-transformers for full functionality.")

@dataclass
class KnowledgeEntry:
    """Standardized knowledge entry structure"""
    id: str
    content: str
    category: str
    system: str
    metadata: Dict[str, Any]
    timestamp: datetime
    confidence: float = 1.0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class RAGResponse:
    """Response from RAG retrieval"""
    content: str
    sources: List[KnowledgeEntry]
    confidence: float
    context_used: bool
    processing_time: float

class RAGConfiguration:
    """Centralized RAG configuration"""
    
    def __init__(self):
        # Vector database settings
        self.vector_db_path = os.getenv('RAG_DB_PATH', './data/rag_db')
        self.embedding_model = os.getenv('RAG_EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        
        # Retrieval settings
        self.max_results = int(os.getenv('RAG_MAX_RESULTS', '5'))
        self.relevance_threshold = float(os.getenv('RAG_RELEVANCE_THRESHOLD', '0.7'))
        self.context_window = int(os.getenv('RAG_CONTEXT_WINDOW', '2000'))
        
        # Performance settings
        self.cache_enabled = os.getenv('RAG_CACHE_ENABLED', 'true').lower() == 'true'
        self.cache_ttl = int(os.getenv('RAG_CACHE_TTL', '3600'))  # 1 hour
        self.batch_size = int(os.getenv('RAG_BATCH_SIZE', '100'))
        
        # Knowledge categories and weights
        self.category_weights = {
            'lore': 0.8,
            'characters': 0.9,
            'locations': 0.7,
            'factions': 0.6,
            'quests': 0.8,
            'items': 0.5,
            'events': 0.7,
            'magic': 0.7,
            'rules': 0.9,
            'history': 0.6,
            'npcs': 0.8,
            'dialogue': 0.8,
            'rumors': 0.5,
            'memory': 0.7
        }

class CrossSystemRAGService:
    """
    Centralized RAG service providing knowledge-enhanced responses for all game systems
    """
    
    def __init__(self, config: Optional[RAGConfiguration] = None):
        self.config = config or RAGConfiguration()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.client = None
        self.embedder = None
        self.collections = {}
        self.cache = {}
        self.is_initialized = False
        
        # System-specific adapters
        self.adapters = {}
        
    async def initialize(self) -> bool:
        """Initialize the RAG service"""
        if not DEPENDENCIES_AVAILABLE:
            self.logger.warning("RAG dependencies not available, operating in fallback mode")
            return False
            
        try:
            # Initialize vector database
            self.client = chromadb.PersistentClient(
                path=self.config.vector_db_path,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Initialize embedding model
            self.embedder = SentenceTransformer(self.config.embedding_model)
            
            # Initialize collections for each system
            await self._initialize_collections()
            
            self.is_initialized = True
            self.logger.info("RAG service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RAG service: {e}")
            return False
    
    async def _initialize_collections(self):
        """Initialize vector database collections for each system"""
        systems = [
            'dialogue', 'quest', 'npc', 'faction', 'memory', 
            'rumor', 'magic', 'world_generation', 'motif', 'region',
            'war', 'time', 'population', 'relationship'
        ]
        
        for system in systems:
            try:
                collection_name = f"{system}_knowledge"
                self.collections[system] = self.client.get_or_create_collection(
                    name=collection_name,
                    metadata={"system": system, "created": datetime.now().isoformat()}
                )
                self.logger.debug(f"Initialized collection for {system}")
            except Exception as e:
                self.logger.error(f"Failed to initialize collection for {system}: {e}")
    
    async def add_knowledge(self, entry: KnowledgeEntry) -> bool:
        """Add knowledge entry to the appropriate collection"""
        if not self.is_initialized:
            return False
            
        try:
            collection = self.collections.get(entry.system)
            if not collection:
                self.logger.error(f"No collection found for system: {entry.system}")
                return False
            
            # Generate embedding
            embedding = self.embedder.encode(entry.content).tolist()
            
            # Add to collection
            collection.add(
                embeddings=[embedding],
                documents=[entry.content],
                metadatas=[{
                    "category": entry.category,
                    "system": entry.system,
                    "timestamp": entry.timestamp.isoformat(),
                    "confidence": entry.confidence,
                    "tags": json.dumps(entry.tags),
                    **entry.metadata
                }],
                ids=[entry.id]
            )
            
            self.logger.debug(f"Added knowledge entry {entry.id} to {entry.system}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add knowledge entry: {e}")
            return False
    
    async def retrieve_knowledge(
        self, 
        query: str, 
        systems: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> List[KnowledgeEntry]:
        """Retrieve relevant knowledge entries"""
        if not self.is_initialized:
            return []
        
        max_results = max_results or self.config.max_results
        systems = systems or list(self.collections.keys())
        
        all_results = []
        
        try:
            # Generate query embedding
            query_embedding = self.embedder.encode(query).tolist()
            
            # Search across specified systems
            for system in systems:
                if system not in self.collections:
                    continue
                    
                collection = self.collections[system]
                
                # Build where clause for categories
                where_clause = {}
                if categories:
                    where_clause["category"] = {"$in": categories}
                
                # Query collection
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(max_results, 10),  # Limit per system
                    where=where_clause if where_clause else None
                )
                
                # Convert results to KnowledgeEntry objects
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else 0.0
                    confidence = 1.0 - distance  # Convert distance to confidence
                    
                    if confidence >= self.config.relevance_threshold:
                        entry = KnowledgeEntry(
                            id=results['ids'][0][i],
                            content=doc,
                            category=metadata.get('category', ''),
                            system=metadata.get('system', system),
                            metadata={k: v for k, v in metadata.items() 
                                    if k not in ['category', 'system', 'timestamp', 'confidence', 'tags']},
                            timestamp=datetime.fromisoformat(metadata.get('timestamp', datetime.now().isoformat())),
                            confidence=confidence,
                            tags=json.loads(metadata.get('tags', '[]'))
                        )
                        all_results.append(entry)
            
            # Sort by confidence and apply category weights
            weighted_results = []
            for entry in all_results:
                weight = self.config.category_weights.get(entry.category, 0.5)
                weighted_confidence = entry.confidence * weight
                entry.confidence = weighted_confidence
                weighted_results.append(entry)
            
            # Sort and limit results
            weighted_results.sort(key=lambda x: x.confidence, reverse=True)
            return weighted_results[:max_results]
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve knowledge: {e}")
            return []
    
    async def enhance_response(
        self, 
        base_response: str, 
        context: str,
        system: str,
        categories: Optional[List[str]] = None
    ) -> RAGResponse:
        """Enhance a base response with retrieved knowledge"""
        start_time = datetime.now()
        
        if not self.is_initialized:
            return RAGResponse(
                content=base_response,
                sources=[],
                confidence=0.0,
                context_used=False,
                processing_time=0.0
            )
        
        try:
            # Retrieve relevant knowledge
            knowledge_entries = await self.retrieve_knowledge(
                query=context,
                systems=[system],
                categories=categories
            )
            
            if not knowledge_entries:
                processing_time = (datetime.now() - start_time).total_seconds()
                return RAGResponse(
                    content=base_response,
                    sources=[],
                    confidence=0.5,
                    context_used=False,
                    processing_time=processing_time
                )
            
            # Combine knowledge for context
            knowledge_context = "\n".join([
                f"[{entry.category}] {entry.content}" 
                for entry in knowledge_entries[:3]  # Limit context
            ])
            
            # For now, return enhanced response with knowledge context
            # In a full implementation, this would call an LLM to integrate the knowledge
            enhanced_response = f"{base_response}\n\n[Enhanced with knowledge about: {', '.join([e.category for e in knowledge_entries[:3]])}]"
            
            processing_time = (datetime.now() - start_time).total_seconds()
            avg_confidence = sum(e.confidence for e in knowledge_entries) / len(knowledge_entries)
            
            return RAGResponse(
                content=enhanced_response,
                sources=knowledge_entries,
                confidence=avg_confidence,
                context_used=True,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to enhance response: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            return RAGResponse(
                content=base_response,
                sources=[],
                confidence=0.0,
                context_used=False,
                processing_time=processing_time
            )
    
    async def register_adapter(self, system: str, adapter):
        """Register a system-specific RAG adapter"""
        self.adapters[system] = adapter
        self.logger.info(f"Registered RAG adapter for {system}")
    
    async def get_system_knowledge(self, system: str, query: str) -> List[KnowledgeEntry]:
        """Get knowledge specific to a system"""
        return await self.retrieve_knowledge(query, systems=[system])
    
    async def update_knowledge(self, entry_id: str, system: str, new_content: str) -> bool:
        """Update existing knowledge entry"""
        if not self.is_initialized:
            return False
            
        try:
            collection = self.collections.get(system)
            if not collection:
                return False
            
            # Delete old entry
            collection.delete(ids=[entry_id])
            
            # Add updated entry (this is a simplified approach)
            # In practice, you'd want to preserve metadata and just update content
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update knowledge entry: {e}")
            return False
    
    async def delete_knowledge(self, entry_id: str, system: str) -> bool:
        """Delete knowledge entry"""
        if not self.is_initialized:
            return False
            
        try:
            collection = self.collections.get(system)
            if not collection:
                return False
            
            collection.delete(ids=[entry_id])
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete knowledge entry: {e}")
            return False
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get RAG service statistics"""
        stats = {
            "initialized": self.is_initialized,
            "collections": {},
            "total_entries": 0,
            "cache_size": len(self.cache),
            "config": asdict(self.config) if hasattr(self.config, '__dict__') else str(self.config)
        }
        
        if self.is_initialized:
            for system, collection in self.collections.items():
                try:
                    count = collection.count()
                    stats["collections"][system] = count
                    stats["total_entries"] += count
                except Exception as e:
                    stats["collections"][system] = f"Error: {e}"
        
        return stats

# Global RAG service instance
_rag_service = None

async def get_rag_service() -> CrossSystemRAGService:
    """Get or create the global RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = CrossSystemRAGService()
        await _rag_service.initialize()
    return _rag_service

async def initialize_rag_service(config: Optional[RAGConfiguration] = None) -> CrossSystemRAGService:
    """Initialize the global RAG service with custom configuration"""
    global _rag_service
    _rag_service = CrossSystemRAGService(config)
    await _rag_service.initialize()
    return _rag_service 