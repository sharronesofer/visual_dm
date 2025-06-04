"""
Arc system - Quest Integration Service.

This module implements the bridge between arcs and the quest system
for seamless integration and tag-based quest generation.
"""

from typing import Optional, Dict, Any, List, Protocol
import logging
from uuid import UUID
import json
import asyncio

from backend.infrastructure.models import BaseService
from backend.systems.arc.models.arc import ArcModel
from backend.infrastructure.config_loaders.arc_config_loader import arc_config_loader
from backend.infrastructure.llm.services.llm_service import LLMService, GenerationContext

logger = logging.getLogger(__name__)


class QuestServiceProtocol(Protocol):
    """Protocol for quest service to avoid circular imports."""
    
    def create_quest(self, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a quest."""
        ...
    
    def link_quest_to_arc(self, quest_id: UUID, arc_id: UUID, step_number: int) -> bool:
        """Link a quest to an arc step."""
        ...


class ArcServiceProtocol(Protocol):
    """Protocol for arc service to avoid circular imports."""
    
    def get_arc_by_id(self, arc_id: UUID) -> Optional[Dict[str, Any]]:
        """Get arc by ID."""
        ...


class EnhancedQuestNarrativeGenerator:
    """Generates rich, contextual quest narratives using LLM"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service
    
    async def generate_quest_narrative(
        self,
        arc_context: Dict[str, Any],
        quest_type: str,
        step_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate rich quest narrative content based on arc context.
        
        Args:
            arc_context: Context from the parent arc
            quest_type: Type of quest to generate
            step_context: Additional context from the current arc step
            
        Returns:
            Rich quest data with narrative content
        """
        if self.llm_service:
            return await self._generate_llm_quest_narrative(arc_context, quest_type, step_context)
        else:
            return self._generate_template_quest_narrative(arc_context, quest_type, step_context)
    
    async def _generate_llm_quest_narrative(
        self,
        arc_context: Dict[str, Any],
        quest_type: str,
        step_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate quest narrative using LLM with rich context"""
        
        prompt_template = """
Create a compelling quest that fits naturally within this story arc:

**Arc Context:**
- Title: {arc_title}
- Description: {arc_description}
- Themes: {arc_themes}
- Current Step: {current_step}
- Arc Type: {arc_type}

**Quest Requirements:**
- Quest Type: {quest_type}
- Step Context: {step_context}

**Additional Context:**
- World Setting: {world_setting}
- Player Level: {player_level}
- Location: {location}

Please create a quest that:
1. Naturally flows from the arc narrative
2. Advances the character's story
3. Feels meaningful and connected to the larger plot
4. Includes rich narrative details and flavor text
5. Has clear but engaging objectives

Respond with a JSON object in this format:
{{
  "title": "Quest Title",
  "description": "Rich quest description with narrative flavor",
  "narrative_hook": "Compelling opening that draws players in",
  "objectives": [
    {{
      "id": "obj1",
      "description": "Objective description",
      "narrative_context": "Why this objective matters to the story"
    }}
  ],
  "key_npcs": [
    {{
      "name": "NPC Name",
      "role": "quest_giver/ally/antagonist",
      "description": "Brief NPC description",
      "dialogue_sample": "Sample dialogue that fits their character"
    }}
  ],
  "locations": [
    {{
      "name": "Location Name",
      "description": "Atmospheric location description",
      "significance": "Why this location is important to the quest"
    }}
  ],
  "rewards": {{
    "experience": 300,
    "narrative_reward": "How completing this quest advances the character's story",
    "items": ["potential item rewards"],
    "reputation": "faction or relationship changes"
  }},
  "difficulty_rating": "easy/medium/hard",
  "estimated_duration": "short/medium/long",
  "moral_complexity": "Description of any moral choices or dilemmas",
  "connection_to_arc": "How this quest specifically advances the arc narrative"
}}
"""
        
        # Build context for the prompt
        context = {
            "arc_title": arc_context.get("title", "Unknown Arc"),
            "arc_description": arc_context.get("description", ""),
            "arc_themes": ", ".join(arc_context.get("themes", [])),
            "current_step": step_context.get("title", "Current Step") if step_context else "Unknown",
            "arc_type": arc_context.get("arc_type", "unknown"),
            "quest_type": quest_type,
            "step_context": step_context.get("description", "") if step_context else "",
            "world_setting": arc_context.get("world_setting", "fantasy"),
            "player_level": arc_context.get("player_level", "appropriate"),
            "location": arc_context.get("location", "current area")
        }
        
        try:
            response = await self.llm_service.generate_content(
                prompt=prompt_template.format(**context),
                context=GenerationContext.QUEST_GENERATION,
                max_tokens=3500,
                temperature=0.8  # High creativity for quest content
            )
            
            response_text = response.get("response", "")
            return self._parse_quest_narrative_response(response_text, arc_context, quest_type)
            
        except Exception as e:
            logger.error(f"LLM quest narrative generation failed: {e}")
            return self._generate_template_quest_narrative(arc_context, quest_type, step_context)
    
    def _parse_quest_narrative_response(
        self,
        response_text: str,
        arc_context: Dict[str, Any],
        quest_type: str
    ) -> Dict[str, Any]:
        """Parse LLM response into structured quest data"""
        import re
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_data = json.loads(json_str)
                
                # Enhance with additional metadata
                parsed_data.update({
                    "generated_via": "llm",
                    "arc_id": arc_context.get("id"),
                    "generation_timestamp": asyncio.get_event_loop().time(),
                    "quest_type": quest_type
                })
                
                return parsed_data
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse LLM quest narrative response: {e}")
        
        # Fallback: extract basic information from text
        return self._extract_quest_from_text(response_text, arc_context, quest_type)
    
    def _extract_quest_from_text(
        self,
        response_text: str,
        arc_context: Dict[str, Any],
        quest_type: str
    ) -> Dict[str, Any]:
        """Extract quest information from free-form text"""
        lines = response_text.split('\n')
        
        title = f"Quest for {arc_context.get('title', 'the Arc')}"
        description = response_text[:500]
        objectives = []
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Look for objectives
            if any(keyword in line_lower for keyword in ['objective', 'goal', 'task', 'must']):
                objectives.append({
                    "id": f"obj{len(objectives) + 1}",
                    "description": line,
                    "narrative_context": "Part of the quest progression"
                })
        
        # Ensure we have at least one objective
        if not objectives:
            objectives = [{
                "id": "obj1",
                "description": f"Complete the {quest_type} quest",
                "narrative_context": "Advance the story"
            }]
        
        return {
            "title": title,
            "description": description,
            "narrative_hook": description[:200],
            "objectives": objectives,
            "key_npcs": [],
            "locations": [],
            "rewards": {
                "experience": 300,
                "narrative_reward": "Story progression",
                "items": [],
                "reputation": ""
            },
            "difficulty_rating": "medium",
            "estimated_duration": "medium",
            "moral_complexity": "Standard quest progression",
            "connection_to_arc": f"Advances the {arc_context.get('title', 'current')} arc",
            "generated_via": "text_extraction",
            "arc_id": arc_context.get("id"),
            "quest_type": quest_type
        }
    
    def _generate_template_quest_narrative(
        self,
        arc_context: Dict[str, Any],
        quest_type: str,
        step_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate quest narrative using enhanced templates"""
        
        quest_templates = {
            "exploration": {
                "title_format": "Discover the {location}",
                "description": "Venture into uncharted territory to uncover secrets related to {arc_theme}.",
                "narrative_hook": "Strange rumors have reached you about {location}, and they seem connected to your {arc_theme}.",
                "objectives": [
                    {
                        "id": "explore",
                        "description": "Explore the designated area thoroughly",
                        "narrative_context": "The area holds clues to your character's journey"
                    },
                    {
                        "id": "discover",
                        "description": "Uncover the hidden truth",
                        "narrative_context": "This discovery will change your understanding"
                    }
                ],
                "difficulty": "medium",
                "duration": "medium"
            },
            "combat": {
                "title_format": "Confront the {threat}",
                "description": "A dangerous force threatens something important to your {arc_theme}.",
                "narrative_hook": "The time for talking has passed. You must face the {threat} that stands in your way.",
                "objectives": [
                    {
                        "id": "prepare",
                        "description": "Gather allies and resources",
                        "narrative_context": "Preparation is key to overcoming this challenge"
                    },
                    {
                        "id": "confront",
                        "description": "Face the threat directly",
                        "narrative_context": "This confrontation will test your resolve"
                    }
                ],
                "difficulty": "hard",
                "duration": "medium"
            },
            "social": {
                "title_format": "Navigate the {social_situation}",
                "description": "Political intrigue and social maneuvering are required to advance your {arc_theme}.",
                "narrative_hook": "Words can be as powerful as swords. The right conversation could change everything.",
                "objectives": [
                    {
                        "id": "gather_info",
                        "description": "Learn about the key players and their motivations",
                        "narrative_context": "Information is your greatest weapon"
                    },
                    {
                        "id": "negotiate",
                        "description": "Navigate the social dynamics to achieve your goal",
                        "narrative_context": "Success here opens new possibilities"
                    }
                ],
                "difficulty": "medium",
                "duration": "long"
            },
            "mystery": {
                "title_format": "Unravel the Mystery of {mystery_element}",
                "description": "Clues and investigation are needed to solve a puzzle connected to your {arc_theme}.",
                "narrative_hook": "Something doesn't add up. The truth is hidden beneath layers of deception.",
                "objectives": [
                    {
                        "id": "investigate",
                        "description": "Gather clues and evidence",
                        "narrative_context": "Each clue brings you closer to the truth"
                    },
                    {
                        "id": "deduce",
                        "description": "Piece together the evidence to reach a conclusion",
                        "narrative_context": "The revelation will have lasting consequences"
                    }
                ],
                "difficulty": "medium",
                "duration": "long"
            }
        }
        
        template = quest_templates.get(quest_type, quest_templates["exploration"])
        
        # Build context-specific replacements
        arc_theme = arc_context.get("themes", ["adventure"])[0] if arc_context.get("themes") else "adventure"
        
        replacements = {
            "location": step_context.get("location", "Unknown Region") if step_context else "Unknown Region",
            "threat": f"enemy of {arc_theme}",
            "social_situation": f"politics surrounding {arc_theme}",
            "mystery_element": f"secrets of {arc_theme}",
            "arc_theme": arc_theme
        }
        
        # Apply replacements to template
        quest_data = {
            "title": template["title_format"].format(**replacements),
            "description": template["description"].format(**replacements),
            "narrative_hook": template["narrative_hook"].format(**replacements),
            "objectives": [
                {
                    "id": obj["id"],
                    "description": obj["description"],
                    "narrative_context": obj["narrative_context"]
                }
                for obj in template["objectives"]
            ],
            "key_npcs": [],
            "locations": [],
            "rewards": {
                "experience": {"easy": 200, "medium": 300, "hard": 500}.get(template["difficulty"], 300),
                "narrative_reward": f"Advances your understanding of {arc_theme}",
                "items": [],
                "reputation": f"Improved standing related to {arc_theme}"
            },
            "difficulty_rating": template["difficulty"],
            "estimated_duration": template["duration"],
            "moral_complexity": "Standard quest with meaningful choices",
            "connection_to_arc": f"Directly advances the {arc_context.get('title', 'current')} arc narrative",
            "generated_via": "enhanced_template",
            "arc_id": arc_context.get("id"),
            "quest_type": quest_type
        }
        
        return quest_data


class QuestIntegrationService(BaseService):
    """Service for integrating arcs with the quest system"""
    
    def __init__(self, db_session=None, quest_service: Optional[QuestServiceProtocol] = None, 
                 arc_service: Optional[ArcServiceProtocol] = None, llm_service: Optional[LLMService] = None):
        super().__init__(db_session, ArcModel)
        self.quest_service = quest_service
        self.arc_service = arc_service
        self.llm_service = llm_service
        self.narrative_generator = EnhancedQuestNarrativeGenerator(llm_service)
        
        # Load configurations
        self.tag_mappings = self._initialize_tag_mappings()
        self.keyword_mappings = self._initialize_keyword_mappings()
        self.quest_templates = self._initialize_quest_templates()
        
    def _initialize_tag_mappings(self) -> Dict[str, List[str]]:
        """Initialize tag mappings from JSON configuration"""
        try:
            tag_mappings = arc_config_loader.get_tag_mappings()
            logger.info(f"Loaded tag mappings for {len(tag_mappings)} arc types from configuration")
            return tag_mappings
        except Exception as e:
            logger.error(f"Failed to load tag mappings from configuration: {e}")
            return self._get_fallback_tag_mappings()
    
    def _get_fallback_tag_mappings(self) -> Dict[str, List[str]]:
        """Fallback tag mappings if configuration loading fails"""
        logger.warning("Using fallback tag mappings due to configuration loading failure")
        return {
            "global": ["world_event", "campaign", "epic"],
            "regional": ["local_politics", "regional_threat", "community"],
            "character": ["personal_growth", "backstory", "relationship"],
            "npc": ["supporting_character", "ally_quest", "rival_story"]
        }
    
    def _initialize_keyword_mappings(self) -> Dict[str, List[str]]:
        """Initialize keyword mappings from JSON configuration"""
        try:
            keyword_mappings = arc_config_loader.get_keyword_mappings()
            logger.info(f"Loaded keyword mappings for {len(keyword_mappings)} categories from configuration")
            return keyword_mappings
        except Exception as e:
            logger.error(f"Failed to load keyword mappings from configuration: {e}")
            return self._get_fallback_keyword_mappings()
    
    def _get_fallback_keyword_mappings(self) -> Dict[str, List[str]]:
        """Fallback keyword mappings if configuration loading fails"""
        logger.warning("Using fallback keyword mappings due to configuration loading failure")
        return {
            "combat": ["combat", "monster_hunt"],
            "mystery": ["investigation", "mystery"],
            "exploration": ["exploration", "dungeon_delve"],
            "social": ["social", "reputation"]
        }
    
    def _initialize_quest_templates(self) -> Dict[str, Any]:
        """Initialize quest templates from JSON configuration"""
        try:
            quest_templates = arc_config_loader.get_quest_templates()
            logger.info(f"Loaded {len(quest_templates)} quest templates from configuration")
            return quest_templates
        except Exception as e:
            logger.error(f"Failed to load quest templates from configuration: {e}")
            return self._get_fallback_quest_templates()
    
    def _get_fallback_quest_templates(self) -> Dict[str, Any]:
        """Fallback quest templates if configuration loading fails"""
        logger.warning("Using fallback quest templates due to configuration loading failure")
        return {
            "exploration": {
                "title": "Explore the Unknown",
                "description": "Venture into uncharted territory",
                "objectives": ["Explore area", "Report findings"],
                "rewards": {"experience": 300}
            }
        }
    
    async def generate_enhanced_quests_for_arc(
        self,
        arc_id: UUID,
        step_number: Optional[int] = None,
        quest_count: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate enhanced quests with rich narratives based on arc content"""
        try:
            # Get arc data using dependency injection pattern
            arc_data = await self._get_arc_data(arc_id)
            
            # Get step context if specified
            step_context = None
            if step_number is not None:
                steps = arc_data.get("steps", [])
                if 0 <= step_number < len(steps):
                    step_context = steps[step_number]
            
            # Determine arc type and extract context
            arc_type = arc_data.get("properties", {}).get("arc_type", "global")
            quest_types = self._determine_quest_types(arc_data, arc_type)
            
            # Generate enhanced quest opportunities
            quest_opportunities = []
            
            for i in range(quest_count):
                quest_type = quest_types[i % len(quest_types)]
                
                # Generate rich narrative quest
                quest_data = await self.narrative_generator.generate_quest_narrative(
                    arc_context=arc_data,
                    quest_type=quest_type,
                    step_context=step_context
                )
                
                # Add metadata
                quest_data.update({
                    "id": f"quest_{arc_data.get('id', 'unknown')}_{i}",
                    "arc_id": str(arc_id),
                    "step_number": step_number,
                    "generated": True,
                    "quest_index": i
                })
                
                # If quest service is available, create actual quests
                if self.quest_service:
                    try:
                        created_quest = self.quest_service.create_quest(quest_data)
                        quest_opportunities.append(created_quest)
                    except Exception as e:
                        logger.error(f"Failed to create quest via quest service: {e}")
                        quest_opportunities.append(quest_data)
                else:
                    quest_opportunities.append(quest_data)
            
            logger.info(f"Generated {len(quest_opportunities)} enhanced quests for arc {arc_id}")
            return quest_opportunities
            
        except Exception as e:
            logger.error(f"Error generating enhanced quests for arc: {e}")
            raise
    
    def _determine_quest_types(self, arc_data: Dict[str, Any], arc_type: str) -> List[str]:
        """Determine appropriate quest types based on arc context"""
        base_types = ["exploration", "combat", "social", "mystery"]
        
        # Customize based on arc themes
        themes = arc_data.get("themes", [])
        if "political" in themes or "intrigue" in themes:
            return ["social", "mystery", "exploration", "combat"]
        elif "combat" in themes or "war" in themes:
            return ["combat", "exploration", "social", "mystery"]
        elif "discovery" in themes or "knowledge" in themes:
            return ["mystery", "exploration", "social", "combat"]
        else:
            return base_types
    
    async def link_quest_to_arc_step(
        self,
        quest_id: UUID,
        arc_id: UUID,
        step_number: int
    ) -> Dict[str, Any]:
        """Link a quest to a specific arc step"""
        try:
            # Use quest service if available
            if self.quest_service:
                result = self.quest_service.link_quest_to_arc(quest_id, arc_id, step_number)
                if result:
                    return {
                        "quest_id": str(quest_id),
                        "arc_id": str(arc_id),
                        "step_number": step_number,
                        "linked": True
                    }
            
            # Fallback to storing link information
            return {
                "quest_id": str(quest_id),
                "arc_id": str(arc_id),
                "step_number": step_number,
                "linked": True,
                "note": "Link created without quest service"
            }
            
        except Exception as e:
            logger.error(f"Error linking quest to arc step: {e}")
            raise
    
    async def get_arc_quest_progress(self, arc_id: UUID) -> Dict[str, Any]:
        """Get quest progress for an arc"""
        try:
            # This would typically query the quest system for linked quests
            # For now, return a placeholder structure
            return {
                "arc_id": str(arc_id),
                "total_quests": 0,
                "completed_quests": 0,
                "active_quests": 0,
                "failed_quests": 0,
                "progress_percentage": 0.0,
                "quest_details": []
            }
            
        except Exception as e:
            logger.error(f"Error getting arc quest progress: {e}")
            raise
    
    async def sync_arc_quest_completion(
        self,
        arc_id: UUID,
        completed_quest_ids: List[UUID]
    ) -> Dict[str, Any]:
        """Sync arc progression based on quest completion"""
        try:
            # Get arc data
            arc_data = await self._get_arc_data(arc_id)
            
            # Calculate new progress based on completed quests
            # This is a simplified calculation
            total_quests = len(completed_quest_ids) + 5  # Assume some remaining quests
            completed_count = len(completed_quest_ids)
            
            progress_percentage = (completed_count / total_quests) * 100.0
            
            sync_result = {
                "arc_id": str(arc_id),
                "completed_quest_count": completed_count,
                "total_quest_count": total_quests,
                "progress_percentage": progress_percentage,
                "sync_timestamp": "now",
                "updated": True
            }
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error syncing arc quest completion: {e}")
            raise
    
    async def _get_arc_data(self, arc_id: UUID) -> Dict[str, Any]:
        """Get arc data using the arc service"""
        if self.arc_service:
            return self.arc_service.get_arc_by_id(arc_id) or {}
        else:
            # Fallback to basic arc data
            return {
                "id": str(arc_id),
                "name": "Unknown Arc",
                "properties": {"arc_type": "global"}
            }
    
    async def _get_quest_arc_link(self, quest_id: UUID, arc_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the link between a quest and arc"""
        # This would query the database for quest-arc links
        # For now, return None as placeholder
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the quest integration service"""
        return {
            "status": "healthy",
            "tag_mappings_loaded": len(self.tag_mappings),
            "keyword_mappings_loaded": len(self.keyword_mappings),
            "quest_templates_loaded": len(self.quest_templates),
            "quest_service_available": self.quest_service is not None,
            "arc_service_available": self.arc_service is not None
        }
