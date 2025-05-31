"""
Station Service

This service handles crafting station management, availability, and configuration.
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

from backend.systems.crafting.models.station import CraftingStation

# Set up logging
logger = logging.getLogger(__name__)


class StationService:
    """
    Service for managing crafting stations, their availability, and configuration.
    """
    
    def __init__(self):
        """Initialize the station service."""
        self._logger = logger
        self._stations: Dict[str, CraftingStation] = {}
        
        # Load stations from data files
        self._load_stations_from_files()
        
    def _load_stations_from_files(self) -> None:
        """Load station data from JSON files."""
        try:
            # Get station directory from environment or use default
            station_dir = os.environ.get("STATION_DIR", "data/stations")
            station_path = Path(station_dir)
            
            if not station_path.exists():
                self._logger.warning(f"Station directory {station_dir} does not exist")
                return
                
            # Load all JSON files in the station directory
            for json_file in station_path.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        station_data = json.load(f)
                        
                    # Process each station in the file
                    for station_id, station_info in station_data.items():
                        station = self._construct_station(station_id, station_info)
                        if station:
                            self._stations[station_id] = station
                            
                except json.JSONDecodeError as e:
                    self._logger.error(f"Invalid JSON in {json_file}: {e}")
                except Exception as e:
                    self._logger.error(f"Error loading stations from {json_file}: {e}")
                    
        except Exception as e:
            self._logger.error(f"Error loading station files: {e}")
            
    def _construct_station(self, station_id: str, station_info: Dict[str, Any]) -> Optional[CraftingStation]:
        """
        Construct a CraftingStation from station data.
        
        Args:
            station_id: ID of the station
            station_info: Station configuration data
            
        Returns:
            CraftingStation object or None if construction fails
        """
        try:
            station = CraftingStation(
                id=station_id,
                name=station_info.get("name", station_id),
                description=station_info.get("description", ""),
                station_type=station_info.get("type", "workshop"),
                level=station_info.get("level", 1),
                metadata=station_info.get("metadata", {})
            )
            return station
            
        except Exception as e:
            self._logger.error(f"Error constructing station {station_id}: {e}")
            return None
            
    def add_station(self, station: CraftingStation) -> None:
        """
        Add a station to the system.
        
        Args:
            station: CraftingStation to add
        """
        self._stations[station.id] = station
        self._logger.info(f"Added station {station.id}: {station.name}")
        
    def remove_station(self, station_id: str) -> bool:
        """
        Remove a station from the system.
        
        Args:
            station_id: ID of the station to remove
            
        Returns:
            True if station was removed, False if not found
        """
        if station_id in self._stations:
            removed_station = self._stations.pop(station_id)
            self._logger.info(f"Removed station {station_id}: {removed_station.name}")
            return True
        else:
            self._logger.warning(f"Station {station_id} not found for removal")
            return False
            
    def get_station(self, station_id: str) -> Optional[CraftingStation]:
        """
        Get a station by ID.
        
        Args:
            station_id: ID of the station to retrieve
            
        Returns:
            CraftingStation or None if not found
        """
        return self._stations.get(station_id)
        
    def get_all_stations(self) -> List[CraftingStation]:
        """
        Get all stations in the system.
        
        Returns:
            List of all CraftingStation objects
        """
        return list(self._stations.values())
        
    def get_available_stations(self, location_id: str) -> List[CraftingStation]:
        """
        Get stations available at a specific location.
        
        Args:
            location_id: ID of the location to check
            
        Returns:
            List of available stations (placeholder returns all)
        """
        # Placeholder implementation - would filter by location
        return self.get_all_stations()
        
    def use_station(self, character_id: str, station_id: str) -> Dict[str, Any]:
        """
        Have a character use a crafting station.
        
        Args:
            character_id: ID of the character
            station_id: ID of the station to use
            
        Returns:
            Result of station usage
        """
        station = self.get_station(station_id)
        if not station:
            return {
                "success": False,
                "error": f"Station {station_id} not found"
            }
            
        # Placeholder implementation
        return {
            "success": True,
            "character_id": character_id,
            "station_id": station_id,
            "station_name": station.name
        }
        
    def upgrade_station(self, station_id: str, upgrade_type: str) -> Dict[str, Any]:
        """
        Upgrade a crafting station.
        
        Args:
            station_id: ID of the station to upgrade
            upgrade_type: Type of upgrade to apply
            
        Returns:
            Result of upgrade attempt
        """
        station = self.get_station(station_id)
        if not station:
            return {
                "success": False,
                "error": f"Station {station_id} not found"
            }
            
        # Placeholder implementation
        return {
            "success": True,
            "station_id": station_id,
            "upgrade_type": upgrade_type,
            "new_level": station.level + 1
        }
        
    def get_station_capacity(self, station_id: str) -> int:
        """
        Get the capacity/usage limit of a station.
        
        Args:
            station_id: ID of the station
            
        Returns:
            Station capacity (placeholder returns 1)
        """
        station = self.get_station(station_id)
        if station:
            return station.metadata.get("capacity", 1)
        return 0
        
    def reserve_station(self, character_id: str, station_id: str, duration: int) -> Dict[str, Any]:
        """
        Reserve a station for a character.
        
        Args:
            character_id: ID of the character
            station_id: ID of the station to reserve
            duration: Duration of reservation in minutes
            
        Returns:
            Reservation result
        """
        station = self.get_station(station_id)
        if not station:
            return {
                "success": False,
                "error": f"Station {station_id} not found"
            }
            
        # Placeholder implementation
        return {
            "success": True,
            "character_id": character_id,
            "station_id": station_id,
            "duration": duration,
            "reservation_id": f"res_{character_id}_{station_id}"
        } 