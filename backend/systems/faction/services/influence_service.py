"""
Service layer for managing faction influence.

This module provides the FactionInfluenceService class for tracking and
managing faction influence on regions, points of interest, and other entities.
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.faction.models.faction import Faction
from backend.systems.faction.services.faction_service import FactionNotFoundError


class FactionInfluenceService:
    """Service for managing faction influence on various entities."""
    
    @staticmethod
    def update_faction_influence(
        db: Session,
        faction_id: int,
        delta: float,
        reason: str = None,
        metadata: Dict[str, Any] = None
    ) -> Tuple[float, float]:
        """
        Update a faction's global influence value.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            delta: Change in influence value
            reason: Reason for the influence change (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Tuple of (old_influence, new_influence)
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        # Update influence
        old_influence = faction.influence
        new_influence = max(0.0, min(100.0, old_influence + delta))
        faction.influence = new_influence
        
        # Record influence change
        if "influence_history" not in faction.state:
            faction.state["influence_history"] = []
            
        event = {
            "type": "influence_changed",
            "old_influence": old_influence,
            "new_influence": new_influence,
            "delta": delta,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if reason:
            event["reason"] = reason
            
        if metadata:
            event["metadata"] = metadata
            
        faction.state["influence_history"].append(event)
        faction.updated_at = datetime.utcnow()
        
        db.commit()
        return old_influence, new_influence
    
    @staticmethod
    def get_region_influence(
        db: Session,
        region_id: int
    ) -> List[Dict]:
        """
        Get all factions with influence in a specific region.
        
        Args:
            db: Database session
            region_id: ID of the region
            
        Returns:
            List of dicts with faction influence details
        """
        # Get all factions with territory data
        factions = db.query(Faction).filter(Faction.is_active == True).all()
        
        # Collect influence data
        influence_data = []
        for faction in factions:
            # Check if faction has influence in this region
            if str(region_id) in faction.territory:
                region_influence = faction.territory[str(region_id)]
                
                # Check if region_influence is a dict with influence value
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
    
    @staticmethod
    def update_region_influence(
        db: Session,
        faction_id: int,
        region_id: int,
        influence: float,
        contested: bool = False,
        metadata: Dict[str, Any] = None
    ) -> Dict:
        """
        Update a faction's influence over a specific region.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            region_id: ID of the region
            influence: New influence value (0-100)
            contested: Whether the region is contested with other factions
            metadata: Additional metadata (optional)
            
        Returns:
            Dict with updated territory data
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        # Ensure territory field exists
        if faction.territory is None:
            faction.territory = {}
            
        # Get old data
        region_id_str = str(region_id)
        old_data = faction.territory.get(region_id_str, {"influence": 0.0})
        
        # If old_data is not a dict, convert it
        if not isinstance(old_data, dict):
            old_data = {"influence": float(old_data) if isinstance(old_data, (int, float, str)) else 0.0}
            
        # Update data
        region_data = {
            "influence": max(0.0, min(100.0, influence)),
            "contested": contested,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Merge with metadata
        if metadata:
            region_data.update(metadata)
            
        # Keep any other existing fields that weren't updated
        for key, value in old_data.items():
            if key not in region_data:
                region_data[key] = value
                
        # Store in territory
        faction.territory[region_id_str] = region_data
        faction.updated_at = datetime.utcnow()
        
        db.commit()
        return region_data
    
    @staticmethod
    def get_poi_control(
        db: Session,
        poi_id: int
    ) -> Dict:
        """
        Get information about which factions control a POI.
        
        Args:
            db: Database session
            poi_id: ID of the POI
            
        Returns:
            Dict with POI control information
        """
        # Get all factions with territory data
        factions = db.query(Faction).filter(Faction.is_active == True).all()
        
        # Data structure to hold control information
        control_info = {
            "poi_id": poi_id,
            "controlling_factions": [],
            "contested": False,
            "total_control_points": 0
        }
        
        # Collect control data
        for faction in factions:
            # Check if faction has this POI as a headquarters
            is_headquarters = faction.headquarters_id == poi_id
            
            # Check if faction has explicit control data for this POI
            poi_control = None
            for resource_id, resource_data in faction.resources.items():
                if resource_id == f"poi_{poi_id}" or (isinstance(resource_data, dict) and resource_data.get("poi_id") == poi_id):
                    poi_control = resource_data
                    break
                    
            # If control data found, add to controlling factions
            if poi_control or is_headquarters:
                control_level = 0
                
                if isinstance(poi_control, dict):
                    control_level = poi_control.get("control_level", 0)
                elif isinstance(poi_control, (int, float)):
                    control_level = float(poi_control)
                    
                # HQ gives automatic control
                if is_headquarters:
                    control_level = max(control_level, 8)  # High control for headquarters
                    
                if control_level > 0:
                    faction_control = {
                        "faction_id": faction.id,
                        "faction_name": faction.name,
                        "control_level": control_level,
                        "is_headquarters": is_headquarters
                    }
                    
                    if isinstance(poi_control, dict) and "control_details" in poi_control:
                        faction_control["details"] = poi_control["control_details"]
                        
                    control_info["controlling_factions"].append(faction_control)
                    control_info["total_control_points"] += control_level
                
        # Sort by control level (highest first)
        control_info["controlling_factions"] = sorted(
            control_info["controlling_factions"],
            key=lambda x: (x["control_level"], x["is_headquarters"]),
            reverse=True
        )
        
        # Determine if contested (more than one faction with substantial control)
        if len(control_info["controlling_factions"]) > 1:
            top_control = control_info["controlling_factions"][0]["control_level"]
            second_control = control_info["controlling_factions"][1]["control_level"]
            
            # Consider contested if second faction has at least 50% of top faction's control
            if second_control >= top_control * 0.5:
                control_info["contested"] = True
                
        return control_info
    
    @staticmethod
    def update_poi_control(
        db: Session,
        faction_id: int,
        poi_id: int,
        control_level: int,
        details: Dict[str, Any] = None
    ) -> Dict:
        """
        Update a faction's control over a POI.
        
        Args:
            db: Database session
            faction_id: ID of the faction
            poi_id: ID of the POI
            control_level: Level of control (0-10)
            details: Additional control details (optional)
            
        Returns:
            Dict with updated control data
            
        Raises:
            FactionNotFoundError: If faction doesn't exist
        """
        # Check if faction exists
        faction = db.query(Faction).filter(Faction.id == faction_id).first()
        if not faction:
            raise FactionNotFoundError(f"Faction {faction_id} not found")
            
        # Ensure resources field exists
        if faction.resources is None:
            faction.resources = {}
            
        # POI resource key
        poi_key = f"poi_{poi_id}"
        
        # Get old data
        old_data = faction.resources.get(poi_key, {"control_level": 0})
        
        # If old_data is not a dict, convert it
        if not isinstance(old_data, dict):
            old_data = {"control_level": int(old_data) if isinstance(old_data, (int, float, str)) else 0}
            
        # Update data
        control_data = {
            "poi_id": poi_id,
            "control_level": max(0, min(10, control_level)),  # Ensure between 0-10
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add details if provided
        if details:
            control_data["control_details"] = details
            
        # Keep any other existing fields that weren't updated
        for key, value in old_data.items():
            if key not in control_data and key != "control_details":
                control_data[key] = value
                
        # Store in resources
        faction.resources[poi_key] = control_data
        faction.updated_at = datetime.utcnow()
        
        db.commit()
        return control_data 