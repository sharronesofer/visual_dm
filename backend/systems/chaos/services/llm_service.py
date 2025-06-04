"""
Chaos LLM Service

Provides AI-powered text generation and narrative reasoning for the chaos system.
Handles dynamic event descriptions, warning narratives, cascade reasoning, and mitigation suggestions.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
import os

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType, EventSeverity

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from LLM service"""
    content: str
    success: bool
    model_used: str
    tokens_used: Optional[int] = None
    error: Optional[str] = None
    context_used: Dict[str, Any] = None


class ChaosLLMService:
    """
    LLM service for chaos system narrative generation and reasoning.
    
    Provides:
    - Dynamic event description generation
    - Contextual warning narratives
    - Intelligent cascade reasoning
    - Dynamic mitigation suggestions
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        self.openai_client = None
        self.anthropic_client = None
        self._initialized = False
        
        # Configuration
        self.model_preference = os.getenv('CHAOS_LLM_MODEL', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('CHAOS_LLM_MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('CHAOS_LLM_TEMPERATURE', '0.7'))
        self.enabled = os.getenv('CHAOS_LLM_ENABLED', 'true').lower() == 'true'
        
        # Fallback templates if LLM fails
        self.fallback_templates = self._load_fallback_templates()
        
    async def initialize(self) -> bool:
        """Initialize LLM clients"""
        if self._initialized:
            return True
            
        if not self.enabled:
            logger.info("Chaos LLM service disabled by configuration")
            return True
            
        success = False
        
        # Try to initialize OpenAI
        if HAS_OPENAI and os.getenv('OPENAI_API_KEY'):
            try:
                self.openai_client = openai.AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                success = True
                logger.info("Chaos LLM service initialized with OpenAI")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Try to initialize Anthropic
        if HAS_ANTHROPIC and os.getenv('ANTHROPIC_API_KEY'):
            try:
                self.anthropic_client = anthropic.AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                success = True
                logger.info("Chaos LLM service initialized with Anthropic")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic: {e}")
        
        if not success:
            logger.warning("No LLM providers available - falling back to templates")
        
        self._initialized = True
        return success
    
    async def generate_event_description(self, 
                                       event_type: ChaosEventType,
                                       severity: EventSeverity,
                                       context: Dict[str, Any]) -> LLMResponse:
        """
        Generate dynamic event descriptions based on current world context.
        
        Args:
            event_type: Type of chaos event
            severity: Event severity level
            context: Current world context (regions, recent events, player actions, etc.)
            
        Returns:
            LLMResponse with generated description
        """
        if not self.enabled or not self._initialized:
            return self._fallback_event_description(event_type, severity, context)
        
        # Construct prompt for event description
        prompt = self._build_event_description_prompt(event_type, severity, context)
        
        # Try LLM generation
        response = await self._call_llm(prompt, "event_description")
        
        if not response.success:
            return self._fallback_event_description(event_type, severity, context)
        
        return response
    
    async def generate_warning_narrative(self,
                                       phase: str,
                                       event_type: str,
                                       region_context: Dict[str, Any]) -> LLMResponse:
        """
        Generate contextual warning narratives for the three-phase warning system.
        
        Args:
            phase: Warning phase (rumor, early, imminent)
            event_type: Type of impending event
            region_context: Regional context and characteristics
            
        Returns:
            LLMResponse with warning narrative
        """
        if not self.enabled or not self._initialized:
            return self._fallback_warning_narrative(phase, event_type, region_context)
        
        prompt = self._build_warning_prompt(phase, event_type, region_context)
        response = await self._call_llm(prompt, "warning_narrative")
        
        if not response.success:
            return self._fallback_warning_narrative(phase, event_type, region_context)
        
        return response
    
    async def analyze_cascade_potential(self,
                                      trigger_event: ChaosEvent,
                                      world_state: Dict[str, Any]) -> LLMResponse:
        """
        Analyze potential cascade events using AI reasoning.
        
        Args:
            trigger_event: The event that might cause cascades
            world_state: Current state of the game world
            
        Returns:
            LLMResponse with cascade analysis (JSON format)
        """
        if not self.enabled or not self._initialized:
            return self._fallback_cascade_analysis(trigger_event, world_state)
        
        prompt = self._build_cascade_analysis_prompt(trigger_event, world_state)
        response = await self._call_llm(prompt, "cascade_analysis")
        
        if not response.success:
            return self._fallback_cascade_analysis(trigger_event, world_state)
        
        return response
    
    async def suggest_mitigations(self,
                                event: ChaosEvent,
                                available_resources: Dict[str, Any]) -> LLMResponse:
        """
        Generate dynamic mitigation suggestions based on context.
        
        Args:
            event: The chaos event to mitigate
            available_resources: Available resources and capabilities
            
        Returns:
            LLMResponse with mitigation suggestions (JSON format)
        """
        if not self.enabled or not self._initialized:
            return self._fallback_mitigation_suggestions(event, available_resources)
        
        prompt = self._build_mitigation_prompt(event, available_resources)
        response = await self._call_llm(prompt, "mitigation_suggestions")
        
        if not response.success:
            return self._fallback_mitigation_suggestions(event, available_resources)
        
        return response
    
    async def _call_llm(self, prompt: str, operation_type: str) -> LLMResponse:
        """Call the available LLM service"""
        try:
            # Try OpenAI first if available
            if self.openai_client and 'gpt' in self.model_preference.lower():
                return await self._call_openai(prompt, operation_type)
            
            # Try Anthropic if available
            if self.anthropic_client and 'claude' in self.model_preference.lower():
                return await self._call_anthropic(prompt, operation_type)
            
            # Fallback to any available client
            if self.openai_client:
                return await self._call_openai(prompt, operation_type)
            elif self.anthropic_client:
                return await self._call_anthropic(prompt, operation_type)
            
            return LLMResponse(
                content="",
                success=False,
                model_used="none",
                error="No LLM providers available"
            )
            
        except Exception as e:
            logger.error(f"LLM call failed for {operation_type}: {e}")
            return LLMResponse(
                content="",
                success=False,
                model_used="error",
                error=str(e)
            )
    
    async def _call_openai(self, prompt: str, operation_type: str) -> LLMResponse:
        """Call OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=self.model_preference if 'gpt' in self.model_preference.lower() else 'gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a narrative AI for a fantasy game's chaos system. Generate vivid, contextually appropriate content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                success=True,
                model_used=response.model,
                tokens_used=response.usage.total_tokens if response.usage else None
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                model_used="openai_error",
                error=str(e)
            )
    
    async def _call_anthropic(self, prompt: str, operation_type: str) -> LLMResponse:
        """Call Anthropic API"""
        try:
            response = await self.anthropic_client.messages.create(
                model=self.model_preference if 'claude' in self.model_preference.lower() else 'claude-3-haiku-20240307',
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": f"You are a narrative AI for a fantasy game's chaos system. Generate vivid, contextually appropriate content.\n\n{prompt}"}
                ]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                success=True,
                model_used=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            )
            
        except Exception as e:
            return LLMResponse(
                content="",
                success=False,
                model_used="anthropic_error",
                error=str(e)
            )
    
    def _build_event_description_prompt(self, event_type: ChaosEventType, severity: EventSeverity, context: Dict[str, Any]) -> str:
        """Build prompt for event description generation"""
        prompt = f"""Generate a dynamic, engaging description for a {event_type.value} event with {severity.value} severity.

Context:
- Affected regions: {context.get('affected_regions', [])}
- Recent events: {context.get('recent_events', [])}
- Current political climate: {context.get('political_climate', 'stable')}
- Economic situation: {context.get('economic_situation', 'stable')}
- Player actions: {context.get('player_actions', [])}
- Regional characteristics: {context.get('regional_characteristics', {})}

Requirements:
- Write in third person, present tense
- 2-3 sentences maximum
- Include specific regional or contextual details when available
- Match the severity level in description intensity
- Make it feel organic to the current world state

Generate only the description text, no additional formatting or explanations."""

        return prompt
    
    def _build_warning_prompt(self, phase: str, event_type: str, region_context: Dict[str, Any]) -> str:
        """Build prompt for warning narrative generation"""
        phase_descriptions = {
            'rumor': 'subtle hints and whispers that something is brewing',
            'early': 'clear signs that trouble is building',
            'imminent': 'immediate precursors indicating the event is about to happen'
        }
        
        prompt = f"""Generate a {phase} phase warning for an impending {event_type} event.

Phase description: {phase_descriptions.get(phase, 'warning signs')}

Regional context:
- Region name: {region_context.get('region_name', 'the region')}
- Culture: {region_context.get('culture', 'unknown')}
- Government: {region_context.get('government_type', 'unknown')}
- Economic focus: {region_context.get('economic_focus', 'unknown')}
- Recent tensions: {region_context.get('tensions', [])}
- Key NPCs: {region_context.get('key_npcs', [])}

Generate a JSON response with:
{{
    "description": "Main warning description",
    "clues": ["observable clue 1", "observable clue 2"],
    "indicators": ["hidden indicator 1", "hidden indicator 2"]
}}

Make the warning appropriate for the phase intensity and include specific regional details."""

        return prompt
    
    def _build_cascade_analysis_prompt(self, trigger_event: ChaosEvent, world_state: Dict[str, Any]) -> str:
        """Build prompt for cascade analysis"""
        prompt = f"""Analyze potential cascade events from this trigger event:

Trigger Event:
- Type: {trigger_event.event_type.value}
- Severity: {trigger_event.severity.value}
- Regions: {trigger_event.affected_regions}
- Description: {trigger_event.description}

World State:
- Current tensions: {world_state.get('tensions', {})}
- Economic stability: {world_state.get('economic_stability', {})}
- Military situations: {world_state.get('military_situations', {})}
- Recent events: {world_state.get('recent_events', [])}
- Resource availability: {world_state.get('resources', {})}

Analyze realistic cascade events that could result. Consider:
- Logical cause-and-effect relationships
- Regional interconnections
- Economic dependencies
- Political ramifications
- Social impacts

Generate a JSON response with potential cascades:
{{
    "cascades": [
        {{
            "event_type": "cascade_event_type",
            "probability": 0.0-1.0,
            "delay_hours": number,
            "affected_regions": ["region1", "region2"],
            "reasoning": "why this cascade makes sense",
            "severity_modifier": -1 to +1
        }}
    ]
}}

Focus on the most realistic and narratively interesting cascades (max 3)."""

        return prompt
    
    def _build_mitigation_prompt(self, event: ChaosEvent, available_resources: Dict[str, Any]) -> str:
        """Build prompt for mitigation suggestions"""
        prompt = f"""Suggest effective mitigation strategies for this chaos event:

Event Details:
- Type: {event.event_type.value}
- Severity: {event.severity.value}
- Regions: {event.affected_regions}
- Description: {event.description}

Available Resources:
- Military assets: {available_resources.get('military', {})}
- Economic resources: {available_resources.get('economic', {})}
- Diplomatic options: {available_resources.get('diplomatic', {})}
- Infrastructure: {available_resources.get('infrastructure', {})}
- Key figures: {available_resources.get('key_figures', [])}
- Player capabilities: {available_resources.get('player_capabilities', [])}

Generate realistic mitigation strategies as JSON:
{{
    "mitigations": [
        {{
            "type": "mitigation_category",
            "name": "specific_action_name",
            "description": "what this action involves",
            "effectiveness": 0.0-1.0,
            "resource_cost": "what resources this requires",
            "duration_hours": number,
            "prerequisites": ["what conditions must be met"],
            "side_effects": ["potential unintended consequences"]
        }}
    ]
}}

Focus on creative, contextually appropriate solutions (max 4)."""

        return prompt
    
    def _fallback_event_description(self, event_type: ChaosEventType, severity: EventSeverity, context: Dict[str, Any]) -> LLMResponse:
        """Fallback to template-based event descriptions"""
        templates = self.fallback_templates.get('event_descriptions', {}).get(event_type.value, {})
        severity_templates = templates.get(severity.value, templates.get('default', ['A chaos event occurs.']))
        
        import random
        description = random.choice(severity_templates)
        
        # Simple context substitution
        regions = context.get('affected_regions', ['the region'])
        region_text = regions[0] if len(regions) == 1 else f"{', '.join(regions[:-1])} and {regions[-1]}"
        description = description.replace('{regions}', region_text)
        description = description.replace('{severity}', severity.value)
        
        return LLMResponse(
            content=description,
            success=True,
            model_used="template_fallback",
            context_used=context
        )
    
    def _fallback_warning_narrative(self, phase: str, event_type: str, region_context: Dict[str, Any]) -> LLMResponse:
        """Fallback to template-based warnings"""
        templates = self.fallback_templates.get('warning_narratives', {})
        phase_templates = templates.get(phase, {})
        event_templates = phase_templates.get(event_type, phase_templates.get('default', {}))
        
        response_data = {
            "description": event_templates.get('description', f'{phase.title()} signs of {event_type} detected'),
            "clues": event_templates.get('clues', [f'Signs of {event_type}']),
            "indicators": event_templates.get('indicators', [f'Monitoring {event_type} situation'])
        }
        
        return LLMResponse(
            content=json.dumps(response_data),
            success=True,
            model_used="template_fallback",
            context_used=region_context
        )
    
    def _fallback_cascade_analysis(self, trigger_event: ChaosEvent, world_state: Dict[str, Any]) -> LLMResponse:
        """Fallback to rule-based cascade analysis"""
        # Simple rule-based cascades
        cascades = []
        
        if trigger_event.event_type == ChaosEventType.ECONOMIC_COLLAPSE:
            cascades.append({
                "event_type": "resource_scarcity",
                "probability": 0.6,
                "delay_hours": 24,
                "affected_regions": trigger_event.affected_regions,
                "reasoning": "Economic collapse leads to resource distribution problems",
                "severity_modifier": 0
            })
        
        response_data = {"cascades": cascades}
        
        return LLMResponse(
            content=json.dumps(response_data),
            success=True,
            model_used="rule_fallback",
            context_used=world_state
        )
    
    def _fallback_mitigation_suggestions(self, event: ChaosEvent, available_resources: Dict[str, Any]) -> LLMResponse:
        """Fallback to template-based mitigation suggestions"""
        mitigations = []
        
        if event.event_type == ChaosEventType.POLITICAL_UPHEAVAL:
            mitigations.append({
                "type": "diplomatic",
                "name": "Emergency Negotiations",
                "description": "Initiate emergency diplomatic talks with all parties",
                "effectiveness": 0.7,
                "resource_cost": "Diplomatic favor",
                "duration_hours": 48,
                "prerequisites": ["Access to faction leaders"],
                "side_effects": ["May reveal weaknesses"]
            })
        
        response_data = {"mitigations": mitigations}
        
        return LLMResponse(
            content=json.dumps(response_data),
            success=True,
            model_used="template_fallback",
            context_used=available_resources
        )
    
    def _load_fallback_templates(self) -> Dict[str, Any]:
        """Load fallback templates for when LLM is unavailable"""
        return {
            'event_descriptions': {
                'political_upheaval': {
                    'minor': ['Political tensions rise in {regions} as local disputes emerge.'],
                    'moderate': ['Significant political unrest grips {regions} as factions clash for control.'],
                    'major': ['Violent political upheaval rocks {regions} as the government struggles to maintain order.'],
                    'critical': ['Revolutionary fervor sweeps through {regions} as the established order crumbles.'],
                    'catastrophic': ['Complete political collapse devastates {regions} as all governance breaks down.']
                },
                'economic_collapse': {
                    'minor': ['Economic instability affects trade in {regions}.'],
                    'moderate': ['Market volatility and business failures spread throughout {regions}.'],
                    'major': ['Economic systems in {regions} face severe disruption and widespread bankruptcies.'],
                    'critical': ['Financial catastrophe engulfs {regions} as markets crash and currency fails.'],
                    'catastrophic': ['Total economic collapse destroys all commerce and trade in {regions}.']
                }
            },
            'warning_narratives': {
                'rumor': {
                    'default': {
                        'description': 'Whispers of concern circulate among the populace',
                        'clues': ['Unusual activity', 'Hushed conversations'],
                        'indicators': ['Rising tension metrics', 'Subtle behavioral changes']
                    }
                }
            }
        } 