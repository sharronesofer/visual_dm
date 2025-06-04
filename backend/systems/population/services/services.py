"""
Population System Services - Pure Business Logic

This module provides business logic services for the population system
according to the Development Bible standards, following the faction system pattern.
"""

# Standard library imports
from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime

# Project imports - Business domain models
from backend.systems.population.models.population import (
    PopulationData, 
    CreatePopulationData, 
    UpdatePopulationData,
    create_population_data_from_dict,
    population_data_to_dict
)

# Business logic utilities
from backend.systems.population.utils.consolidated_utils import (
    calculate_war_impact,
    calculate_catastrophe_impact,
    calculate_resource_shortage_impact,
    calculate_migration_impact,
    calculate_seasonal_growth_modifier,
    calculate_seasonal_death_rate_modifier,
    is_valid_transition,
    is_valid_state_progression,
    estimate_time_to_state,
    get_poi_status_description,
    calculate_controlled_growth_rate,
    calculate_racial_distribution
)

# Configuration loading
import json
import os
from pathlib import Path


def load_population_config():
    """Load population configuration from JSON file"""
    config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "systems" / "population" / "population_config.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default config if file not found
        return {
            "growth_control": {"base_growth_rate": 0.02},
            "racial_distribution": {"default_weights": {"human": 0.6}},
            "resource_consumption": {"base_rates_per_capita_per_day": {"food": 2.5}},
            "war_impact": {"base_mortality_multiplier": 0.15}
        }


def load_settlement_types():
    """Load settlement types configuration from JSON file"""
    config_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "systems" / "population" / "settlement_types.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default settlement types if file not found
        return {
            "settlement_types": {
                "village": {"population_range": [50, 300]},
                "town": {"population_range": [300, 2000]},
                "city": {"population_range": [2000, 15000]}
            }
        }


# Load configurations
POPULATION_CONFIG = load_population_config()
SETTLEMENT_TYPES = load_settlement_types()


# Business Logic Protocols (dependency injection)
class PopulationRepository(Protocol):
    """Protocol for population data access"""
    
    def get_population_by_id(self, population_id: UUID) -> Optional[PopulationData]:
        """Get population by ID"""
        ...
    
    def get_population_by_name(self, name: str) -> Optional[PopulationData]:
        """Get population by name"""
        ...
    
    def create_population(self, population_data: PopulationData) -> PopulationData:
        """Create a new population"""
        ...
    
    def update_population(self, population_data: PopulationData) -> PopulationData:
        """Update existing population"""
        ...
    
    def delete_population(self, population_id: UUID) -> bool:
        """Delete population"""
        ...
    
    def list_populations(self, 
                        page: int = 1, 
                        size: int = 50, 
                        status: Optional[str] = None,
                        search: Optional[str] = None) -> Tuple[List[PopulationData], int]:
        """List populations with pagination"""
        ...
    
    def get_population_statistics(self) -> Dict[str, Any]:
        """Get population statistics"""
        ...


class PopulationValidationService(Protocol):
    """Protocol for population validation"""
    
    def validate_population_data(self, population_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate population creation/update data"""
        ...
    
    def validate_demographic_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Validate demographic attributes"""
        ...
    
    def generate_default_attributes(self) -> Dict[str, Any]:
        """Generate default population attributes"""
        ...


class PopulationBusinessService:
    """Service class for population business logic - pure business rules"""
    
    def __init__(self, 
                 population_repository: PopulationRepository,
                 validation_service: PopulationValidationService):
        self.population_repository = population_repository
        self.validation_service = validation_service

    def create_population(
        self, 
        create_data: CreatePopulationData,
        user_id: Optional[UUID] = None
    ) -> PopulationData:
        """Create a new population with business validation"""
        # Convert to dict for validation
        population_data_dict = {
            'name': create_data.name,
            'description': create_data.description,
            'status': create_data.status,
            'properties': create_data.properties,
            'population_count': create_data.population_count,
            'capacity': create_data.capacity,
            'state': create_data.state,
            'resources': create_data.resources
        }
        
        # Comprehensive validation and sanitization
        validated_data = self.validation_service.validate_population_data(population_data_dict)
        
        # Business rule: Check for existing population with same name
        existing_population = self.population_repository.get_population_by_name(validated_data['name'])
        if existing_population:
            raise ValueError(f"Population with name '{validated_data['name']}' already exists")
        
        # Business rule: Generate default attributes if not provided
        if not validated_data.get('population_count'):
            defaults = self.validation_service.generate_default_attributes()
            for key, value in defaults.items():
                if key not in validated_data or validated_data[key] is None:
                    validated_data[key] = value
        
        # Create business entity with validated data
        population_entity = PopulationData(
            id=uuid4(),
            name=validated_data['name'],
            description=validated_data.get('description'),
            status=validated_data.get('status', 'active'),
            properties=validated_data.get('properties', {}),
            population_count=validated_data.get('population_count'),
            capacity=validated_data.get('capacity'),
            state=validated_data.get('state', 'stable'),
            resources=validated_data.get('resources', {}),
            created_at=datetime.utcnow()
        )
        
        # Business rule: Add user tracking if provided
        if user_id:
            population_entity.properties = population_entity.properties or {}
            population_entity.properties['created_by'] = str(user_id)
        
        # Persist via repository
        return self.population_repository.create_population(population_entity)

    def get_population_by_id(self, population_id: UUID) -> Optional[PopulationData]:
        """Get population by ID"""
        return self.population_repository.get_population_by_id(population_id)

    def update_population(
        self, 
        population_id: UUID, 
        update_data: UpdatePopulationData
    ) -> PopulationData:
        """Update existing population with business rules"""
        # Business rule: Population must exist
        entity = self.population_repository.get_population_by_id(population_id)
        if not entity:
            raise ValueError(f"Population {population_id} not found")
        
        # Apply updates with business validation
        update_fields = update_data.get_fields()
        if update_fields:
            # Business rule: Validate demographic attributes if any are being updated
            demographic_updates = {}
            for attr_name in ["population_count", "capacity", "growth_rate", "state", "resources"]:
                if attr_name in update_fields:
                    demographic_updates[attr_name] = update_fields.pop(attr_name)
            
            if demographic_updates:
                # Get current values for attributes not being updated
                current_attrs = {
                    'population_count': entity.population_count,
                    'capacity': entity.capacity,
                    'growth_rate': entity.growth_rate,
                    'state': entity.state,
                    'resources': entity.resources or {}
                }
                current_attrs.update(demographic_updates)
                validated_attrs = self.validation_service.validate_demographic_attributes(current_attrs)
                
                # Apply validated demographic attributes
                for attr_name, value in validated_attrs.items():
                    setattr(entity, attr_name, value)
            
            # Apply other updates
            for field, value in update_fields.items():
                setattr(entity, field, value)
            
            # Update timestamp
            entity.updated_at = datetime.utcnow()
        
        return self.population_repository.update_population(entity)

    def delete_population(self, population_id: UUID) -> bool:
        """Soft delete population with business rules"""
        # Business rule: Population must exist
        entity = self.population_repository.get_population_by_id(population_id)
        if not entity:
            raise ValueError(f"Population {population_id} not found")
        
        return self.population_repository.delete_population(population_id)

    def list_populations(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[PopulationData], int]:
        """List populations with pagination and filtering"""
        return self.population_repository.list_populations(page, size, status, search)

    def get_population_statistics(self) -> Dict[str, Any]:
        """Get population statistics"""
        return self.population_repository.get_population_statistics()

    def calculate_population_growth_rate(self, population: PopulationData) -> float:
        """Business logic: Calculate growth rate for a population"""
        if not population.population_count or not population.capacity:
            return 0.0
        
        base_growth_rate = POPULATION_CONFIG.get("growth_control", {}).get("base_growth_rate", 0.02)
        
        growth_rate = calculate_controlled_growth_rate(
            current_population=population.population_count,
            base_growth_rate=base_growth_rate,
            carrying_capacity=population.capacity,
            minimum_viable_population=POPULATION_CONFIG.get("growth_control", {}).get("minimum_viable_population", 50),
            resource_availability=population.resource_modifier or 1.0,
            stability_factor=1.0,  # TODO: Calculate from population data
            config=POPULATION_CONFIG["growth_control"]
        )
        
        return round(growth_rate, 4)

    def assess_population_stability(self, population: PopulationData) -> Dict[str, Any]:
        """Business logic: Assess stability of a population"""
        if not population.population_count:
            return {
                "stability_score": 0.0,
                "category": "unknown",
                "factors": ["insufficient_data"]
            }
        
        # Calculate stability based on various factors
        population_stability = 1.0
        factors = []
        
        # Population size factor
        if population.population_count < 50:
            population_stability *= 0.5
            factors.append("small_population")
        elif population.population_count > (population.capacity or 1000) * 1.2:
            population_stability *= 0.7
            factors.append("overpopulation")
        
        # Recent impacts factor
        if population.casualties and population.casualties > 0:
            casualty_rate = population.casualties / population.population_count
            population_stability *= (1.0 - casualty_rate)
            factors.append("war_casualties")
        
        if population.catastrophe_deaths and population.catastrophe_deaths > 0:
            disaster_rate = population.catastrophe_deaths / population.population_count
            population_stability *= (1.0 - disaster_rate)
            factors.append("disaster_losses")
        
        # Resource availability factor
        if population.resource_modifier and population.resource_modifier < 0.8:
            population_stability *= population.resource_modifier
            factors.append("resource_shortage")
        
        # Determine stability category
        if population_stability >= 0.8:
            category = "highly_stable"
        elif population_stability >= 0.6:
            category = "stable"
        elif population_stability >= 0.4:
            category = "moderately_stable"
        elif population_stability >= 0.2:
            category = "unstable"
        else:
            category = "highly_unstable"
        
        return {
            "stability_score": round(population_stability, 2),
            "category": category,
            "factors": factors
        }

    def apply_war_impact(
        self,
        population_id: UUID,
        war_intensity: float,
        duration_days: int,
        defensive_strength: float = 0.5
    ) -> Dict[str, Any]:
        """Apply war impact to population using business logic"""
        population = self.population_repository.get_population_by_id(population_id)
        if not population:
            raise ValueError(f"Population {population_id} not found")
        
        if not population.population_count:
            raise ValueError("Population count not set")
        
        # Calculate war impact using business logic
        impact_result = calculate_war_impact(
            current_population=population.population_count,
            war_intensity=war_intensity,
            duration_days=duration_days,
            defensive_strength=defensive_strength,
            config=POPULATION_CONFIG.get("war_impact", {})
        )
        
        # Apply the impact to the population
        population.casualties = impact_result.get("casualties", 0)
        population.refugees = impact_result.get("refugees", 0)
        population.population_count = impact_result.get("new_population", population.population_count)
        population.last_war_impact = impact_result
        population.last_war_date = datetime.utcnow().isoformat()
        
        # Update the population
        self.population_repository.update_population(population)
        
        return impact_result

    def apply_catastrophe_impact(
        self,
        population_id: UUID,
        catastrophe_type: str,
        severity: float,
        preparedness: float = 0.3
    ) -> Dict[str, Any]:
        """Apply catastrophe impact to population using business logic"""
        population = self.population_repository.get_population_by_id(population_id)
        if not population:
            raise ValueError(f"Population {population_id} not found")
        
        if not population.population_count:
            raise ValueError("Population count not set")
        
        # Calculate catastrophe impact using business logic
        impact_result = calculate_catastrophe_impact(
            current_population=population.population_count,
            catastrophe_type=catastrophe_type,
            severity=severity,
            preparedness=preparedness
        )
        
        # Apply the impact to the population
        population.catastrophe_deaths = impact_result.get("deaths", 0)
        population.catastrophe_displaced = impact_result.get("displaced", 0)
        population.catastrophe_injured = impact_result.get("injured", 0)
        population.population_count = impact_result.get("new_population", population.population_count)
        population.last_catastrophe_impact = impact_result
        population.last_catastrophe_date = datetime.utcnow().isoformat()
        
        # Update the population
        self.population_repository.update_population(population)
        
        return impact_result

    def apply_migration(
        self,
        origin_population_id: UUID,
        destination_population_id: UUID,
        push_factors: Dict[str, float],
        pull_factors: Dict[str, float],
        distance_km: float = 100.0
    ) -> Dict[str, Any]:
        """Apply migration between populations using business logic"""
        origin_pop = self.population_repository.get_population_by_id(origin_population_id)
        dest_pop = self.population_repository.get_population_by_id(destination_population_id)
        
        if not origin_pop:
            raise ValueError(f"Origin population {origin_population_id} not found")
        if not dest_pop:
            raise ValueError(f"Destination population {destination_population_id} not found")
        
        if not origin_pop.population_count:
            raise ValueError("Origin population count not set")
        
        # Calculate migration using business logic
        migration_result = calculate_migration_impact(
            origin_population=origin_pop.population_count,
            push_factors=push_factors,
            pull_factors=pull_factors,
            distance_km=distance_km
        )
        
        migrants = migration_result.get("migrants", 0)
        
        # Apply migration effects
        if migrants > 0:
            origin_pop.population_count = max(0, origin_pop.population_count - migrants)
            origin_pop.last_migration_out = migrants
            origin_pop.last_migration_date = datetime.utcnow().isoformat()
            
            dest_pop.population_count += migrants
            dest_pop.last_migration_in = migrants
            dest_pop.last_migration_date = datetime.utcnow().isoformat()
            
            # Update both populations
            self.population_repository.update_population(origin_pop)
            self.population_repository.update_population(dest_pop)
        
        return migration_result

    def _categorize_attribute(self, value: float) -> str:
        """Helper method to categorize attribute values"""
        if value >= 0.8:
            return "very_high"
        elif value >= 0.6:
            return "high"
        elif value >= 0.4:
            return "moderate"
        elif value >= 0.2:
            return "low"
        else:
            return "very_low"


def create_population_business_service(
    population_repository: PopulationRepository,
    validation_service: PopulationValidationService
) -> PopulationBusinessService:
    """Factory function to create population business service"""
    return PopulationBusinessService(population_repository, validation_service)


class PopulationService:
    """Facade service for population operations - adapts business service to API expectations"""
    
    def __init__(self, db_session):
        """Initialize with database session (for compatibility with existing tests/router)"""
        self.db_session = db_session
        # Initialize the repository and business service
        from backend.infrastructure.repositories.population_repository import SQLAlchemyPopulationRepository
        from backend.infrastructure.utils.population.validators import DefaultPopulationValidationService
        
        self.repository = SQLAlchemyPopulationRepository(db_session)
        self.validation_service = DefaultPopulationValidationService()
        self.business_service = PopulationBusinessService(self.repository, self.validation_service)
    
    async def create_population(self, request, user_id: Optional[UUID] = None):
        """Create a new population"""
        try:
            # Convert API request to business data
            create_data = CreatePopulationData(
                name=request.name,
                description=request.description,
                status=getattr(request, 'status', 'active'),
                properties=getattr(request, 'properties', {}),
                population_count=getattr(request, 'population_count', None),
                capacity=getattr(request, 'capacity', None),
                state=getattr(request, 'state', 'stable'),
                resources=getattr(request, 'resources', {})
            )
            
            # Create via business service
            population_data = self.business_service.create_population(create_data, user_id)
            
            # Convert back to API response
            from backend.infrastructure.models.population.models import PopulationResponse
            return PopulationResponse(
                id=population_data.id,
                name=population_data.name,
                description=population_data.description,
                status=population_data.status,
                properties=population_data.properties,
                created_at=population_data.created_at or datetime.utcnow(),
                updated_at=population_data.updated_at,
                is_active=population_data.is_active,
                population_count=population_data.population_count,
                capacity=population_data.capacity,
                growth_rate=population_data.growth_rate,
                state=population_data.state,
                previous_state=population_data.previous_state,
                casualties=population_data.casualties,
                refugees=population_data.refugees,
                last_war_impact=population_data.last_war_impact,
                last_war_date=population_data.last_war_date,
                catastrophe_deaths=population_data.catastrophe_deaths,
                catastrophe_displaced=population_data.catastrophe_displaced,
                catastrophe_injured=population_data.catastrophe_injured,
                last_catastrophe_impact=population_data.last_catastrophe_impact,
                last_catastrophe_date=population_data.last_catastrophe_date,
                shortage_deaths=population_data.shortage_deaths,
                shortage_migrants=population_data.shortage_migrants,
                last_shortage_impact=population_data.last_shortage_impact,
                last_shortage_date=population_data.last_shortage_date,
                last_migration_in=population_data.last_migration_in,
                last_migration_out=population_data.last_migration_out,
                last_migration_date=population_data.last_migration_date,
                state_history=population_data.state_history,
                state_transition_date=population_data.state_transition_date,
                resources=population_data.resources,
                resource_modifier=population_data.resource_modifier
            )
            
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Population creation failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during population creation: {str(e)}")
    
    async def get_population_by_id(self, population_id: UUID):
        """Get population by ID"""
        population_data = self.business_service.get_population_by_id(population_id)
        if not population_data:
            return None
            
        from backend.infrastructure.models.population.models import PopulationResponse
        return PopulationResponse(
            id=population_data.id,
            name=population_data.name,
            description=population_data.description,
            status=population_data.status,
            properties=population_data.properties,
            created_at=population_data.created_at or datetime.utcnow(),
            updated_at=population_data.updated_at,
            is_active=population_data.is_active,
            population_count=population_data.population_count,
            capacity=population_data.capacity,
            growth_rate=population_data.growth_rate,
            state=population_data.state,
            previous_state=population_data.previous_state,
            casualties=population_data.casualties,
            refugees=population_data.refugees,
            last_war_impact=population_data.last_war_impact,
            last_war_date=population_data.last_war_date,
            catastrophe_deaths=population_data.catastrophe_deaths,
            catastrophe_displaced=population_data.catastrophe_displaced,
            catastrophe_injured=population_data.catastrophe_injured,
            last_catastrophe_impact=population_data.last_catastrophe_impact,
            last_catastrophe_date=population_data.last_catastrophe_date,
            shortage_deaths=population_data.shortage_deaths,
            shortage_migrants=population_data.shortage_migrants,
            last_shortage_impact=population_data.last_shortage_impact,
            last_shortage_date=population_data.last_shortage_date,
            last_migration_in=population_data.last_migration_in,
            last_migration_out=population_data.last_migration_out,
            last_migration_date=population_data.last_migration_date,
            state_history=population_data.state_history,
            state_transition_date=population_data.state_transition_date,
            resources=population_data.resources,
            resource_modifier=population_data.resource_modifier
        )
    
    async def update_population(self, population_id: UUID, request):
        """Update existing population"""
        try:
            # Convert API request to business data
            update_fields = {}
            for field in ['name', 'description', 'status', 'properties', 'population_count', 
                         'capacity', 'state', 'resources']:
                if hasattr(request, field) and getattr(request, field) is not None:
                    update_fields[field] = getattr(request, field)
            
            update_data = UpdatePopulationData(**update_fields)
            
            # Update via business service
            population_data = self.business_service.update_population(population_id, update_data)
            
            # Convert back to API response
            from backend.infrastructure.models.population.models import PopulationResponse
            return PopulationResponse(
                id=population_data.id,
                name=population_data.name,
                description=population_data.description,
                status=population_data.status,
                properties=population_data.properties,
                created_at=population_data.created_at or datetime.utcnow(),
                updated_at=population_data.updated_at or datetime.utcnow(),
                is_active=population_data.is_active,
                population_count=population_data.population_count,
                capacity=population_data.capacity,
                growth_rate=population_data.growth_rate,
                state=population_data.state,
                previous_state=population_data.previous_state,
                casualties=population_data.casualties,
                refugees=population_data.refugees,
                last_war_impact=population_data.last_war_impact,
                last_war_date=population_data.last_war_date,
                catastrophe_deaths=population_data.catastrophe_deaths,
                catastrophe_displaced=population_data.catastrophe_displaced,
                catastrophe_injured=population_data.catastrophe_injured,
                last_catastrophe_impact=population_data.last_catastrophe_impact,
                last_catastrophe_date=population_data.last_catastrophe_date,
                shortage_deaths=population_data.shortage_deaths,
                shortage_migrants=population_data.shortage_migrants,
                last_shortage_impact=population_data.last_shortage_impact,
                last_shortage_date=population_data.last_shortage_date,
                last_migration_in=population_data.last_migration_in,
                last_migration_out=population_data.last_migration_out,
                last_migration_date=population_data.last_migration_date,
                state_history=population_data.state_history,
                state_transition_date=population_data.state_transition_date,
                resources=population_data.resources,
                resource_modifier=population_data.resource_modifier
            )
            
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Population update failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during population update: {str(e)}")
    
    async def delete_population(self, population_id: UUID) -> bool:
        """Delete population"""
        try:
            return self.business_service.delete_population(population_id)
        except ValueError as e:
            # Preserve specific error type for better debugging
            raise ValueError(f"Population deletion failed: {str(e)}")
        except Exception as e:
            # Only convert unexpected errors to generic exception
            raise Exception(f"Unexpected error during population deletion: {str(e)}")
    
    async def list_populations(self, page: int = 1, size: int = 50, status_filter: Optional[str] = None, search: Optional[str] = None):
        """List populations with pagination"""
        populations_data, total = self.business_service.list_populations(page, size, status_filter, search)
        
        from backend.infrastructure.models.population.models import PopulationResponse, PopulationListResponse
        
        population_responses = []
        for population_data in populations_data:
            population_responses.append(PopulationResponse(
                id=population_data.id,
                name=population_data.name,
                description=population_data.description,
                status=population_data.status,
                properties=population_data.properties,
                created_at=population_data.created_at or datetime.utcnow(),
                updated_at=population_data.updated_at,
                is_active=population_data.is_active,
                population_count=population_data.population_count,
                capacity=population_data.capacity,
                growth_rate=population_data.growth_rate,
                state=population_data.state,
                previous_state=population_data.previous_state,
                casualties=population_data.casualties,
                refugees=population_data.refugees,
                last_war_impact=population_data.last_war_impact,
                last_war_date=population_data.last_war_date,
                catastrophe_deaths=population_data.catastrophe_deaths,
                catastrophe_displaced=population_data.catastrophe_displaced,
                catastrophe_injured=population_data.catastrophe_injured,
                last_catastrophe_impact=population_data.last_catastrophe_impact,
                last_catastrophe_date=population_data.last_catastrophe_date,
                shortage_deaths=population_data.shortage_deaths,
                shortage_migrants=population_data.shortage_migrants,
                last_shortage_impact=population_data.last_shortage_impact,
                last_shortage_date=population_data.last_shortage_date,
                last_migration_in=population_data.last_migration_in,
                last_migration_out=population_data.last_migration_out,
                last_migration_date=population_data.last_migration_date,
                state_history=population_data.state_history,
                state_transition_date=population_data.state_transition_date,
                resources=population_data.resources,
                resource_modifier=population_data.resource_modifier
            ))
        
        return PopulationListResponse(
            items=population_responses,
            total=total,
            page=page,
            size=size,
            has_next=(page * size) < total,
            has_prev=page > 1
        )
    
    async def get_population_statistics(self) -> Dict[str, Any]:
        """Get population statistics"""
        return self.business_service.get_population_statistics()


def create_population_service(db_session) -> PopulationService:
    """Factory function to create population service"""
    return PopulationService(db_session)
