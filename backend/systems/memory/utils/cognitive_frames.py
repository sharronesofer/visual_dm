"""
Cognitive Frames for Memory System.

This module provides cognitive frame detection and application for memory processing.
Cognitive frames help categorize and understand the context of memories.
"""

from enum import Enum
from typing import Dict, List, Any, Optional, Set
from pydantic import BaseModel
import re


class CognitiveFrame(Enum):
    """Different cognitive frames for understanding memory context."""
    
    # Social frames
    COOPERATION = "cooperation"
    COMPETITION = "competition"
    CONFLICT = "conflict"
    ALLIANCE = "alliance"
    BETRAYAL = "betrayal"
    
    # Emotional frames
    TRUST = "trust"
    FEAR = "fear"
    LOVE = "love"
    ANGER = "anger"
    JOY = "joy"
    SADNESS = "sadness"
    
    # Achievement frames
    SUCCESS = "success"
    FAILURE = "failure"
    LEARNING = "learning"
    GROWTH = "growth"
    MASTERY = "mastery"
    
    # Survival frames
    THREAT = "threat"
    SAFETY = "safety"
    RESOURCE = "resource"
    TERRITORY = "territory"
    
    # Knowledge frames
    DISCOVERY = "discovery"
    MYSTERY = "mystery"
    UNDERSTANDING = "understanding"
    CONFUSION = "confusion"
    
    # Moral frames
    JUSTICE = "justice"
    INJUSTICE = "injustice"
    DUTY = "duty"
    FREEDOM = "freedom"


class FramePattern(BaseModel):
    """Pattern for detecting cognitive frames in memory content."""
    
    frame: CognitiveFrame
    keywords: List[str]
    context_patterns: List[str]
    emotional_indicators: List[str]
    importance_modifier: float


# Frame detection patterns
FRAME_PATTERNS: Dict[CognitiveFrame, FramePattern] = {
    CognitiveFrame.COOPERATION: FramePattern(
        frame=CognitiveFrame.COOPERATION,
        keywords=["together", "help", "assist", "collaborate", "team", "alliance", "support"],
        context_patterns=["worked with", "helped", "assisted", "collaborated"],
        emotional_indicators=["grateful", "pleased", "satisfied"],
        importance_modifier=0.1
    ),
    
    CognitiveFrame.COMPETITION: FramePattern(
        frame=CognitiveFrame.COMPETITION,
        keywords=["compete", "rival", "contest", "challenge", "race", "beat", "win"],
        context_patterns=["competed against", "challenged", "raced", "tried to beat"],
        emotional_indicators=["determined", "focused", "driven"],
        importance_modifier=0.15
    ),
    
    CognitiveFrame.CONFLICT: FramePattern(
        frame=CognitiveFrame.CONFLICT,
        keywords=["fight", "battle", "war", "attack", "defend", "enemy", "hostile"],
        context_patterns=["fought against", "battled", "attacked", "defended"],
        emotional_indicators=["angry", "hostile", "aggressive", "defensive"],
        importance_modifier=0.3
    ),
    
    CognitiveFrame.BETRAYAL: FramePattern(
        frame=CognitiveFrame.BETRAYAL,
        keywords=["betray", "deceive", "lie", "cheat", "backstab", "double-cross"],
        context_patterns=["betrayed by", "lied to", "deceived", "cheated"],
        emotional_indicators=["hurt", "angry", "disappointed", "bitter"],
        importance_modifier=0.4
    ),
    
    CognitiveFrame.TRUST: FramePattern(
        frame=CognitiveFrame.TRUST,
        keywords=["trust", "reliable", "honest", "faithful", "loyal", "dependable"],
        context_patterns=["trusted", "relied on", "counted on"],
        emotional_indicators=["secure", "confident", "comfortable"],
        importance_modifier=0.2
    ),
    
    CognitiveFrame.FEAR: FramePattern(
        frame=CognitiveFrame.FEAR,
        keywords=["fear", "afraid", "scared", "terrified", "panic", "dread", "horror"],
        context_patterns=["was afraid", "feared", "panicked"],
        emotional_indicators=["anxious", "nervous", "worried", "terrified"],
        importance_modifier=0.35
    ),
    
    CognitiveFrame.SUCCESS: FramePattern(
        frame=CognitiveFrame.SUCCESS,
        keywords=["success", "achieve", "accomplish", "win", "victory", "triumph"],
        context_patterns=["succeeded", "achieved", "accomplished", "won"],
        emotional_indicators=["proud", "satisfied", "elated", "triumphant"],
        importance_modifier=0.25
    ),
    
    CognitiveFrame.FAILURE: FramePattern(
        frame=CognitiveFrame.FAILURE,
        keywords=["fail", "lose", "defeat", "unsuccessful", "mistake", "error"],
        context_patterns=["failed to", "lost", "was defeated", "made a mistake"],
        emotional_indicators=["disappointed", "frustrated", "ashamed", "regretful"],
        importance_modifier=0.2
    ),
    
    CognitiveFrame.LEARNING: FramePattern(
        frame=CognitiveFrame.LEARNING,
        keywords=["learn", "discover", "understand", "realize", "figure out", "study"],
        context_patterns=["learned", "discovered", "figured out", "realized"],
        emotional_indicators=["curious", "enlightened", "satisfied", "intrigued"],
        importance_modifier=0.15
    ),
    
    CognitiveFrame.THREAT: FramePattern(
        frame=CognitiveFrame.THREAT,
        keywords=["threat", "danger", "risk", "peril", "hazard", "menace"],
        context_patterns=["threatened by", "in danger", "at risk"],
        emotional_indicators=["afraid", "cautious", "alert", "worried"],
        importance_modifier=0.3
    ),
    
    CognitiveFrame.DISCOVERY: FramePattern(
        frame=CognitiveFrame.DISCOVERY,
        keywords=["discover", "find", "uncover", "reveal", "explore", "investigate"],
        context_patterns=["discovered", "found", "uncovered", "revealed"],
        emotional_indicators=["excited", "curious", "amazed", "intrigued"],
        importance_modifier=0.2
    ),
    
    CognitiveFrame.JUSTICE: FramePattern(
        frame=CognitiveFrame.JUSTICE,
        keywords=["justice", "fair", "right", "wrong", "moral", "ethical", "deserve"],
        context_patterns=["was fair", "deserved", "was right", "was wrong"],
        emotional_indicators=["righteous", "satisfied", "vindicated"],
        importance_modifier=0.25
    )
}


def detect_cognitive_frames(content: str, context: Optional[str] = None) -> List[CognitiveFrame]:
    """
    Detect cognitive frames present in memory content.
    
    Args:
        content: The memory content to analyze
        context: Optional additional context
        
    Returns:
        List of detected cognitive frames
    """
    detected_frames = []
    content_lower = content.lower()
    context_lower = context.lower() if context else ""
    
    for frame, pattern in FRAME_PATTERNS.items():
        frame_score = 0
        
        # Check for keywords
        keyword_matches = sum(1 for keyword in pattern.keywords if keyword in content_lower)
        frame_score += keyword_matches * 2
        
        # Check for context patterns
        context_matches = sum(1 for ctx_pattern in pattern.context_patterns 
                            if ctx_pattern in content_lower or ctx_pattern in context_lower)
        frame_score += context_matches * 3
        
        # Check for emotional indicators
        emotion_matches = sum(1 for emotion in pattern.emotional_indicators 
                            if emotion in content_lower)
        frame_score += emotion_matches * 1.5
        
        # If score is high enough, include this frame
        if frame_score >= 2:
            detected_frames.append(frame)
    
    return detected_frames


def apply_cognitive_frames(memory_data: Dict[str, Any], frames: List[CognitiveFrame]) -> Dict[str, Any]:
    """
    Apply cognitive frames to memory data, modifying importance and metadata.
    
    Args:
        memory_data: The memory data to modify
        frames: List of cognitive frames to apply
        
    Returns:
        Modified memory data
    """
    if not frames:
        return memory_data
    
    # Calculate frame-based importance modifier
    total_modifier = 0.0
    frame_info = []
    
    for frame in frames:
        if frame in FRAME_PATTERNS:
            pattern = FRAME_PATTERNS[frame]
            total_modifier += pattern.importance_modifier
            frame_info.append({
                "frame": frame.value,
                "importance_modifier": pattern.importance_modifier
            })
    
    # Apply importance modifier
    current_importance = memory_data.get('importance', 0.5)
    new_importance = min(1.0, current_importance + (total_modifier / len(frames)))
    memory_data['importance'] = new_importance
    
    # Add frame metadata
    if 'metadata' not in memory_data:
        memory_data['metadata'] = {}
    
    memory_data['metadata']['cognitive_frames'] = frame_info
    memory_data['metadata']['frame_importance_boost'] = total_modifier / len(frames)
    
    return memory_data


def get_frame_relationships(frames: List[CognitiveFrame]) -> Dict[str, List[str]]:
    """
    Get relationships between cognitive frames.
    
    Args:
        frames: List of cognitive frames
        
    Returns:
        Dictionary of frame relationships
    """
    relationships = {
        "reinforcing": [],
        "conflicting": [],
        "neutral": []
    }
    
    # Define frame relationships
    reinforcing_pairs = [
        (CognitiveFrame.COOPERATION, CognitiveFrame.TRUST),
        (CognitiveFrame.CONFLICT, CognitiveFrame.FEAR),
        (CognitiveFrame.SUCCESS, CognitiveFrame.JOY),
        (CognitiveFrame.FAILURE, CognitiveFrame.SADNESS),
        (CognitiveFrame.BETRAYAL, CognitiveFrame.ANGER),
        (CognitiveFrame.DISCOVERY, CognitiveFrame.LEARNING),
        (CognitiveFrame.THREAT, CognitiveFrame.FEAR)
    ]
    
    conflicting_pairs = [
        (CognitiveFrame.COOPERATION, CognitiveFrame.COMPETITION),
        (CognitiveFrame.TRUST, CognitiveFrame.BETRAYAL),
        (CognitiveFrame.SUCCESS, CognitiveFrame.FAILURE),
        (CognitiveFrame.SAFETY, CognitiveFrame.THREAT),
        (CognitiveFrame.JOY, CognitiveFrame.SADNESS),
        (CognitiveFrame.JUSTICE, CognitiveFrame.INJUSTICE)
    ]
    
    # Check for relationships in the provided frames
    for i, frame1 in enumerate(frames):
        for j, frame2 in enumerate(frames):
            if i >= j:
                continue
                
            pair = (frame1, frame2)
            reverse_pair = (frame2, frame1)
            
            if pair in reinforcing_pairs or reverse_pair in reinforcing_pairs:
                relationships["reinforcing"].append(f"{frame1.value} + {frame2.value}")
            elif pair in conflicting_pairs or reverse_pair in conflicting_pairs:
                relationships["conflicting"].append(f"{frame1.value} vs {frame2.value}")
            else:
                relationships["neutral"].append(f"{frame1.value} ~ {frame2.value}")
    
    return relationships


def get_frame_summary(frames: List[CognitiveFrame]) -> Dict[str, Any]:
    """
    Get a summary of cognitive frames and their implications.
    
    Args:
        frames: List of cognitive frames
        
    Returns:
        Summary of frame analysis
    """
    if not frames:
        return {"frames": [], "analysis": "No cognitive frames detected"}
    
    frame_categories = {
        "social": [CognitiveFrame.COOPERATION, CognitiveFrame.COMPETITION, CognitiveFrame.CONFLICT, 
                  CognitiveFrame.ALLIANCE, CognitiveFrame.BETRAYAL],
        "emotional": [CognitiveFrame.TRUST, CognitiveFrame.FEAR, CognitiveFrame.LOVE, 
                     CognitiveFrame.ANGER, CognitiveFrame.JOY, CognitiveFrame.SADNESS],
        "achievement": [CognitiveFrame.SUCCESS, CognitiveFrame.FAILURE, CognitiveFrame.LEARNING, 
                       CognitiveFrame.GROWTH, CognitiveFrame.MASTERY],
        "survival": [CognitiveFrame.THREAT, CognitiveFrame.SAFETY, CognitiveFrame.RESOURCE, 
                    CognitiveFrame.TERRITORY],
        "knowledge": [CognitiveFrame.DISCOVERY, CognitiveFrame.MYSTERY, CognitiveFrame.UNDERSTANDING, 
                     CognitiveFrame.CONFUSION],
        "moral": [CognitiveFrame.JUSTICE, CognitiveFrame.INJUSTICE, CognitiveFrame.DUTY, 
                 CognitiveFrame.FREEDOM]
    }
    
    categorized_frames = {}
    for category, category_frames in frame_categories.items():
        found_frames = [f for f in frames if f in category_frames]
        if found_frames:
            categorized_frames[category] = [f.value for f in found_frames]
    
    relationships = get_frame_relationships(frames)
    
    return {
        "frames": [f.value for f in frames],
        "categorized_frames": categorized_frames,
        "relationships": relationships,
        "frame_count": len(frames),
        "dominant_categories": list(categorized_frames.keys())
    }
