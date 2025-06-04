"""
Disease API Router

FastAPI router for disease management endpoints.
Provides CRUD operations and disease-specific functionality.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from ..schemas import (
    DiseaseCreate,
    DiseaseUpdate,
    DiseaseResponse,
    DiseaseListResponse,
    DiseaseSystemStatusResponse,
    PaginationParams
)
from ..dependencies import (
    get_disease_business_service_dependency,
    get_disease_infrastructure_service_dependency,
    validate_disease_exists,
    require_disease_read_permission,
    require_disease_write_permission,
    require_disease_admin_permission,
    get_pagination_params,
    get_disease_filters
)
from backend.systems.disease import DiseaseBusinessService
from ..services.disease_infrastructure_service import DiseaseInfrastructureService

# Create router
router = APIRouter(
    prefix="/diseases",
    tags=["diseases"],
    responses={
        404: {"description": "Disease not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=DiseaseListResponse,
    summary="List diseases",
    description="Get a paginated list of diseases with optional filtering"
)
async def list_diseases(
    pagination: dict = Depends(get_pagination_params),
    filters: dict = Depends(get_disease_filters),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """List diseases with pagination and filtering"""
    try:
        diseases, total = business_service.list_diseases(
            page=pagination["page"],
            size=pagination["size"],
            status=filters.get("status"),
            disease_type=filters.get("disease_type")
        )
        
        pages = (total + pagination["size"] - 1) // pagination["size"]
        
        return DiseaseListResponse(
            diseases=[DiseaseResponse.from_orm(disease) for disease in diseases],
            total=total,
            page=pagination["page"],
            size=pagination["size"],
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list diseases: {str(e)}"
        )


@router.post(
    "/",
    response_model=DiseaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create disease",
    description="Create a new disease with specified characteristics"
)
async def create_disease(
    disease_data: DiseaseCreate,
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Create a new disease"""
    try:
        # Convert Pydantic model to business model
        from backend.systems.disease.models.disease_models import CreateDiseaseData
        
        create_data = CreateDiseaseData(
            name=disease_data.name,
            description=disease_data.description,
            disease_type=disease_data.disease_type.value,
            status=disease_data.status,
            mortality_rate=disease_data.mortality_rate,
            transmission_rate=disease_data.transmission_rate,
            incubation_days=disease_data.incubation_days,
            recovery_days=disease_data.recovery_days,
            immunity_duration_days=disease_data.immunity_duration_days,
            crowding_factor=disease_data.crowding_factor,
            hygiene_factor=disease_data.hygiene_factor,
            healthcare_factor=disease_data.healthcare_factor,
            targets_young=disease_data.targets_young,
            targets_old=disease_data.targets_old,
            targets_weak=disease_data.targets_weak,
            properties=disease_data.properties
        )
        
        created_disease = business_service.create_disease(create_data)
        return DiseaseResponse.from_orm(created_disease)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create disease: {str(e)}"
        )


@router.get(
    "/{disease_id}",
    response_model=DiseaseResponse,
    summary="Get disease",
    description="Get a specific disease by ID"
)
async def get_disease(
    disease_id: UUID = Depends(validate_disease_exists),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get a specific disease by ID"""
    try:
        disease = business_service.get_disease_by_id(disease_id)
        if not disease:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disease with ID {disease_id} not found"
            )
        
        return DiseaseResponse.from_orm(disease)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get disease: {str(e)}"
        )


@router.put(
    "/{disease_id}",
    response_model=DiseaseResponse,
    summary="Update disease",
    description="Update an existing disease"
)
async def update_disease(
    disease_data: DiseaseUpdate,
    disease_id: UUID = Depends(validate_disease_exists),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Update an existing disease"""
    try:
        # Convert Pydantic model to business model
        from backend.systems.disease.models.disease_models import UpdateDiseaseData
        
        # Only include fields that were actually provided
        update_data_dict = {}
        for field, value in disease_data.dict(exclude_unset=True).items():
            if field == "disease_type" and value is not None:
                update_data_dict[field] = value.value
            else:
                update_data_dict[field] = value
        
        update_data = UpdateDiseaseData(**update_data_dict)
        
        updated_disease = business_service.update_disease(disease_id, update_data)
        return DiseaseResponse.from_orm(updated_disease)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update disease: {str(e)}"
        )


@router.delete(
    "/{disease_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete disease",
    description="Delete a disease (admin only)"
)
async def delete_disease(
    disease_id: UUID = Depends(validate_disease_exists),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_admin_permission)
):
    """Delete a disease (admin only)"""
    try:
        success = business_service.delete_disease(disease_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disease with ID {disease_id} not found"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete disease: {str(e)}"
        )


@router.get(
    "/{disease_id}/outbreaks",
    summary="Get disease outbreaks",
    description="Get all outbreaks for a specific disease"
)
async def get_disease_outbreaks(
    disease_id: UUID = Depends(validate_disease_exists),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get all outbreaks for a specific disease"""
    try:
        # This would need to be implemented in the infrastructure service
        # For now, return a placeholder
        return {
            "disease_id": disease_id,
            "outbreaks": [],
            "message": "Outbreak listing for specific diseases not yet implemented"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get disease outbreaks: {str(e)}"
        )


@router.post(
    "/{disease_id}/outbreaks",
    status_code=status.HTTP_201_CREATED,
    summary="Create outbreak",
    description="Create a new outbreak for this disease"
)
async def create_disease_outbreak(
    disease_id: UUID = Depends(validate_disease_exists),
    region_id: Optional[UUID] = Query(None, description="Region where outbreak occurs"),
    population_id: Optional[UUID] = Query(None, description="Population affected by outbreak"),
    initial_infected: int = Query(1, ge=1, description="Initial number of infected"),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Create a new outbreak for this disease"""
    try:
        # This would use the business service to create an outbreak
        # For now, return a placeholder
        return {
            "disease_id": disease_id,
            "region_id": region_id,
            "population_id": population_id,
            "initial_infected": initial_infected,
            "message": "Outbreak creation not yet fully implemented"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create outbreak: {str(e)}"
        )


@router.get(
    "/system/status",
    response_model=DiseaseSystemStatusResponse,
    summary="Get system status",
    description="Get the overall status of the disease system"
)
async def get_system_status(
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get the overall status of the disease system"""
    try:
        from datetime import datetime
        
        status_data = infrastructure_service.get_system_status()
        
        return DiseaseSystemStatusResponse(
            status=status_data["status"],
            active_diseases=status_data["active_diseases"],
            active_outbreaks=status_data["active_outbreaks"],
            configured_profiles=status_data["configured_profiles"],
            database_connected=status_data["database_connected"],
            config_loaded=status_data.get("config_loaded", True),
            last_updated=datetime.utcnow(),
            error=status_data.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )


@router.post(
    "/system/reload-config",
    summary="Reload configuration",
    description="Reload disease configuration from files (admin only)"
)
async def reload_configuration(
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_admin_permission)
):
    """Reload disease configuration from files (admin only)"""
    try:
        infrastructure_service.reload_configuration()
        
        return {
            "message": "Disease configuration reloaded successfully",
            "timestamp": str(datetime.utcnow())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload configuration: {str(e)}"
        ) 