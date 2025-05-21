"""
This module defines cognitive frames and utilities for memory interpretation.
Cognitive frames represent how NPCs interpret and contextualize memories.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Set

class CognitiveFrame(str, Enum):
    """Canonical cognitive frames for interpreting memories."""
    # Interpretation frames
    VICTIM = "victim"                # Sees self as wronged/harmed
    HERO = "hero"                    # Sees self as savior/victor
    MENTOR = "mentor"                # Sees self as guide/teacher
    SURVIVOR = "survivor"            # Sees self as enduring hardship
    AVENGER = "avenger"              # Sees self as justice-bringer
    
    # Worldview frames
    OPTIMISTIC = "optimistic"        # Positive outlook, sees opportunity
    PESSIMISTIC = "pessimistic"      # Negative outlook, expects the worst
    PARANOID = "paranoid"            # Suspicious, sees threats/conspiracies
    FATALISTIC = "fatalistic"        # Believes in predetermined outcomes
    PRAGMATIC = "pragmatic"          # Practical, focuses on results
    
    # Relational frames
    LOYAL = "loyal"                  # Values allegiance, honors commitments
    DISTRUSTFUL = "distrustful"      # Wary of others' motives
    PROTECTIVE = "protective"        # Guards others, prioritizes safety
    COMPETITIVE = "competitive"      # Views relationships as contests
    COLLABORATIVE = "collaborative"  # Seeks mutual benefit
    
    # Moral frames
    JUSTICE = "justice"              # Concerned with fairness/equity
    CARE = "care"                    # Focused on well-being/harm prevention
    AUTHORITY = "authority"          # Values hierarchy/respect for order
    LIBERTY = "liberty"              # Values freedom/autonomy
    TRADITION = "tradition"          # Values customs/established ways


class CognitiveFrameMetadata:
    """Metadata and utility methods for cognitive frames."""
    
    _frame_metadata: Dict[CognitiveFrame, Dict[str, Any]] = {
        CognitiveFrame.VICTIM: {
            "display_name": "Victim Frame",
            "description": "Interprets events through lens of being wronged",
            "opposites": [CognitiveFrame.HERO, CognitiveFrame.SURVIVOR],
            "related": [CognitiveFrame.DISTRUSTFUL, CognitiveFrame.PESSIMISTIC]
        },
        CognitiveFrame.HERO: {
            "display_name": "Hero Frame",
            "description": "Interprets events through lens of being a savior",
            "opposites": [CognitiveFrame.VICTIM, CognitiveFrame.DISTRUSTFUL],
            "related": [CognitiveFrame.OPTIMISTIC, CognitiveFrame.PROTECTIVE]
        },
        CognitiveFrame.OPTIMISTIC: {
            "display_name": "Optimistic Frame",
            "description": "Interprets events positively, sees opportunity",
            "opposites": [CognitiveFrame.PESSIMISTIC, CognitiveFrame.FATALISTIC],
            "related": [CognitiveFrame.HERO, CognitiveFrame.COLLABORATIVE]
        },
        CognitiveFrame.PESSIMISTIC: {
            "display_name": "Pessimistic Frame",
            "description": "Interprets events negatively, expects the worst",
            "opposites": [CognitiveFrame.OPTIMISTIC],
            "related": [CognitiveFrame.PARANOID, CognitiveFrame.DISTRUSTFUL]
        },
        # Default values for other frames if not explicitly defined
        "_default": {
            "display_name": "",  # Will be auto-generated from enum name
            "description": "General cognitive frame",
            "opposites": [],
            "related": []
        }
    }
    
    @classmethod
    def get_metadata(cls, frame: CognitiveFrame) -> Dict[str, Any]:
        """Get metadata for a specific cognitive frame."""
        if frame in cls._frame_metadata:
            metadata = cls._frame_metadata[frame].copy()
        else:
            metadata = cls._frame_metadata["_default"].copy()
            # Generate display name from enum if not explicitly defined
            metadata["display_name"] = frame.name.title().replace('_', ' ')
            
        return metadata
    
    @classmethod
    def get_opposite_frames(cls, frame: CognitiveFrame) -> List[CognitiveFrame]:
        """Get opposite cognitive frames."""
        return cls.get_metadata(frame).get("opposites", [])
    
    @classmethod
    def get_related_frames(cls, frame: CognitiveFrame) -> List[CognitiveFrame]:
        """Get related cognitive frames."""
        return cls.get_metadata(frame).get("related", [])


def detect_cognitive_frames(memory_content: str) -> Set[CognitiveFrame]:
    """
    Detect cognitive frames based on memory content.
    
    Args:
        memory_content: The memory content text
        
    Returns:
        A set of CognitiveFrame values
    """
    content_lower = memory_content.lower()
    frames = set()
    
    # Victim frame detection
    if any(word in content_lower for word in ["wronged", "attacked", "unfair", "victim", "hurt by"]):
        frames.add(CognitiveFrame.VICTIM)
    
    # Hero frame detection
    if any(word in content_lower for word in ["saved", "protected", "rescued", "hero", "helped"]):
        frames.add(CognitiveFrame.HERO)
    
    # Optimistic frame detection
    if any(word in content_lower for word in ["hopeful", "opportunity", "bright future", "positive", "chance"]):
        frames.add(CognitiveFrame.OPTIMISTIC)
    
    # Pessimistic frame detection
    if any(word in content_lower for word in ["hopeless", "doomed", "inevitable", "pointless", "never work"]):
        frames.add(CognitiveFrame.PESSIMISTIC)
    
    # Paranoid frame detection
    if any(word in content_lower for word in ["conspiracy", "watching", "spying", "out to get", "trust no one"]):
        frames.add(CognitiveFrame.PARANOID)
    
    # Add more detection logic for other frames
    
    return frames


def apply_cognitive_frame(memory_content: str, frame: CognitiveFrame) -> str:
    """
    Apply a cognitive frame to reinterpret a memory.
    
    Args:
        memory_content: Original memory content
        frame: The cognitive frame to apply
        
    Returns:
        Reinterpreted memory content
    """
    import openai
    
    try:
        prompt = f"""Reinterpret this memory from a {frame.value} perspective:
        
Original memory: {memory_content}

Reinterpreted memory (keep similar length):"""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cognitive frame interpreter for an NPC memory system."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=len(memory_content) + 50
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error applying cognitive frame: {e}")
        return memory_content  # Return original if reinterpretation fails


def get_memory_emotional_impact(memory_content: str) -> Dict[str, float]:
    """
    Analyze a memory for emotional impact.
    
    Args:
        memory_content: The memory content
        
    Returns:
        Dictionary mapping emotion names to intensity values (0.0-1.0)
    """
    emotions = {
        "joy": 0.0,
        "fear": 0.0,
        "anger": 0.0,
        "sadness": 0.0,
        "surprise": 0.0,
        "disgust": 0.0,
        "trust": 0.0,
        "anticipation": 0.0
    }
    
    # Simple rule-based emotion detection - in a real implementation,
    # this would use a more sophisticated approach (e.g., ML model)
    content_lower = memory_content.lower()
    
    # Joy detection
    if any(word in content_lower for word in ["happy", "joy", "delighted", "pleased", "excited"]):
        emotions["joy"] = 0.8
    elif any(word in content_lower for word in ["good", "nice", "satisfied"]):
        emotions["joy"] = 0.5
    
    # Fear detection  
    if any(word in content_lower for word in ["terrified", "horror", "panic"]):
        emotions["fear"] = 0.8
    elif any(word in content_lower for word in ["afraid", "scared", "worried"]):
        emotions["fear"] = 0.5
    
    # Anger detection
    if any(word in content_lower for word in ["furious", "enraged", "hate"]):
        emotions["anger"] = 0.8
    elif any(word in content_lower for word in ["angry", "annoyed", "irritated"]):
        emotions["anger"] = 0.5
    
    # Sadness detection
    if any(word in content_lower for word in ["grief", "devastated", "miserable"]):
        emotions["sadness"] = 0.8
    elif any(word in content_lower for word in ["sad", "unhappy", "disappointed"]):
        emotions["sadness"] = 0.5
    
    return emotions 