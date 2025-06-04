"""
Faction Diplomacy Integration Service - Pure Business Logic

This service provides business logic for diplomatic interactions between factions,
using faction configuration and hidden attributes to drive diplomatic behavior.
"""

from typing import Dict, List, Optional, Tuple, Any, Protocol
from uuid import UUID
from datetime import datetime, timedelta


# Business Logic Protocols (dependency injection)
class FactionDataProvider(Protocol):
    """Protocol for accessing faction data"""
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[Any]:
        """Get faction data by ID"""
        ...


class DiplomacyConfigurationService(Protocol):
    """Protocol for diplomatic configuration"""
    
    def get_alliance_types(self) -> Dict[str, Dict]:
        """Get available alliance types and their configuration"""
        ...
    
    def get_alliance_compatibility_factors(self, alliance_type: str) -> Dict[str, float]:
        """Get compatibility factors for alliance type"""
        ...
    
    def calculate_behavior_modifier(self, behavior_type: str, hidden_attrs: Dict[str, int]) -> float:
        """Calculate behavior modifier based on faction attributes"""
        ...


class RelationshipService(Protocol):
    """Protocol for relationship data"""
    
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict[str, Any]:
        """Get relationship data between factions"""
        ...


class FactionDiplomacyBusinessService:
    """Business service for managing diplomatic interactions between factions"""
    
    def __init__(self, 
                 faction_data_provider: FactionDataProvider,
                 config_service: DiplomacyConfigurationService,
                 relationship_service: RelationshipService):
        self.faction_data_provider = faction_data_provider
        self.config_service = config_service
        self.relationship_service = relationship_service
    
    def evaluate_alliance_proposal(
        self, 
        proposer_id: UUID, 
        target_id: UUID, 
        alliance_type: str = "military"
    ) -> Dict[str, Any]:
        """
        Business logic: Evaluate whether a faction would accept an alliance proposal
        
        Args:
            proposer_id: UUID of the faction making the proposal
            target_id: UUID of the faction receiving the proposal
            alliance_type: Type of alliance ('military', 'economic', etc.)
            
        Returns:
            Dict with acceptance probability and business reasoning
        """
        # Get faction data
        proposer = self.faction_data_provider.get_faction_by_id(proposer_id)
        target = self.faction_data_provider.get_faction_by_id(target_id)
        
        if not proposer or not target:
            return {"error": "One or both factions not found"}
        
        # Get alliance configuration
        alliance_types = self.config_service.get_alliance_types()
        alliance_config = alliance_types.get(alliance_type, {})
        if not alliance_config:
            return {"error": f"Unknown alliance type: {alliance_type}"}
        
        # Business rule: Calculate compatibility
        compatibility = self._calculate_alliance_compatibility(
            proposer, target, alliance_type
        )
        
        # Business rule: Get current diplomatic relationship
        relationship = self.relationship_service.get_faction_relationship(proposer_id, target_id)
        current_tension = relationship.get('tension', 50)
        
        # Business rule: Calculate acceptance probability
        acceptance_probability = self._calculate_acceptance_probability(
            compatibility, current_tension, target, alliance_config
        )
        
        return {
            "acceptance_probability": round(acceptance_probability, 3),
            "compatibility_score": round(compatibility, 3),
            "current_tension": current_tension,
            "alliance_type": alliance_type,
            "trust_required": alliance_config.get('trust_requirements', 50),
            "reasoning": {
                "compatibility": f"Faction compatibility: {compatibility:.2f}",
                "tension": f"Current tension level: {current_tension}",
                "recommendation": self._get_recommendation(acceptance_probability)
            }
        }
    
    def calculate_betrayal_risk(
        self, 
        faction_id: UUID, 
        ally_id: UUID, 
        scenario: str = "opportunity"
    ) -> Dict[str, Any]:
        """
        Business logic: Calculate the risk of faction betrayal
        
        Args:
            faction_id: Faction that might betray
            ally_id: Faction that might be betrayed  
            scenario: Scenario context ('opportunity', 'desperation', etc.)
            
        Returns:
            Dict with betrayal risk analysis
        """
        faction = self.faction_data_provider.get_faction_by_id(faction_id)
        ally = self.faction_data_provider.get_faction_by_id(ally_id)
        
        if not faction or not ally:
            return {"error": "One or both factions not found"}
        
        # Business rule: Get relationship data
        relationship = self.relationship_service.get_faction_relationship(faction_id, ally_id)
        
        # Business rule: Calculate betrayal risk using faction attributes
        hidden_attrs = faction.get_hidden_attributes() if hasattr(faction, 'get_hidden_attributes') else {}
        
        base_risk = self._calculate_base_betrayal_risk(hidden_attrs, relationship, scenario)
        
        return {
            "betrayal_risk": round(base_risk, 3),
            "risk_level": self._categorize_risk(base_risk),
            "scenario": scenario,
            "relationship_tension": relationship.get('tension', 50),
            "primary_risk_factors": self._identify_betrayal_risk_factors(hidden_attrs, relationship)
        }
    
    def assess_diplomatic_compatibility(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID
    ) -> Dict[str, Any]:
        """
        Business logic: Assess overall diplomatic compatibility between factions
        """
        faction_a = self.faction_data_provider.get_faction_by_id(faction_a_id)
        faction_b = self.faction_data_provider.get_faction_by_id(faction_b_id)
        
        if not faction_a or not faction_b:
            return {"error": "One or both factions not found"}
        
        # Calculate compatibility across different alliance types
        alliance_types = self.config_service.get_alliance_types()
        compatibility_scores = {}
        
        for alliance_type in alliance_types.keys():
            compatibility_scores[alliance_type] = self._calculate_alliance_compatibility(
                faction_a, faction_b, alliance_type
            )
        
        # Overall compatibility is average across all types
        overall_compatibility = sum(compatibility_scores.values()) / len(compatibility_scores)
        
        # Business rule: Determine best alliance type
        best_alliance_type = max(compatibility_scores.items(), key=lambda x: x[1])
        
        return {
            "overall_compatibility": round(overall_compatibility, 3),
            "alliance_compatibilities": {k: round(v, 3) for k, v in compatibility_scores.items()},
            "best_alliance_type": best_alliance_type[0],
            "best_compatibility_score": round(best_alliance_type[1], 3),
            "recommendation": self._get_compatibility_recommendation(overall_compatibility)
        }
    
    def predict_diplomatic_behavior(
        self, 
        faction_id: UUID, 
        situation: str = "general"
    ) -> Dict[str, Any]:
        """
        Business logic: Predict how a faction will behave diplomatically
        
        Args:
            faction_id: Faction to analyze
            situation: Diplomatic situation context
            
        Returns:
            Dict with behavioral predictions
        """
        faction = self.faction_data_provider.get_faction_by_id(faction_id)
        
        if not faction:
            return {"error": "Faction not found"}
        
        hidden_attrs = faction.get_hidden_attributes() if hasattr(faction, 'get_hidden_attributes') else {}
        
        # Business rules: Calculate behavioral tendencies
        tendencies = {
            "aggression_tendency": self._calculate_aggression_tendency(hidden_attrs),
            "cooperation_tendency": self._calculate_cooperation_tendency(hidden_attrs),
            "trustworthiness": self._calculate_trustworthiness(hidden_attrs),
            "flexibility": self._calculate_diplomatic_flexibility(hidden_attrs),
            "betrayal_tendency": self._calculate_betrayal_tendency(hidden_attrs),
            "alliance_preference": self._determine_preferred_alliance_types(hidden_attrs)
        }
        
        return {
            "faction_id": faction_id,
            "situation": situation,
            "behavioral_tendencies": tendencies,
            "diplomatic_style": self._determine_diplomatic_style(hidden_attrs),
            "risk_factors": self._identify_diplomatic_risk_factors(hidden_attrs)
        }
    
    # Private business logic methods
    
    def _calculate_alliance_compatibility(self, faction_a: Any, faction_b: Any, alliance_type: str) -> float:
        """Business rule: Calculate alliance compatibility using configuration"""
        factors = self.config_service.get_alliance_compatibility_factors(alliance_type)
        if not factors:
            return 0.5  # Default neutral compatibility
        
        attrs_a = faction_a.get_hidden_attributes() if hasattr(faction_a, 'get_hidden_attributes') else {}
        attrs_b = faction_b.get_hidden_attributes() if hasattr(faction_b, 'get_hidden_attributes') else {}
        
        total_compatibility = 0.0
        total_weight = 0.0
        
        for factor, weight in factors.items():
            attr_name = factor.replace('_weight', '')
            full_attr_name = f"hidden_{attr_name}"
            
            if full_attr_name in attrs_a and full_attr_name in attrs_b:
                # Business rule: Closer values = higher compatibility
                diff = abs(attrs_a[full_attr_name] - attrs_b[full_attr_name])
                attr_compatibility = 1.0 - (diff / 10.0)  # Assuming 0-10 scale
                
                total_compatibility += attr_compatibility * weight
                total_weight += weight
        
        return total_compatibility / total_weight if total_weight > 0 else 0.5
    
    def _calculate_acceptance_probability(self, compatibility: float, tension: int, target_faction: Any, alliance_config: Dict) -> float:
        """Business rule: Calculate acceptance probability"""
        # Base acceptance probability
        base_acceptance = 0.5
        
        # Compatibility modifier
        compatibility_modifier = (compatibility - 0.5) * 0.6
        
        # Tension modifier (lower tension = higher acceptance)
        tension_modifier = (50 - tension) / 100.0
        
        # Target faction reliability modifier
        target_attrs = target_faction.get_hidden_attributes() if hasattr(target_faction, 'get_hidden_attributes') else {}
        reliability = target_attrs.get('hidden_integrity', 5) / 10.0
        reliability_modifier = (reliability - 0.5) * 0.4
        
        # Calculate final probability
        acceptance_probability = base_acceptance + compatibility_modifier + tension_modifier + reliability_modifier
        return max(0.0, min(1.0, acceptance_probability))
    
    def _calculate_base_betrayal_risk(self, hidden_attrs: Dict[str, int], relationship: Dict[str, Any], scenario: str) -> float:
        """Business rule: Calculate base betrayal risk"""
        ambition = hidden_attrs.get('hidden_ambition', 5)
        integrity = hidden_attrs.get('hidden_integrity', 5)
        impulsivity = hidden_attrs.get('hidden_impulsivity', 5)
        tension = relationship.get('tension', 50)
        
        # High ambition + low integrity + high impulsivity + high tension = higher betrayal risk
        risk = (
            (ambition / 10.0) * 0.3 +           # Ambition drives betrayal
            ((10 - integrity) / 10.0) * 0.4 +   # Low integrity enables betrayal
            (impulsivity / 10.0) * 0.2 +        # Impulsivity triggers betrayal
            (tension / 100.0) * 0.1              # Tension provides justification
        )
        
        # Scenario modifiers
        if scenario == "opportunity":
            risk *= 1.2  # Opportunities increase betrayal chance
        elif scenario == "desperation":
            risk *= 1.5  # Desperation strongly drives betrayal
        elif scenario == "provocation":
            risk *= 1.3  # Provocation increases chance
        
        return min(1.0, risk)
    
    def _categorize_risk(self, risk: float) -> str:
        """Business rule: Categorize risk level"""
        if risk < 0.2:
            return "very_low"
        elif risk < 0.4:
            return "low"
        elif risk < 0.6:
            return "moderate"
        elif risk < 0.8:
            return "high"
        else:
            return "very_high"
    
    def _get_recommendation(self, probability: float) -> str:
        """Business rule: Get recommendation based on probability"""
        if probability > 0.7:
            return "Strongly Accept"
        elif probability > 0.5:
            return "Accept"
        elif probability > 0.3:
            return "Consider"
        else:
            return "Reject"
    
    def _get_compatibility_recommendation(self, compatibility: float) -> str:
        """Business rule: Get compatibility recommendation"""
        if compatibility > 0.8:
            return "Excellent diplomatic partner"
        elif compatibility > 0.6:
            return "Good diplomatic potential"
        elif compatibility > 0.4:
            return "Moderate compatibility"
        else:
            return "Poor diplomatic compatibility"
    
    def _identify_betrayal_risk_factors(self, hidden_attrs: Dict[str, int], relationship: Dict[str, Any]) -> List[str]:
        """Business rule: Identify specific betrayal risk factors"""
        factors = []
        
        if hidden_attrs.get('hidden_ambition', 5) > 7:
            factors.append("High ambition drives opportunistic behavior")
        if hidden_attrs.get('hidden_integrity', 5) < 3:
            factors.append("Low integrity enables betrayal")
        if hidden_attrs.get('hidden_impulsivity', 5) > 7:
            factors.append("High impulsivity leads to rash decisions")
        if relationship.get('tension', 50) > 70:
            factors.append("High tension provides betrayal justification")
        
        return factors
    
    def _calculate_aggression_tendency(self, hidden_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate aggression tendency"""
        ambition = hidden_attrs.get('hidden_ambition', 5)
        impulsivity = hidden_attrs.get('hidden_impulsivity', 5)
        discipline = hidden_attrs.get('hidden_discipline', 5)
        
        # High ambition + high impulsivity - discipline = aggression
        aggression = ((ambition + impulsivity) / 2 - discipline * 0.3) / 10.0
        return max(0.0, min(1.0, aggression))
    
    def _calculate_cooperation_tendency(self, hidden_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate cooperation tendency"""
        integrity = hidden_attrs.get('hidden_integrity', 5)
        pragmatism = hidden_attrs.get('hidden_pragmatism', 5)
        discipline = hidden_attrs.get('hidden_discipline', 5)
        
        # High integrity + pragmatism + discipline = cooperation
        cooperation = (integrity + pragmatism + discipline) / 30.0
        return max(0.0, min(1.0, cooperation))
    
    def _calculate_trustworthiness(self, hidden_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate trustworthiness"""
        integrity = hidden_attrs.get('hidden_integrity', 5)
        discipline = hidden_attrs.get('hidden_discipline', 5)
        impulsivity = hidden_attrs.get('hidden_impulsivity', 5)
        
        # High integrity + discipline - impulsivity = trustworthiness
        trustworthiness = (integrity + discipline - impulsivity) / 20.0
        return max(0.0, min(1.0, trustworthiness))
    
    def _calculate_diplomatic_flexibility(self, hidden_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate diplomatic flexibility"""
        pragmatism = hidden_attrs.get('hidden_pragmatism', 5)
        impulsivity = hidden_attrs.get('hidden_impulsivity', 5)
        
        # High pragmatism + moderate impulsivity = flexibility
        flexibility = (pragmatism + impulsivity * 0.5) / 15.0
        return max(0.0, min(1.0, flexibility))
    
    def _calculate_betrayal_tendency(self, hidden_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate general betrayal tendency"""
        ambition = hidden_attrs.get('hidden_ambition', 5)
        integrity = hidden_attrs.get('hidden_integrity', 5)
        
        # High ambition - integrity = betrayal tendency
        betrayal = (ambition - integrity) / 10.0
        return max(0.0, min(1.0, betrayal))
    
    def _determine_preferred_alliance_types(self, hidden_attrs: Dict[str, int]) -> List[str]:
        """Business rule: Determine preferred alliance types"""
        preferences = []
        
        if hidden_attrs.get('hidden_ambition', 5) > 6:
            preferences.append("military")
        if hidden_attrs.get('hidden_pragmatism', 5) > 6:
            preferences.append("economic")
        if hidden_attrs.get('hidden_integrity', 5) > 7:
            preferences.append("mutual_defense")
        
        return preferences or ["defensive"]
    
    def _determine_diplomatic_style(self, hidden_attrs: Dict[str, int]) -> str:
        """Business rule: Determine overall diplomatic style"""
        aggression = self._calculate_aggression_tendency(hidden_attrs)
        cooperation = self._calculate_cooperation_tendency(hidden_attrs)
        
        if aggression > 0.7:
            return "aggressive"
        elif cooperation > 0.7:
            return "cooperative"
        elif hidden_attrs.get('hidden_pragmatism', 5) > 7:
            return "pragmatic"
        elif hidden_attrs.get('hidden_integrity', 5) > 7:
            return "honorable"
        else:
            return "unpredictable"
    
    def _identify_diplomatic_risk_factors(self, hidden_attrs: Dict[str, int]) -> List[str]:
        """Business rule: Identify diplomatic risk factors"""
        risks = []
        
        if hidden_attrs.get('hidden_impulsivity', 5) > 7:
            risks.append("Impulsive decision-making")
        if hidden_attrs.get('hidden_ambition', 5) > 8:
            risks.append("Overly ambitious expansion")
        if hidden_attrs.get('hidden_integrity', 5) < 3:
            risks.append("Unreliable treaty adherence")
        if hidden_attrs.get('hidden_discipline', 5) < 3:
            risks.append("Poor internal organization")
        
        return risks


def create_faction_diplomacy_business_service(
    faction_data_provider: FactionDataProvider,
    config_service: DiplomacyConfigurationService,
    relationship_service: RelationshipService
) -> FactionDiplomacyBusinessService:
    """Factory function to create faction diplomacy business service"""
    return FactionDiplomacyBusinessService(faction_data_provider, config_service, relationship_service) 