"""
Enhanced Prompt Manager for Character System
==========================================
Manages prompts for character-related LLM interactions including dialogue,
personality enhancement, and rumor transformation.
Enhanced to work with deterministic fallbacks.
"""

import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BasePromptManager(ABC):
    """Base class for prompt managers with deterministic fallbacks."""
    
    @abstractmethod
    def build_prompt(self, *args, **kwargs) -> str:
        """Build a prompt for LLM interaction."""
        pass
    
    @abstractmethod  
    def get_fallback_response(self, *args, **kwargs) -> str:
        """Get a deterministic fallback response when LLM is unavailable."""
        pass


class CharacterDialoguePromptManager(BasePromptManager):
    """Manages prompts for character dialogue generation."""
    
    def build_prompt(self, character_name: str, personality: str, context: str, 
                    player_input: Optional[str] = None, 
                    conversation_history: Optional[str] = None) -> str:
        """
        Build a prompt for character dialogue generation.
        
        Args:
            character_name: Name of the character
            personality: Personality description
            context: Current situation context
            player_input: What the player said
            conversation_history: Previous conversation
            
        Returns:
            Formatted prompt string
        """
        base_prompt = f"""You are {character_name}, a character with the following personality:

{personality}

Current situation: {context}

"""
        
        if conversation_history:
            base_prompt += f"Previous conversation:\n{conversation_history}\n\n"
        
        if player_input:
            base_prompt += f"The player just said: \"{player_input}\"\n\n"
        
        base_prompt += f"""Respond as {character_name} would, staying true to their personality and the current situation. 
Keep the response natural and in-character. Respond with dialogue only, no action descriptions."""
        
        return base_prompt
    
    def get_fallback_response(self, character_name: str, context: str, **kwargs) -> str:
        """Get a simple fallback dialogue response."""
        fallback_responses = [
            "I'm not sure what to say about that.",
            "That's interesting...",
            "Let me think about that for a moment.",
            "I see what you mean.",
            "That's quite something."
        ]
        import random
        return random.choice(fallback_responses)


class CharacterReactionPromptManager(BasePromptManager):
    """Manages prompts for character reactions to events."""
    
    def build_prompt(self, character_name: str, personality: str, event: str,
                    emotional_impact: str = "moderate") -> str:
        """
        Build a prompt for character event reactions.
        
        Args:
            character_name: Name of the character
            personality: Personality description 
            event: Description of what happened
            emotional_impact: Level of emotional impact
            
        Returns:
            Formatted prompt string
        """
        return f"""You are {character_name}, a character with the following personality:

{personality}

An event has just occurred: {event}

The emotional impact on you is: {emotional_impact}

Describe how {character_name} reacts to this event, both emotionally and behaviorally. 
Keep the response focused on their immediate reaction and any visible emotional response.
Stay true to their personality traits."""
    
    def get_fallback_response(self, character_name: str, event: str, **kwargs) -> str:
        """Get a simple fallback reaction."""
        return f"{character_name} notices what happened and seems to react appropriately to the situation."


class NPCEnhancementPromptManager(BasePromptManager):
    """Manages prompts for LLM-enhanced NPC generation."""
    
    def build_prompt(self, profession: str, race: str, age: int, personality: str,
                    backstory: str, wealth_level: str) -> str:
        """
        Build a prompt for NPC enhancement.
        
        Args:
            profession: Character's profession
            race: Character's race
            age: Character's age
            personality: Personality description
            backstory: Backstory elements
            wealth_level: Economic status
            
        Returns:
            Formatted prompt string
        """
        return f"""Create an enhanced description for an NPC with the following characteristics:

Profession: {profession}
Race: {race}
Age: {age}
Wealth Level: {wealth_level}

Personality Profile:
{personality}

Backstory Elements:
{backstory}

Provide a rich, immersive description that brings this character to life. Include:
- Physical appearance details
- Mannerisms and habits
- Notable possessions or clothing
- How they might be encountered in the world
- Any interesting quirks or details that make them memorable

Keep the description concise but vivid, suitable for a game master to use during play."""
    
    def get_fallback_response(self, profession: str, race: str, age: int, **kwargs) -> str:
        """Get a basic fallback description."""
        return f"A {age}-year-old {race} who works as a {profession}. They have a typical appearance for their profession and seem to approach their work with a practical attitude."


class RumorPromptManager(BasePromptManager):
    """Manages prompts for rumor transformation through character personalities."""
    
    @staticmethod
    def build_prompt(event_context: str, original_rumor: str, personality_traits: str, 
                    distortion_level: float) -> str:
        """
        Build a prompt for rumor transformation based on character personality.
        
        Args:
            event_context: Context about the original event
            original_rumor: The rumor as originally heard
            personality_traits: Character's personality description
            distortion_level: How much to distort (0.0-1.0)
            
        Returns:
            Formatted prompt string
        """
        # Determine distortion guidance based on level
        if distortion_level < 0.2:
            distortion_guidance = "very faithful to the original, with only minor personal perspective"
        elif distortion_level < 0.5:
            distortion_guidance = "somewhat modified with personal interpretation and emphasis"
        elif distortion_level < 0.8:
            distortion_guidance = "significantly altered with personal biases and embellishments"
        else:
            distortion_guidance = "heavily distorted with major changes, embellishments, or misunderstandings"
        
        return f"""A rumor is being passed along by someone with these personality traits:
{personality_traits}

Original Event Context: {event_context}
Original Rumor: "{original_rumor}"

Based on this character's personality, how would they retell this rumor? 
The retelling should be {distortion_guidance}.

Consider how their personality traits would affect:
- What details they emphasize or downplay
- What they might add based on assumptions
- How their own biases might color the story
- Their typical speech patterns and vocabulary

Provide only the retold rumor as this character would tell it, without additional commentary."""
    
    def get_fallback_response(self, original_rumor: str, personality_traits: str, **kwargs) -> str:
        """Get a simple fallback rumor transformation."""
        # Very basic personality-based modification
        if "honest" in personality_traits.lower() or "integrity" in personality_traits.lower():
            return f"{original_rumor} (though I'm not entirely sure of all the details)"
        elif "dramatic" in personality_traits.lower() or "ambitious" in personality_traits.lower():
            return f"{original_rumor} - and from what I hear, it was even more dramatic than it sounds!"
        else:
            return original_rumor


# Convenience functions for easy access
def build_dialogue_prompt(character_name: str, personality: str, context: str, 
                         player_input: Optional[str] = None,
                         conversation_history: Optional[str] = None) -> str:
    """Quick function to build dialogue prompts."""
    manager = CharacterDialoguePromptManager()
    return manager.build_prompt(character_name, personality, context, player_input, conversation_history)


def build_reaction_prompt(character_name: str, personality: str, event: str,
                         emotional_impact: str = "moderate") -> str:
    """Quick function to build reaction prompts."""
    manager = CharacterReactionPromptManager()
    return manager.build_prompt(character_name, personality, event, emotional_impact)


def build_npc_enhancement_prompt(profession: str, race: str, age: int, personality: str,
                               backstory: str, wealth_level: str) -> str:
    """Quick function to build NPC enhancement prompts."""
    manager = NPCEnhancementPromptManager()
    return manager.build_prompt(profession, race, age, personality, backstory, wealth_level)


def build_rumor_prompt(event_context: str, original_rumor: str, personality_traits: str,
                      distortion_level: float) -> str:
    """Quick function to build rumor transformation prompts."""
    return RumorPromptManager.build_prompt(event_context, original_rumor, personality_traits, distortion_level) 
