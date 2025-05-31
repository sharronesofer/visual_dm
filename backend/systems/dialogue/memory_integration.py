"""
Memory integration for dialogue system.

Provides integration between dialogue processing and memory systems
for context-aware conversations and memory persistence.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class DialogueMemoryIntegration:
    """
    Integration layer between dialogue and memory systems.
    
    Handles storing dialogue context, retrieving relevant memories,
    and maintaining conversation state across interactions.
    """
    
    def __init__(self, memory_manager=None):
        """
        Initialize dialogue memory integration.
        
        Args:
            memory_manager: Optional memory manager instance
        """
        self.memory_manager = memory_manager
        self.conversation_cache = {}
        self.context_window = 10  # Number of recent messages to keep in context
        
    def store_dialogue_memory(
        self,
        user_id: str,
        session_id: str,
        message: str,
        speaker: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store dialogue message in memory.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            message: Message content
            speaker: Speaker identifier
            metadata: Optional metadata
            
        Returns:
            True if stored successfully
        """
        try:
            memory_data = {
                "type": "dialogue",
                "user_id": user_id,
                "session_id": session_id,
                "message": message,
                "speaker": speaker,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Store in memory manager if available
            if self.memory_manager:
                return self.memory_manager.store_memory(memory_data)
            
            # Fallback: store in local cache
            cache_key = f"{user_id}:{session_id}"
            if cache_key not in self.conversation_cache:
                self.conversation_cache[cache_key] = []
            
            self.conversation_cache[cache_key].append(memory_data)
            
            # Limit cache size
            if len(self.conversation_cache[cache_key]) > 100:
                self.conversation_cache[cache_key] = self.conversation_cache[cache_key][-100:]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to store dialogue memory: {e}")
            return False
    
    def retrieve_conversation_history(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a user session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of conversation messages
        """
        try:
            # Try memory manager first
            if self.memory_manager:
                filters = {
                    "type": "dialogue",
                    "user_id": user_id,
                    "session_id": session_id
                }
                memories = self.memory_manager.retrieve_memories(filters, limit)
                return memories
            
            # Fallback: use local cache
            cache_key = f"{user_id}:{session_id}"
            if cache_key in self.conversation_cache:
                messages = self.conversation_cache[cache_key]
                return messages[-limit:] if limit else messages
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []
    
    def get_relevant_context(
        self,
        user_id: str,
        current_message: str,
        max_context: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context for current message.
        
        Args:
            user_id: User identifier
            current_message: Current message to find context for
            max_context: Maximum context items to return
            
        Returns:
            List of relevant context items
        """
        try:
            # Try memory manager first
            if self.memory_manager:
                # Search for relevant memories
                search_results = self.memory_manager.search_memories(
                    query=current_message,
                    user_id=user_id,
                    limit=max_context
                )
                return search_results
            
            # Fallback: simple keyword matching in cache
            relevant_items = []
            keywords = set(current_message.lower().split())
            
            for cache_key, messages in self.conversation_cache.items():
                if user_id in cache_key:
                    for message_data in messages:
                        message_text = message_data.get("message", "").lower()
                        message_keywords = set(message_text.split())
                        
                        # Simple relevance check
                        overlap = len(keywords.intersection(message_keywords))
                        if overlap > 0:
                            message_data["relevance_score"] = overlap / len(keywords)
                            relevant_items.append(message_data)
            
            # Sort by relevance and return top items
            relevant_items.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            return relevant_items[:max_context]
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return []
    
    def update_conversation_context(
        self,
        user_id: str,
        session_id: str,
        context_data: Dict[str, Any]
    ) -> bool:
        """
        Update conversation context with new information.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            context_data: Context data to update
            
        Returns:
            True if updated successfully
        """
        try:
            # Store context update as a special memory type
            memory_data = {
                "type": "context_update",
                "user_id": user_id,
                "session_id": session_id,
                "context_data": context_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.memory_manager:
                return self.memory_manager.store_memory(memory_data)
            
            # Fallback: store in cache
            cache_key = f"{user_id}:{session_id}:context"
            self.conversation_cache[cache_key] = context_data
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation context: {e}")
            return False
    
    def get_conversation_summary(
        self,
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Get summary of conversation for the session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Conversation summary
        """
        try:
            history = self.retrieve_conversation_history(user_id, session_id, limit=50)
            
            if not history:
                return {
                    "message_count": 0,
                    "participants": [],
                    "topics": [],
                    "duration": 0,
                    "last_activity": None
                }
            
            # Extract basic statistics
            participants = set()
            topics = set()
            
            for message in history:
                speaker = message.get("speaker")
                if speaker:
                    participants.add(speaker)
                
                # Simple topic extraction (keywords)
                message_text = message.get("message", "")
                words = message_text.lower().split()
                # Add significant words as topics
                for word in words:
                    if len(word) > 4:  # Only longer words
                        topics.add(word)
            
            # Calculate duration
            timestamps = [msg.get("timestamp") for msg in history if msg.get("timestamp")]
            duration = 0
            if len(timestamps) >= 2:
                try:
                    start_time = datetime.fromisoformat(timestamps[0])
                    end_time = datetime.fromisoformat(timestamps[-1])
                    duration = (end_time - start_time).total_seconds()
                except:
                    pass
            
            return {
                "message_count": len(history),
                "participants": list(participants),
                "topics": list(topics)[:10],  # Top 10 topics
                "duration": duration,
                "last_activity": timestamps[-1] if timestamps else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get conversation summary: {e}")
            return {
                "message_count": 0,
                "participants": [],
                "topics": [],
                "duration": 0,
                "last_activity": None
            }
    
    def clear_session_memory(
        self,
        user_id: str,
        session_id: str
    ) -> bool:
        """
        Clear memory for a specific session.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            True if cleared successfully
        """
        try:
            if self.memory_manager:
                filters = {
                    "user_id": user_id,
                    "session_id": session_id
                }
                return self.memory_manager.clear_memories(filters)
            
            # Fallback: clear from cache
            cache_key = f"{user_id}:{session_id}"
            if cache_key in self.conversation_cache:
                del self.conversation_cache[cache_key]
            
            context_key = f"{user_id}:{session_id}:context"
            if context_key in self.conversation_cache:
                del self.conversation_cache[context_key]
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear session memory: {e}")
            return False 