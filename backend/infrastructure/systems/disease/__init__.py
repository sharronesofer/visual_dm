"""
Disease System Infrastructure

Infrastructure layer for the disease system providing data access,
API endpoints, cross-system integration, and external service coordination.
"""

# Repositories
from .repositories import (
    DiseaseRepository,
    DiseaseOutbreakRepository,
    get_disease_repository,
    get_disease_outbreak_repository
)

# Configuration Loaders
from .config_loaders import (
    DiseaseConfigLoader,
    get_disease_config_loader
)

# Infrastructure Services
from .services import (
    DiseaseInfrastructureService,
    get_disease_infrastructure_service
)

# API Routers
from .routers import (
    disease_router,
    outbreak_router,
    profile_router,
    config_router
)

# API Schemas
from .schemas import (
    # Base schemas
    DiseaseBase,
    DiseaseCreate,
    DiseaseUpdate,
    DiseaseResponse,
    DiseaseListResponse,
    
    # Outbreak schemas
    OutbreakBase,
    OutbreakCreate,
    OutbreakUpdate,
    OutbreakResponse,
    OutbreakListResponse,
    OutbreakProgressResponse,
    
    # Profile schemas
    DiseaseProfileResponse,
    DiseaseProfileListResponse,
    
    # Configuration schemas
    EnvironmentalFactorsResponse,
    OutbreakParametersResponse,
    InterventionEffectivenessResponse,
    
    # Analysis schemas
    DiseaseImpactResponse,
    TreatmentApplicationResponse,
    DiseaseSystemStatusResponse
)

# Database Models
from .models import (
    Disease,
    DiseaseOutbreak,
    DiseaseProfile,
    DiseaseHistory,
    DiseaseImpact,
    DiseaseIntervention
)

# Cross-System Adapters
from .adapters import (
    DiseasePopulationAdapter,
    DiseaseRegionAdapter
)

# Dependencies
from .dependencies import (
    get_disease_business_service_dependency,
    get_disease_infrastructure_service_dependency,
    get_disease_config_loader_dependency,
    get_disease_repository_dependency,
    get_disease_outbreak_repository_dependency,
    validate_disease_exists,
    validate_outbreak_exists,
    validate_disease_profile_exists,
    require_disease_read_permission,
    require_disease_write_permission,
    require_disease_admin_permission
)

__all__ = [
    # Repositories
    'DiseaseRepository',
    'DiseaseOutbreakRepository',
    'get_disease_repository',
    'get_disease_outbreak_repository',
    
    # Configuration Loaders
    'DiseaseConfigLoader',
    'get_disease_config_loader',
    
    # Infrastructure Services
    'DiseaseInfrastructureService',
    'get_disease_infrastructure_service',
    
    # API Routers
    'disease_router',
    'outbreak_router',
    'profile_router',
    'config_router',
    
    # API Schemas
    'DiseaseBase',
    'DiseaseCreate',
    'DiseaseUpdate',
    'DiseaseResponse',
    'DiseaseListResponse',
    'OutbreakBase',
    'OutbreakCreate',
    'OutbreakUpdate',
    'OutbreakResponse',
    'OutbreakListResponse',
    'OutbreakProgressResponse',
    'DiseaseProfileResponse',
    'DiseaseProfileListResponse',
    'EnvironmentalFactorsResponse',
    'OutbreakParametersResponse',
    'InterventionEffectivenessResponse',
    'DiseaseImpactResponse',
    'TreatmentApplicationResponse',
    'DiseaseSystemStatusResponse',
    
    # Database Models
    'Disease',
    'DiseaseOutbreak',
    'DiseaseProfile',
    'DiseaseHistory',
    'DiseaseImpact',
    'DiseaseIntervention',
    
    # Cross-System Adapters
    'DiseasePopulationAdapter',
    'DiseaseRegionAdapter',
    
    # Dependencies
    'get_disease_business_service_dependency',
    'get_disease_infrastructure_service_dependency',
    'get_disease_config_loader_dependency',
    'get_disease_repository_dependency',
    'get_disease_outbreak_repository_dependency',
    'validate_disease_exists',
    'validate_outbreak_exists',
    'validate_disease_profile_exists',
    'require_disease_read_permission',
    'require_disease_write_permission',
    'require_disease_admin_permission'
] 