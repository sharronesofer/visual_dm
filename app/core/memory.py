"""
Memory system for tracking events and managing memory decay.
"""

from flask import current_app
from firebase_admin import firestore
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class MemorySystem:
    def __init__(self, app):
        self.app = app
        self.db = firestore.client()
        self.memory_collection = self.db.collection('memories')
        self.event_collection = self.db.collection('events')
        self.scheduler = BackgroundScheduler()
        self._setup_cleanup_tasks()
        
    def _setup_cleanup_tasks(self):
        """Set up scheduled cleanup tasks."""
        # Run memory pruning daily
        self.scheduler.add_job(
            self.prune_memories,
            trigger=IntervalTrigger(days=1),
            id='memory_pruning',
            replace_existing=True
        )
        
        # Run persistence check weekly
        self.scheduler.add_job(
            self.persist_important_memories,
            trigger=IntervalTrigger(weeks=1),
            id='memory_persistence',
            replace_existing=True
        )
        
        self.scheduler.start()
        
    def prune_memories(self):
        """Remove memories that have decayed beyond recovery."""
        min_clarity = current_app.config.get('MIN_MEMORY_CLARITY', 0.1)
        
        # Get all memories below minimum clarity
        memories_to_prune = self.memory_collection.where(
            'clarity', '<', min_clarity
        ).get()
        
        for memory_doc in memories_to_prune:
            memory = memory_doc.to_dict()
            
            # Only delete if importance is below threshold
            if memory.get('importance', 0) < current_app.config.get('MIN_MEMORY_IMPORTANCE', 0.3):
                memory_doc.reference.delete()
                
    def persist_important_memories(self):
        """Ensure important memories are properly persisted."""
        min_importance = current_app.config.get('PERSISTENT_MEMORY_IMPORTANCE', 0.7)
        
        # Get all important memories
        important_memories = self.memory_collection.where(
            'importance', '>=', min_importance
        ).get()
        
        for memory_doc in important_memories:
            memory = memory_doc.to_dict()
            
            # Update last accessed and ensure clarity doesn't decay below threshold
            memory_doc.reference.update({
                'last_accessed': datetime.utcnow().isoformat(),
                'clarity': max(memory.get('clarity', 0.5), 0.5)
            })
            
    def cleanup(self):
        """Clean up resources when shutting down."""
        self.scheduler.shutdown()
        
    def record_event(self, event_type: str, description: str, 
                    participants: List[str], importance: float) -> str:
        """Record a new event in the system."""
        event = {
            'type': event_type,
            'description': description,
            'participants': participants,
            'importance': importance,
            'timestamp': datetime.utcnow().isoformat(),
            'location': None,  # Can be updated later
            'related_events': [],
            'tags': []
        }
        
        event_doc = self.event_collection.add(event)
        return event_doc[1].id
        
    def create_memory(self, npc_id: str, event_id: str, 
                     perspective: str, emotional_impact: float) -> str:
        """Create a memory of an event for an NPC."""
        event = self.event_collection.document(event_id).get()
        if not event.exists:
            return None
            
        event_data = event.to_dict()
        
        memory = {
            'npc_id': npc_id,
            'event_id': event_id,
            'perspective': perspective,
            'emotional_impact': emotional_impact,
            'created_at': datetime.utcnow().isoformat(),
            'last_accessed': datetime.utcnow().isoformat(),
            'clarity': 1.0,  # Starts at full clarity
            'importance': event_data['importance'],
            'tags': event_data.get('tags', [])
        }
        
        memory_doc = self.memory_collection.add(memory)
        return memory_doc[1].id
        
    def get_npc_memories(self, npc_id: str, 
                        min_clarity: float = 0.0,
                        min_importance: float = 0.0) -> List[Dict]:
        """Retrieve memories for an NPC, optionally filtered by clarity and importance."""
        memories_query = self.memory_collection.where(
            'npc_id', '==', npc_id
        ).where(
            'clarity', '>=', min_clarity
        ).where(
            'importance', '>=', min_importance
        ).get()
        
        memories = []
        for memory_doc in memories_query:
            memory = memory_doc.to_dict()
            memory['id'] = memory_doc.id
            
            # Get the associated event
            event = self.event_collection.document(memory['event_id']).get()
            if event.exists:
                memory['event'] = event.to_dict()
                
            memories.append(memory)
            
        return memories
        
    def update_memory_clarity(self, memory_id: str) -> None:
        """Update memory clarity based on time and importance."""
        memory_ref = self.memory_collection.document(memory_id)
        memory = memory_ref.get().to_dict()
        
        if not memory:
            return
            
        # Calculate time since last access
        last_accessed = datetime.fromisoformat(memory['last_accessed'])
        time_diff = datetime.utcnow() - last_accessed
        
        # Calculate decay based on time and importance
        decay_rate = current_app.config.get('MEMORY_DECAY_RATE', 0.1)
        importance_factor = 1.0 - (memory['importance'] * 0.5)  # More important = slower decay
        days_passed = time_diff.days
        
        new_clarity = max(0.0, memory['clarity'] - (decay_rate * days_passed * importance_factor))
        
        memory_ref.update({
            'clarity': new_clarity,
            'last_accessed': datetime.utcnow().isoformat()
        })
        
    def get_related_memories(self, memory_id: str, 
                           min_similarity: float = 0.5) -> List[Dict]:
        """Get memories related to a specific memory based on tags and participants."""
        memory_ref = self.memory_collection.document(memory_id)
        memory = memory_ref.get().to_dict()
        
        if not memory:
            return []
            
        # Get the event
        event = self.event_collection.document(memory['event_id']).get()
        if not event.exists:
            return []
            
        event_data = event.to_dict()
        
        # Find related memories
        related_memories = []
        memories_query = self.memory_collection.where(
            'npc_id', '==', memory['npc_id']
        ).get()
        
        for mem_doc in memories_query:
            if mem_doc.id == memory_id:
                continue
                
            mem = mem_doc.to_dict()
            mem_event = self.event_collection.document(mem['event_id']).get()
            if not mem_event.exists:
                continue
                
            mem_event_data = mem_event.to_dict()
            
            # Calculate similarity score
            similarity = self._calculate_memory_similarity(
                event_data, mem_event_data,
                memory['tags'], mem['tags']
            )
            
            if similarity >= min_similarity:
                mem['similarity'] = similarity
                mem['event'] = mem_event_data
                related_memories.append(mem)
                
        return sorted(related_memories, key=lambda x: x['similarity'], reverse=True)
        
    def _calculate_memory_similarity(self, event1: Dict, event2: Dict,
                                   tags1: List[str], tags2: List[str]) -> float:
        """Calculate similarity between two memories based on events and tags."""
        similarity = 0.0
        
        # Check event type
        if event1['type'] == event2['type']:
            similarity += 0.3
            
        # Check participants
        common_participants = set(event1['participants']) & set(event2['participants'])
        if common_participants:
            similarity += 0.3 * (len(common_participants) / max(len(event1['participants']), len(event2['participants'])))
            
        # Check tags
        common_tags = set(tags1) & set(tags2)
        if common_tags:
            similarity += 0.4 * (len(common_tags) / max(len(tags1), len(tags2)))
            
        return similarity

def init_memory_system(app):
    """Initialize the memory system."""
    app.memory_system = MemorySystem(app)
    
    # Register cleanup on app teardown
    @app.teardown_appcontext
    def cleanup_memory_system(exception=None):
        app.memory_system.cleanup() 