"""
Firebase service for memory storage and retrieval.
"""

from typing import Dict, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.models.memory import Memory, MemorySummary, NPCKnowledge, MemoryLayer

class FirebaseMemoryService:
    def __init__(self):
        """Initialize Firebase connection."""
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate("path/to/serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()
        self.memories_collection = self.db.collection('memories')
        self.npc_knowledge_collection = self.db.collection('npc_knowledge')

    async def store_memory(self, memory: Memory) -> str:
        """Store a memory in Firebase."""
        memory_dict = memory.model_dump()
        memory_dict['timestamp'] = memory_dict['timestamp'].isoformat()
        doc_ref = self.memories_collection.document(memory.id)
        doc_ref.set(memory_dict)
        return memory.id

    async def store_memory_summary(self, summary: MemorySummary) -> str:
        """Store a memory summary in Firebase."""
        summary_dict = summary.model_dump()
        summary_dict['timestamp'] = summary_dict['timestamp'].isoformat()
        doc_ref = self.memories_collection.document(summary.id)
        doc_ref.set(summary_dict)
        return summary.id

    async def store_npc_knowledge(self, npc_knowledge: NPCKnowledge) -> str:
        """Store NPC knowledge in Firebase."""
        knowledge_dict = npc_knowledge.model_dump()
        knowledge_dict['last_update'] = knowledge_dict['last_update'].isoformat()
        
        # Convert memories and summaries to dict format
        for layer in MemoryLayer:
            knowledge_dict['memories'][layer] = [
                m.model_dump() for m in knowledge_dict['memories'][layer]
            ]
            knowledge_dict['summaries'][layer] = [
                s.model_dump() for s in knowledge_dict['summaries'][layer]
            ]
        
        doc_ref = self.npc_knowledge_collection.document(npc_knowledge.npc_id)
        doc_ref.set(knowledge_dict)
        return npc_knowledge.npc_id

    async def get_memory(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory from Firebase."""
        doc = self.memories_collection.document(memory_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            return Memory(**data)
        return None

    async def get_npc_knowledge(self, npc_id: str) -> Optional[NPCKnowledge]:
        """Retrieve NPC knowledge from Firebase."""
        doc = self.npc_knowledge_collection.document(npc_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['last_update'] = datetime.fromisoformat(data['last_update'])
            
            # Convert dicts back to Memory and MemorySummary objects
            for layer in MemoryLayer:
                data['memories'][layer] = [
                    Memory(**m) for m in data['memories'][layer]
                ]
                data['summaries'][layer] = [
                    MemorySummary(**s) for s in data['summaries'][layer]
                ]
            
            return NPCKnowledge(**data)
        return None

    async def get_memories_by_type(self, memory_type: str, 
                                 limit: int = 100) -> List[Memory]:
        """Retrieve memories by type."""
        query = self.memories_collection.where(
            filter=FieldFilter("type", "==", memory_type)
        ).limit(limit)
        
        memories = []
        for doc in query.stream():
            data = doc.to_dict()
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            memories.append(Memory(**data))
        return memories

    async def get_memories_by_tag(self, tag: str, 
                                limit: int = 100) -> List[Memory]:
        """Retrieve memories by tag."""
        query = self.memories_collection.where(
            filter=FieldFilter("tags", "array_contains", tag)
        ).limit(limit)
        
        memories = []
        for doc in query.stream():
            data = doc.to_dict()
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
            memories.append(Memory(**data))
        return memories

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory from Firebase."""
        doc_ref = self.memories_collection.document(memory_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()
            return True
        return False

    async def update_memory_confidence(self, memory_id: str, 
                                     confidence: float) -> bool:
        """Update a memory's confidence level."""
        doc_ref = self.memories_collection.document(memory_id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.update({"confidence": confidence})
            return True
        return False 