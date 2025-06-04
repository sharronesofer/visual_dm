"""
Dialogue System AI Service

This module provides AI-powered dialogue generation using LLM integration
with context management, personality-driven responses, and conversation memory.
"""

import logging
import asyncio
import json
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from uuid import UUID, uuid4
import openai
from dataclasses import dataclass

from backend.infrastructure.shared.exceptions import (
    DialogueAIError,
    DialogueContextError
)

logger = logging.getLogger(__name__)


@dataclass
class NPCPersonality:
    """Data class for NPC personality configuration"""
    personality_traits: Dict[str, float]  # trait_name -> strength (0.0-1.0)
    conversation_style: Dict[str, Any]
    background_context: str
    relationship_modifiers: Dict[str, float]
    bartering_preferences: Dict[str, Any]
    
    def to_prompt_context(self) -> str:
        """Convert personality to LLM prompt context"""
        traits_str = ", ".join([f"{trait}: {strength:.1f}" for trait, strength in self.personality_traits.items()])
        style_str = ", ".join([f"{key}: {value}" for key, value in self.conversation_style.items()])
        
        return f"""
Character Personality:
- Traits: {traits_str}
- Style: {style_str}
- Background: {self.background_context}
        """.strip()


@dataclass
class ConversationContext:
    """Data class for conversation context"""
    conversation_id: str
    npc_id: str
    player_id: str
    interaction_type: str
    location: Optional[str] = None
    time_of_day: Optional[str] = None
    relationship_level: float = 0.5
    previous_interactions: int = 0
    current_quest_context: Optional[Dict[str, Any]] = None
    faction_standings: Optional[Dict[str, float]] = None
    
    def to_prompt_context(self) -> str:
        """Convert context to LLM prompt context"""
        context_parts = [
            f"Location: {self.location or 'Unknown'}",
            f"Time: {self.time_of_day or 'Unknown'}",
            f"Relationship Level: {self.relationship_level:.2f}",
            f"Previous Interactions: {self.previous_interactions}",
            f"Interaction Type: {self.interaction_type}"
        ]
        
        if self.current_quest_context:
            context_parts.append(f"Quest Context: {json.dumps(self.current_quest_context, indent=2)}")
        
        if self.faction_standings:
            standings_str = ", ".join([f"{faction}: {standing:.2f}" for faction, standing in self.faction_standings.items()])
            context_parts.append(f"Faction Standings: {standings_str}")
        
        return "\n".join(context_parts)


class ConversationMemory:
    """Manages conversation memory and context windows"""
    
    def __init__(self, max_context_messages: int = 10):
        self.max_context_messages = max_context_messages
        self.conversation_histories: Dict[str, List[Dict[str, Any]]] = {}
    
    def add_message(self, conversation_id: str, message: Dict[str, Any]):
        """Add a message to conversation history"""
        if conversation_id not in self.conversation_histories:
            self.conversation_histories[conversation_id] = []
        
        history = self.conversation_histories[conversation_id]
        history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'speaker': message.get('speaker'),
            'content': message.get('content'),
            'metadata': message.get('metadata', {})
        })
        
        # Trim to max context size
        if len(history) > self.max_context_messages:
            # Keep recent messages but preserve conversation start context
            start_messages = history[:2]  # Keep first 2 messages for context
            recent_messages = history[-(self.max_context_messages-2):]  # Keep recent messages
            self.conversation_histories[conversation_id] = start_messages + recent_messages
    
    def get_conversation_context(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for context"""
        return self.conversation_histories.get(conversation_id, [])
    
    def format_context_for_llm(self, conversation_id: str) -> str:
        """Format conversation history for LLM prompt"""
        history = self.get_conversation_context(conversation_id)
        if not history:
            return "No previous conversation history."
        
        formatted_messages = []
        for msg in history:
            speaker = msg.get('speaker', 'unknown')
            content = msg.get('content', '')
            formatted_messages.append(f"{speaker.title()}: {content}")
        
        return "\n".join(formatted_messages)


class LLMClient:
    """Client for LLM API communication"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        if api_key:
            openai.api_key = api_key
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.7
    ) -> str:
        """
        Generate AI response using LLM
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0.0-1.0)
            
        Returns:
            str: Generated response
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an NPC in a fantasy role-playing game. Respond in character based on the provided personality and context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM API error: {str(e)}")
            raise DialogueAIError(f"Failed to generate AI response: {str(e)}")
    
    async def generate_bartering_response(
        self,
        prompt: str,
        available_items: List[Dict[str, Any]],
        npc_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI response for bartering interactions
        
        Args:
            prompt: Base prompt for the interaction
            available_items: Items available for trade
            npc_preferences: NPC's bartering preferences
            
        Returns:
            Dict[str, Any]: Response with dialogue and trading recommendations
        """
        items_context = json.dumps(available_items, indent=2)
        preferences_context = json.dumps(npc_preferences, indent=2)
        
        bartering_prompt = f"""
{prompt}

Available Items for Trade:
{items_context}

NPC Trading Preferences:
{preferences_context}

Respond with both dialogue and trading suggestions. Format your response as JSON:
{{
    "dialogue": "Your spoken response to the player",
    "trading_interest": "high|medium|low",
    "preferred_items": ["item_id1", "item_id2"],
    "price_modifiers": {{"item_id": multiplier}},
    "special_offers": ["any special deals or comments"]
}}
        """
        
        try:
            response = await self.generate_response(bartering_prompt, max_tokens=300, temperature=0.6)
            
            # Try to parse JSON response
            try:
                parsed_response = json.loads(response)
                return parsed_response
            except json.JSONDecodeError:
                # Fallback to simple dialogue if JSON parsing fails
                return {
                    "dialogue": response,
                    "trading_interest": "medium",
                    "preferred_items": [],
                    "price_modifiers": {},
                    "special_offers": []
                }
                
        except Exception as e:
            logger.error(f"Bartering AI error: {str(e)}")
            raise DialogueAIError(f"Failed to generate bartering response: {str(e)}")


class PromptBuilder:
    """Builds contextualized prompts for LLM"""
    
    def build_conversation_prompt(
        self,
        npc_personality: NPCPersonality,
        context: ConversationContext,
        conversation_history: str,
        player_message: str
    ) -> str:
        """
        Build a comprehensive prompt for conversation generation
        
        Args:
            npc_personality: NPC personality data
            context: Conversation context
            conversation_history: Previous conversation messages
            player_message: Current player message
            
        Returns:
            str: Complete LLM prompt
        """
        prompt = f"""
You are roleplaying as an NPC in a fantasy world. Stay in character and respond naturally.

{npc_personality.to_prompt_context()}

Current Situation:
{context.to_prompt_context()}

Conversation History:
{conversation_history}

Player says: "{player_message}"

Instructions:
- Stay in character based on your personality traits
- Consider the relationship level and interaction history
- Keep responses concise but engaging (1-3 sentences)
- Match the interaction type ({context.interaction_type})
- Consider the location and time context
- Respond naturally without breaking character

Your response:
        """
        
        return prompt.strip()
    
    def build_bartering_prompt(
        self,
        npc_personality: NPCPersonality,
        context: ConversationContext,
        player_message: str,
        available_items: List[Dict[str, Any]]
    ) -> str:
        """
        Build a prompt for bartering interactions
        
        Args:
            npc_personality: NPC personality data
            context: Conversation context
            player_message: Player's message
            available_items: Items available for trade
            
        Returns:
            str: Bartering-specific prompt
        """
        items_summary = f"Available items: {len(available_items)} items including " + \
                        ", ".join([item.get('name', 'Unknown') for item in available_items[:3]])
        
        prompt = f"""
You are a trader/merchant NPC engaging in bartering. Stay in character.

{npc_personality.to_prompt_context()}

Current Situation:
{context.to_prompt_context()}
{items_summary}

Player says: "{player_message}"

Respond as a merchant would, considering:
- Your personality affects your trading style
- Relationship level affects prices and willingness to trade
- Some items may be more valuable to you than others
- You want to make profitable trades but maintain relationships

Your response should include dialogue and indicate your interest in trading.
        """
        
        return prompt.strip()


class DialogueAIService:
    """Main AI service for dialogue generation"""
    
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        memory: Optional[ConversationMemory] = None
    ):
        self.llm_client = llm_client or LLMClient()
        self.memory = memory or ConversationMemory()
        self.prompt_builder = PromptBuilder()
        self.personality_cache: Dict[str, NPCPersonality] = {}
    
    async def generate_npc_response(
        self,
        conversation_context: ConversationContext,
        npc_personality: NPCPersonality,
        player_message: str,
        response_type: str = "dialogue"
    ) -> Dict[str, Any]:
        """
        Generate AI-powered NPC response
        
        Args:
            conversation_context: Context for the conversation
            npc_personality: NPC personality configuration
            player_message: Player's message
            response_type: Type of response (dialogue, bartering, quest, etc.)
            
        Returns:
            Dict[str, Any]: AI-generated response with metadata
        """
        try:
            # Add player message to conversation memory
            self.memory.add_message(conversation_context.conversation_id, {
                'speaker': 'player',
                'content': player_message,
                'metadata': {'interaction_type': conversation_context.interaction_type}
            })
            
            # Get conversation history
            conversation_history = self.memory.format_context_for_llm(conversation_context.conversation_id)
            
            # Generate response based on type
            if response_type == "bartering":
                response = await self._generate_bartering_response(
                    conversation_context, npc_personality, player_message
                )
            else:
                response = await self._generate_dialogue_response(
                    conversation_context, npc_personality, player_message, conversation_history
                )
            
            # Add NPC response to memory
            self.memory.add_message(conversation_context.conversation_id, {
                'speaker': 'npc',
                'content': response.get('content', ''),
                'metadata': {
                    'response_type': response_type,
                    'ai_generated': True,
                    'generation_timestamp': datetime.utcnow().isoformat()
                }
            })
            
            return response
            
        except Exception as e:
            logger.error(f"AI response generation error: {str(e)}")
            raise DialogueAIError(f"Failed to generate NPC response: {str(e)}")
    
    async def _generate_dialogue_response(
        self,
        context: ConversationContext,
        personality: NPCPersonality,
        player_message: str,
        conversation_history: str
    ) -> Dict[str, Any]:
        """Generate standard dialogue response"""
        prompt = self.prompt_builder.build_conversation_prompt(
            personality, context, conversation_history, player_message
        )
        
        ai_response = await self.llm_client.generate_response(prompt)
        
        return {
            'type': 'dialogue_response',
            'content': ai_response,
            'metadata': {
                'response_time': datetime.utcnow().isoformat(),
                'interaction_type': context.interaction_type,
                'relationship_impact': self._calculate_relationship_impact(player_message, ai_response)
            }
        }
    
    async def _generate_bartering_response(
        self,
        context: ConversationContext,
        personality: NPCPersonality,
        player_message: str
    ) -> Dict[str, Any]:
        """Generate bartering-specific response"""
        # TODO: Get available items from inventory integration
        available_items = []  # Placeholder
        
        bartering_response = await self.llm_client.generate_bartering_response(
            self.prompt_builder.build_bartering_prompt(
                personality, context, player_message, available_items
            ),
            available_items,
            personality.bartering_preferences
        )
        
        return {
            'type': 'bartering_response',
            'content': bartering_response.get('dialogue', ''),
            'metadata': {
                'response_time': datetime.utcnow().isoformat(),
                'trading_interest': bartering_response.get('trading_interest', 'medium'),
                'preferred_items': bartering_response.get('preferred_items', []),
                'price_modifiers': bartering_response.get('price_modifiers', {}),
                'special_offers': bartering_response.get('special_offers', [])
            }
        }
    
    def _calculate_relationship_impact(self, player_message: str, npc_response: str) -> float:
        """
        Calculate the impact of the interaction on relationship
        
        Args:
            player_message: What the player said
            npc_response: How the NPC responded
            
        Returns:
            float: Relationship change (-1.0 to 1.0)
        """
        # Simple sentiment-based relationship calculation
        # TODO: Implement more sophisticated relationship modeling
        
        positive_words = ['thank', 'please', 'help', 'friend', 'good', 'great', 'excellent']
        negative_words = ['stupid', 'hate', 'bad', 'terrible', 'awful', 'die', 'kill']
        
        player_message_lower = player_message.lower()
        
        positive_count = sum(1 for word in positive_words if word in player_message_lower)
        negative_count = sum(1 for word in negative_words if word in player_message_lower)
        
        # Calculate impact
        if positive_count > negative_count:
            return min(0.1, positive_count * 0.05)
        elif negative_count > positive_count:
            return max(-0.1, negative_count * -0.05)
        else:
            return 0.0
    
    async def get_npc_personality(self, npc_id: str) -> NPCPersonality:
        """
        Get or generate NPC personality
        
        Args:
            npc_id: NPC identifier
            
        Returns:
            NPCPersonality: Personality configuration
        """
        if npc_id in self.personality_cache:
            return self.personality_cache[npc_id]
        
        # TODO: Load from database or generate default personality
        default_personality = NPCPersonality(
            personality_traits={
                'friendliness': 0.6,
                'helpfulness': 0.7,
                'suspicion': 0.3,
                'greed': 0.4,
                'curiosity': 0.5
            },
            conversation_style={
                'formality': 'casual',
                'verbosity': 'moderate',
                'humor': 'light'
            },
            background_context="A merchant in the town square who has lived here for many years.",
            relationship_modifiers={
                'trust_building_rate': 1.0,
                'forgiveness_factor': 0.8
            },
            bartering_preferences={
                'preferred_item_types': ['weapons', 'armor', 'gems'],
                'price_flexibility': 0.15,
                'bulk_discount': True
            }
        )
        
        self.personality_cache[npc_id] = default_personality
        return default_personality
    
    def clear_conversation_memory(self, conversation_id: str):
        """Clear conversation memory for a specific conversation"""
        if conversation_id in self.memory.conversation_histories:
            del self.memory.conversation_histories[conversation_id]


def create_dialogue_ai_service(
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo"
) -> DialogueAIService:
    """Factory function to create dialogue AI service"""
    llm_client = LLMClient(api_key=api_key, model=model)
    return DialogueAIService(llm_client=llm_client) 