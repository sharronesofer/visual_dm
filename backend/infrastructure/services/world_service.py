"""World service for managing world entities."""

from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.systems.world_state.world_types import WorldState as World
from backend.infrastructure.services import BaseService
from backend.infrastructure.database import get_db

class WorldService(BaseService[World]):
    """Service for managing world entities."""
    
    def __init__(self, db: Session = Depends(get_db)):
        """Initialize the world service.
        
        Args:
            db: Database session
        """
        super().__init__(World, db)
    
    async def update_world_state(self, world_id: int, state_data: Dict[str, Any]) -> World:
        """Update the state of a world.
        
        Args:
            world_id: World ID
            state_data: Updated state data
            
        Returns:
            Updated world entity
            
        Raises:
            HTTPException: If world not found or update fails
        """
        world = await self.get_by_id(world_id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"World with ID {world_id} not found"
            )
        
        # Update only state-related fields
        update_data = {}
        state_fields = ["time", "season", "weather", "events", "calendar_day"]
        
        for field in state_fields:
            if field in state_data:
                update_data[field] = state_data[field]
        
        return await self.update(world_id, update_data)
    
    async def advance_time(self, world_id: int, time_increment: int) -> World:
        """Advance the time in a world.
        
        Args:
            world_id: World ID
            time_increment: Amount of time to advance (in minutes)
            
        Returns:
            Updated world entity
            
        Raises:
            HTTPException: If world not found or update fails
        """
        world = await self.get_by_id(world_id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"World with ID {world_id} not found"
            )
        
        # Calculate new time and possibly update season
        current_time = world.time + time_increment
        
        # In a real implementation, this would have logic for day/night cycle,
        # season changes based on time passing, etc.
        
        update_data = {
            "time": current_time,
            # Other time-dependent state could be updated here
        }
        
        return await self.update(world_id, update_data)
    
    async def generate_weather(self, world_id: int, region: Optional[str] = None) -> Dict[str, Any]:
        """Generate weather for a world or specific region.
        
        Args:
            world_id: World ID
            region: Optional region name
            
        Returns:
            Weather data
            
        Raises:
            HTTPException: If world not found
        """
        world = await self.get_by_id(world_id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"World with ID {world_id} not found"
            )
        
        # In a real implementation, this would have complex weather generation logic
        # based on season, region, and other factors
        
        # Basic weather generation
        weather_types = ["sunny", "cloudy", "rainy", "stormy", "foggy", "snowy"]
        import random
        weather_type = random.choice(weather_types)
        
        weather_data = {
            "type": weather_type,
            "intensity": random.randint(1, 5),
            "region": region or "global",
            "temperature": random.randint(-10, 30)
        }
        
        # If this is global weather, update the world entity
        if not region:
            await self.update(world_id, {"weather": weather_data})
        
        return weather_data 