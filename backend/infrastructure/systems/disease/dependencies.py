"""
Disease System Dependencies

FastAPI dependency injection setup for the disease system.
Provides database sessions, services, and other dependencies.
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

# Import database and service dependencies
from backend.core.database import get_db_session
from backend.systems.disease import (
    DiseaseBusinessService,
    create_disease_business_service
)
from .services.disease_infrastructure_service import (
    DiseaseInfrastructureService,
    get_disease_infrastructure_service
)
from .repositories.disease_repository import (
    DiseaseRepository,
    get_disease_repository
)
from .repositories.disease_outbreak_repository import (
    DiseaseOutbreakRepository,
    get_disease_outbreak_repository
)
from .config_loaders.disease_config_loader import (
    DiseaseConfigLoader,
    get_disease_config_loader
)


# Database Dependencies
def get_disease_db_session() -> Generator[Session, None, None]:
    """Get database session for disease operations"""
    yield from get_db_session()


# Repository Dependencies
def get_disease_repository_dependency(
    db: Session = Depends(get_disease_db_session)
) -> DiseaseRepository:
    """Get disease repository instance"""
    return get_disease_repository(db)


def get_disease_outbreak_repository_dependency(
    db: Session = Depends(get_disease_db_session)
) -> DiseaseOutbreakRepository:
    """Get disease outbreak repository instance"""
    return get_disease_outbreak_repository(db)


# Configuration Dependencies
def get_disease_config_loader_dependency() -> DiseaseConfigLoader:
    """Get disease configuration loader instance"""
    return get_disease_config_loader()


# Infrastructure Service Dependencies
def get_disease_infrastructure_service_dependency(
    db: Session = Depends(get_disease_db_session)
) -> DiseaseInfrastructureService:
    """Get disease infrastructure service instance"""
    return get_disease_infrastructure_service(db)


# Business Service Dependencies
def get_disease_business_service_dependency(
    disease_repo: DiseaseRepository = Depends(get_disease_repository_dependency),
    outbreak_repo: DiseaseOutbreakRepository = Depends(get_disease_outbreak_repository_dependency),
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency)
) -> DiseaseBusinessService:
    """Get disease business service instance with all dependencies"""
    
    # Create a simple validation service for now
    # In a full implementation, this would be a proper validation service
    class SimpleValidationService:
        def validate_disease_data(self, disease_data: dict) -> dict:
            # Basic validation - in practice this would be more comprehensive
            if not disease_data.get('name'):
                raise ValueError("Disease name is required")
            return disease_data
        
        def validate_outbreak_data(self, outbreak_data: dict) -> dict:
            # Basic validation - in practice this would be more comprehensive
            if not outbreak_data.get('disease_profile_id'):
                raise ValueError("Disease profile ID is required")
            return outbreak_data
    
    # Create a simple profile repository adapter
    class ProfileRepositoryAdapter:
        def __init__(self, config_loader: DiseaseConfigLoader):
            self.config_loader = config_loader
        
        def get_profile_by_id(self, profile_id: UUID) -> Optional[dict]:
            return self.config_loader.get_disease_profile_by_id(str(profile_id))
        
        def get_profile_by_type(self, disease_type: str) -> Optional[dict]:
            profiles = self.config_loader.get_disease_profiles_by_type(disease_type)
            return profiles[0] if profiles else None
        
        def list_profiles(self) -> list:
            return self.config_loader.get_disease_profiles()
    
    # Create business service with dependencies
    return create_disease_business_service(
        disease_repository=disease_repo,
        profile_repository=ProfileRepositoryAdapter(config_loader),
        outbreak_repository=outbreak_repo,
        validation_service=SimpleValidationService(),
        event_dispatcher=None  # Would be implemented with proper event system
    )


# Validation Dependencies
async def validate_disease_exists(
    disease_id: UUID,
    disease_repo: DiseaseRepository = Depends(get_disease_repository_dependency)
) -> UUID:
    """Validate that a disease exists and return its ID"""
    disease = disease_repo.get_disease_by_id(disease_id)
    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease with ID {disease_id} not found"
        )
    return disease_id


async def validate_outbreak_exists(
    outbreak_id: UUID,
    outbreak_repo: DiseaseOutbreakRepository = Depends(get_disease_outbreak_repository_dependency)
) -> UUID:
    """Validate that an outbreak exists and return its ID"""
    outbreak = outbreak_repo.get_outbreak_by_id(outbreak_id)
    if not outbreak:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outbreak with ID {outbreak_id} not found"
        )
    return outbreak_id


async def validate_disease_profile_exists(
    profile_id: str,
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency)
) -> str:
    """Validate that a disease profile exists and return its ID"""
    profile = config_loader.get_disease_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disease profile with ID {profile_id} not found"
        )
    return profile_id


# Permission Dependencies (placeholder for future authorization)
async def require_disease_read_permission() -> bool:
    """Require read permission for disease operations"""
    # Placeholder for future authorization system
    return True


async def require_disease_write_permission() -> bool:
    """Require write permission for disease operations"""
    # Placeholder for future authorization system
    return True


async def require_disease_admin_permission() -> bool:
    """Require admin permission for disease operations"""
    # Placeholder for future authorization system
    return True


# Pagination Dependencies
def get_pagination_params(
    page: int = 1,
    size: int = 50
) -> dict:
    """Get pagination parameters with validation"""
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be at least 1"
        )
    if size < 1 or size > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 1000"
        )
    return {"page": page, "size": size}


# Filter Dependencies
def get_disease_filters(
    disease_type: Optional[str] = None,
    status: Optional[str] = None,
    min_mortality_rate: Optional[float] = None,
    max_mortality_rate: Optional[float] = None,
    targets_young: Optional[bool] = None,
    targets_old: Optional[bool] = None,
    targets_weak: Optional[bool] = None
) -> dict:
    """Get disease filtering parameters"""
    filters = {}
    if disease_type:
        filters['disease_type'] = disease_type
    if status:
        filters['status'] = status
    if min_mortality_rate is not None:
        if not (0.0 <= min_mortality_rate <= 1.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum mortality rate must be between 0.0 and 1.0"
            )
        filters['min_mortality_rate'] = min_mortality_rate
    if max_mortality_rate is not None:
        if not (0.0 <= max_mortality_rate <= 1.0):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum mortality rate must be between 0.0 and 1.0"
            )
        filters['max_mortality_rate'] = max_mortality_rate
    if targets_young is not None:
        filters['targets_young'] = targets_young
    if targets_old is not None:
        filters['targets_old'] = targets_old
    if targets_weak is not None:
        filters['targets_weak'] = targets_weak
    
    return filters


def get_outbreak_filters(
    stage: Optional[str] = None,
    region_id: Optional[UUID] = None,
    population_id: Optional[UUID] = None,
    disease_profile_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    min_infected: Optional[int] = None,
    max_infected: Optional[int] = None
) -> dict:
    """Get outbreak filtering parameters"""
    filters = {}
    if stage:
        filters['stage'] = stage
    if region_id:
        filters['region_id'] = region_id
    if population_id:
        filters['population_id'] = population_id
    if disease_profile_id:
        filters['disease_profile_id'] = disease_profile_id
    if is_active is not None:
        filters['is_active'] = is_active
    if min_infected is not None:
        if min_infected < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum infected count must be non-negative"
            )
        filters['min_infected'] = min_infected
    if max_infected is not None:
        if max_infected < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum infected count must be non-negative"
            )
        filters['max_infected'] = max_infected
    
    return filters 