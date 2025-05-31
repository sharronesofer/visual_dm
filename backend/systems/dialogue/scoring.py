"""
Dialogue scoring utilities.

Provides relevance scoring and other scoring functions for dialogue
processing and context evaluation.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import re
from collections import Counter

logger = logging.getLogger(__name__)


def relevance_score(
    text: str,
    context: Union[str, Dict[str, Any], List[str]],
    method: str = "keyword_overlap"
) -> float:
    """
    Calculate relevance score between text and context.
    
    Args:
        text: Text to score
        context: Context to compare against (string, dict, or list)
        method: Scoring method to use
        
    Returns:
        Relevance score between 0.0 and 1.0
    """
    if not text:
        return 0.0
    
    try:
        # Convert context to text if needed
        context_text = _extract_text_from_context(context)
        
        if not context_text:
            return 0.0
        
        if method == "keyword_overlap":
            return _keyword_overlap_score(text, context_text)
        elif method == "semantic_similarity":
            return _semantic_similarity_score(text, context_text)
        elif method == "weighted":
            return _weighted_relevance_score(text, context_text)
        else:
            # Default to keyword overlap
            return _keyword_overlap_score(text, context_text)
            
    except Exception as e:
        logger.error(f"Error calculating relevance score: {e}")
        return 0.0


def _extract_text_from_context(context: Union[str, Dict[str, Any], List[str]]) -> str:
    """Extract text content from various context formats."""
    if isinstance(context, str):
        return context
    elif isinstance(context, dict):
        # Extract text from common dictionary fields
        text_parts = []
        for key in ['text', 'content', 'message', 'description', 'title']:
            if key in context and context[key]:
                text_parts.append(str(context[key]))
        return " ".join(text_parts)
    elif isinstance(context, list):
        # Join list items
        return " ".join(str(item) for item in context if item)
    else:
        return str(context) if context else ""


def _keyword_overlap_score(text1: str, text2: str) -> float:
    """Calculate keyword overlap score between two texts."""
    # Extract keywords from both texts
    words1 = set(_extract_keywords(text1))
    words2 = set(_extract_keywords(text2))
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def _semantic_similarity_score(text1: str, text2: str) -> float:
    """Calculate semantic similarity score (simplified version)."""
    # This is a simplified version - in a real implementation,
    # you might use word embeddings or other NLP techniques
    
    # For now, use enhanced keyword matching with synonyms
    keywords1 = _extract_keywords(text1)
    keywords2 = _extract_keywords(text2)
    
    # Simple synonym mapping for common words
    synonyms = {
        'good': ['great', 'excellent', 'fine', 'nice'],
        'bad': ['terrible', 'awful', 'poor', 'horrible'],
        'big': ['large', 'huge', 'massive', 'enormous'],
        'small': ['tiny', 'little', 'mini', 'compact'],
        'fast': ['quick', 'rapid', 'swift', 'speedy'],
        'slow': ['sluggish', 'gradual', 'leisurely']
    }
    
    # Expand keywords with synonyms
    expanded_keywords1 = set(keywords1)
    expanded_keywords2 = set(keywords2)
    
    for word in keywords1:
        if word in synonyms:
            expanded_keywords1.update(synonyms[word])
    
    for word in keywords2:
        if word in synonyms:
            expanded_keywords2.update(synonyms[word])
    
    # Calculate similarity with expanded keywords
    intersection = len(expanded_keywords1.intersection(expanded_keywords2))
    union = len(expanded_keywords1.union(expanded_keywords2))
    
    return intersection / union if union > 0 else 0.0


def _weighted_relevance_score(text1: str, text2: str) -> float:
    """Calculate weighted relevance score combining multiple factors."""
    # Combine keyword overlap and length similarity
    keyword_score = _keyword_overlap_score(text1, text2)
    
    # Length similarity factor
    len1, len2 = len(text1.split()), len(text2.split())
    if len1 == 0 or len2 == 0:
        length_score = 0.0
    else:
        length_ratio = min(len1, len2) / max(len1, len2)
        length_score = length_ratio
    
    # Weighted combination
    return 0.7 * keyword_score + 0.3 * length_score


def _extract_keywords(text: str) -> List[str]:
    """Extract keywords from text."""
    if not text:
        return []
    
    # Convert to lowercase and extract words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Filter out stop words and short words
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    return keywords


def dialogue_quality_score(
    dialogue_text: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, float]:
    """
    Calculate dialogue quality metrics.
    
    Args:
        dialogue_text: The dialogue text to evaluate
        context: Optional context for evaluation
        
    Returns:
        Dictionary of quality scores
    """
    if not dialogue_text:
        return {
            "coherence": 0.0,
            "relevance": 0.0,
            "engagement": 0.0,
            "overall": 0.0
        }
    
    # Coherence score (based on sentence structure and flow)
    coherence = _calculate_coherence_score(dialogue_text)
    
    # Relevance score (if context provided)
    relevance = 0.5  # Default neutral score
    if context:
        relevance = relevance_score(dialogue_text, context)
    
    # Engagement score (based on variety and interest)
    engagement = _calculate_engagement_score(dialogue_text)
    
    # Overall score (weighted average)
    overall = 0.4 * coherence + 0.4 * relevance + 0.2 * engagement
    
    return {
        "coherence": coherence,
        "relevance": relevance,
        "engagement": engagement,
        "overall": overall
    }


def _calculate_coherence_score(text: str) -> float:
    """Calculate coherence score based on text structure."""
    if not text:
        return 0.0
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 2:
        return 0.5  # Neutral score for single sentence
    
    # Check for sentence length variety
    lengths = [len(s.split()) for s in sentences]
    avg_length = sum(lengths) / len(lengths)
    
    # Penalize very short or very long sentences
    length_score = 1.0
    for length in lengths:
        if length < 3 or length > 30:
            length_score -= 0.1
    
    length_score = max(0.0, length_score)
    
    # Check for repetition
    words = text.lower().split()
    word_freq = Counter(words)
    repetition_penalty = 0.0
    
    for word, freq in word_freq.items():
        if freq > 3 and len(word) > 3:  # Repeated content words
            repetition_penalty += 0.1
    
    coherence = max(0.0, length_score - repetition_penalty)
    return min(1.0, coherence)


def _calculate_engagement_score(text: str) -> float:
    """Calculate engagement score based on text variety and interest."""
    if not text:
        return 0.0
    
    # Check for variety in sentence types
    questions = len(re.findall(r'\?', text))
    exclamations = len(re.findall(r'!', text))
    sentences = len(re.findall(r'[.!?]', text))
    
    if sentences == 0:
        return 0.0
    
    # Variety score
    variety_score = 0.0
    if questions > 0:
        variety_score += 0.3
    if exclamations > 0:
        variety_score += 0.2
    
    # Word variety score
    words = text.lower().split()
    unique_words = len(set(words))
    total_words = len(words)
    
    if total_words > 0:
        word_variety = unique_words / total_words
        variety_score += 0.5 * word_variety
    
    return min(1.0, variety_score)


def context_relevance_score(
    current_text: str,
    conversation_history: List[str],
    max_history: int = 5
) -> float:
    """
    Calculate relevance score based on conversation history.
    
    Args:
        current_text: Current dialogue text
        conversation_history: List of previous dialogue texts
        max_history: Maximum number of history items to consider
        
    Returns:
        Relevance score between 0.0 and 1.0
    """
    if not current_text or not conversation_history:
        return 0.5  # Neutral score
    
    # Consider only recent history
    recent_history = conversation_history[-max_history:]
    
    # Calculate relevance to each history item
    scores = []
    for i, history_text in enumerate(recent_history):
        # Weight more recent items higher
        weight = (i + 1) / len(recent_history)
        score = relevance_score(current_text, history_text)
        scores.append(score * weight)
    
    # Return weighted average
    return sum(scores) / len(scores) if scores else 0.5 