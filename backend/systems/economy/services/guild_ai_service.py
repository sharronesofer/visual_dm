"""
Guild AI Service

This module implements intelligent guild behavior, autonomous decision-making,
and complete guild system integration with factions and economy.
"""

import logging
import random
import math
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.orm import Session
from dataclasses import dataclass
from enum import Enum

from backend.infrastructure.database.economy.advanced_models import (
    MerchantGuildEntity, EconomicCompetition, EconomicCycle
)
from backend.systems.economy.models.advanced_economy import (
    CompetitionType, EconomicCyclePhase
)
from backend.infrastructure.config_loaders.economy_config_loader import get_economy_config

logger = logging.getLogger(__name__)


class GuildPersonality(Enum):
    """Guild personality types that drive decision-making"""
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    INNOVATIVE = "innovative"
    DIPLOMATIC = "diplomatic"


class ExpansionStrategy(Enum):
    """Guild expansion strategies"""
    RAPID_EXPANSION = "rapid_expansion"
    STEADY_GROWTH = "steady_growth"
    DEFENSIVE_CONSOLIDATION = "defensive_consolidation"
    OPPORTUNISTIC = "opportunistic"


class PricingStrategy(Enum):
    """Guild pricing strategies"""
    PRICE_LEADERSHIP = "price_leadership"
    COMPETITIVE_PRICING = "competitive_pricing"
    PREMIUM_PRICING = "premium_pricing"
    PREDATORY_PRICING = "predatory_pricing"
    COOPERATIVE_PRICING = "cooperative_pricing"


@dataclass
class ExpansionOption:
    """Represents a potential expansion opportunity"""
    region_id: str
    priority_score: float
    expansion_cost: float
    expected_profit: float
    risk_level: float
    competition_level: float
    strategic_value: float
    reasoning: str


@dataclass
class CompetitionThreat:
    """Represents a competitive threat to the guild"""
    threat_id: str
    threat_type: str
    severity: float
    source_guild_id: Optional[UUID]
    affected_regions: List[str]
    recommended_response: str
    urgency: float


@dataclass
class AllianceProposal:
    """Represents a potential alliance opportunity"""
    target_guild_id: UUID
    alliance_type: str
    mutual_benefit_score: float
    trust_level: float
    strategic_alignment: float
    proposed_terms: Dict[str, Any]
    success_probability: float


@dataclass
class ManipulationPlan:
    """Represents a market manipulation strategy"""
    manipulation_type: str
    target_markets: List[str]
    target_resources: List[str]
    expected_impact: float
    execution_cost: float
    risk_level: float
    timeline: int  # days
    success_probability: float


class GuildAIService:
    """
    Service for intelligent guild behavior and autonomous decision-making.
    
    This service implements AI-driven guild personalities, strategic planning,
    and automated guild operations including expansion, pricing, competition,
    and alliance management.
    """
    
    def __init__(self, db_session: Session):
        """Initialize the Guild AI Service."""
        self.db_session = db_session
        self.config = get_economy_config()
        self.guild_ai_config = self._load_guild_ai_config()
        
    def _load_guild_ai_config(self) -> Dict[str, Any]:
        """Load guild AI configuration."""
        return {
            "personality_traits": {
                "aggressive": {
                    "expansion_rate": 0.3,
                    "risk_tolerance": 0.8,
                    "cooperation_willingness": 0.2,
                    "competition_aggression": 0.9,
                    "profit_priority": 0.8
                },
                "conservative": {
                    "expansion_rate": 0.1,
                    "risk_tolerance": 0.3,
                    "cooperation_willingness": 0.7,
                    "competition_aggression": 0.3,
                    "profit_priority": 0.6
                },
                "innovative": {
                    "expansion_rate": 0.25,
                    "risk_tolerance": 0.7,
                    "cooperation_willingness": 0.5,
                    "competition_aggression": 0.6,
                    "profit_priority": 0.7
                },
                "diplomatic": {
                    "expansion_rate": 0.15,
                    "risk_tolerance": 0.4,
                    "cooperation_willingness": 0.9,
                    "competition_aggression": 0.2,
                    "profit_priority": 0.5
                }
            },
            "decision_weights": {
                "profit_priority": 0.4,
                "territory_priority": 0.3,
                "influence_priority": 0.3
            },
            "expansion_thresholds": {
                "wealth_requirement": 5000.0,
                "influence_requirement": 0.3,
                "max_regions_per_expansion": 2
            },
            "alliance_criteria": {
                "min_trust_level": 0.6,
                "min_mutual_benefit": 0.5,
                "max_alliances": 3
            }
        }
    
    def get_guild_personality(self, guild: MerchantGuildEntity) -> GuildPersonality:
        """Determine guild personality based on its characteristics."""
        # Use guild metadata or derive from behavior patterns
        guild_metadata = getattr(guild, 'guild_metadata', {}) or {}
        
        if 'personality' in guild_metadata:
            try:
                return GuildPersonality(guild_metadata['personality'])
            except ValueError:
                pass
        
        # Derive personality from guild characteristics
        if guild.pricing_influence > 0.7 and guild.market_share > 0.5:
            return GuildPersonality.AGGRESSIVE
        elif len(guild.allied_guilds or []) > 2:
            return GuildPersonality.DIPLOMATIC
        elif guild.coordination_level > 0.8:
            return GuildPersonality.INNOVATIVE
        else:
            return GuildPersonality.CONSERVATIVE
    
    def evaluate_expansion_opportunities(self, guild_id: UUID) -> List[ExpansionOption]:
        """
        Evaluate potential expansion opportunities for a guild.
        
        Args:
            guild_id: ID of the guild to evaluate expansion for
            
        Returns:
            List of expansion opportunities ranked by priority
        """
        try:
            guild = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.id == guild_id
            ).first()
            
            if not guild:
                logger.error(f"Guild {guild_id} not found")
                return []
            
            personality = self.get_guild_personality(guild)
            personality_config = self.guild_ai_config["personality_traits"][personality.value]
            
            # Get current territories
            current_territories = set(guild.territory_control or [])
            
            # Evaluate potential regions (simplified - would query actual regions)
            potential_regions = self._get_potential_expansion_regions(current_territories)
            
            expansion_options = []
            for region_id in potential_regions:
                option = self._evaluate_region_expansion(
                    guild, region_id, personality_config
                )
                if option:
                    expansion_options.append(option)
            
            # Sort by priority score
            expansion_options.sort(key=lambda x: x.priority_score, reverse=True)
            
            # Filter based on guild's expansion capacity
            max_expansions = self.guild_ai_config["expansion_thresholds"]["max_regions_per_expansion"]
            return expansion_options[:max_expansions]
            
        except Exception as e:
            logger.error(f"Error evaluating expansion opportunities: {e}")
            return []
    
    def _get_potential_expansion_regions(self, current_territories: set) -> List[str]:
        """Get list of potential regions for expansion."""
        # Simplified implementation - would query actual region data
        all_regions = [f"region_{i}" for i in range(1, 21)]  # 20 regions
        return [r for r in all_regions if r not in current_territories]
    
    def _evaluate_region_expansion(self, guild: MerchantGuildEntity, 
                                 region_id: str, personality_config: Dict[str, float]) -> Optional[ExpansionOption]:
        """Evaluate a specific region for expansion potential."""
        try:
            # Calculate various factors (simplified)
            base_profit = random.uniform(1000, 5000)
            competition_level = random.uniform(0.1, 0.9)
            risk_level = random.uniform(0.2, 0.8)
            expansion_cost = base_profit * random.uniform(0.5, 2.0)
            
            # Adjust for guild personality
            risk_tolerance = personality_config["risk_tolerance"]
            profit_priority = personality_config["profit_priority"]
            
            # Calculate strategic value
            strategic_value = self._calculate_strategic_value(guild, region_id)
            
            # Calculate expected profit adjusted for risk
            risk_adjusted_profit = base_profit * (1 - (risk_level * (1 - risk_tolerance)))
            
            # Calculate priority score
            priority_score = (
                (risk_adjusted_profit / expansion_cost) * profit_priority +
                strategic_value * (1 - profit_priority) -
                competition_level * 0.3
            )
            
            # Only consider if meets minimum thresholds
            if (expansion_cost > guild.total_wealth * 0.8 or 
                priority_score < 0.3):
                return None
            
            return ExpansionOption(
                region_id=region_id,
                priority_score=priority_score,
                expansion_cost=expansion_cost,
                expected_profit=risk_adjusted_profit,
                risk_level=risk_level,
                competition_level=competition_level,
                strategic_value=strategic_value,
                reasoning=f"Strategic expansion with {priority_score:.2f} priority score"
            )
            
        except Exception as e:
            logger.error(f"Error evaluating region {region_id}: {e}")
            return None
    
    def _calculate_strategic_value(self, guild: MerchantGuildEntity, region_id: str) -> float:
        """Calculate strategic value of a region for the guild."""
        strategic_value = 0.5  # Base value
        
        # Bonus for adjacent territories
        current_territories = guild.territory_control or []
        adjacent_bonus = 0.2 if any(self._are_regions_adjacent(region_id, t) for t in current_territories) else 0
        
        # Bonus for trade route connections
        trade_route_bonus = 0.1 if self._has_trade_route_potential(region_id) else 0
        
        # Bonus for resource availability
        resource_bonus = random.uniform(0, 0.3)  # Simplified
        
        return min(1.0, strategic_value + adjacent_bonus + trade_route_bonus + resource_bonus)
    
    def _are_regions_adjacent(self, region1: str, region2: str) -> bool:
        """Check if two regions are adjacent (simplified)."""
        # Simplified adjacency check
        try:
            id1 = int(region1.split('_')[1])
            id2 = int(region2.split('_')[1])
            return abs(id1 - id2) <= 2
        except:
            return False
    
    def _has_trade_route_potential(self, region_id: str) -> bool:
        """Check if region has trade route potential (simplified)."""
        return random.random() > 0.5
    
    def plan_pricing_strategy(self, guild_id: UUID) -> Dict[str, Any]:
        """
        Plan pricing strategy for a guild based on market conditions and personality.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            Pricing strategy plan
        """
        try:
            guild = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.id == guild_id
            ).first()
            
            if not guild:
                return {"error": "Guild not found"}
            
            personality = self.get_guild_personality(guild)
            personality_config = self.guild_ai_config["personality_traits"][personality.value]
            
            # Determine pricing strategy based on personality and market position
            strategy = self._determine_pricing_strategy(guild, personality_config)
            
            # Calculate pricing adjustments for controlled markets
            pricing_adjustments = {}
            for market_id in (guild.controlled_markets or []):
                adjustment = self._calculate_market_pricing_adjustment(
                    guild, market_id, strategy, personality_config
                )
                pricing_adjustments[market_id] = adjustment
            
            return {
                "guild_id": str(guild_id),
                "strategy": strategy.value,
                "personality": personality.value,
                "pricing_adjustments": pricing_adjustments,
                "coordination_level": guild.coordination_level,
                "expected_impact": self._estimate_pricing_impact(guild, strategy),
                "implementation_timeline": "immediate"
            }
            
        except Exception as e:
            logger.error(f"Error planning pricing strategy: {e}")
            return {"error": str(e)}
    
    def _determine_pricing_strategy(self, guild: MerchantGuildEntity, 
                                  personality_config: Dict[str, float]) -> PricingStrategy:
        """Determine optimal pricing strategy for guild."""
        market_share = guild.market_share
        pricing_influence = guild.pricing_influence
        competition_aggression = personality_config["competition_aggression"]
        cooperation_willingness = personality_config["cooperation_willingness"]
        
        # High market share + high aggression = Price leadership
        if market_share > 0.6 and competition_aggression > 0.7:
            return PricingStrategy.PRICE_LEADERSHIP
        
        # High cooperation = Cooperative pricing
        elif cooperation_willingness > 0.7:
            return PricingStrategy.COOPERATIVE_PRICING
        
        # High aggression + low market share = Predatory pricing
        elif competition_aggression > 0.6 and market_share < 0.3:
            return PricingStrategy.PREDATORY_PRICING
        
        # High pricing influence = Premium pricing
        elif pricing_influence > 0.7:
            return PricingStrategy.PREMIUM_PRICING
        
        # Default to competitive pricing
        else:
            return PricingStrategy.COMPETITIVE_PRICING
    
    def _calculate_market_pricing_adjustment(self, guild: MerchantGuildEntity, 
                                           market_id: str, strategy: PricingStrategy,
                                           personality_config: Dict[str, float]) -> Dict[str, Any]:
        """Calculate pricing adjustment for a specific market."""
        base_adjustment = 1.0
        
        if strategy == PricingStrategy.PRICE_LEADERSHIP:
            base_adjustment = 1.1  # 10% premium
        elif strategy == PricingStrategy.PREDATORY_PRICING:
            base_adjustment = 0.85  # 15% discount
        elif strategy == PricingStrategy.PREMIUM_PRICING:
            base_adjustment = 1.15  # 15% premium
        elif strategy == PricingStrategy.COOPERATIVE_PRICING:
            base_adjustment = 1.02  # 2% premium
        else:  # Competitive pricing
            base_adjustment = 0.98  # 2% discount
        
        return {
            "price_multiplier": base_adjustment,
            "strategy": strategy.value,
            "confidence": personality_config["profit_priority"],
            "market_id": market_id
        }
    
    def _estimate_pricing_impact(self, guild: MerchantGuildEntity, 
                               strategy: PricingStrategy) -> Dict[str, float]:
        """Estimate the impact of pricing strategy."""
        base_revenue_change = 0.0
        base_market_share_change = 0.0
        
        if strategy == PricingStrategy.PRICE_LEADERSHIP:
            base_revenue_change = 0.08
            base_market_share_change = 0.02
        elif strategy == PricingStrategy.PREDATORY_PRICING:
            base_revenue_change = -0.05
            base_market_share_change = 0.15
        elif strategy == PricingStrategy.PREMIUM_PRICING:
            base_revenue_change = 0.12
            base_market_share_change = -0.03
        elif strategy == PricingStrategy.COOPERATIVE_PRICING:
            base_revenue_change = 0.03
            base_market_share_change = 0.01
        else:  # Competitive pricing
            base_revenue_change = 0.01
            base_market_share_change = 0.05
        
        return {
            "revenue_change": base_revenue_change,
            "market_share_change": base_market_share_change,
            "risk_level": abs(base_revenue_change) + abs(base_market_share_change)
        }
    
    def assess_competition_threats(self, guild_id: UUID) -> List[CompetitionThreat]:
        """
        Assess competitive threats facing a guild.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            List of identified threats
        """
        try:
            guild = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.id == guild_id
            ).first()
            
            if not guild:
                return []
            
            threats = []
            
            # Check for rival guild activities
            rival_threats = self._assess_rival_guild_threats(guild)
            threats.extend(rival_threats)
            
            # Check for market competition
            market_threats = self._assess_market_competition_threats(guild)
            threats.extend(market_threats)
            
            # Check for economic cycle threats
            economic_threats = self._assess_economic_cycle_threats(guild)
            threats.extend(economic_threats)
            
            # Sort by severity
            threats.sort(key=lambda x: x.severity, reverse=True)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error assessing competition threats: {e}")
            return []
    
    def _assess_rival_guild_threats(self, guild: MerchantGuildEntity) -> List[CompetitionThreat]:
        """Assess threats from rival guilds."""
        threats = []
        
        for rival_id in (guild.rival_guilds or []):
            try:
                rival = self.db_session.query(MerchantGuildEntity).filter(
                    MerchantGuildEntity.id == rival_id
                ).first()
                
                if not rival:
                    continue
                
                # Check for territorial overlap
                guild_territories = set(guild.territory_control or [])
                rival_territories = set(rival.territory_control or [])
                overlap = guild_territories.intersection(rival_territories)
                
                if overlap:
                    severity = min(0.9, len(overlap) * 0.3 + (rival.total_wealth / guild.total_wealth) * 0.4)
                    
                    threats.append(CompetitionThreat(
                        threat_id=f"rival_{rival_id}",
                        threat_type="territorial_competition",
                        severity=severity,
                        source_guild_id=rival.id,
                        affected_regions=list(overlap),
                        recommended_response="defensive_pricing" if severity < 0.6 else "aggressive_expansion",
                        urgency=severity * 0.8
                    ))
                    
            except Exception as e:
                logger.warning(f"Error assessing rival {rival_id}: {e}")
        
        return threats
    
    def _assess_market_competition_threats(self, guild: MerchantGuildEntity) -> List[CompetitionThreat]:
        """Assess threats from market competition."""
        threats = []
        
        # Simplified market competition assessment
        for market_id in (guild.controlled_markets or []):
            competition_level = random.uniform(0.3, 0.8)
            
            if competition_level > 0.6:
                threats.append(CompetitionThreat(
                    threat_id=f"market_{market_id}",
                    threat_type="market_competition",
                    severity=competition_level,
                    source_guild_id=None,
                    affected_regions=[market_id],
                    recommended_response="price_adjustment",
                    urgency=competition_level * 0.6
                ))
        
        return threats
    
    def _assess_economic_cycle_threats(self, guild: MerchantGuildEntity) -> List[CompetitionThreat]:
        """Assess threats from economic cycles."""
        threats = []
        
        # Check economic cycles in guild territories
        for region_id in (guild.territory_control or []):
            # Simplified economic cycle check
            cycle_risk = random.uniform(0.1, 0.7)
            
            if cycle_risk > 0.5:
                threats.append(CompetitionThreat(
                    threat_id=f"economic_{region_id}",
                    threat_type="economic_downturn",
                    severity=cycle_risk,
                    source_guild_id=None,
                    affected_regions=[region_id],
                    recommended_response="diversification",
                    urgency=cycle_risk * 0.4
                ))
        
        return threats
    
    def propose_alliances(self, guild_id: UUID) -> List[AllianceProposal]:
        """
        Propose potential alliances for a guild.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            List of alliance proposals
        """
        try:
            guild = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.id == guild_id
            ).first()
            
            if not guild:
                return []
            
            personality = self.get_guild_personality(guild)
            personality_config = self.guild_ai_config["personality_traits"][personality.value]
            
            # Don't propose alliances if guild is not cooperative
            if personality_config["cooperation_willingness"] < 0.4:
                return []
            
            # Get potential alliance targets
            potential_allies = self._get_potential_alliance_targets(guild)
            
            proposals = []
            for ally in potential_allies:
                proposal = self._evaluate_alliance_potential(guild, ally, personality_config)
                if proposal:
                    proposals.append(proposal)
            
            # Sort by mutual benefit score
            proposals.sort(key=lambda x: x.mutual_benefit_score, reverse=True)
            
            # Limit to max alliances
            max_alliances = self.guild_ai_config["alliance_criteria"]["max_alliances"]
            current_alliances = len(guild.allied_guilds or [])
            available_slots = max_alliances - current_alliances
            
            return proposals[:available_slots]
            
        except Exception as e:
            logger.error(f"Error proposing alliances: {e}")
            return []
    
    def _get_potential_alliance_targets(self, guild: MerchantGuildEntity) -> List[MerchantGuildEntity]:
        """Get potential alliance targets for a guild."""
        # Get other active guilds that are not rivals or already allied
        current_allies = set(str(aid) for aid in (guild.allied_guilds or []))
        current_rivals = set(str(rid) for rid in (guild.rival_guilds or []))
        
        potential_allies = self.db_session.query(MerchantGuildEntity).filter(
            MerchantGuildEntity.id != guild.id,
            MerchantGuildEntity.is_active == True
        ).all()
        
        return [
            ally for ally in potential_allies 
            if (str(ally.id) not in current_allies and 
                str(ally.id) not in current_rivals)
        ]
    
    def _evaluate_alliance_potential(self, guild: MerchantGuildEntity, 
                                   potential_ally: MerchantGuildEntity,
                                   personality_config: Dict[str, float]) -> Optional[AllianceProposal]:
        """Evaluate potential alliance with another guild."""
        try:
            # Calculate mutual benefit
            mutual_benefit = self._calculate_mutual_benefit(guild, potential_ally)
            
            # Calculate trust level (simplified)
            trust_level = random.uniform(0.3, 0.9)
            
            # Calculate strategic alignment
            strategic_alignment = self._calculate_strategic_alignment(guild, potential_ally)
            
            # Check minimum criteria
            min_trust = self.guild_ai_config["alliance_criteria"]["min_trust_level"]
            min_benefit = self.guild_ai_config["alliance_criteria"]["min_mutual_benefit"]
            
            if trust_level < min_trust or mutual_benefit < min_benefit:
                return None
            
            # Determine alliance type
            alliance_type = self._determine_alliance_type(guild, potential_ally)
            
            # Calculate success probability
            success_probability = (
                trust_level * 0.4 +
                mutual_benefit * 0.3 +
                strategic_alignment * 0.2 +
                personality_config["cooperation_willingness"] * 0.1
            )
            
            # Propose terms
            proposed_terms = self._propose_alliance_terms(guild, potential_ally, alliance_type)
            
            return AllianceProposal(
                target_guild_id=potential_ally.id,
                alliance_type=alliance_type,
                mutual_benefit_score=mutual_benefit,
                trust_level=trust_level,
                strategic_alignment=strategic_alignment,
                proposed_terms=proposed_terms,
                success_probability=success_probability
            )
            
        except Exception as e:
            logger.error(f"Error evaluating alliance potential: {e}")
            return None
    
    def _calculate_mutual_benefit(self, guild1: MerchantGuildEntity, 
                                guild2: MerchantGuildEntity) -> float:
        """Calculate mutual benefit score for potential alliance."""
        # Territory complementarity
        territories1 = set(guild1.territory_control or [])
        territories2 = set(guild2.territory_control or [])
        overlap = len(territories1.intersection(territories2))
        complementarity = len(territories1.union(territories2)) - overlap
        
        # Wealth balance
        wealth_ratio = min(guild1.total_wealth, guild2.total_wealth) / max(guild1.total_wealth, guild2.total_wealth)
        
        # Market share synergy
        combined_market_share = guild1.market_share + guild2.market_share
        
        benefit_score = (
            (complementarity / 10) * 0.4 +  # Territory synergy
            wealth_ratio * 0.3 +  # Balanced partnership
            min(1.0, combined_market_share) * 0.3  # Market power
        )
        
        return min(1.0, benefit_score)
    
    def _calculate_strategic_alignment(self, guild1: MerchantGuildEntity, 
                                     guild2: MerchantGuildEntity) -> float:
        """Calculate strategic alignment between guilds."""
        # Similar coordination levels indicate compatible operations
        coord_similarity = 1.0 - abs(guild1.coordination_level - guild2.coordination_level)
        
        # Similar market influence indicates compatible strategies
        influence_similarity = 1.0 - abs(guild1.pricing_influence - guild2.pricing_influence)
        
        # Faction alignment (if both have factions)
        faction_alignment = 0.5  # Default neutral
        if guild1.faction_id and guild2.faction_id:
            faction_alignment = 0.8 if guild1.faction_id == guild2.faction_id else 0.2
        
        return (coord_similarity * 0.4 + influence_similarity * 0.3 + faction_alignment * 0.3)
    
    def _determine_alliance_type(self, guild1: MerchantGuildEntity, 
                               guild2: MerchantGuildEntity) -> str:
        """Determine the type of alliance to propose."""
        combined_wealth = guild1.total_wealth + guild2.total_wealth
        combined_influence = guild1.pricing_influence + guild2.pricing_influence
        
        if combined_wealth > 20000 and combined_influence > 1.2:
            return "strategic_partnership"
        elif len(set(guild1.territory_control or []).intersection(set(guild2.territory_control or []))) > 0:
            return "territorial_cooperation"
        else:
            return "trade_agreement"
    
    def _propose_alliance_terms(self, guild1: MerchantGuildEntity, 
                              guild2: MerchantGuildEntity, alliance_type: str) -> Dict[str, Any]:
        """Propose specific terms for the alliance."""
        base_terms = {
            "alliance_type": alliance_type,
            "duration": "indefinite",
            "mutual_defense": False,
            "profit_sharing": 0.0,
            "territory_sharing": False,
            "information_sharing": True
        }
        
        if alliance_type == "strategic_partnership":
            base_terms.update({
                "mutual_defense": True,
                "profit_sharing": 0.1,
                "territory_sharing": True,
                "coordinated_pricing": True
            })
        elif alliance_type == "territorial_cooperation":
            base_terms.update({
                "territory_sharing": True,
                "coordinated_pricing": True,
                "resource_sharing": True
            })
        elif alliance_type == "trade_agreement":
            base_terms.update({
                "trade_route_sharing": True,
                "preferential_pricing": True
            })
        
        return base_terms
    
    def execute_market_manipulation(self, guild_id: UUID) -> ManipulationPlan:
        """
        Plan and execute market manipulation strategies.
        
        Args:
            guild_id: ID of the guild
            
        Returns:
            Market manipulation plan
        """
        try:
            guild = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.id == guild_id
            ).first()
            
            if not guild:
                raise ValueError("Guild not found")
            
            personality = self.get_guild_personality(guild)
            personality_config = self.guild_ai_config["personality_traits"][personality.value]
            
            # Only aggressive and innovative guilds engage in manipulation
            if personality not in [GuildPersonality.AGGRESSIVE, GuildPersonality.INNOVATIVE]:
                return ManipulationPlan(
                    manipulation_type="none",
                    target_markets=[],
                    target_resources=[],
                    expected_impact=0.0,
                    execution_cost=0.0,
                    risk_level=0.0,
                    timeline=0,
                    success_probability=0.0
                )
            
            # Determine manipulation strategy
            manipulation_type = self._determine_manipulation_strategy(guild, personality_config)
            
            # Select target markets and resources
            target_markets = self._select_manipulation_targets(guild, manipulation_type)
            target_resources = self._select_target_resources(guild, target_markets)
            
            # Calculate costs and risks
            execution_cost = self._calculate_manipulation_cost(guild, manipulation_type, target_markets)
            risk_level = self._calculate_manipulation_risk(guild, manipulation_type)
            expected_impact = self._estimate_manipulation_impact(guild, manipulation_type)
            success_probability = self._calculate_manipulation_success_probability(
                guild, manipulation_type, risk_level
            )
            
            # Determine timeline
            timeline = self._determine_manipulation_timeline(manipulation_type)
            
            return ManipulationPlan(
                manipulation_type=manipulation_type,
                target_markets=target_markets,
                target_resources=target_resources,
                expected_impact=expected_impact,
                execution_cost=execution_cost,
                risk_level=risk_level,
                timeline=timeline,
                success_probability=success_probability
            )
            
        except Exception as e:
            logger.error(f"Error executing market manipulation: {e}")
            return ManipulationPlan(
                manipulation_type="error",
                target_markets=[],
                target_resources=[],
                expected_impact=0.0,
                execution_cost=0.0,
                risk_level=1.0,
                timeline=0,
                success_probability=0.0
            )
    
    def _determine_manipulation_strategy(self, guild: MerchantGuildEntity, 
                                       personality_config: Dict[str, float]) -> str:
        """Determine the type of market manipulation to employ."""
        market_share = guild.market_share
        pricing_influence = guild.pricing_influence
        aggression = personality_config["competition_aggression"]
        
        if market_share > 0.6 and pricing_influence > 0.7:
            return "price_fixing"
        elif aggression > 0.8 and guild.total_wealth > 10000:
            return "supply_cornering"
        elif len(guild.controlled_markets or []) > 3:
            return "cross_market_coordination"
        else:
            return "competitive_undercutting"
    
    def _select_manipulation_targets(self, guild: MerchantGuildEntity, 
                                   manipulation_type: str) -> List[str]:
        """Select target markets for manipulation."""
        controlled_markets = guild.controlled_markets or []
        
        if manipulation_type == "price_fixing":
            return controlled_markets[:3]  # Focus on top markets
        elif manipulation_type == "supply_cornering":
            return controlled_markets[:1]  # Focus on one market
        elif manipulation_type == "cross_market_coordination":
            return controlled_markets  # All controlled markets
        else:
            return controlled_markets[:2]  # Limited scope
    
    def _select_target_resources(self, guild: MerchantGuildEntity, 
                               target_markets: List[str]) -> List[str]:
        """Select target resources for manipulation."""
        # Simplified resource selection
        common_resources = ["iron", "gold", "food", "wood", "stone"]
        return random.sample(common_resources, min(3, len(common_resources)))
    
    def _calculate_manipulation_cost(self, guild: MerchantGuildEntity, 
                                   manipulation_type: str, target_markets: List[str]) -> float:
        """Calculate the cost of executing manipulation strategy."""
        base_cost = guild.total_wealth * 0.1  # 10% of wealth as base
        
        market_multiplier = len(target_markets) * 0.5
        
        type_multipliers = {
            "price_fixing": 1.2,
            "supply_cornering": 2.0,
            "cross_market_coordination": 1.5,
            "competitive_undercutting": 0.8
        }
        
        type_multiplier = type_multipliers.get(manipulation_type, 1.0)
        
        return base_cost * market_multiplier * type_multiplier
    
    def _calculate_manipulation_risk(self, guild: MerchantGuildEntity, 
                                   manipulation_type: str) -> float:
        """Calculate the risk level of manipulation strategy."""
        base_risk = 0.3
        
        type_risks = {
            "price_fixing": 0.7,
            "supply_cornering": 0.8,
            "cross_market_coordination": 0.5,
            "competitive_undercutting": 0.3
        }
        
        type_risk = type_risks.get(manipulation_type, 0.5)
        
        # Higher market share = higher risk of detection
        market_share_risk = guild.market_share * 0.3
        
        return min(1.0, base_risk + type_risk + market_share_risk)
    
    def _estimate_manipulation_impact(self, guild: MerchantGuildEntity, 
                                    manipulation_type: str) -> float:
        """Estimate the expected impact of manipulation strategy."""
        base_impact = guild.pricing_influence * 0.5
        
        type_impacts = {
            "price_fixing": 0.8,
            "supply_cornering": 0.9,
            "cross_market_coordination": 0.6,
            "competitive_undercutting": 0.4
        }
        
        type_impact = type_impacts.get(manipulation_type, 0.5)
        
        return min(1.0, base_impact + type_impact)
    
    def _calculate_manipulation_success_probability(self, guild: MerchantGuildEntity, 
                                                  manipulation_type: str, risk_level: float) -> float:
        """Calculate probability of successful manipulation."""
        base_probability = guild.coordination_level * 0.6
        
        # Higher risk = lower success probability
        risk_penalty = risk_level * 0.4
        
        # Market influence bonus
        influence_bonus = guild.pricing_influence * 0.3
        
        return max(0.1, min(0.9, base_probability - risk_penalty + influence_bonus))
    
    def _determine_manipulation_timeline(self, manipulation_type: str) -> int:
        """Determine timeline for manipulation execution in days."""
        timelines = {
            "price_fixing": 7,
            "supply_cornering": 14,
            "cross_market_coordination": 21,
            "competitive_undercutting": 3
        }
        
        return timelines.get(manipulation_type, 7)
    
    def process_guild_ai_tick(self, guild_id: UUID) -> Dict[str, Any]:
        """
        Process AI decision-making for a guild during a game tick.
        
        Args:
            guild_id: ID of the guild to process
            
        Returns:
            Results of AI processing
        """
        try:
            guild = self.db_session.query(MerchantGuildEntity).filter(
                MerchantGuildEntity.id == guild_id
            ).first()
            
            if not guild or not guild.is_active:
                return {"error": "Guild not found or inactive"}
            
            results = {
                "guild_id": str(guild_id),
                "actions_taken": [],
                "decisions_made": [],
                "status_changes": {}
            }
            
            personality = self.get_guild_personality(guild)
            personality_config = self.guild_ai_config["personality_traits"][personality.value]
            
            # 1. Evaluate expansion opportunities
            if random.random() < personality_config["expansion_rate"]:
                expansion_options = self.evaluate_expansion_opportunities(guild_id)
                if expansion_options:
                    best_option = expansion_options[0]
                    if best_option.expansion_cost <= guild.total_wealth * 0.6:
                        # Execute expansion
                        self._execute_expansion(guild, best_option)
                        results["actions_taken"].append(f"Expanded to {best_option.region_id}")
            
            # 2. Update pricing strategy
            pricing_strategy = self.plan_pricing_strategy(guild_id)
            if "error" not in pricing_strategy:
                results["decisions_made"].append(f"Updated pricing strategy: {pricing_strategy['strategy']}")
            
            # 3. Assess threats and respond
            threats = self.assess_competition_threats(guild_id)
            if threats:
                high_priority_threats = [t for t in threats if t.severity > 0.7]
                for threat in high_priority_threats[:2]:  # Handle top 2 threats
                    response = self._respond_to_threat(guild, threat)
                    results["actions_taken"].append(f"Responded to {threat.threat_type}: {response}")
            
            # 4. Consider alliances (less frequent)
            if random.random() < personality_config["cooperation_willingness"] * 0.3:
                alliance_proposals = self.propose_alliances(guild_id)
                if alliance_proposals:
                    best_proposal = alliance_proposals[0]
                    if best_proposal.success_probability > 0.7:
                        # Attempt alliance
                        success = self._attempt_alliance(guild, best_proposal)
                        if success:
                            results["actions_taken"].append(f"Formed alliance with guild {best_proposal.target_guild_id}")
            
            # 5. Market manipulation (aggressive guilds only)
            if (personality == GuildPersonality.AGGRESSIVE and 
                random.random() < 0.2):  # 20% chance for aggressive guilds
                manipulation_plan = self.execute_market_manipulation(guild_id)
                if manipulation_plan.manipulation_type != "none":
                    results["actions_taken"].append(f"Initiated {manipulation_plan.manipulation_type}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing guild AI tick: {e}")
            return {"error": str(e)}
    
    def _execute_expansion(self, guild: MerchantGuildEntity, expansion_option: ExpansionOption):
        """Execute guild expansion to a new region."""
        try:
            # Add region to territory control
            territory = guild.territory_control or []
            if expansion_option.region_id not in territory:
                territory.append(expansion_option.region_id)
                guild.territory_control = territory
                
                # Deduct expansion cost
                guild.total_wealth -= expansion_option.expansion_cost
                
                # Update market share and influence
                guild.market_share = min(1.0, guild.market_share + 0.05)
                guild.pricing_influence = min(1.0, guild.pricing_influence + 0.03)
                
                self.db_session.commit()
                logger.info(f"Guild {guild.name} expanded to {expansion_option.region_id}")
                
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error executing expansion: {e}")
    
    def _respond_to_threat(self, guild: MerchantGuildEntity, threat: CompetitionThreat) -> str:
        """Respond to a competitive threat."""
        try:
            if threat.recommended_response == "defensive_pricing":
                # Adjust pricing to be more competitive
                guild.pricing_influence = max(0.1, guild.pricing_influence - 0.1)
                response = "Implemented defensive pricing"
                
            elif threat.recommended_response == "aggressive_expansion":
                # Increase market presence
                guild.market_share = min(1.0, guild.market_share + 0.05)
                response = "Increased market presence"
                
            elif threat.recommended_response == "price_adjustment":
                # Moderate pricing adjustment
                guild.pricing_influence = max(0.1, guild.pricing_influence - 0.05)
                response = "Adjusted pricing strategy"
                
            elif threat.recommended_response == "diversification":
                # Improve coordination to handle economic uncertainty
                guild.coordination_level = min(1.0, guild.coordination_level + 0.05)
                response = "Improved operational coordination"
                
            else:
                response = "Monitored situation"
            
            self.db_session.commit()
            return response
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error responding to threat: {e}")
            return "Failed to respond"
    
    def _attempt_alliance(self, guild: MerchantGuildEntity, proposal: AllianceProposal) -> bool:
        """Attempt to form an alliance with another guild."""
        try:
            # Simplified alliance formation
            if random.random() < proposal.success_probability:
                # Add to allied guilds
                allied_guilds = guild.allied_guilds or []
                if proposal.target_guild_id not in allied_guilds:
                    allied_guilds.append(proposal.target_guild_id)
                    guild.allied_guilds = allied_guilds
                    
                    # Update coordination level
                    guild.coordination_level = min(1.0, guild.coordination_level + 0.1)
                    
                    self.db_session.commit()
                    return True
            
            return False
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error attempting alliance: {e}")
            return False 