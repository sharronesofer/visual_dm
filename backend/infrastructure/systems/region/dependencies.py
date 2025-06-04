"""
FastAPI Dependency Injection for Region System
Manages business service lifecycles and dependency resolution
"""
from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db_session

# Import business services
from backend.systems.region.services.services import (
    RegionBusinessService, ContinentBusinessService,
    RegionValidationService, WorldGenerationService
)
from backend.systems.region.services.event_service import RegionEventBusinessService

# Import repository implementations
from backend.infrastructure.systems.region.repositories import (
    get_region_repository, get_continent_repository
)


@lru_cache()
def get_region_validation_service() -> RegionValidationService:
    """Get singleton instance of region validation service"""
    return RegionValidationService()


@lru_cache()
def get_world_generation_service() -> WorldGenerationService:
    """Get singleton instance of world generation service"""
    return WorldGenerationService()


@lru_cache()
def get_region_event_service() -> RegionEventBusinessService:
    """Get singleton instance of region event service"""
    return RegionEventBusinessService()


def get_region_business_service(
    db: Annotated[Session, Depends(get_db_session)],
    validation_service: Annotated[RegionValidationService, Depends(get_region_validation_service)],
    world_generation_service: Annotated[WorldGenerationService, Depends(get_world_generation_service)]
) -> RegionBusinessService:
    """Get region business service with injected dependencies"""
    repository = get_region_repository(db)
    return RegionBusinessService(
        repository=repository,
        validation_service=validation_service,
        world_generation_service=world_generation_service
    )


def get_continent_business_service(
    db: Annotated[Session, Depends(get_db_session)]
) -> ContinentBusinessService:
    """Get continent business service with injected dependencies"""
    repository = get_continent_repository(db)
    return ContinentBusinessService(repository=repository)


# Convenience type aliases for dependency injection
RegionService = Annotated[RegionBusinessService, Depends(get_region_business_service)]
ContinentService = Annotated[ContinentBusinessService, Depends(get_continent_business_service)]
EventService = Annotated[RegionEventBusinessService, Depends(get_region_event_service)]
ValidationService = Annotated[RegionValidationService, Depends(get_region_validation_service)]
WorldGenService = Annotated[WorldGenerationService, Depends(get_world_generation_service)] 