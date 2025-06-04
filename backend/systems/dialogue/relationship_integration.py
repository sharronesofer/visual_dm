"""
Relationship integration for the dialogue system.

This module provides functionality for connecting dialogue with the Relationship system,
allowing dialogue to reference and be influenced by character relationships, personal
history, and interpersonal dynamics.
"""

from typing import Dict, Any, List, Optional, Set
import logging

# Import relationship system components
from backend.systems.characters.relationship_manager import RelationshipManager
from backend.systems.characters.character_manager import CharacterManager

# Configure logger
logger = logging.getLogger(__name__)


class DialogueRelationshipIntegration:
    """
    Integration between dialogue and relationship systems.
    
    Allows dialogue to reference and be influenced by character relationships,
    personal history, and interpersonal dynamics.
    """
    
    def __init__(self, relationship_manager=None, character_manager=None):
        """
        Initialize the dialogue relationship integration.
        
        Args:
            relationship_manager: Optional relationship manager instance
            character_manager: Optional character manager instance
        """
        self.relationship_manager = relationship_manager or RelationshipManager.get_instance()
        self.character_manager = character_manager or CharacterManager.get_instance()
    
    def add_relationship_context_to_dialogue(
        self,
        context: Dict[str, Any],
        character1_id: str,
        character2_id: str,
        include_history: bool = True,
        include_network: bool = False,
        network_depth: int = 1
    ) -> Dict[str, Any]:
        """
        Add relationship information to dialogue context.
        
        Args:
            context: The existing dialogue context
            character1_id: ID of the first character
            character2_id: ID of the second character
            include_history: Whether to include relationship history
            include_network: Whether to include relationship network
            network_depth: Depth of relationship network to include
            
        Returns:
            Updated context with relationship information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create relationship context if it doesn't exist
        if "relationships" not in updated_context:
            updated_context["relationships"] = {}
            
        # Get direct relationship
        relationship = self._get_relationship_info(character1_id, character2_id)
        
        if relationship:
            updated_context["relationships"]["direct"] = relationship
            
            # Add relationship history if requested
            if include_history:
                history = self._get_relationship_history(character1_id, character2_id)
                
                if history:
                    updated_context["relationships"]["history"] = history
            
            # Add relationship network if requested
            if include_network:
                network = self._get_relationship_network(
                    character1_id, 
                    character2_id,
                    depth=network_depth
                )
                
                if network:
                    updated_context["relationships"]["network"] = network
        
        # Add relationship status description
        status = relationship.get("status", "neutral")
        updated_context["relationships"]["status_description"] = self._get_relationship_status_description(status)
        
        return updated_context
    
    def get_relationship_dialogue_modifiers(
        self,
        character1_id: str,
        character2_id: str
    ) -> Dict[str, float]:
        """
        Get dialogue modifiers based on relationship.
        
        Args:
            character1_id: ID of the first character (speaker)
            character2_id: ID of the second character (listener)
            
        Returns:
            Dictionary with dialogue modifiers based on relationship
        """
        try:
            # Get relationship
            relationship = self._get_relationship_info(character1_id, character2_id)
            
            if not relationship:
                # Default neutral modifiers
                return {
                    "formality": 0.0,
                    "openness": 0.0,
                    "friendliness": 0.0,
                    "empathy": 0.0,
                    "respect": 0.0
                }
                
            # Get modifiers based on relationship status
            status = relationship.get("status", "neutral")
            disposition = relationship.get("disposition", 0)
            trust = relationship.get("trust", 0)
            history_length = relationship.get("relationship_duration", 0)
            
            # Base modifiers
            modifiers = {
                "formality": 0.0,
                "openness": 0.0,
                "friendliness": 0.0,
                "empathy": 0.0,
                "respect": 0.0
            }
            
            # Apply status-based modifiers
            if status == "intimate":
                modifiers["formality"] = -0.6  # Much less formal
                modifiers["openness"] = 0.8    # Very open
                modifiers["friendliness"] = 0.9 # Very friendly
                modifiers["empathy"] = 0.8     # High empathy
                modifiers["respect"] = 0.7     # High respect
            elif status == "friendly":
                modifiers["formality"] = -0.3  # Less formal
                modifiers["openness"] = 0.5    # Fairly open
                modifiers["friendliness"] = 0.7 # Quite friendly
                modifiers["empathy"] = 0.5     # Moderate empathy
                modifiers["respect"] = 0.5     # Moderate respect
            elif status == "cordial":
                modifiers["formality"] = 0.1   # Slightly formal
                modifiers["openness"] = 0.2    # Somewhat open
                modifiers["friendliness"] = 0.4 # Somewhat friendly
                modifiers["empathy"] = 0.3     # Some empathy
                modifiers["respect"] = 0.4     # Some respect
            elif status == "neutral":
                # Default neutral modifiers
                pass
            elif status == "cold":
                modifiers["formality"] = 0.4   # More formal
                modifiers["openness"] = -0.3   # Not very open
                modifiers["friendliness"] = -0.4 # Not friendly
                modifiers["empathy"] = -0.2    # Limited empathy
                modifiers["respect"] = 0.0     # Neutral respect
            elif status == "hostile":
                modifiers["formality"] = 0.6   # Very formal
                modifiers["openness"] = -0.6   # Closed off
                modifiers["friendliness"] = -0.8 # Unfriendly
                modifiers["empathy"] = -0.5    # Low empathy
                modifiers["respect"] = -0.5    # Low respect
            
            # Adjust based on disposition and trust
            disposition_factor = disposition / 100.0  # Normalize to -1.0 to 1.0
            trust_factor = trust / 100.0  # Normalize to -1.0 to 1.0
            
            modifiers["friendliness"] += disposition_factor * 0.3
            modifiers["openness"] += trust_factor * 0.4
            modifiers["respect"] += (disposition_factor * 0.2 + trust_factor * 0.2)
            
            # Adjust based on relationship duration
            if history_length > 365:  # Long relationship (more than a year)
                modifiers["formality"] -= 0.2  # Less formal with time
                modifiers["openness"] += 0.2   # More open with time
            
            # Ensure values are within range -1.0 to 1.0
            for key in modifiers:
                modifiers[key] = max(-1.0, min(1.0, modifiers[key]))
            
            return modifiers
            
        except Exception as e:
            logger.error(f"Error getting relationship dialogue modifiers: {e}")
            # Return default neutral modifiers
            return {
                "formality": 0.0,
                "openness": 0.0,
                "friendliness": 0.0,
                "empathy": 0.0,
                "respect": 0.0
            }
    
    def get_relationship_specific_greetings(
        self,
        character1_id: str,
        character2_id: str,
        count: int = 3
    ) -> List[str]:
        """
        Get relationship-specific greetings.
        
        Args:
            character1_id: ID of the first character (speaker)
            character2_id: ID of the second character (listener)
            count: Number of greeting options to return
            
        Returns:
            List of relationship-appropriate greetings
        """
        try:
            # Get relationship
            relationship = self._get_relationship_info(character1_id, character2_id)
            
            if not relationship:
                # Default neutral greetings
                return [
                    "Hello there.",
                    "Greetings.",
                    "Good day to you."
                ]
                
            # Get relationship status
            status = relationship.get("status", "neutral")
            
            # Get character names for personalization
            character1 = self.character_manager.get_character(character1_id)
            character2 = self.character_manager.get_character(character2_id)
            
            char1_name = character1.get("name", "stranger") if character1 else "stranger"
            char2_name = character2.get("name", "stranger") if character2 else "stranger"
            
            # Greetings based on relationship status
            greetings = {
                "intimate": [
                    f"My dearest {char2_name}! It's so good to see you!",
                    f"{char2_name}! I was just thinking about you.",
                    f"There you are! I've been looking forward to seeing you, {char2_name}."
                ],
                "friendly": [
                    f"Hey {char2_name}! How have you been?",
                    f"Good to see you, {char2_name}! What's new?",
                    f"{char2_name}! Nice to run into you."
                ],
                "cordial": [
                    f"Hello, {char2_name}. Hope you're well today.",
                    f"Good day, {char2_name}.",
                    f"Ah, {char2_name}. How do you do?"
                ],
                "neutral": [
                    f"Hello there.",
                    f"Greetings.",
                    f"Good day to you."
                ],
                "cold": [
                    f"Oh. It's you.",
                    f"{char2_name}.",
                    f"I see you're here."
                ],
                "hostile": [
                    f"What do you want?",
                    f"I have nothing to say to you.",
                    f"*glares silently*"
                ]
            }
            
            # Get greetings for the relationship status
            status_greetings = greetings.get(status, greetings["neutral"])
            
            # Personalize based on additional relationship factors
            if relationship.get("is_family", False):
                family_relation = relationship.get("family_relation", "relative")
                family_greetings = [
                    f"Hello, {family_relation}!",
                    f"Good to see you, {family_relation}.",
                    f"There you are, {family_relation}."
                ]
                status_greetings.extend(family_greetings)
            
            if relationship.get("events", []):
                recent_event = relationship.get("events", [])[0] if relationship.get("events") else None
                if recent_event and recent_event.get("type") == "positive":
                    status_greetings.append(f"Hello {char2_name}! I'm still thinking about {recent_event.get('description', 'our time together')}.")
            
            # Return the requested number of greetings
            return status_greetings[:count]
            
        except Exception as e:
            logger.error(f"Error getting relationship-specific greetings: {e}")
            # Return default neutral greetings
            return [
                "Hello there.",
                "Greetings.",
                "Good day to you."
            ]
    
    def get_relationship_specific_farewells(
        self,
        character1_id: str,
        character2_id: str,
        count: int = 3
    ) -> List[str]:
        """
        Get relationship-specific farewells.
        
        Args:
            character1_id: ID of the first character (speaker)
            character2_id: ID of the second character (listener)
            count: Number of farewell options to return
            
        Returns:
            List of relationship-appropriate farewells
        """
        try:
            # Get relationship
            relationship = self._get_relationship_info(character1_id, character2_id)
            
            if not relationship:
                # Default neutral farewells
                return [
                    "Goodbye.",
                    "Farewell.",
                    "Until next time."
                ]
                
            # Get relationship status
            status = relationship.get("status", "neutral")
            
            # Get character names for personalization
            character1 = self.character_manager.get_character(character1_id)
            character2 = self.character_manager.get_character(character2_id)
            
            char1_name = character1.get("name", "stranger") if character1 else "stranger"
            char2_name = character2.get("name", "stranger") if character2 else "stranger"
            
            # Farewells based on relationship status
            farewells = {
                "intimate": [
                    f"Take care, my dear {char2_name}. I'll miss you.",
                    f"Farewell for now, {char2_name}. Can't wait to see you again!",
                    f"Until next time, {char2_name}. Don't be a stranger!"
                ],
                "friendly": [
                    f"See you around, {char2_name}! Take care!",
                    f"Goodbye, {char2_name}! Always good talking with you.",
                    f"Until next time, {char2_name}!"
                ],
                "cordial": [
                    f"Good day, {char2_name}. Take care.",
                    f"Farewell, {char2_name}. Until our paths cross again.",
                    f"Goodbye, {char2_name}. Pleasant journeys."
                ],
                "neutral": [
                    f"Goodbye.",
                    f"Farewell.",
                    f"Until next time."
                ],
                "cold": [
                    f"I must be going now.",
                    f"That's all for now.",
                    f"We're done here."
                ],
                "hostile": [
                    f"I hope I don't see you again anytime soon.",
                    f"Finally, I can leave.",
                    f"*turns away without a word*"
                ]
            }
            
            # Get farewells for the relationship status
            status_farewells = farewells.get(status, farewells["neutral"])
            
            # Personalize based on additional relationship factors
            if relationship.get("is_family", False):
                family_relation = relationship.get("family_relation", "relative")
                family_farewells = [
                    f"Goodbye, {family_relation}. Take care of yourself.",
                    f"Farewell, {family_relation}. See you at home.",
                    f"Until later, {family_relation}."
                ]
                status_farewells.extend(family_farewells)
            
            if relationship.get("next_meeting_context"):
                next_meeting = relationship.get("next_meeting_context")
                status_farewells.append(f"Goodbye, {char2_name}. I'll see you at {next_meeting}.")
            
            # Return the requested number of farewells
            return status_farewells[:count]
            
        except Exception as e:
            logger.error(f"Error getting relationship-specific farewells: {e}")
            # Return default neutral farewells
            return [
                "Goodbye.",
                "Farewell.",
                "Until next time."
            ]
    
    def get_relationship_dialogue_topics(
        self,
        character1_id: str,
        character2_id: str,
        count: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get potential dialogue topics based on relationship.
        
        Args:
            character1_id: ID of the first character
            character2_id: ID of the second character
            count: Number of topics to return
            
        Returns:
            List of potential dialogue topics
        """
        try:
            # Get relationship
            relationship = self._get_relationship_info(character1_id, character2_id)
            
            if not relationship:
                # Default neutral topics
                return [
                    {"topic": "weather", "relevance": "neutral", "description": "Current weather conditions"},
                    {"topic": "local_events", "relevance": "neutral", "description": "Recent happenings in the area"},
                    {"topic": "general_news", "relevance": "neutral", "description": "General news and gossip"}
                ]
                
            # Get character names for personalization
            character1 = self.character_manager.get_character(character1_id)
            character2 = self.character_manager.get_character(character2_id)
            
            # Build topics based on relationship information
            topics = []
            
            # Add shared history topics
            events = relationship.get("events", [])
            for event in events[:2]:  # Use up to 2 most recent events
                event_desc = event.get("description", "")
                if event_desc:
                    topics.append({
                        "topic": "shared_experience",
                        "relevance": "high",
                        "description": f"Shared experience: {event_desc}",
                        "context": event
                    })
            
            # Add shared connections
            connections = relationship.get("shared_connections", [])
            if connections:
                for connection in connections[:2]:  # Use up to 2 shared connections
                    connection_name = connection.get("name", "someone")
                    topics.append({
                        "topic": "shared_connection",
                        "relevance": "medium",
                        "description": f"Discussion about mutual acquaintance: {connection_name}",
                        "context": connection
                    })
            
            # Add topics based on relationship status
            status = relationship.get("status", "neutral")
            if status in ["intimate", "friendly"]:
                # Personal topics for close relationships
                if character1:
                    personal_topics = character1.get("personal_topics", [])
                    for topic in personal_topics[:2]:
                        topics.append({
                            "topic": "personal",
                            "relevance": "high",
                            "description": f"Personal topic: {topic}",
                            "context": {"topic": topic}
                        })
                
                # Add family topics if relevant
                if relationship.get("is_family", False):
                    topics.append({
                        "topic": "family",
                        "relevance": "high",
                        "description": "Family matters and concerns",
                        "context": {"family_relation": relationship.get("family_relation", "relative")}
                    })
            
            # Add topics based on recent interactions
            interaction_history = relationship.get("recent_interactions", [])
            if interaction_history:
                latest_interaction = interaction_history[0]
                topics.append({
                    "topic": "follow_up",
                    "relevance": "high",
                    "description": f"Follow-up on previous conversation: {latest_interaction.get('topic', 'previous discussion')}",
                    "context": latest_interaction
                })
            
            # Add topics based on character interests (if status is at least cordial)
            if status not in ["cold", "hostile"]:
                if character2:
                    interests = character2.get("interests", [])
                    for interest in interests[:2]:
                        topics.append({
                            "topic": "interest",
                            "relevance": "medium",
                            "description": f"Discussion about {character2.get('name', 'their')} interest: {interest}",
                            "context": {"interest": interest}
                        })
            
            # Add default topics to fill out the list
            default_topics = [
                {"topic": "weather", "relevance": "low", "description": "Current weather conditions"},
                {"topic": "local_events", "relevance": "medium", "description": "Recent happenings in the area"},
                {"topic": "general_news", "relevance": "medium", "description": "General news and gossip"}
            ]
            
            topics.extend(default_topics)
            
            # Sort by relevance and return requested count
            topics.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x.get("relevance", "low"), 0), reverse=True)
            return topics[:count]
            
        except Exception as e:
            logger.error(f"Error getting relationship dialogue topics: {e}")
            # Return default neutral topics
            return [
                {"topic": "weather", "relevance": "neutral", "description": "Current weather conditions"},
                {"topic": "local_events", "relevance": "neutral", "description": "Recent happenings in the area"},
                {"topic": "general_news", "relevance": "neutral", "description": "General news and gossip"}
            ]
    
    def update_relationship_from_dialogue(
        self,
        character1_id: str,
        character2_id: str,
        dialogue_data: Dict[str, Any],
        event_type: str = "conversation"
    ) -> bool:
        """
        Update relationship based on dialogue interaction.
        
        Args:
            character1_id: ID of the first character
            character2_id: ID of the second character
            dialogue_data: Dictionary with dialogue data
            event_type: Type of dialogue event
            
        Returns:
            True if successfully updated, False otherwise
        """
        try:
            # Determine relationship changes based on dialogue
            sentiment = dialogue_data.get("sentiment", 0)  # -1.0 to 1.0
            dialogue_topics = dialogue_data.get("topics", [])
            
            # Calculate disposition and trust changes
            disposition_change = int(sentiment * 5)  # Scale to roughly -5 to +5
            trust_change = int(sentiment * 3)  # Scale to roughly -3 to +3
            
            # Adjust based on topic sensitivity
            sensitive_topics = dialogue_data.get("sensitive_topics", [])
            if sensitive_topics:
                # Sensitive topics can have a larger impact
                if sentiment > 0:
                    trust_change += 2  # Additional trust gain for positive discussion of sensitive topics
                else:
                    trust_change -= 1  # Additional trust loss for negative discussion of sensitive topics
            
            # Update the relationship
            update_data = {
                "disposition_change": disposition_change,
                "trust_change": trust_change,
                "add_event": {
                    "type": event_type,
                    "description": dialogue_data.get("summary", "Had a conversation"),
                    "sentiment": sentiment,
                    "topics": dialogue_topics
                }
            }
            
            success = self.relationship_manager.update_relationship(
                character1_id=character1_id,
                character2_id=character2_id,
                update_data=update_data
            )
            
            if success:
                logger.debug(f"Updated relationship between {character1_id} and {character2_id} based on dialogue")
            else:
                logger.warning(f"Failed to update relationship between {character1_id} and {character2_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating relationship from dialogue: {e}")
            return False
    
    def _get_relationship_info(
        self,
        character1_id: str,
        character2_id: str
    ) -> Dict[str, Any]:
        """
        Get information about a relationship for dialogue context.
        
        Args:
            character1_id: ID of the first character
            character2_id: ID of the second character
            
        Returns:
            Dictionary with relationship information
        """
        try:
            # Get the relationship
            relationship = self.relationship_manager.get_relationship(
                character1_id=character1_id,
                character2_id=character2_id
            )
            
            if not relationship:
                logger.warning(f"No relationship found between {character1_id} and {character2_id}")
                return {}
                
            # Format for dialogue
            relationship_info = {
                "character1_id": character1_id,
                "character2_id": character2_id,
                "status": relationship.get("status", "neutral"),
                "disposition": relationship.get("disposition", 0),
                "trust": relationship.get("trust", 0),
                "is_family": relationship.get("is_family", False),
                "family_relation": relationship.get("family_relation", ""),
                "relationship_duration": relationship.get("duration", 0),  # Days
                "tags": relationship.get("tags", []),
                "events": relationship.get("events", [])[:3],  # Just the most recent 3
                "shared_connections": relationship.get("shared_connections", []),
                "last_interaction": relationship.get("last_interaction")
            }
            
            return relationship_info
            
        except Exception as e:
            logger.error(f"Error getting relationship info for '{character1_id}' and '{character2_id}': {e}")
            return {}
    
    def _get_relationship_history(
        self,
        character1_id: str,
        character2_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get history of a relationship for dialogue context.
        
        Args:
            character1_id: ID of the first character
            character2_id: ID of the second character
            limit: Maximum number of events to include
            
        Returns:
            List of relationship history events
        """
        try:
            # Get the relationship history
            history = self.relationship_manager.get_relationship_history(
                character1_id=character1_id,
                character2_id=character2_id,
                limit=limit
            )
            
            if not history:
                return []
                
            # Format for dialogue
            formatted_history = []
            for event in history:
                formatted_event = {
                    "type": event.get("type", "event"),
                    "description": event.get("description", ""),
                    "timestamp": event.get("timestamp", ""),
                    "sentiment": event.get("sentiment", 0)
                }
                formatted_history.append(formatted_event)
            
            return formatted_history
            
        except Exception as e:
            logger.error(f"Error getting relationship history for '{character1_id}' and '{character2_id}': {e}")
            return []
    
    def _get_relationship_network(
        self,
        character1_id: str,
        character2_id: str,
        depth: int = 1
    ) -> Dict[str, Any]:
        """
        Get relationship network for dialogue context.
        
        Args:
            character1_id: ID of the first character
            character2_id: ID of the second character
            depth: Depth of network to include
            
        Returns:
            Dictionary with relationship network information
        """
        try:
            # Get the relationship network
            network = self.relationship_manager.get_relationship_network(
                character1_id=character1_id,
                character2_id=character2_id,
                depth=depth
            )
            
            if not network:
                return {}
                
            # Format for dialogue
            formatted_network = {
                "shared_connections": network.get("shared_connections", []),
                "mutual_friends": network.get("mutual_friends", []),
                "mutual_enemies": network.get("mutual_enemies", []),
                "character1_connections": network.get("character1_connections", [])[:3],  # Limit to 3
                "character2_connections": network.get("character2_connections", [])[:3]  # Limit to 3
            }
            
            return formatted_network
            
        except Exception as e:
            logger.error(f"Error getting relationship network for '{character1_id}' and '{character2_id}': {e}")
            return {}
    
    def _get_relationship_status_description(
        self,
        status: str
    ) -> str:
        """
        Get a description for a relationship status.
        
        Args:
            status: The relationship status
            
        Returns:
            Description of the relationship status
        """
        descriptions = {
            "intimate": "There is a deep bond of intimacy and trust between them.",
            "friendly": "They share a warm and friendly relationship.",
            "cordial": "They maintain a polite and cordial relationship.",
            "neutral": "Their relationship is neither particularly friendly nor unfriendly.",
            "cold": "There is a noticeable coldness in their interactions.",
            "hostile": "Their relationship is marked by open hostility and antagonism."
        }
        
        return descriptions.get(status, "Their relationship status is unclear.") 