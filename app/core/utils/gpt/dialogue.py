"""
GPT-based dialogue generation for NPCs and characters.
"""

import logging
from typing import Dict, Any, Optional, List
from app.core.utils.gpt.client import GPTClient

logger = logging.getLogger(__name__)

class DialogueGPTClient:
    """Client for generating NPC dialogue using GPT."""
    
    def __init__(self, temperature: float = 0.7):
        """
        Initialize the dialogue client.
        
        Args:
            temperature: Temperature for GPT responses (0.0 to 1.0)
        """
        self.client = GPTClient(
            model="gpt-4.1",
            temperature=temperature
        )
        self.system_prompt = """You are a dialogue generator for a fantasy RPG game. 
Your task is to generate natural, engaging dialogue based on the provided context.
The dialogue should reflect:
1. The NPC's personality and relationship with the character
2. The success or failure of the social interaction
3. The specific skill and application being used
4. The consequences of the interaction

Keep responses concise and focused on the immediate interaction."""

    def generate_dialogue(self, context: Dict[str, Any]) -> str:
        """
        Generate dialogue using GPT based on the provided context.
        
        Args:
            context: Dictionary containing NPC, character, and interaction context
            
        Returns:
            Generated dialogue string
        """
        try:
            # Format the context into a prompt
            prompt = self._format_context_to_prompt(context)
            
            # Call GPT API
            response = self.client.call(
                system_prompt=self.system_prompt,
                user_prompt=prompt,
                max_tokens=150
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating dialogue with GPT: {str(e)}")
            return "I'm sorry, I'm having trouble responding right now."
            
    def generate_description(self, npc: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Generate a description of an NPC based on their current state and context.
        
        Args:
            npc: Dictionary containing NPC data
            context: Dictionary containing current context
            
        Returns:
            Generated description string
        """
        try:
            prompt = f"""NPC: {npc['name']}
Personality: {npc['personality']}
Current State: {npc.get('current_state', 'Unknown')}
Location: {context.get('location', 'Unknown')}
Time of Day: {context.get('time_of_day', 'Unknown')}
Recent Events: {', '.join(context.get('recent_events', []))}

Describe what the character observes about this NPC in their current state and circumstances.
Focus on visual details, body language, and immediate impressions."""

            response = self.client.call(
                system_prompt="You are a fantasy RPG narrator describing NPCs.",
                user_prompt=prompt,
                max_tokens=100
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating NPC description with GPT: {str(e)}")
            return "You see a figure, but can't make out much detail in the current conditions."
            
    def _format_context_to_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format the context into a prompt for GPT.
        
        Args:
            context: Dictionary containing interaction context
            
        Returns:
            Formatted prompt string
        """
        npc = context["npc"]
        character = context["character"]
        interaction = context["interaction"]
        
        prompt = f"""NPC: {npc['name']}
Personality: {npc['personality']}
Relationship: {npc['relationship_status']}
Loyalty: {npc['loyalty']}

Character: {character['name']}
Skills: {', '.join(character['skills'])}

Interaction:
- Skill: {interaction['skill']}
- Application: {interaction['application']}
- Request Difficulty: {interaction['request_difficulty']}
- Circumstances: {interaction['circumstances']}
- Evidence Leverage: {interaction['evidence_leverage']}
- Result: {interaction['result']['degree']}
- Consequence: {interaction['consequence']}

Generate a natural response from the NPC based on this context."""
        
        return prompt 