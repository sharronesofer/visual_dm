"""
Crisis Management Utilities

Utility classes for crisis detection, escalation calculations, and resolution analysis
for diplomatic crisis management.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID, uuid4

from backend.systems.diplomacy.models.crisis_models import (
    DiplomaticCrisis, CrisisResolutionAttempt, CrisisIntervention,
    CrisisEscalationTrigger, CrisisImpactAssessment,
    CrisisType, CrisisEscalationLevel, CrisisStatus, ResolutionType, InterventionType
)
from backend.systems.diplomacy.models.core_models import (
    DiplomaticStatus, DiplomaticIncidentSeverity, DiplomaticEventType, TreatyViolation,
    NegotiationStatus, UltimatumStatus, TreatyType
)


class CrisisDetectionUtils:
    """Utility class for crisis detection calculations and logic."""
    
    @staticmethod
    def should_tension_create_crisis(tension_level: float, threshold: float = 80.0) -> bool:
        """Determine if a tension level should trigger a crisis."""
        return tension_level >= threshold
    
    @staticmethod
    def is_high_stakes_negotiation(negotiation) -> bool:
        """Determine if a negotiation is high-stakes based on its characteristics."""
        if not hasattr(negotiation, 'treaty_type') or not negotiation.treaty_type:
            return False
        
        high_stakes_types = [
            TreatyType.ALLIANCE,
            TreatyType.MUTUAL_DEFENSE,
            TreatyType.PEACE,
            TreatyType.CEASEFIRE
        ]
        
        # Check if it's a high-stakes type
        if negotiation.treaty_type in high_stakes_types:
            return True
        
        # Check if it involves many parties (3+)
        if hasattr(negotiation, 'parties') and len(negotiation.parties) >= 3:
            return True
        
        # Check metadata for importance indicators
        if hasattr(negotiation, 'metadata') and negotiation.metadata and negotiation.metadata.get('importance') == 'critical':
            return True
        
        return False
    
    @staticmethod
    def should_violation_create_crisis(violation: TreatyViolation, treaty) -> bool:
        """Determine if a treaty violation should escalate to a crisis."""
        # High severity violations should create crises
        if violation.severity >= 80:
            return True
        
        # Multiple violations of the same treaty
        if hasattr(violation, 'violation_count') and violation.violation_count >= 3:
            return True
        
        # Critical treaty types are more sensitive
        if hasattr(treaty, 'treaty_type'):
            critical_types = [TreatyType.PEACE, TreatyType.CEASEFIRE, TreatyType.MUTUAL_DEFENSE]
            if treaty.treaty_type in critical_types and violation.severity >= 60:
                return True
        
        return False
    
    @staticmethod
    def count_cascading_incidents(incidents: List) -> bool:
        """Determine if incidents constitute a cascading crisis."""
        return len(incidents) >= 3
    
    @staticmethod
    def create_crisis_title(crisis_type: CrisisType, primary_factions: List[UUID]) -> str:
        """Generate an appropriate title for a crisis."""
        titles = {
            CrisisType.BORDER_DISPUTE: "Border Crisis",
            CrisisType.TRADE_WAR: "Trade Conflict",
            CrisisType.ALLIANCE_BREAKDOWN: "Alliance Crisis",
            CrisisType.TERRITORIAL_DISPUTE: "Territorial Crisis",
            CrisisType.RESOURCE_CONFLICT: "Resource Dispute",
            CrisisType.SUCCESSION_CRISIS: "Succession Crisis",
            CrisisType.DIPLOMATIC_INCIDENT: "Diplomatic Crisis",
            CrisisType.MILITARY_STANDOFF: "Military Standoff"
        }
        return titles.get(crisis_type, "Diplomatic Crisis")


class CrisisEscalationCalculator:
    """Utility class for crisis escalation calculations."""
    
    @staticmethod
    def calculate_escalation_level_score(level: CrisisEscalationLevel) -> int:
        """Convert escalation level to numeric score for calculations."""
        scores = {
            CrisisEscalationLevel.LOW: 25,
            CrisisEscalationLevel.MODERATE: 50,
            CrisisEscalationLevel.HIGH: 75,
            CrisisEscalationLevel.CRITICAL: 90,
            CrisisEscalationLevel.IMMINENT_WAR: 100
        }
        return scores.get(level, 50)
    
    @staticmethod
    def score_to_escalation_level(score: int) -> CrisisEscalationLevel:
        """Convert numeric score back to escalation level."""
        if score >= 95:
            return CrisisEscalationLevel.IMMINENT_WAR
        elif score >= 80:
            return CrisisEscalationLevel.CRITICAL
        elif score >= 65:
            return CrisisEscalationLevel.HIGH
        elif score >= 35:
            return CrisisEscalationLevel.MODERATE
        else:
            return CrisisEscalationLevel.LOW
    
    @staticmethod
    def calculate_new_escalation_level(current_crisis: DiplomaticCrisis, 
                                     trigger: CrisisEscalationTrigger) -> CrisisEscalationLevel:
        """Calculate new escalation level after a trigger."""
        current_score = CrisisEscalationCalculator.calculate_escalation_level_score(current_crisis.escalation_level)
        new_score = min(100, current_score + trigger.severity_increase)
        return CrisisEscalationCalculator.score_to_escalation_level(new_score)
    
    @staticmethod
    def should_trigger_escalate(trigger: CrisisEscalationTrigger) -> bool:
        """Determine if an escalation trigger should fire."""
        # Use probability to determine if trigger activates
        if trigger.probability:
            return random.randint(1, 100) <= trigger.probability
        
        # Default logic based on severity
        return trigger.severity_increase >= 10
    
    @staticmethod
    def calculate_escalation_risk(crisis: DiplomaticCrisis) -> int:
        """Calculate the risk of further escalation."""
        base_risk = CrisisEscalationCalculator.calculate_escalation_level_score(crisis.escalation_level)
        
        # Factor in crisis duration
        if crisis.created_at:
            days_active = (datetime.utcnow() - crisis.created_at).days
            if days_active > 30:
                base_risk += 10  # Longer crises tend to escalate
        
        # Factor in number of affected factions
        if crisis.affected_factions:
            base_risk += len(crisis.affected_factions) * 5
        
        return min(100, base_risk)


class CrisisResolutionAnalyzer:
    """Utility class for crisis resolution analysis."""
    
    @staticmethod
    def calculate_resolution_success_probability(resolution: CrisisResolutionAttempt, 
                                               crisis: DiplomaticCrisis) -> int:
        """Calculate probability of resolution success."""
        base_probability = {
            ResolutionType.DIPLOMATIC_MEDIATION: 60,
            ResolutionType.ECONOMIC_INCENTIVES: 45,
            ResolutionType.ARBITRATION: 70,
            ResolutionType.FACE_SAVING_COMPROMISE: 55,
            ResolutionType.INTERNATIONAL_PRESSURE: 40,
            ResolutionType.MILITARY_INTERVENTION: 80,
            ResolutionType.TREATY_NEGOTIATION: 65
        }.get(resolution.resolution_type, 50)
        
        # Adjust based on escalation level
        escalation_penalty = CrisisEscalationCalculator.calculate_escalation_level_score(crisis.escalation_level) // 4
        
        # Adjust based on support
        support_bonus = len(resolution.supported_by or []) * 5
        opposition_penalty = len(resolution.opposed_by or []) * 8
        
        final_probability = base_probability - escalation_penalty + support_bonus - opposition_penalty
        
        return max(10, min(90, final_probability))
    
    @staticmethod
    def calculate_resolution_probability(crisis: DiplomaticCrisis) -> int:
        """Calculate overall probability of crisis resolution."""
        base_prob = 50
        
        # Lower escalation = higher resolution chance
        escalation_score = CrisisEscalationCalculator.calculate_escalation_level_score(crisis.escalation_level)
        base_prob -= escalation_score // 3
        
        # Fewer factions involved = easier to resolve
        total_factions = len(crisis.primary_factions) + len(crisis.affected_factions or [])
        if total_factions <= 2:
            base_prob += 20
        elif total_factions <= 4:
            base_prob += 10
        else:
            base_prob -= (total_factions - 4) * 5
        
        # Recent crises are easier to resolve
        if crisis.created_at:
            days_active = (datetime.utcnow() - crisis.created_at).days
            if days_active <= 7:
                base_prob += 15
            elif days_active <= 30:
                base_prob += 5
            else:
                base_prob -= 10
        
        return max(5, min(95, base_prob))
    
    @staticmethod
    def generate_recommended_actions(crisis: DiplomaticCrisis) -> List[str]:
        """Generate recommended actions based on crisis characteristics."""
        actions = []
        
        escalation_level = crisis.escalation_level
        
        if escalation_level == CrisisEscalationLevel.LOW:
            actions.extend([
                "Initiate direct bilateral dialogue",
                "Establish communication channels",
                "Deploy diplomatic observers"
            ])
        elif escalation_level == CrisisEscalationLevel.MODERATE:
            actions.extend([
                "Engage neutral mediators",
                "Implement confidence-building measures",
                "Establish crisis hotline"
            ])
        elif escalation_level == CrisisEscalationLevel.HIGH:
            actions.extend([
                "Emergency diplomatic summit",
                "Deploy peacekeeping observers",
                "Activate international mediation"
            ])
        elif escalation_level in [CrisisEscalationLevel.CRITICAL, CrisisEscalationLevel.IMMINENT_WAR]:
            actions.extend([
                "Immediate ceasefire negotiations",
                "International intervention",
                "Emergency Security Council session"
            ])
        
        return actions
    
    @staticmethod
    def generate_priority_interventions(crisis: DiplomaticCrisis) -> List[str]:
        """Generate priority interventions based on crisis type and level."""
        interventions = []
        
        crisis_type = crisis.crisis_type
        
        if crisis_type == CrisisType.BORDER_DISPUTE:
            interventions.extend([
                "Deploy border monitors",
                "Establish demilitarized zone",
                "Border demarcation talks"
            ])
        elif crisis_type == CrisisType.TRADE_WAR:
            interventions.extend([
                "Trade talks facilitation",
                "Economic impact assessment",
                "Alternative trade routes"
            ])
        elif crisis_type == CrisisType.ALLIANCE_BREAKDOWN:
            interventions.extend([
                "Alliance review summit",
                "Mediated alliance restructuring",
                "Face-saving exit mechanisms"
            ])
        elif crisis_type == CrisisType.RESOURCE_CONFLICT:
            interventions.extend([
                "Resource sharing negotiations",
                "Joint development proposals",
                "Third-party arbitration"
            ])
        else:
            interventions.extend([
                "Diplomatic dialogue",
                "Neutral mediation",
                "Confidence-building measures"
            ])
        
        return interventions


class CrisisImpactCalculator:
    """Utility class for calculating crisis impacts."""
    
    @staticmethod
    def calculate_economic_impact(crisis: DiplomaticCrisis, faction_id: UUID) -> int:
        """Calculate economic impact of crisis on a faction."""
        base_impact = 30
        
        # Higher escalation = higher impact
        escalation_score = CrisisEscalationCalculator.calculate_escalation_level_score(crisis.escalation_level)
        base_impact += escalation_score // 2
        
        # Primary factions affected more
        if faction_id in crisis.primary_factions:
            base_impact += 20
        elif crisis.affected_factions and faction_id in crisis.affected_factions:
            base_impact += 10
        
        # Trade conflicts have higher economic impact
        if crisis.crisis_type == CrisisType.TRADE_WAR:
            base_impact += 25
        
        return min(100, base_impact)
    
    @staticmethod
    def calculate_political_impact(crisis: DiplomaticCrisis, faction_id: UUID) -> int:
        """Calculate political impact of crisis on a faction."""
        base_impact = 25
        
        # Alliance crises have high political impact
        if crisis.crisis_type == CrisisType.ALLIANCE_BREAKDOWN:
            base_impact += 30
        
        # Primary factions suffer more political damage
        if faction_id in crisis.primary_factions:
            base_impact += 25
        
        return min(100, base_impact)
    
    @staticmethod
    def calculate_military_impact(crisis: DiplomaticCrisis, faction_id: UUID) -> int:
        """Calculate military impact of crisis on a faction."""
        base_impact = 20
        
        # Military standoffs have obvious military impact
        if crisis.crisis_type == CrisisType.MILITARY_STANDOFF:
            base_impact += 40
        
        # Border disputes also have military implications
        if crisis.crisis_type == CrisisType.BORDER_DISPUTE:
            base_impact += 25
        
        # Critical escalation levels suggest military preparation
        if crisis.escalation_level in [CrisisEscalationLevel.CRITICAL, CrisisEscalationLevel.IMMINENT_WAR]:
            base_impact += 30
        
        return min(100, base_impact)
    
    @staticmethod
    def calculate_social_impact(crisis: DiplomaticCrisis, faction_id: UUID) -> int:
        """Calculate social impact of crisis on a faction."""
        base_impact = 15
        
        # Public awareness increases social impact
        if hasattr(crisis, 'public_awareness') and crisis.public_awareness:
            base_impact += crisis.public_awareness // 2
        
        # Longer crises have more social impact
        if crisis.created_at:
            days_active = (datetime.utcnow() - crisis.created_at).days
            base_impact += min(days_active // 5, 20)
        
        return min(100, base_impact)
    
    @staticmethod
    def calculate_spillover_risk(crisis: DiplomaticCrisis) -> int:
        """Calculate risk of crisis spilling over to other factions."""
        base_risk = 20
        
        # More affected factions = higher spillover risk
        total_factions = len(crisis.primary_factions) + len(crisis.affected_factions or [])
        base_risk += total_factions * 8
        
        # Alliance breakdowns tend to spread
        if crisis.crisis_type == CrisisType.ALLIANCE_BREAKDOWN:
            base_risk += 25
        
        # High escalation increases spillover risk
        escalation_score = CrisisEscalationCalculator.calculate_escalation_level_score(crisis.escalation_level)
        base_risk += escalation_score // 3
        
        return min(100, base_risk)


class CrisisContentGenerator:
    """Utility class for generating crisis-related content."""
    
    @staticmethod
    def generate_crisis_description(crisis_type: CrisisType, primary_factions: List[UUID]) -> str:
        """Generate a description for a crisis."""
        descriptions = {
            CrisisType.BORDER_DISPUTE: f"Escalating border tensions between {len(primary_factions)} factions requiring immediate diplomatic intervention",
            CrisisType.TRADE_WAR: f"Economic conflict affecting trade relationships and regional stability",
            CrisisType.ALLIANCE_BREAKDOWN: f"Critical breakdown in alliance structure threatening regional balance",
            CrisisType.TERRITORIAL_DISPUTE: f"Territorial claims dispute escalating beyond normal diplomatic channels",
            CrisisType.RESOURCE_CONFLICT: f"Competition over critical resources leading to increased tensions",
            CrisisType.SUCCESSION_CRISIS: f"Leadership succession dispute with international implications",
            CrisisType.DIPLOMATIC_INCIDENT: f"Major diplomatic incident requiring crisis-level response",
            CrisisType.MILITARY_STANDOFF: f"Military forces in dangerous proximity requiring de-escalation"
        }
        
        return descriptions.get(crisis_type, f"Diplomatic crisis involving {len(primary_factions)} factions")
    
    @staticmethod
    def generate_root_causes(crisis_type: CrisisType, context: Dict = None) -> List[str]:
        """Generate likely root causes for a crisis."""
        context = context or {}
        
        causes = {
            CrisisType.BORDER_DISPUTE: [
                "Unclear border demarcation",
                "Historical territorial claims",
                "Resource discovery in disputed area"
            ],
            CrisisType.TRADE_WAR: [
                "Trade imbalance disputes",
                "Tariff escalation",
                "Market access restrictions"
            ],
            CrisisType.ALLIANCE_BREAKDOWN: [
                "Conflicting strategic interests",
                "Failed mutual obligations",
                "Third-party interference"
            ],
            CrisisType.RESOURCE_CONFLICT: [
                "Competing resource claims",
                "Supply disruption",
                "Pricing disputes"
            ]
        }
        
        return causes.get(crisis_type, ["Diplomatic disagreement", "Policy conflicts", "Communication breakdown"]) 