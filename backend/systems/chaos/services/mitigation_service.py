"""
Mitigation Service

Manages chaos mitigation factors and their effects on pressure reduction.
Handles diplomatic actions, stability measures, and positive interventions.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import UUID, uuid4
from dataclasses import dataclass, field

from backend.systems.chaos.models.chaos_state import MitigationFactor, ChaosState
from backend.systems.chaos.models.pressure_data import PressureData, PressureSource
from backend.systems.chaos.core.config import ChaosConfig

logger = logging.getLogger(__name__)


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
    Service for managing chaos mitigation factors and their effects
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # Mitigation effectiveness configurations
        self.mitigation_configs = self._initialize_mitigation_configs()
        
        # Tracking active mitigations
        self.active_mitigations: Dict[str, MitigationFactor] = {}
        self.mitigation_history: List[MitigationFactor] = []
        
        # Performance tracking
        self.mitigation_applications = 0
        self.total_effectiveness_applied = 0.0
        self.last_cleanup = datetime.now()
        
        logger.info("Mitigation Service initialized")
    
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
                'stacking_multiplier': 0.8
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
        """Apply a mitigation action and return the created mitigation factor"""
        try:
            # Validate mitigation type
            if mitigation_type not in self.mitigation_configs:
                logger.error(f"Unknown mitigation type: {mitigation_type}")
                return None
            
            config = self.mitigation_configs[mitigation_type]
            
            # Check concurrent limits
            current_count = self._count_active_mitigations(mitigation_type)
            if current_count >= config['max_concurrent']:
                logger.warning(f"Maximum concurrent {mitigation_type} mitigations reached ({current_count})")
                return None
            
            # Calculate effectiveness with stacking penalties
            base_effectiveness = config['base_effectiveness'] * magnitude
            stacking_multiplier = config['stacking_multiplier'] ** current_count
            final_effectiveness = base_effectiveness * stacking_multiplier
            
            # Apply context-based modifiers
            if additional_context:
                final_effectiveness = self._apply_context_modifiers(
                    final_effectiveness, mitigation_type, additional_context
                )
            
            # Create mitigation factor
            mitigation = MitigationFactor(
                mitigation_id=str(uuid4()),
                mitigation_type=mitigation_type,
                source_id=source_id,
                source_type=source_type,
                effectiveness=final_effectiveness,
                duration_hours=config['duration_hours'],
                affected_regions=affected_regions or [],
                affected_sources=config['affects_sources'],
                description=f"{mitigation_type} from {source_type} {source_id}",
                metadata={
                    'base_effectiveness': base_effectiveness,
                    'stacking_multiplier': stacking_multiplier,
                    'magnitude': magnitude,
                    'concurrent_count': current_count,
                    **(additional_context or {})
                }
            )
            
            # Add to active mitigations
            self.active_mitigations[mitigation.mitigation_id] = mitigation
            self.mitigation_history.append(mitigation)
            
            # Update tracking
            self.mitigation_applications += 1
            self.total_effectiveness_applied += final_effectiveness
            
            logger.info(f"Applied mitigation: {mitigation_type} (effectiveness: {final_effectiveness:.3f}, "
                       f"duration: {config['duration_hours']}h)")
            
            return mitigation
            
        except Exception as e:
            logger.error(f"Error applying mitigation {mitigation_type}: {e}")
            return None
    
    def _apply_context_modifiers(self, base_effectiveness: float, 
                               mitigation_type: str, context: Dict[str, Any]) -> float:
        """Apply context-based modifiers to mitigation effectiveness"""
        effectiveness = base_effectiveness
        
        # Success quality modifier
        if 'success_quality' in context:
            quality = context['success_quality']  # 0.0 to 2.0, where 1.0 is normal
            effectiveness *= quality
        
        # Urgency modifier
        if 'urgency' in context:
            urgency = context['urgency']  # 0.0 to 2.0
            if mitigation_type in ['disaster_relief', 'crisis_management']:
                effectiveness *= (1.0 + urgency * 0.5)  # Emergency responses more effective when urgent
        
        # Regional stability modifier
        if 'regional_stability' in context:
            stability = context['regional_stability']  # 0.0 to 1.0
            if stability < 0.3:  # Very unstable regions
                effectiveness *= 1.3  # Higher impact in unstable areas
            elif stability > 0.8:  # Very stable regions
                effectiveness *= 0.8  # Lower impact in stable areas
        
        # Population support modifier
        if 'population_support' in context:
            support = context['population_support']  # 0.0 to 1.0
            effectiveness *= (0.5 + support * 0.8)  # 0.5x to 1.3x based on support
        
        # Resource availability modifier
        if 'resource_availability' in context:
            resources = context['resource_availability']  # 0.0 to 2.0
            effectiveness *= min(2.0, 0.3 + resources * 0.85)  # Better resources = better outcomes
        
        # Faction relations modifier
        if 'faction_relations' in context:
            relations = context['faction_relations']  # -1.0 to 1.0
            if mitigation_type.startswith('diplomatic'):
                effectiveness *= (1.0 + relations * 0.5)  # Better relations help diplomacy
        
        return max(0.0, min(2.0, effectiveness))  # Cap between 0 and 2x effectiveness
    
    def _count_active_mitigations(self, mitigation_type: str) -> int:
        """Count active mitigations of a specific type"""
        count = 0
        for mitigation in self.active_mitigations.values():
            if mitigation.mitigation_type == mitigation_type and mitigation.is_active():
                count += 1
        return count
    
    def calculate_total_mitigation_effect(self, pressure_data: PressureData, 
                                        chaos_state: ChaosState) -> Dict[str, float]:
        """Calculate total mitigation effects for each pressure source"""
        # Clean up expired mitigations first
        self._cleanup_expired_mitigations()
        
        mitigation_effects = {}
        
        # Initialize all pressure sources with 0 mitigation
        for source in PressureSource:
            mitigation_effects[source.value] = 0.0
        
        # Calculate effects from active mitigations
        for mitigation in self.active_mitigations.values():
            if not mitigation.is_active():
                continue
            
            # Calculate current effectiveness (may decay over time)
            current_effectiveness = self._calculate_current_effectiveness(mitigation)
            
            # Apply to affected pressure sources
            affected_sources = mitigation.affected_sources
            if 'all' in affected_sources:
                # Apply to all pressure sources
                for source in PressureSource:
                    mitigation_effects[source.value] += current_effectiveness
            else:
                # Apply to specific sources
                for source_name in affected_sources:
                    if source_name in mitigation_effects:
                        mitigation_effects[source_name] += current_effectiveness
        
        # Apply diminishing returns for high mitigation values
        for source, effect in mitigation_effects.items():
            if effect > 1.0:
                # Logarithmic scaling for very high mitigation
                mitigation_effects[source] = 1.0 + (effect - 1.0) * 0.5
            
            # Cap maximum mitigation at 90%
            mitigation_effects[source] = min(0.9, mitigation_effects[source])
        
        return mitigation_effects
    
    def _calculate_current_effectiveness(self, mitigation: MitigationFactor) -> float:
        """Calculate current effectiveness considering decay"""
        if not mitigation.is_active():
            return 0.0
        
        config = self.mitigation_configs.get(mitigation.mitigation_type)
        if not config:
            return mitigation.effectiveness
        
        # Calculate time-based decay
        age_hours = (datetime.now() - mitigation.applied_at).total_seconds() / 3600.0
        decay_rate = config.get('decay_rate', 0.0)
        
        # Apply exponential decay
        decay_factor = (1.0 - decay_rate) ** (age_hours / 24.0)  # Daily decay rate
        
        current_effectiveness = mitigation.effectiveness * decay_factor
        
        return max(0.0, current_effectiveness)
    
    def _cleanup_expired_mitigations(self) -> None:
        """Remove expired mitigations"""
        # Check if it's time for cleanup
        if (datetime.now() - self.last_cleanup).total_seconds() < 300:  # Every 5 minutes
            return
        
        expired_ids = []
        for mitigation_id, mitigation in self.active_mitigations.items():
            if not mitigation.is_active():
                expired_ids.append(mitigation_id)
        
        for mitigation_id in expired_ids:
            del self.active_mitigations[mitigation_id]
        
        if expired_ids:
            logger.debug(f"Cleaned up {len(expired_ids)} expired mitigations")
        
        self.last_cleanup = datetime.now()
    
    def get_mitigation_summary(self) -> Dict[str, Any]:
        """Get summary of current mitigation state"""
        active_mitigations = list(self.active_mitigations.values())
        active_count = len([m for m in active_mitigations if m.is_active()])
        
        # Group by type
        by_type = {}
        for mitigation in active_mitigations:
            if mitigation.is_active():
                mitigation_type = mitigation.mitigation_type
                if mitigation_type not in by_type:
                    by_type[mitigation_type] = {
                        'count': 0,
                        'total_effectiveness': 0.0,
                        'average_effectiveness': 0.0
                    }
                
                current_effectiveness = self._calculate_current_effectiveness(mitigation)
                by_type[mitigation_type]['count'] += 1
                by_type[mitigation_type]['total_effectiveness'] += current_effectiveness
        
        # Calculate averages
        for type_data in by_type.values():
            if type_data['count'] > 0:
                type_data['average_effectiveness'] = type_data['total_effectiveness'] / type_data['count']
        
        return {
            'active_mitigations': active_count,
            'total_applications': self.mitigation_applications,
            'total_effectiveness_applied': self.total_effectiveness_applied,
            'mitigations_by_type': by_type,
            'last_cleanup': self.last_cleanup.isoformat()
        }
    
    def get_mitigation_recommendations(self, pressure_data: PressureData, 
                                     chaos_state: ChaosState) -> List[Dict[str, Any]]:
        """Get recommendations for mitigation actions based on current state"""
        recommendations = []
        
        # Analyze current pressure sources
        pressure_breakdown = pressure_data.global_pressure.get_pressure_breakdown()
        
        # Find top pressure sources
        top_sources = sorted(pressure_breakdown.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for source_name, pressure_value in top_sources:
            if pressure_value < 0.3:  # Skip low pressure sources
                continue
            
            # Find appropriate mitigations for this pressure source
            suitable_mitigations = []
            for mitigation_type, config in self.mitigation_configs.items():
                if source_name in config['affects_sources'] or 'all' in config['affects_sources']:
                    # Check if we can apply more of this type
                    current_count = self._count_active_mitigations(mitigation_type)
                    if current_count < config['max_concurrent']:
                        effectiveness_score = config['base_effectiveness'] * (config['stacking_multiplier'] ** current_count)
                        suitable_mitigations.append({
                            'type': mitigation_type,
                            'effectiveness': effectiveness_score,
                            'duration': config['duration_hours'],
                            'current_count': current_count,
                            'max_concurrent': config['max_concurrent']
                        })
            
            if suitable_mitigations:
                # Sort by effectiveness
                suitable_mitigations.sort(key=lambda x: x['effectiveness'], reverse=True)
                
                recommendations.append({
                    'pressure_source': source_name,
                    'pressure_value': pressure_value,
                    'priority': 'high' if pressure_value > 0.7 else 'medium',
                    'recommended_mitigations': suitable_mitigations[:3]  # Top 3 recommendations
                })
        
        return recommendations
    
    def force_remove_mitigation(self, mitigation_id: str) -> bool:
        """Force remove a mitigation (for admin/testing purposes)"""
        if mitigation_id in self.active_mitigations:
            del self.active_mitigations[mitigation_id]
            logger.info(f"Force removed mitigation: {mitigation_id}")
            return True
        return False
    
    def get_mitigation_by_id(self, mitigation_id: str) -> Optional[MitigationFactor]:
        """Get a specific mitigation by ID"""
        return self.active_mitigations.get(mitigation_id)
    
    def get_mitigations_by_source(self, source_id: str) -> List[MitigationFactor]:
        """Get all mitigations from a specific source"""
        return [m for m in self.active_mitigations.values() if m.source_id == source_id]
    
    def get_mitigations_by_type(self, mitigation_type: str) -> List[MitigationFactor]:
        """Get all mitigations of a specific type"""
        return [m for m in self.active_mitigations.values() if m.mitigation_type == mitigation_type] 