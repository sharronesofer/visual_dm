"""
This module defines custom GPT summarization styles for generating
memory summaries with different levels of detail and narrative approaches.
"""

from typing import Dict, Any, List, Optional
from enum import Enum, auto

class SummarizationStyle(str, Enum):
    """Enumeration of available summarization styles."""
    CONCISE = "concise"          # Brief, factual summaries
    DETAILED = "detailed"        # More comprehensive summaries
    NARRATIVE = "narrative"      # Story-like, character-focused summaries
    EMOTIONAL = "emotional"      # Emphasizes feelings and reactions
    NEUTRAL = "neutral"          # Objective, unbiased summaries
    CYNICAL = "cynical"          # Skeptical, pessimistic view
    OPTIMISTIC = "optimistic"    # Positive, hopeful view
    STRATEGIC = "strategic"      # Focuses on tactical/strategic implications

class SummarizationDetail(str, Enum):
    """Enumeration of summarization detail levels."""
    LOW = "low"         # Minimal detail, key points only
    MEDIUM = "medium"   # Balanced detail level
    HIGH = "high"       # Extensive detail, comprehensive

class SummarizationConfig:
    """
    Configuration for GPT summarization of memories.
    Provides system prompts and parameters for different summarization styles.
    """
    
    # Base prompts for different styles
    _STYLE_PROMPTS = {
        SummarizationStyle.CONCISE: "Summarize the following events briefly and factually.",
        SummarizationStyle.DETAILED: "Provide a comprehensive summary with important details.",
        SummarizationStyle.NARRATIVE: "Craft a narrative summary that feels like part of a story.",
        SummarizationStyle.EMOTIONAL: "Summarize with emphasis on emotional impact and reactions.",
        SummarizationStyle.NEUTRAL: "Provide an objective, unbiased summary of events.",
        SummarizationStyle.CYNICAL: "Summarize with a skeptical, slightly pessimistic perspective.",
        SummarizationStyle.OPTIMISTIC: "Create a positive, hopeful summary that sees potential.",
        SummarizationStyle.STRATEGIC: "Summarize with focus on strategic and tactical implications."
    }
    
    # Detail level modifiers
    _DETAIL_MODIFIERS = {
        SummarizationDetail.LOW: "Focus only on the most essential points.",
        SummarizationDetail.MEDIUM: "Include a balanced level of detail.",
        SummarizationDetail.HIGH: "Include comprehensive details and context."
    }
    
    # Temperature settings for different styles
    _STYLE_TEMPERATURES = {
        SummarizationStyle.CONCISE: 0.3,
        SummarizationStyle.DETAILED: 0.5,
        SummarizationStyle.NARRATIVE: 0.7,
        SummarizationStyle.EMOTIONAL: 0.6,
        SummarizationStyle.NEUTRAL: 0.2,
        SummarizationStyle.CYNICAL: 0.5,
        SummarizationStyle.OPTIMISTIC: 0.5,
        SummarizationStyle.STRATEGIC: 0.4
    }
    
    # Token limits for different detail levels
    _DETAIL_TOKEN_LIMITS = {
        SummarizationDetail.LOW: 100,
        SummarizationDetail.MEDIUM: 200,
        SummarizationDetail.HIGH: 350
    }
    
    @classmethod
    def get_system_prompt(cls, style: SummarizationStyle, detail: SummarizationDetail) -> str:
        """
        Get the system prompt for a specific summarization style and detail level.
        
        Args:
            style: The summarization style
            detail: The detail level
            
        Returns:
            System prompt string for LLM
        """
        style_prompt = cls._STYLE_PROMPTS.get(style, cls._STYLE_PROMPTS[SummarizationStyle.NEUTRAL])
        detail_modifier = cls._DETAIL_MODIFIERS.get(detail, cls._DETAIL_MODIFIERS[SummarizationDetail.MEDIUM])
        
        return f"{style_prompt} {detail_modifier}"
    
    @classmethod
    def get_temperature(cls, style: SummarizationStyle) -> float:
        """
        Get the temperature setting for a specific summarization style.
        
        Args:
            style: The summarization style
            
        Returns:
            Temperature value (0.0 to 1.0)
        """
        return cls._STYLE_TEMPERATURES.get(style, 0.5)
    
    @classmethod
    def get_max_tokens(cls, detail: SummarizationDetail) -> int:
        """
        Get the maximum tokens for a specific detail level.
        
        Args:
            detail: The detail level
            
        Returns:
            Maximum token count
        """
        return cls._DETAIL_TOKEN_LIMITS.get(detail, 200)
    
    @classmethod
    def get_config(cls, 
                  style: SummarizationStyle = SummarizationStyle.NEUTRAL, 
                  detail: SummarizationDetail = SummarizationDetail.MEDIUM, 
                  model: str = "gpt-4") -> Dict[str, Any]:
        """
        Get the complete configuration for a summarization request.
        
        Args:
            style: The summarization style
            detail: The detail level
            model: The GPT model to use
            
        Returns:
            Dictionary with model, system_prompt, temperature, and max_tokens
        """
        return {
            "model": model,
            "system_prompt": cls.get_system_prompt(style, detail),
            "temperature": cls.get_temperature(style),
            "max_tokens": cls.get_max_tokens(detail)
        }
    
    @classmethod
    def get_all_styles(cls) -> List[Dict[str, Any]]:
        """
        Get a list of all available summarization styles with descriptions.
        
        Returns:
            List of dictionaries with style information
        """
        return [
            {"id": style.value, "name": style.name.title(), "description": cls._STYLE_PROMPTS[style].split('.')[0]}
            for style in SummarizationStyle
        ]
    
    @classmethod
    def get_all_detail_levels(cls) -> List[Dict[str, Any]]:
        """
        Get a list of all available detail levels with descriptions.
        
        Returns:
            List of dictionaries with detail level information
        """
        return [
            {"id": detail.value, "name": detail.name.title(), "description": cls._DETAIL_MODIFIERS[detail]}
            for detail in SummarizationDetail
        ] 