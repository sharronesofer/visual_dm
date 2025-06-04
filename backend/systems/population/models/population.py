"""
Population System Domain Models - Business Logic

This module defines clean business domain models for the population system
according to the Development Bible standards, following the faction system pattern.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class PopulationData:
    """Business domain population data structure"""
    id: UUID
    name: str
    description: Optional[str] = None
    status: str = 'active'
    properties: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: bool = True

    # Population-specific business attributes
    population_count: Optional[int] = None
    capacity: Optional[int] = None
    growth_rate: Optional[float] = None
    state: Optional[str] = None
    previous_state: Optional[str] = None
    
    # Impact tracking
    casualties: Optional[int] = None
    refugees: Optional[int] = None
    last_war_impact: Optional[Dict[str, Any]] = None
    last_war_date: Optional[str] = None
    
    catastrophe_deaths: Optional[int] = None
    catastrophe_displaced: Optional[int] = None
    catastrophe_injured: Optional[int] = None
    last_catastrophe_impact: Optional[Dict[str, Any]] = None
    last_catastrophe_date: Optional[str] = None
    
    shortage_deaths: Optional[int] = None
    shortage_migrants: Optional[int] = None
    last_shortage_impact: Optional[Dict[str, Any]] = None
    last_shortage_date: Optional[str] = None
    
    # Migration tracking
    last_migration_in: Optional[int] = None
    last_migration_out: Optional[int] = None
    last_migration_date: Optional[str] = None
    
    # State management
    state_history: Optional[List[Dict[str, Any]]] = None
    state_transition_date: Optional[str] = None
    
    # Resources
    resources: Optional[Dict[str, float]] = None
    resource_modifier: Optional[float] = None

    def __post_init__(self):
        """Initialize properties if None"""
        if self.properties is None:
            self.properties = {}
        if self.state_history is None:
            self.state_history = []
        if self.resources is None:
            self.resources = {}


@dataclass
class CreatePopulationData:
    """Business domain data for population creation"""
    name: str
    description: Optional[str] = None
    status: str = 'active'
    properties: Optional[Dict[str, Any]] = None
    
    # Population-specific creation data
    population_count: Optional[int] = None
    capacity: Optional[int] = None
    state: Optional[str] = None
    resources: Optional[Dict[str, float]] = None

    def __post_init__(self):
        """Initialize properties if None"""
        if self.properties is None:
            self.properties = {}
        if self.resources is None:
            self.resources = {}


@dataclass
class UpdatePopulationData:
    """Business domain data for population updates"""
    update_fields: Dict[str, Any] = field(default_factory=dict)

    def __init__(self, **update_fields):
        self.update_fields = update_fields

    def get_fields(self) -> Dict[str, Any]:
        """Get the update fields"""
        return self.update_fields

    def add_field(self, field_name: str, value: Any):
        """Add a field to update"""
        self.update_fields[field_name] = value

    def remove_field(self, field_name: str):
        """Remove a field from updates"""
        self.update_fields.pop(field_name, None)


# Helper functions for domain model operations
def create_population_data_from_dict(data: Dict[str, Any]) -> PopulationData:
    """Convert dictionary to PopulationData"""
    return PopulationData(
        id=data.get('id') or uuid4(),
        name=data['name'],
        description=data.get('description'),
        status=data.get('status', 'active'),
        properties=data.get('properties', {}),
        created_at=data.get('created_at'),
        updated_at=data.get('updated_at'),
        is_active=data.get('is_active', True),
        population_count=data.get('population_count'),
        capacity=data.get('capacity'),
        growth_rate=data.get('growth_rate'),
        state=data.get('state'),
        previous_state=data.get('previous_state'),
        casualties=data.get('casualties'),
        refugees=data.get('refugees'),
        last_war_impact=data.get('last_war_impact'),
        last_war_date=data.get('last_war_date'),
        catastrophe_deaths=data.get('catastrophe_deaths'),
        catastrophe_displaced=data.get('catastrophe_displaced'),
        catastrophe_injured=data.get('catastrophe_injured'),
        last_catastrophe_impact=data.get('last_catastrophe_impact'),
        last_catastrophe_date=data.get('last_catastrophe_date'),
        shortage_deaths=data.get('shortage_deaths'),
        shortage_migrants=data.get('shortage_migrants'),
        last_shortage_impact=data.get('last_shortage_impact'),
        last_shortage_date=data.get('last_shortage_date'),
        last_migration_in=data.get('last_migration_in'),
        last_migration_out=data.get('last_migration_out'),
        last_migration_date=data.get('last_migration_date'),
        state_history=data.get('state_history', []),
        state_transition_date=data.get('state_transition_date'),
        resources=data.get('resources', {}),
        resource_modifier=data.get('resource_modifier')
    )


def population_data_to_dict(population: PopulationData) -> Dict[str, Any]:
    """Convert PopulationData to dictionary"""
    return {
        'id': population.id,
        'name': population.name,
        'description': population.description,
        'status': population.status,
        'properties': population.properties,
        'created_at': population.created_at,
        'updated_at': population.updated_at,
        'is_active': population.is_active,
        'population_count': population.population_count,
        'capacity': population.capacity,
        'growth_rate': population.growth_rate,
        'state': population.state,
        'previous_state': population.previous_state,
        'casualties': population.casualties,
        'refugees': population.refugees,
        'last_war_impact': population.last_war_impact,
        'last_war_date': population.last_war_date,
        'catastrophe_deaths': population.catastrophe_deaths,
        'catastrophe_displaced': population.catastrophe_displaced,
        'catastrophe_injured': population.catastrophe_injured,
        'last_catastrophe_impact': population.last_catastrophe_impact,
        'last_catastrophe_date': population.last_catastrophe_date,
        'shortage_deaths': population.shortage_deaths,
        'shortage_migrants': population.shortage_migrants,
        'last_shortage_impact': population.last_shortage_impact,
        'last_shortage_date': population.last_shortage_date,
        'last_migration_in': population.last_migration_in,
        'last_migration_out': population.last_migration_out,
        'last_migration_date': population.last_migration_date,
        'state_history': population.state_history,
        'state_transition_date': population.state_transition_date,
        'resources': population.resources,
        'resource_modifier': population.resource_modifier
    } 