"""
Faction Influence Database Service - Technical Infrastructure

This service handles all database operations for faction influence management,
separating technical database concerns from business logic.
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.systems.faction.models.faction import Faction


class InfluenceUpdate(BaseModel):
    """Pydantic model for influence updates"""
    faction_id: int
    delta: float
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RegionInfluenceUpdate(BaseModel):
    """Pydantic model for region influence updates"""
    faction_id: int
    region_id: int
    influence: float = Field(ge=0.0, le=100.0)
    contested: bool = False
    metadata: Optional[Dict[str, Any]] = None


class POIControlUpdate(BaseModel):
    """Pydantic model for POI control updates"""
    faction_id: int
    poi_id: int
    control_level: int
    details: Optional[Dict[str, Any]] = None


class FactionInfluenceDatabaseService:
    """Database service for faction influence operations"""
    
    def __init__(self, db_session: Session):
        """Initialize with database session"""
        self.db_session = db_session

    def get_faction_by_id(self, faction_id: int) -> Optional[Faction]:
        """Get faction by ID from database"""
        return self.db_session.query(Faction).filter(Faction.id == faction_id).first()

    def update_faction_influence(
        self, 
        influence_update: InfluenceUpdate
    ) -> Tuple[float, float]:
        """
        Update a faction's global influence value in database
        
        Returns:
            Tuple of (old_influence, new_influence)
            
        Raises:
            ValueError: If faction doesn't exist
        """
        # Check if faction exists
        faction = self.get_faction_by_id(influence_update.faction_id)
        if not faction:
            raise ValueError(f"Faction {influence_update.faction_id} not found")
            
        # Update influence with bounds checking
        old_influence = faction.influence
        new_influence = max(0.0, min(100.0, old_influence + influence_update.delta))
        faction.influence = new_influence
        
        # Record influence change in state
        if "influence_history" not in faction.state:
            faction.state["influence_history"] = []
            
        event = {
            "type": "influence_changed",
            "old_influence": old_influence,
            "new_influence": new_influence,
            "delta": influence_update.delta,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if influence_update.reason:
            event["reason"] = influence_update.reason
            
        if influence_update.metadata:
            event["metadata"] = influence_update.metadata
            
        faction.state["influence_history"].append(event)
        faction.updated_at = datetime.utcnow()
        
        self.db_session.commit()
        return old_influence, new_influence

    def get_region_influence_data(self, region_id: int) -> List[Dict]:
        """
        Get all factions with influence in a specific region from database
        
        Returns:
            List of dicts with faction influence details
        """
        # Get all active factions with territory data
        factions = self.db_session.query(Faction).filter(Faction.is_active == True).all()
        
        # Collect influence data
        influence_data = []
        for faction in factions:
            # Check if faction has influence in this region
            if str(region_id) in faction.territory:
                region_influence = faction.territory[str(region_id)]
                
                # Handle different territory data formats
                if isinstance(region_influence, dict) and "influence" in region_influence:
                    influence = region_influence["influence"]
                else:
                    # If not a dict, assume the value itself is the influence
                    influence = float(region_influence) if isinstance(region_influence, (int, float, str)) else 0.0
                    
                if influence > 0:
                    influence_data.append({
                        "faction_id": faction.id,
                        "faction_name": faction.name,
                        "influence": influence,
                        "additional_data": region_influence if isinstance(region_influence, dict) else {}
                    })
        
        # Sort by influence (highest first)
        return sorted(influence_data, key=lambda x: x["influence"], reverse=True)

    def update_region_influence_data(
        self, 
        region_update: RegionInfluenceUpdate
    ) -> Dict:
        """
        Update a faction's influence over a specific region in database
        
        Returns:
            Dict with updated territory data
            
        Raises:
            ValueError: If faction doesn't exist
        """
        # Check if faction exists
        faction = self.get_faction_by_id(region_update.faction_id)
        if not faction:
            raise ValueError(f"Faction {region_update.faction_id} not found")
            
        # Ensure territory field exists
        if faction.territory is None:
            faction.territory = {}
            
        # Get old data
        region_id_str = str(region_update.region_id)
        old_data = faction.territory.get(region_id_str, {"influence": 0.0})
        
        # Handle different territory data formats
        if not isinstance(old_data, dict):
            old_data = {"influence": float(old_data) if isinstance(old_data, (int, float, str)) else 0.0}
            
        # Create updated data
        region_data = {
            "influence": region_update.influence,
            "contested": region_update.contested,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Merge with metadata
        if region_update.metadata:
            region_data.update(region_update.metadata)
            
        # Keep any other existing fields that weren't updated
        for key, value in old_data.items():
            if key not in region_data:
                region_data[key] = value
                
        # Store in territory
        faction.territory[region_id_str] = region_data
        faction.updated_at = datetime.utcnow()
        
        self.db_session.commit()
        return region_data

    def get_poi_control_data(self, poi_id: int) -> Dict:
        """
        Get information about which factions control a POI from database
        
        Returns:
            Dict with POI control information
        """
        # Get all active factions with territory data
        factions = self.db_session.query(Faction).filter(Faction.is_active == True).all()
        
        # Check for POI control data
        control_data = {
            "poi_id": poi_id,
            "controllers": [],
            "contested": False,
            "last_updated": None
        }
        
        for faction in factions:
            # Check faction's territory for POI data
            if faction.territory and "poi_control" in faction.territory:
                poi_control = faction.territory["poi_control"]
                if str(poi_id) in poi_control:
                    poi_data = poi_control[str(poi_id)]
                    
                    # Handle different POI data formats
                    if isinstance(poi_data, dict):
                        control_level = poi_data.get("control_level", 0)
                        details = poi_data.get("details", {})
                    else:
                        control_level = int(poi_data) if isinstance(poi_data, (int, float, str)) else 0
                        details = {}
                    
                    if control_level > 0:
                        control_data["controllers"].append({
                            "faction_id": faction.id,
                            "faction_name": faction.name,
                            "control_level": control_level,
                            "details": details
                        })
        
        # Determine if contested (multiple controllers)
        control_data["contested"] = len(control_data["controllers"]) > 1
        
        # Sort by control level (highest first)
        control_data["controllers"] = sorted(
            control_data["controllers"], 
            key=lambda x: x["control_level"], 
            reverse=True
        )
        
        return control_data

    def update_poi_control_data(
        self, 
        poi_update: POIControlUpdate
    ) -> Dict:
        """
        Update a faction's control over a POI in database
        
        Returns:
            Dict with updated POI control data
            
        Raises:
            ValueError: If faction doesn't exist
        """
        # Check if faction exists
        faction = self.get_faction_by_id(poi_update.faction_id)
        if not faction:
            raise ValueError(f"Faction {poi_update.faction_id} not found")
            
        # Ensure territory and poi_control fields exist
        if faction.territory is None:
            faction.territory = {}
        if "poi_control" not in faction.territory:
            faction.territory["poi_control"] = {}
            
        # Create POI control data
        poi_data = {
            "control_level": max(0, min(10, poi_update.control_level)),  # Clamp to 0-10
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Merge with details
        if poi_update.details:
            poi_data["details"] = poi_update.details
            
        # Store POI control data
        faction.territory["poi_control"][str(poi_update.poi_id)] = poi_data
        faction.updated_at = datetime.utcnow()
        
        self.db_session.commit()
        return poi_data

    def get_all_active_factions(self) -> List[Faction]:
        """Get all active factions from database"""
        return self.db_session.query(Faction).filter(Faction.is_active == True).all() 