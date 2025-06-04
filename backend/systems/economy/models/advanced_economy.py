"""
Advanced Economy System Business Models

This module defines the business data models for advanced economy features.
SQLAlchemy models have been moved to backend/infrastructure/database/economy/advanced_models.py
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from backend.infrastructure.shared.models import SharedBaseModel


class PriceModifierType(Enum):
    """Types of price modifiers"""
    DANGER_LEVEL = "danger_level"
    TRADE_ROUTE_SAFETY = "trade_route_safety"
    ROAD_ACCESS = "road_access"
    WATERWAY_ACCESS = "waterway_access"
    GUILD_CONTROL = "guild_control"
    MARKET_COMPETITION = "market_competition"
    ECONOMIC_CYCLE = "economic_cycle"
    FACTION_WAR = "faction_war"
    RESOURCE_SCARCITY = "resource_scarcity"


class EconomicCyclePhase(Enum):
    """Economic cycle phases"""
    BOOM = "boom"
    GROWTH = "growth"
    STABLE = "stable"
    RECESSION = "recession"
    BUST = "bust"
    RECOVERY = "recovery"


class CompetitionType(Enum):
    """Types of economic competition"""
    HOSTILE_TAKEOVER = "hostile_takeover"
    COMMODITY_BUYOUT = "commodity_buyout"
    PROPERTY_ACQUISITION = "property_acquisition"
    PRICE_UNDERCUTTING = "price_undercutting"
    MARKET_MANIPULATION = "market_manipulation"


class MerchantGuildModel(SharedBaseModel):
    """Pydantic model for merchant guild"""
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    faction_id: Optional[UUID] = None
    headquarters_region_id: Optional[str] = None
    total_wealth: float = Field(default=0.0, ge=0.0)
    territory_control: List[str] = Field(default_factory=list)
    trade_routes: List[str] = Field(default_factory=list)
    controlled_markets: List[str] = Field(default_factory=list)
    pricing_influence: float = Field(default=0.0, ge=0.0, le=1.0)
    market_share: float = Field(default=0.0, ge=0.0, le=1.0)
    coordination_level: float = Field(default=0.5, ge=0.0, le=1.0)
    allied_guilds: List[UUID] = Field(default_factory=list)
    rival_guilds: List[UUID] = Field(default_factory=list)
    status: str = Field(default="active")
    is_active: bool = Field(default=True)

    model_config = ConfigDict(from_attributes=True)


class DynamicPricingModel(SharedBaseModel):
    """Pydantic model for dynamic pricing"""
    
    id: UUID = Field(default_factory=uuid4)
    region_id: str = Field(..., min_length=1)
    resource_id: UUID = Field(...)
    base_price: float = Field(..., gt=0.0)
    current_price: float = Field(..., gt=0.0)
    danger_level_modifier: float = Field(default=1.0, gt=0.0)
    trade_route_modifier: float = Field(default=1.0, gt=0.0)
    infrastructure_modifier: float = Field(default=1.0, gt=0.0)
    guild_modifier: float = Field(default=1.0, gt=0.0)
    competition_modifier: float = Field(default=1.0, gt=0.0)
    cycle_modifier: float = Field(default=1.0, gt=0.0)
    last_calculated: datetime = Field(default_factory=datetime.utcnow)
    calculation_source: Optional[str] = None
    active_modifiers: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=True)

    model_config = ConfigDict(from_attributes=True)

    def calculate_final_price(self) -> float:
        """Calculate the final price with all modifiers"""
        return self.base_price * (
            self.danger_level_modifier *
            self.trade_route_modifier *
            self.infrastructure_modifier *
            self.guild_modifier *
            self.competition_modifier *
            self.cycle_modifier
        )


class EconomicCompetitionModel(SharedBaseModel):
    """Pydantic model for economic competition"""
    
    id: UUID = Field(default_factory=uuid4)
    initiator_npc_id: UUID = Field(...)
    target_npc_id: Optional[UUID] = None
    target_poi_id: Optional[str] = None
    region_id: str = Field(..., min_length=1)
    competition_type: CompetitionType = Field(...)
    offered_amount: float = Field(default=0.0, ge=0.0)
    resource_targeted: Optional[str] = None
    success_probability: float = Field(default=0.5, ge=0.0, le=1.0)
    status: str = Field(default="pending")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    completion_date: Optional[datetime] = None
    success: Optional[bool] = None
    impact_details: Dict[str, Any] = Field(default_factory=dict)
    wealth_transferred: float = Field(default=0.0)
    is_active: bool = Field(default=True)

    model_config = ConfigDict(from_attributes=True)


class EconomicCycleModel(SharedBaseModel):
    """Pydantic model for economic cycle"""
    
    id: UUID = Field(default_factory=uuid4)
    region_id: str = Field(..., min_length=1)
    cycle_name: str = Field(..., min_length=1, max_length=255)
    current_phase: EconomicCyclePhase = Field(...)
    phase_start_date: datetime = Field(default_factory=datetime.utcnow)
    phase_duration_days: int = Field(default=30, gt=0)
    prosperity_level: float = Field(default=0.5, ge=0.0, le=1.0)
    inflation_rate: float = Field(default=0.0, ge=-1.0, le=1.0)
    unemployment_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    trade_volume: float = Field(default=1.0, gt=0.0)
    trigger_events: List[str] = Field(default_factory=list)
    affected_resources: List[UUID] = Field(default_factory=list)
    war_impact: float = Field(default=0.0, ge=-1.0, le=1.0)
    faction_stability: float = Field(default=0.5, ge=0.0, le=1.0)
    is_active: bool = Field(default=True)

    model_config = ConfigDict(from_attributes=True)

    def get_cycle_modifier(self) -> float:
        """Calculate the cycle's impact on prices"""
        base_modifier = 1.0
        
        # Phase impacts
        phase_modifiers = {
            "boom": 1.3,
            "growth": 1.1,
            "stable": 1.0,
            "recession": 0.8,
            "bust": 0.6,
            "recovery": 0.9
        }
        
        phase_mod = phase_modifiers.get(self.current_phase.value, 1.0)
        prosperity_mod = 0.5 + (self.prosperity_level * 0.5)  # 0.5 to 1.0 range
        war_mod = 1.0 + self.war_impact  # -1.0 to 1.0 becomes 0.0 to 2.0
        
        return base_modifier * phase_mod * prosperity_mod * war_mod


# Request Models
class CreateMerchantGuildRequest(BaseModel):
    """Request model for creating merchant guild"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    faction_id: Optional[UUID] = None
    headquarters_region_id: Optional[str] = None
    initial_wealth: float = Field(default=1000.0, ge=0.0)


class UpdateMerchantGuildRequest(BaseModel):
    """Request model for updating merchant guild"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    headquarters_region_id: Optional[str] = None
    status: Optional[str] = None


class CreateEconomicCompetitionRequest(BaseModel):
    """Request model for creating economic competition"""
    
    initiator_npc_id: UUID = Field(...)
    target_npc_id: Optional[UUID] = None
    target_poi_id: Optional[str] = None
    region_id: str = Field(..., min_length=1)
    competition_type: CompetitionType = Field(...)
    offered_amount: float = Field(default=0.0, ge=0.0)
    resource_targeted: Optional[str] = None


class UpdateDynamicPricingRequest(BaseModel):
    """Request model for updating dynamic pricing"""
    
    region_id: str = Field(..., min_length=1)
    resource_id: UUID = Field(...)
    recalculate_from_source: Optional[str] = None


# Response Models
class MerchantGuildResponse(BaseModel):
    """Response model for merchant guild"""
    
    id: UUID
    name: str
    description: Optional[str]
    faction_id: Optional[UUID]
    headquarters_region_id: Optional[str]
    total_wealth: float
    territory_control: List[str]
    trade_routes: List[str]
    controlled_markets: List[str]
    pricing_influence: float
    market_share: float
    coordination_level: float
    allied_guilds: List[UUID]
    rival_guilds: List[UUID]
    status: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class DynamicPricingResponse(BaseModel):
    """Response model for dynamic pricing"""
    
    id: UUID
    region_id: str
    resource_id: UUID
    base_price: float
    current_price: float
    final_price: float
    modifiers: Dict[str, float]
    last_calculated: datetime
    calculation_source: Optional[str]
    active_modifiers: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class EconomicCompetitionResponse(BaseModel):
    """Response model for economic competition"""
    
    id: UUID
    initiator_npc_id: UUID
    target_npc_id: Optional[UUID]
    target_poi_id: Optional[str]
    region_id: str
    competition_type: str
    offered_amount: float
    resource_targeted: Optional[str]
    success_probability: float
    status: str
    start_date: datetime
    completion_date: Optional[datetime]
    success: Optional[bool]
    impact_details: Dict[str, Any]
    wealth_transferred: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class EconomicCycleResponse(BaseModel):
    """Response model for economic cycle"""
    
    id: UUID
    region_id: str
    cycle_name: str
    current_phase: str
    phase_start_date: datetime
    phase_duration_days: int
    prosperity_level: float
    inflation_rate: float
    unemployment_rate: float
    trade_volume: float
    trigger_events: List[str]
    affected_resources: List[UUID]
    war_impact: float
    faction_stability: float
    cycle_modifier: float
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True) 