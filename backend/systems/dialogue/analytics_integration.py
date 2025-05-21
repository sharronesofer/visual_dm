"""
Analytics integration for the dialogue system.

This module provides functionality for connecting dialogue with the Analytics systems,
allowing for logging dialogue events, tracking metrics, and collecting data for
LLM training and system improvement.
"""

from typing import Dict, Any, List, Optional, Set
import logging
from datetime import datetime
import json
import os

# Import analytics system components
from backend.systems.analytics.analytics_manager import AnalyticsManager
from backend.systems.analytics.event_logger import EventLogger

# Configure logger
logger = logging.getLogger(__name__)


class DialogueAnalyticsIntegration:
    """
    Integration between dialogue and analytics systems.
    
    Allows for logging dialogue events, tracking metrics, and collecting data
    for LLM training and system improvement.
    """
    
    def __init__(self, analytics_manager=None, event_logger=None):
        """
        Initialize the dialogue analytics integration.
        
        Args:
            analytics_manager: Optional analytics manager instance
            event_logger: Optional event logger instance
        """
        self.analytics_manager = analytics_manager or AnalyticsManager.get_instance()
        self.event_logger = event_logger or EventLogger.get_instance()
        
        # Initialize dialogue-specific analytics storage
        self.dialogue_metrics = {
            "total_interactions": 0,
            "total_player_responses": 0,
            "response_categories": {},
            "topic_counts": {},
            "character_interactions": {}
        }
    
    def log_dialogue_event(
        self,
        event_type: str,
        dialogue_data: Dict[str, Any],
        player_id: Optional[str] = None,
        character_id: Optional[str] = None,
        location_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log a dialogue event to the analytics system.
        
        Args:
            event_type: Type of dialogue event ('start', 'response', 'end', etc.)
            dialogue_data: Dictionary with dialogue event data
            player_id: Optional player ID
            character_id: Optional character ID
            location_id: Optional location ID
            metadata: Optional additional metadata
            
        Returns:
            True if successfully logged, False otherwise
        """
        try:
            # Create event data
            event_data = {
                "event_type": f"dialogue_{event_type}",
                "timestamp": datetime.utcnow().isoformat(),
                "dialogue_data": dialogue_data,
                "player_id": player_id,
                "character_id": character_id,
                "location_id": location_id
            }
            
            # Add metadata if provided
            if metadata:
                event_data["metadata"] = metadata
            
            # Log the event
            success = self.event_logger.log_event(
                category="dialogue",
                event_data=event_data
            )
            
            if success:
                logger.debug(f"Logged dialogue {event_type} event")
                self._update_dialogue_metrics(event_type, dialogue_data, character_id)
            else:
                logger.warning(f"Failed to log dialogue {event_type} event")
            
            return success
            
        except Exception as e:
            logger.error(f"Error logging dialogue event: {e}")
            return False
    
    def export_dialogue_for_training(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 1000,
        export_path: Optional[str] = None
    ) -> str:
        """
        Export dialogue data for LLM training.
        
        Args:
            start_time: Optional start time for filtering (ISO format)
            end_time: Optional end time for filtering (ISO format)
            limit: Maximum number of dialogues to export
            export_path: Optional path to export the data
            
        Returns:
            Path to the exported file
        """
        try:
            # Query dialogue events
            filters = {
                "category": "dialogue",
                "event_types": ["dialogue_start", "dialogue_response", "dialogue_end"],
                "start_time": start_time,
                "end_time": end_time,
                "limit": limit
            }
            
            events = self.event_logger.query_events(filters)
            
            # Group events by conversation ID
            conversations = {}
            for event in events:
                conversation_id = event.get("dialogue_data", {}).get("conversation_id")
                if not conversation_id:
                    continue
                    
                if conversation_id not in conversations:
                    conversations[conversation_id] = []
                    
                conversations[conversation_id].append(event)
            
            # Format conversations for training
            training_data = []
            for conversation_id, events in conversations.items():
                # Sort events by timestamp
                events.sort(key=lambda e: e.get("timestamp", ""))
                
                # Extract dialogue turns
                turns = []
                for event in events:
                    event_type = event.get("event_type")
                    
                    if event_type == "dialogue_response":
                        dialogue_data = event.get("dialogue_data", {})
                        speaker = dialogue_data.get("speaker", "unknown")
                        text = dialogue_data.get("text", "")
                        
                        if text:
                            turns.append({
                                "speaker": speaker,
                                "text": text
                            })
                
                # Only include conversations with at least 2 turns
                if len(turns) >= 2:
                    training_sample = {
                        "conversation_id": conversation_id,
                        "turns": turns,
                        "metadata": {
                            "character_id": events[0].get("character_id"),
                            "location_id": events[0].get("location_id"),
                            "timestamp": events[0].get("timestamp")
                        }
                    }
                    training_data.append(training_sample)
            
            # Export to file
            if not export_path:
                export_dir = "data/analytics/dialogue_exports"
                os.makedirs(export_dir, exist_ok=True)
                export_path = f"{export_dir}/dialogue_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(export_path, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            logger.info(f"Exported {len(training_data)} dialogues to {export_path}")
            return export_path
            
        except Exception as e:
            logger.error(f"Error exporting dialogue for training: {e}")
            default_path = "data/analytics/dialogue_exports/dialogue_export_error.json"
            return default_path
    
    def track_dialogue_topic(
        self,
        topic: str,
        subtopics: Optional[List[str]] = None,
        player_id: Optional[str] = None,
        character_id: Optional[str] = None
    ) -> bool:
        """
        Track dialogue topic for analytics.
        
        Args:
            topic: Main topic of the dialogue
            subtopics: Optional list of subtopics
            player_id: Optional player ID
            character_id: Optional character ID
            
        Returns:
            True if successfully tracked, False otherwise
        """
        try:
            # Create topic data
            topic_data = {
                "topic": topic,
                "subtopics": subtopics or [],
                "timestamp": datetime.utcnow().isoformat(),
                "player_id": player_id,
                "character_id": character_id
            }
            
            # Log the topic event
            success = self.event_logger.log_event(
                category="dialogue_topics",
                event_data=topic_data
            )
            
            if success:
                logger.debug(f"Tracked dialogue topic: {topic}")
                
                # Update topic metrics
                if topic not in self.dialogue_metrics["topic_counts"]:
                    self.dialogue_metrics["topic_counts"][topic] = 0
                    
                self.dialogue_metrics["topic_counts"][topic] += 1
            else:
                logger.warning(f"Failed to track dialogue topic: {topic}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error tracking dialogue topic: {e}")
            return False
    
    def log_player_response_choice(
        self,
        player_id: str,
        character_id: str,
        conversation_id: str,
        options: List[Dict[str, Any]],
        chosen_option_index: int,
        response_time: Optional[float] = None
    ) -> bool:
        """
        Log player's dialogue response choice.
        
        Args:
            player_id: ID of the player
            character_id: ID of the character in conversation
            conversation_id: ID of the conversation
            options: List of dialogue options presented
            chosen_option_index: Index of the option chosen
            response_time: Optional time taken to respond (seconds)
            
        Returns:
            True if successfully logged, False otherwise
        """
        try:
            # Get the chosen option
            chosen_option = options[chosen_option_index] if 0 <= chosen_option_index < len(options) else None
            
            # Create response data
            response_data = {
                "conversation_id": conversation_id,
                "player_id": player_id,
                "character_id": character_id,
                "options": options,
                "chosen_option_index": chosen_option_index,
                "chosen_option": chosen_option,
                "response_time": response_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log the response event
            success = self.event_logger.log_event(
                category="player_responses",
                event_data=response_data
            )
            
            if success:
                logger.debug(f"Logged player response choice for conversation {conversation_id}")
                
                # Update response metrics
                self.dialogue_metrics["total_player_responses"] += 1
                
                # Track response by category if available
                if chosen_option and "category" in chosen_option:
                    category = chosen_option["category"]
                    if category not in self.dialogue_metrics["response_categories"]:
                        self.dialogue_metrics["response_categories"][category] = 0
                        
                    self.dialogue_metrics["response_categories"][category] += 1
            else:
                logger.warning(f"Failed to log player response choice for conversation {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error logging player response choice: {e}")
            return False
    
    def track_character_interaction_frequency(
        self,
        player_id: str,
        character_id: str
    ) -> None:
        """
        Track frequency of player interactions with characters.
        
        Args:
            player_id: ID of the player
            character_id: ID of the character
        """
        try:
            # Update character interaction metrics
            if character_id not in self.dialogue_metrics["character_interactions"]:
                self.dialogue_metrics["character_interactions"][character_id] = {
                    "total": 0,
                    "players": {}
                }
            
            self.dialogue_metrics["character_interactions"][character_id]["total"] += 1
            
            if player_id not in self.dialogue_metrics["character_interactions"][character_id]["players"]:
                self.dialogue_metrics["character_interactions"][character_id]["players"][player_id] = 0
                
            self.dialogue_metrics["character_interactions"][character_id]["players"][player_id] += 1
            
            logger.debug(f"Tracked character interaction: Player {player_id} with Character {character_id}")
            
        except Exception as e:
            logger.error(f"Error tracking character interaction frequency: {e}")
    
    def get_dialogue_metrics(
        self,
        metric_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get dialogue metrics for analysis.
        
        Args:
            metric_type: Optional specific metric type to retrieve
            
        Returns:
            Dictionary with dialogue metrics
        """
        try:
            if metric_type:
                if metric_type in self.dialogue_metrics:
                    return {metric_type: self.dialogue_metrics[metric_type]}
                else:
                    logger.warning(f"Unknown metric type: {metric_type}")
                    return {}
            else:
                return self.dialogue_metrics
                
        except Exception as e:
            logger.error(f"Error getting dialogue metrics: {e}")
            return {}
    
    def record_dialogue_quality_rating(
        self,
        conversation_id: str,
        rating: int,
        feedback: Optional[str] = None,
        player_id: Optional[str] = None
    ) -> bool:
        """
        Record player rating of dialogue quality.
        
        Args:
            conversation_id: ID of the conversation
            rating: Numeric rating (typically 1-5)
            feedback: Optional text feedback
            player_id: Optional player ID
            
        Returns:
            True if successfully recorded, False otherwise
        """
        try:
            # Create rating data
            rating_data = {
                "conversation_id": conversation_id,
                "rating": rating,
                "feedback": feedback,
                "player_id": player_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log the rating event
            success = self.event_logger.log_event(
                category="dialogue_ratings",
                event_data=rating_data
            )
            
            if success:
                logger.debug(f"Recorded dialogue quality rating {rating} for conversation {conversation_id}")
            else:
                logger.warning(f"Failed to record dialogue quality rating for conversation {conversation_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error recording dialogue quality rating: {e}")
            return False
    
    def get_player_dialogue_history(
        self,
        player_id: str,
        character_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get player's dialogue history for personalized context.
        
        Args:
            player_id: ID of the player
            character_id: Optional character ID to filter by
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of dialogue conversations
        """
        try:
            # Create filters
            filters = {
                "category": "dialogue",
                "player_id": player_id,
                "limit": limit * 10  # Request more to account for filtering
            }
            
            if character_id:
                filters["character_id"] = character_id
                
            # Get dialogue events
            events = self.event_logger.query_events(filters)
            
            # Group events by conversation ID
            conversations = {}
            for event in events:
                conversation_id = event.get("dialogue_data", {}).get("conversation_id")
                if not conversation_id:
                    continue
                    
                if conversation_id not in conversations:
                    conversations[conversation_id] = []
                    
                conversations[conversation_id].append(event)
            
            # Format dialogue history
            dialogue_history = []
            for conversation_id, events in conversations.items():
                # Sort events by timestamp
                events.sort(key=lambda e: e.get("timestamp", ""))
                
                # Get basic conversation metadata
                first_event = events[0] if events else {}
                metadata = {
                    "conversation_id": conversation_id,
                    "character_id": first_event.get("character_id"),
                    "location_id": first_event.get("location_id"),
                    "timestamp": first_event.get("timestamp"),
                    "topics": []
                }
                
                # Extract dialogue turns
                turns = []
                for event in events:
                    event_type = event.get("event_type")
                    
                    if event_type == "dialogue_response":
                        dialogue_data = event.get("dialogue_data", {})
                        speaker = dialogue_data.get("speaker", "unknown")
                        text = dialogue_data.get("text", "")
                        
                        if text:
                            turns.append({
                                "speaker": speaker,
                                "text": text
                            })
                    
                    # Collect topics if available
                    if event_type == "dialogue_topics":
                        topic = event.get("topic")
                        if topic and topic not in metadata["topics"]:
                            metadata["topics"].append(topic)
                
                dialogue_history.append({
                    "metadata": metadata,
                    "turns": turns
                })
            
            # Sort by timestamp (newest first) and limit the result
            dialogue_history.sort(key=lambda d: d["metadata"]["timestamp"], reverse=True)
            return dialogue_history[:limit]
            
        except Exception as e:
            logger.error(f"Error getting player dialogue history: {e}")
            return []
    
    def _update_dialogue_metrics(
        self,
        event_type: str,
        dialogue_data: Dict[str, Any],
        character_id: Optional[str] = None
    ) -> None:
        """
        Update internal dialogue metrics.
        
        Args:
            event_type: Type of dialogue event
            dialogue_data: Dictionary with dialogue event data
            character_id: Optional character ID
        """
        # Update total interactions
        self.dialogue_metrics["total_interactions"] += 1
        
        # Update other metrics based on event type
        if event_type == "start":
            # Track character interaction if available
            player_id = dialogue_data.get("player_id")
            if player_id and character_id:
                self.track_character_interaction_frequency(player_id, character_id) 