"""
GPT-based intent parsing and entity extraction.
"""

from typing import Dict, Any, List, Optional
import json
import logging
from app.core.utils.gpt.client import GPTClient

logger = logging.getLogger(__name__)

class IntentAnalyzer:
    """Analyzer for user intents and entities using GPT."""
    
    def __init__(self, temperature: float = 0.3):
        """
        Initialize the intent analyzer.
        
        Args:
            temperature: Temperature for GPT responses (0.0 to 1.0)
        """
        self.client = GPTClient(
            model="gpt-4.1",
            temperature=temperature
        )
        
    def analyze_intent(self, text: str) -> Dict[str, Any]:
        """
        Analyze user input to determine intent and action.
        
        Args:
            text: User input text
            
        Returns:
            Dict containing intent analysis
        """
        prompt = (
            f"Analyze the following user input for intent and action:\n{text}\n\n"
            "Respond with a JSON object containing:\n"
            "- primary_intent: The main intent (e.g. attack, move, interact)\n"
            "- action_type: Specific action being attempted\n"
            "- target: Target of the action if any\n"
            "- modifiers: Any modifying information"
        )
        
        try:
            response = self.client.call(
                system_prompt="You are an intent analyzer for a fantasy RPG game.",
                user_prompt=prompt,
                max_tokens=100
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Failed to analyze intent: {str(e)}")
            return {
                "error": f"Failed to analyze intent: {e}",
                "primary_intent": "unknown",
                "action_type": "none",
                "target": None,
                "modifiers": {}
            }
            
    def extract_entities(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to analyze
            entity_types: Optional list of entity types to extract
            
        Returns:
            Dict mapping entity types to lists of extracted entities
        """
        entity_types = entity_types or ["character", "location", "item", "action"]
        types_str = ", ".join(entity_types)
        
        prompt = (
            f"Extract the following entity types from the text: {types_str}\n\n"
            f"Text: {text}\n\n"
            "Respond with a JSON object mapping entity types to lists of extracted entities."
        )
        
        try:
            response = self.client.call(
                system_prompt="You are an entity extractor for a fantasy RPG game.",
                user_prompt=prompt,
                max_tokens=150
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Failed to extract entities: {str(e)}")
            return {entity_type: [] for entity_type in entity_types}
            
    def parse_command(self, text: str) -> Dict[str, Any]:
        """
        Parse a user command into structured data.
        
        Args:
            text: User command text
            
        Returns:
            Dict containing parsed command data
        """
        prompt = (
            f"Parse the following user command into structured data:\n{text}\n\n"
            "Respond with a JSON object containing:\n"
            "- command: The base command being attempted\n"
            "- args: List of command arguments\n"
            "- flags: Dict of command flags/options\n"
            "- target: Primary target of the command"
        )
        
        try:
            response = self.client.call(
                system_prompt="You are a command parser for a fantasy RPG game.",
                user_prompt=prompt,
                max_tokens=100
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Failed to parse command: {str(e)}")
            return {
                "error": f"Failed to parse command: {e}",
                "command": "unknown",
                "args": [],
                "flags": {},
                "target": None
            } 