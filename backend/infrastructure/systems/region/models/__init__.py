"""
Infrastructure Database Models for Region System

SQLAlchemy ORM models for persisting region and continent data.
These models provide the database layer for the region system business logic.
"""

from sqlalchemy import Column, String, Integer, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from backend.infrastructure.database import Base, BaseModel


class RegionDB(BaseModel):
    """SQLAlchemy model for region persistence."""
    __tablename__ = 'regions'
    
    # Basic identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    region_type = Column(String(50), nullable=False, default='wilderness')
    status = Column(String(20), nullable=False, default='active')
    
    # Geographic data
    dominant_biome = Column(String(50), nullable=False, default='temperate_forest')
    climate = Column(String(50), nullable=False, default='temperate')
    hex_coordinates = Column(JSON)  # List of hex coordinate dicts
    center_coordinate = Column(JSON)  # Single hex coordinate dict
    area_square_km = Column(Float, default=0.0)
    perimeter_km = Column(Float, default=0.0)
    elevation = Column(Float, default=0.0)
    elevation_variance = Column(Float, default=0.0)
    
    # Environmental data
    temperature_range = Column(JSON)  # [min, max] tuple
    precipitation = Column(Float, default=500.0)
    humidity = Column(Float, default=0.5)
    wind_patterns = Column(JSON)
    seasonal_variations = Column(JSON)
    natural_hazards = Column(ARRAY(String))
    soil_fertility = Column(Float, default=0.5)
    water_availability = Column(Float, default=0.5)
    
    # Political data
    controlling_faction_id = Column(UUID(as_uuid=True), nullable=True)
    government_type = Column(String(50), default='none')
    political_stability = Column(Float, default=0.5)
    law_level = Column(Integer, default=5)
    
    # Economic data
    wealth_level = Column(Float, default=0.5)
    trade_routes = Column(ARRAY(String))
    primary_industries = Column(ARRAY(String))
    
    # Demographic data
    population = Column(Integer, default=0)
    population_density = Column(Float, default=0.0)
    major_settlements = Column(ARRAY(String))
    
    # Gameplay data
    danger_level = Column(Integer, default=2)
    exploration_status = Column(Float, default=0.0)
    discovery_date = Column(String)  # ISO date string
    
    # Connections
    neighboring_region_ids = Column(ARRAY(String))
    continent_id = Column(UUID(as_uuid=True), ForeignKey('continents.id'), nullable=True)
    
    # Dynamic state
    current_events = Column(ARRAY(String))
    historical_events = Column(ARRAY(String))
    
    # Resource nodes (stored as JSON for now)
    resource_nodes = Column(JSON, default=list)
    poi_ids = Column(ARRAY(String))
    
    # Additional properties for extensibility
    properties = Column(JSON, default=dict)
    
    # Relationships
    continent = relationship("ContinentDB", back_populates="regions")
    
    def __repr__(self):
        return f"<RegionDB(id={self.id}, name='{self.name}', type='{self.region_type}')>"


class ContinentDB(BaseModel):
    """SQLAlchemy model for continent persistence."""
    __tablename__ = 'continents'
    
    # Basic identification
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    
    # Geographic data
    total_area_square_km = Column(Float, default=0.0)
    climate_zones = Column(ARRAY(String))  # Array of climate type strings
    major_biomes = Column(ARRAY(String))   # Array of biome type strings
    
    # Political data
    major_powers = Column(ARRAY(String))   # Array of faction UUIDs as strings
    political_situation = Column(String(50), default='stable')
    
    # Generation data
    generation_seed = Column(Integer, nullable=True)
    generation_parameters = Column(JSON, default=dict)
    
    # Additional properties for extensibility
    properties = Column(JSON, default=dict)
    
    # Relationships
    regions = relationship("RegionDB", back_populates="continent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ContinentDB(id={self.id}, name='{self.name}')>"


class ResourceNodeDB(BaseModel):
    """SQLAlchemy model for resource node persistence."""
    __tablename__ = 'resource_nodes'
    
    # Resource identification
    resource_type = Column(String(50), nullable=False)
    
    # Resource properties
    abundance = Column(Float, nullable=False)
    quality = Column(Float, nullable=False)
    accessibility = Column(Float, nullable=False)
    depletion_rate = Column(Float, default=0.0)
    current_reserves = Column(Float, default=1.0)
    
    # Location data
    region_id = Column(UUID(as_uuid=True), ForeignKey('regions.id'), nullable=False)
    hex_coordinate = Column(JSON, nullable=True)  # Optional specific location within region
    
    # Additional properties
    properties = Column(JSON, default=dict)
    
    # Relationships
    region = relationship("RegionDB")
    
    def __repr__(self):
        return f"<ResourceNodeDB(id={self.id}, type='{self.resource_type}', abundance={self.abundance})>"


__all__ = [
    'RegionDB',
    'ContinentDB', 
    'ResourceNodeDB'
] 