"""
Advanced Economy System SQLAlchemy Models - Infrastructure Layer

This module contains the SQLAlchemy table definitions for advanced economy features.
Business logic models remain in backend/systems/economy/models/advanced_economy.py
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base


class MerchantGuildEntity(Base):
    """SQLAlchemy entity for merchant guilds"""
    
    __tablename__ = "merchant_guilds"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    faction_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('faction_entities.id'), nullable=True)
    headquarters_region_id = Column(String(100), index=True)
    
    # Guild Economics
    total_wealth = Column(Float, default=0.0)
    territory_control = Column(JSONB, default=list)  # List of region IDs controlled
    trade_routes = Column(JSONB, default=list)  # List of trade route IDs
    controlled_markets = Column(JSONB, default=list)  # List of market IDs
    
    # Guild Operations
    pricing_influence = Column(Float, default=0.0)  # 0.0 to 1.0
    market_share = Column(Float, default=0.0)  # 0.0 to 1.0
    coordination_level = Column(Float, default=0.5)  # How well they coordinate
    
    # Guild Relationships
    allied_guilds = Column(JSONB, default=list)  # List of allied guild IDs
    rival_guilds = Column(JSONB, default=list)  # List of rival guild IDs
    
    status = Column(String(50), default="active", index=True)
    is_active = Column(Boolean, default=True, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "faction_id": str(self.faction_id) if self.faction_id else None,
            "headquarters_region_id": self.headquarters_region_id,
            "total_wealth": self.total_wealth,
            "territory_control": self.territory_control or [],
            "trade_routes": self.trade_routes or [],
            "controlled_markets": self.controlled_markets or [],
            "pricing_influence": self.pricing_influence,
            "market_share": self.market_share,
            "coordination_level": self.coordination_level,
            "allied_guilds": self.allied_guilds or [],
            "rival_guilds": self.rival_guilds or [],
            "status": self.status,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class DynamicPricing(Base):
    """SQLAlchemy entity for dynamic pricing rules"""
    
    __tablename__ = "dynamic_pricing"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    region_id = Column(String(100), nullable=False, index=True)
    resource_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    
    # Base pricing
    base_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    
    # Price modifiers
    danger_level_modifier = Column(Float, default=1.0)
    trade_route_modifier = Column(Float, default=1.0)
    infrastructure_modifier = Column(Float, default=1.0)
    guild_modifier = Column(Float, default=1.0)
    competition_modifier = Column(Float, default=1.0)
    cycle_modifier = Column(Float, default=1.0)
    
    # Last update information
    last_calculated = Column(DateTime, default=datetime.utcnow)
    calculation_source = Column(String(100))  # What triggered the recalculation
    
    # Active modifiers (for debugging/transparency)
    active_modifiers = Column(JSONB, default=dict)
    
    is_active = Column(Boolean, default=True, index=True)

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "region_id": self.region_id,
            "resource_id": str(self.resource_id),
            "base_price": self.base_price,
            "current_price": self.current_price,
            "final_price": self.calculate_final_price(),
            "modifiers": {
                "danger_level": self.danger_level_modifier,
                "trade_route": self.trade_route_modifier,
                "infrastructure": self.infrastructure_modifier,
                "guild": self.guild_modifier,
                "competition": self.competition_modifier,
                "cycle": self.cycle_modifier
            },
            "last_calculated": self.last_calculated.isoformat() if self.last_calculated else None,
            "calculation_source": self.calculation_source,
            "active_modifiers": self.active_modifiers or {},
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class EconomicCompetition(Base):
    """SQLAlchemy entity for economic competition events"""
    
    __tablename__ = "economic_competition"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    initiator_npc_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    target_npc_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=True, index=True)
    target_poi_id = Column(String(100), nullable=True, index=True)
    region_id = Column(String(100), nullable=False, index=True)
    
    competition_type = Column(String(50), nullable=False, index=True)
    
    # Competition details
    offered_amount = Column(Float, default=0.0)
    resource_targeted = Column(String(100))
    success_probability = Column(Float, default=0.5)
    
    # Status and timing
    status = Column(String(50), default="pending", index=True)  # pending, in_progress, completed, failed
    start_date = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(DateTime, nullable=True)
    
    # Results
    success = Column(Boolean, nullable=True)
    impact_details = Column(JSONB, default=dict)
    wealth_transferred = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True, index=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "initiator_npc_id": str(self.initiator_npc_id),
            "target_npc_id": str(self.target_npc_id) if self.target_npc_id else None,
            "target_poi_id": self.target_poi_id,
            "region_id": self.region_id,
            "competition_type": self.competition_type,
            "offered_amount": self.offered_amount,
            "resource_targeted": self.resource_targeted,
            "success_probability": self.success_probability,
            "status": self.status,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "success": self.success,
            "impact_details": self.impact_details or {},
            "wealth_transferred": self.wealth_transferred,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class EconomicCycle(Base):
    """SQLAlchemy entity for regional economic cycles"""
    
    __tablename__ = "economic_cycles"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    region_id = Column(String(100), nullable=False, index=True)
    cycle_name = Column(String(255), nullable=False)
    
    # Cycle phases
    current_phase = Column(String(50), nullable=False, index=True)
    phase_start_date = Column(DateTime, default=datetime.utcnow)
    phase_duration_days = Column(Integer, default=30)
    
    # Economic indicators
    prosperity_level = Column(Float, default=0.5)  # 0.0 to 1.0
    inflation_rate = Column(Float, default=0.0)  # -1.0 to 1.0
    unemployment_rate = Column(Float, default=0.1)  # 0.0 to 1.0
    trade_volume = Column(Float, default=1.0)  # Multiplier
    
    # Cycle triggers and causes
    trigger_events = Column(JSONB, default=list)  # List of events that triggered this cycle
    affected_resources = Column(JSONB, default=list)  # List of resource IDs affected
    
    # War and faction impact
    war_impact = Column(Float, default=0.0)  # -1.0 to 1.0
    faction_stability = Column(Float, default=0.5)  # 0.0 to 1.0
    
    is_active = Column(Boolean, default=True, index=True)

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
        
        phase_mod = phase_modifiers.get(self.current_phase, 1.0)
        prosperity_mod = 0.5 + (self.prosperity_level * 0.5)  # 0.5 to 1.0 range
        war_mod = 1.0 + self.war_impact  # -1.0 to 1.0 becomes 0.0 to 2.0
        
        return base_modifier * phase_mod * prosperity_mod * war_mod

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "region_id": self.region_id,
            "cycle_name": self.cycle_name,
            "current_phase": self.current_phase,
            "phase_start_date": self.phase_start_date.isoformat() if self.phase_start_date else None,
            "phase_duration_days": self.phase_duration_days,
            "prosperity_level": self.prosperity_level,
            "inflation_rate": self.inflation_rate,
            "unemployment_rate": self.unemployment_rate,
            "trade_volume": self.trade_volume,
            "trigger_events": self.trigger_events or [],
            "affected_resources": [str(r) for r in (self.affected_resources or [])],
            "war_impact": self.war_impact,
            "faction_stability": self.faction_stability,
            "cycle_modifier": self.get_cycle_modifier(),
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 