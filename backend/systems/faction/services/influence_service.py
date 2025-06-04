"""
Faction Influence Service - Pure Business Logic

This module provides business logic for managing faction influence,
separated from technical database and infrastructure concerns.
"""

from typing import List, Dict, Optional, Any, Tuple, Protocol
from datetime import datetime
from uuid import UUID


# Business Domain Models
class InfluenceChangeRequest:
    """Business domain model for influence change requests"""
    def __init__(self, 
                 faction_id: int,
                 delta: float,
                 reason: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        self.faction_id = faction_id
        self.delta = delta
        self.reason = reason
        self.metadata = metadata


class RegionInfluenceRequest:
    """Business domain model for region influence requests"""
    def __init__(self,
                 faction_id: int,
                 region_id: int,
                 influence: float,
                 contested: bool = False,
                 metadata: Optional[Dict[str, Any]] = None):
        self.faction_id = faction_id
        self.region_id = region_id
        self.influence = max(0.0, min(100.0, influence))  # Business rule: clamp to 0-100
        self.contested = contested
        self.metadata = metadata


class POIControlRequest:
    """Business domain model for POI control requests"""
    def __init__(self,
                 faction_id: int,
                 poi_id: int,
                 control_level: int,
                 details: Optional[Dict[str, Any]] = None):
        self.faction_id = faction_id
        self.poi_id = poi_id
        self.control_level = max(0, min(10, control_level))  # Business rule: clamp to 0-10
        self.details = details


# Business Logic Protocols (dependency injection)
class InfluenceDatabaseService(Protocol):
    """Protocol for influence data access"""
    
    def update_faction_influence(self, influence_update: Any) -> Tuple[float, float]:
        """Update faction's global influence"""
        ...
    
    def get_region_influence_data(self, region_id: int) -> List[Dict]:
        """Get region influence data"""
        ...
    
    def update_region_influence_data(self, region_update: Any) -> Dict:
        """Update region influence data"""
        ...
    
    def get_poi_control_data(self, poi_id: int) -> Dict:
        """Get POI control data"""
        ...
    
    def update_poi_control_data(self, poi_update: Any) -> Dict:
        """Update POI control data"""
        ...
    
    def get_all_active_factions(self) -> List[Any]:
        """Get all active factions"""
        ...


class FactionInfluenceBusinessService:
    """Business service for faction influence management - pure business rules"""
    
    def __init__(self, database_service: InfluenceDatabaseService):
        self.database_service = database_service

    def update_faction_influence(
        self,
        change_request: InfluenceChangeRequest,
        user_id: Optional[UUID] = None
    ) -> Tuple[float, float]:
        """
        Business logic: Update a faction's global influence value
        
        Business rules:
        - Influence is clamped between 0.0 and 100.0
        - Changes are logged with timestamps and reasons
        - User tracking is optional but recommended
        
        Returns:
            Tuple of (old_influence, new_influence)
        """
        # Business rule: Validate influence change
        if abs(change_request.delta) > 50.0:
            raise ValueError("Influence change cannot exceed 50 points in a single operation")
        
        # Add user tracking to metadata if provided
        metadata = change_request.metadata or {}
        if user_id:
            metadata['changed_by'] = str(user_id)
            metadata['change_timestamp'] = datetime.utcnow().isoformat()
        
        # Create database request with validated data
        from backend.infrastructure.database_services.faction_influence_database_service import InfluenceUpdate
        db_request = InfluenceUpdate(
            faction_id=change_request.faction_id,
            delta=change_request.delta,
            reason=change_request.reason,
            metadata=metadata
        )
        
        return self.database_service.update_faction_influence(db_request)

    def get_region_influence(self, region_id: int) -> List[Dict]:
        """
        Business logic: Get all factions with influence in a specific region
        
        Business rules:
        - Only return factions with positive influence
        - Results are sorted by influence (highest first)
        - Include additional faction metadata
        """
        # Business rule: Validate region ID
        if region_id <= 0:
            raise ValueError("Region ID must be positive")
        
        # Get raw data from database
        influence_data = self.database_service.get_region_influence_data(region_id)
        
        # Business rule: Calculate influence percentage and categorize
        total_influence = sum(data["influence"] for data in influence_data)
        
        # Enhance data with business calculations
        for data in influence_data:
            data["influence_percentage"] = (data["influence"] / total_influence * 100) if total_influence > 0 else 0
            data["dominance_level"] = self._categorize_influence_level(data["influence"])
            data["is_dominant"] = data["influence"] >= 50.0  # Business rule: 50+ influence = dominant
        
        return influence_data

    def update_region_influence(
        self,
        region_request: RegionInfluenceRequest,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Business logic: Update a faction's influence over a specific region
        
        Business rules:
        - Influence is automatically clamped to 0-100 range
        - High influence (>70) in contested regions triggers warnings
        - Changes are logged with user tracking
        """
        # Business rule: Validate contested region logic
        if region_request.contested and region_request.influence > 70.0:
            # High influence in contested region is unusual - log warning
            metadata = region_request.metadata or {}
            metadata['warning'] = 'High influence in contested region'
            metadata['review_recommended'] = True
            region_request.metadata = metadata
        
        # Add user tracking
        metadata = region_request.metadata or {}
        if user_id:
            metadata['updated_by'] = str(user_id)
            metadata['update_timestamp'] = datetime.utcnow().isoformat()
        
        # Create database request
        from backend.infrastructure.database_services.faction_influence_database_service import RegionInfluenceUpdate
        db_request = RegionInfluenceUpdate(
            faction_id=region_request.faction_id,
            region_id=region_request.region_id,
            influence=region_request.influence,
            contested=region_request.contested,
            metadata=metadata
        )
        
        result = self.database_service.update_region_influence_data(db_request)
        
        # Business rule: Add calculated fields
        result["dominance_level"] = self._categorize_influence_level(result["influence"])
        result["is_contested"] = result["contested"]
        
        return result

    def get_poi_control(self, poi_id: int) -> Dict:
        """
        Business logic: Get information about which factions control a POI
        
        Business rules:
        - Multiple factions can have control (contested)
        - Control levels determine actual authority
        - Zero control levels are filtered out
        """
        # Business rule: Validate POI ID
        if poi_id <= 0:
            raise ValueError("POI ID must be positive")
        
        # Get raw data from database
        control_data = self.database_service.get_poi_control_data(poi_id)
        
        # Business logic: Enhance with control analysis
        if control_data["controllers"]:
            # Business rule: Determine primary controller
            primary_controller = control_data["controllers"][0]  # Highest control level
            control_data["primary_controller"] = primary_controller
            
            # Business rule: Calculate control distribution
            total_control = sum(controller["control_level"] for controller in control_data["controllers"])
            for controller in control_data["controllers"]:
                controller["control_percentage"] = (controller["control_level"] / total_control * 100) if total_control > 0 else 0
                controller["control_category"] = self._categorize_control_level(controller["control_level"])
            
            # Business rule: Determine contest status
            control_data["contest_intensity"] = len(control_data["controllers"])
            control_data["is_stable"] = control_data["contest_intensity"] == 1 and primary_controller["control_level"] >= 7
        else:
            control_data["primary_controller"] = None
            control_data["contest_intensity"] = 0
            control_data["is_stable"] = False
        
        return control_data

    def update_poi_control(
        self,
        control_request: POIControlRequest,
        user_id: Optional[UUID] = None
    ) -> Dict:
        """
        Business logic: Update a faction's control over a POI
        
        Business rules:
        - Control level is clamped to 0-10 range
        - Changes above level 7 require justification
        - Zero control removes the faction from POI
        """
        # Business rule: Validate control level change
        if control_request.control_level > 7:
            details = control_request.details or {}
            if 'justification' not in details:
                details['warning'] = 'High control level without justification'
                details['review_required'] = True
            control_request.details = details
        
        # Add user tracking
        details = control_request.details or {}
        if user_id:
            details['updated_by'] = str(user_id)
            details['update_timestamp'] = datetime.utcnow().isoformat()
        
        # Create database request
        from backend.infrastructure.database_services.faction_influence_database_service import POIControlUpdate
        db_request = POIControlUpdate(
            faction_id=control_request.faction_id,
            poi_id=control_request.poi_id,
            control_level=control_request.control_level,
            details=details
        )
        
        result = self.database_service.update_poi_control_data(db_request)
        
        # Business rule: Add calculated fields
        result["control_category"] = self._categorize_control_level(result["control_level"])
        result["is_significant"] = result["control_level"] >= 5
        
        return result

    def analyze_faction_territorial_power(self, faction_id: int) -> Dict[str, Any]:
        """
        Business logic: Analyze a faction's overall territorial power and influence
        """
        # Get all active factions to compare against
        all_factions = self.database_service.get_all_active_factions()
        
        target_faction = None
        for faction in all_factions:
            if faction.id == faction_id:
                target_faction = faction
                break
        
        if not target_faction:
            raise ValueError(f"Faction {faction_id} not found")
        
        # Business rule: Calculate territorial metrics
        territory_count = len(target_faction.territory) if target_faction.territory else 0
        total_influence = 0.0
        contested_territories = 0
        poi_control_count = 0
        
        if target_faction.territory:
            for region_id, region_data in target_faction.territory.items():
                if isinstance(region_data, dict):
                    influence = region_data.get("influence", 0.0)
                    total_influence += influence
                    if region_data.get("contested", False):
                        contested_territories += 1
                else:
                    total_influence += float(region_data) if isinstance(region_data, (int, float, str)) else 0.0
            
            # Count POI controls
            poi_controls = target_faction.territory.get("poi_control", {})
            poi_control_count = len([poi for poi, data in poi_controls.items() 
                                   if (isinstance(data, dict) and data.get("control_level", 0) > 0) 
                                   or (not isinstance(data, dict) and int(data) > 0)])
        
        # Business rule: Calculate power metrics
        average_influence = total_influence / territory_count if territory_count > 0 else 0.0
        stability_score = (territory_count - contested_territories) / territory_count if territory_count > 0 else 1.0
        
        return {
            "faction_id": faction_id,
            "faction_name": target_faction.name,
            "territorial_metrics": {
                "territory_count": territory_count,
                "total_influence": round(total_influence, 2),
                "average_influence": round(average_influence, 2),
                "contested_territories": contested_territories,
                "poi_controls": poi_control_count
            },
            "power_analysis": {
                "stability_score": round(stability_score, 3),
                "territorial_power_level": self._categorize_territorial_power(territory_count, average_influence),
                "expansion_potential": self._assess_expansion_potential(target_faction),
                "strategic_position": self._assess_strategic_position(stability_score, contested_territories, poi_control_count)
            }
        }

    def _categorize_influence_level(self, influence: float) -> str:
        """Business rule: Categorize influence levels"""
        if influence >= 75.0:
            return "dominant"
        elif influence >= 50.0:
            return "strong"
        elif influence >= 25.0:
            return "moderate"
        elif influence > 0.0:
            return "minor"
        else:
            return "none"

    def _categorize_control_level(self, control_level: int) -> str:
        """Business rule: Categorize POI control levels"""
        if control_level >= 8:
            return "absolute"
        elif control_level >= 6:
            return "strong"
        elif control_level >= 4:
            return "moderate"
        elif control_level >= 2:
            return "weak"
        elif control_level > 0:
            return "minimal"
        else:
            return "none"

    def _categorize_territorial_power(self, territory_count: int, average_influence: float) -> str:
        """Business rule: Categorize overall territorial power"""
        power_score = (territory_count * 0.4) + (average_influence * 0.6)
        
        if power_score >= 60.0:
            return "empire"
        elif power_score >= 40.0:
            return "major_power"
        elif power_score >= 20.0:
            return "regional_power"
        elif power_score >= 10.0:
            return "minor_power"
        else:
            return "emerging"

    def _assess_expansion_potential(self, faction) -> str:
        """Business rule: Assess faction's expansion potential"""
        global_influence = getattr(faction, 'influence', 0)
        
        if global_influence >= 70.0:
            return "high"
        elif global_influence >= 40.0:
            return "moderate"
        elif global_influence >= 20.0:
            return "limited"
        else:
            return "minimal"

    def _assess_strategic_position(self, stability_score: float, contested_territories: int, poi_controls: int) -> str:
        """Business rule: Assess overall strategic position"""
        if stability_score >= 0.8 and poi_controls >= 3:
            return "excellent"
        elif stability_score >= 0.6 and poi_controls >= 2:
            return "strong"
        elif stability_score >= 0.4 or poi_controls >= 1:
            return "adequate"
        elif contested_territories > 2:
            return "vulnerable"
        else:
            return "weak"


def create_faction_influence_business_service(
    database_service: InfluenceDatabaseService
) -> FactionInfluenceBusinessService:
    """Factory function for creating faction influence business service"""
    return FactionInfluenceBusinessService(database_service) 