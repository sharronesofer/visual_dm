"""
Text utility functions for dialogue system.

Provides text processing, token counting, and information extraction
utilities for dialogue processing and analysis.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from collections import Counter

logger = logging.getLogger(__name__)


def count_tokens(text: str, method: str = "simple") -> int:
    """
    Count tokens in text using specified method.
    
    Args:
        text: Text to count tokens in
        method: Counting method ("simple", "whitespace", "words")
        
    Returns:
        Number of tokens
    """
    if not text or not isinstance(text, str):
        return 0
    
    text = text.strip()
    if not text:
        return 0
    
    if method == "simple":
        # Simple approximation: ~4 characters per token
        return max(1, len(text) // 4)
    elif method == "whitespace":
        # Split on whitespace
        return len(text.split())
    elif method == "words":
        # Split on word boundaries
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    else:
        # Default to simple method
        return max(1, len(text) // 4)


def extract_key_info(text: str, max_keywords: int = 10) -> Dict[str, Any]:
    """
    Extract key information from text.
    
    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        Dictionary containing extracted information
    """
    if not text or not isinstance(text, str):
        return {
            "keywords": [],
            "word_count": 0,
            "sentence_count": 0,
            "character_count": 0,
            "sentiment": "neutral"
        }
    
    # Basic text statistics
    word_count = len(text.split())
    sentence_count = len(re.findall(r'[.!?]+', text))
    character_count = len(text)
    
    # Extract keywords (simple frequency-based approach)
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Extract words and filter
    words = re.findall(r'\b\w+\b', text.lower())
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Get most common words as keywords
    word_freq = Counter(filtered_words)
    keywords = [word for word, _ in word_freq.most_common(max_keywords)]
    
    # Simple sentiment analysis (very basic)
    positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'happy', 'joy'}
    negative_words = {'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'sad', 'angry', 'frustrated', 'disappointed'}
    
    text_words = set(words)
    positive_score = len(text_words.intersection(positive_words))
    negative_score = len(text_words.intersection(negative_words))
    
    if positive_score > negative_score:
        sentiment = "positive"
    elif negative_score > positive_score:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "keywords": keywords,
        "word_count": word_count,
        "sentence_count": max(1, sentence_count),  # At least 1 sentence
        "character_count": character_count,
        "sentiment": sentiment,
        "positive_score": positive_score,
        "negative_score": negative_score
    }


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\'"()-]', '', text)
    
    # Trim and return
    return text.strip()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or not isinstance(text, str):
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length // 2:  # Only use word boundary if it's not too short
        truncated = truncated[:last_space]
    
    return truncated + suffix


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text (simple pattern-based approach).
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary of entity types and their values
    """
    if not text or not isinstance(text, str):
        return {"names": [], "locations": [], "organizations": []}
    
    entities = {
        "names": [],
        "locations": [],
        "organizations": []
    }
    
    # Simple pattern matching for names (capitalized words)
    name_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    potential_names = re.findall(name_pattern, text)
    
    # Filter out common words that might be capitalized
    common_words = {'The', 'This', 'That', 'These', 'Those', 'A', 'An', 'And', 'Or', 'But'}
    names = [name for name in potential_names if name not in common_words]
    
    entities["names"] = list(set(names))  # Remove duplicates
    
    # For locations and organizations, we'd need more sophisticated NLP
    # For now, just return empty lists
    
    return entities


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts (simple word overlap).
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Convert to sets of words
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def format_dialogue_text(text: str, speaker: Optional[str] = None) -> str:
    """
    Format text for dialogue display.
    
    Args:
        text: Text to format
        speaker: Optional speaker name
        
    Returns:
        Formatted dialogue text
    """
    if not text:
        return ""
    
    # Clean the text
    formatted = clean_text(text)
    
    # Add speaker if provided
    if speaker:
        formatted = f"{speaker}: {formatted}"
    
    return formatted 