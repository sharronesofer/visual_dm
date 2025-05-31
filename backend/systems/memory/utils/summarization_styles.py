"""
Memory Summarization Styles.

This module defines different styles and approaches for memory summarization.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class SummarizationStyle(Enum):
    """Different styles for memory summarization."""
    
    CHRONOLOGICAL = "chronological"      # Time-based summary
    THEMATIC = "thematic"                # Topic-based grouping
    IMPORTANCE = "importance"            # Importance-weighted summary
    EMOTIONAL = "emotional"              # Emotion-focused summary
    RELATIONSHIP = "relationship"        # Relationship-focused summary
    FACTUAL = "factual"                 # Fact-based summary
    NARRATIVE = "narrative"             # Story-like summary


class SummarizationConfig(BaseModel):
    """Configuration for a summarization style."""
    
    style: SummarizationStyle
    display_name: str
    description: str
    max_memories_per_chunk: int
    min_importance_threshold: float
    preserve_core_memories: bool
    grouping_criteria: List[str]
    output_format: str


# Summarization style configurations
SUMMARIZATION_CONFIGS: Dict[SummarizationStyle, SummarizationConfig] = {
    SummarizationStyle.CHRONOLOGICAL: SummarizationConfig(
        style=SummarizationStyle.CHRONOLOGICAL,
        display_name="Chronological Summary",
        description="Summarize memories in chronological order, preserving timeline",
        max_memories_per_chunk=20,
        min_importance_threshold=0.3,
        preserve_core_memories=True,
        grouping_criteria=["created_at", "temporal_context"],
        output_format="timeline"
    ),
    
    SummarizationStyle.THEMATIC: SummarizationConfig(
        style=SummarizationStyle.THEMATIC,
        display_name="Thematic Summary",
        description="Group memories by themes and topics",
        max_memories_per_chunk=15,
        min_importance_threshold=0.2,
        preserve_core_memories=True,
        grouping_criteria=["categories", "content_similarity"],
        output_format="thematic_groups"
    ),
    
    SummarizationStyle.IMPORTANCE: SummarizationConfig(
        style=SummarizationStyle.IMPORTANCE,
        display_name="Importance-Weighted Summary",
        description="Prioritize memories by importance and saliency",
        max_memories_per_chunk=10,
        min_importance_threshold=0.5,
        preserve_core_memories=True,
        grouping_criteria=["importance", "saliency"],
        output_format="importance_ranked"
    ),
    
    SummarizationStyle.EMOTIONAL: SummarizationConfig(
        style=SummarizationStyle.EMOTIONAL,
        display_name="Emotional Summary",
        description="Focus on emotionally significant memories",
        max_memories_per_chunk=12,
        min_importance_threshold=0.4,
        preserve_core_memories=True,
        grouping_criteria=["emotional_intensity", "trauma", "achievement"],
        output_format="emotional_narrative"
    ),
    
    SummarizationStyle.RELATIONSHIP: SummarizationConfig(
        style=SummarizationStyle.RELATIONSHIP,
        display_name="Relationship Summary",
        description="Organize memories around relationships and interactions",
        max_memories_per_chunk=18,
        min_importance_threshold=0.3,
        preserve_core_memories=True,
        grouping_criteria=["relationship", "interaction", "conversation"],
        output_format="relationship_map"
    ),
    
    SummarizationStyle.FACTUAL: SummarizationConfig(
        style=SummarizationStyle.FACTUAL,
        display_name="Factual Summary",
        description="Extract and preserve factual information",
        max_memories_per_chunk=25,
        min_importance_threshold=0.2,
        preserve_core_memories=True,
        grouping_criteria=["knowledge", "location", "faction", "world_state"],
        output_format="fact_list"
    ),
    
    SummarizationStyle.NARRATIVE: SummarizationConfig(
        style=SummarizationStyle.NARRATIVE,
        display_name="Narrative Summary",
        description="Create story-like summaries of memory sequences",
        max_memories_per_chunk=15,
        min_importance_threshold=0.3,
        preserve_core_memories=True,
        grouping_criteria=["event", "achievement", "temporal_sequence"],
        output_format="story_narrative"
    )
}


def get_summarization_styles() -> List[Dict[str, Any]]:
    """Get all available summarization styles."""
    styles = []
    for style, config in SUMMARIZATION_CONFIGS.items():
        styles.append({
            "value": style.value,
            "display_name": config.display_name,
            "description": config.description,
            "max_memories_per_chunk": config.max_memories_per_chunk,
            "min_importance_threshold": config.min_importance_threshold,
            "preserve_core_memories": config.preserve_core_memories,
            "grouping_criteria": config.grouping_criteria,
            "output_format": config.output_format
        })
    return styles


def get_style_config(style: SummarizationStyle) -> SummarizationConfig:
    """Get configuration for a specific summarization style."""
    return SUMMARIZATION_CONFIGS[style]


def get_default_style() -> SummarizationStyle:
    """Get the default summarization style."""
    return SummarizationStyle.CHRONOLOGICAL


def get_style_by_name(style_name: str) -> Optional[SummarizationStyle]:
    """Get a summarization style by its string name."""
    try:
        return SummarizationStyle(style_name)
    except ValueError:
        return None


def should_summarize_memories(
    memory_count: int,
    style: SummarizationStyle,
    force_threshold: Optional[int] = None
) -> bool:
    """
    Determine if memories should be summarized based on count and style.
    
    Args:
        memory_count: Number of memories to potentially summarize
        style: The summarization style to use
        force_threshold: Optional override for the threshold
        
    Returns:
        True if memories should be summarized
    """
    config = get_style_config(style)
    threshold = force_threshold or config.max_memories_per_chunk
    
    return memory_count >= threshold


def get_grouping_strategy(style: SummarizationStyle) -> List[str]:
    """Get the grouping strategy for a summarization style."""
    config = get_style_config(style)
    return config.grouping_criteria


def get_output_format(style: SummarizationStyle) -> str:
    """Get the output format for a summarization style."""
    config = get_style_config(style)
    return config.output_format
