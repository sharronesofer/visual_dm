"""
Faction Expansion Service

Service for managing different faction expansion strategies including military conquest,
economic influence, and cultural conversion according to Task 67 requirements.
"""

import logging
import random
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from backend.infrastructure.models.faction.models import FactionEntity
from backend.infrastructure.schemas.faction.expansion_schemas import ExpansionStrategy
from backend.systems.faction.services.territory_service import FactionTerritoryBusinessService
from backend.systems.faction.services.influence_service import FactionInfluenceBusinessService
from backend.infrastructure.shared.exceptions import FactionNotFoundError

logger = logging.getLogger(__name__)


@dataclass
class ExpansionAttempt:
    """Results of an expansion attempt"""
    success: bool
    strategy_used: ExpansionStrategy
    target_region_id: UUID
    cost: float
    effectiveness: float
    reason: str
    consequences: Dict[str, Any]


class FactionExpansionService:
    """Service for managing faction expansion strategies"""
    
    def __init__(self, territory_service=None, influence_service=None):
        # Proper dependency injection with defaults
        self.territory_service = territory_service
        self.influence_service = influence_service
        logger.info("FactionExpansionService initialized")
    
    def set_territory_service(self, territory_service):
        """Set territory service dependency (for late injection)"""
        self.territory_service = territory_service
    
    def set_influence_service(self, influence_service):
        """Set influence service dependency (for late injection)"""
        self.influence_service = influence_service
    
    def determine_expansion_strategy(self, faction: FactionEntity) -> ExpansionStrategy:
        """
        Determine the primary expansion strategy for a faction based on hidden attributes
        
        Uses the faction's hidden personality attributes to determine preferred expansion method:
        - High ambition + low integrity -> Military conquest
        - High pragmatism + high discipline -> Economic influence  
        - High integrity + low impulsivity -> Cultural conversion
        """
        # Get hidden attributes
        attrs = faction.get_hidden_attributes()
        
        # Calculate strategy scores based on personality
        military_score = (
            attrs["hidden_ambition"] * 2 +  # Ambitious factions prefer direct conquest
            (10 - attrs["hidden_integrity"]) +  # Less honorable factions use force (inverted from 1-10 range)
            attrs["hidden_impulsivity"]  # Impulsive factions attack quickly
        )
        
        economic_score = (
            attrs["hidden_pragmatism"] * 2 +  # Pragmatic factions use economic pressure
            attrs["hidden_discipline"] * 2 +  # Disciplined factions plan economic strategies
            attrs["hidden_ambition"]  # Ambitious factions want control through wealth
        )
        
        cultural_score = (
            attrs["hidden_integrity"] * 2 +  # Honorable factions prefer cultural means
            (10 - attrs["hidden_impulsivity"]) * 2 +  # Patient factions use slow cultural methods (inverted from 1-10 range)
            attrs["hidden_resilience"]  # Resilient factions invest in long-term conversion
        )
        
        # Add some randomness but weight by personality
        military_score += random.randint(0, 3)
        economic_score += random.randint(0, 3)
        cultural_score += random.randint(0, 3)
        
        # Determine primary strategy
        scores = {
            ExpansionStrategy.MILITARY: military_score,
            ExpansionStrategy.ECONOMIC: economic_score,
            ExpansionStrategy.CULTURAL: cultural_score
        }
        
        primary_strategy = max(scores, key=scores.get)
        
        logger.info(f"Faction {faction.name} expansion strategy: {primary_strategy.value} "
                   f"(scores: M:{military_score}, E:{economic_score}, C:{cultural_score})")
        
        return primary_strategy
    
    async def attempt_expansion(
        self,
        faction: FactionEntity,
        target_region_id: UUID,
        strategy: Optional[ExpansionStrategy] = None
    ) -> ExpansionAttempt:
        """
        Attempt to expand into a target region using the specified strategy
        """
        if strategy is None:
            strategy = self.determine_expansion_strategy(faction)
        
        logger.info(f"Faction {faction.name} attempting {strategy.value} expansion into region {target_region_id}")
        
        # Route to appropriate expansion method
        if strategy == ExpansionStrategy.MILITARY:
            return await self._attempt_military_expansion(faction, target_region_id)
        elif strategy == ExpansionStrategy.ECONOMIC:
            return await self._attempt_economic_expansion(faction, target_region_id)
        elif strategy == ExpansionStrategy.CULTURAL:
            return await self._attempt_cultural_expansion(faction, target_region_id)
        else:
            raise ValueError(f"Unknown expansion strategy: {strategy}")
    
    async def _attempt_military_expansion(
        self,
        faction: FactionEntity,
        target_region_id: UUID
    ) -> ExpansionAttempt:
        """
        Military conquest expansion strategy - direct territorial takeover through force
        """
        attrs = faction.get_hidden_attributes()
        
        # Calculate military effectiveness based on faction attributes
        military_strength = (
            attrs["hidden_ambition"] * 0.3 +  # Ambitious factions fight harder
            attrs["hidden_discipline"] * 0.3 +  # Disciplined factions coordinate better
            (10 - attrs["hidden_impulsivity"]) * 0.2 +  # Less impulsive = better strategy (inverted from 1-10 range)
            attrs["hidden_resilience"] * 0.2  # Resilient factions endure campaigns
        ) / 10.0  # Normalize to 0-1 (from 1-10 range)
        
        # Add randomness for battle uncertainty
        battle_roll = random.uniform(0.3, 1.0)
        final_effectiveness = military_strength * battle_roll
        
        # Determine success
        success = final_effectiveness > 0.55
        cost = 0.8 if success else 0.5  # Military campaigns are expensive
        
        consequences = {
            "tension_increase": 15 if success else 10,
            "military_casualties": random.randint(50, 200) if success else random.randint(100, 300),
            "reputation_change": 5 if success else -10,
            "regional_stability": -20 if success else -30
        }
        
        if success:
            # Claim territory through conquest
            if self.territory_service:
                await self.territory_service.claim_territory(
                    faction_id=faction.id,
                    faction_name=faction.name,
                    region_metadata=None,  # Would be passed from caller
                    claim_method="military_conquest",
                    control_strength=final_effectiveness,
                    claim_details={
                        "expansion_strategy": "military",
                        "battle_effectiveness": final_effectiveness,
                        "casualties": consequences["military_casualties"]
                    }
                )
            else:
                logger.warning("Territory service not available for military expansion")
            reason = f"Successfully conquered region through military force (effectiveness: {final_effectiveness:.2f})"
        else:
            reason = f"Military conquest failed (effectiveness: {final_effectiveness:.2f})"
        
        return ExpansionAttempt(
            success=success,
            strategy_used=ExpansionStrategy.MILITARY,
            target_region_id=target_region_id,
            cost=cost,
            effectiveness=final_effectiveness,
            reason=reason,
            consequences=consequences
        )
    
    async def _attempt_economic_expansion(
        self,
        faction: FactionEntity,
        target_region_id: UUID
    ) -> ExpansionAttempt:
        """
        Economic influence expansion strategy - control through trade and economic pressure
        """
        attrs = faction.get_hidden_attributes()
        
        # Calculate economic effectiveness
        economic_strength = (
            attrs["hidden_pragmatism"] * 0.4 +  # Pragmatic factions excel at economics
            attrs["hidden_discipline"] * 0.3 +  # Disciplined factions manage resources well
            attrs["hidden_ambition"] * 0.2 +  # Ambitious factions pursue wealth aggressively
            (10 - attrs["hidden_impulsivity"]) * 0.1  # Patient factions build lasting economies (inverted from 1-10 range)
        ) / 10.0  # Normalize to 0-1 (from 1-10 range)
        
        # Economic expansion has more consistent but slower results
        market_conditions = random.uniform(0.6, 1.0)
        final_effectiveness = economic_strength * market_conditions
        
        # Economic expansion is more reliable but takes time
        success = final_effectiveness > 0.5
        cost = 0.6 if success else 0.4  # Economic pressure costs money
        
        consequences = {
            "economic_dependency": 25 if success else 10,
            "trade_route_control": 40 if success else 15,
            "local_business_influence": 60 if success else 20,
            "wealth_transfer": random.randint(1000, 5000) if success else random.randint(200, 800),
            "regional_prosperity": 10 if success else -5
        }
        
        if success:
            # Update economic influence in region
            if self.influence_service:
                await self.influence_service.update_region_influence(
                    faction_id=faction.id,
                    region_id=target_region_id,
                    influence=final_effectiveness * 100,  # Convert to 0-100 scale
                    influence_type="economic"
                )
            else:
                logger.warning("Influence service not available for economic expansion")
            reason = f"Established economic dominance through trade and investment (effectiveness: {final_effectiveness:.2f})"
        else:
            reason = f"Economic expansion failed - market resistance (effectiveness: {final_effectiveness:.2f})"
        
        return ExpansionAttempt(
            success=success,
            strategy_used=ExpansionStrategy.ECONOMIC,
            target_region_id=target_region_id,
            cost=cost,
            effectiveness=final_effectiveness,
            reason=reason,
            consequences=consequences
        )
    
    async def _attempt_cultural_expansion(
        self,
        faction: FactionEntity,
        target_region_id: UUID
    ) -> ExpansionAttempt:
        """
        Cultural conversion expansion strategy - spread ideology and convert NPCs
        """
        attrs = faction.get_hidden_attributes()
        
        # Calculate cultural effectiveness
        cultural_strength = (
            attrs["hidden_integrity"] * 0.4 +  # Honorable factions are trusted
            (10 - attrs["hidden_impulsivity"]) * 0.3 +  # Patient factions build relationships (inverted from 1-10 range)
            attrs["hidden_resilience"] * 0.2 +  # Resilient factions persist through resistance
            attrs["hidden_discipline"] * 0.1  # Disciplined factions organize cultural campaigns
        ) / 10.0  # Normalize to 0-1 (from 1-10 range)
        
        # Cultural conversion depends on local receptiveness
        cultural_receptiveness = random.uniform(0.4, 0.9)
        final_effectiveness = cultural_strength * cultural_receptiveness
        
        # Cultural expansion is slow but stable when successful
        success = final_effectiveness > 0.45
        cost = 0.4 if success else 0.3  # Cultural campaigns are less expensive
        
        consequences = {
            "npc_conversion_rate": int(final_effectiveness * 30) if success else int(final_effectiveness * 10),
            "cultural_influence": 35 if success else 12,
            "ideology_spread": 50 if success else 15,
            "local_acceptance": 20 if success else -5,
            "long_term_stability": 25 if success else 5
        }
        
        if success:
            # Update cultural influence in region
            if self.influence_service:
                await self.influence_service.update_region_influence(
                    faction_id=faction.id,
                    region_id=target_region_id,
                    influence=final_effectiveness * 80,  # Cultural influence grows slower but more stable
                    influence_type="cultural"
                )
            else:
                logger.warning("Influence service not available for cultural expansion")
            reason = f"Successfully converted local population through cultural influence (effectiveness: {final_effectiveness:.2f})"
        else:
            reason = f"Cultural conversion failed - local resistance (effectiveness: {final_effectiveness:.2f})"
        
        return ExpansionAttempt(
            success=success,
            strategy_used=ExpansionStrategy.CULTURAL,
            target_region_id=target_region_id,
            cost=cost,
            effectiveness=final_effectiveness,
            reason=reason,
            consequences=consequences
        )
    
    def get_expansion_aggressiveness(self, faction: FactionEntity) -> float:
        """
        Calculate how aggressively a faction pursues expansion based on hidden attributes
        """
        attrs = faction.get_hidden_attributes()
        
        aggressiveness = (
            attrs["hidden_ambition"] * 0.5 +  # Primary driver of expansion
            attrs["hidden_impulsivity"] * 0.3 +  # Impulsive factions expand rapidly
            (10 - attrs["hidden_integrity"]) * 0.1 +  # Less honorable = more aggressive (inverted from 1-10 range)
            attrs["hidden_resilience"] * 0.1  # Resilient factions keep trying
        ) / 10.0  # Normalize to 0-1 (from 1-10 range)
        
        return aggressiveness
    
    def should_attempt_expansion(self, faction: FactionEntity) -> bool:
        """
        Determine if a faction should attempt expansion based on their personality
        """
        aggressiveness = self.get_expansion_aggressiveness(faction)
        
        # Random chance modified by aggressiveness
        expansion_chance = aggressiveness * 0.8 + 0.1  # 10% to 90% chance
        
        return random.random() < expansion_chance


def get_faction_expansion_service() -> FactionExpansionService:
    """Get faction expansion service instance"""
    return FactionExpansionService() 