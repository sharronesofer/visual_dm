"""
FastAPI Routes for Optimized World Generation & Geography System

This module provides API routes for the optimized world generation system,
allowing external access to generate and manage world geography.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import random
import time
import os
import json

from backend.systems.world_state.optimized_worldgen import (
    OptimizedWorldGenerator, 
    create_world_generator
)
from backend.systems.world_state.utils.terrain_generator import (
    RegionParams,
    BiomeInfo
)

# Initialize router
router = APIRouter(
    prefix="/worldgen",
    tags=["world_generation"],
    responses={404: {"description": "Not found"}},
)

# Global generator instance with caching
generator = create_world_generator()

# Data models for API
class BiomeData(BaseModel):
    id: str
    name: str
    temperature_range: List[float] = Field(..., min_items=2, max_items=2)
    moisture_range: List[float] = Field(..., min_items=2, max_items=2)
    elevation_range: List[float] = Field(..., min_items=2, max_items=2)
    features: List[str]
    resources: Dict[str, float]
    color: str
    is_water: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "id": "forest",
                "name": "Forest",
                "temperature_range": [0.3, 0.7],
                "moisture_range": [0.6, 1.0],
                "elevation_range": [0.3, 0.7],
                "features": ["trees", "wildlife"],
                "resources": {"wood": 0.9, "game": 0.7},
                "color": "#228B22",
                "is_water": False
            }
        }

class PointOfInterestData(BaseModel):
    id: str
    name: str
    type: str
    x: int
    y: int
    biome: str
    elevation: float
    attributes: Dict[str, Any]
    
    class Config:
        schema_extra = {
            "example": {
                "id": "poi_12345_10_15",
                "name": "Ancient Grove",
                "type": "grove",
                "x": 10,
                "y": 15,
                "biome": "forest",
                "elevation": 0.45,
                "attributes": {
                    "difficulty": 3,
                    "treasure": True,
                    "discovered": False,
                    "resources": {"herbs": 0.8, "wood": 0.6}
                }
            }
        }

class RegionRequest(BaseModel):
    x: int = Field(..., description="X coordinate of the region")
    y: int = Field(..., description="Y coordinate of the region")
    size: int = Field(64, description="Size of the region (number of tiles per side)")
    world_seed: int = Field(..., description="World seed for consistent generation")
    continent_id: str = Field(..., description="ID of the continent this region belongs to")
    biome_influence: Optional[Dict[str, float]] = Field(
        None, 
        description="Optional biome influences to apply (biome_id: strength)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "x": 3,
                "y": 5,
                "size": 64,
                "world_seed": 12345,
                "continent_id": "continent_1",
                "biome_influence": {"forest": 0.3, "mountains": 0.1}
            }
        }

class RegionResponse(BaseModel):
    region_id: str
    world_seed: int
    continent_id: str
    size: int
    elevation: List[List[float]]
    moisture: List[List[float]]
    temperature: List[List[float]]
    biomes: List[List[str]]
    rivers: List[List[bool]]
    pois: List[PointOfInterestData]
    generation_time: float
    
    class Config:
        schema_extra = {
            "example": {
                "region_id": "3:5",
                "world_seed": 12345,
                "continent_id": "continent_1",
                "size": 64,
                "elevation": [[0.3, 0.4], [0.5, 0.6]],  # Simplified for example
                "moisture": [[0.5, 0.6], [0.7, 0.8]],   # Simplified for example
                "temperature": [[0.4, 0.5], [0.6, 0.7]], # Simplified for example
                "biomes": [["forest", "forest"], ["plains", "mountains"]], # Simplified
                "rivers": [[False, False], [True, False]], # Simplified for example
                "pois": [
                    {
                        "id": "poi_12345_10_15",
                        "name": "Ancient Grove",
                        "type": "grove",
                        "x": 10,
                        "y": 15,
                        "biome": "forest",
                        "elevation": 0.45,
                        "attributes": {
                            "difficulty": 3,
                            "treasure": True,
                            "discovered": False,
                            "resources": {"herbs": 0.8, "wood": 0.6}
                        }
                    }
                ],
                "generation_time": 0.125
            }
        }

class ContinentResponse(BaseModel):
    continent_id: str
    name: str
    regions: List[str]
    predominant_biomes: Dict[str, float]
    size: int
    
    class Config:
        schema_extra = {
            "example": {
                "continent_id": "continent_1",
                "name": "Eastern Lands",
                "regions": ["3:5", "3:6", "4:5", "4:6"],
                "predominant_biomes": {"forest": 0.5, "mountains": 0.3, "plains": 0.2},
                "size": 4
            }
        }

class WorldResponse(BaseModel):
    world_seed: int
    name: str
    continents: List[str]
    ocean_level: float
    total_regions: int
    
    class Config:
        schema_extra = {
            "example": {
                "world_seed": 12345,
                "name": "Mystical Realms",
                "continents": ["continent_1", "continent_2", "continent_3"],
                "ocean_level": 0.3,
                "total_regions": 120
            }
        }

# Dependency for getting the world generator
def get_world_generator():
    return generator

# Routes
@router.get("/biomes", response_model=List[BiomeData], summary="Get all available biomes")
async def get_biomes(world_generator: OptimizedWorldGenerator = Depends(get_world_generator)):
    """
    Get information about all available biomes in the world generation system.
    
    Returns a list of BiomeData objects containing details about each biome.
    """
    biomes_data = []
    
    for biome_id, biome in world_generator.biomes.items():
        # Skip transition biomes in the API to reduce data size
        if biome.is_transition:
            continue
            
        biomes_data.append(BiomeData(
            id=biome_id,
            name=biome.name,
            temperature_range=list(biome.temperature_range),
            moisture_range=list(biome.moisture_range),
            elevation_range=list(biome.elevation_range),
            features=biome.features,
            resources=biome.resources,
            color=biome.color,
            is_water=biome.is_water
        ))
    
    return biomes_data

@router.post("/region", response_model=RegionResponse, summary="Generate a region")
async def generate_region(
    request: RegionRequest,
    world_generator: OptimizedWorldGenerator = Depends(get_world_generator)
):
    """
    Generate a single region with the specified parameters.
    
    Returns detailed region data including terrain, biomes, and points of interest.
    """
    try:
        # Validate size (must be between 16 and 256)
        if request.size < 16 or request.size > 256:
            raise HTTPException(
                status_code=400, 
                detail="Region size must be between 16 and 256"
            )
        
        # Create region parameters
        params = RegionParams(
            x=request.x,
            y=request.y,
            size=request.size,
            continent_id=request.continent_id,
            world_seed=request.world_seed,
            biome_influence=request.biome_influence or {}
        )
        
        # Generate the region terrain
        start_time = time.time()
        terrain_data = world_generator.generate_region_terrain(params)
        
        # Process POIs data
        pois_data = []
        for poi in terrain_data.get('pois', []):
            pois_data.append(PointOfInterestData(
                id=poi['id'],
                name=poi['name'],
                type=poi['type'],
                x=poi['x'],
                y=poi['y'],
                biome=poi['biome'],
                elevation=poi['elevation'],
                attributes=poi['attributes']
            ))
        
        # Create response
        return RegionResponse(
            region_id=terrain_data['region_id'],
            world_seed=terrain_data['world_seed'],
            continent_id=terrain_data['continent_id'],
            size=terrain_data['size'],
            elevation=terrain_data['elevation'],
            moisture=terrain_data['moisture'],
            temperature=terrain_data['temperature'],
            biomes=terrain_data['biomes'],
            rivers=terrain_data['rivers'],
            pois=pois_data,
            generation_time=terrain_data.get('generation_time', time.time() - start_time)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating region: {str(e)}"
        )

@router.get("/region/{x}/{y}", response_model=RegionResponse, summary="Get a specific region")
async def get_region(
    x: int,
    y: int,
    size: int = Query(64, ge=16, le=256),
    seed: int = Query(..., description="World seed"),
    continent_id: str = Query(..., description="Continent ID"),
    world_generator: OptimizedWorldGenerator = Depends(get_world_generator)
):
    """
    Get a specific region by coordinates.
    
    Similar to generate_region but using GET parameters.
    """
    try:
        # Create region parameters
        params = RegionParams(
            x=x,
            y=y,
            size=size,
            continent_id=continent_id,
            world_seed=seed,
            biome_influence={}
        )
        
        # Generate the region terrain
        start_time = time.time()
        terrain_data = world_generator.generate_region_terrain(params)
        
        # Process POIs data
        pois_data = []
        for poi in terrain_data.get('pois', []):
            pois_data.append(PointOfInterestData(
                id=poi['id'],
                name=poi['name'],
                type=poi['type'],
                x=poi['x'],
                y=poi['y'],
                biome=poi['biome'],
                elevation=poi['elevation'],
                attributes=poi['attributes']
            ))
        
        # Create response
        return RegionResponse(
            region_id=terrain_data['region_id'],
            world_seed=terrain_data['world_seed'],
            continent_id=terrain_data['continent_id'],
            size=terrain_data['size'],
            elevation=terrain_data['elevation'],
            moisture=terrain_data['moisture'],
            temperature=terrain_data['temperature'],
            biomes=terrain_data['biomes'],
            rivers=terrain_data['rivers'],
            pois=pois_data,
            generation_time=terrain_data.get('generation_time', time.time() - start_time)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting region: {str(e)}"
        )

@router.get("/continent/{continent_id}", response_model=ContinentResponse, summary="Get continent data")
async def get_continent(
    continent_id: str,
    world_seed: int = Query(..., description="World seed")
):
    """
    Get data for a specific continent.
    
    This is a placeholder for continent data - in a full implementation, this would
    retrieve data about the entire continent.
    """
    # This is a placeholder - in a real implementation, this would load or generate
    # detailed continent data
    return ContinentResponse(
        continent_id=continent_id,
        name=f"Continent {continent_id}",
        regions=[],  # This would contain region IDs that are part of this continent
        predominant_biomes={"forest": 0.5, "mountains": 0.3, "plains": 0.2},
        size=0  # This would be the number of regions in the continent
    )

@router.get("/world/{world_seed}", response_model=WorldResponse, summary="Get world data")
async def get_world(world_seed: int):
    """
    Get data for an entire world.
    
    This is a placeholder for world data - in a full implementation, this would
    retrieve data about the entire world.
    """
    # This is a placeholder - in a real implementation, this would load or generate
    # detailed world data
    return WorldResponse(
        world_seed=world_seed,
        name=f"World {world_seed}",
        continents=[],  # This would contain continent IDs for this world
        ocean_level=0.3,
        total_regions=0  # This would be the total number of regions in the world
    )

@router.get("/test-region", response_model=RegionResponse, summary="Test region generation")
async def test_region(
    size: int = Query(64, ge=16, le=256),
    world_generator: OptimizedWorldGenerator = Depends(get_world_generator)
):
    """
    Generate a test region with default parameters.
    
    Useful for testing the world generation system.
    """
    import random
    
    test_seed = random.randint(1, 1000000)
    test_params = RegionParams(
        x=0,
        y=0,
        size=size,
        continent_id="test_continent",
        world_seed=test_seed
    )
    
    # Generate the region terrain
    start_time = time.time()
    terrain_data = world_generator.generate_region_terrain(test_params)
    
    # Process POIs data
    pois_data = []
    for poi in terrain_data.get('pois', []):
        pois_data.append(PointOfInterestData(
            id=poi['id'],
            name=poi['name'],
            type=poi['type'],
            x=poi['x'],
            y=poi['y'],
            biome=poi['biome'],
            elevation=poi['elevation'],
            attributes=poi['attributes']
        ))
    
    # Create response
    return RegionResponse(
        region_id=terrain_data['region_id'],
        world_seed=terrain_data['world_seed'],
        continent_id=terrain_data['continent_id'],
        size=terrain_data['size'],
        elevation=terrain_data['elevation'],
        moisture=terrain_data['moisture'],
        temperature=terrain_data['temperature'],
        biomes=terrain_data['biomes'],
        rivers=terrain_data['rivers'],
        pois=pois_data,
        generation_time=terrain_data.get('generation_time', time.time() - start_time)
    ) 