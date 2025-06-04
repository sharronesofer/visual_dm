"""
Faction Territory Service - Pure Business Logic

Service for managing faction territorial control business rules and logic,
separated from technical infrastructure concerns.
"""

from typing import Optional, Dict, Any, List, Protocol
from uuid import UUID
from datetime import datetime

from backend.systems.faction.models import FactionEntity
from backend.systems.region.models import RegionMetadata


# Business Domain Models
class TerritoryClaimRequest:
    """Business domain model for territory claim requests"""
    def __init__(self,
                 faction_id: UUID,
                 faction_name: str,
                 region_metadata: RegionMetadata,
                 claim_method: str = "conquest",
                 control_strength: float = 1.0,
                 previous_controller: Optional[UUID] = None,
                 claim_details: Optional[Dict[str, Any]] = None):
        self.faction_id = faction_id
        self.faction_name = faction_name
        self.region_metadata = region_metadata
        self.claim_method = claim_method
        self.control_strength = max(0.0, min(1.0, control_strength))  # Business rule: clamp to 0-1
        self.previous_controller = previous_controller
        self.claim_details = claim_details or {}


class TerritoryReleaseRequest:
    """Business domain model for territory release requests"""
    def __init__(self,
                 faction_id: UUID,
                 faction_name: str,
                 region_id: UUID,
                 region_name: str,
                 release_reason: str = "voluntary",
                 new_controller: Optional[UUID] = None,
                 continent_id: Optional[UUID] = None):
        self.faction_id = faction_id
        self.faction_name = faction_name
        self.region_id = region_id
        self.region_name = region_name
        self.release_reason = release_reason
        self.new_controller = new_controller
        self.continent_id = continent_id


class TerritoryContestRequest:
    """Business domain model for territory contest requests"""
    def __init__(self,
                 region_id: UUID,
                 region_name: str,
                 contesting_factions: List[UUID],
                 current_controller: Optional[UUID] = None,
                 contest_type: str = "military",
                 contest_details: Optional[Dict[str, Any]] = None,
                 continent_id: Optional[UUID] = None):
        self.region_id = region_id
        self.region_name = region_name
        self.contesting_factions = contesting_factions
        self.current_controller = current_controller
        self.contest_type = contest_type
        self.contest_details = contest_details or {}
        self.continent_id = continent_id


class SettlementRequest:
    """Business domain model for settlement establishment requests"""
    def __init__(self,
                 faction_id: UUID,
                 faction_name: str,
                 region_id: UUID,
                 region_name: str,
                 settlement_name: str,
                 settlement_type: str = "outpost",
                 initial_population: int = 100,
                 continent_id: Optional[UUID] = None):
        self.faction_id = faction_id
        self.faction_name = faction_name
        self.region_id = region_id
        self.region_name = region_name
        self.settlement_name = settlement_name
        self.settlement_type = settlement_type
        self.initial_population = max(0, initial_population)  # Business rule: no negative population
        self.continent_id = continent_id


class WarfareRequest:
    """Business domain model for territorial warfare requests"""
    def __init__(self,
                 attacking_faction_id: UUID,
                 attacking_faction_name: str,
                 defending_faction_id: UUID,
                 defending_faction_name: str,
                 region_id: UUID,
                 region_name: str,
                 battle_outcome: str,
                 casualties: Optional[Dict[str, int]] = None,
                 continent_id: Optional[UUID] = None):
        self.attacking_faction_id = attacking_faction_id
        self.attacking_faction_name = attacking_faction_name
        self.defending_faction_id = defending_faction_id
        self.defending_faction_name = defending_faction_name
        self.region_id = region_id
        self.region_name = region_name
        self.battle_outcome = battle_outcome
        self.casualties = casualties or {}
        self.continent_id = continent_id


# Business Logic Protocols (dependency injection)
class TerritoryEventPublisher(Protocol):
    """Protocol for publishing territory events"""
    
    async def publish_territory_claimed_event(
        self,
        region_metadata: RegionMetadata,
        faction_id: UUID,
        faction_name: str,
        previous_controller: Optional[UUID] = None,
        claim_method: str = "conquest",
        control_strength: float = 1.0,
        claim_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish territory claimed event"""
        ...
    
    async def publish_territory_released_event(
        self,
        faction_id: UUID,
        faction_name: str,
        region_id: UUID,
        region_name: str,
        release_reason: str = "voluntary",
        new_controller: Optional[UUID] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish territory released event"""
        ...
    
    async def publish_territory_contested_event(
        self,
        region_id: UUID,
        region_name: str,
        contesting_factions: List[UUID],
        current_controller: Optional[UUID] = None,
        contest_type: str = "military",
        contest_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish territory contested event"""
        ...
    
    async def publish_settlement_created_event(
        self,
        faction_id: UUID,
        faction_name: str,
        region_id: UUID,
        region_name: str,
        settlement_name: str,
        settlement_type: str = "outpost",
        initial_population: int = 100,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish settlement created event"""
        ...
    
    async def publish_population_changed_event(
        self,
        region_id: UUID,
        region_name: str,
        old_population: int,
        new_population: int,
        change_reason: str = "natural_growth",
        affected_demographics: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish population changed event"""
        ...
    
    async def publish_territorial_warfare_events(
        self,
        attacking_faction_id: UUID,
        attacking_faction_name: str,
        defending_faction_id: UUID,
        defending_faction_name: str,
        region_id: UUID,
        region_name: str,
        battle_outcome: str,
        casualties: Optional[Dict[str, int]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish territorial warfare events"""
        ...


class FactionTerritoryBusinessService:
    """Business service for faction territorial control - pure business rules"""
    
    def __init__(self, event_publisher: TerritoryEventPublisher):
        self.event_publisher = event_publisher

    async def claim_territory(self, claim_request: TerritoryClaimRequest) -> Dict[str, Any]:
        """
        Business logic: Handle faction claiming territory in a region
        
        Business rules:
        - Control strength must be between 0.0 and 1.0
        - Certain claim methods require higher control strength
        - Previous controller must be different from new controller
        - Claim details must include timestamp and justification
        """
        # Business rule: Validate claim request
        if claim_request.faction_id == claim_request.previous_controller:
            raise ValueError("Faction cannot claim territory from itself")
        
        # Business rule: Validate claim method requirements
        if claim_request.claim_method == "conquest" and claim_request.control_strength < 0.7:
            raise ValueError("Conquest claims require at least 70% control strength")
        elif claim_request.claim_method == "diplomacy" and claim_request.control_strength < 0.5:
            raise ValueError("Diplomatic claims require at least 50% control strength")
        
        # Business rule: Enhance claim details with business context
        enhanced_details = {
            **claim_request.claim_details,
            "business_validation": {
                "claim_timestamp": datetime.utcnow().isoformat(),
                "claim_legitimacy": self._assess_claim_legitimacy(claim_request),
                "expected_stability": self._predict_territorial_stability(claim_request)
            }
        }
        
        # Delegate to technical event publisher
        await self.event_publisher.publish_territory_claimed_event(
            region_metadata=claim_request.region_metadata,
            faction_id=claim_request.faction_id,
            faction_name=claim_request.faction_name,
            previous_controller=claim_request.previous_controller,
            claim_method=claim_request.claim_method,
            control_strength=claim_request.control_strength,
            claim_details=enhanced_details
        )
        
        return {
            "status": "claimed",
            "faction_id": claim_request.faction_id,
            "region_id": claim_request.region_metadata.id,
            "control_strength": claim_request.control_strength,
            "claim_legitimacy": enhanced_details["business_validation"]["claim_legitimacy"],
            "stability_prediction": enhanced_details["business_validation"]["expected_stability"]
        }

    async def release_territory(self, release_request: TerritoryReleaseRequest) -> Dict[str, Any]:
        """
        Business logic: Handle faction releasing control of territory
        
        Business rules:
        - Voluntary releases have different consequences than forced releases
        - Must specify new controller for strategic territories
        - Release reasons affect faction reputation
        """
        # Business rule: Validate release logic
        if release_request.release_reason == "strategic_withdrawal" and not release_request.new_controller:
            raise ValueError("Strategic withdrawals must specify a successor controller")
        
        # Business rule: Assess release consequences
        release_consequences = self._assess_release_consequences(release_request)
        
        # Delegate to technical event publisher
        await self.event_publisher.publish_territory_released_event(
            faction_id=release_request.faction_id,
            faction_name=release_request.faction_name,
            region_id=release_request.region_id,
            region_name=release_request.region_name,
            release_reason=release_request.release_reason,
            new_controller=release_request.new_controller,
            continent_id=release_request.continent_id
        )
        
        return {
            "status": "released",
            "faction_id": release_request.faction_id,
            "region_id": release_request.region_id,
            "release_reason": release_request.release_reason,
            "consequences": release_consequences
        }

    async def contest_territory(self, contest_request: TerritoryContestRequest) -> Dict[str, Any]:
        """
        Business logic: Handle territory being contested by multiple factions
        
        Business rules:
        - Must have at least 2 contesting factions
        - Current controller can be one of the contestants
        - Contest intensity affects regional stability
        """
        # Business rule: Validate contest
        if len(contest_request.contesting_factions) < 2:
            raise ValueError("Territory contests require at least 2 factions")
        
        # Business rule: Assess contest dynamics
        contest_analysis = self._analyze_territorial_contest(contest_request)
        
        # Business rule: Enhance contest details
        enhanced_details = {
            **contest_request.contest_details,
            "business_analysis": contest_analysis
        }
        
        # Delegate to technical event publisher
        await self.event_publisher.publish_territory_contested_event(
            region_id=contest_request.region_id,
            region_name=contest_request.region_name,
            contesting_factions=contest_request.contesting_factions,
            current_controller=contest_request.current_controller,
            contest_type=contest_request.contest_type,
            contest_details=enhanced_details,
            continent_id=contest_request.continent_id
        )
        
        return {
            "status": "contested",
            "region_id": contest_request.region_id,
            "contestant_count": len(contest_request.contesting_factions),
            "contest_intensity": contest_analysis["intensity"],
            "predicted_outcome": contest_analysis["likely_winner"]
        }

    async def establish_settlement(self, settlement_request: SettlementRequest) -> Dict[str, Any]:
        """
        Business logic: Handle faction establishing a settlement in a region
        
        Business rules:
        - Settlement types have minimum population requirements
        - Settlement names must be unique within region
        - Initial population affects settlement viability
        """
        # Business rule: Validate settlement requirements
        min_population = self._get_minimum_population_for_settlement_type(settlement_request.settlement_type)
        if settlement_request.initial_population < min_population:
            raise ValueError(f"Settlement type '{settlement_request.settlement_type}' requires at least {min_population} population")
        
        # Business rule: Assess settlement viability
        viability_assessment = self._assess_settlement_viability(settlement_request)
        
        # Delegate to technical event publisher
        await self.event_publisher.publish_settlement_created_event(
            faction_id=settlement_request.faction_id,
            faction_name=settlement_request.faction_name,
            region_id=settlement_request.region_id,
            region_name=settlement_request.region_name,
            settlement_name=settlement_request.settlement_name,
            settlement_type=settlement_request.settlement_type,
            initial_population=settlement_request.initial_population,
            continent_id=settlement_request.continent_id
        )
        
        return {
            "status": "established",
            "settlement_name": settlement_request.settlement_name,
            "settlement_type": settlement_request.settlement_type,
            "initial_population": settlement_request.initial_population,
            "viability": viability_assessment
        }

    async def update_population(
        self,
        region_id: UUID,
        region_name: str,
        old_population: int,
        new_population: int,
        change_reason: str = "natural_growth",
        affected_demographics: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Business logic: Handle population changes in faction-controlled territory
        
        Business rules:
        - Population changes must be realistic (not more than 20% in one update)
        - Negative population changes require justification
        - Demographics data affects growth patterns
        """
        # Business rule: Validate population change
        population_change = new_population - old_population
        change_percentage = abs(population_change) / old_population if old_population > 0 else 0
        
        if change_percentage > 0.2:  # 20% change limit
            raise ValueError(f"Population change of {change_percentage:.1%} exceeds realistic limits")
        
        if new_population < 0:
            raise ValueError("Population cannot be negative")
        
        # Business rule: Assess population change impact
        change_impact = self._assess_population_change_impact(
            old_population, new_population, change_reason, affected_demographics
        )
        
        # Delegate to technical event publisher
        await self.event_publisher.publish_population_changed_event(
            region_id=region_id,
            region_name=region_name,
            old_population=old_population,
            new_population=new_population,
            change_reason=change_reason,
            affected_demographics=affected_demographics,
            continent_id=continent_id
        )
        
        return {
            "status": "updated",
            "region_id": region_id,
            "population_change": population_change,
            "change_percentage": round(change_percentage * 100, 1),
            "impact_assessment": change_impact
        }

    async def handle_territorial_warfare(self, warfare_request: WarfareRequest) -> Dict[str, Any]:
        """
        Business logic: Handle warfare between factions over territory
        
        Business rules:
        - Valid battle outcomes: attacker_victory, defender_victory, stalemate
        - Casualties must be proportional to faction populations
        - Warfare outcomes affect future territorial control
        """
        # Business rule: Validate warfare request
        valid_outcomes = ["attacker_victory", "defender_victory", "stalemate"]
        if warfare_request.battle_outcome not in valid_outcomes:
            raise ValueError(f"Invalid battle outcome: {warfare_request.battle_outcome}")
        
        if warfare_request.attacking_faction_id == warfare_request.defending_faction_id:
            raise ValueError("Faction cannot wage war against itself")
        
        # Business rule: Assess warfare consequences
        warfare_consequences = self._assess_warfare_consequences(warfare_request)
        
        # Delegate to technical event publisher
        await self.event_publisher.publish_territorial_warfare_events(
            attacking_faction_id=warfare_request.attacking_faction_id,
            attacking_faction_name=warfare_request.attacking_faction_name,
            defending_faction_id=warfare_request.defending_faction_id,
            defending_faction_name=warfare_request.defending_faction_name,
            region_id=warfare_request.region_id,
            region_name=warfare_request.region_name,
            battle_outcome=warfare_request.battle_outcome,
            casualties=warfare_request.casualties,
            continent_id=warfare_request.continent_id
        )
        
        return {
            "status": "warfare_resolved",
            "battle_outcome": warfare_request.battle_outcome,
            "region_id": warfare_request.region_id,
            "consequences": warfare_consequences,
            "total_casualties": sum(warfare_request.casualties.values()) if warfare_request.casualties else 0
        }

    def _assess_claim_legitimacy(self, claim_request: TerritoryClaimRequest) -> str:
        """Business rule: Assess the legitimacy of a territorial claim"""
        if claim_request.claim_method == "inheritance":
            return "high"
        elif claim_request.claim_method == "diplomacy":
            return "medium"
        elif claim_request.claim_method == "conquest" and claim_request.control_strength >= 0.8:
            return "medium"
        else:
            return "low"

    def _predict_territorial_stability(self, claim_request: TerritoryClaimRequest) -> str:
        """Business rule: Predict territorial stability after claim"""
        if claim_request.control_strength >= 0.9:
            return "stable"
        elif claim_request.control_strength >= 0.7:
            return "moderate"
        else:
            return "unstable"

    def _assess_release_consequences(self, release_request: TerritoryReleaseRequest) -> Dict[str, str]:
        """Business rule: Assess consequences of territory release"""
        consequences = {}
        
        if release_request.release_reason == "voluntary":
            consequences["reputation"] = "neutral"
        elif release_request.release_reason == "military_defeat":
            consequences["reputation"] = "negative"
        elif release_request.release_reason == "strategic_withdrawal":
            consequences["reputation"] = "slight_negative"
        else:
            consequences["reputation"] = "unknown"
        
        consequences["strategic_impact"] = "moderate" if release_request.new_controller else "high"
        
        return consequences

    def _analyze_territorial_contest(self, contest_request: TerritoryContestRequest) -> Dict[str, Any]:
        """Business rule: Analyze territorial contest dynamics"""
        contestant_count = len(contest_request.contesting_factions)
        
        # Determine contest intensity
        if contestant_count >= 4:
            intensity = "very_high"
        elif contestant_count == 3:
            intensity = "high"
        else:
            intensity = "moderate"
        
        # Predict likely winner (simplified logic)
        likely_winner = contest_request.current_controller if contest_request.current_controller else "uncertain"
        
        return {
            "intensity": intensity,
            "contestant_count": contestant_count,
            "likely_winner": likely_winner,
            "stability_risk": "high" if contestant_count >= 3 else "moderate"
        }

    def _get_minimum_population_for_settlement_type(self, settlement_type: str) -> int:
        """Business rule: Get minimum population requirements for settlement types"""
        requirements = {
            "outpost": 25,
            "village": 100,
            "town": 500,
            "city": 2000,
            "fortress": 200,
            "trading_post": 50
        }
        return requirements.get(settlement_type, 100)  # Default to village requirements

    def _assess_settlement_viability(self, settlement_request: SettlementRequest) -> str:
        """Business rule: Assess settlement viability"""
        min_pop = self._get_minimum_population_for_settlement_type(settlement_request.settlement_type)
        
        if settlement_request.initial_population >= min_pop * 2:
            return "high"
        elif settlement_request.initial_population >= min_pop * 1.5:
            return "good"
        elif settlement_request.initial_population >= min_pop:
            return "adequate"
        else:
            return "poor"

    def _assess_population_change_impact(
        self,
        old_population: int,
        new_population: int,
        change_reason: str,
        demographics: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Business rule: Assess impact of population changes"""
        change = new_population - old_population
        
        impact = {
            "economic": "neutral",
            "social": "neutral",
            "strategic": "neutral"
        }
        
        if change > 0:  # Population growth
            if change_reason == "migration":
                impact["economic"] = "positive"
                impact["social"] = "mixed"
            elif change_reason == "natural_growth":
                impact["economic"] = "positive"
                impact["social"] = "positive"
        else:  # Population decline
            if change_reason == "warfare":
                impact["strategic"] = "negative"
                impact["social"] = "negative"
            elif change_reason == "disease":
                impact["economic"] = "negative"
                impact["social"] = "negative"
        
        return impact

    def _assess_warfare_consequences(self, warfare_request: WarfareRequest) -> Dict[str, Any]:
        """Business rule: Assess consequences of territorial warfare"""
        consequences = {
            "territorial_control": "unchanged",
            "regional_stability": "decreased",
            "faction_relations": "deteriorated"
        }
        
        if warfare_request.battle_outcome == "attacker_victory":
            consequences["territorial_control"] = "changed_to_attacker"
        elif warfare_request.battle_outcome == "defender_victory":
            consequences["territorial_control"] = "retained_by_defender"
        # stalemate keeps "unchanged"
        
        # Assess casualty impact
        total_casualties = sum(warfare_request.casualties.values()) if warfare_request.casualties else 0
        if total_casualties > 1000:
            consequences["population_impact"] = "severe"
            consequences["regional_stability"] = "severely_decreased"
        elif total_casualties > 100:
            consequences["population_impact"] = "moderate"
        else:
            consequences["population_impact"] = "light"
        
        return consequences


def create_faction_territory_business_service(
    event_publisher: TerritoryEventPublisher
) -> FactionTerritoryBusinessService:
    """Factory function for creating faction territory business service"""
    return FactionTerritoryBusinessService(event_publisher) 