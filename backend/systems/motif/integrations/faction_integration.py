"""
Motif Faction Integration

Provides motif-influenced diplomatic interactions, conflicts, and faction behavior.
Connects motifs to faction personality and diplomatic systems.
"""

from typing import Dict, List, Optional, Any
import logging

from backend.infrastructure.systems.motif.models.models import Motif, MotifEffectTarget

logger = logging.getLogger(__name__)

class MotifFactionConnector:
    """Connector for integrating motifs with faction systems"""
    
    def __init__(self, motif_manager):
        self.motif_manager = motif_manager
    
    async def get_faction_diplomatic_modifiers(
        self, 
        faction_id: str, 
        region_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get diplomatic behavior modifiers for a faction based on active motifs
        
        Args:
            faction_id: ID of the faction
            region_context: Regional and territorial context
            
        Returns:
            Diplomatic behavior modification data
        """
        try:
            # Get motifs affecting faction territory/region
            motifs = await self._get_faction_area_motifs(region_context)
            
            # Filter to faction-affecting motifs
            faction_affecting_motifs = [
                m for m in motifs 
                for effect in m.effects 
                if effect.target == MotifEffectTarget.FACTION
            ]
            
            if not faction_affecting_motifs:
                return {
                    "has_modifiers": False,
                    "faction_id": faction_id,
                    "message": "No motifs affecting faction behavior"
                }
            
            # Calculate diplomatic modifiers
            trust_modifiers = self._calculate_trust_modifiers(faction_affecting_motifs)
            aggression_modifiers = self._calculate_aggression_modifiers(faction_affecting_motifs)
            cooperation_tendencies = self._calculate_cooperation_tendencies(faction_affecting_motifs)
            alliance_preferences = self._calculate_alliance_preferences(faction_affecting_motifs)
            
            return {
                "has_modifiers": True,
                "faction_id": faction_id,
                "affecting_motifs": [
                    {
                        "name": m.name,
                        "category": m.category.value,
                        "intensity": m.get_effective_intensity()
                    } for m in faction_affecting_motifs[:3]
                ],
                "trust_modifiers": trust_modifiers,
                "aggression_modifiers": aggression_modifiers,
                "cooperation_tendencies": cooperation_tendencies,
                "alliance_preferences": alliance_preferences,
                "last_updated": region_context.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"Error getting faction diplomatic modifiers for {faction_id}: {e}")
            return {
                "has_modifiers": False,
                "faction_id": faction_id,
                "error": str(e)
            }
    
    async def _get_faction_area_motifs(self, region_context: Dict[str, Any]) -> List[Motif]:
        """Get all motifs affecting a faction's area of influence"""
        all_motifs = []
        
        # Global motifs always apply
        global_motifs = await self.motif_manager.get_global_motifs()
        all_motifs.extend(global_motifs)
        
        # Regional motifs in faction territory
        if 'region_ids' in region_context:
            for region_id in region_context['region_ids']:
                regional_motifs = await self.motif_manager.get_regional_motifs(region_id)
                all_motifs.extend(regional_motifs)
        elif 'region_id' in region_context:
            regional_motifs = await self.motif_manager.get_regional_motifs(region_context['region_id'])
            all_motifs.extend(regional_motifs)
        
        return all_motifs
    
    def _calculate_trust_modifiers(self, motifs: List[Motif]) -> Dict[str, float]:
        """Calculate trust-related modifiers for diplomatic interactions"""
        modifiers = {
            "baseline_trust": 0.0,
            "betrayal_likelihood": 0.0,
            "treaty_reliability": 0.0,
            "information_sharing": 0.0,
            "paranoia_level": 0.0
        }
        
        for motif in motifs:
            intensity_factor = motif.get_effective_intensity() / 10.0
            
            if motif.category.value in ['loyalty', 'unity', 'protection']:
                modifiers["baseline_trust"] += intensity_factor * 0.3
                modifiers["treaty_reliability"] += intensity_factor * 0.4
                modifiers["betrayal_likelihood"] -= intensity_factor * 0.2
                
            elif motif.category.value in ['betrayal', 'deception', 'paranoia']:
                modifiers["baseline_trust"] -= intensity_factor * 0.4
                modifiers["betrayal_likelihood"] += intensity_factor * 0.5
                modifiers["paranoia_level"] += intensity_factor * 0.3
                modifiers["information_sharing"] -= intensity_factor * 0.3
                
            elif motif.category.value in ['honor', 'integrity', 'justice']:
                modifiers["treaty_reliability"] += intensity_factor * 0.3
                modifiers["information_sharing"] += intensity_factor * 0.2
                
            elif motif.category.value in ['chaos', 'madness', 'collapse']:
                modifiers["treaty_reliability"] -= intensity_factor * 0.3
                modifiers["paranoia_level"] += intensity_factor * 0.2
        
        # Clamp values to reasonable ranges
        for key in modifiers:
            modifiers[key] = max(-1.0, min(1.0, modifiers[key]))
        
        return modifiers
    
    def _calculate_aggression_modifiers(self, motifs: List[Motif]) -> Dict[str, float]:
        """Calculate aggression and conflict-related modifiers"""
        modifiers = {
            "military_aggression": 0.0,
            "territorial_expansion": 0.0,
            "conflict_escalation": 0.0,
            "peaceful_resolution": 0.0,
            "revenge_seeking": 0.0
        }
        
        for motif in motifs:
            intensity_factor = motif.get_effective_intensity() / 10.0
            
            if motif.category.value in ['power', 'control', 'pride']:
                modifiers["military_aggression"] += intensity_factor * 0.3
                modifiers["territorial_expansion"] += intensity_factor * 0.4
                modifiers["conflict_escalation"] += intensity_factor * 0.2
                
            elif motif.category.value in ['vengeance', 'anger', 'hatred']:
                modifiers["military_aggression"] += intensity_factor * 0.4
                modifiers["revenge_seeking"] += intensity_factor * 0.5
                modifiers["peaceful_resolution"] -= intensity_factor * 0.3
                
            elif motif.category.value in ['peace', 'unity', 'harmony']:
                modifiers["peaceful_resolution"] += intensity_factor * 0.4
                modifiers["conflict_escalation"] -= intensity_factor * 0.3
                modifiers["military_aggression"] -= intensity_factor * 0.2
                
            elif motif.category.value in ['chaos', 'madness', 'destruction']:
                modifiers["conflict_escalation"] += intensity_factor * 0.5
                modifiers["peaceful_resolution"] -= intensity_factor * 0.4
        
        # Clamp values
        for key in modifiers:
            modifiers[key] = max(-1.0, min(1.0, modifiers[key]))
        
        return modifiers
    
    def _calculate_cooperation_tendencies(self, motifs: List[Motif]) -> Dict[str, Any]:
        """Calculate cooperation and collaboration tendencies"""
        tendencies = {
            "trade_openness": 0.5,
            "information_exchange": 0.5,
            "joint_operations": 0.5,
            "resource_sharing": 0.5,
            "mutual_defense": 0.5
        }
        
        cooperation_themes = []
        special_conditions = []
        
        for motif in motifs:
            intensity_factor = motif.get_effective_intensity() / 10.0
            adjustment = intensity_factor * 0.1
            
            if motif.category.value in ['unity', 'cooperation', 'mutual_aid']:
                tendencies["trade_openness"] += adjustment
                tendencies["information_exchange"] += adjustment
                tendencies["joint_operations"] += adjustment
                tendencies["resource_sharing"] += adjustment
                cooperation_themes.append("mutual_benefit")
                
            elif motif.category.value in ['isolation', 'distrust', 'self_reliance']:
                tendencies["trade_openness"] -= adjustment
                tendencies["information_exchange"] -= adjustment * 1.5
                tendencies["joint_operations"] -= adjustment
                special_conditions.append("requires_guarantees")
                
            elif motif.category.value in ['desperation', 'need', 'survival']:
                tendencies["mutual_defense"] += adjustment * 1.5
                tendencies["resource_sharing"] -= adjustment  # Hoarding
                cooperation_themes.append("survival_alliance")
                
            elif motif.category.value in ['greed', 'opportunism', 'exploitation']:
                tendencies["trade_openness"] += adjustment
                tendencies["resource_sharing"] -= adjustment
                special_conditions.append("expects_profit")
        
        # Clamp values
        for key in tendencies:
            tendencies[key] = max(0.0, min(1.0, tendencies[key]))
        
        return {
            "tendencies": tendencies,
            "cooperation_themes": cooperation_themes,
            "special_conditions": special_conditions,
            "overall_cooperativeness": sum(tendencies.values()) / len(tendencies)
        }
    
    def _calculate_alliance_preferences(self, motifs: List[Motif]) -> Dict[str, Any]:
        """Calculate alliance formation and maintenance preferences"""
        preferences = {
            "alliance_formation_likelihood": 0.5,
            "long_term_commitment": 0.5,
            "multi_party_alliances": 0.5,
            "conditional_alliances": 0.5,
            "defensive_focus": 0.5,
            "offensive_focus": 0.5
        }
        
        preferred_alliance_types = []
        alliance_motivations = []
        
        for motif in motifs:
            intensity_factor = motif.get_effective_intensity() / 10.0
            adjustment = intensity_factor * 0.1
            
            if motif.category.value in ['loyalty', 'honor', 'commitment']:
                preferences["long_term_commitment"] += adjustment * 1.5
                preferences["alliance_formation_likelihood"] += adjustment
                preferred_alliance_types.append("honor_based")
                alliance_motivations.append("mutual_respect")
                
            elif motif.category.value in ['protection', 'defense', 'security']:
                preferences["defensive_focus"] += adjustment * 1.5
                preferences["alliance_formation_likelihood"] += adjustment
                preferred_alliance_types.append("defensive_pact")
                alliance_motivations.append("security")
                
            elif motif.category.value in ['power', 'conquest', 'expansion']:
                preferences["offensive_focus"] += adjustment * 1.5
                preferences["multi_party_alliances"] += adjustment
                preferred_alliance_types.append("conquest_alliance")
                alliance_motivations.append("power_projection")
                
            elif motif.category.value in ['pragmatism', 'opportunism', 'convenience']:
                preferences["conditional_alliances"] += adjustment * 1.5
                preferred_alliance_types.append("trade_agreement")
                alliance_motivations.append("mutual_benefit")
                
            elif motif.category.value in ['distrust', 'betrayal', 'isolation']:
                preferences["alliance_formation_likelihood"] -= adjustment * 1.5
                preferences["long_term_commitment"] -= adjustment
                alliance_motivations.append("reluctant_cooperation")
        
        # Clamp values
        for key in preferences:
            preferences[key] = max(0.0, min(1.0, preferences[key]))
        
        return {
            "preferences": preferences,
            "preferred_types": preferred_alliance_types,
            "motivations": alliance_motivations,
            "alliance_disposition": self._determine_alliance_disposition(preferences)
        }
    
    def _determine_alliance_disposition(self, preferences: Dict[str, float]) -> str:
        """Determine overall alliance disposition"""
        formation_likelihood = preferences["alliance_formation_likelihood"]
        commitment_level = preferences["long_term_commitment"]
        
        if formation_likelihood >= 0.7 and commitment_level >= 0.7:
            return "eager_ally"
        elif formation_likelihood >= 0.5 and commitment_level >= 0.5:
            return "willing_partner"
        elif formation_likelihood >= 0.3:
            return "cautious_cooperator"
        else:
            return "isolationist"
    
    async def get_faction_conflict_escalation_risk(
        self, 
        faction_a_id: str, 
        faction_b_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate conflict escalation risk between two factions based on motifs"""
        try:
            # Get motifs affecting both factions' regions
            motifs = await self._get_faction_area_motifs(context)
            
            # Calculate escalation factors
            escalation_factors = []
            de_escalation_factors = []
            risk_multipliers = 1.0
            
            for motif in motifs:
                intensity = motif.get_effective_intensity()
                
                if motif.category.value in ['vengeance', 'hatred', 'anger']:
                    escalation_factors.append({
                        "factor": motif.category.value,
                        "intensity": intensity,
                        "risk_increase": intensity * 0.1
                    })
                    risk_multipliers *= (1 + intensity * 0.05)
                    
                elif motif.category.value in ['peace', 'diplomacy', 'understanding']:
                    de_escalation_factors.append({
                        "factor": motif.category.value,
                        "intensity": intensity,
                        "risk_decrease": intensity * 0.1
                    })
                    risk_multipliers *= (1 - intensity * 0.03)
                    
                elif motif.category.value in ['chaos', 'madness', 'unpredictability']:
                    escalation_factors.append({
                        "factor": motif.category.value,
                        "intensity": intensity,
                        "risk_increase": intensity * 0.15  # Higher impact
                    })
            
            # Calculate base risk (could be enhanced with faction relationship data)
            base_risk = context.get('base_tension', 0.3)
            
            # Apply motif modifiers
            total_escalation = sum(f["risk_increase"] for f in escalation_factors)
            total_de_escalation = sum(f["risk_decrease"] for f in de_escalation_factors)
            
            adjusted_risk = base_risk + total_escalation - total_de_escalation
            final_risk = max(0.0, min(1.0, adjusted_risk * risk_multipliers))
            
            # Determine risk level
            if final_risk >= 0.8:
                risk_level = "critical"
            elif final_risk >= 0.6:
                risk_level = "high"
            elif final_risk >= 0.4:
                risk_level = "moderate"
            elif final_risk >= 0.2:
                risk_level = "low"
            else:
                risk_level = "minimal"
            
            return {
                "faction_a_id": faction_a_id,
                "faction_b_id": faction_b_id,
                "escalation_risk": final_risk,
                "risk_level": risk_level,
                "escalation_factors": escalation_factors,
                "de_escalation_factors": de_escalation_factors,
                "affecting_motifs": [m.name for m in motifs[:5]],
                "recommendations": self._generate_conflict_recommendations(risk_level, motifs)
            }
            
        except Exception as e:
            logger.error(f"Error calculating faction conflict risk: {e}")
            return {
                "faction_a_id": faction_a_id,
                "faction_b_id": faction_b_id,
                "error": str(e)
            }
    
    def _generate_conflict_recommendations(self, risk_level: str, motifs: List[Motif]) -> List[str]:
        """Generate recommendations for managing faction conflicts"""
        recommendations = []
        
        if risk_level in ["critical", "high"]:
            recommendations.append("Immediate diplomatic intervention required")
            recommendations.append("Deploy peace-keeping forces to neutral zones")
            
            # Check for specific motif-based solutions
            peace_motifs = [m for m in motifs if m.category.value in ['peace', 'unity', 'diplomacy']]
            if peace_motifs:
                recommendations.append("Leverage existing peace-building motifs in the region")
            else:
                recommendations.append("Consider introducing peace-building initiatives")
                
        elif risk_level == "moderate":
            recommendations.append("Monitor situation closely")
            recommendations.append("Facilitate dialogue between faction representatives")
            
        elif risk_level in ["low", "minimal"]:
            recommendations.append("Maintain standard diplomatic channels")
            recommendations.append("Continue regular relationship monitoring")
            
        # Motif-specific recommendations
        chaos_motifs = [m for m in motifs if m.category.value in ['chaos', 'madness', 'unpredictability']]
        if chaos_motifs:
            recommendations.append("Address underlying chaos and instability in the region")
            
        return recommendations 