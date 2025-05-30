"""
Rumor system integration for the dialogue system.

This module provides functionality for connecting dialogue with the rumor system,
allowing rumors to be created from significant dialogue and for NPCs to
reference rumors in their conversations.
"""

from typing import Dict, Any, List, Optional, Set
import logging
import random
from datetime import datetime

# Import rumor system components
from backend.systems.rumors.rumor_manager import RumorManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueRumorIntegration:
    """
    Integration between dialogue and rumor systems.
    
    Allows for creating rumors from dialogue content and for incorporating
    relevant rumors into dialogue context.
    """
    
    def __init__(self, rumor_manager=None):
        """
        Initialize the dialogue rumor integration.
        
        Args:
            rumor_manager: Optional rumor manager instance
        """
        self.rumor_manager = rumor_manager or RumorManager.get_instance()
        self.rumor_threshold = 0.7  # Configurable threshold for rumor creation
    
    def generate_rumor_from_dialogue(
        self,
        speaker_id: str,
        message: str,
        location_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Attempt to generate a rumor from dialogue content.
        
        Args:
            speaker_id: ID of the character who spoke
            message: Content of the message
            location_id: Optional location where the conversation occurred
            metadata: Optional additional metadata
            
        Returns:
            ID of the created rumor or None if no rumor was created
        """
        # Check if message has potential for being a rumor
        rumor_potential = self._evaluate_rumor_potential(message)
        
        if rumor_potential < self.rumor_threshold:
            logger.debug(f"Message doesn't meet rumor threshold: {message}")
            return None
        
        # Extract key information for rumor
        rumor_content = self._extract_rumor_content(message)
        
        if not rumor_content:
            return None
        
        # Prepare rumor data
        rumor_data = {
            "content": rumor_content,
            "source_character_id": speaker_id,
            "origin_location_id": location_id,
            "veracity": self._determine_veracity(message),
            "spread_factors": {
                "sensationalism": rumor_potential,
                "plausibility": random.uniform(0.4, 0.9)  # Randomize for variety
            },
            "metadata": metadata or {}
        }
        
        # Create the rumor
        try:
            rumor_id = self.rumor_manager.create_rumor(rumor_data)
            logger.info(f"Created rumor {rumor_id} from dialogue")
            return rumor_id
        except Exception as e:
            logger.error(f"Failed to create rumor: {e}")
            return None
    
    def add_rumors_to_context(
        self,
        character_id: str,
        context: Dict[str, Any],
        limit: int = 3
    ) -> Dict[str, Any]:
        """
        Add relevant rumors to dialogue context.
        
        Args:
            character_id: ID of the character whose known rumors to add
            context: The existing dialogue context
            limit: Maximum number of rumors to add
            
        Returns:
            Updated context with rumors added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Get rumors known by the character
        rumors = self.get_relevant_rumors(character_id, context, limit)
        
        # Add rumors to context
        if rumors:
            if "rumors" not in updated_context:
                updated_context["rumors"] = []
                
            updated_context["rumors"].extend(rumors)
            logger.debug(f"Added {len(rumors)} rumors to context for character {character_id}")
        
        return updated_context
    
    def get_relevant_rumors(
        self,
        character_id: str,
        context: Dict[str, Any],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Get rumors that would be relevant to the current dialogue context.
        
        Args:
            character_id: ID of the character whose known rumors to check
            context: The dialogue context to check relevance against
            limit: Maximum number of rumors to return
            
        Returns:
            List of relevant rumors
        """
        # Get all rumors known by the character
        rumors = self.rumor_manager.get_character_known_rumors(character_id)
        
        if not rumors:
            return []
        
        # Extract topics from context
        topics = self._extract_topics_from_context(context)
        
        # Filter and sort rumors by relevance to context
        relevant_rumors = []
        for rumor in rumors:
            relevance = self._calculate_rumor_relevance(rumor, topics, context)
            relevant_rumors.append({
                "rumor": rumor,
                "relevance": relevance
            })
        
        # Sort by relevance (most relevant first)
        relevant_rumors.sort(key=lambda x: x["relevance"], reverse=True)
        
        # Return the top rumors (up to limit)
        return [r["rumor"] for r in relevant_rumors[:limit]]
    
    def spread_rumor_via_dialogue(
        self,
        rumor_id: str,
        speaker_id: str,
        listener_id: str,
        belief_modifier: float = 0.0
    ) -> bool:
        """
        Spread a rumor from one character to another through dialogue.
        
        Args:
            rumor_id: ID of the rumor to spread
            speaker_id: ID of the character spreading the rumor
            listener_id: ID of the character hearing the rumor
            belief_modifier: Optional modifier to default belief probability
            
        Returns:
            True if rumor was successfully spread, False otherwise
        """
        try:
            # Attempt to spread the rumor
            result = self.rumor_manager.spread_rumor(
                rumor_id=rumor_id,
                from_character_id=speaker_id,
                to_character_id=listener_id,
                spread_method="dialogue",
                belief_modifier=belief_modifier
            )
            
            if result:
                logger.debug(f"Rumor {rumor_id} spread from {speaker_id} to {listener_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to spread rumor {rumor_id}: {e}")
            return False
    
    def _evaluate_rumor_potential(self, message: str) -> float:
        """
        Evaluate the potential of a message becoming a rumor.
        
        Args:
            message: Content of the message
            
        Returns:
            Score between 0.0 and 1.0 representing rumor potential
        """
        # In a real implementation, this would use more sophisticated NLP techniques
        # For now, we'll use a keyword-based approach
        
        # Base score based on message length
        base_score = min(0.3 + (len(message) / 300), 0.5)
        
        # Check for rumor keywords
        rumor_keywords = [
            "secret", "hidden", "discovered", "mysterious", "strange",
            "unusual", "suspicious", "rumor", "heard", "they say",
            "legend", "myth", "whisper", "gossip", "supposedly",
            "apparently", "allegedly", "claim", "believe", "conspiracy"
        ]
        
        keyword_score = 0.0
        for keyword in rumor_keywords:
            if keyword in message.lower():
                keyword_score += 0.1
                
        # Cap at 1.0
        return min(base_score + keyword_score, 1.0)
    
    def _extract_rumor_content(self, message: str) -> str:
        """
        Extract the part of a message that could form a rumor.
        
        Args:
            message: Content of the message
            
        Returns:
            Extracted rumor content or None if no good content found
        """
        # In a real implementation, this would use NLP for better extraction
        
        # Look for common rumor-starter phrases
        rumor_starters = [
            "I heard that", "They say that", "Rumor has it", 
            "Did you know that", "Have you heard", "People are saying",
            "Word is that", "According to", "There's talk of",
            "It's said that", "Supposedly", "Apparently",
            "There's a rumor"
        ]
        
        for starter in rumor_starters:
            lower_message = message.lower()
            lower_starter = starter.lower()
            
            if lower_starter in lower_message:
                # Extract the content after the starter phrase
                start_index = lower_message.find(lower_starter) + len(lower_starter)
                content = message[start_index:].strip()
                
                # Remove trailing punctuation
                if content and content[-1] in ['.', '!', '?']:
                    content = content[:-1]
                    
                # Check if content is long enough to be a meaningful rumor
                if len(content) > 10:
                    return content
        
        # If no starter phrases found, return None
        return None
    
    def _determine_veracity(self, message: str) -> float:
        """
        Determine the likely veracity of a potential rumor.
        
        Args:
            message: Content of the message
            
        Returns:
            Score between 0.0 and 1.0 representing likely truth
        """
        # In a real implementation, this would be more sophisticated
        # For now, we'll randomize with some keyword influence
        
        # Start with a random baseline
        veracity = random.uniform(0.3, 0.7)
        
        # Modify based on certainty keywords
        certainty_keywords = {
            "definitely": 0.2,
            "certainly": 0.2,
            "absolutely": 0.2,
            "without doubt": 0.2,
            "surely": 0.1,
            "probably": 0.0,
            "perhaps": -0.1,
            "maybe": -0.1,
            "possibly": -0.1,
            "uncertain": -0.2,
            "not sure": -0.2,
            "doubtful": -0.2,
            "unlikely": -0.2
        }
        
        for keyword, modifier in certainty_keywords.items():
            if keyword in message.lower():
                veracity += modifier
                break
        
        # Ensure within [0.0, 1.0] range
        return max(0.0, min(veracity, 1.0))
    
    def _extract_topics_from_context(self, context: Dict[str, Any]) -> Set[str]:
        """
        Extract potential topics from dialogue context.
        
        Args:
            context: The dialogue context
            
        Returns:
            Set of topics extracted from context
        """
        topics = set()
        
        # Extract from recent messages if available
        if "recent_messages" in context and context["recent_messages"]:
            for message in context["recent_messages"]:
                if "content" in message:
                    content = message["content"]
                    words = content.lower().split()
                    for word in words:
                        # Keep only meaningful words (4+ characters)
                        if len(word) >= 4 and word not in ["that", "with", "from", "this", "have", "what", "here", "there"]:
                            topics.add(word)
        
        # Extract from location context if available
        if "location" in context and isinstance(context["location"], dict):
            location_data = context["location"]
            if "name" in location_data:
                topics.add(location_data["name"].lower())
            if "type" in location_data:
                topics.add(location_data["type"].lower())
        
        # Extract from character context if available
        if "target_id" in context and context["target_id"]:
            topics.add(context["target_id"])
        
        return topics
    
    def _calculate_rumor_relevance(
        self,
        rumor: Dict[str, Any],
        topics: Set[str],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate how relevant a rumor is to the current context.
        
        Args:
            rumor: The rumor to evaluate
            topics: Set of topics extracted from context
            context: The full dialogue context
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        # Start with base relevance
        relevance = 0.2
        
        # Check content overlap with topics
        rumor_content = rumor.get("content", "").lower()
        topic_matches = 0
        for topic in topics:
            if topic in rumor_content:
                topic_matches += 1
        
        # Add topic match relevance
        relevance += min(topic_matches * 0.1, 0.5)
        
        # Check location relevance
        context_location = context.get("location_id")
        rumor_location = rumor.get("origin_location_id")
        
        if context_location and rumor_location and context_location == rumor_location:
            relevance += 0.2
        
        # Check character relevance
        if "mentions_character_id" in rumor and context.get("target_id") == rumor["mentions_character_id"]:
            relevance += 0.3
        
        # Freshness bonus for newer rumors
        if "created_at" in rumor:
            # Simplified - would use actual time comparison in real implementation
            relevance += 0.1
        
        # Cap at 1.0
        return min(relevance, 1.0) 