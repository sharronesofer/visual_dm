"""
Metropolitan Spread Service for POI System

Manages urban expansion, suburban development, and metropolitan area growth
patterns for cities and large settlements.
"""

from typing import Dict, List, Optional, Tuple, Set, Any
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import math
import logging
from datetime import datetime, timedelta
import random

from backend.infrastructure.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db_session
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class UrbanSize(str, Enum):
    """Classification of urban area sizes"""
    HAMLET = "hamlet"         # 0-100 population
    VILLAGE = "village"       # 100-1,000 population
    TOWN = "town"            # 1,000-10,000 population
    CITY = "city"            # 10,000-100,000 population
    METROPOLIS = "metropolis" # 100,000+ population


class ExpansionDirection(str, Enum):
    """Directions for hex expansion"""
    NORTH = "north"
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
    SOUTH = "south"
    SOUTHWEST = "southwest"
    NORTHWEST = "northwest"


@dataclass
class HexCoordinate:
    """Represents a hexagonal grid coordinate"""
    q: int  # Column
    r: int  # Row
    s: int  # Diagonal (q + r + s = 0)
    
    def __post_init__(self):
        if self.q + self.r + self.s != 0:
            raise ValueError("Invalid hex coordinate: q + r + s must equal 0")
    
    def distance(self, other: 'HexCoordinate') -> int:
        """Calculate distance between two hex coordinates"""
        return (abs(self.q - other.q) + abs(self.q + self.r - other.q - other.r) + abs(self.r - other.r)) // 2
    
    def neighbors(self) -> List['HexCoordinate']:
        """Get all neighboring hex coordinates"""
        directions = [
            (1, -1, 0), (1, 0, -1), (0, 1, -1),
            (-1, 1, 0), (-1, 0, 1), (0, -1, 1)
        ]
        return [HexCoordinate(self.q + dq, self.r + dr, self.s + ds) for dq, dr, ds in directions]


@dataclass
class MetropolitanArea:
    """Represents a metropolitan area with its constituent POIs"""
    center_poi_id: UUID
    constituent_poi_ids: Set[UUID]
    total_population: int
    urban_size: UrbanSize
    expansion_radius: int
    claimed_hexes: Set[HexCoordinate]
    economic_strength: float
    growth_rate: float
    
    def can_expand(self) -> bool:
        """Check if the metropolitan area can expand"""
        return (
            self.total_population > self.get_expansion_threshold() and
            self.economic_strength > 0.5 and
            self.growth_rate > 0.01
        )
    
    def get_expansion_threshold(self) -> int:
        """Get population threshold for next expansion"""
        thresholds = {
            UrbanSize.HAMLET: 150,
            UrbanSize.VILLAGE: 1500,
            UrbanSize.TOWN: 15000,
            UrbanSize.CITY: 150000,
            UrbanSize.METROPOLIS: 500000
        }
        return thresholds.get(self.urban_size, 1000000)


class MetropolitanSpreadService:
    """Service for managing metropolitan area expansion and urban growth"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        self.event_dispatcher = EventDispatcher()
        
        # Configuration
        self.population_thresholds = {
            UrbanSize.HAMLET: (0, 100),
            UrbanSize.VILLAGE: (100, 1000),
            UrbanSize.TOWN: (1000, 10000),
            UrbanSize.CITY: (10000, 100000),
            UrbanSize.METROPOLIS: (100000, float('inf'))
        }
        
        self.expansion_costs = {
            UrbanSize.HAMLET: 100,
            UrbanSize.VILLAGE: 500,
            UrbanSize.TOWN: 2000,
            UrbanSize.CITY: 10000,
            UrbanSize.METROPOLIS: 50000
        }
    
    def detect_metropolitan_areas(self, region_id: Optional[UUID] = None) -> List[MetropolitanArea]:
        """Detect and classify metropolitan areas in a region"""
        try:
            query = self.db_session.query(PoiEntity).filter(
                PoiEntity.is_active == True,
                PoiEntity.poi_type.in_([POIType.CITY, POIType.TOWN, POIType.VILLAGE])
            )
            
            if region_id:
                query = query.filter(PoiEntity.region_id == region_id)
            
            pois = query.all()
            metropolitan_areas = []
            processed_pois = set()
            
            for poi in pois:
                if poi.id in processed_pois:
                    continue
                
                # Find nearby POIs that could be part of the same metropolitan area
                nearby_pois = self._find_nearby_pois(poi, pois, max_distance=50)
                total_population = sum(p.population or 0 for p in nearby_pois)
                
                if total_population < 100:  # Too small to be a metropolitan area
                    continue
                
                # Create metropolitan area
                metro_area = MetropolitanArea(
                    center_poi_id=poi.id,
                    constituent_poi_ids={p.id for p in nearby_pois},
                    total_population=total_population,
                    urban_size=self._classify_urban_size(total_population),
                    expansion_radius=self._calculate_expansion_radius(total_population),
                    claimed_hexes=self._calculate_claimed_hexes(poi, nearby_pois),
                    economic_strength=self._calculate_economic_strength(nearby_pois),
                    growth_rate=self._calculate_growth_rate(nearby_pois)
                )
                
                metropolitan_areas.append(metro_area)
                processed_pois.update(p.id for p in nearby_pois)
            
            return metropolitan_areas
            
        except Exception as e:
            logger.error(f"Error detecting metropolitan areas: {e}")
            return []
    
    def expand_metropolitan_area(self, metro_area: MetropolitanArea) -> bool:
        """Attempt to expand a metropolitan area by claiming new hexes"""
        try:
            if not metro_area.can_expand():
                return False
            
            # Calculate expansion budget
            expansion_budget = self._calculate_expansion_budget(metro_area)
            if expansion_budget < self.expansion_costs[metro_area.urban_size]:
                return False
            
            # Find optimal expansion hexes
            expansion_candidates = self._find_expansion_candidates(metro_area)
            selected_hexes = self._select_expansion_hexes(
                expansion_candidates, 
                expansion_budget, 
                metro_area.urban_size
            )
            
            if not selected_hexes:
                return False
            
            # Claim the hexes
            metro_area.claimed_hexes.update(selected_hexes)
            
            # Create new POIs if necessary
            new_pois = self._create_expansion_pois(selected_hexes, metro_area)
            metro_area.constituent_poi_ids.update(poi.id for poi in new_pois)
            
            # Update expansion radius
            metro_area.expansion_radius = max(
                metro_area.expansion_radius,
                max(self._hex_to_coordinate(list(metro_area.claimed_hexes)[0]).distance(
                    self._hex_to_coordinate(hex_coord)
                ) for hex_coord in metro_area.claimed_hexes)
            )
            
            # Dispatch expansion event
            self.event_dispatcher.publish({
                'type': 'metropolitan_area_expanded',
                'metro_area_id': str(metro_area.center_poi_id),
                'new_hexes': len(selected_hexes),
                'new_pois': len(new_pois),
                'total_population': metro_area.total_population,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error expanding metropolitan area: {e}")
            return False
    
    def simulate_urban_growth(self, time_steps: int = 1) -> Dict[str, Any]:
        """Simulate urban growth over time steps"""
        try:
            results = {
                'time_steps': time_steps,
                'expansions': 0,
                'new_pois': 0,
                'population_growth': 0,
                'metropolitan_areas': []
            }
            
            for step in range(time_steps):
                metro_areas = self.detect_metropolitan_areas()
                
                for metro_area in metro_areas:
                    # Apply population growth
                    growth = self._apply_population_growth(metro_area)
                    results['population_growth'] += growth
                    
                    # Attempt expansion
                    if self.expand_metropolitan_area(metro_area):
                        results['expansions'] += 1
                        results['new_pois'] += len(metro_area.constituent_poi_ids)
                
                results['metropolitan_areas'] = metro_areas
            
            return results
            
        except Exception as e:
            logger.error(f"Error simulating urban growth: {e}")
            return {'error': str(e)}
    
    def get_expansion_pressure(self, poi_id: UUID) -> float:
        """Calculate expansion pressure for a POI"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return 0.0
            
            population = poi.population or 0
            max_population = poi.max_population or population * 2
            
            if max_population == 0:
                return 0.0
            
            # Base pressure from population density
            density_pressure = min(population / max_population, 1.0)
            
            # Economic pressure
            economic_pressure = self._calculate_economic_pressure(poi)
            
            # Geographic pressure (based on nearby POIs)
            geographic_pressure = self._calculate_geographic_pressure(poi)
            
            # Combined pressure
            total_pressure = (
                density_pressure * 0.4 +
                economic_pressure * 0.3 +
                geographic_pressure * 0.3
            )
            
            return min(total_pressure, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating expansion pressure: {e}")
            return 0.0
    
    def _find_nearby_pois(self, center_poi: PoiEntity, all_pois: List[PoiEntity], max_distance: float) -> List[PoiEntity]:
        """Find POIs within distance of center POI"""
        nearby = [center_poi]
        
        for poi in all_pois:
            if poi.id == center_poi.id:
                continue
            
            distance = self._calculate_distance(center_poi, poi)
            if distance <= max_distance:
                nearby.append(poi)
        
        return nearby
    
    def _calculate_distance(self, poi1: PoiEntity, poi2: PoiEntity) -> float:
        """Calculate distance between two POIs"""
        if not all([poi1.location_x, poi1.location_y, poi2.location_x, poi2.location_y]):
            return float('inf')
        
        dx = poi1.location_x - poi2.location_x
        dy = poi1.location_y - poi2.location_y
        return math.sqrt(dx * dx + dy * dy)
    
    def _classify_urban_size(self, population: int) -> UrbanSize:
        """Classify urban area size based on population"""
        for size, (min_pop, max_pop) in self.population_thresholds.items():
            if min_pop <= population < max_pop:
                return size
        return UrbanSize.METROPOLIS
    
    def _calculate_expansion_radius(self, population: int) -> int:
        """Calculate expansion radius based on population"""
        return min(int(math.sqrt(population / 100)), 20)
    
    def _calculate_claimed_hexes(self, center_poi: PoiEntity, constituent_pois: List[PoiEntity]) -> Set[HexCoordinate]:
        """Calculate initial claimed hexes for metropolitan area"""
        claimed = set()
        
        for poi in constituent_pois:
            if poi.location_x is not None and poi.location_y is not None:
                hex_coord = self._coordinate_to_hex(poi.location_x, poi.location_y)
                claimed.add(hex_coord)
                
                # Add immediate neighbors for larger POIs
                if poi.population and poi.population > 1000:
                    claimed.update(hex_coord.neighbors())
        
        return claimed
    
    def _calculate_economic_strength(self, pois: List[PoiEntity]) -> float:
        """Calculate economic strength of metropolitan area"""
        total_strength = 0.0
        
        for poi in pois:
            # Base economic value from population
            population_value = (poi.population or 0) * 0.001
            
            # Bonus for certain POI types
            type_bonus = {
                POIType.CITY: 2.0,
                POIType.TOWN: 1.5,
                POIType.MARKET: 1.8,
                POIType.VILLAGE: 1.0
            }.get(POIType(poi.poi_type), 1.0)
            
            # Resource bonuses
            resource_bonus = len(poi.resources or {}) * 0.1
            
            total_strength += (population_value * type_bonus) + resource_bonus
        
        return min(total_strength, 10.0)
    
    def _calculate_growth_rate(self, pois: List[PoiEntity]) -> float:
        """Calculate growth rate for metropolitan area"""
        # Simplified growth rate calculation
        # In a real implementation, this would consider economic factors,
        # resource availability, migration patterns, etc.
        
        total_population = sum(poi.population or 0 for poi in pois)
        if total_population == 0:
            return 0.0
        
        # Base growth rate diminishes with size
        base_rate = 0.05 / (1 + total_population / 10000)
        
        # Economic factor
        economic_factor = self._calculate_economic_strength(pois) / 10.0
        
        return min(base_rate * (1 + economic_factor), 0.1)
    
    def _calculate_expansion_budget(self, metro_area: MetropolitanArea) -> int:
        """Calculate available budget for expansion"""
        return int(metro_area.economic_strength * metro_area.total_population * 0.01)
    
    def _find_expansion_candidates(self, metro_area: MetropolitanArea) -> List[HexCoordinate]:
        """Find candidate hexes for expansion"""
        candidates = set()
        
        for hex_coord in metro_area.claimed_hexes:
            candidates.update(hex_coord.neighbors())
        
        # Remove already claimed hexes
        candidates -= metro_area.claimed_hexes
        
        return list(candidates)
    
    def _select_expansion_hexes(self, candidates: List[HexCoordinate], budget: int, urban_size: UrbanSize) -> List[HexCoordinate]:
        """Select optimal hexes for expansion within budget"""
        cost_per_hex = self.expansion_costs[urban_size] // 10
        max_hexes = budget // cost_per_hex
        
        # For now, just select the first available hexes
        # In a real implementation, this would consider terrain, resources, etc.
        return candidates[:min(max_hexes, len(candidates))]
    
    def _create_expansion_pois(self, hexes: List[HexCoordinate], metro_area: MetropolitanArea) -> List[PoiEntity]:
        """Create new POIs in expansion hexes"""
        new_pois = []
        
        for hex_coord in hexes:
            # Only create POIs for some hexes (not all hexes need POIs)
            if len(new_pois) >= len(hexes) // 3:
                break
            
            x, y = self._hex_to_coordinate(hex_coord)
            
            poi = PoiEntity(
                name=f"Expansion Settlement {len(new_pois) + 1}",
                description="Settlement created through metropolitan expansion",
                poi_type=POIType.SETTLEMENT.value,
                state=POIState.UNDER_CONSTRUCTION.value,
                location_x=x,
                location_y=y,
                population=50,  # Small initial population
                max_population=500,
                resources={},
                properties={'expansion_origin': str(metro_area.center_poi_id)}
            )
            
            self.db_session.add(poi)
            new_pois.append(poi)
        
        self.db_session.commit()
        return new_pois
    
    def _apply_population_growth(self, metro_area: MetropolitanArea) -> int:
        """Apply population growth to metropolitan area"""
        growth_amount = int(metro_area.total_population * metro_area.growth_rate)
        
        # Distribute growth among constituent POIs
        pois = self.db_session.query(PoiEntity).filter(
            PoiEntity.id.in_(metro_area.constituent_poi_ids)
        ).all()
        
        total_growth = 0
        for poi in pois:
            poi_growth = growth_amount // len(pois)
            if poi.population is not None:
                poi.population += poi_growth
                total_growth += poi_growth
        
        self.db_session.commit()
        return total_growth
    
    def _calculate_economic_pressure(self, poi: PoiEntity) -> float:
        """Calculate economic pressure for expansion"""
        # Simplified calculation based on POI properties
        resources = poi.resources or {}
        return min(len(resources) * 0.1, 1.0)
    
    def _calculate_geographic_pressure(self, poi: PoiEntity) -> float:
        """Calculate geographic pressure from nearby POIs"""
        # Simplified calculation
        # In reality, this would consider overcrowding, competition, etc.
        return 0.5
    
    def _coordinate_to_hex(self, x: float, y: float) -> HexCoordinate:
        """Convert world coordinates to hex coordinates"""
        # Simplified hex conversion
        # In a real implementation, this would use proper hex grid mathematics
        q = int(x // 100)
        r = int(y // 100)
        s = -q - r
        return HexCoordinate(q, r, s)
    
    def _hex_to_coordinate(self, hex_coord: HexCoordinate) -> Tuple[float, float]:
        """Convert hex coordinates to world coordinates"""
        # Simplified coordinate conversion
        x = hex_coord.q * 100
        y = hex_coord.r * 100
        return (x, y)


# Factory function for dependency injection
def get_metropolitan_spread_service(db_session: Optional[Session] = None) -> MetropolitanSpreadService:
    """Factory function to create MetropolitanSpreadService instance"""
    return MetropolitanSpreadService(db_session) 