"""
Advanced Economy Service - Enhanced economic features

This service manages complex economic systems including dynamic pricing,
merchant guilds, economic competition, and economic cycles.
"""

import random
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc
from enum import Enum

# Infrastructure layer - SQLAlchemy models for database operations
from backend.infrastructure.database.economy.advanced_models import (
    DynamicPricing,
    MerchantGuildEntity, 
    EconomicCompetition,
    EconomicCycle
)
from backend.infrastructure.database.economy.trade_route_models import TradeRoute

# Business layer - Pydantic models and enums for business logic
from backend.systems.economy.models.advanced_economy import (
    PriceModifierType, EconomicCyclePhase, CompetitionType,
    MerchantGuildModel, DynamicPricingModel, EconomicCompetitionModel, EconomicCycleModel
)

# Remove cross-system dependency - use interface instead
# from backend.systems.region.models import DangerLevel, Region as RegionEntity, RegionPOI, POIType

from backend.infrastructure.events import EventDispatcher
from backend.infrastructure.utils import ServiceError
from backend.infrastructure.config_loaders.economy_config_loader import get_economy_config
from backend.systems.economy.services.integration_interfaces import get_integration_manager

logger = logging.getLogger(__name__)

# Define local enums to avoid cross-system dependencies
class DangerLevel(Enum):
    """Local definition to avoid cross-system dependency"""
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5

class POIType(Enum):
    """Local definition to avoid cross-system dependency"""
    ROAD = "road"
    WATERWAY = "waterway"
    MARKET = "market"
    GUILD_HALL = "guild_hall"

class AdvancedEconomyService:
    """Service for managing advanced economy features"""
    
    def __init__(self, db_session: Session, event_dispatcher: Optional[EventDispatcher] = None):
        self.db = db_session
        self.event_dispatcher = event_dispatcher
    
    # =========================================================================
    # DYNAMIC PRICING SYSTEM
    # =========================================================================
    
    def calculate_dynamic_price(self, region_id: str, resource_id: UUID, 
                              base_price: float) -> Tuple[float, Dict[str, Any]]:
        """Calculate dynamic price based on various factors"""
        try:
            # Get or create dynamic pricing record
            pricing_record = self.db.query(DynamicPricing).filter(
                and_(
                    DynamicPricing.region_id == region_id,
                    DynamicPricing.resource_id == resource_id,
                    DynamicPricing.is_active == True
                )
            ).first()
            
            if not pricing_record:
                pricing_record = DynamicPricing(
                    region_id=region_id,
                    resource_id=resource_id,
                    base_price=base_price,
                    current_price=base_price
                )
                self.db.add(pricing_record)
            
            # Calculate all modifiers
            modifiers = self._calculate_price_modifiers(region_id, resource_id)
            
            # Apply modifiers to pricing record
            pricing_record.danger_level_modifier = modifiers.get("danger_level", 1.0)
            pricing_record.trade_route_modifier = modifiers.get("trade_route", 1.0)
            pricing_record.infrastructure_modifier = modifiers.get("infrastructure", 1.0)
            pricing_record.guild_modifier = modifiers.get("guild", 1.0)
            pricing_record.competition_modifier = modifiers.get("competition", 1.0)
            pricing_record.cycle_modifier = modifiers.get("cycle", 1.0)
            pricing_record.active_modifiers = modifiers
            pricing_record.last_calculated = datetime.utcnow()
            pricing_record.calculation_source = "dynamic_calculation"
            
            # Calculate final price
            final_price = pricing_record.calculate_final_price()
            pricing_record.current_price = final_price
            
            self.db.commit()
            
            return final_price, modifiers
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error calculating dynamic price: {str(e)}")
            raise ServiceError(f"Failed to calculate dynamic price: {str(e)}")
    
    def _calculate_price_modifiers(self, region_id: str, resource_id: UUID) -> Dict[str, float]:
        """Calculate all price modifiers for a region and resource"""
        modifiers = {}
        
        # Danger level modifier
        modifiers["danger_level"] = self._get_danger_level_modifier(region_id)
        
        # Trade route safety modifier
        modifiers["trade_route"] = self._get_trade_route_modifier(region_id)
        
        # Infrastructure modifier (roads, waterways)
        modifiers["infrastructure"] = self._get_infrastructure_modifier(region_id)
        
        # Guild control modifier
        modifiers["guild"] = self._get_guild_control_modifier(region_id)
        
        # Competition modifier
        modifiers["competition"] = self._get_competition_modifier(region_id, resource_id)
        
        # Economic cycle modifier
        modifiers["cycle"] = self._get_economic_cycle_modifier(region_id)
        
        return modifiers
    
    def _get_danger_level_modifier(self, region_id: str) -> float:
        """Get price modifier based on region danger level"""
        try:
            # Use integration interface to get region data
            integration_manager = get_integration_manager()
            region_interface = integration_manager.get_region_interface()
            
            # Get region data through interface (no direct dependency)
            region_data = region_interface.get_region_data(region_id)
            
            if region_data and 'danger_level' in region_data:
                danger_level = region_data['danger_level']
            else:
                # Default to moderate danger if region not found
                danger_level = DangerLevel.MODERATE.value
                logger.warning(f"Region {region_id} not found, using default danger level")
            
            # Get danger level modifiers from configuration
            config = get_economy_config()
            danger_modifiers = config.get_danger_level_modifiers()
            
            modifier = danger_modifiers.get(str(danger_level), 1.0)
            logger.debug(f"Region {region_id} danger level {danger_level} -> price modifier {modifier}")
            return modifier
            
        except Exception as e:
            logger.warning(f"Error getting danger level modifier for region {region_id}: {str(e)}")
            return 1.0
    
    def _get_trade_route_modifier(self, region_id: str) -> float:
        """Get price modifier based on trade route safety"""
        try:
            # Get configuration for trade route calculations
            config = get_economy_config()
            trade_config = config.get_trade_route_config()
            
            # Query trade routes connected to this region
            trade_routes = self.db.query(TradeRoute).filter(
                or_(
                    TradeRoute.origin_region_id == region_id,
                    TradeRoute.destination_region_id == region_id
                )
            ).filter(
                TradeRoute.is_active == True
            ).all()
            
            if not trade_routes:
                # No trade routes = higher prices due to isolation
                isolation_penalty = trade_config.get("isolation_penalty", 1.3)
                logger.debug(f"No trade routes found for region {region_id}, applying isolation penalty")
                return isolation_penalty
            
            # Calculate average safety from route metadata
            total_safety = 0.0
            total_routes = 0
            
            for route in trade_routes:
                route_metadata = route.route_metadata or {}
                
                # Check for safety rating in metadata
                if 'safety_rating' in route_metadata:
                    safety = route_metadata['safety_rating']
                elif 'danger_level' in route_metadata:
                    # Convert danger level to safety (inverse)
                    danger = route_metadata['danger_level']
                    safety = max(0.1, 1.0 - (danger / 10))
                else:
                    # Default to moderate safety if no data
                    safety = 0.5
                
                total_safety += safety
                total_routes += 1
            
            if total_routes > 0:
                avg_safety = total_safety / total_routes
                
                # Convert safety to price modifier using configuration
                base_modifier = trade_config.get("base_modifier", 1.6)
                safety_reduction = trade_config.get("safety_reduction", 0.9)
                modifier = base_modifier - (avg_safety * safety_reduction)
                
                # Apply min/max bounds from configuration
                min_modifier = trade_config.get("minimum_modifier", 0.7)
                max_modifier = trade_config.get("maximum_modifier", 1.6)
                modifier = max(min_modifier, min(modifier, max_modifier))
                
                logger.debug(f"Region {region_id} average trade route safety {avg_safety:.2f} -> price modifier {modifier:.2f}")
                return modifier
            else:
                return 1.0
            
        except Exception as e:
            logger.warning(f"Error getting trade route modifier for region {region_id}: {str(e)}")
            return 1.0
    
    def _get_infrastructure_modifier(self, region_id: str) -> float:
        """Get price modifier based on infrastructure (roads, waterways)"""
        try:
            # Get configuration for infrastructure calculations
            config = get_economy_config()
            infra_config = config.get_infrastructure_modifiers()
            
            # Use integration interface to get POI data
            integration_manager = get_integration_manager()
            region_interface = integration_manager.get_region_interface()
            
            # Get infrastructure POI data through interface (no direct dependency)
            infrastructure_data = region_interface.get_region_infrastructure(region_id)
            
            modifier = 1.0
            has_roads = False
            has_waterways = False
            
            # Check for infrastructure based on returned data
            if infrastructure_data:
                has_roads = infrastructure_data.get('has_roads', False)
                has_waterways = infrastructure_data.get('has_waterways', False)
                
                # Check POI types if detailed data available
                poi_types = infrastructure_data.get('poi_types', [])
                for poi_type in poi_types:
                    if poi_type in ['crossroads', 'trading_post']:
                        has_roads = True
                    elif poi_type in ['bridge', 'waterway']:
                        has_waterways = True
                        has_roads = True  # Bridges often connect roads
            
            # Apply infrastructure modifiers from configuration
            if has_roads:
                modifier *= infra_config.get("roads", 0.9)
                logger.debug(f"Region {region_id} has road infrastructure")
            
            if has_waterways:
                modifier *= infra_config.get("waterways", 0.85)
                logger.debug(f"Region {region_id} has waterway infrastructure")
            
            # Bonus for having both
            if has_roads and has_waterways:
                modifier *= infra_config.get("both_bonus", 0.95)
                logger.debug(f"Region {region_id} has excellent infrastructure (roads + waterways)")
            
            # Infrastructure isolation penalty
            if not has_roads and not has_waterways:
                modifier *= infra_config.get("isolation_penalty", 1.2)
                logger.debug(f"Region {region_id} has poor infrastructure")
            
            return modifier
            
        except Exception as e:
            logger.warning(f"Error getting infrastructure modifier for region {region_id}: {str(e)}")
            return 1.0
    
    def _get_guild_control_modifier(self, region_id: str) -> float:
        """Get price modifier based on merchant guild control"""
        try:
            # Check if any merchant guilds control this region
            guild = self.db.query(MerchantGuildEntity).filter(
                and_(
                    MerchantGuildEntity.territory_control.contains([region_id]),
                    MerchantGuildEntity.is_active == True
                )
            ).first()
            
            if guild:
                # Guild control can increase or decrease prices based on their influence
                influence = guild.pricing_influence
                coordination = guild.coordination_level
                
                # High influence + coordination = price manipulation
                modifier = 1.0 + (influence * coordination * 0.3)  # Up to 30% increase
                return modifier
            
            return 1.0
            
        except Exception as e:
            logger.warning(f"Error getting guild control modifier: {str(e)}")
            return 1.0
    
    def _get_competition_modifier(self, region_id: str, resource_id: UUID) -> float:
        """Get price modifier based on economic competition"""
        try:
            # Check for active competition affecting this resource
            competition_count = self.db.query(EconomicCompetition).filter(
                and_(
                    EconomicCompetition.region_id == region_id,
                    EconomicCompetition.resource_targeted == str(resource_id),
                    EconomicCompetition.status.in_(["pending", "in_progress"]),
                    EconomicCompetition.is_active == True
                )
            ).count()
            
            if competition_count > 0:
                # More competition = lower prices
                modifier = 1.0 - (competition_count * 0.1)
                return max(modifier, 0.5)  # Minimum 50% of base price
            
            return 1.0
            
        except Exception as e:
            logger.warning(f"Error getting competition modifier: {str(e)}")
            return 1.0
    
    def _get_economic_cycle_modifier(self, region_id: str) -> float:
        """Get price modifier based on current economic cycle"""
        try:
            # Get active economic cycle for the region
            cycle = self.db.query(EconomicCycle).filter(
                and_(
                    EconomicCycle.region_id == region_id,
                    EconomicCycle.is_active == True
                )
            ).first()
            
            if cycle:
                return cycle.get_cycle_modifier()
            
            return 1.0  # Stable economy default
            
        except Exception as e:
            logger.warning(f"Error getting economic cycle modifier: {str(e)}")
            return 1.0
    
    # =========================================================================
    # MERCHANT GUILD SYSTEM
    # =========================================================================
    
    def create_merchant_guild(self, name: str, description: Optional[str] = None,
                            faction_id: Optional[UUID] = None, 
                            headquarters_region_id: Optional[str] = None,
                            initial_wealth: float = 1000.0) -> MerchantGuildEntity:
        """Create a new merchant guild"""
        try:
            guild = MerchantGuildEntity(
                name=name,
                description=description,
                faction_id=faction_id,
                headquarters_region_id=headquarters_region_id,
                total_wealth=initial_wealth
            )
            
            self.db.add(guild)
            self.db.commit()
            
            logger.info(f"Created merchant guild: {name}")
            return guild
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating merchant guild: {str(e)}")
            raise ServiceError(f"Failed to create merchant guild: {str(e)}")
    
    def expand_guild_territory(self, guild_id: UUID, region_id: str) -> bool:
        """Expand merchant guild territory to a new region"""
        try:
            guild = self.db.query(MerchantGuildEntity).filter(
                and_(
                    MerchantGuildEntity.id == guild_id,
                    MerchantGuildEntity.is_active == True
                )
            ).first()
            
            if not guild:
                raise ServiceError(f"Guild {guild_id} not found")
            
            # Add region to territory control if not already controlled
            territory = guild.territory_control or []
            if region_id not in territory:
                territory.append(region_id)
                guild.territory_control = territory
                self.db.commit()
                
                logger.info(f"Guild {guild.name} expanded to region {region_id}")
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error expanding guild territory: {str(e)}")
            raise ServiceError(f"Failed to expand guild territory: {str(e)}")
    
    def coordinate_guild_pricing(self, region_id: str) -> Dict[str, Any]:
        """Coordinate pricing between merchant guilds in a region"""
        try:
            # Get all guilds operating in the region
            guilds = self.db.query(MerchantGuildEntity).filter(
                and_(
                    MerchantGuildEntity.territory_control.contains([region_id]),
                    MerchantGuildEntity.is_active == True
                )
            ).all()
            
            if len(guilds) <= 1:
                return {"coordination": False, "reason": "Insufficient guilds"}
            
            # Check for coordinated pricing (allied guilds)
            coordinated_guilds = []
            for guild in guilds:
                for other_guild in guilds:
                    if (guild.id != other_guild.id and 
                        str(other_guild.id) in (guild.allied_guilds or [])):
                        coordinated_guilds.extend([guild, other_guild])
            
            if coordinated_guilds:
                # Apply coordinated pricing effects
                coordination_bonus = len(set(coordinated_guilds)) * 0.1
                
                for guild in set(coordinated_guilds):
                    guild.pricing_influence = min(1.0, guild.pricing_influence + coordination_bonus)
                
                self.db.commit()
                
                return {
                    "coordination": True,
                    "guilds_involved": len(set(coordinated_guilds)),
                    "coordination_bonus": coordination_bonus
                }
            
            return {"coordination": False, "reason": "No allied guilds"}
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error coordinating guild pricing: {str(e)}")
            raise ServiceError(f"Failed to coordinate guild pricing: {str(e)}")
    
    # =========================================================================
    # ECONOMIC COMPETITION SYSTEM
    # =========================================================================
    
    def initiate_npc_competition(self, initiator_npc_id: UUID, region_id: str,
                               competition_type: CompetitionType, 
                               target_npc_id: Optional[UUID] = None,
                               target_poi_id: Optional[str] = None,
                               offered_amount: float = 0.0,
                               resource_targeted: Optional[str] = None) -> EconomicCompetition:
        """Initiate economic competition between NPCs"""
        try:
            # Calculate success probability based on NPC wealth and influence
            success_probability = self._calculate_competition_success_rate(
                initiator_npc_id, target_npc_id, competition_type, offered_amount
            )
            
            competition = EconomicCompetition(
                initiator_npc_id=initiator_npc_id,
                target_npc_id=target_npc_id,
                target_poi_id=target_poi_id,
                region_id=region_id,
                competition_type=competition_type.value,
                offered_amount=offered_amount,
                resource_targeted=resource_targeted,
                success_probability=success_probability,
                status="pending"
            )
            
            self.db.add(competition)
            self.db.commit()
            
            logger.info(f"Initiated {competition_type.value} competition in region {region_id}")
            return competition
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error initiating NPC competition: {str(e)}")
            raise ServiceError(f"Failed to initiate NPC competition: {str(e)}")
    
    def _calculate_competition_success_rate(self, initiator_npc_id: UUID,
                                          target_npc_id: Optional[UUID],
                                          competition_type: CompetitionType,
                                          offered_amount: float) -> float:
        """Calculate the success rate for economic competition"""
        try:
            # Base success rate by competition type
            base_rates = {
                CompetitionType.HOSTILE_TAKEOVER: 0.3,
                CompetitionType.COMMODITY_BUYOUT: 0.6,
                CompetitionType.PROPERTY_ACQUISITION: 0.5,
                CompetitionType.PRICE_UNDERCUTTING: 0.7,
                CompetitionType.MARKET_MANIPULATION: 0.4
            }
            
            base_rate = base_rates.get(competition_type, 0.5)
            
            # Get integration manager for NPC system access
            integration = get_integration_manager(self.db)
            
            # Factor in wealth disparity using actual NPC wealth
            try:
                initiator_wealth = integration.npc_interface.get_npc_wealth(initiator_npc_id)
                
                # Wealth advantage calculation
                wealth_modifier = 0.0
                if initiator_wealth > 5000:
                    wealth_modifier += 0.3  # Significant wealth advantage
                elif initiator_wealth > 2000:
                    wealth_modifier += 0.2  # Moderate wealth advantage
                elif initiator_wealth > 1000:
                    wealth_modifier += 0.1  # Small wealth advantage
                
                # If we have a target NPC, compare wealth levels
                if target_npc_id:
                    target_wealth = integration.npc_interface.get_npc_wealth(target_npc_id)
                    wealth_ratio = initiator_wealth / max(target_wealth, 100)  # Avoid division by zero
                    
                    if wealth_ratio > 3.0:
                        wealth_modifier += 0.3  # Massive wealth advantage
                    elif wealth_ratio > 2.0:
                        wealth_modifier += 0.2  # Significant wealth advantage
                    elif wealth_ratio > 1.5:
                        wealth_modifier += 0.1  # Moderate wealth advantage
                    elif wealth_ratio < 0.5:
                        wealth_modifier -= 0.2  # Wealth disadvantage
                
                # Factor in offered amount vs NPC wealth
                if offered_amount > 0:
                    offer_ratio = offered_amount / initiator_wealth
                    if offer_ratio > 0.5:  # Offering more than half their wealth
                        wealth_modifier += 0.2  # Serious commitment bonus
                    elif offer_ratio > 0.3:
                        wealth_modifier += 0.1  # Moderate commitment bonus
                
                base_rate += wealth_modifier
                
                logger.debug(f"Competition success rate: base={base_rates.get(competition_type, 0.5):.2f}, "
                           f"wealth_modifier={wealth_modifier:.2f}, final={base_rate:.2f}")
                
            except Exception as e:
                logger.warning(f"Error calculating wealth-based success rate: {e}")
                # Fall back to offered amount as proxy for wealth
                if offered_amount > 1000:
                    base_rate += 0.2
                elif offered_amount > 5000:
                    base_rate += 0.4
            
            # Ensure rate stays within bounds
            return max(0.1, min(0.9, base_rate))
            
        except Exception as e:
            logger.warning(f"Error calculating competition success rate: {str(e)}")
            return 0.5
    
    def process_competition_outcome(self, competition_id: UUID) -> Dict[str, Any]:
        """Process the outcome of an economic competition"""
        try:
            competition = self.db.query(EconomicCompetition).filter(
                and_(
                    EconomicCompetition.id == competition_id,
                    EconomicCompetition.status == "pending",
                    EconomicCompetition.is_active == True
                )
            ).first()
            
            if not competition:
                raise ServiceError(f"Competition {competition_id} not found or not pending")
            
            # Determine success based on probability
            success = random.random() < competition.success_probability
            
            competition.success = success
            competition.status = "completed" if success else "failed"
            competition.completion_date = datetime.utcnow()
            
            # Apply effects based on competition type and success
            impact_details = self._apply_competition_effects(competition, success)
            competition.impact_details = impact_details
            
            self.db.commit()
            
            logger.info(f"Processed competition {competition_id}: {'success' if success else 'failure'}")
            return {
                "competition_id": str(competition_id),
                "success": success,
                "impact": impact_details
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing competition outcome: {str(e)}")
            raise ServiceError(f"Failed to process competition outcome: {str(e)}")
    
    def _apply_competition_effects(self, competition: EconomicCompetition, 
                                 success: bool) -> Dict[str, Any]:
        """Apply the effects of economic competition"""
        effects = {
            "wealth_change": 0.0,
            "market_impact": {},
            "reputation_change": {},
            "property_transfer": None
        }
        
        if success:
            if competition.competition_type == "hostile_takeover":
                effects["property_transfer"] = competition.target_poi_id
                effects["wealth_change"] = -competition.offered_amount
                
            elif competition.competition_type == "commodity_buyout":
                effects["market_impact"] = {
                    "resource": competition.resource_targeted,
                    "price_increase": 0.2,
                    "supply_decrease": 0.3
                }
                effects["wealth_change"] = -competition.offered_amount
                
            elif competition.competition_type == "property_acquisition":
                effects["property_transfer"] = competition.target_poi_id
                effects["wealth_change"] = -competition.offered_amount
                
            competition.wealth_transferred = competition.offered_amount
        
        return effects
    
    # =========================================================================
    # ECONOMIC CYCLE SYSTEM
    # =========================================================================
    
    def create_economic_cycle(self, region_id: str, cycle_name: str,
                            initial_phase: EconomicCyclePhase = EconomicCyclePhase.STABLE,
                            trigger_events: Optional[List[str]] = None,
                            war_impact: float = 0.0) -> EconomicCycle:
        """Create a new economic cycle for a region"""
        try:
            # End any existing active cycles for the region
            existing_cycles = self.db.query(EconomicCycle).filter(
                and_(
                    EconomicCycle.region_id == region_id,
                    EconomicCycle.is_active == True
                )
            ).all()
            
            for cycle in existing_cycles:
                cycle.is_active = False
            
            # Create new cycle
            new_cycle = EconomicCycle(
                region_id=region_id,
                cycle_name=cycle_name,
                current_phase=initial_phase.value,
                trigger_events=trigger_events or [],
                war_impact=war_impact
            )
            
            self.db.add(new_cycle)
            self.db.commit()
            
            logger.info(f"Created economic cycle '{cycle_name}' for region {region_id}")
            return new_cycle
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating economic cycle: {str(e)}")
            raise ServiceError(f"Failed to create economic cycle: {str(e)}")
    
    def advance_economic_cycle(self, region_id: str) -> Optional[EconomicCycle]:
        """Advance the economic cycle to the next phase"""
        try:
            cycle = self.db.query(EconomicCycle).filter(
                and_(
                    EconomicCycle.region_id == region_id,
                    EconomicCycle.is_active == True
                )
            ).first()
            
            if not cycle:
                return None
            
            # Check if phase duration has passed
            time_since_phase = datetime.utcnow() - cycle.phase_start_date
            if time_since_phase.days < cycle.phase_duration_days:
                return cycle  # Not time to advance yet
            
            # Advance to next phase
            next_phase = self._get_next_economic_phase(
                EconomicCyclePhase(cycle.current_phase)
            )
            
            cycle.current_phase = next_phase.value
            cycle.phase_start_date = datetime.utcnow()
            cycle.phase_duration_days = self._get_phase_duration(next_phase)
            
            # Update economic indicators
            self._update_economic_indicators(cycle, next_phase)
            
            self.db.commit()
            
            logger.info(f"Advanced economic cycle in region {region_id} to {next_phase.value}")
            return cycle
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error advancing economic cycle: {str(e)}")
            raise ServiceError(f"Failed to advance economic cycle: {str(e)}")
    
    def _get_next_economic_phase(self, current_phase: EconomicCyclePhase) -> EconomicCyclePhase:
        """Get the next phase in the economic cycle"""
        phase_progression = {
            EconomicCyclePhase.STABLE: EconomicCyclePhase.GROWTH,
            EconomicCyclePhase.GROWTH: EconomicCyclePhase.BOOM,
            EconomicCyclePhase.BOOM: EconomicCyclePhase.RECESSION,
            EconomicCyclePhase.RECESSION: EconomicCyclePhase.BUST,
            EconomicCyclePhase.BUST: EconomicCyclePhase.RECOVERY,
            EconomicCyclePhase.RECOVERY: EconomicCyclePhase.STABLE
        }
        
        return phase_progression.get(current_phase, EconomicCyclePhase.STABLE)
    
    def _get_phase_duration(self, phase: EconomicCyclePhase) -> int:
        """Get the duration in days for an economic phase"""
        durations = {
            EconomicCyclePhase.STABLE: 60,
            EconomicCyclePhase.GROWTH: 45,
            EconomicCyclePhase.BOOM: 30,
            EconomicCyclePhase.RECESSION: 40,
            EconomicCyclePhase.BUST: 35,
            EconomicCyclePhase.RECOVERY: 50
        }
        
        return durations.get(phase, 30)
    
    def _update_economic_indicators(self, cycle: EconomicCycle, 
                                  new_phase: EconomicCyclePhase) -> None:
        """Update economic indicators based on the new phase"""
        phase_effects = {
            EconomicCyclePhase.STABLE: {
                "prosperity_level": 0.5,
                "inflation_rate": 0.0,
                "unemployment_rate": 0.1,
                "trade_volume": 1.0
            },
            EconomicCyclePhase.GROWTH: {
                "prosperity_level": 0.7,
                "inflation_rate": 0.1,
                "unemployment_rate": 0.08,
                "trade_volume": 1.2
            },
            EconomicCyclePhase.BOOM: {
                "prosperity_level": 0.9,
                "inflation_rate": 0.2,
                "unemployment_rate": 0.05,
                "trade_volume": 1.5
            },
            EconomicCyclePhase.RECESSION: {
                "prosperity_level": 0.3,
                "inflation_rate": -0.1,
                "unemployment_rate": 0.15,
                "trade_volume": 0.8
            },
            EconomicCyclePhase.BUST: {
                "prosperity_level": 0.1,
                "inflation_rate": -0.2,
                "unemployment_rate": 0.25,
                "trade_volume": 0.6
            },
            EconomicCyclePhase.RECOVERY: {
                "prosperity_level": 0.4,
                "inflation_rate": 0.05,
                "unemployment_rate": 0.12,
                "trade_volume": 0.9
            }
        }
        
        effects = phase_effects.get(new_phase, {})
        
        for attribute, value in effects.items():
            if hasattr(cycle, attribute):
                setattr(cycle, attribute, value)
    
    # =========================================================================
    # NPC MIGRATION AND OPPORTUNITY SEEKING
    # =========================================================================
    
    def trigger_opportunity_migration(self, region_id: str, 
                                    opportunity_type: str = "gold_rush") -> List[UUID]:
        """Trigger NPC migration to a region due to economic opportunities"""
        try:
            # Get integration manager for cross-system access
            integration = get_integration_manager(self.db)
            
            # Get nearby regions to draw NPCs from
            nearby_regions = integration.region_interface.get_nearby_regions(region_id, max_distance=3)
            
            if not nearby_regions:
                logger.warning(f"No nearby regions found for migration to {region_id}")
                return []
            
            migrating_npcs = []
            target_migrants = random.randint(2, 6)  # 2-6 NPCs will migrate
            
            for source_region in nearby_regions:
                if len(migrating_npcs) >= target_migrants:
                    break
                
                # Look for NPCs with high wanderlust and entrepreneurial traits
                trait_filters = {
                    "wanderlust": 0.6,  # High wanderlust
                    "entrepreneurial": 0.5,  # Moderate to high entrepreneurial spirit
                    "wealth_seeking": 0.4  # Some interest in wealth
                }
                
                potential_migrants = integration.npc_interface.get_npcs_in_region(
                    source_region, trait_filters
                )
                
                # Calculate migration probability for each NPC
                for npc_id in potential_migrants:
                    if len(migrating_npcs) >= target_migrants:
                        break
                    
                    try:
                        # Get NPC traits for migration decision
                        traits = integration.npc_interface.get_npc_traits(npc_id)
                        
                        # Calculate migration probability based on traits and distance
                        travel_time = integration.region_interface.calculate_travel_time(
                            source_region, region_id
                        )
                        
                        # Higher wanderlust and entrepreneurial spirit = higher migration chance
                        migration_prob = (
                            traits.get("wanderlust", 0.5) * 0.4 +
                            traits.get("entrepreneurial", 0.5) * 0.3 +
                            traits.get("wealth_seeking", 0.5) * 0.2 +
                            traits.get("risk_tolerance", 0.5) * 0.1
                        )
                        
                        # Distance penalty (longer travel = less likely to migrate)
                        distance_penalty = min(0.3, travel_time * 0.05)
                        migration_prob -= distance_penalty
                        
                        # Opportunity type bonus
                        opportunity_bonuses = {
                            "gold_rush": 0.3,
                            "trade_boom": 0.2,
                            "resource_discovery": 0.25,
                            "market_expansion": 0.15
                        }
                        migration_prob += opportunity_bonuses.get(opportunity_type, 0.1)
                        
                        # Roll for migration
                        if random.random() < migration_prob:
                            # Attempt to move the NPC
                            success = integration.npc_interface.move_npc_to_region(
                                npc_id, region_id, f"{opportunity_type}_migration"
                            )
                            
                            if success:
                                migrating_npcs.append(npc_id)
                                
                                # Create economic competition for the arriving NPC
                                competition_types = [
                                    CompetitionType.COMMODITY_BUYOUT,
                                    CompetitionType.PROPERTY_ACQUISITION,
                                    CompetitionType.PRICE_UNDERCUTTING
                                ]
                                competition_type = random.choice(competition_types)
                                
                                # Calculate offered amount based on NPC wealth
                                npc_wealth = integration.npc_interface.get_npc_wealth(npc_id)
                                offered_amount = npc_wealth * random.uniform(0.2, 0.6)  # 20-60% of wealth
                                
                                competition = self.initiate_npc_competition(
                                    initiator_npc_id=npc_id,
                                    region_id=region_id,
                                    competition_type=competition_type,
                                    offered_amount=offered_amount,
                                    resource_targeted=opportunity_type
                                )
                                
                                logger.info(f"Migrating NPC {npc_id} created {competition_type.value} "
                                          f"competition with offer of {offered_amount:.0f}")
                    
                    except Exception as e:
                        logger.warning(f"Error processing migration for NPC {npc_id}: {e}")
                        continue
            
            # If we didn't get enough migrants from existing NPCs, create some wandering merchants
            if len(migrating_npcs) < 2:
                merchants_needed = 2 - len(migrating_npcs)
                for _ in range(merchants_needed):
                    new_merchant = integration.npc_interface.create_wandering_npc(
                        region_id, "opportunity_seeker"
                    )
                    
                    if new_merchant and new_merchant != UUID('00000000-0000-0000-0000-000000000000'):
                        migrating_npcs.append(new_merchant)
                        
                        # Create competition for new merchant
                        competition = self.initiate_npc_competition(
                            initiator_npc_id=new_merchant,
                            region_id=region_id,
                            competition_type=CompetitionType.COMMODITY_BUYOUT,
                            offered_amount=random.uniform(800, 2500),
                            resource_targeted=opportunity_type
                        )
                        
                        logger.info(f"Created wandering merchant {new_merchant} for {opportunity_type}")
            
            logger.info(f"Triggered {opportunity_type} migration to region {region_id}: "
                       f"{len(migrating_npcs)} NPCs migrated")
            return migrating_npcs
            
        except Exception as e:
            logger.error(f"Error triggering opportunity migration: {str(e)}")
            raise ServiceError(f"Failed to trigger opportunity migration: {str(e)}")
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_region_economic_summary(self, region_id: str) -> Dict[str, Any]:
        """Get a comprehensive economic summary for a region"""
        try:
            summary = {
                "region_id": region_id,
                "merchant_guilds": [],
                "active_competitions": [],
                "economic_cycle": None,
                "price_modifiers": {}
            }
            
            # Get merchant guilds
            guilds = self.db.query(MerchantGuildEntity).filter(
                and_(
                    MerchantGuildEntity.territory_control.contains([region_id]),
                    MerchantGuildEntity.is_active == True
                )
            ).all()
            summary["merchant_guilds"] = [guild.to_dict() for guild in guilds]
            
            # Get active competitions
            competitions = self.db.query(EconomicCompetition).filter(
                and_(
                    EconomicCompetition.region_id == region_id,
                    EconomicCompetition.status.in_(["pending", "in_progress"]),
                    EconomicCompetition.is_active == True
                )
            ).all()
            summary["active_competitions"] = [comp.to_dict() for comp in competitions]
            
            # Get economic cycle
            cycle = self.db.query(EconomicCycle).filter(
                and_(
                    EconomicCycle.region_id == region_id,
                    EconomicCycle.is_active == True
                )
            ).first()
            if cycle:
                summary["economic_cycle"] = cycle.to_dict()
            
            # Get sample price modifiers
            sample_resource_id = UUID('87654321-4321-8765-4321-210987654321')  # Placeholder
            summary["price_modifiers"] = self._calculate_price_modifiers(region_id, sample_resource_id)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting region economic summary: {str(e)}")
            raise ServiceError(f"Failed to get region economic summary: {str(e)}") 