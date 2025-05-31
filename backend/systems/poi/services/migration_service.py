"""
Migration Service

Handles population movement between POIs, migration triggers, and
demographic changes in the POI system.
"""

from typing import Dict, List, Optional, Tuple, Set, Any
from uuid import UUID
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta
import random
import math

from backend.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db
from backend.infrastructure.events import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MigrationType(str, Enum):
    """Types of migration events"""
    VOLUNTARY = "voluntary"          # Economic or quality of life driven
    FORCED = "forced"               # War, disaster, persecution
    SEASONAL = "seasonal"           # Seasonal work or climate
    TRADE = "trade"                 # Following trade routes
    RESOURCE_DRIVEN = "resource"    # Following resource availability
    REFUGEE = "refugee"             # Fleeing conflict or disaster
    EXPANSION = "expansion"         # City expansion driven


class MigrationTrigger(str, Enum):
    """Triggers that cause migration"""
    OVERCROWDING = "overcrowding"
    RESOURCE_SCARCITY = "resource_scarcity"
    ECONOMIC_OPPORTUNITY = "economic_opportunity"
    CONFLICT = "conflict"
    DISASTER = "disaster"
    FACTION_CHANGE = "faction_change"
    SEASONAL_CYCLE = "seasonal_cycle"
    TRADE_OPPORTUNITY = "trade_opportunity"
    FAMILY_REUNION = "family_reunion"
    RELIGIOUS_PERSECUTION = "religious_persecution"


class MigrationStatus(str, Enum):
    """Status of migration groups"""
    PLANNING = "planning"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    SETTLED = "settled"
    FAILED = "failed"
    RETURNED = "returned"


@dataclass
class MigrationGroup:
    """Represents a group of people migrating between POIs"""
    id: UUID
    source_poi_id: UUID
    destination_poi_id: UUID
    population_size: int
    migration_type: MigrationType
    trigger: MigrationTrigger
    status: MigrationStatus = MigrationStatus.PLANNING
    created_at: datetime = field(default_factory=datetime.utcnow)
    departure_date: Optional[datetime] = None
    arrival_date: Optional[datetime] = None
    travel_time_days: int = 0
    success_probability: float = 1.0
    resources_carried: Dict[str, int] = field(default_factory=dict)
    cultural_traits: List[str] = field(default_factory=list)
    
    def is_in_transit(self) -> bool:
        """Check if the migration group is currently traveling"""
        return self.status == MigrationStatus.IN_TRANSIT
    
    def calculate_arrival_date(self) -> Optional[datetime]:
        """Calculate when the group will arrive at destination"""
        if self.departure_date and self.travel_time_days > 0:
            return self.departure_date + timedelta(days=self.travel_time_days)
        return None


@dataclass
class MigrationRoute:
    """Represents a migration route between POIs"""
    source_poi_id: UUID
    destination_poi_id: UUID
    distance: float
    base_travel_time: int  # Days
    difficulty: float  # 0.0 to 1.0
    safety: float  # 0.0 to 1.0
    established: bool = False  # Whether this is a known route
    usage_count: int = 0
    
    def get_travel_time(self, group_size: int, season_modifier: float = 1.0) -> int:
        """Calculate travel time considering group size and conditions"""
        size_modifier = 1.0 + (group_size / 1000) * 0.5  # Larger groups travel slower
        total_modifier = size_modifier * season_modifier * (1.0 + self.difficulty)
        return max(1, int(self.base_travel_time * total_modifier))
    
    def get_success_probability(self, group_size: int, resources: int) -> float:
        """Calculate probability of successful migration"""
        base_success = self.safety * 0.8 + (0.2 if self.established else 0.0)
        
        # Larger groups have better survival rates but are easier targets
        size_factor = min(1.0, group_size / 100) * 0.1
        if group_size > 500:
            size_factor -= (group_size - 500) / 10000  # Penalty for very large groups
        
        # Resources improve success rate
        resource_factor = min(0.2, resources / 1000)
        
        return max(0.1, min(1.0, base_success + size_factor + resource_factor))


@dataclass
class PopulationDemographics:
    """Represents demographic information for a POI"""
    poi_id: UUID
    total_population: int
    age_distribution: Dict[str, int] = field(default_factory=dict)  # children, adults, elderly
    occupation_distribution: Dict[str, int] = field(default_factory=dict)
    cultural_groups: Dict[str, int] = field(default_factory=dict)
    migration_pressure: float = 0.0  # 0.0 to 1.0
    attractiveness: float = 0.5  # 0.0 to 1.0
    
    def get_migration_capacity(self) -> int:
        """Calculate how many people could migrate from this POI"""
        # Conservative estimate: up to 10% of population could migrate in crisis
        max_migrants = int(self.total_population * 0.1)
        pressure_multiplier = self.migration_pressure
        return int(max_migrants * pressure_multiplier)
    
    def get_reception_capacity(self, max_population: Optional[int] = None) -> int:
        """Calculate how many migrants this POI could accept"""
        if max_population:
            available_space = max_population - self.total_population
            return max(0, int(available_space * 0.8))  # 80% of available space
        return int(self.total_population * 0.2)  # Can accept 20% more people


class MigrationService:
    """Service for managing population migration between POIs"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db()
        self.event_dispatcher = EventDispatcher()
        
        # Migration data (in a real system, this would be in the database)
        self.migration_groups: Dict[UUID, MigrationGroup] = {}
        self.migration_routes: Dict[Tuple[UUID, UUID], MigrationRoute] = {}
        self.population_demographics: Dict[UUID, PopulationDemographics] = {}
        
        # Configuration
        self.max_daily_migrants = 100  # Maximum migrants processed per day per POI
        self.route_discovery_chance = 0.1  # Chance to discover new routes
        self.cultural_integration_time = 30  # Days for cultural integration
    
    def initialize_poi_demographics(self, poi_id: UUID, initial_population: int = None) -> bool:
        """Initialize demographic data for a POI"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return False
            
            population = initial_population or poi.population or 0
            
            # Generate basic age distribution
            age_distribution = {
                'children': int(population * 0.25),
                'adults': int(population * 0.65),
                'elderly': int(population * 0.10)
            }
            
            # Generate basic occupation distribution based on POI type
            occupation_distribution = self._generate_occupation_distribution(poi.poi_type, population)
            
            demographics = PopulationDemographics(
                poi_id=poi_id,
                total_population=population,
                age_distribution=age_distribution,
                occupation_distribution=occupation_distribution,
                cultural_groups={'local': population},
                migration_pressure=self._calculate_initial_migration_pressure(poi),
                attractiveness=self._calculate_initial_attractiveness(poi)
            )
            
            self.population_demographics[poi_id] = demographics
            
            logger.info(f"Initialized demographics for POI {poi_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing POI demographics: {e}")
            return False
    
    def create_migration_group(self, source_poi_id: UUID, destination_poi_id: UUID,
                              population_size: int, migration_type: MigrationType,
                              trigger: MigrationTrigger, resources: Dict[str, int] = None) -> Optional[MigrationGroup]:
        """Create a new migration group"""
        try:
            # Validate source POI has enough population
            source_demo = self.population_demographics.get(source_poi_id)
            if not source_demo or source_demo.total_population < population_size:
                logger.warning(f"Insufficient population at source POI {source_poi_id}")
                return None
            
            # Get or create migration route
            route = self._get_or_create_route(source_poi_id, destination_poi_id)
            if not route:
                logger.warning(f"Cannot establish route from {source_poi_id} to {destination_poi_id}")
                return None
            
            # Create migration group
            migration_group = MigrationGroup(
                id=UUID(),
                source_poi_id=source_poi_id,
                destination_poi_id=destination_poi_id,
                population_size=population_size,
                migration_type=migration_type,
                trigger=trigger,
                travel_time_days=route.get_travel_time(population_size),
                success_probability=route.get_success_probability(population_size, sum(resources.values()) if resources else 0),
                resources_carried=resources or {}
            )
            
            self.migration_groups[migration_group.id] = migration_group
            
            # Update source demographics
            source_demo.total_population -= population_size
            
            # Dispatch migration created event
            self.event_dispatcher.publish({
                'type': 'migration_group_created',
                'group_id': str(migration_group.id),
                'source_poi': str(source_poi_id),
                'destination_poi': str(destination_poi_id),
                'population_size': population_size,
                'migration_type': migration_type.value,
                'trigger': trigger.value,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return migration_group
            
        except Exception as e:
            logger.error(f"Error creating migration group: {e}")
            return None
    
    def start_migration(self, group_id: UUID) -> bool:
        """Start the migration journey for a group"""
        try:
            group = self.migration_groups.get(group_id)
            if not group or group.status != MigrationStatus.PLANNING:
                return False
            
            group.status = MigrationStatus.IN_TRANSIT
            group.departure_date = datetime.utcnow()
            group.arrival_date = group.calculate_arrival_date()
            
            # Dispatch migration started event
            self.event_dispatcher.publish({
                'type': 'migration_started',
                'group_id': str(group_id),
                'departure_date': group.departure_date.isoformat(),
                'expected_arrival': group.arrival_date.isoformat() if group.arrival_date else None,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting migration: {e}")
            return False
    
    def process_daily_migrations(self) -> Dict[str, Any]:
        """Process daily migration activities"""
        try:
            results = {
                'groups_arrived': 0,
                'groups_failed': 0,
                'new_migrations': 0,
                'total_migrants_moved': 0
            }
            
            current_time = datetime.utcnow()
            
            # Process arriving migration groups
            for group in list(self.migration_groups.values()):
                if group.status == MigrationStatus.IN_TRANSIT and group.arrival_date:
                    if current_time >= group.arrival_date:
                        if self._process_arrival(group):
                            results['groups_arrived'] += 1
                            results['total_migrants_moved'] += group.population_size
                        else:
                            results['groups_failed'] += 1
            
            # Check for new migration triggers
            new_migrations = self._check_migration_triggers()
            results['new_migrations'] = len(new_migrations)
            
            # Start planned migrations
            for migration in new_migrations:
                self.start_migration(migration.id)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing daily migrations: {e}")
            return {'error': str(e)}
    
    def calculate_migration_pressure(self, poi_id: UUID) -> float:
        """Calculate current migration pressure for a POI"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return 0.0
            
            demographics = self.population_demographics.get(poi_id)
            if not demographics:
                return 0.0
            
            pressure = 0.0
            
            # Overcrowding pressure
            if poi.max_population and demographics.total_population > poi.max_population:
                overcrowding = (demographics.total_population - poi.max_population) / poi.max_population
                pressure += min(overcrowding * 0.5, 0.4)
            
            # Resource scarcity pressure (simplified)
            # In a real system, this would integrate with ResourceManagementService
            if poi.state in [POIState.DECLINING, POIState.ABANDONED]:
                pressure += 0.3
            
            # Conflict pressure
            # In a real system, this would integrate with faction conflict systems
            if poi.state == POIState.RUINED:
                pressure += 0.8
            
            # Economic pressure (simplified)
            if poi.poi_type == POIType.VILLAGE and demographics.total_population > 800:
                pressure += 0.2  # Villages want to grow into towns
            
            return min(pressure, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating migration pressure: {e}")
            return 0.0
    
    def calculate_attractiveness(self, poi_id: UUID) -> float:
        """Calculate how attractive a POI is for migrants"""
        try:
            poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == poi_id).first()
            if not poi:
                return 0.0
            
            demographics = self.population_demographics.get(poi_id)
            if not demographics:
                return 0.0
            
            attractiveness = 0.5  # Base attractiveness
            
            # Population capacity
            if poi.max_population and demographics.total_population < poi.max_population:
                capacity_bonus = (poi.max_population - demographics.total_population) / poi.max_population
                attractiveness += capacity_bonus * 0.3
            
            # POI type bonus
            type_bonus = {
                POIType.CITY: 0.3,
                POIType.TOWN: 0.2,
                POIType.MARKET: 0.25,
                POIType.TEMPLE: 0.15,
                POIType.FORTRESS: -0.1,  # Less attractive due to military nature
            }.get(POIType(poi.poi_type), 0.0)
            
            attractiveness += type_bonus
            
            # State modifier
            if poi.state == POIState.GROWING:
                attractiveness += 0.2
            elif poi.state in [POIState.DECLINING, POIState.RUINED]:
                attractiveness -= 0.3
            
            return max(0.0, min(attractiveness, 1.0))
            
        except Exception as e:
            logger.error(f"Error calculating attractiveness: {e}")
            return 0.0
    
    def get_migration_statistics(self, poi_id: UUID) -> Dict[str, Any]:
        """Get migration statistics for a POI"""
        try:
            outgoing = [g for g in self.migration_groups.values() if g.source_poi_id == poi_id]
            incoming = [g for g in self.migration_groups.values() if g.destination_poi_id == poi_id]
            
            return {
                'outgoing_groups': len(outgoing),
                'incoming_groups': len(incoming),
                'outgoing_population': sum(g.population_size for g in outgoing),
                'incoming_population': sum(g.population_size for g in incoming),
                'in_transit_to': len([g for g in incoming if g.is_in_transit()]),
                'in_transit_from': len([g for g in outgoing if g.is_in_transit()]),
                'migration_pressure': self.calculate_migration_pressure(poi_id),
                'attractiveness': self.calculate_attractiveness(poi_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting migration statistics: {e}")
            return {}
    
    def _generate_occupation_distribution(self, poi_type: str, population: int) -> Dict[str, int]:
        """Generate occupation distribution based on POI type"""
        distributions = {
            POIType.CITY: {
                'farmers': 0.1, 'craftsmen': 0.3, 'merchants': 0.2, 
                'laborers': 0.25, 'nobles': 0.05, 'clergy': 0.1
            },
            POIType.TOWN: {
                'farmers': 0.2, 'craftsmen': 0.25, 'merchants': 0.15,
                'laborers': 0.3, 'nobles': 0.02, 'clergy': 0.08
            },
            POIType.VILLAGE: {
                'farmers': 0.6, 'craftsmen': 0.15, 'merchants': 0.05,
                'laborers': 0.15, 'nobles': 0.01, 'clergy': 0.04
            }
        }
        
        base_dist = distributions.get(POIType(poi_type), distributions[POIType.VILLAGE])
        return {occupation: int(population * ratio) for occupation, ratio in base_dist.items()}
    
    def _calculate_initial_migration_pressure(self, poi: PoiEntity) -> float:
        """Calculate initial migration pressure for a POI"""
        pressure = 0.0
        
        if poi.max_population and poi.population:
            if poi.population > poi.max_population:
                pressure += 0.3
        
        if poi.state in [POIState.DECLINING, POIState.ABANDONED]:
            pressure += 0.4
        
        return min(pressure, 1.0)
    
    def _calculate_initial_attractiveness(self, poi: PoiEntity) -> float:
        """Calculate initial attractiveness for a POI"""
        attractiveness = 0.5
        
        if poi.state == POIState.GROWING:
            attractiveness += 0.2
        elif poi.state in [POIState.DECLINING, POIState.RUINED]:
            attractiveness -= 0.3
        
        if poi.poi_type in [POIType.CITY, POIType.TOWN]:
            attractiveness += 0.1
        
        return max(0.0, min(attractiveness, 1.0))
    
    def _get_or_create_route(self, source_poi_id: UUID, destination_poi_id: UUID) -> Optional[MigrationRoute]:
        """Get existing route or create new one"""
        route_key = (source_poi_id, destination_poi_id)
        
        if route_key in self.migration_routes:
            return self.migration_routes[route_key]
        
        # Create new route
        source_poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == source_poi_id).first()
        dest_poi = self.db_session.query(PoiEntity).filter(PoiEntity.id == destination_poi_id).first()
        
        if not source_poi or not dest_poi:
            return None
        
        # Calculate distance and properties
        if all([source_poi.location_x, source_poi.location_y, dest_poi.location_x, dest_poi.location_y]):
            distance = math.sqrt(
                (source_poi.location_x - dest_poi.location_x) ** 2 +
                (source_poi.location_y - dest_poi.location_y) ** 2
            )
        else:
            distance = 100.0  # Default distance
        
        route = MigrationRoute(
            source_poi_id=source_poi_id,
            destination_poi_id=destination_poi_id,
            distance=distance,
            base_travel_time=max(1, int(distance / 10)),  # 10 units per day
            difficulty=random.uniform(0.1, 0.8),
            safety=random.uniform(0.5, 0.9),
            established=False
        )
        
        self.migration_routes[route_key] = route
        return route
    
    def _process_arrival(self, group: MigrationGroup) -> bool:
        """Process the arrival of a migration group"""
        try:
            # Check if migration succeeds
            if random.random() > group.success_probability:
                group.status = MigrationStatus.FAILED
                return False
            
            # Add population to destination
            dest_demo = self.population_demographics.get(group.destination_poi_id)
            if dest_demo:
                dest_demo.total_population += group.population_size
                
                # Update destination POI population in database
                dest_poi = self.db_session.query(PoiEntity).filter(
                    PoiEntity.id == group.destination_poi_id
                ).first()
                if dest_poi:
                    dest_poi.population = dest_demo.total_population
                    self.db_session.commit()
            
            group.status = MigrationStatus.ARRIVED
            
            # Dispatch arrival event
            self.event_dispatcher.publish({
                'type': 'migration_arrived',
                'group_id': str(group.id),
                'destination_poi': str(group.destination_poi_id),
                'population_size': group.population_size,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing migration arrival: {e}")
            return False
    
    def _check_migration_triggers(self) -> List[MigrationGroup]:
        """Check for conditions that trigger new migrations"""
        new_migrations = []
        
        try:
            for poi_id, demographics in self.population_demographics.items():
                pressure = self.calculate_migration_pressure(poi_id)
                
                if pressure > 0.7:  # High pressure triggers migration
                    # Find suitable destination
                    destinations = self._find_migration_destinations(poi_id)
                    if destinations:
                        best_destination = max(destinations, key=lambda x: x[1])[0]
                        
                        # Create migration group
                        migration_size = min(
                            demographics.get_migration_capacity(),
                            random.randint(50, 200)
                        )
                        
                        trigger = MigrationTrigger.OVERCROWDING
                        if pressure > 0.8:
                            trigger = MigrationTrigger.RESOURCE_SCARCITY
                        
                        migration = self.create_migration_group(
                            poi_id, best_destination, migration_size,
                            MigrationType.VOLUNTARY, trigger
                        )
                        
                        if migration:
                            new_migrations.append(migration)
            
            return new_migrations
            
        except Exception as e:
            logger.error(f"Error checking migration triggers: {e}")
            return []
    
    def _find_migration_destinations(self, source_poi_id: UUID) -> List[Tuple[UUID, float]]:
        """Find suitable migration destinations for a POI"""
        destinations = []
        
        for poi_id, demographics in self.population_demographics.items():
            if poi_id == source_poi_id:
                continue
            
            attractiveness = self.calculate_attractiveness(poi_id)
            reception_capacity = demographics.get_reception_capacity()
            
            if reception_capacity > 0 and attractiveness > 0.3:
                destinations.append((poi_id, attractiveness))
        
        return destinations


# Factory function for dependency injection
def get_migration_service(db_session: Optional[Session] = None) -> MigrationService:
    """Factory function to create MigrationService instance"""
    return MigrationService(db_session) 