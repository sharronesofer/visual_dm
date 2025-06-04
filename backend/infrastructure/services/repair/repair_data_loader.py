"""
Repair Data Loader Service

Handles loading and caching of repair configuration data from JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from functools import lru_cache


logger = logging.getLogger(__name__)


class RepairDataLoader:
    """Service for loading repair configuration data from JSON files"""
    
    def __init__(self, data_root_path: Path = None):
        """
        Initialize with optional data root path.
        
        Args:
            data_root_path: Root path for data directory (defaults to project data directory)
        """
        if data_root_path is None:
            # Default to project data directory
            self.data_root = Path(__file__).parent.parent.parent.parent.parent / "data"
        else:
            self.data_root = data_root_path
        
        self.logger = logger
    
    @lru_cache(maxsize=1)
    def load_repair_stations(self) -> Dict[str, Any]:
        """
        Load repair stations configuration with caching.
        
        Returns:
            Dictionary of repair stations data
        """
        try:
            stations_path = self.data_root / "systems" / "repair" / "stations" / "repair_stations.json"
            with open(stations_path, 'r') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded repair stations from {stations_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load repair stations: {e}")
            return {}
    
    @lru_cache(maxsize=1)
    def load_building_materials(self) -> Dict[str, Any]:
        """
        Load building materials configuration with caching.
        
        Returns:
            Dictionary of building materials data
        """
        try:
            materials_path = self.data_root / "resources" / "building_materials.json"
            with open(materials_path, 'r') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded building materials from {materials_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load building materials: {e}")
            return {"materials": {}}
    
    @lru_cache(maxsize=1)
    def load_repair_formulas(self) -> Dict[str, Any]:
        """
        Load repair formulas configuration with caching.
        
        Returns:
            Dictionary of repair formulas data
        """
        try:
            formulas_path = self.data_root / "systems" / "repair" / "repair_formulas.json"
            with open(formulas_path, 'r') as f:
                data = json.load(f)
            
            self.logger.info(f"Loaded repair formulas from {formulas_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load repair formulas: {e}")
            # Fallback to default configuration
            return {
                "repair_success_rates": {"base_success_rate": 85.0},
                "material_calculations": {"base_quantity_multiplier": 5},
                "equipment_skill_mapping": {},
                "cost_formulas": {"time_cost_base": 2.0}
            }
    
    def reload_all_data(self) -> None:
        """
        Clear cache and reload all configuration data.
        Useful for development or when configuration files change.
        """
        # Clear the LRU cache
        self.load_repair_stations.cache_clear()
        self.load_building_materials.cache_clear()
        self.load_repair_formulas.cache_clear()
        
        # Reload data
        self.load_repair_stations()
        self.load_building_materials()
        self.load_repair_formulas()
        
        self.logger.info("Reloaded all repair configuration data")
    
    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all loaded configuration data.
        
        Returns:
            Dictionary containing all configuration data
        """
        return {
            "repair_stations": self.load_repair_stations(),
            "building_materials": self.load_building_materials(),
            "repair_formulas": self.load_repair_formulas()
        } 