"""
Enhanced Context Management for Visual DM LLM System

Provides intelligent context window management, dynamic prioritization, and 
memory-aware prompt construction for optimal LLM performance.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from backend.infrastructure.llm.config.llm_config import llm_config
from backend.infrastructure.llm.utils.llm_utils import LLMUtils
from backend.infrastructure.systems.memory.services import get_memory_service

logger = logging.getLogger(__name__)

class ContextPriority(Enum):
    """Context section priority levels"""
    CRITICAL = 1.0      # Never truncate - character identity, current situation
    HIGH = 0.9          # High priority - recent interactions, immediate context
    MEDIUM = 0.7        # Medium priority - faction relationships, recent events
    LOW = 0.5           # Low priority - background lore, distant history
    MINIMAL = 0.3       # Minimal priority - general world information

@dataclass
class ContextSection:
    """Represents a section of context with metadata"""
    name: str
    content: str
    priority: ContextPriority
    estimated_tokens: int
    last_updated: datetime
    context_type: str

class ContextManager:
    """
    Manages context window efficiently for optimal LLM performance.
    
    Features:
    - Intelligent context truncation based on priority
    - Dynamic prioritization based on interaction type
    - Token estimation and management
    - Memory-aware context construction
    """
    
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.token_estimator = LLMUtils()
        self.memory_service = None
        
        # Default context priorities by section type
        self.default_priorities = {
            "character_identity": ContextPriority.CRITICAL,
            "character_personality": ContextPriority.CRITICAL,
            "immediate_context": ContextPriority.HIGH,
            "current_situation": ContextPriority.HIGH,
            "conversation_history": ContextPriority.HIGH,
            "recent_interactions": ContextPriority.MEDIUM,
            "faction_relationships": ContextPriority.MEDIUM,
            "recent_events": ContextPriority.MEDIUM,
            "character_background": ContextPriority.LOW,
            "world_lore": ContextPriority.LOW,
            "general_information": ContextPriority.MINIMAL
        }
        
        # Interaction-specific priority overrides
        self.interaction_priorities = {
            "dialogue": {
                "character_personality": ContextPriority.CRITICAL,
                "conversation_history": ContextPriority.HIGH,
                "current_situation": ContextPriority.HIGH,
                "faction_relationships": ContextPriority.MEDIUM,
                "world_lore": ContextPriority.LOW
            },
            "quest_generation": {
                "region_details": ContextPriority.CRITICAL,
                "faction_relationships": ContextPriority.HIGH,
                "player_progress": ContextPriority.HIGH,
                "character_personality": ContextPriority.MEDIUM,
                "world_lore": ContextPriority.MEDIUM
            },
            "narrative": {
                "location_details": ContextPriority.CRITICAL,
                "environmental_context": ContextPriority.HIGH,
                "time_context": ContextPriority.HIGH,
                "recent_events": ContextPriority.MEDIUM,
                "character_presence": ContextPriority.LOW
            },
            "world_building": {
                "existing_lore": ContextPriority.CRITICAL,
                "faction_relationships": ContextPriority.HIGH,
                "regional_details": ContextPriority.HIGH,
                "historical_context": ContextPriority.MEDIUM,
                "character_context": ContextPriority.LOW
            }
        }
    
    async def initialize(self):
        """Initialize the context manager"""
        self.memory_service = await get_memory_service()
        logger.info("ContextManager initialized")
    
    async def prepare_context(self, 
                            context_data: Dict[str, Any], 
                            interaction_type: str = "general") -> str:
        """
        Prepare context with intelligent truncation and prioritization.
        
        Args:
            context_data: Raw context data organized by section
            interaction_type: Type of interaction for priority adjustment
            
        Returns:
            Formatted context string optimized for the interaction type
        """
        if not self.memory_service:
            await self.initialize()
        
        # Convert context data to ContextSection objects
        context_sections = await self._create_context_sections(context_data, interaction_type)
        
        # Calculate total token usage
        total_tokens = sum(section.estimated_tokens for section in context_sections)
        
        # Apply intelligent truncation if necessary
        if total_tokens > self.max_tokens:
            context_sections = await self._intelligent_truncation(
                context_sections, target_tokens=int(self.max_tokens * 0.9)
            )
        
        # Format the final context
        formatted_context = await self._format_context(context_sections)
        
        logger.debug(f"Prepared context: {len(formatted_context)} chars, "
                    f"~{await self._estimate_tokens(formatted_context)} tokens")
        
        return formatted_context
    
    async def _create_context_sections(self, 
                                     context_data: Dict[str, Any], 
                                     interaction_type: str) -> List[ContextSection]:
        """Create ContextSection objects from raw data"""
        sections = []
        
        # Get priority overrides for this interaction type
        priority_overrides = self.interaction_priorities.get(interaction_type, {})
        
        for section_name, content in context_data.items():
            if not content:  # Skip empty sections
                continue
            
            # Determine priority
            priority = priority_overrides.get(
                section_name, 
                self.default_priorities.get(section_name, ContextPriority.MEDIUM)
            )
            
            # Estimate tokens
            if isinstance(content, str):
                content_str = content
            elif isinstance(content, dict):
                content_str = await self._dict_to_string(content)
            elif isinstance(content, list):
                content_str = await self._list_to_string(content)
            else:
                content_str = str(content)
            
            estimated_tokens = await self._estimate_tokens(content_str)
            
            sections.append(ContextSection(
                name=section_name,
                content=content_str,
                priority=priority,
                estimated_tokens=estimated_tokens,
                last_updated=datetime.utcnow(),
                context_type=interaction_type
            ))
        
        # Sort by priority (highest first)
        sections.sort(key=lambda x: x.priority.value, reverse=True)
        
        return sections
    
    async def _intelligent_truncation(self, 
                                    sections: List[ContextSection], 
                                    target_tokens: int) -> List[ContextSection]:
        """
        Apply intelligent truncation to fit within token limits.
        
        Strategy:
        1. Never truncate CRITICAL priority content
        2. Progressively truncate lower priority content
        3. Within same priority, truncate older content first
        4. Preserve content structure and meaning
        """
        current_tokens = sum(section.estimated_tokens for section in sections)
        
        if current_tokens <= target_tokens:
            return sections
        
        logger.debug(f"Truncating context: {current_tokens} -> {target_tokens} tokens")
        
        # Separate sections by priority
        critical_sections = [s for s in sections if s.priority == ContextPriority.CRITICAL]
        high_sections = [s for s in sections if s.priority == ContextPriority.HIGH]
        medium_sections = [s for s in sections if s.priority == ContextPriority.MEDIUM]
        low_sections = [s for s in sections if s.priority == ContextPriority.LOW]
        minimal_sections = [s for s in sections if s.priority == ContextPriority.MINIMAL]
        
        # Calculate tokens used by critical sections (never truncated)
        critical_tokens = sum(s.estimated_tokens for s in critical_sections)
        remaining_tokens = target_tokens - critical_tokens
        
        if remaining_tokens <= 0:
            logger.warning("Critical context exceeds token limit")
            return critical_sections
        
        # Progressively add sections by priority
        final_sections = critical_sections.copy()
        
        for section_group in [high_sections, medium_sections, low_sections, minimal_sections]:
            for section in section_group:
                if remaining_tokens >= section.estimated_tokens:
                    final_sections.append(section)
                    remaining_tokens -= section.estimated_tokens
                else:
                    # Try to partially include this section if possible
                    if remaining_tokens > 100:  # Minimum meaningful size
                        truncated_section = await self._truncate_section(
                            section, remaining_tokens
                        )
                        if truncated_section:
                            final_sections.append(truncated_section)
                    break
            
            if remaining_tokens <= 0:
                break
        
        return final_sections
    
    async def _truncate_section(self, 
                              section: ContextSection, 
                              max_tokens: int) -> Optional[ContextSection]:
        """Truncate a single section to fit within token limit"""
        if section.estimated_tokens <= max_tokens:
            return section
        
        # Calculate truncation ratio
        ratio = max_tokens / section.estimated_tokens
        target_chars = int(len(section.content) * ratio * 0.9)  # 90% for safety
        
        if target_chars < 50:  # Too small to be meaningful
            return None
        
        # Truncate at word boundaries when possible
        truncated_content = section.content[:target_chars]
        
        # Find last complete sentence or word
        last_sentence = truncated_content.rfind('.')
        last_word = truncated_content.rfind(' ')
        
        if last_sentence > target_chars * 0.7:  # If we have most of the content
            truncated_content = truncated_content[:last_sentence + 1]
        elif last_word > target_chars * 0.8:
            truncated_content = truncated_content[:last_word]
        
        # Add truncation indicator
        truncated_content += "... [truncated]"
        
        # Create new section with truncated content
        new_tokens = await self._estimate_tokens(truncated_content)
        
        return ContextSection(
            name=section.name,
            content=truncated_content,
            priority=section.priority,
            estimated_tokens=new_tokens,
            last_updated=section.last_updated,
            context_type=section.context_type
        )
    
    async def _format_context(self, sections: List[ContextSection]) -> str:
        """Format context sections into a coherent string"""
        formatted_parts = []
        
        # Group sections by type for better organization
        section_groups = {}
        for section in sections:
            group_name = self._get_section_group(section.name)
            if group_name not in section_groups:
                section_groups[group_name] = []
            section_groups[group_name].append(section)
        
        # Format each group
        group_order = [
            "Character Information",
            "Current Context",
            "Interaction History", 
            "World Information",
            "Background Information"
        ]
        
        for group_name in group_order:
            if group_name in section_groups:
                formatted_parts.append(f"## {group_name}")
                
                for section in section_groups[group_name]:
                    if section.content.strip():
                        formatted_parts.append(f"### {section.name.replace('_', ' ').title()}")
                        formatted_parts.append(section.content.strip())
                        formatted_parts.append("")  # Empty line for separation
        
        return "\n".join(formatted_parts)
    
    def _get_section_group(self, section_name: str) -> str:
        """Categorize sections into logical groups"""
        character_sections = [
            "character_identity", "character_personality", "character_background"
        ]
        context_sections = [
            "immediate_context", "current_situation", "location_details", 
            "environmental_context", "time_context"
        ]
        history_sections = [
            "conversation_history", "recent_interactions", "player_progress"
        ]
        world_sections = [
            "faction_relationships", "recent_events", "regional_details"
        ]
        
        if section_name in character_sections:
            return "Character Information"
        elif section_name in context_sections:
            return "Current Context"
        elif section_name in history_sections:
            return "Interaction History"
        elif section_name in world_sections:
            return "World Information"
        else:
            return "Background Information"
    
    async def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return self.token_estimator.estimate_tokens(text)
    
    async def _dict_to_string(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to formatted string"""
        parts = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                parts.append(f"{key}: {str(value)}")
            else:
                parts.append(f"{key}: {value}")
        return "\n".join(parts)
    
    async def _list_to_string(self, data: List[Any]) -> str:
        """Convert list to formatted string"""
        if not data:
            return ""
        
        # Handle list of dicts (common for conversation history)
        if isinstance(data[0], dict):
            parts = []
            for item in data:
                if isinstance(item, dict):
                    item_str = ", ".join(f"{k}: {v}" for k, v in item.items())
                    parts.append(f"- {item_str}")
                else:
                    parts.append(f"- {item}")
            return "\n".join(parts)
        else:
            return "\n".join(f"- {item}" for item in data)

class MemoryAwarePromptBuilder:
    """
    Builds prompts with awareness of conversation memory and character relationships.
    
    Integrates with the Memory System to provide context-aware prompt construction
    that considers past interactions and relationship dynamics.
    """
    
    def __init__(self):
        self.context_manager = None
        self.memory_service = None
    
    async def initialize(self):
        """Initialize the prompt builder"""
        self.context_manager = ContextManager()
        await self.context_manager.initialize()
        self.memory_service = await get_memory_service()
        logger.info("MemoryAwarePromptBuilder initialized")
    
    async def build_dialogue_prompt(self, 
                                  npc_id: str, 
                                  player_message: str,
                                  character_context: Dict[str, Any],
                                  additional_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build dialogue prompt with memory integration.
        
        Args:
            npc_id: ID of the NPC character
            player_message: What the player said
            character_context: Character data from NPC system
            additional_context: Additional context data
            
        Returns:
            Memory-aware dialogue prompt
        """
        if not self.memory_service:
            await self.initialize()
        
        # Gather memory-based context
        conversation_memory = await self.memory_service.get_conversation_summary(npc_id)
        player_memory = await self.memory_service.get_character_memory(npc_id, "player")
        relationship_context = await self.memory_service.get_relationship_context(npc_id)
        
        # Build comprehensive context
        context_data = {
            "character_identity": self._format_character_identity(character_context),
            "character_personality": self._format_personality(character_context),
            "conversation_history": conversation_memory,
            "player_memory": player_memory,
            "relationship_context": relationship_context,
            "current_situation": additional_context.get("current_situation", "") if additional_context else "",
            "immediate_context": f"Player message: \"{player_message}\""
        }
        
        # Add any additional context
        if additional_context:
            context_data.update(additional_context)
        
        # Use context manager to prepare optimized context
        formatted_context = await self.context_manager.prepare_context(
            context_data, interaction_type="dialogue"
        )
        
        # Build the final prompt
        prompt = f"""
{formatted_context}

Instructions:
- Respond as {character_context.get('name', 'the character')} in character
- Consider your relationship with the player and past interactions
- Keep the response natural and conversational
- Maintain consistency with your established personality
- Response should be 1-3 sentences unless the situation calls for more

Generate your response:
"""
        
        return prompt.strip()
    
    async def build_narrative_prompt(self,
                                   location_context: Dict[str, Any],
                                   environmental_context: Dict[str, Any],
                                   narrative_type: str = "description") -> str:
        """
        Build narrative prompt for environmental storytelling.
        
        Args:
            location_context: Location/POI details
            environmental_context: Time, weather, etc.
            narrative_type: Type of narrative (description, event, etc.)
            
        Returns:
            Context-aware narrative prompt
        """
        context_data = {
            "location_details": self._format_location_details(location_context),
            "environmental_context": self._format_environmental_context(environmental_context),
            "time_context": environmental_context.get("time_of_day", ""),
            "weather_context": environmental_context.get("weather", "")
        }
        
        formatted_context = await self.context_manager.prepare_context(
            context_data, interaction_type="narrative"
        )
        
        prompt = f"""
{formatted_context}

Generate a {narrative_type} that:
- Creates atmosphere appropriate to the location and conditions
- Uses vivid but concise language
- Fits the current environmental context
- Maintains consistency with established lore
- Length: 2-4 sentences

Generate the {narrative_type}:
"""
        
        return prompt.strip()
    
    async def build_quest_prompt(self,
                               quest_parameters: Dict[str, Any],
                               world_context: Dict[str, Any]) -> str:
        """
        Build quest generation prompt with world context.
        
        Args:
            quest_parameters: Quest type, difficulty, etc.
            world_context: Current world state, factions, etc.
            
        Returns:
            Context-aware quest generation prompt
        """
        context_data = {
            "region_details": world_context.get("region_details", ""),
            "faction_relationships": world_context.get("faction_relationships", ""),
            "player_progress": world_context.get("player_progress", ""),
            "recent_events": world_context.get("recent_events", ""),
            "quest_parameters": self._format_quest_parameters(quest_parameters)
        }
        
        formatted_context = await self.context_manager.prepare_context(
            context_data, interaction_type="quest_generation"
        )
        
        prompt = f"""
{formatted_context}

Generate a quest that:
- Fits the specified parameters and difficulty
- Integrates with current world state and faction relationships
- Provides clear objectives and context
- Considers player progress and capabilities
- Offers meaningful rewards and consequences

Structure your response as:
Title: [Quest Title]
Description: [2-3 sentence description]
Objectives: [List of specific objectives]
Context: [Why this quest is relevant now]

Generate the quest:
"""
        
        return prompt.strip()
    
    def _format_character_identity(self, character_context: Dict[str, Any]) -> str:
        """Format character identity information"""
        name = character_context.get("name", "Unknown")
        role = character_context.get("role", character_context.get("profession", ""))
        location = character_context.get("current_location", "")
        
        identity_parts = [f"Name: {name}"]
        if role:
            identity_parts.append(f"Role: {role}")
        if location:
            identity_parts.append(f"Current Location: {location}")
        
        return "\n".join(identity_parts)
    
    def _format_personality(self, character_context: Dict[str, Any]) -> str:
        """Format character personality traits"""
        personality = character_context.get("personality", {})
        if not personality:
            return "Personality traits not specified."
        
        if isinstance(personality, dict):
            traits = []
            for trait, value in personality.items():
                if isinstance(value, (int, float)):
                    traits.append(f"{trait}: {value}")
                else:
                    traits.append(f"{trait}: {value}")
            return "\n".join(traits)
        else:
            return str(personality)
    
    def _format_location_details(self, location_context: Dict[str, Any]) -> str:
        """Format location details"""
        name = location_context.get("name", "Unknown Location")
        description = location_context.get("description", "")
        location_type = location_context.get("type", "")
        
        details = [f"Location: {name}"]
        if location_type:
            details.append(f"Type: {location_type}")
        if description:
            details.append(f"Description: {description}")
        
        return "\n".join(details)
    
    def _format_environmental_context(self, env_context: Dict[str, Any]) -> str:
        """Format environmental context"""
        time_of_day = env_context.get("time_of_day", "")
        weather = env_context.get("weather", "")
        season = env_context.get("season", "")
        
        context_parts = []
        if time_of_day:
            context_parts.append(f"Time: {time_of_day}")
        if weather:
            context_parts.append(f"Weather: {weather}")
        if season:
            context_parts.append(f"Season: {season}")
        
        return "\n".join(context_parts) if context_parts else "Environmental context not specified."
    
    def _format_quest_parameters(self, quest_params: Dict[str, Any]) -> str:
        """Format quest parameters"""
        quest_type = quest_params.get("quest_type", "general")
        difficulty = quest_params.get("difficulty", "medium")
        location = quest_params.get("location", "")
        player_level = quest_params.get("player_level", "unknown")
        
        params = [
            f"Quest Type: {quest_type}",
            f"Difficulty: {difficulty}",
            f"Player Level: {player_level}"
        ]
        
        if location:
            params.append(f"Location: {location}")
        
        return "\n".join(params)

# Global instances
_context_manager = None
_prompt_builder = None

async def get_context_manager() -> ContextManager:
    """Get the global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
        await _context_manager.initialize()
    return _context_manager

async def get_prompt_builder() -> MemoryAwarePromptBuilder:
    """Get the global prompt builder instance"""
    global _prompt_builder
    if _prompt_builder is None:
        _prompt_builder = MemoryAwarePromptBuilder()
        await _prompt_builder.initialize()
    return _prompt_builder 