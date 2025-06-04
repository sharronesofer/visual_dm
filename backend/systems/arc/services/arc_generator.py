"""
Arc system - Arc Generator Service.

This module implements GPT-powered arc generation with templates
and dynamic content creation for narrative arcs.
"""

from typing import Optional, Dict, Any, List
import logging
import json
import re
from uuid import UUID
from pydantic import BaseModel, ValidationError as PydanticValidationError

from backend.infrastructure.shared.services import BaseService
from backend.systems.arc.models.arc import ArcModel, CreateArcRequest
from backend.systems.arc.models.arc_step import ArcStepModel, CreateArcStepRequest
from backend.infrastructure.config_loaders.arc_config_loader import arc_config_loader

logger = logging.getLogger(__name__)

# Response validation schemas
class ArcStepSchema(BaseModel):
    """Schema for validating generated arc steps"""
    step_number: int
    title: str
    description: str
    narrative_text: str
    completion_criteria: Dict[str, Any]
    is_optional: Optional[bool] = False

class GeneratedArcSchema(BaseModel):
    """Schema for validating complete generated arc responses"""
    name: str
    description: str
    properties: Dict[str, Any]
    steps: List[ArcStepSchema]
    
    class Config:
        extra = "allow"  # Allow additional fields

class LLMResponseValidator:
    """Validates and sanitizes LLM responses for arc generation"""
    
    @staticmethod
    def validate_arc_response(response_text: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and parse LLM response into structured arc data with comprehensive error checking.
        
        Args:
            response_text: Raw LLM response
            template: Template used for generation
            
        Returns:
            Validated and structured arc data
            
        Raises:
            ValueError: If response cannot be parsed or validated
        """
        if not response_text or len(response_text.strip()) < 10:
            raise ValueError("LLM response is too short or empty")
        
        # Try JSON parsing first
        parsed_data = LLMResponseValidator._try_json_parsing(response_text)
        
        if not parsed_data:
            # Fall back to text parsing with regex
            parsed_data = LLMResponseValidator._parse_text_response(response_text, template)
        
        # Validate against schema
        try:
            validated_arc = GeneratedArcSchema(**parsed_data)
            return validated_arc.dict()
        except PydanticValidationError as e:
            logger.warning(f"Schema validation failed: {e}")
            # Return sanitized fallback data
            return LLMResponseValidator._create_fallback_arc(response_text, template)
    
    @staticmethod
    def _try_json_parsing(response_text: str) -> Optional[Dict[str, Any]]:
        """Attempt to parse response as JSON"""
        # Look for JSON blocks in the response
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{[^}]*"name"[^}]*\}.*?\})',
            r'(\{.*\})'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, dict) and "name" in data:
                        return data
                except json.JSONDecodeError:
                    continue
        
        # Try parsing the entire response as JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def _parse_text_response(response_text: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Parse free-text response using pattern matching"""
        lines = response_text.split('\n')
        
        # Extract basic info using patterns
        name = LLMResponseValidator._extract_field(lines, ['name', 'title', 'arc name'], "Generated Arc")
        description = LLMResponseValidator._extract_field(lines, ['description', 'summary'], response_text[:500])
        
        # Extract steps
        steps = LLMResponseValidator._extract_steps_from_text(lines, template)
        
        return {
            "name": name,
            "description": description,
            "properties": {
                "generated": True,
                "template_used": template.get("name", "unknown"),
                "complexity": template.get("complexity", "medium"),
                "parsing_method": "text_extraction"
            },
            "steps": steps
        }
    
    @staticmethod
    def _extract_field(lines: List[str], field_names: List[str], default: str) -> str:
        """Extract a field value from text lines"""
        for line in lines:
            line_lower = line.lower().strip()
            for field_name in field_names:
                if line_lower.startswith(field_name.lower() + ':'):
                    value = line.split(':', 1)[1].strip()
                    if value:
                        return value
                elif field_name.lower() in line_lower and ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        value = parts[1].strip()
                        if value:
                            return value
        return default
    
    @staticmethod
    def _extract_steps_from_text(lines: List[str], template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract step information from text lines"""
        steps = []
        current_step = None
        step_number = 1
        
        step_keywords = ['step', 'phase', 'chapter', 'stage', 'part']
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            line_lower = line_stripped.lower()
            
            # Check if this line starts a new step
            is_step_line = any(keyword in line_lower for keyword in step_keywords)
            is_numbered = re.match(r'^\d+\.', line_stripped)
            is_bullet = line_stripped.startswith(('-', '*', '•'))
            
            if is_step_line or is_numbered or (is_bullet and len(line_stripped) > 10):
                # Save previous step
                if current_step:
                    steps.append(current_step)
                
                # Start new step
                title = re.sub(r'^\d+\.\s*', '', line_stripped)
                title = re.sub(r'^[-*•]\s*', '', title)
                title = title.strip()
                
                current_step = {
                    "step_number": step_number,
                    "title": title,
                    "description": title,
                    "narrative_text": f"Narrative content for {title}",
                    "completion_criteria": {
                        "type": "objective",
                        "description": f"Complete objectives for {title}"
                    },
                    "is_optional": step_number > template.get("default_steps", 4)
                }
                step_number += 1
            
            elif current_step and len(line_stripped) > 20:
                # Add to current step description
                if current_step["description"] == current_step["title"]:
                    current_step["description"] = line_stripped
                else:
                    current_step["description"] += f" {line_stripped}"
        
        # Add final step
        if current_step:
            steps.append(current_step)
        
        # Ensure we have at least some steps
        if not steps:
            default_steps = template.get("default_steps", 4)
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
                    "is_optional": i > 2
                })
        
        return steps
    
    @staticmethod
    def _create_fallback_arc(response_text: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fallback arc when validation fails"""
        return {
            "name": "Generated Arc (Fallback)",
            "description": response_text[:500] if response_text else "Generated arc description",
            "properties": {
                "generated": True,
                "fallback": True,
                "template_used": template.get("name", "unknown"),
                "complexity": template.get("complexity", "medium"),
                "validation_failed": True
            },
            "steps": LLMResponseValidator._extract_steps_from_text(
                response_text.split('\n') if response_text else [], 
                template
            )
        }

class ArcGenerator(BaseService):
    """Service for generating arcs using GPT and templates"""
    
    def __init__(self, db_session=None, llm_service=None):
        super().__init__(db_session, ArcModel)
        self.llm_service = llm_service
        self.templates = self._load_templates()
        self.validator = LLMResponseValidator()
        
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load arc templates from JSON configuration"""
        try:
            templates = arc_config_loader.load_arc_templates()
            logger.info(f"Loaded {len(templates)} arc templates from configuration")
            return templates
        except Exception as e:
            logger.error(f"Failed to load arc templates from configuration: {e}")
            # Fallback to minimal templates if config loading fails
            return self._get_fallback_templates()
    
    def _get_fallback_templates(self) -> Dict[str, Dict[str, Any]]:
        """Fallback templates if configuration loading fails"""
        logger.warning("Using fallback templates due to configuration loading failure")
        return {
            "global": {
                "name": "Global Arc Template",
                "description": "Fallback template for world-spanning narratives", 
                "prompt_template": """Create a global arc that affects the entire campaign world.

Please respond with a JSON object containing:
{
  "name": "Arc Title",
  "description": "Detailed arc description",
  "properties": {
    "complexity": "high",
    "estimated_duration": "6-8 sessions"
  },
  "steps": [
    {
      "step_number": 1,
      "title": "Step Title",
      "description": "Step description",
      "narrative_text": "Rich narrative content",
      "completion_criteria": {
        "type": "objective",
        "description": "What needs to be accomplished"
      }
    }
  ]
}""",
                "default_steps": 6,
                "complexity": "high"
            },
            "regional": {
                "name": "Regional Arc Template",
                "description": "Fallback template for location-specific storylines",
                "prompt_template": """Create a regional arc focused on a specific location.

Please respond with a JSON object containing:
{
  "name": "Arc Title",
  "description": "Detailed arc description",
  "properties": {
    "complexity": "medium",
    "estimated_duration": "4-6 sessions"
  },
  "steps": [
    {
      "step_number": 1,
      "title": "Step Title", 
      "description": "Step description",
      "narrative_text": "Rich narrative content",
      "completion_criteria": {
        "type": "objective",
        "description": "What needs to be accomplished"
      }
    }
  ]
}""",
                "default_steps": 4,
                "complexity": "medium"
            }
        }
    
    async def generate_arc(
        self,
        arc_type: str,
        parameters: Dict[str, Any],
        custom_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a new arc using GPT with enhanced validation"""
        try:
            template = self.templates.get(arc_type, self.templates.get("global", self._get_fallback_templates()["global"]))
            
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
            fallback_template = self._get_fallback_templates().get("global")
            return self._generate_fallback(arc_type, parameters, fallback_template)
    
    async def _generate_with_llm(self, prompt: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Generate arc content using LLM service with robust validation"""
        try:
            # Call LLM service to generate content
            response = await self.llm_service.generate_content(
                prompt=prompt,
                max_tokens=3000,  # Increased for richer content
                temperature=0.7
            )
            
            response_text = response.get("response", "")
            
            # Validate and parse the response
            return self.validator.validate_arc_response(response_text, template)
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured arc data (deprecated - use validator)"""
        logger.warning("Using deprecated _parse_llm_response - should use LLMResponseValidator")
        return self.validator.validate_arc_response(response, template)
    
    def _extract_steps_from_response(self, response: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract arc steps from LLM response (deprecated - use validator)"""
        logger.warning("Using deprecated _extract_steps_from_response - should use LLMResponseValidator")
        return self.validator._extract_steps_from_text(response.split('\n'), template)
    
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
        step_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate an arc with a specific number of steps"""
        try:
            template = self.templates.get(arc_type, self.templates.get("global"))
            if not template:
                logger.error(f"No template found for arc type: {arc_type}")
                template = self._get_fallback_templates()["global"]
            
            # Override default step count if specified
            if step_count:
                template = template.copy()
                template["default_steps"] = step_count
            
            return await self.generate_arc(arc_type, parameters)
            
        except Exception as e:
            logger.error(f"Error generating arc with steps: {e}")
            fallback_template = self._get_fallback_templates()["global"]
            return self._generate_fallback(arc_type, parameters, fallback_template)
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available arc templates"""
        return self.templates
    
    def add_custom_template(self, name: str, template: Dict[str, Any]) -> bool:
        """Add a custom template (runtime only)"""
        try:
            self.templates[name] = template
            logger.info(f"Added custom template: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom template: {e}")
            return False
    
    def reload_templates(self) -> bool:
        """Reload templates from configuration"""
        try:
            self.templates = self._load_templates()
            logger.info("Templates reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload templates: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the arc generator"""
        return {
            "status": "healthy",
            "templates_loaded": len(self.templates),
            "llm_available": self.llm_service is not None,
            "available_templates": list(self.templates.keys())
        }
