"""
NPC Memory Repository

Repository for NPC memory management operations.
Handles memory creation, retrieval, updates, and deletion.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from sqlalchemy.exc import IntegrityError
import logging

# Use local infrastructure imports
from backend.infrastructure.systems.npc.models.models import NpcMemory, NpcEntity
from backend.infrastructure.shared.exceptions import NpcNotFoundError

logger = logging.getLogger(__name__)


class NPCMemoryRepository:
    """Specialized repository for NPC memory operations"""
    
    def __init__(self, db_session: Session):
        """Initialize with database session"""
        self.db = db_session
    
    def get_memories_by_importance(self, npc_id: UUID, min_importance: float = 5.0) -> List[NpcMemory]:
        """Get memories above a certain importance threshold"""
        try:
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.importance >= min_importance
            ).order_by(desc(NpcMemory.importance)).all()
        except Exception as e:
            logger.error(f"Error getting important memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_memories_by_emotion(self, npc_id: UUID, emotion: str) -> List[NpcMemory]:
        """Get memories with specific emotional context"""
        try:
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.emotion == emotion
            ).order_by(desc(NpcMemory.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting emotional memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_memories_by_location(self, npc_id: UUID, location: str) -> List[NpcMemory]:
        """Get memories from a specific location"""
        try:
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.location == location
            ).order_by(desc(NpcMemory.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting location memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_memories_by_participant(self, npc_id: UUID, participant: str) -> List[NpcMemory]:
        """Get memories involving a specific participant"""
        try:
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.participants.contains([participant])
            ).order_by(desc(NpcMemory.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting participant memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_memories_by_tags(self, npc_id: UUID, tags: List[str]) -> List[NpcMemory]:
        """Get memories that contain any of the specified tags"""
        try:
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.tags.op('&&')(tags)  # PostgreSQL array overlap operator
            ).order_by(desc(NpcMemory.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting tagged memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_recent_memories(self, npc_id: UUID, days: int = 7) -> List[NpcMemory]:
        """Get memories from the last N days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.created_at >= cutoff_date
            ).order_by(desc(NpcMemory.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting recent memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_frequently_recalled_memories(self, npc_id: UUID, min_recalls: int = 3) -> List[NpcMemory]:
        """Get memories that have been recalled frequently"""
        try:
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.recalled_count >= min_recalls
            ).order_by(desc(NpcMemory.recalled_count)).all()
        except Exception as e:
            logger.error(f"Error getting frequently recalled memories for NPC {npc_id}: {str(e)}")
            raise
    
    def recall_memory(self, npc_id: UUID, memory_id: str) -> Optional[NpcMemory]:
        """Mark a memory as recalled and increment recall count"""
        try:
            memory = self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.memory_id == memory_id
            ).first()
            
            if memory:
                memory.recalled_count += 1
                memory.last_recalled = datetime.utcnow()
                self.db.commit()
                logger.info(f"Recalled memory {memory_id} for NPC {npc_id} (count: {memory.recalled_count})")
            
            return memory
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error recalling memory {memory_id} for NPC {npc_id}: {str(e)}")
            raise
    
    def search_memories(self, npc_id: UUID, search_term: str) -> List[NpcMemory]:
        """Search memories by content"""
        try:
            search_pattern = f"%{search_term}%"
            return self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.content.ilike(search_pattern)
            ).order_by(desc(NpcMemory.importance)).all()
        except Exception as e:
            logger.error(f"Error searching memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_memory_summary_stats(self, npc_id: UUID) -> Dict[str, Any]:
        """Get statistics about an NPC's memory collection"""
        try:
            # Total memories
            total_memories = self.db.query(func.count(NpcMemory.id)).filter(
                NpcMemory.npc_id == npc_id
            ).scalar()
            
            # Average importance
            avg_importance = self.db.query(func.avg(NpcMemory.importance)).filter(
                NpcMemory.npc_id == npc_id
            ).scalar() or 0.0
            
            # Most frequent emotion
            emotion_stats = self.db.query(
                NpcMemory.emotion,
                func.count(NpcMemory.id).label('count')
            ).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.emotion.isnot(None)
            ).group_by(NpcMemory.emotion).order_by(desc('count')).first()
            
            most_frequent_emotion = emotion_stats[0] if emotion_stats else None
            
            # Memory types breakdown
            type_stats = self.db.query(
                NpcMemory.memory_type,
                func.count(NpcMemory.id).label('count')
            ).filter(
                NpcMemory.npc_id == npc_id
            ).group_by(NpcMemory.memory_type).all()
            
            type_breakdown = {stat[0]: stat[1] for stat in type_stats}
            
            # Recent activity (last 7 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            recent_count = self.db.query(func.count(NpcMemory.id)).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.created_at >= recent_cutoff
            ).scalar()
            
            return {
                "total_memories": total_memories,
                "average_importance": round(float(avg_importance), 2),
                "most_frequent_emotion": most_frequent_emotion,
                "memory_types": type_breakdown,
                "recent_memories_count": recent_count,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting memory stats for NPC {npc_id}: {str(e)}")
            raise
    
    def consolidate_similar_memories(self, npc_id: UUID, similarity_threshold: float = 0.8) -> int:
        """
        Consolidate similar memories to prevent memory bloat.
        This is a placeholder for future AI-based memory consolidation.
        """
        try:
            # For now, just mark very old, low-importance memories for cleanup
            old_cutoff = datetime.utcnow() - timedelta(days=365)  # 1 year old
            low_importance_threshold = 2.0
            
            old_memories = self.db.query(NpcMemory).filter(
                NpcMemory.npc_id == npc_id,
                NpcMemory.created_at < old_cutoff,
                NpcMemory.importance < low_importance_threshold,
                NpcMemory.recalled_count == 0
            ).all()
            
            # In a full implementation, we would use AI to merge similar memories
            # For now, we'll just count them as candidates for consolidation
            consolidation_candidates = len(old_memories)
            
            logger.info(f"Found {consolidation_candidates} memory consolidation candidates for NPC {npc_id}")
            return consolidation_candidates
            
        except Exception as e:
            logger.error(f"Error consolidating memories for NPC {npc_id}: {str(e)}")
            raise
    
    def get_memories_needing_decay(self, days_old: int = 30) -> List[NpcMemory]:
        """Get memories that haven't been recalled recently and may need importance decay"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            return self.db.query(NpcMemory).filter(
                or_(
                    NpcMemory.last_recalled < cutoff_date,
                    NpcMemory.last_recalled.is_(None)
                ),
                NpcMemory.importance > 1.0  # Only decay memories that still have some importance
            ).all()
        except Exception as e:
            logger.error(f"Error getting memories needing decay: {str(e)}")
            raise
    
    def decay_memory_importance(self, memory_id: UUID, decay_factor: float = 0.9) -> Optional[NpcMemory]:
        """Reduce the importance of a memory due to time/lack of recall"""
        try:
            memory = self.db.query(NpcMemory).filter(NpcMemory.id == memory_id).first()
            if memory:
                memory.importance = max(0.1, memory.importance * decay_factor)  # Minimum importance of 0.1
                self.db.commit()
                logger.info(f"Decayed memory {memory.memory_id} importance to {memory.importance}")
            return memory
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error decaying memory {memory_id}: {str(e)}")
            raise 