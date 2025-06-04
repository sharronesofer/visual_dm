"""
Alliance Service Module

This module provides pure business logic for faction alliances and betrayals.
"""

import random
from typing import Dict, List, Optional, Tuple, Any, Union, Protocol
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from enum import Enum

from backend.systems.faction.models.alliance import (
    AllianceModel, BetrayalEvent, AllianceEntity, BetrayalEntity,
    AllianceType, AllianceStatus, BetrayalReason,
    CreateAllianceRequest, UpdateAllianceRequest
)

# Local enum to avoid complex diplomacy import chain
class DiplomaticStatus(str, Enum):
    """Diplomatic status between factions"""
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    AT_WAR = "at_war"


class FactionDataProvider(Protocol):
    """Protocol for accessing faction data"""
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[Dict[str, Any]]:
        """Get faction data by ID"""
        ...
    
    def get_faction_hidden_attributes(self, faction_id: UUID) -> Dict[str, int]:
        """Get faction's hidden attributes"""
        ...


class AllianceService:
    """Service for managing faction alliances and betrayal mechanics - pure business logic"""
    
    def __init__(self, faction_data_provider: FactionDataProvider):
        """
        Initialize the alliance service with data provider.
        
        Args:
            faction_data_provider: Provider for faction data access
        """
        self.faction_data_provider = faction_data_provider
        
        # Configuration for alliance formation algorithms
        self.alliance_formation_config = {
            "min_threat_level": 0.6,  # Minimum threat level to trigger alliance consideration
            "max_trust_difference": 0.4,  # Maximum difference in trust levels for alliance
            "pragmatism_weight": 0.3,  # How much pragmatism influences alliance decisions
            "integrity_weight": 0.2,   # How much integrity influences alliance reliability
            "ambition_weight": 0.25,   # How much ambition drives expansion alliances
            "base_betrayal_chance": 0.05,  # Base 5% chance of betrayal per evaluation
        }
        
        # Betrayal probability modifiers based on hidden attributes
        self.betrayal_modifiers = {
            "hidden_ambition": {
                0: -0.02, 1: -0.01, 2: 0.0, 3: 0.01, 4: 0.02, 5: 0.04, 6: 0.06, 7: 0.08, 8: 0.10, 9: 0.12, 10: 0.15
            },
            "hidden_integrity": {
                0: 0.15, 1: 0.12, 2: 0.08, 3: 0.04, 4: 0.02, 5: 0.0, 6: -0.02, 7: -0.04, 8: -0.06, 9: -0.08, 10: -0.10
            },
            "hidden_impulsivity": {
                0: -0.02, 1: -0.01, 2: 0.0, 3: 0.01, 4: 0.02, 5: 0.04, 6: 0.06, 7: 0.08, 8: 0.10, 9: 0.12, 10: 0.15
            },
            "hidden_pragmatism": {
                0: 0.08, 1: 0.06, 2: 0.04, 3: 0.02, 4: 0.0, 5: -0.01, 6: -0.02, 7: -0.03, 8: -0.04, 9: -0.05, 10: -0.06
            }
        }

    def evaluate_alliance_opportunity(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID,
        common_threat_ids: Optional[List[UUID]] = None,
        alliance_type: Optional[AllianceType] = None
    ) -> Dict[str, Any]:
        """
        Evaluate whether two factions should form an alliance based on their
        hidden attributes and external circumstances.
        
        Args:
            faction_a_id: First faction ID
            faction_b_id: Second faction ID  
            common_threat_ids: List of common enemy faction IDs
            alliance_type: Specific type of alliance to evaluate
            
        Returns:
            Dict containing evaluation results and recommendations
        """
        # Get faction data
        faction_a = self.faction_data_provider.get_faction_by_id(faction_a_id)
        faction_b = self.faction_data_provider.get_faction_by_id(faction_b_id)
        
        if not faction_a or not faction_b:
            raise ValueError(f"Faction {faction_a_id if not faction_a else faction_b_id} not found")
        
        # Get hidden attributes
        attrs_a = self.faction_data_provider.get_faction_hidden_attributes(faction_a_id)
        attrs_b = self.faction_data_provider.get_faction_hidden_attributes(faction_b_id)
        
        # Calculate compatibility scores
        compatibility_score = self._calculate_faction_compatibility(attrs_a, attrs_b)
        
        # Evaluate threat level
        threat_level = self._calculate_threat_level(faction_a_id, faction_b_id, common_threat_ids or [])
        
        # Calculate alliance willingness for each faction
        willingness_a = self._calculate_alliance_willingness(attrs_a, threat_level, compatibility_score)
        willingness_b = self._calculate_alliance_willingness(attrs_b, threat_level, compatibility_score)
        
        # Overall willingness score
        willingness_score = (willingness_a + willingness_b) / 2.0
        
        # Determine if they are compatible (accounting for threat overrides)
        compatible = compatibility_score > 0.4 or threat_level > 0.8
        
        # Determine recommended alliance types if not specified
        recommended_types = []
        if alliance_type:
            recommended_types = [alliance_type]
        else:
            recommended_types = self._recommend_alliance_types(attrs_a, attrs_b, threat_level)
        
        # Identify risks and benefits
        risks = self._identify_alliance_risks(attrs_a, attrs_b)
        benefits = self._identify_alliance_benefits(attrs_a, attrs_b, threat_level)
        
        # Estimate duration
        estimated_duration = self._estimate_alliance_duration(attrs_a, attrs_b)
        
        return {
            "compatible": compatible,
            "compatibility_score": compatibility_score,
            "threat_level": threat_level,
            "willingness_score": willingness_score,
            "recommended_alliance_types": [t.value if hasattr(t, 'value') else t for t in recommended_types],
            "risks": risks,
            "benefits": benefits,
            "estimated_duration": estimated_duration,
            "willingness_breakdown": {
                "faction_a": willingness_a,
                "faction_b": willingness_b
            }
        }

    def create_alliance_proposal(self, request: CreateAllianceRequest) -> AllianceEntity:
        """
        Create a new alliance proposal based on business rules
        
        Args:
            request: Alliance creation request with details
            
        Returns:
            Created alliance entity (not yet persisted)
            
        Raises:
            ValueError: If leader faction doesn't exist
        """
        # Validate leader faction exists
        leader_faction = self.faction_data_provider.get_faction_by_id(request.leader_faction_id)
        if not leader_faction:
            raise ValueError(f"Leader faction {request.leader_faction_id} not found")
        
        # Create alliance entity with business rules
        alliance = AllianceEntity(
            name=request.name,
            alliance_type=request.alliance_type.value,
            description=request.description,
            leader_faction_id=request.leader_faction_id,
            member_faction_ids=request.member_faction_ids,
            terms=request.terms,
            mutual_obligations=request.mutual_obligations,
            shared_enemies=request.shared_enemies,
            shared_goals=request.shared_goals,
            end_date=request.end_date,
            auto_renew=request.auto_renew,
            start_date=datetime.utcnow(),
            status=AllianceStatus.PROPOSED.value
        )
        
        # Initialize alliance metrics (trust levels, betrayal risks)
        self._initialize_alliance_metrics(alliance)
        
        return alliance

    def evaluate_betrayal_probability(
        self, 
        alliance_member_attrs: Dict[str, int],
        external_factors: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the probability of betrayal by a specific faction member
        
        Args:
            alliance_member_attrs: Hidden attributes of the potential betrayer
            external_factors: External circumstances affecting betrayal risk
            
        Returns:
            Dict containing betrayal analysis
        """
        # Calculate base betrayal probability based on personality
        base_risk = self._calculate_base_betrayal_risk(alliance_member_attrs)
        
        # Apply external factor modifications
        external_modifier = 0.0
        if external_factors:
            # Stress factors increase betrayal risk
            if external_factors.get("under_pressure", False):
                external_modifier += 0.15
            
            # Military losses increase betrayal risk
            if external_factors.get("recent_defeats", 0) > 2:
                external_modifier += 0.1
            
            # Economic struggles increase betrayal risk
            if external_factors.get("resource_shortage", False):
                external_modifier += 0.08
            
            # Better opportunities elsewhere
            if external_factors.get("better_alliance_opportunity", False):
                external_modifier += 0.12
        
        # Calculate final betrayal probability (capped at 0.8)
        betrayal_probability = min(0.8, base_risk + external_modifier)
        
        # Determine primary betrayal reason
        primary_reason = self._determine_primary_betrayal_reason(alliance_member_attrs, external_factors)
        
        # Calculate trust impact if betrayal occurs
        trust_impact = self._calculate_betrayal_trust_impact(alliance_member_attrs)
        
        return {
            "betrayal_probability": betrayal_probability,
            "base_risk": base_risk,
            "external_modifier": external_modifier,
            "primary_reason": primary_reason.value if primary_reason else None,
            "trust_impact": trust_impact,
            "risk_level": "high" if betrayal_probability > 0.6 else "medium" if betrayal_probability > 0.3 else "low"
        }

    def create_betrayal_event(
        self,
        alliance_id: UUID,
        betrayer_faction_id: UUID,
        betrayal_type: str,
        description: str,
        reason: BetrayalReason
    ) -> BetrayalEntity:
        """
        Create a betrayal event based on business rules
        
        Args:
            alliance_id: ID of the alliance being betrayed
            betrayer_faction_id: ID of the faction committing betrayal
            betrayal_type: Type of betrayal
            description: Description of the betrayal
            reason: Reason for the betrayal
            
        Returns:
            Created betrayal entity (not yet persisted)
        """
        # Get betrayer attributes for impact calculation
        betrayer_attrs = self.faction_data_provider.get_faction_hidden_attributes(betrayer_faction_id)
        
        # Create betrayal entity
        betrayal = BetrayalEntity(
            alliance_id=alliance_id,
            betrayer_faction_id=betrayer_faction_id,
            betrayal_type=betrayal_type,
            reason=reason.value,
            description=description,
            timestamp=datetime.utcnow(),
            impact_severity=self._calculate_betrayal_severity(betrayer_attrs),
            trust_damage=self._calculate_trust_damage(betrayer_attrs),
            consequences=self._determine_betrayal_consequences(betrayer_attrs, betrayal_type)
        )
        
        return betrayal

    def _calculate_faction_compatibility(
        self, 
        attrs_a: Dict[str, int], 
        attrs_b: Dict[str, int]
    ) -> float:
        """
        Calculate compatibility score between two factions based on hidden attributes
        
        Args:
            attrs_a: Hidden attributes of faction A
            attrs_b: Hidden attributes of faction B
            
        Returns:
            Compatibility score between 0.0 and 1.0
        """
        # Normalize attributes to 0-1 scale
        norm_a = {k: v/10.0 for k, v in attrs_a.items()}
        norm_b = {k: v/10.0 for k, v in attrs_b.items()}
        
        # Calculate compatibility for key traits
        integrity_compat = 1.0 - abs(norm_a.get('hidden_integrity', 0.5) - norm_b.get('hidden_integrity', 0.5))
        pragmatism_compat = 1.0 - abs(norm_a.get('hidden_pragmatism', 0.5) - norm_b.get('hidden_pragmatism', 0.5))
        discipline_compat = 1.0 - abs(norm_a.get('hidden_discipline', 0.5) - norm_b.get('hidden_discipline', 0.5))
        
        # Ambition can be complementary (one high, one low works)
        ambition_diff = abs(norm_a.get('hidden_ambition', 0.5) - norm_b.get('hidden_ambition', 0.5))
        ambition_compat = 0.8 if ambition_diff > 0.3 else 1.0 - ambition_diff
        
        # Weight the compatibility scores
        overall_compatibility = (
            integrity_compat * 0.35 +
            pragmatism_compat * 0.25 +
            discipline_compat * 0.25 +
            ambition_compat * 0.15
        )
        
        return max(0.0, min(1.0, overall_compatibility))

    def _calculate_threat_level(
        self,
        faction_a_id: UUID,
        faction_b_id: UUID, 
        common_threat_ids: List[UUID]
    ) -> float:
        """
        Calculate external threat level that might motivate alliance
        
        Args:
            faction_a_id: First faction ID
            faction_b_id: Second faction ID
            common_threat_ids: List of common enemies
            
        Returns:
            Threat level between 0.0 and 1.0
        """
        # Basic threat calculation - in real implementation would analyze
        # actual military capabilities, territorial proximity, etc.
        base_threat = len(common_threat_ids) * 0.2
        
        # Mock calculation for demonstration
        # In practice, this would analyze actual faction strength, recent conflicts, etc.
        threat_level = min(1.0, base_threat + random.uniform(0.0, 0.3))
        
        return threat_level

    def _calculate_alliance_willingness(
        self,
        hidden_attrs: Dict[str, int],
        threat_level: float,
        compatibility: float
    ) -> float:
        """
        Calculate how willing a faction is to form an alliance
        
        Args:
            hidden_attrs: Faction's hidden attributes
            threat_level: External threat level
            compatibility: Compatibility with potential ally
            
        Returns:
            Willingness score between 0.0 and 1.0
        """
        # Base willingness from attributes
        pragmatism = hidden_attrs.get('hidden_pragmatism', 5) / 10.0
        integrity = hidden_attrs.get('hidden_integrity', 5) / 10.0
        ambition = hidden_attrs.get('hidden_ambition', 5) / 10.0
        
        # Pragmatic factions are more willing to ally
        base_willingness = pragmatism * 0.4
        
        # High integrity factions value compatibility more
        compatibility_weight = integrity * 0.3
        willingness_from_compatibility = compatibility * compatibility_weight
        
        # Threat increases willingness regardless of personality
        threat_motivation = threat_level * 0.4
        
        # Ambitious factions might be less willing unless threat is high
        ambition_modifier = -ambition * 0.1 if threat_level < 0.5 else ambition * 0.1
        
        total_willingness = base_willingness + willingness_from_compatibility + threat_motivation + ambition_modifier
        
        return max(0.0, min(1.0, total_willingness))

    def _recommend_alliance_types(
        self,
        attrs_a: Dict[str, int],
        attrs_b: Dict[str, int],
        threat_level: float
    ) -> List[AllianceType]:
        """
        Recommend appropriate alliance types based on faction attributes and situation
        
        Args:
            attrs_a: Faction A attributes
            attrs_b: Faction B attributes
            threat_level: External threat level
            
        Returns:
            List of recommended alliance types
        """
        recommended = []
        
        # High threat suggests defensive alliances
        if threat_level > 0.7:
            recommended.extend([AllianceType.DEFENSIVE, AllianceType.MUTUAL_PROTECTION])
        
        # High ambition suggests expansion alliances
        avg_ambition = (attrs_a.get('hidden_ambition', 5) + attrs_b.get('hidden_ambition', 5)) / 20.0
        if avg_ambition > 0.6:
            recommended.append(AllianceType.EXPANSIONIST)
        
        # High pragmatism suggests trade alliances
        avg_pragmatism = (attrs_a.get('hidden_pragmatism', 5) + attrs_b.get('hidden_pragmatism', 5)) / 20.0
        if avg_pragmatism > 0.6:
            recommended.append(AllianceType.TRADE)
        
        # High integrity suggests formal alliances
        avg_integrity = (attrs_a.get('hidden_integrity', 5) + attrs_b.get('hidden_integrity', 5)) / 20.0
        if avg_integrity > 0.7:
            recommended.append(AllianceType.FORMAL)
        
        # Default to basic cooperation if no specific recommendations
        if not recommended:
            recommended.append(AllianceType.COOPERATION)
        
        return recommended

    def _identify_alliance_risks(
        self,
        attrs_a: Dict[str, int],
        attrs_b: Dict[str, int]
    ) -> List[str]:
        """Identify potential risks in the alliance"""
        risks = []
        
        # High ambition difference creates power struggle risk
        ambition_diff = abs(attrs_a.get('hidden_ambition', 5) - attrs_b.get('hidden_ambition', 5))
        if ambition_diff > 4:
            risks.append("Significant ambition mismatch may lead to power struggles")
        
        # Low integrity increases betrayal risk
        min_integrity = min(attrs_a.get('hidden_integrity', 5), attrs_b.get('hidden_integrity', 5))
        if min_integrity < 3:
            risks.append("Low integrity partner increases betrayal risk")
        
        # High impulsivity increases volatility
        max_impulsivity = max(attrs_a.get('hidden_impulsivity', 5), attrs_b.get('hidden_impulsivity', 5))
        if max_impulsivity > 7:
            risks.append("High impulsivity may lead to rash decisions")
        
        # Low discipline reduces reliability
        min_discipline = min(attrs_a.get('hidden_discipline', 5), attrs_b.get('hidden_discipline', 5))
        if min_discipline < 4:
            risks.append("Poor discipline may affect alliance reliability")
        
        return risks

    def _estimate_alliance_duration(
        self,
        attrs_a: Dict[str, int],
        attrs_b: Dict[str, int]
    ) -> str:
        """Estimate how long the alliance might last"""
        # Base duration from integrity and discipline
        avg_integrity = (attrs_a.get('hidden_integrity', 5) + attrs_b.get('hidden_integrity', 5)) / 2
        avg_discipline = (attrs_a.get('hidden_discipline', 5) + attrs_b.get('hidden_discipline', 5)) / 2
        
        stability_score = (avg_integrity + avg_discipline) / 2
        
        if stability_score > 7:
            return "Long-term (5+ years)"
        elif stability_score > 5:
            return "Medium-term (2-5 years)"
        elif stability_score > 3:
            return "Short-term (6 months - 2 years)"
        else:
            return "Very short-term (< 6 months)"

    def _determine_primary_betrayal_reason(
        self,
        hidden_attrs: Dict[str, int],
        external_factors: Optional[Dict[str, Any]]
    ) -> BetrayalReason:
        """Determine the most likely reason for betrayal"""
        ambition = hidden_attrs.get('hidden_ambition', 5)
        integrity = hidden_attrs.get('hidden_integrity', 5)
        pragmatism = hidden_attrs.get('hidden_pragmatism', 5)
        
        # High ambition + low integrity = power grab
        if ambition > 7 and integrity < 4:
            return BetrayalReason.POWER_GRAB
        
        # External pressure
        if external_factors and external_factors.get('under_pressure', False):
            return BetrayalReason.EXTERNAL_PRESSURE
        
        # Opportunistic
        if pragmatism > 7:
            return BetrayalReason.OPPORTUNISM
        
        # Default
        return BetrayalReason.IDEOLOGICAL_DIFFERENCES

    def _initialize_alliance_metrics(self, alliance: AllianceEntity) -> None:
        """Initialize alliance metrics based on member attributes"""
        # This would set initial trust levels, betrayal risks, etc.
        # Implementation depends on AllianceEntity structure
        pass

    def _calculate_base_betrayal_risk(self, hidden_attrs: Dict[str, int]) -> float:
        """Calculate base betrayal risk from personality attributes"""
        risk = self.alliance_formation_config["base_betrayal_chance"]
        
        for attr_name, modifiers in self.betrayal_modifiers.items():
            attr_value = hidden_attrs.get(attr_name, 5)
            risk += modifiers.get(attr_value, 0)
        
        return max(0.0, min(1.0, risk))

    def _calculate_betrayal_trust_impact(
        self,
        betrayer_attrs: Dict[str, int]
    ) -> Dict[UUID, float]:
        """Calculate trust impact on other alliance members"""
        # This would calculate how betrayal affects trust with other members
        # Placeholder implementation
        base_impact = 0.3 + (betrayer_attrs.get('hidden_ambition', 5) / 10.0 * 0.2)
        return {"all_members": base_impact}

    def _identify_alliance_benefits(
        self,
        attrs_a: Dict[str, int],
        attrs_b: Dict[str, int],
        threat_level: float
    ) -> List[str]:
        """Identify potential benefits of the alliance"""
        benefits = []
        
        # Complementary strengths
        if abs(attrs_a.get('hidden_ambition', 5) - attrs_b.get('hidden_ambition', 5)) > 3:
            benefits.append("Complementary ambition levels provide balance")
        
        # Strong integrity
        min_integrity = min(attrs_a.get('hidden_integrity', 5), attrs_b.get('hidden_integrity', 5))
        if min_integrity > 6:
            benefits.append("High mutual integrity ensures reliability")
        
        # Threat protection
        if threat_level > 0.5:
            benefits.append("Mutual protection against external threats")
        
        # Economic advantages
        avg_pragmatism = (attrs_a.get('hidden_pragmatism', 5) + attrs_b.get('hidden_pragmatism', 5)) / 2
        if avg_pragmatism > 6:
            benefits.append("Strong economic cooperation potential")
        
        return benefits

    def _calculate_betrayal_severity(self, betrayer_attrs: Dict[str, int]) -> float:
        """Calculate the severity of a betrayal event"""
        ambition = betrayer_attrs.get('hidden_ambition', 5) / 10.0
        impulsivity = betrayer_attrs.get('hidden_impulsivity', 5) / 10.0
        return min(1.0, 0.3 + ambition * 0.4 + impulsivity * 0.3)

    def _calculate_trust_damage(self, betrayer_attrs: Dict[str, int]) -> float:
        """Calculate trust damage from betrayal"""
        integrity_loss = (10 - betrayer_attrs.get('hidden_integrity', 5)) / 10.0
        return min(1.0, 0.2 + integrity_loss * 0.6)

    def _determine_betrayal_consequences(
        self, 
        betrayer_attrs: Dict[str, int], 
        betrayal_type: str
    ) -> List[str]:
        """Determine consequences of the betrayal"""
        consequences = ["Alliance dissolution", "Trust penalty with other factions"]
        
        severity = self._calculate_betrayal_severity(betrayer_attrs)
        if severity > 0.7:
            consequences.append("Diplomatic isolation")
        
        if betrayal_type == "military":
            consequences.append("Military retaliation risk")
        
        return consequences 