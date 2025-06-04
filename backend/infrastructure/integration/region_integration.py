"""
Region Integration Service - Infrastructure Layer

Concrete implementation of region system integration for cross-system communication.
Provides region data, biome information, infrastructure data, and travel calculations
to other systems without creating direct dependencies.
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Import from infrastructure database layer (not business layer to avoid circular deps)
try:
    from backend.infrastructure.database.region.models import RegionEntity, RegionPOI
    from backend.infrastructure.database.region.enums import DangerLevel, POIType
except ImportError:
    # Fallback if region models not available
    RegionEntity = None
    RegionPOI = None
    DangerLevel = None
    POIType = None

from backend.systems.economy.services.integration_interfaces import RegionSystemInterface

logger = logging.getLogger(__name__)


class ConcreteRegionSystemInterface(RegionSystemInterface):
    """Concrete implementation of region system interface"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_region_data(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get basic region data including danger level and biome"""
        try:
            if not RegionEntity:
                logger.warning("Region database models not available, using defaults")
                return {
                    'region_id': region_id,
                    'name': f'Region {region_id}',
                    'danger_level': 3,  # Moderate default
                    'biome_type': 'temperate',
                    'population': 1000
                }
            
            region = self.db.query(RegionEntity).filter(
                RegionEntity.id == region_id
            ).first()
            
            if region:
                return {
                    'region_id': region.id,
                    'name': region.name,
                    'danger_level': region.danger_level,
                    'biome_type': region.biome_type,
                    'population': getattr(region, 'population', 1000),
                    'climate': getattr(region, 'climate', 'temperate'),
                    'terrain': getattr(region, 'terrain', 'plains'),
                    'wealth_level': getattr(region, 'wealth_level', 'moderate'),
                    'government_type': getattr(region, 'government_type', 'feudal'),
                    'description': getattr(region, 'description', ''),
                    'metadata': getattr(region, 'metadata', {})
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting region data for {region_id}: {e}")
            return None
    
    def get_region_infrastructure(self, region_id: str) -> Optional[Dict[str, Any]]:
        """Get region infrastructure information including POIs"""
        try:
            if not RegionPOI or not POIType:
                logger.warning("Region POI models not available, using defaults")
                return {
                    'region_id': region_id,
                    'has_roads': True,
                    'has_waterways': False,
                    'poi_types': ['market', 'inn'],
                    'infrastructure_level': 'moderate'
                }
            
            # Get POIs for the region
            pois = self.db.query(RegionPOI).filter(
                RegionPOI.region_id == region_id
            ).all()
            
            infrastructure_data = {
                'region_id': region_id,
                'has_roads': False,
                'has_waterways': False,
                'poi_types': [],
                'infrastructure_level': 'poor',
                'pois': []
            }
            
            road_related_pois = {'crossroads', 'trading_post', 'bridge', 'gate'}
            waterway_related_pois = {'bridge', 'dock', 'waterway', 'ferry'}
            
            for poi in pois:
                poi_type = poi.poi_type.lower() if hasattr(poi, 'poi_type') else 'unknown'
                infrastructure_data['poi_types'].append(poi_type)
                
                # Check for roads
                if poi_type in road_related_pois:
                    infrastructure_data['has_roads'] = True
                
                # Check for waterways
                if poi_type in waterway_related_pois:
                    infrastructure_data['has_waterways'] = True
                
                # Add POI details
                infrastructure_data['pois'].append({
                    'id': poi.id,
                    'name': getattr(poi, 'name', f'POI {poi.id}'),
                    'type': poi_type,
                    'description': getattr(poi, 'description', ''),
                    'coordinates': getattr(poi, 'coordinates', None)
                })
            
            # Determine infrastructure level
            poi_count = len(pois)
            if poi_count >= 5 and infrastructure_data['has_roads'] and infrastructure_data['has_waterways']:
                infrastructure_data['infrastructure_level'] = 'excellent'
            elif poi_count >= 3 and (infrastructure_data['has_roads'] or infrastructure_data['has_waterways']):
                infrastructure_data['infrastructure_level'] = 'good'
            elif poi_count >= 2:
                infrastructure_data['infrastructure_level'] = 'moderate'
            elif poi_count >= 1:
                infrastructure_data['infrastructure_level'] = 'basic'
            
            return infrastructure_data
            
        except Exception as e:
            logger.error(f"Error getting infrastructure for region {region_id}: {e}")
            return None
    
    def get_nearby_regions(self, region_id: str, max_distance: int = 3) -> List[str]:
        """Get list of nearby region IDs within max_distance"""
        try:
            if not RegionEntity:
                logger.warning("Region database models not available, using mock nearby regions")
                # Return mock nearby regions
                region_num = int(region_id) if region_id.isdigit() else 1
                return [str(region_num + i) for i in range(-max_distance, max_distance + 1) 
                       if region_num + i > 0 and region_num + i != region_num]
            
            # In a real implementation, this would calculate based on coordinates or adjacency
            # For now, we'll use a simple approach based on region metadata or adjacency lists
            base_region = self.db.query(RegionEntity).filter(
                RegionEntity.id == region_id
            ).first()
            
            if not base_region:
                return []
            
            # If regions have coordinates, calculate distance
            if hasattr(base_region, 'coordinates') and base_region.coordinates:
                base_coords = base_region.coordinates
                nearby_regions = []
                
                # Get all regions and calculate distances
                all_regions = self.db.query(RegionEntity).all()
                
                for region in all_regions:
                    if region.id == region_id:
                        continue
                    
                    if hasattr(region, 'coordinates') and region.coordinates:
                        # Simple Euclidean distance calculation
                        distance = ((base_coords[0] - region.coordinates[0]) ** 2 + 
                                  (base_coords[1] - region.coordinates[1]) ** 2) ** 0.5
                        
                        if distance <= max_distance:
                            nearby_regions.append(region.id)
                
                return nearby_regions
            
            # Fallback: use adjacency metadata if available
            metadata = getattr(base_region, 'metadata', {})
            adjacent_regions = metadata.get('adjacent_regions', [])
            
            # For max_distance > 1, we'd need to recursively find regions
            if max_distance == 1:
                return adjacent_regions
            
            # Simple expansion for max_distance > 1
            all_nearby = set(adjacent_regions)
            current_level = set(adjacent_regions)
            
            for distance in range(2, max_distance + 1):
                next_level = set()
                for region in current_level:
                    region_entity = self.db.query(RegionEntity).filter(
                        RegionEntity.id == region
                    ).first()
                    
                    if region_entity:
                        region_metadata = getattr(region_entity, 'metadata', {})
                        next_adjacent = region_metadata.get('adjacent_regions', [])
                        next_level.update(next_adjacent)
                
                # Remove already found regions and the base region
                next_level.discard(region_id)
                next_level -= all_nearby
                
                all_nearby.update(next_level)
                current_level = next_level
            
            return list(all_nearby)
            
        except Exception as e:
            logger.error(f"Error getting nearby regions for {region_id}: {e}")
            return []
    
    def calculate_travel_time(self, from_region: str, to_region: str) -> float:
        """Calculate travel time between regions in hours"""
        try:
            if not RegionEntity:
                # Mock travel time calculation
                distance = abs(int(from_region) - int(to_region)) if from_region.isdigit() and to_region.isdigit() else 1
                return distance * 24.0  # 24 hours per region distance
            
            from_region_entity = self.db.query(RegionEntity).filter(
                RegionEntity.id == from_region
            ).first()
            
            to_region_entity = self.db.query(RegionEntity).filter(
                RegionEntity.id == to_region
            ).first()
            
            if not from_region_entity or not to_region_entity:
                return 48.0  # Default 2 days travel time
            
            # Calculate based on coordinates if available
            if (hasattr(from_region_entity, 'coordinates') and from_region_entity.coordinates and
                hasattr(to_region_entity, 'coordinates') and to_region_entity.coordinates):
                
                from_coords = from_region_entity.coordinates
                to_coords = to_region_entity.coordinates
                
                # Euclidean distance
                distance = ((from_coords[0] - to_coords[0]) ** 2 + 
                           (from_coords[1] - to_coords[1]) ** 2) ** 0.5
                
                # Base travel speed: 1 coordinate unit = 12 hours
                base_travel_time = distance * 12.0
                
                # Adjust based on terrain and infrastructure
                from_infrastructure = self.get_region_infrastructure(from_region)
                to_infrastructure = self.get_region_infrastructure(to_region)
                
                speed_modifier = 1.0
                
                # Good infrastructure reduces travel time
                if (from_infrastructure and from_infrastructure.get('has_roads') and
                    to_infrastructure and to_infrastructure.get('has_roads')):
                    speed_modifier *= 0.7  # 30% faster with roads
                
                # Waterways can also help
                if (from_infrastructure and from_infrastructure.get('has_waterways') and
                    to_infrastructure and to_infrastructure.get('has_waterways')):
                    speed_modifier *= 0.8  # 20% faster with waterways
                
                # Terrain difficulty (from metadata)
                from_metadata = getattr(from_region_entity, 'metadata', {})
                to_metadata = getattr(to_region_entity, 'metadata', {})
                
                terrain_difficulty = max(
                    from_metadata.get('terrain_difficulty', 1.0),
                    to_metadata.get('terrain_difficulty', 1.0)
                )
                speed_modifier *= terrain_difficulty
                
                return base_travel_time * speed_modifier
            
            # Fallback: use region adjacency
            from_metadata = getattr(from_region_entity, 'metadata', {})
            adjacent_regions = from_metadata.get('adjacent_regions', [])
            
            if to_region in adjacent_regions:
                return 12.0  # 12 hours to adjacent region
            else:
                # Use simple distance approximation
                distance = self._calculate_region_distance(from_region, to_region)
                return distance * 12.0
            
        except Exception as e:
            logger.error(f"Error calculating travel time from {from_region} to {to_region}: {e}")
            return 24.0  # Default 1 day travel time
    
    def _calculate_region_distance(self, from_region: str, to_region: str) -> int:
        """Simple distance calculation based on region IDs"""
        try:
            from_num = int(from_region) if from_region.isdigit() else 1
            to_num = int(to_region) if to_region.isdigit() else 1
            return abs(from_num - to_num)
        except:
            return 1
    
    def get_region_type(self, region_id: str) -> str:
        """Get region type for economic calculations"""
        try:
            region_data = self.get_region_data(region_id)
            if not region_data:
                return "neutral_regions"
            
            # Determine region type based on wealth and characteristics
            wealth_level = region_data.get('wealth_level', 'moderate')
            population = region_data.get('population', 1000)
            biome_type = region_data.get('biome_type', 'temperate')
            
            # High wealth and population = wealthy region
            if wealth_level in ['wealthy', 'rich'] or population > 5000:
                return "wealthy_regions"
            
            # Low wealth and population = poor region
            if wealth_level in ['poor', 'destitute'] or population < 500:
                return "poor_regions"
            
            # Biome-specific classifications
            if biome_type in ['desert', 'arctic', 'mountain']:
                return "harsh_regions"
            
            if biome_type in ['coastal', 'river']:
                return "coastal_regions"
            
            if biome_type in ['forest', 'plains']:
                return "agricultural_regions"
            
            if population > 2000:
                return "urban_centers"
            
            return "neutral_regions"
            
        except Exception as e:
            logger.error(f"Error getting region type for {region_id}: {e}")
            return "neutral_regions"


class RegionIntegrationService:
    """Service for managing region integrations across systems"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.region_interface = ConcreteRegionSystemInterface(db_session)
    
    def get_interface(self) -> RegionSystemInterface:
        """Get the region system interface"""
        return self.region_interface
    
    def update_region_economic_data(self, region_id: str, economic_data: Dict[str, Any]) -> bool:
        """Update region with economic impact data"""
        try:
            if not RegionEntity:
                logger.warning("Region database models not available for economic updates")
                return False
            
            region = self.db.query(RegionEntity).filter(
                RegionEntity.id == region_id
            ).first()
            
            if region:
                # Update metadata with economic information
                metadata = getattr(region, 'metadata', {}) or {}
                metadata.update({
                    'economic_data': economic_data,
                    'last_economic_update': economic_data.get('timestamp')
                })
                
                if hasattr(region, 'metadata'):
                    region.metadata = metadata
                
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating region economic data: {e}")
            return False
    
    def get_regions_by_biome(self, biome_type: str) -> List[str]:
        """Get all regions of a specific biome type"""
        try:
            if not RegionEntity:
                return []
            
            regions = self.db.query(RegionEntity).filter(
                RegionEntity.biome_type == biome_type
            ).all()
            
            return [region.id for region in regions]
            
        except Exception as e:
            logger.error(f"Error getting regions by biome {biome_type}: {e}")
            return []
    
    def get_regions_with_infrastructure(self, infrastructure_type: str) -> List[str]:
        """Get regions that have specific infrastructure"""
        try:
            if not RegionPOI:
                return []
            
            # Get regions that have POIs of the specified type
            regions_with_infrastructure = self.db.query(RegionPOI.region_id).filter(
                RegionPOI.poi_type.ilike(f'%{infrastructure_type}%')
            ).distinct().all()
            
            return [result[0] for result in regions_with_infrastructure]
            
        except Exception as e:
            logger.error(f"Error getting regions with infrastructure {infrastructure_type}: {e}")
            return []


def create_region_integration_service(db_session: Session) -> RegionIntegrationService:
    """Factory function to create region integration service"""
    return RegionIntegrationService(db_session) 