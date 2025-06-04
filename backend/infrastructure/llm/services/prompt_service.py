"""
Enhanced Prompt Service for Visual DM LLM Infrastructure

This service provides the integration layer between the centralized prompt management system
and the broader LLM infrastructure. It handles template discovery, dynamic loading, and
provides simplified interfaces for other systems to use AI-generated content.

Integrates with:
- Centralized PromptManager for template management
- Model Manager for optimal model selection
- Context Manager for memory-aware prompting
- Quality Control for response validation
"""

from typing import Dict, List, Optional, Any
import logging
import asyncio
import json
from pathlib import Path

from backend.infrastructure.llm.services.prompt_manager import (
    get_prompt_manager, PromptManager, PromptTemplate, TemplateCategory
)
from backend.infrastructure.llm.repositories.prompt_repository import PromptRepository

logger = logging.getLogger(__name__)

class PromptService:
    """
    Enhanced prompt management service that bridges template management 
    with the broader LLM infrastructure capabilities.
    """
    
    def __init__(self):
        self.prompt_manager: Optional[PromptManager] = None
        self.prompt_repo = PromptRepository()
        self.logger = logger
        self.initialized = False
    
    async def initialize(self):
        """Initialize the prompt service and load templates"""
        if self.initialized:
            return
            
        logger.info("Initializing Enhanced Prompt Service...")
        
        # Initialize prompt manager
        self.prompt_manager = await get_prompt_manager()
        
        # Load additional templates from repository/files
        await self._load_external_templates()
        
        self.initialized = True
        logger.info("Enhanced Prompt Service initialization complete")
    
    async def generate_prompt(self, template_id: str, variables: Dict[str, Any]) -> str:
        """
        Legacy interface - Generate prompt from template for backward compatibility
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            response = await self.prompt_manager.generate(
                template_name=template_id,
                variables=variables
            )
            return response.get("response", "")
        except Exception as e:
            logger.error(f"Failed to generate prompt with template {template_id}: {e}")
            # Fallback to repository method
            template = await self.prompt_repo.get_prompt_template(template_id)
            if template:
                return template.get("content", "").format(**variables)
            raise
    
    async def process_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Process a template with variables to produce a formatted prompt
        """
        if not self.initialized:
            await self.initialize()
        
        template = self.prompt_manager.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        system_prompt, user_prompt = template.format_prompt(variables)
        return user_prompt  # Return just the user prompt for simple cases
    
    async def generate_with_template(self,
                                   template_name: str,
                                   variables: Dict[str, Any],
                                   context: Optional[Dict[str, Any]] = None,
                                   **kwargs) -> Dict[str, Any]:
        """
        Generate content using a template with full response metadata
        """
        if not self.initialized:
            await self.initialize()
        
        return await self.prompt_manager.generate(
            template_name=template_name,
            variables=variables,
            context=context,
            **kwargs
        )
    
    async def create_template(self, template_data: Dict[str, Any]) -> str:
        """
        Create new prompt template - enhanced to work with PromptManager
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create PromptTemplate object
            template = PromptTemplate(**template_data)
            
            # Register with prompt manager
            success = self.prompt_manager.register_template(template)
            if not success:
                raise ValueError("Failed to register template")
            
            # Also save to repository for persistence
            template_id = await self.prompt_repo.save_prompt_template(template_data)
            
            return template.name
            
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise
    
    async def find_templates(self,
                           category: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           search_term: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find templates matching specified criteria with detailed metadata
        """
        if not self.initialized:
            await self.initialize()
        
        templates = self.prompt_manager.find_templates(
            category=category,
            tags=tags
        )
        
        result = []
        for template in templates:
            # Apply search term filter if specified
            if search_term:
                search_term_lower = search_term.lower()
                if not (search_term_lower in template.name.lower() or
                       search_term_lower in template.description.lower()):
                    continue
            
            result.append({
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "tags": template.tags,
                "version": template.version,
                "model": template.model,
                "usage_count": template.usage_count,
                "success_rate": template.success_rate,
                "avg_response_time": template.avg_response_time,
                "required_variables": template.required_variables,
                "optional_variables": template.optional_variables
            })
        
        return result
    
    async def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific template
        """
        if not self.initialized:
            await self.initialize()
        
        template = self.prompt_manager.get_template(template_name)
        if not template:
            return None
        
        return {
            "name": template.name,
            "description": template.description,
            "category": template.category,
            "tags": template.tags,
            "version": template.version,
            "model": template.model,
            "batch_eligible": template.batch_eligible,
            "author": template.author,
            "created_at": template.created_at,
            "updated_at": template.updated_at,
            "usage_count": template.usage_count,
            "success_rate": template.success_rate,
            "avg_response_time": template.avg_response_time,
            "required_variables": template.required_variables,
            "optional_variables": template.optional_variables,
            "context_requirements": template.context_requirements,
            "system_prompt": template.system_prompt,
            "user_prompt_template": template.user_prompt_template
        }
    
    async def get_categories(self) -> List[str]:
        """Get all available template categories"""
        if not self.initialized:
            await self.initialize()
        
        return list(self.prompt_manager.category_index.keys())
    
    async def get_tags(self) -> List[str]:
        """Get all available template tags"""
        if not self.initialized:
            await self.initialize()
        
        return list(self.prompt_manager.tag_index.keys())
    
    async def validate_template_variables(self, 
                                        template_name: str, 
                                        variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate variables against template requirements
        """
        if not self.initialized:
            await self.initialize()
        
        template = self.prompt_manager.get_template(template_name)
        if not template:
            return {"valid": False, "error": f"Template not found: {template_name}"}
        
        valid, missing = template.validate_variables(variables)
        
        return {
            "valid": valid,
            "missing_required": missing,
            "provided_optional": [var for var in template.optional_variables if var in variables],
            "extra_variables": [var for var in variables if var not in template.required_variables + template.optional_variables]
        }
    
    async def preview_prompt(self, 
                           template_name: str, 
                           variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Preview formatted prompt without generating AI response
        """
        if not self.initialized:
            await self.initialize()
        
        template = self.prompt_manager.get_template(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        system_prompt, user_prompt = template.format_prompt(variables)
        
        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "template_name": template.name,
            "model": template.model
        }
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive service and template performance metrics"""
        if not self.initialized:
            await self.initialize()
        
        prompt_manager_metrics = await self.prompt_manager.get_metrics()
        
        return {
            "prompt_service": {
                "initialized": self.initialized,
                "total_templates": len(self.prompt_manager.templates)
            },
            **prompt_manager_metrics
        }
    
    async def _load_external_templates(self):
        """Load templates from external sources (files, database, etc.)"""
        try:
            # Load templates from repository
            repo_templates = await self.prompt_repo.list_templates()
            for template_data in repo_templates:
                if template_data:
                    try:
                        template = PromptTemplate(**template_data)
                        self.prompt_manager.register_template(template)
                    except Exception as e:
                        logger.warning(f"Failed to load template from repository: {e}")
            
            # Load templates from prompt library file if available
            await self._load_prompt_library_templates()
            
        except Exception as e:
            logger.error(f"Error loading external templates: {e}")
    
    async def _load_prompt_library_templates(self):
        """
        Load templates from the prompt library documentation file
        This bridges the gap with the existing comprehensive template system
        """
        try:
            # Path to the prompt library
            library_path = Path("docs/prompt_library.md")
            
            if library_path.exists():
                logger.info("Found prompt library, integrating templates...")
                # Future enhancement: Parse the markdown file and extract template definitions
                # For now, the core templates are already registered in PromptManager
                pass
            else:
                logger.debug("Prompt library file not found, using core templates only")
                
        except Exception as e:
            logger.warning(f"Error loading prompt library templates: {e}")
    
    async def clear_cache(self):
        """Clear all caches"""
        if self.prompt_manager:
            await self.prompt_manager.clear_cache()
    
    async def reload_templates(self):
        """Reload all templates from external sources"""
        if self.prompt_manager:
            # Clear existing templates (keep core ones)
            core_templates = ["system_dm_persona", "npc_dialogue_basic", "location_description", "quest_hook_generation"]
            all_templates = list(self.prompt_manager.templates.keys())
            
            for template_name in all_templates:
                if template_name not in core_templates:
                    del self.prompt_manager.templates[template_name]
            
            # Rebuild indexes
            self.prompt_manager.category_index.clear()
            self.prompt_manager.tag_index.clear()
            
            for template in self.prompt_manager.templates.values():
                # Rebuild category index
                if template.category not in self.prompt_manager.category_index:
                    self.prompt_manager.category_index[template.category] = []
                self.prompt_manager.category_index[template.category].append(template.name)
                
                # Rebuild tag index
                for tag in template.tags:
                    if tag not in self.prompt_manager.tag_index:
                        self.prompt_manager.tag_index[tag] = []
                    self.prompt_manager.tag_index[tag].append(template.name)
            
            # Reload external templates
            await self._load_external_templates()
            
        logger.info("Template reload completed")
