"""
Centralized Prompt Management System for Visual DM LLM Infrastructure

This module provides the core prompt management functionality that was previously distributed
across multiple systems. It implements a centralized template repository with dynamic loading,
version control, and integration with the hybrid LLM architecture.

Architecture:
- PromptTemplate: Core template data structure
- PromptManager: Central management service 
- Template registration and discovery
- Context-aware template selection
- Performance caching and optimization

Usage:
    from backend.infrastructure.llm.services.prompt_manager import get_prompt_manager
    
    prompt_manager = await get_prompt_manager()
    response = await prompt_manager.generate(
        template_name="npc_dialogue_basic",
        context={...},
        variables={...}
    )
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
import json
import time
from pathlib import Path
import inspect

from backend.infrastructure.shared.models.models import BaseModel
from backend.infrastructure.llm.services.model_manager import ModelType, get_model_manager

logger = logging.getLogger(__name__)

class TemplateCategory(Enum):
    """Categories for organizing prompt templates"""
    SYSTEM = "system"
    FORMATTING = "formatting" 
    CONTEXT = "context"
    QUEST = "quest"
    NPC = "npc"
    WORLD = "world"
    COMBAT = "combat"
    ITEM = "item"
    UTILITY = "utility"
    DIALOGUE = "dialogue"
    NARRATIVE = "narrative"

@dataclass
class PromptTemplate:
    """
    Core prompt template data structure with comprehensive metadata
    """
    name: str
    system_prompt: str
    user_prompt_template: str
    description: str
    version: str = "1.0"
    category: str = "utility"
    tags: List[str] = field(default_factory=list)
    model: str = "gpt-4.1-mini"
    batch_eligible: bool = False
    
    # Enhanced metadata
    author: Optional[str] = None
    created_at: Optional[float] = None
    updated_at: Optional[float] = None
    usage_count: int = 0
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    
    # Context requirements
    required_variables: List[str] = field(default_factory=list)
    optional_variables: List[str] = field(default_factory=list)
    context_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def validate_variables(self, variables: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate that all required variables are provided"""
        missing = [var for var in self.required_variables if var not in variables]
        return len(missing) == 0, missing
    
    def format_prompt(self, variables: Dict[str, Any]) -> tuple[str, str]:
        """Format the template with provided variables"""
        valid, missing = self.validate_variables(variables)
        if not valid:
            raise ValueError(f"Missing required variables: {missing}")
        
        try:
            formatted_system_prompt = self.system_prompt.format(**variables)
            formatted_user_prompt = self.user_prompt_template.format(**variables)
            return formatted_system_prompt, formatted_user_prompt
        except KeyError as e:
            raise ValueError(f"Template variable not provided: {e}")
    
    def update_metrics(self, response_time: float, success: bool):
        """Update performance metrics"""
        self.usage_count += 1
        self.avg_response_time = (
            (self.avg_response_time * (self.usage_count - 1) + response_time) / self.usage_count
        )
        if success:
            self.success_rate = (
                (self.success_rate * (self.usage_count - 1) + 1.0) / self.usage_count
            )
        else:
            self.success_rate = (
                (self.success_rate * (self.usage_count - 1) + 0.0) / self.usage_count
            )
        self.updated_at = time.time()

class PromptManager:
    """
    Central prompt management service providing template registration, 
    discovery, and intelligent generation capabilities.
    """
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.category_index: Dict[str, List[str]] = {}
        self.tag_index: Dict[str, List[str]] = {}
        self.model_manager = None
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Performance tracking
        self.metrics = {
            "total_generations": 0,
            "cache_hits": 0,
            "template_load_time": 0.0,
            "avg_generation_time": 0.0
        }
    
    async def initialize(self):
        """Initialize the prompt manager and load templates"""
        logger.info("Initializing Prompt Manager...")
        start_time = time.time()
        
        self.model_manager = await get_model_manager()
        await self._load_default_templates()
        
        load_time = time.time() - start_time
        self.metrics["template_load_time"] = load_time
        
        logger.info(f"Prompt Manager initialized with {len(self.templates)} templates in {load_time:.2f}s")
    
    def register_template(self, template: PromptTemplate) -> bool:
        """Register a new template with indexing"""
        try:
            self.templates[template.name] = template
            
            # Update category index
            if template.category not in self.category_index:
                self.category_index[template.category] = []
            if template.name not in self.category_index[template.category]:
                self.category_index[template.category].append(template.name)
            
            # Update tag index
            for tag in template.tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                if template.name not in self.tag_index[tag]:
                    self.tag_index[tag].append(template.name)
            
            logger.debug(f"Registered template: {template.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register template {template.name}: {e}")
            return False
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Retrieve a template by name"""
        return self.templates.get(name)
    
    def find_templates(self, 
                      category: Optional[str] = None,
                      tags: Optional[List[str]] = None,
                      model_type: Optional[str] = None) -> List[PromptTemplate]:
        """Find templates matching specified criteria"""
        candidates = set(self.templates.keys())
        
        if category and category in self.category_index:
            candidates &= set(self.category_index[category])
        
        if tags:
            for tag in tags:
                if tag in self.tag_index:
                    candidates &= set(self.tag_index[tag])
        
        results = [self.templates[name] for name in candidates if name in self.templates]
        
        if model_type:
            results = [t for t in results if t.model == model_type]
        
        return results
    
    async def generate(self,
                      template_name: str,
                      variables: Dict[str, Any],
                      context: Optional[Dict[str, Any]] = None,
                      model_override: Optional[str] = None,
                      cache_key: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """
        Generate content using specified template with comprehensive error handling
        """
        if not self.model_manager:
            await self.initialize()
        
        start_time = time.time()
        self.metrics["total_generations"] += 1
        
        # Check cache first
        if cache_key:
            cached = self._get_cached_response(cache_key)
            if cached:
                self.metrics["cache_hits"] += 1
                return cached
        
        # Get template
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        try:
            # Format prompt
            system_prompt, user_prompt = template.format_prompt(variables)
            
            # Determine model
            model = model_override or template.model
            
            # Generate response using model manager
            response_data = await self.model_manager.generate_response(
                prompt=user_prompt,
                system_prompt=system_prompt,
                model_name=model,
                **kwargs
            )
            
            # Calculate metrics
            generation_time = time.time() - start_time
            template.update_metrics(generation_time, True)
            
            # Update service metrics
            self.metrics["avg_generation_time"] = (
                (self.metrics["avg_generation_time"] * (self.metrics["total_generations"] - 1) + generation_time) 
                / self.metrics["total_generations"]
            )
            
            # Enhance response with metadata
            enhanced_response = {
                **response_data,
                "template": {
                    "name": template.name,
                    "category": template.category,
                    "version": template.version
                },
                "generation_time": generation_time,
                "cached": False,
                "timestamp": time.time()
            }
            
            # Cache if requested
            if cache_key:
                self._cache_response(cache_key, enhanced_response)
            
            return enhanced_response
            
        except Exception as e:
            template.update_metrics(time.time() - start_time, False)
            logger.error(f"Generation failed for template {template_name}: {e}")
            raise
    
    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if valid"""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry["timestamp"] < self.cache_ttl:
                return entry["data"]
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response_data: Dict[str, Any]):
        """Cache response with TTL"""
        self.cache[cache_key] = {
            "data": response_data,
            "timestamp": time.time()
        }
    
    async def _load_default_templates(self):
        """Load the default template library"""
        # This will load templates from the prompt library
        # For now, implementing core templates that integrate with existing systems
        await self._register_core_templates()
    
    async def _register_core_templates(self):
        """Register essential templates for Visual DM systems"""
        
        # System templates
        self.register_template(PromptTemplate(
            name="system_dm_persona",
            system_prompt="You are an AI assistant helping with a tabletop RPG system.",
            user_prompt_template="""You are the Dungeon Master for a tabletop role-playing game. Your role is to create engaging narratives, challenging encounters, and memorable characters for the players. You should maintain consistency in the world and adapt to player actions. Your tone should be descriptive, imaginative, and immersive, bringing the fantasy world to life.""",
            description="Base dungeon master persona for narrative generation",
            category="system",
            tags=["persona", "dm", "base"],
            model="gpt-4.1-mini",
            required_variables=[],
            optional_variables=["world_context", "current_scene"]
        ))
        
        self.register_template(PromptTemplate(
            name="npc_dialogue_basic",
            system_prompt="You are an NPC in a fantasy RPG responding to a player.",
            user_prompt_template="""Character: {character_name}
Background: {character_background}
Current situation: {current_situation}
Player said: "{player_message}"

Respond in character with a single paragraph of dialogue. Stay true to the character's personality and knowledge.""",
            description="Basic NPC dialogue generation",
            category="npc",
            tags=["dialogue", "npc", "conversation"],
            model="gpt-4.1-mini",
            required_variables=["character_name", "character_background", "current_situation", "player_message"],
            optional_variables=["mood", "relationship_to_player"]
        ))
        
        self.register_template(PromptTemplate(
            name="location_description",
            system_prompt="You are describing a location in a fantasy RPG setting.",
            user_prompt_template="""Location: {location_name}
Type: {location_type}
Notable features: {notable_features}
Time of day: {time_of_day}
Weather: {weather}

Provide an immersive 2-3 sentence description that sets the scene and atmosphere.""",
            description="Generate atmospheric location descriptions",
            category="world",
            tags=["description", "location", "atmosphere"],
            model="gpt-4.1-mini",
            required_variables=["location_name", "location_type", "notable_features"],
            optional_variables=["time_of_day", "weather", "mood"]
        ))
        
        self.register_template(PromptTemplate(
            name="quest_hook_generation",
            system_prompt="You are generating quest hooks for a tabletop RPG.",
            user_prompt_template="""Quest type: {quest_type}
Difficulty: {difficulty}
Location: {location}
Player level: {player_level}

Generate a compelling quest hook that includes:
1. The initial problem or opportunity
2. Why the characters would be interested
3. A hint at the potential complications

Keep it to 2-3 sentences that would intrigue players.""",
            description="Generate engaging quest hooks",
            category="quest",
            tags=["quest", "hook", "adventure"],
            model="gpt-4.1-mini",
            required_variables=["quest_type", "difficulty", "location", "player_level"],
            optional_variables=["faction_involvement", "time_pressure"]
        ))

    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        template_stats = {}
        for name, template in self.templates.items():
            template_stats[name] = {
                "usage_count": template.usage_count,
                "success_rate": template.success_rate,
                "avg_response_time": template.avg_response_time
            }
        
        return {
            "service_metrics": self.metrics,
            "template_count": len(self.templates),
            "categories": list(self.category_index.keys()),
            "cache_size": len(self.cache),
            "cache_hit_rate": self.metrics["cache_hits"] / max(1, self.metrics["total_generations"]),
            "template_performance": template_stats
        }
    
    async def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
        logger.info("Prompt manager cache cleared")

# Global instance management
_prompt_manager_instance: Optional[PromptManager] = None

async def get_prompt_manager() -> PromptManager:
    """Get or create the global prompt manager instance"""
    global _prompt_manager_instance
    if _prompt_manager_instance is None:
        _prompt_manager_instance = PromptManager()
        await _prompt_manager_instance.initialize()
    return _prompt_manager_instance

async def register_template_from_dict(template_data: Dict[str, Any]) -> bool:
    """Utility function to register template from dictionary"""
    manager = await get_prompt_manager()
    template = PromptTemplate(**template_data)
    return manager.register_template(template) 