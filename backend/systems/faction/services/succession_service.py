"""
Faction Succession Service - Pure Business Logic

Service for managing faction succession crises according to Task 69 requirements.
Implements different succession types for various faction types and handles
crisis triggers, candidate competition, and resolution.
"""

import random
from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID
from datetime import datetime, timedelta

from backend.systems.faction.models.succession import (
    SuccessionCrisisEntity,
    SuccessionType,
    SuccessionCrisisStatus,
    SuccessionTrigger,
    SuccessionCandidate,
    CreateSuccessionCrisisRequest,
    UpdateSuccessionCrisisRequest,
    AddCandidateRequest
)


# Business Logic Protocols (dependency injection)
class FactionDataProvider(Protocol):
    """Protocol for accessing faction data"""
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[Any]:
        """Get faction data by ID"""
        ...


class MembershipService(Protocol):
    """Protocol for faction membership operations"""
    
    def get_faction_members(self, faction_id: UUID) -> List[Any]:
        """Get members of a faction"""
        ...
    
    def get_potential_leaders(self, faction_id: UUID) -> List[Any]:
        """Get potential leaders for succession"""
        ...


class SuccessionBusinessService:
    """Service for managing faction succession crises - pure business logic"""
    
    def __init__(self, 
                 faction_data_provider: FactionDataProvider,
                 membership_service: MembershipService):
        self.faction_data_provider = faction_data_provider
        self.membership_service = membership_service
    
    def determine_succession_type(self, faction_data: Any) -> SuccessionType:
        """
        Business rule: Determine succession type based on faction properties and type
        
        Maps faction types to appropriate succession mechanisms:
        - Trading companies -> Economic competition
        - Military/Kingdoms -> Hereditary or military coup
        - Religious -> Religious election or divine mandate
        - Guilds/Democratic -> Elections or merit selection
        """
        faction_props = getattr(faction_data, 'properties', {}) or {}
        faction_type = faction_props.get("faction_type", "unknown")
        faction_name = getattr(faction_data, 'name', '').lower()
        hidden_attrs = faction_data.get_hidden_attributes() if hasattr(faction_data, 'get_hidden_attributes') else {}
        
        # Royal Bay Trading Company and merchant factions
        if faction_type in ["merchant", "trading_company"] or "trading" in faction_name:
            return SuccessionType.ECONOMIC_COMPETITION
        
        # Military and kingdom factions
        elif faction_type in ["military", "kingdom", "noble"]:
            # Business rule: High ambition + low integrity = military coup tendency
            if hidden_attrs.get("hidden_ambition", 5) >= 4 and hidden_attrs.get("hidden_integrity", 5) <= 2:
                coup_chance = (hidden_attrs.get("hidden_ambition", 5) - hidden_attrs.get("hidden_integrity", 5)) / 6.0
                if random.random() < coup_chance:
                    return SuccessionType.MILITARY_COUP
            return SuccessionType.HEREDITARY
        
        # Religious factions
        elif faction_type in ["religious", "temple", "church"]:
            # Business rule: High integrity = traditional election, low integrity = divine mandate claims
            if hidden_attrs.get("hidden_integrity", 5) >= 4:
                return SuccessionType.RELIGIOUS_ELECTION
            else:
                return SuccessionType.DIVINE_MANDATE
        
        # Guilds and democratic factions
        elif faction_type in ["guild", "democratic", "council"]:
            # Business rule: High discipline = merit-based, otherwise democratic
            if hidden_attrs.get("hidden_discipline", 5) >= 4:
                return SuccessionType.MERIT_SELECTION
            else:
                return SuccessionType.DEMOCRATIC_ELECTION
        
        # Default based on faction personality
        else:
            if hidden_attrs.get("hidden_integrity", 5) >= 4:
                return SuccessionType.DEMOCRATIC_ELECTION
            elif hidden_attrs.get("hidden_ambition", 5) >= 4:
                return SuccessionType.MILITARY_COUP
            else:
                return SuccessionType.HEREDITARY
    
    def calculate_succession_vulnerability(self, faction_data: Any) -> float:
        """
        Business rule: Calculate how vulnerable a faction is to succession crisis
        
        Factors:
        - Leader stability and support
        - Faction stability and unity
        - Hidden attributes driving ambition
        - External pressures
        """
        hidden_attrs = faction_data.get_hidden_attributes() if hasattr(faction_data, 'get_hidden_attributes') else {}
        
        # Base vulnerability from faction personality
        ambition_pressure = hidden_attrs.get("hidden_ambition", 5) / 6.0  # High ambition = more challenges
        impulsivity_risk = hidden_attrs.get("hidden_impulsivity", 5) / 6.0  # Impulsive = sudden crises
        instability_factor = (6 - hidden_attrs.get("hidden_discipline", 5)) / 6.0  # Low discipline = chaos
        
        # Resilience reduces vulnerability
        resilience_protection = hidden_attrs.get("hidden_resilience", 5) / 6.0
        
        # Calculate base vulnerability
        base_vulnerability = (
            ambition_pressure * 0.4 +
            impulsivity_risk * 0.3 +
            instability_factor * 0.3
        ) * (1 - resilience_protection * 0.3)  # Resilience provides protection
        
        # Add randomness and external factors
        external_pressure = random.uniform(0.1, 0.3)
        
        vulnerability = min(1.0, base_vulnerability + external_pressure)
        
        return vulnerability
    
    def should_trigger_crisis(
        self, 
        faction_data: Any,
        trigger_type: Optional[SuccessionTrigger] = None
    ) -> bool:
        """
        Business rule: Determine if a succession crisis should be triggered for a faction
        """
        vulnerability = self.calculate_succession_vulnerability(faction_data)
        hidden_attrs = faction_data.get_hidden_attributes() if hasattr(faction_data, 'get_hidden_attributes') else {}
        
        if trigger_type:
            # Specific trigger - adjust probability
            if trigger_type == SuccessionTrigger.HIDDEN_AMBITION_COUP:
                # High ambition characters more likely to attempt coups
                coup_chance = hidden_attrs.get("hidden_ambition", 5) / 6.0 * 0.8
                return random.random() < coup_chance
            elif trigger_type in [SuccessionTrigger.LEADER_DEATH_NATURAL, SuccessionTrigger.LEADER_DEATH_VIOLENT]:
                # Death triggers always cause crisis
                return True
            elif trigger_type == SuccessionTrigger.EXTERNAL_PRESSURE:
                # External pressure depends on faction resilience
                pressure_resistance = hidden_attrs.get("hidden_resilience", 5) / 6.0
                return random.random() > pressure_resistance
        
        # General crisis probability based on vulnerability
        crisis_chance = vulnerability * 0.4  # 0-40% chance based on vulnerability
        return random.random() < crisis_chance
    
    def create_succession_crisis(self, faction_id: UUID, trigger: SuccessionTrigger) -> SuccessionCrisisEntity:
        """
        Business rule: Create a new succession crisis for a faction
        """
        faction = self.faction_data_provider.get_faction_by_id(faction_id)
        if not faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        # Determine succession type based on faction characteristics
        succession_type = self.determine_succession_type(faction)
        
        # Create crisis entity
        crisis = SuccessionCrisisEntity(
            faction_id=faction_id,
            succession_type=succession_type.value,
            trigger=trigger.value,
            status=SuccessionCrisisStatus.ACTIVE.value,
            start_date=datetime.utcnow(),
            candidates=[],
            properties={}
        )
        
        return crisis
    
    def evaluate_succession_candidates(
        self, 
        faction_id: UUID, 
        succession_type: SuccessionType
    ) -> List[SuccessionCandidate]:
        """
        Business rule: Evaluate and rank potential succession candidates
        """
        # Get potential candidates through membership service
        potential_leaders = self.membership_service.get_potential_leaders(faction_id)
        
        candidates = []
        for leader in potential_leaders:
            candidate = self._create_candidate_from_leader(leader, succession_type)
            candidates.append(candidate)
        
        # Sort by success probability
        candidates.sort(key=lambda c: c.success_probability, reverse=True)
        
        return candidates
    
    def resolve_succession_crisis(
        self, 
        crisis: SuccessionCrisisEntity,
        resolution_method: str = "automatic"
    ) -> Dict[str, Any]:
        """
        Business rule: Resolve a succession crisis and determine the winner
        """
        if not crisis.candidates:
            return {"error": "No candidates available for succession"}
        
        # Calculate final success probabilities
        candidates_with_scores = []
        for candidate in crisis.candidates:
            final_score = self._calculate_final_candidate_score(candidate, crisis.succession_type)
            candidates_with_scores.append((candidate, final_score))
        
        # Sort by final score
        candidates_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Determine winner based on succession type
        winner = self._determine_succession_winner(candidates_with_scores, crisis.succession_type)
        
        # Calculate transition effects
        transition_effects = self._calculate_succession_effects(winner, crisis)
        
        return {
            "winner": winner,
            "final_scores": {c[0].character_id: c[1] for c in candidates_with_scores},
            "succession_type": crisis.succession_type,
            "transition_effects": transition_effects,
            "resolution_date": datetime.utcnow()
        }
    
    def predict_succession_outcome(
        self, 
        faction_id: UUID, 
        succession_type: Optional[SuccessionType] = None
    ) -> Dict[str, Any]:
        """
        Business rule: Predict the likely outcome of a succession crisis
        """
        faction = self.faction_data_provider.get_faction_by_id(faction_id)
        if not faction:
            return {"error": "Faction not found"}
        
        if not succession_type:
            succession_type = self.determine_succession_type(faction)
        
        # Get candidates
        candidates = self.evaluate_succession_candidates(faction_id, succession_type)
        
        if not candidates:
            return {"error": "No viable candidates found"}
        
        # Calculate predictions
        predictions = []
        for candidate in candidates[:5]:  # Top 5 candidates
            prediction = {
                "candidate_id": candidate.character_id,
                "success_probability": candidate.success_probability,
                "expected_effects": self._predict_leadership_effects(candidate, faction),
                "risk_factors": self._identify_candidate_risks(candidate)
            }
            predictions.append(prediction)
        
        return {
            "succession_type": succession_type.value,
            "vulnerability": self.calculate_succession_vulnerability(faction),
            "predictions": predictions,
            "faction_stability_impact": self._predict_stability_impact(faction, succession_type)
        }
    
    # Private business logic methods
    
    def _create_candidate_from_leader(self, leader: Any, succession_type: SuccessionType) -> SuccessionCandidate:
        """Business rule: Create succession candidate from potential leader"""
        leader_attrs = getattr(leader, 'hidden_attributes', {})
        
        # Calculate base success probability based on succession type
        if succession_type == SuccessionType.MILITARY_COUP:
            success_prob = self._calculate_military_success_probability(leader_attrs)
        elif succession_type == SuccessionType.ECONOMIC_COMPETITION:
            success_prob = self._calculate_economic_success_probability(leader_attrs)
        elif succession_type == SuccessionType.DEMOCRATIC_ELECTION:
            success_prob = self._calculate_democratic_success_probability(leader_attrs)
        elif succession_type == SuccessionType.RELIGIOUS_ELECTION:
            success_prob = self._calculate_religious_success_probability(leader_attrs)
        else:
            success_prob = self._calculate_general_success_probability(leader_attrs)
        
        return SuccessionCandidate(
            character_id=getattr(leader, 'id', UUID()),
            faction_id=getattr(leader, 'faction_id', UUID()),
            success_probability=success_prob,
            support_base=random.uniform(0.1, 0.9),  # Would be calculated from relationships
            campaign_resources=random.uniform(0.2, 1.0),  # Would be calculated from wealth/influence
            legitimacy_claim=random.uniform(0.3, 1.0),  # Would be calculated from position/lineage
            attributes=leader_attrs,
            status="active"
        )
    
    def _calculate_military_success_probability(self, leader_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate success probability for military succession"""
        ambition = leader_attrs.get('hidden_ambition', 5) / 10.0
        discipline = leader_attrs.get('hidden_discipline', 5) / 10.0
        resilience = leader_attrs.get('hidden_resilience', 5) / 10.0
        
        return (ambition * 0.4 + discipline * 0.35 + resilience * 0.25)
    
    def _calculate_economic_success_probability(self, leader_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate success probability for economic succession"""
        pragmatism = leader_attrs.get('hidden_pragmatism', 5) / 10.0
        discipline = leader_attrs.get('hidden_discipline', 5) / 10.0
        ambition = leader_attrs.get('hidden_ambition', 5) / 10.0
        
        return (pragmatism * 0.4 + discipline * 0.3 + ambition * 0.3)
    
    def _calculate_democratic_success_probability(self, leader_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate success probability for democratic succession"""
        integrity = leader_attrs.get('hidden_integrity', 5) / 10.0
        pragmatism = leader_attrs.get('hidden_pragmatism', 5) / 10.0
        discipline = leader_attrs.get('hidden_discipline', 5) / 10.0
        
        return (integrity * 0.4 + pragmatism * 0.35 + discipline * 0.25)
    
    def _calculate_religious_success_probability(self, leader_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate success probability for religious succession"""
        integrity = leader_attrs.get('hidden_integrity', 5) / 10.0
        discipline = leader_attrs.get('hidden_discipline', 5) / 10.0
        low_impulsivity = (10 - leader_attrs.get('hidden_impulsivity', 5)) / 10.0
        
        return (integrity * 0.5 + discipline * 0.3 + low_impulsivity * 0.2)
    
    def _calculate_general_success_probability(self, leader_attrs: Dict[str, int]) -> float:
        """Business rule: Calculate general success probability"""
        # Balanced calculation across all attributes
        total = sum(leader_attrs.values()) if leader_attrs else 30
        return min(1.0, total / 60.0)  # Assuming max score of 10 per attribute
    
    def _calculate_final_candidate_score(self, candidate: SuccessionCandidate, succession_type: str) -> float:
        """Business rule: Calculate final score including all factors"""
        base_score = candidate.success_probability
        support_modifier = candidate.support_base * 0.3
        resource_modifier = candidate.campaign_resources * 0.2
        legitimacy_modifier = candidate.legitimacy_claim * 0.2
        
        return base_score + support_modifier + resource_modifier + legitimacy_modifier
    
    def _determine_succession_winner(self, candidates_with_scores: List[Tuple], succession_type: str) -> SuccessionCandidate:
        """Business rule: Determine winner with some randomness"""
        if not candidates_with_scores:
            raise ValueError("No candidates available")
        
        # Top candidate has best chance, but not guaranteed
        top_candidate, top_score = candidates_with_scores[0]
        
        # Add some randomness - higher scores have better chance but not guaranteed
        total_weight = sum(score for _, score in candidates_with_scores)
        
        if total_weight == 0:
            return top_candidate
        
        # Weighted random selection
        random_value = random.uniform(0, total_weight)
        current_weight = 0
        
        for candidate, score in candidates_with_scores:
            current_weight += score
            if random_value <= current_weight:
                return candidate
        
        return top_candidate  # Fallback
    
    def _calculate_succession_effects(self, winner: SuccessionCandidate, crisis: SuccessionCrisisEntity) -> Dict[str, Any]:
        """Business rule: Calculate effects of succession on faction"""
        effects = {
            "stability_change": 0.0,
            "unity_change": 0.0,
            "external_reputation_change": 0.0,
            "economic_impact": 0.0
        }
        
        winner_attrs = winner.attributes or {}
        
        # Stability effects based on winner's discipline and integrity
        effects["stability_change"] = (
            winner_attrs.get('hidden_discipline', 5) / 10.0 - 0.5 +
            winner_attrs.get('hidden_integrity', 5) / 10.0 - 0.5
        ) / 2.0
        
        # Unity effects based on how contested the succession was
        contest_factor = 1.0 - winner.success_probability  # More contested = lower unity
        effects["unity_change"] = -contest_factor * 0.3
        
        return effects
    
    def _predict_leadership_effects(self, candidate: SuccessionCandidate, faction: Any) -> Dict[str, str]:
        """Business rule: Predict leadership style and effects"""
        attrs = candidate.attributes or {}
        
        effects = {}
        
        if attrs.get('hidden_ambition', 5) > 7:
            effects["expansion_tendency"] = "high"
        elif attrs.get('hidden_ambition', 5) < 4:
            effects["expansion_tendency"] = "low"
        else:
            effects["expansion_tendency"] = "moderate"
        
        if attrs.get('hidden_integrity', 5) > 7:
            effects["diplomatic_style"] = "honorable"
        elif attrs.get('hidden_pragmatism', 5) > 7:
            effects["diplomatic_style"] = "pragmatic"
        else:
            effects["diplomatic_style"] = "opportunistic"
        
        return effects
    
    def _identify_candidate_risks(self, candidate: SuccessionCandidate) -> List[str]:
        """Business rule: Identify risks associated with candidate"""
        risks = []
        attrs = candidate.attributes or {}
        
        if attrs.get('hidden_impulsivity', 5) > 7:
            risks.append("Impulsive decision-making")
        if attrs.get('hidden_ambition', 5) > 8:
            risks.append("Overaggressive expansion")
        if attrs.get('hidden_integrity', 5) < 3:
            risks.append("Potential corruption")
        if candidate.legitimacy_claim < 0.4:
            risks.append("Legitimacy challenges")
        
        return risks
    
    def _predict_stability_impact(self, faction: Any, succession_type: SuccessionType) -> str:
        """Business rule: Predict overall stability impact"""
        faction_discipline = faction.get_hidden_attributes().get('hidden_discipline', 5) if hasattr(faction, 'get_hidden_attributes') else 5
        
        if succession_type == SuccessionType.MILITARY_COUP:
            if faction_discipline > 6:
                return "moderate_disruption"
            else:
                return "high_disruption"
        elif succession_type == SuccessionType.HEREDITARY:
            return "low_disruption"
        elif succession_type in [SuccessionType.DEMOCRATIC_ELECTION, SuccessionType.RELIGIOUS_ELECTION]:
            return "minimal_disruption"
        else:
            return "moderate_disruption"


def create_succession_business_service(
    faction_data_provider: FactionDataProvider,
    membership_service: MembershipService
) -> SuccessionBusinessService:
    """Factory function to create succession business service"""
    return SuccessionBusinessService(faction_data_provider, membership_service) 