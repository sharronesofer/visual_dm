"""
Memory Decay and Summarization System
------------------------------------

Implements memory decay, word count limits, and LLM-driven summarization.
Follows the user's vision: day -> week -> quarter -> year summarization progression
where important things remain and details are forgotten.
"""

from typing import Dict, List, Optional, Any, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import re
import asyncio

if TYPE_CHECKING:
    from backend.systems.memory.services.memory import Memory
    from backend.systems.memory.memory_categories import MemoryCategory

logger = logging.getLogger(__name__)


@dataclass
class MemoryStorageConfig:
    """Configuration for memory storage limits."""
    
    # Per-NPC limits (reasonable for narrative purposes)
    max_words_per_npc: int = 10000  # ~20 pages of text
    max_individual_memory_words: int = 500  # ~1 page per memory
    
    # Summarization thresholds
    daily_summarization_threshold: int = 1000  # Words before daily summary
    weekly_summarization_threshold: int = 2000  # Words before weekly summary
    quarterly_summarization_threshold: int = 4000  # Words before quarterly summary
    
    # Decay settings
    importance_preservation_threshold: float = 0.7  # Memories above this importance resist decay
    access_frequency_protection: int = 3  # Memories accessed this many times resist decay
    
    # LLM summarization settings
    summary_target_reduction: float = 0.3  # Target 30% of original word count in summaries
    preserve_high_importance: bool = True
    preserve_emotional_content: bool = True


class SummarizationTimeframe(Enum):
    """Timeframes for memory summarization."""
    
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class MemoryDecayResult:
    """Result of memory decay operation."""
    
    entity_id: str
    original_memory_count: int
    final_memory_count: int
    original_word_count: int
    final_word_count: int
    summaries_created: List[str]  # IDs of summary memories created
    memories_archived: List[str]  # IDs of memories archived
    decay_timestamp: datetime


class MemoryDecayManager:
    """Manages memory decay, summarization, and storage limits."""
    
    def __init__(self, memory_manager=None, config: Optional[MemoryStorageConfig] = None):
        self.memory_manager = memory_manager
        self.config = config or MemoryStorageConfig()
        self.logger = logging.getLogger(__name__)
    
    async def check_and_apply_decay(self, entity_id: str) -> MemoryDecayResult:
        """Check memory limits and apply decay/summarization as needed."""
        if not self.memory_manager:
            return self._empty_decay_result(entity_id)
        
        # Get all active memories for entity
        memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=1000)
        
        # Calculate current word count
        total_words = sum(self._count_words(memory.content) for memory in memories)
        
        original_count = len(memories)
        original_words = total_words
        
        # If within limits, no action needed
        if total_words <= self.config.max_words_per_npc:
            return MemoryDecayResult(
                entity_id=entity_id,
                original_memory_count=original_count,
                final_memory_count=original_count,
                original_word_count=original_words,
                final_word_count=original_words,
                summaries_created=[],
                memories_archived=[],
                decay_timestamp=datetime.utcnow()
            )
        
        # Apply progressive summarization
        summaries_created = []
        memories_archived = []
        
        # 1. Daily summarization (oldest memories first)
        if total_words > self.config.daily_summarization_threshold:
            daily_summaries, daily_archived = await self._create_daily_summaries(entity_id, memories)
            summaries_created.extend(daily_summaries)
            memories_archived.extend(daily_archived)
        
        # 2. Weekly summarization
        if total_words > self.config.weekly_summarization_threshold:
            weekly_summaries, weekly_archived = await self._create_weekly_summaries(entity_id)
            summaries_created.extend(weekly_summaries)
            memories_archived.extend(weekly_archived)
        
        # 3. Quarterly summarization (if still over limit)
        if total_words > self.config.quarterly_summarization_threshold:
            quarterly_summaries, quarterly_archived = await self._create_quarterly_summaries(entity_id)
            summaries_created.extend(quarterly_summaries)
            memories_archived.extend(quarterly_archived)
        
        # 4. If still over limit, archive oldest low-importance memories
        final_memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=1000)
        final_words = sum(self._count_words(memory.content) for memory in final_memories)
        
        if final_words > self.config.max_words_per_npc:
            archived_low_importance = await self._archive_low_importance_memories(entity_id, final_words)
            memories_archived.extend(archived_low_importance)
        
        # Calculate final stats
        post_decay_memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=1000)
        final_count = len(post_decay_memories)
        final_words = sum(self._count_words(memory.content) for memory in post_decay_memories)
        
        return MemoryDecayResult(
            entity_id=entity_id,
            original_memory_count=original_count,
            final_memory_count=final_count,
            original_word_count=original_words,
            final_word_count=final_words,
            summaries_created=summaries_created,
            memories_archived=memories_archived,
            decay_timestamp=datetime.utcnow()
        )
    
    async def _create_daily_summaries(self, entity_id: str, memories: List["Memory"]) -> Tuple[List[str], List[str]]:
        """Create daily summaries for groups of memories."""
        summaries_created = []
        memories_archived = []
        
        # Group memories by day
        daily_groups = self._group_memories_by_timeframe(memories, SummarizationTimeframe.DAILY)
        
        for date_key, day_memories in daily_groups.items():
            if len(day_memories) < 3:  # Don't summarize if too few memories
                continue
            
            # Check if any memories are protected from summarization
            protected_memories = [m for m in day_memories if self._is_memory_protected(m)]
            summarizable_memories = [m for m in day_memories if not self._is_memory_protected(m)]
            
            if len(summarizable_memories) < 2:
                continue
            
            # Create LLM-driven summary
            summary_content = await self._generate_llm_summary(
                memories=summarizable_memories,
                timeframe=SummarizationTimeframe.DAILY,
                date_context=date_key
            )
            
            if summary_content:
                # Create summary memory
                summary_memory = await self.memory_manager.create_memory(
                    content=summary_content,
                    memory_type="summary",
                    importance=self._calculate_summary_importance(summarizable_memories),
                    metadata={
                        "summary_type": "daily",
                        "date": date_key,
                        "original_memory_count": len(summarizable_memories),
                        "summarized_memories": [m.memory_id for m in summarizable_memories]
                    }
                )
                
                summaries_created.append(summary_memory.memory_id)
                
                # Archive the original memories (soft delete)
                for memory in summarizable_memories:
                    await self.memory_manager.archive_memory(memory.memory_id)
                    memories_archived.append(memory.memory_id)
        
        return summaries_created, memories_archived
    
    async def _create_weekly_summaries(self, entity_id: str) -> Tuple[List[str], List[str]]:
        """Create weekly summaries from daily summaries."""
        summaries_created = []
        memories_archived = []
        
        # Get existing daily summaries
        daily_summaries = await self._get_summaries_by_type(entity_id, "daily")
        
        # Group by week
        weekly_groups = self._group_memories_by_timeframe(daily_summaries, SummarizationTimeframe.WEEKLY)
        
        for week_key, week_summaries in weekly_groups.items():
            if len(week_summaries) < 3:  # Need at least 3 daily summaries
                continue
            
            # Create weekly summary from daily summaries
            weekly_content = await self._generate_llm_summary(
                memories=week_summaries,
                timeframe=SummarizationTimeframe.WEEKLY,
                date_context=week_key
            )
            
            if weekly_content:
                weekly_memory = await self.memory_manager.create_memory(
                    content=weekly_content,
                    memory_type="summary",
                    importance=self._calculate_summary_importance(week_summaries),
                    metadata={
                        "summary_type": "weekly",
                        "week": week_key,
                        "original_summary_count": len(week_summaries),
                        "summarized_summaries": [m.memory_id for m in week_summaries]
                    }
                )
                
                summaries_created.append(weekly_memory.memory_id)
                
                # Archive daily summaries
                for summary in week_summaries:
                    await self.memory_manager.archive_memory(summary.memory_id)
                    memories_archived.append(summary.memory_id)
        
        return summaries_created, memories_archived
    
    async def _create_quarterly_summaries(self, entity_id: str) -> Tuple[List[str], List[str]]:
        """Create quarterly summaries from monthly/weekly summaries."""
        summaries_created = []
        memories_archived = []
        
        # Get existing weekly summaries
        weekly_summaries = await self._get_summaries_by_type(entity_id, "weekly")
        
        # Group by quarter
        quarterly_groups = self._group_memories_by_timeframe(weekly_summaries, SummarizationTimeframe.QUARTERLY)
        
        for quarter_key, quarter_summaries in quarterly_groups.items():
            if len(quarter_summaries) < 4:  # Need multiple weeks for a quarter
                continue
            
            quarterly_content = await self._generate_llm_summary(
                memories=quarter_summaries,
                timeframe=SummarizationTimeframe.QUARTERLY,
                date_context=quarter_key
            )
            
            if quarterly_content:
                quarterly_memory = await self.memory_manager.create_memory(
                    content=quarterly_content,
                    memory_type="summary",
                    importance=self._calculate_summary_importance(quarter_summaries),
                    metadata={
                        "summary_type": "quarterly",
                        "quarter": quarter_key,
                        "original_summary_count": len(quarter_summaries),
                        "summarized_summaries": [m.memory_id for m in quarter_summaries]
                    }
                )
                
                summaries_created.append(quarterly_memory.memory_id)
                
                # Archive weekly summaries
                for summary in quarter_summaries:
                    await self.memory_manager.archive_memory(summary.memory_id)
                    memories_archived.append(summary.memory_id)
        
        return summaries_created, memories_archived
    
    async def _generate_llm_summary(self, memories: List["Memory"], timeframe: SummarizationTimeframe, date_context: str) -> Optional[str]:
        """Generate LLM-driven summary of memories."""
        if not memories:
            return None
        
        # Prepare memory content for LLM
        memory_texts = []
        for memory in memories:
            memory_texts.append(f"[Importance: {memory.importance:.1f}] {memory.content}")
        
        # Create summarization prompt
        prompt = self._create_summarization_prompt(memory_texts, timeframe, date_context)
        
        try:
            # TODO: Replace with actual LLM call
            # For now, create a basic extractive summary
            summary = await self._create_extractive_summary(memories, timeframe)
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to generate LLM summary: {e}")
            # Fallback to extractive summary
            return await self._create_extractive_summary(memories, timeframe)
    
    def _create_summarization_prompt(self, memory_texts: List[str], timeframe: SummarizationTimeframe, date_context: str) -> str:
        """Create prompt for LLM summarization."""
        prompt = f"""
Summarize the following {timeframe.value} memories into a concise narrative that preserves:
1. Important events and their emotional impact
2. Key relationships and interactions
3. Significant achievements or failures
4. Core beliefs and values expressed
5. Any traumatic or highly meaningful experiences

Target length: {int(sum(len(text.split()) for text in memory_texts) * self.config.summary_target_reduction)} words

Memories from {date_context}:

"""
        
        for i, memory_text in enumerate(memory_texts, 1):
            prompt += f"{i}. {memory_text}\n"
        
        prompt += "\nSummary:"
        
        return prompt
    
    async def _create_extractive_summary(self, memories: List["Memory"], timeframe: SummarizationTimeframe) -> str:
        """Create extractive summary as fallback when LLM is unavailable."""
        # Sort by importance
        sorted_memories = sorted(memories, key=lambda m: m.importance, reverse=True)
        
        # Take top memories that fit word limit
        target_words = int(sum(self._count_words(m.content) for m in memories) * self.config.summary_target_reduction)
        
        summary_parts = []
        current_words = 0
        
        for memory in sorted_memories:
            memory_words = self._count_words(memory.content)
            if current_words + memory_words <= target_words:
                # Condense the memory content
                condensed = self._condense_memory_content(memory.content)
                summary_parts.append(condensed)
                current_words += self._count_words(condensed)
            else:
                break
        
        return f"{timeframe.value.title()} summary: " + ". ".join(summary_parts)
    
    def _condense_memory_content(self, content: str) -> str:
        """Condense memory content by removing less important details."""
        # Remove filler words and redundant phrases
        condensed = re.sub(r'\b(very|really|quite|somewhat|rather|fairly)\b', '', content)
        condensed = re.sub(r'\s+', ' ', condensed).strip()
        
        # Limit to one sentence if too long
        sentences = condensed.split('.')
        if len(sentences) > 1 and len(condensed) > 100:
            return sentences[0].strip() + '.'
        
        return condensed
    
    async def _archive_low_importance_memories(self, entity_id: str, current_words: int) -> List[str]:
        """Archive oldest, lowest importance memories to meet word limit."""
        archived = []
        
        if current_words <= self.config.max_words_per_npc:
            return archived
        
        # Get all memories sorted by importance (ascending) and age (descending)
        memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=1000)
        
        # Sort by importance (low first) then by age (old first)
        archival_candidates = sorted(
            [m for m in memories if not self._is_memory_protected(m)],
            key=lambda m: (m.importance, m.created_at)
        )
        
        words_to_remove = current_words - self.config.max_words_per_npc
        words_removed = 0
        
        for memory in archival_candidates:
            if words_removed >= words_to_remove:
                break
            
            memory_words = self._count_words(memory.content)
            await self.memory_manager.archive_memory(memory.memory_id)
            archived.append(memory.memory_id)
            words_removed += memory_words
        
        return archived
    
    def _is_memory_protected(self, memory: "Memory") -> bool:
        """Check if memory is protected from decay/summarization."""
        # Protect high importance memories
        if memory.importance >= self.config.importance_preservation_threshold:
            return True
        
        # Protect frequently accessed memories
        if getattr(memory, 'access_count', 0) >= self.config.access_frequency_protection:
            return True
        
        # Protect core memories
        if memory.memory_type == "core":
            return True
        
        # Protect trauma and identity memories
        if hasattr(memory, 'categories'):
            protected_categories = ["TRAUMA", "IDENTITY", "CORE", "SECRET"]
            if any(cat in memory.categories for cat in protected_categories):
                return True
        
        return False
    
    def _calculate_summary_importance(self, memories: List["Memory"]) -> float:
        """Calculate importance for summary based on constituent memories."""
        if not memories:
            return 0.5
        
        # Use weighted average, with higher weight for more important memories
        weights = [m.importance ** 2 for m in memories]  # Square to emphasize high importance
        weighted_sum = sum(w * m.importance for w, m in zip(weights, memories))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.5
    
    def _group_memories_by_timeframe(self, memories: List["Memory"], timeframe: SummarizationTimeframe) -> Dict[str, List["Memory"]]:
        """Group memories by specified timeframe."""
        groups = {}
        
        for memory in memories:
            if timeframe == SummarizationTimeframe.DAILY:
                key = memory.created_at.strftime("%Y-%m-%d")
            elif timeframe == SummarizationTimeframe.WEEKLY:
                # Week starting Monday
                week_start = memory.created_at - timedelta(days=memory.created_at.weekday())
                key = week_start.strftime("%Y-W%U")
            elif timeframe == SummarizationTimeframe.MONTHLY:
                key = memory.created_at.strftime("%Y-%m")
            elif timeframe == SummarizationTimeframe.QUARTERLY:
                quarter = (memory.created_at.month - 1) // 3 + 1
                key = f"{memory.created_at.year}-Q{quarter}"
            elif timeframe == SummarizationTimeframe.YEARLY:
                key = memory.created_at.strftime("%Y")
            else:
                key = "unknown"
            
            if key not in groups:
                groups[key] = []
            groups[key].append(memory)
        
        return groups
    
    async def _get_summaries_by_type(self, entity_id: str, summary_type: str) -> List["Memory"]:
        """Get existing summaries of specified type."""
        all_memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=1000)
        return [m for m in all_memories if 
                m.memory_type == "summary" and 
                m.metadata.get("summary_type") == summary_type]
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split()) if text else 0
    
    def _empty_decay_result(self, entity_id: str) -> MemoryDecayResult:
        """Return empty decay result when memory manager unavailable."""
        return MemoryDecayResult(
            entity_id=entity_id,
            original_memory_count=0,
            final_memory_count=0,
            original_word_count=0,
            final_word_count=0,
            summaries_created=[],
            memories_archived=[],
            decay_timestamp=datetime.utcnow()
        )
    
    async def enforce_memory_limits(self, entity_id: str) -> MemoryDecayResult:
        """Public method to enforce memory limits and trigger decay as needed."""
        return await self.check_and_apply_decay(entity_id)
    
    async def get_memory_storage_stats(self, entity_id: str) -> Dict[str, Any]:
        """Get storage statistics for an entity."""
        if not self.memory_manager:
            return {"error": "No memory manager available"}
        
        memories = await self.memory_manager.get_memories_by_entity(entity_id, limit=1000)
        
        total_words = sum(self._count_words(memory.content) for memory in memories)
        
        # Categorize memories
        regular_memories = [m for m in memories if m.memory_type == "regular"]
        core_memories = [m for m in memories if m.memory_type == "core"]
        summary_memories = [m for m in memories if m.memory_type == "summary"]
        
        return {
            "entity_id": entity_id,
            "total_memories": len(memories),
            "total_words": total_words,
            "word_limit": self.config.max_words_per_npc,
            "usage_percentage": (total_words / self.config.max_words_per_npc) * 100,
            "regular_memories": len(regular_memories),
            "core_memories": len(core_memories),
            "summary_memories": len(summary_memories),
            "needs_summarization": total_words > self.config.daily_summarization_threshold,
            "approaching_limit": total_words > (self.config.max_words_per_npc * 0.8),
            "over_limit": total_words > self.config.max_words_per_npc
        }


def create_decay_manager(memory_manager=None, config: Optional[MemoryStorageConfig] = None) -> MemoryDecayManager:
    """Factory function for creating memory decay manager."""
    return MemoryDecayManager(memory_manager, config) 