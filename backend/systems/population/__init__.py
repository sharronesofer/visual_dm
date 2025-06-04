"""
Population System

Manages NPC generation, population dynamics, demographics, and state transitions
for all Points of Interest (POIs) in the game world.

Key Features:
- Consolidated utility functions (no more duplicates!)
- Enhanced population growth controls to prevent over/under-population
- Comprehensive racial distribution management
- JSON-configurable parameters for easy tuning
- Clean separation of business logic from technical infrastructure
"""

# Business logic services and managers
from backend.systems.population.services.services import PopulationService
from backend.systems.population.services.demographic_service import DemographicAnalysisService
from backend.systems.population.managers.population_manager import PopulationManager, get_population_manager

# Business logic utilities and models
from backend.systems.population.utils.consolidated_utils import (
    # Population control functions
    calculate_controlled_growth_rate,
    calculate_racial_distribution,
    
    # Impact calculation functions
    calculate_war_impact,
    calculate_catastrophe_impact,
    calculate_resource_shortage_impact,
    calculate_migration_impact,
    
    # Seasonal and environmental effects
    calculate_seasonal_growth_modifier,
    calculate_seasonal_death_rate_modifier,
    
    # State management functions
    is_valid_transition,
    is_valid_state_progression,
    estimate_time_to_state,
    get_poi_status_description,
    
    # Enums and types
    RaceType,
    PopulationState,
    WarImpactSeverity,
    CatastropheType,
    
    # Configuration
    DEFAULT_POPULATION_CONFIG
)

# Demographic models for advanced calculations
from backend.systems.population.utils.demographic_models import (
    DemographicModels,
    PopulationProjectionModels,
    DemographicProfile,
    AgeGroup,
    MigrationType,
    SettlementType
)

__all__ = [
    # Core Services
    "PopulationService",
    "DemographicAnalysisService",
    
    # Manager
    "PopulationManager",
    "get_population_manager",
    
    # Core business logic functions
    "calculate_controlled_growth_rate",
    "calculate_racial_distribution",
    "calculate_war_impact", 
    "calculate_catastrophe_impact",
    "calculate_resource_shortage_impact",
    "calculate_migration_impact",
    "calculate_seasonal_growth_modifier",
    "calculate_seasonal_death_rate_modifier",
    
    # State management
    "is_valid_transition",
    "is_valid_state_progression", 
    "estimate_time_to_state",
    "get_poi_status_description",
    
    # Types and enums
    "RaceType",
    "PopulationState",
    "WarImpactSeverity",
    "CatastropheType",
    
    # Demographic models and calculations
    "DemographicModels",
    "PopulationProjectionModels",
    "DemographicProfile",
    "AgeGroup",
    "MigrationType",
    "SettlementType",
    
    # Configuration
    "DEFAULT_POPULATION_CONFIG"
]
