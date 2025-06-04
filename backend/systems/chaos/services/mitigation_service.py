"""
Mitigation Service

Manages chaos mitigation factors and their effects on pressure reduction.
Handles diplomatic actions, stability measures, and positive interventions.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from backend.infrastructure.systems.chaos.models.chaos_state import MitigationFactor, ChaosState
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData, PressureSource
from backend.systems.chaos.core.config import ChaosConfig


@dataclass
class MitigationEffect:
    """Represents the effect of a mitigation action"""
    mitigation_id: str
    source_type: str
    source_id: str
    effect_type: str
    base_effectiveness: float
    duration_hours: float
    affected_sources: List[str] = field(default_factory=list)
    affected_regions: List[str] = field(default_factory=list)
    conditions: Dict[str, Any] = field(default_factory=dict)
    multipliers: Dict[str, float] = field(default_factory=dict)
    description: str = ""


class MitigationService:
    """
    Service for managing chaos mitigation factors and their effects.
    Enhanced with LLM-powered dynamic mitigation suggestions.
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # LLM service reference (set by chaos manager)
        self.llm_service: Optional[Any] = None
        
        # Mitigation effectiveness configurations
        self.mitigation_configs = self._initialize_mitigation_configs()
        
        # Tracking active mitigations
        self.active_mitigations: Dict[str, MitigationFactor] = {}
        self.mitigation_history: List[MitigationFactor] = []
        
        # Performance tracking
        self.mitigation_applications = 0
        self.total_effectiveness_applied = 0.0
        self.last_cleanup = datetime.now()
        
        # LLM metrics
        self.llm_suggestions_generated = 0
        self.template_suggestions_generated = 0
    
    def set_llm_service(self, llm_service: Any) -> None:
        """Set the LLM service for enhanced mitigation suggestions"""
        self.llm_service = llm_service
    
    def _initialize_mitigation_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mitigation configurations for different types"""
        return {
            # Diplomatic Actions
            'diplomatic_treaty': {
                'base_effectiveness': 0.4,
                'duration_hours': 720.0,  # 30 days
                'affects_sources': ['diplomatic_tension', 'faction_conflict'],
                'decay_rate': 0.02,  # 2% per day
                'max_concurrent': 5,
                'stacking_multiplier': 0.8  # Diminishing returns
            },
            'peace_negotiations': {
                'base_effectiveness': 0.3,
                'duration_hours': 168.0,  # 7 days
                'affects_sources': ['faction_conflict', 'military_buildup'],
                'decay_rate': 0.05,
                'max_concurrent': 3,
                'stacking_multiplier': 0.7
            },
            'alliance_formation': {
                'base_effectiveness': 0.5,
                'duration_hours': 1440.0,  # 60 days
                'affects_sources': ['diplomatic_tension', 'faction_conflict'],
                'decay_rate': 0.01,
                'max_concurrent': 3,
                'stacking_multiplier': 0.9
            },
            'trade_agreement': {
                'base_effectiveness': 0.25,
                'duration_hours': 720.0,  # 30 days
                'affects_sources': ['economic_instability', 'resource_scarcity'],
                'decay_rate': 0.03,
                'max_concurrent': 10,
                'stacking_multiplier': 0.9
            },
            
            # Quest Completions
            'main_quest_completion': {
                'base_effectiveness': 0.6,
                'duration_hours': 168.0,  # 7 days
                'affects_sources': ['all'],  # Affects all pressure sources
                'decay_rate': 0.1,  # Quick decay but powerful
                'max_concurrent': 1,
                'stacking_multiplier': 1.0
            },
            'faction_quest_completion': {
                'base_effectiveness': 0.3,
                'duration_hours': 72.0,  # 3 days
                'affects_sources': ['faction_conflict', 'diplomatic_tension'],
                'decay_rate': 0.08,
                'max_concurrent': 5,
                'stacking_multiplier': 0.8
            },
            'economic_quest_completion': {
                'base_effectiveness': 0.25,
                'duration_hours': 120.0,  # 5 days
                'affects_sources': ['economic_instability', 'resource_scarcity'],
                'decay_rate': 0.06,
                'max_concurrent': 5,
                'stacking_multiplier': 0.9
            },
            'exploration_quest_completion': {
                'base_effectiveness': 0.2,
                'duration_hours': 96.0,  # 4 days
                'affects_sources': ['environmental_pressure', 'resource_scarcity'],
                'decay_rate': 0.05,
                'max_concurrent': 3,
                'stacking_multiplier': 0.8
            },
            
            # Infrastructure Development
            'infrastructure_construction': {
                'base_effectiveness': 0.35,
                'duration_hours': 2160.0,  # 90 days
                'affects_sources': ['economic_instability', 'population_stress'],
                'decay_rate': 0.005,  # Very slow decay
                'max_concurrent': 20,
                'stacking_multiplier': 0.95  # Minimal diminishing returns
            },
            'military_fortification': {
                'base_effectiveness': 0.4,
                'duration_hours': 1440.0,  # 60 days
                'affects_sources': ['military_buildup', 'faction_conflict'],
                'decay_rate': 0.01,
                'max_concurrent': 10,
                'stacking_multiplier': 0.9
            },
            'trade_route_establishment': {
                'base_effectiveness': 0.3,
                'duration_hours': 720.0,  # 30 days
                'affects_sources': ['economic_instability', 'resource_scarcity'],
                'decay_rate': 0.02,
                'max_concurrent': 15,
                'stacking_multiplier': 0.95
            },
            'research_facility': {
                'base_effectiveness': 0.2,
                'duration_hours': 1440.0,  # 60 days
                'affects_sources': ['all'],  # Long-term benefits to all areas
                'decay_rate': 0.005,
                'max_concurrent': 5,
                'stacking_multiplier': 0.9
            },
            
            # Resource Management
            'resource_stockpiling': {
                'base_effectiveness': 0.3,
                'duration_hours': 336.0,  # 14 days
                'affects_sources': ['resource_scarcity', 'economic_instability'],
                'decay_rate': 0.04,
                'max_concurrent': 10,
                'stacking_multiplier': 0.8
            },
            'agricultural_investment': {
                'base_effectiveness': 0.4,
                'duration_hours': 720.0,  # 30 days
                'affects_sources': ['resource_scarcity', 'population_stress'],
                'decay_rate': 0.02,
                'max_concurrent': 8,
                'stacking_multiplier': 0.9
            },
            'mining_expansion': {
                'base_effectiveness': 0.35,
                'duration_hours': 1440.0,  # 60 days
                'affects_sources': ['resource_scarcity', 'economic_instability'],
                'decay_rate': 0.015,
                'max_concurrent': 6,
                'stacking_multiplier': 0.85
            },
            
            # Governance & Leadership
            'effective_leadership': {
                'base_effectiveness': 0.5,
                'duration_hours': 168.0,  # 7 days
                'affects_sources': ['all'],
                'decay_rate': 0.08,  # Requires constant reinforcement
                'max_concurrent': 1,
                'stacking_multiplier': 1.0
            },
            'judicial_reform': {
                'base_effectiveness': 0.3,
                'duration_hours': 1440.0,  # 60 days
                'affects_sources': ['corruption', 'population_stress'],
                'decay_rate': 0.01,
                'max_concurrent': 3,
                'stacking_multiplier': 0.9
            },
            'administrative_efficiency': {
                'base_effectiveness': 0.25,
                'duration_hours': 720.0,  # 30 days
                'affects_sources': ['corruption', 'economic_instability'],
                'decay_rate': 0.02,
                'max_concurrent': 5,
                'stacking_multiplier': 0.9
            },
            
            # Social & Cultural
            'cultural_festival': {
                'base_effectiveness': 0.15,
                'duration_hours': 72.0,  # 3 days
                'affects_sources': ['population_stress', 'faction_conflict'],
                'decay_rate': 0.1,  # Short but immediate effect
                'max_concurrent': 3,
                'stacking_multiplier': 0.7
            },
            'education_initiative': {
                'base_effectiveness': 0.2,
                'duration_hours': 1440.0,  # 60 days
                'affects_sources': ['population_stress', 'corruption'],
                'decay_rate': 0.005,  # Long-term benefits
                'max_concurrent': 5,
                'stacking_multiplier': 0.95
            },
            'religious_ceremony': {
                'base_effectiveness': 0.1,
                'duration_hours': 48.0,  # 2 days
                'affects_sources': ['population_stress', 'faction_conflict'],
                'decay_rate': 0.15,  # Very quick decay
                'max_concurrent': 2,
                'stacking_multiplier': 0.6
            },
            
            # Emergency Responses
            'disaster_relief': {
                'base_effectiveness': 0.6,
                'duration_hours': 168.0,  # 7 days
                'affects_sources': ['environmental_pressure', 'population_stress'],
                'decay_rate': 0.08,
                'max_concurrent': 3,
                'stacking_multiplier': 0.8
            },
            'crisis_management': {
                'base_effectiveness': 0.4,
                'duration_hours': 120.0,  # 5 days
                'affects_sources': ['all'],  # Emergency response affects all
                'decay_rate': 0.1,
                'max_concurrent': 2,
                'stacking_multiplier': 0.9
            }
        }
    
    async def apply_mitigation(self, mitigation_type: str, source_id: str, 
                             source_type: str, magnitude: float = 1.0,
                             affected_regions: List[str] = None,
                             additional_context: Dict[str, Any] = None) -> Optional[MitigationFactor]:
        """Apply a mitigation factor to the chaos system"""
        if mitigation_type not in self.mitigation_configs:
            print(f"Warning: Unknown mitigation type '{mitigation_type}', applying generic mitigation")
            return await self._apply_generic_mitigation(mitigation_type, source_id, source_type, magnitude, affected_regions, additional_context)
        
        config = self.mitigation_configs[mitigation_type]
        
        # Check if we've exceeded maximum concurrent instances
        active_count = self._count_active_mitigations(mitigation_type)
        if active_count >= config['max_concurrent']:
            print(f"Maximum concurrent instances of {mitigation_type} reached ({config['max_concurrent']})")
            return None
        
        # Calculate effectiveness with context modifiers
        base_effectiveness = config['base_effectiveness'] * magnitude
        final_effectiveness = self._apply_context_modifiers(
            base_effectiveness, mitigation_type, additional_context or {}
        )
        
        # Apply stacking penalty if there are other instances
        if active_count > 0:
            stacking_penalty = config['stacking_multiplier'] ** active_count
            final_effectiveness *= stacking_penalty
        
        # Create mitigation factor
        mitigation = MitigationFactor(
            mitigation_id=str(uuid4()),
            source_type=source_type,
            source_id=source_id,
            mitigation_type=mitigation_type,
            effectiveness=final_effectiveness,
            applied_at=datetime.now(),
            duration_hours=config['duration_hours'],
            affected_sources=config['affects_sources'].copy(),
            affected_regions=affected_regions or [],
            decay_rate=config['decay_rate'],
            description=additional_context.get('description', f'{mitigation_type} applied by {source_type}'),
            metadata=additional_context or {}
        )
        
        # Store mitigation
        self.active_mitigations[mitigation.mitigation_id] = mitigation
        self.mitigation_history.append(mitigation)
        
        # Update tracking
        self.mitigation_applications += 1
        self.total_effectiveness_applied += final_effectiveness
        
        print(f"Applied mitigation: {mitigation_type} (effectiveness: {final_effectiveness:.2f})")
        return mitigation
    
    async def _apply_generic_mitigation(self, mitigation_type: str, source_id: str,
                                      source_type: str, magnitude: float,
                                      affected_regions: List[str],
                                      additional_context: Dict[str, Any]) -> Optional[MitigationFactor]:
        """Apply a generic mitigation for unknown types"""
        mitigation = MitigationFactor(
            mitigation_id=str(uuid4()),
            source_type=source_type,
            source_id=source_id,
            mitigation_type=mitigation_type,
            effectiveness=0.2 * magnitude,  # Conservative generic effectiveness
            applied_at=datetime.now(),
            duration_hours=72.0,  # 3 days default
            affected_sources=['all'],
            affected_regions=affected_regions or [],
            decay_rate=0.05,
            description=additional_context.get('description', f'Generic {mitigation_type} applied'),
            metadata=additional_context or {}
        )
        
        self.active_mitigations[mitigation.mitigation_id] = mitigation
        self.mitigation_history.append(mitigation)
        return mitigation
    
    def _apply_context_modifiers(self, base_effectiveness: float, 
                               mitigation_type: str, context: Dict[str, Any]) -> float:
        """Apply context-based modifiers to mitigation effectiveness"""
        effectiveness = base_effectiveness
        
        # Resource availability modifiers
        if 'resource_availability' in context:
            resource_mult = max(0.5, min(2.0, context['resource_availability']))
            effectiveness *= resource_mult
        
        # Public support modifiers
        if 'public_support' in context:
            support_mult = 0.7 + (context['public_support'] * 0.6)  # 0.7 to 1.3 multiplier
            effectiveness *= support_mult
        
        # Crisis urgency modifiers (higher urgency = higher effectiveness)
        if 'crisis_urgency' in context:
            urgency_mult = 1.0 + (context['crisis_urgency'] * 0.5)  # Up to +50% in urgent situations
            effectiveness *= urgency_mult
        
        # Diplomatic relations modifiers (for diplomatic mitigations)
        if mitigation_type.startswith('diplomatic') and 'diplomatic_relations' in context:
            relations = context['diplomatic_relations']
            if relations > 0.5:
                effectiveness *= 1.2  # Good relations boost effectiveness
            elif relations < 0.3:
                effectiveness *= 0.8  # Poor relations reduce effectiveness
        
        # Economic conditions modifiers (for economic mitigations)
        if ('economic' in mitigation_type or 'trade' in mitigation_type) and 'economic_stability' in context:
            stability = context['economic_stability']
            if stability > 0.6:
                effectiveness *= 1.1  # Stable economy helps
            elif stability < 0.4:
                effectiveness *= 0.9  # Unstable economy hinders
        
        return max(0.0, effectiveness)  # Ensure non-negative
    
    def _count_active_mitigations(self, mitigation_type: str) -> int:
        """Count currently active mitigations of a specific type"""
        now = datetime.now()
        return sum(1 for m in self.active_mitigations.values() 
                  if m.mitigation_type == mitigation_type and m.expires_at > now)
    
    def calculate_total_mitigation_effect(self, pressure_data: PressureData, 
                                        chaos_state: ChaosState) -> Dict[str, float]:
        """Calculate total mitigation effects across all pressure sources"""
        self._cleanup_expired_mitigations()
        
        mitigation_effects = {}
        now = datetime.now()
        
        # Initialize all pressure sources with zero mitigation
        for source in PressureSource:
            mitigation_effects[source.value] = 0.0
        
        # Calculate effects from active mitigations
        for mitigation in self.active_mitigations.values():
            if mitigation.expires_at <= now:
                continue
            
            current_effectiveness = self._calculate_current_effectiveness(mitigation)
            
            # Apply to specified pressure sources
            for source in mitigation.affected_sources:
                if source == 'all':
                    # Apply to all sources
                    for pressure_source in PressureSource:
                        mitigation_effects[pressure_source.value] += current_effectiveness
                elif source in mitigation_effects:
                    mitigation_effects[source] += current_effectiveness
        
        # Cap mitigation effects (can't reduce pressure below 0 or above 100%)
        for source in mitigation_effects:
            mitigation_effects[source] = max(0.0, min(1.0, mitigation_effects[source]))
        
        return mitigation_effects
    
    def _calculate_current_effectiveness(self, mitigation: MitigationFactor) -> float:
        """Calculate current effectiveness accounting for decay"""
        now = datetime.now()
        hours_active = (now - mitigation.applied_at).total_seconds() / 3600
        
        # Apply decay
        decay_factor = 1.0 - (mitigation.decay_rate * (hours_active / 24.0))  # decay per day
        decay_factor = max(0.0, decay_factor)
        
        return mitigation.effectiveness * decay_factor
    
    def _cleanup_expired_mitigations(self) -> None:
        """Remove expired mitigations"""
        now = datetime.now()
        
        # Only clean up if it's been more than an hour since last cleanup
        if (now - self.last_cleanup).total_seconds() < 3600:
            return
        
        expired_ids = [
            mid for mid, mitigation in self.active_mitigations.items()
            if mitigation.expires_at <= now
        ]
        
        for mid in expired_ids:
            del self.active_mitigations[mid]
        
        if expired_ids:
            print(f"Cleaned up {len(expired_ids)} expired mitigations")
        
        self.last_cleanup = now
    
    def get_mitigation_summary(self) -> Dict[str, Any]:
        """Get a summary of current mitigation status"""
        self._cleanup_expired_mitigations()
        
        active_by_type = {}
        total_effectiveness_by_source = {}
        
        # Initialize source tracking
        for source in PressureSource:
            total_effectiveness_by_source[source.value] = 0.0
        
        # Analyze active mitigations
        for mitigation in self.active_mitigations.values():
            # Count by type
            if mitigation.mitigation_type not in active_by_type:
                active_by_type[mitigation.mitigation_type] = 0
            active_by_type[mitigation.mitigation_type] += 1
            
            # Sum effectiveness by source
            current_effectiveness = self._calculate_current_effectiveness(mitigation)
            for source in mitigation.affected_sources:
                if source == 'all':
                    for pressure_source in PressureSource:
                        total_effectiveness_by_source[pressure_source.value] += current_effectiveness
                elif source in total_effectiveness_by_source:
                    total_effectiveness_by_source[source] += current_effectiveness
        
        return {
            'total_active_mitigations': len(self.active_mitigations),
            'active_by_type': active_by_type,
            'effectiveness_by_source': total_effectiveness_by_source,
            'total_applications_lifetime': self.mitigation_applications,
            'average_effectiveness': (
                self.total_effectiveness_applied / max(1, self.mitigation_applications)
            ),
            'llm_suggestions_generated': self.llm_suggestions_generated,
            'template_suggestions_generated': self.template_suggestions_generated
        }
    
    async def get_mitigation_recommendations(self, chaos_event: Any,
                                           available_resources: Dict[str, Any],
                                           pressure_data: Optional[PressureData] = None,
                                           chaos_state: Optional[ChaosState] = None) -> List[Dict[str, Any]]:
        """
        Get context-aware mitigation recommendations using LLM analysis when available.
        
        Args:
            chaos_event: The chaos event to mitigate
            available_resources: Available resources and capabilities
            pressure_data: Current pressure data (optional)
            chaos_state: Current chaos state (optional)
            
        Returns:
            List of mitigation recommendations
        """
        
        # Try LLM-powered recommendations first
        if self.llm_service:
            try:
                llm_response = await self.llm_service.suggest_mitigations(chaos_event, available_resources)
                
                if llm_response.success:
                    self.llm_suggestions_generated += 1
                    return await self._parse_llm_mitigation_suggestions(llm_response.content, available_resources)
                    
            except Exception as e:
                print(f"LLM mitigation suggestions failed: {e}")
                # Continue to template-based recommendations
        
        # Fallback to template-based recommendations
        self.template_suggestions_generated += 1
        return self._get_template_mitigation_recommendations(chaos_event, available_resources, pressure_data, chaos_state)
    
    async def _parse_llm_mitigation_suggestions(self, llm_content: str, 
                                              available_resources: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse LLM response into structured mitigation recommendations"""
        try:
            import json
            suggestions_data = json.loads(llm_content)
            recommendations = []
            
            for mitigation_info in suggestions_data.get('mitigations', []):
                recommendation = {
                    'type': mitigation_info.get('type', 'diplomatic'),
                    'name': mitigation_info.get('name', 'Unknown Mitigation'),
                    'description': mitigation_info.get('description', 'LLM-suggested mitigation'),
                    'effectiveness': mitigation_info.get('effectiveness', 0.5),
                    'resource_cost': mitigation_info.get('resource_cost', 'Unknown'),
                    'duration_hours': mitigation_info.get('duration_hours', 72),
                    'prerequisites': mitigation_info.get('prerequisites', []),
                    'side_effects': mitigation_info.get('side_effects', []),
                    'priority': self._calculate_recommendation_priority(mitigation_info, available_resources),
                    'feasibility': self._assess_feasibility(mitigation_info, available_resources),
                    'source': 'llm'
                }
                recommendations.append(recommendation)
            
            # Sort by priority and feasibility
            recommendations.sort(key=lambda x: (x['priority'] * x['feasibility']), reverse=True)
            return recommendations[:5]  # Return top 5
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Failed to parse LLM mitigation suggestions: {e}")
            return []
    
    def _calculate_recommendation_priority(self, mitigation_info: Dict[str, Any], 
                                         available_resources: Dict[str, Any]) -> float:
        """Calculate priority score for a mitigation recommendation"""
        effectiveness = mitigation_info.get('effectiveness', 0.5)
        duration = mitigation_info.get('duration_hours', 72)
        
        # Higher effectiveness = higher priority
        priority = effectiveness
        
        # Longer duration = slightly higher priority (lasting effects)
        duration_bonus = min(0.2, duration / 1000.0)  # Cap at 20% bonus
        priority += duration_bonus
        
        return min(1.0, priority)
    
    def _assess_feasibility(self, mitigation_info: Dict[str, Any], 
                          available_resources: Dict[str, Any]) -> float:
        """Assess how feasible a mitigation is given available resources"""
        prerequisites = mitigation_info.get('prerequisites', [])
        resource_cost = mitigation_info.get('resource_cost', '').lower()
        
        feasibility = 1.0
        
        # Check prerequisites
        for prereq in prerequisites:
            if isinstance(prereq, str):
                # Simple string matching for now
                prereq_lower = prereq.lower()
                found = False
                for resource_type, resources in available_resources.items():
                    if resource_type.lower() in prereq_lower or prereq_lower in str(resources).lower():
                        found = True
                        break
                if not found:
                    feasibility *= 0.7  # Reduce feasibility for missing prerequisites
        
        # Check resource costs
        if 'expensive' in resource_cost or 'high' in resource_cost:
            economic_resources = available_resources.get('economic', {})
            if not economic_resources or str(economic_resources).lower() in ['limited', 'low', 'poor']:
                feasibility *= 0.6
        
        return max(0.1, feasibility)  # Minimum 10% feasibility
    
    def _get_template_mitigation_recommendations(self, chaos_event: Any,
                                               available_resources: Dict[str, Any],
                                               pressure_data: Optional[PressureData] = None,
                                               chaos_state: Optional[ChaosState] = None) -> List[Dict[str, Any]]:
        """Generate template-based mitigation recommendations"""
        recommendations = []
        
        # Determine event type and suggest appropriate mitigations
        event_type = getattr(chaos_event, 'event_type', None)
        event_severity = getattr(chaos_event, 'severity', None)
        
        if event_type:
            event_type_str = event_type.value if hasattr(event_type, 'value') else str(event_type)
            
            # Map event types to mitigation strategies
            if 'political' in event_type_str.lower():
                recommendations.extend([
                    {
                        'type': 'diplomatic',
                        'name': 'Emergency Diplomatic Talks',
                        'description': 'Initiate emergency negotiations with key political factions',
                        'effectiveness': 0.7,
                        'resource_cost': 'Diplomatic resources',
                        'duration_hours': 48,
                        'prerequisites': ['Access to faction leaders'],
                        'side_effects': ['May reveal political weaknesses'],
                        'priority': 0.8,
                        'feasibility': 0.9,
                        'source': 'template'
                    },
                    {
                        'type': 'governance',
                        'name': 'Leadership Demonstration',
                        'description': 'Demonstrate strong, decisive leadership to restore confidence',
                        'effectiveness': 0.6,
                        'resource_cost': 'Political capital',
                        'duration_hours': 72,
                        'prerequisites': ['Authority position'],
                        'side_effects': ['Increased scrutiny of future decisions'],
                        'priority': 0.7,
                        'feasibility': 0.8,
                        'source': 'template'
                    }
                ])
            
            if 'economic' in event_type_str.lower():
                recommendations.extend([
                    {
                        'type': 'economic',
                        'name': 'Emergency Economic Stimulus',
                        'description': 'Inject resources into the economy to stabilize markets',
                        'effectiveness': 0.6,
                        'resource_cost': 'Economic reserves',
                        'duration_hours': 168,  # 1 week
                        'prerequisites': ['Available funds'],
                        'side_effects': ['Depletion of reserves'],
                        'priority': 0.8,
                        'feasibility': 0.7,
                        'source': 'template'
                    },
                    {
                        'type': 'trade',
                        'name': 'Emergency Trade Agreements',
                        'description': 'Establish temporary trade deals to stabilize supply chains',
                        'effectiveness': 0.5,
                        'resource_cost': 'Trade concessions',
                        'duration_hours': 240,  # 10 days
                        'prerequisites': ['Trading partners'],
                        'side_effects': ['Potential dependency'],
                        'priority': 0.6,
                        'feasibility': 0.8,
                        'source': 'template'
                    }
                ])
            
            if 'social' in event_type_str.lower():
                recommendations.extend([
                    {
                        'type': 'social',
                        'name': 'Community Outreach Program',
                        'description': 'Deploy community leaders to address grievances and concerns',
                        'effectiveness': 0.5,
                        'resource_cost': 'Personnel and time',
                        'duration_hours': 120,  # 5 days
                        'prerequisites': ['Trusted community figures'],
                        'side_effects': ['Exposure of deeper issues'],
                        'priority': 0.7,
                        'feasibility': 0.9,
                        'source': 'template'
                    },
                    {
                        'type': 'humanitarian',
                        'name': 'Emergency Aid Distribution',
                        'description': 'Distribute emergency supplies and aid to affected populations',
                        'effectiveness': 0.4,
                        'resource_cost': 'Supplies and logistics',
                        'duration_hours': 48,
                        'prerequisites': ['Available supplies'],
                        'side_effects': ['Resource depletion'],
                        'priority': 0.6,
                        'feasibility': 0.8,
                        'source': 'template'
                    }
                ])
        
        # Add general mitigations that work for any crisis
        recommendations.extend([
            {
                'type': 'information',
                'name': 'Crisis Communication Campaign',
                'description': 'Launch coordinated communication to manage public perception',
                'effectiveness': 0.3,
                'resource_cost': 'Communication resources',
                'duration_hours': 72,
                'prerequisites': ['Communication channels'],
                'side_effects': ['Potential backlash if message fails'],
                'priority': 0.5,
                'feasibility': 0.9,
                'source': 'template'
            }
        ])
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: x['priority'] * x['feasibility'], reverse=True)
        return recommendations[:4]  # Return top 4 template recommendations 