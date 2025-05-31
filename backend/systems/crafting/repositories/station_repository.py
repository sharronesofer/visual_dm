"""
Station Repository

Provides database operations for crafting stations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.systems.crafting.models.station import CraftingStation
from backend.systems.crafting.repositories.base_repository import BaseRepository

class StationRepository(BaseRepository[CraftingStation]):
    """
    Repository for crafting station operations.
    """
    
    def __init__(self):
        """Initialize the station repository."""
        super().__init__(CraftingStation)
    
    def get_by_type(self, station_type: str) -> List[CraftingStation]:
        """
        Get all stations of a specific type.
        
        Args:
            station_type: The station type
            
        Returns:
            List of stations of the specified type
        """
        return self.find_by(station_type=station_type, is_active=True)
    
    def get_by_location(self, location_id: str) -> List[CraftingStation]:
        """
        Get all stations at a specific location.
        
        Args:
            location_id: The location ID
            
        Returns:
            List of stations at the location
        """
        return self.find_by(location_id=location_id, is_active=True)
    
    def get_by_owner(self, owner_id: str) -> List[CraftingStation]:
        """
        Get all stations owned by a specific character.
        
        Args:
            owner_id: The owner's character ID
            
        Returns:
            List of owned stations
        """
        return self.find_by(owner_id=owner_id)
    
    def get_public_stations(self, location_id: Optional[str] = None) -> List[CraftingStation]:
        """
        Get all public stations, optionally filtered by location.
        
        Args:
            location_id: Optional location filter
            
        Returns:
            List of public stations
        """
        filters = {"is_public": True, "is_active": True}
        if location_id:
            filters["location_id"] = location_id
        return self.find_by(**filters)
    
    def get_available_stations(self, character_id: str, location_id: Optional[str] = None) -> List[CraftingStation]:
        """
        Get stations available to a character (public or owned by them).
        
        Args:
            character_id: The character's ID
            location_id: Optional location filter
            
        Returns:
            List of available stations
        """
        session = self._get_session()
        try:
            query = session.query(self.model)\
                .filter(self.model.is_active == True)\
                .filter(or_(
                    self.model.is_public == True,
                    self.model.owner_id == character_id
                ))
            
            if location_id:
                query = query.filter(self.model.location_id == location_id)
                
            return query.order_by(self.model.station_type, self.model.level.desc()).all()
        finally:
            session.close()
    
    def get_stations_by_level_range(self, min_level: int, max_level: int) -> List[CraftingStation]:
        """
        Get stations within a level range.
        
        Args:
            min_level: Minimum level
            max_level: Maximum level
            
        Returns:
            List of stations in level range
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .filter(and_(
                    self.model.level >= min_level,
                    self.model.level <= max_level
                ))\
                .filter(self.model.is_active == True)\
                .order_by(self.model.level)\
                .all()
        finally:
            session.close()
    
    def get_high_efficiency_stations(self, min_efficiency: float = 1.5) -> List[CraftingStation]:
        """
        Get stations with high efficiency bonuses.
        
        Args:
            min_efficiency: Minimum efficiency bonus
            
        Returns:
            List of high-efficiency stations
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .filter(self.model.efficiency_bonus >= min_efficiency)\
                .filter(self.model.is_active == True)\
                .order_by(self.model.efficiency_bonus.desc())\
                .all()
        finally:
            session.close()
    
    def get_stations_with_capacity(self, min_capacity: int = 2) -> List[CraftingStation]:
        """
        Get stations with specific minimum capacity.
        
        Args:
            min_capacity: Minimum capacity required
            
        Returns:
            List of stations with sufficient capacity
        """
        session = self._get_session()
        try:
            return session.query(self.model)\
                .filter(self.model.capacity >= min_capacity)\
                .filter(self.model.is_active == True)\
                .order_by(self.model.capacity.desc())\
                .all()
        finally:
            session.close()
    
    def search_stations(self, search_term: str, limit: int = 50) -> List[CraftingStation]:
        """
        Search stations by name or description.
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of matching stations
        """
        session = self._get_session()
        try:
            search_pattern = f"%{search_term}%"
            return session.query(self.model)\
                .filter(or_(
                    self.model.name.ilike(search_pattern),
                    self.model.description.ilike(search_pattern)
                ))\
                .filter(self.model.is_active == True)\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def activate_station(self, station_id: str) -> bool:
        """
        Activate a station.
        
        Args:
            station_id: The station ID
            
        Returns:
            True if activated, False if not found
        """
        return self.update(station_id, is_active=True) is not None
    
    def deactivate_station(self, station_id: str) -> bool:
        """
        Deactivate a station.
        
        Args:
            station_id: The station ID
            
        Returns:
            True if deactivated, False if not found
        """
        return self.update(station_id, is_active=False) is not None
    
    def make_public(self, station_id: str) -> bool:
        """
        Make a station public.
        
        Args:
            station_id: The station ID
            
        Returns:
            True if made public, False if not found
        """
        return self.update(station_id, is_public=True) is not None
    
    def make_private(self, station_id: str) -> bool:
        """
        Make a station private.
        
        Args:
            station_id: The station ID
            
        Returns:
            True if made private, False if not found
        """
        return self.update(station_id, is_public=False) is not None
    
    def upgrade_station_level(self, station_id: str) -> Optional[CraftingStation]:
        """
        Upgrade a station's level.
        
        Args:
            station_id: The station ID
            
        Returns:
            The upgraded station if successful, None if not found
        """
        station = self.get_by_id(station_id)
        if station:
            return self.update(station_id, level=station.level + 1)
        return None
    
    def upgrade_station_upgrade_level(self, station_id: str) -> Optional[CraftingStation]:
        """
        Upgrade a station's upgrade level.
        
        Args:
            station_id: The station ID
            
        Returns:
            The upgraded station if successful, None if not found
        """
        station = self.get_by_id(station_id)
        if station:
            return self.update(station_id, upgrade_level=station.upgrade_level + 1)
        return None
    
    def set_capacity(self, station_id: str, capacity: int) -> bool:
        """
        Set the capacity of a station.
        
        Args:
            station_id: The station ID
            capacity: New capacity
            
        Returns:
            True if updated, False if not found
        """
        return self.update(station_id, capacity=max(1, capacity)) is not None
    
    def set_efficiency_bonus(self, station_id: str, efficiency_bonus: float) -> bool:
        """
        Set the efficiency bonus of a station.
        
        Args:
            station_id: The station ID
            efficiency_bonus: New efficiency bonus
            
        Returns:
            True if updated, False if not found
        """
        return self.update(station_id, efficiency_bonus=max(0.1, efficiency_bonus)) is not None
    
    def set_quality_bonus(self, station_id: str, quality_bonus: float) -> bool:
        """
        Set the quality bonus of a station.
        
        Args:
            station_id: The station ID
            quality_bonus: New quality bonus
            
        Returns:
            True if updated, False if not found
        """
        return self.update(station_id, quality_bonus=max(0.0, quality_bonus)) is not None
    
    def transfer_ownership(self, station_id: str, new_owner_id: str) -> bool:
        """
        Transfer ownership of a station.
        
        Args:
            station_id: The station ID
            new_owner_id: New owner's character ID
            
        Returns:
            True if transferred, False if not found
        """
        return self.update(station_id, owner_id=new_owner_id) is not None
    
    def relocate_station(self, station_id: str, new_location_id: str) -> bool:
        """
        Move a station to a new location.
        
        Args:
            station_id: The station ID
            new_location_id: New location ID
            
        Returns:
            True if relocated, False if not found
        """
        return self.update(station_id, location_id=new_location_id) is not None 