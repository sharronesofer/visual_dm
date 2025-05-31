"""
Arc system - Arc Generator Service.

This module implements GPT-powered arc generation with templates
and dynamic content creation for narrative arcs.
"""

from typing import Optional, Dict, Any, List
import logging
from uuid import UUID

from backend.infrastructure.models import BaseService
from backend.systems.arc.models.arc import ArcModel, CreateArcRequest
from backend.systems.arc.models.arc_step import ArcStepModel, CreateArcStepRequest

logger = logging.getLogger(__name__)


class ArcGenerator(BaseService):
    """Service for generating arcs using GPT and templates"""
    
    def __init__(self, db_session=None, llm_service=None):
        super().__init__(db_session, ArcModel)
        self.llm_service = llm_service
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load arc generation templates"""
        return {
            "global": {
                "name": "Global Arc Template",
                "description": "Template for world-spanning narratives",
                "prompt_template": """
                Create a global arc that affects the entire campaign world.
                Theme: {theme}
                Scope: {scope}
                Duration: {duration}
                Key Elements: {elements}
                
                Generate an arc with:
                - Compelling overarching narrative
                - 5-8 major steps/phases
                - World-changing consequences
                - Multiple faction involvement
                """,
                "default_steps": 6,
                "complexity": "high"
            },
            "regional": {
                "name": "Regional Arc Template",
                "description": "Template for location-specific storylines",
                "prompt_template": """
                Create a regional arc focused on a specific location.
                Region: {region}
                Theme: {theme}
                Local Issues: {issues}
                Key NPCs: {npcs}
                
                Generate an arc with:
                - Regional narrative focus
                - 3-5 major steps
                - Local consequences
                - Community involvement
                """,
                "default_steps": 4,
                "complexity": "medium"
            },
            "character": {
                "name": "Character Arc Template",
                "description": "Template for personal character development",
                "prompt_template": """
                Create a character development arc.
                Character: {character}
                Background: {background}
                Goals: {goals}
                Conflicts: {conflicts}
                
                Generate an arc with:
                - Personal growth narrative
                - 3-4 development phases
                - Character-specific challenges
                - Meaningful choices
                """,
                "default_steps": 3,
                "complexity": "low"
            },
            "npc": {
                "name": "NPC Arc Template",
                "description": "Template for supporting character storylines",
                "prompt_template": """
                Create an NPC storyline arc.
                NPC: {npc}
                Role: {role}
                Motivations: {motivations}
                Relationship to Players: {relationship}
                
                Generate an arc with:
                - Supporting character focus
                - 2-4 interaction points
                - Player intersection opportunities
                - Character development
                """,
                "default_steps": 3,
                "complexity": "low"
            }
        }
    
    async def generate_arc(
        self,
        arc_type: str,
        parameters: Dict[str, Any],
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a new arc using GPT"""
        try:
            template = self.templates.get(arc_type, self.templates["global"])
            
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = template["prompt_template"].format(**parameters)
            
            # Generate arc content using LLM service
            if self.llm_service:
                arc_content = await self._generate_with_llm(prompt, template)
            else:
                arc_content = self._generate_fallback(arc_type, parameters, template)
            
            return arc_content
            
        except Exception as e:
            logger.error(f"Error generating arc: {e}")
            return self._generate_fallback(arc_type, parameters, self.templates["global"])
    
    async def _generate_with_llm(self, prompt: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate arc content using LLM service"""
        try:
            # Call LLM service to generate content
            response = await self.llm_service.generate_content(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Parse and structure the response
            return self._parse_llm_response(response, template)
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured arc data"""
        # This would parse the LLM response and extract structured data
        # For now, return a structured format
        return {
            "name": "Generated Arc",
            "description": response[:500] if response else "Generated arc description",
            "properties": {
                "generated": True,
                "template_used": template["name"],
                "complexity": template.get("complexity", "medium"),
                "content": response
            },
            "steps": self._extract_steps_from_response(response, template)
        }
    
    def _extract_steps_from_response(self, response: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract arc steps from LLM response"""
        default_steps = template.get("default_steps", 4)
        steps = []
        
        # Simple step extraction (would be more sophisticated in practice)
        for i in range(default_steps):
            steps.append({
                "step_number": i + 1,
                "title": f"Step {i + 1}",
                "description": f"Generated step {i + 1} description",
                "narrative_text": f"Narrative content for step {i + 1}",
                "completion_criteria": {
                    "type": "objective",
                    "description": f"Complete objectives for step {i + 1}"
                }
            })
        
        return steps
    
    def _generate_fallback(
        self,
        arc_type: str,
        parameters: Dict[str, Any],
        template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback arc content when LLM is unavailable"""
        return {
            "name": f"Generated {arc_type.title()} Arc",
            "description": f"A {arc_type} arc generated with fallback content",
            "properties": {
                "generated": True,
                "fallback": True,
                "template_used": template["name"],
                "complexity": template.get("complexity", "medium"),
                "parameters": parameters
            },
            "steps": self._generate_fallback_steps(template)
        }
    
    def _generate_fallback_steps(self, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback steps when LLM is unavailable"""
        default_steps = template.get("default_steps", 4)
        steps = []
        
        for i in range(default_steps):
            steps.append({
                "step_number": i + 1,
                "title": f"Arc Step {i + 1}",
                "description": f"Step {i + 1} in the arc progression",
                "narrative_text": f"Narrative content for step {i + 1}",
                "completion_criteria": {
                    "type": "objective",
                    "description": f"Complete the objectives for step {i + 1}"
                },
                "is_optional": i > 2  # Make later steps optional
            })
        
        return steps
    
    async def generate_arc_with_steps(
        self,
        arc_type: str,
        parameters: Dict[str, Any],
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a complete arc with steps"""
        try:
            # Generate the arc content
            arc_data = await self.generate_arc(arc_type, parameters, custom_prompt)
            
            # Create the arc model
            arc_request = CreateArcRequest(
                name=arc_data["name"],
                description=arc_data["description"],
                properties=arc_data["properties"]
            )
            
            # Generate steps
            steps_data = arc_data.get("steps", [])
            
            return {
                "arc": arc_request.dict(),
                "steps": steps_data,
                "generation_metadata": {
                    "arc_type": arc_type,
                    "parameters": parameters,
                    "template_used": arc_data["properties"].get("template_used"),
                    "generated_at": "now"  # Would use actual timestamp
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating arc with steps: {e}")
            raise
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all available arc templates"""
        return self.templates
    
    def add_custom_template(self, name: str, template: Dict[str, Any]) -> bool:
        """Add a custom arc template"""
        try:
            self.templates[name] = template
            return True
        except Exception as e:
            logger.error(f"Error adding custom template: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            "status": "healthy",
            "service": "ArcGenerator",
            "templates_loaded": len(self.templates),
            "llm_service_available": self.llm_service is not None
        }
