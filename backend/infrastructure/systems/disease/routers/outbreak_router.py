"""
Outbreak API Router

FastAPI router for disease outbreak management endpoints.
Provides outbreak tracking, progression, and intervention functionality.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from ..schemas import (
    OutbreakCreate,
    OutbreakUpdate,
    OutbreakResponse,
    OutbreakListResponse,
    OutbreakProgressResponse,
    TreatmentApplicationResponse,
    DiseaseImpactResponse,
    TreatmentTypeEnum
)
from ..dependencies import (
    get_disease_business_service_dependency,
    get_disease_infrastructure_service_dependency,
    validate_outbreak_exists,
    validate_disease_profile_exists,
    require_disease_read_permission,
    require_disease_write_permission,
    require_disease_admin_permission,
    get_pagination_params,
    get_outbreak_filters
)
from backend.systems.disease import DiseaseBusinessService
from ..services.disease_infrastructure_service import DiseaseInfrastructureService

# Create router
router = APIRouter(
    prefix="/outbreaks",
    tags=["outbreaks"],
    responses={
        404: {"description": "Outbreak not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=OutbreakListResponse,
    summary="List outbreaks",
    description="Get a paginated list of outbreaks with optional filtering"
)
async def list_outbreaks(
    pagination: dict = Depends(get_pagination_params),
    filters: dict = Depends(get_outbreak_filters),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """List outbreaks with pagination and filtering"""
    try:
        # Get outbreaks from infrastructure service
        outbreaks = []
        
        if filters.get("region_id"):
            outbreaks.extend(infrastructure_service.get_outbreaks_by_region(filters["region_id"]))
        elif filters.get("population_id"):
            outbreaks.extend(infrastructure_service.get_outbreaks_by_population(filters["population_id"]))
        elif filters.get("disease_profile_id"):
            outbreaks.extend(infrastructure_service.get_outbreaks_by_disease(filters["disease_profile_id"]))
        elif filters.get("stage"):
            outbreaks.extend(infrastructure_service.get_outbreaks_by_stage(filters["stage"]))
        elif filters.get("is_active") is not None:
            if filters["is_active"]:
                outbreaks.extend(infrastructure_service.get_active_outbreaks())
            # For inactive outbreaks, we'd need a different method
        else:
            # Get all active outbreaks by default
            outbreaks.extend(infrastructure_service.get_active_outbreaks())
        
        # Apply additional filters
        if filters.get("min_infected") is not None:
            outbreaks = [o for o in outbreaks if o.get("infected_count", 0) >= filters["min_infected"]]
        if filters.get("max_infected") is not None:
            outbreaks = [o for o in outbreaks if o.get("infected_count", 0) <= filters["max_infected"]]
        
        # Apply pagination
        total = len(outbreaks)
        start = (pagination["page"] - 1) * pagination["size"]
        end = start + pagination["size"]
        paginated_outbreaks = outbreaks[start:end]
        pages = (total + pagination["size"] - 1) // pagination["size"]
        
        return OutbreakListResponse(
            outbreaks=[OutbreakResponse(**outbreak) for outbreak in paginated_outbreaks],
            total=total,
            page=pagination["page"],
            size=pagination["size"],
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list outbreaks: {str(e)}"
        )


@router.post(
    "/",
    response_model=OutbreakResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create outbreak",
    description="Create a new disease outbreak"
)
async def create_outbreak(
    outbreak_data: OutbreakCreate,
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Create a new disease outbreak"""
    try:
        # Convert to business service format
        from backend.systems.disease.models.disease_models import DiseaseType
        
        # Get disease type from profile (this would need to be implemented)
        # For now, use a default type
        disease_type = DiseaseType.FEVER  # This should be looked up from the profile
        
        outbreak = business_service.introduce_outbreak(
            disease_type=disease_type,
            region_id=outbreak_data.region_id,
            population_id=outbreak_data.population_id,
            initial_infected=outbreak_data.infected_count,
            environmental_factors=outbreak_data.environmental_factors
        )
        
        # Convert business model back to response format
        return OutbreakResponse(
            id=outbreak.id,
            disease_profile_id=str(outbreak_data.disease_profile_id),
            region_id=outbreak_data.region_id,
            population_id=outbreak_data.population_id,
            stage=outbreak.stage,
            infected_count=outbreak.infected_count,
            recovered_count=outbreak.recovered_count,
            deceased_count=outbreak.deceased_count,
            immune_count=outbreak.immune_count,
            environmental_factors=outbreak_data.environmental_factors,
            is_active=outbreak_data.is_active,
            properties=outbreak_data.properties,
            started_at=outbreak.started_at,
            ended_at=outbreak.ended_at,
            created_at=outbreak.created_at,
            updated_at=outbreak.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create outbreak: {str(e)}"
        )


@router.get(
    "/{outbreak_id}",
    response_model=OutbreakResponse,
    summary="Get outbreak",
    description="Get a specific outbreak by ID"
)
async def get_outbreak(
    outbreak_id: UUID = Depends(validate_outbreak_exists),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get a specific outbreak by ID"""
    try:
        outbreak_data = infrastructure_service.get_outbreak_by_id(outbreak_id)
        if not outbreak_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbreak with ID {outbreak_id} not found"
            )
        
        return OutbreakResponse(**outbreak_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get outbreak: {str(e)}"
        )


@router.put(
    "/{outbreak_id}",
    response_model=OutbreakResponse,
    summary="Update outbreak",
    description="Update an existing outbreak"
)
async def update_outbreak(
    outbreak_data: OutbreakUpdate,
    outbreak_id: UUID = Depends(validate_outbreak_exists),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Update an existing outbreak"""
    try:
        # Convert to dict for infrastructure service
        update_data_dict = {}
        for field, value in outbreak_data.dict(exclude_unset=True).items():
            if field == "stage" and value is not None:
                update_data_dict[field] = value.value
            else:
                update_data_dict[field] = value
        
        updated_outbreak = infrastructure_service.update_outbreak(outbreak_id, update_data_dict)
        if not updated_outbreak:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbreak with ID {outbreak_id} not found"
            )
        
        return OutbreakResponse(**updated_outbreak)
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update outbreak: {str(e)}"
        )


@router.delete(
    "/{outbreak_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete outbreak",
    description="Delete an outbreak (admin only)"
)
async def delete_outbreak(
    outbreak_id: UUID = Depends(validate_outbreak_exists),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_admin_permission)
):
    """Delete an outbreak (admin only)"""
    try:
        success = infrastructure_service.delete_outbreak(outbreak_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbreak with ID {outbreak_id} not found"
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
            detail=f"Failed to delete outbreak: {str(e)}"
        )


@router.post(
    "/{outbreak_id}/progress",
    response_model=OutbreakProgressResponse,
    summary="Progress outbreak",
    description="Advance outbreak by one time step"
)
async def progress_outbreak(
    outbreak_id: UUID = Depends(validate_outbreak_exists),
    total_population: int = Query(..., ge=1, description="Total population size"),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Progress an outbreak by one time step"""
    try:
        progress_data = business_service.progress_outbreak(
            outbreak_id=outbreak_id,
            total_population=total_population
        )
        
        return OutbreakProgressResponse(
            outbreak_id=outbreak_id,
            previous_stage=progress_data.get("previous_stage", "emerging"),
            current_stage=progress_data.get("current_stage", "emerging"),
            new_infections=progress_data.get("new_infections", 0),
            new_recoveries=progress_data.get("new_recoveries", 0),
            new_deaths=progress_data.get("new_deaths", 0),
            transmission_rate=progress_data.get("transmission_rate", 0.0),
            severity_score=progress_data.get("severity_score", 0.0),
            stage_changed=progress_data.get("stage_changed", False),
            environmental_impact=progress_data.get("environmental_impact", {})
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to progress outbreak: {str(e)}"
        )


@router.post(
    "/{outbreak_id}/treatment",
    response_model=TreatmentApplicationResponse,
    summary="Apply treatment",
    description="Apply a treatment or intervention to an outbreak"
)
async def apply_treatment(
    outbreak_id: UUID = Depends(validate_outbreak_exists),
    treatment_type: TreatmentTypeEnum = Query(..., description="Type of treatment to apply"),
    effectiveness: float = Query(1.0, ge=0.0, le=1.0, description="Treatment effectiveness modifier"),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Apply a treatment or intervention to an outbreak"""
    try:
        from backend.systems.disease.models.disease_models import TreatmentType
        
        # Convert enum value
        treatment_type_business = TreatmentType(treatment_type.value)
        
        treatment_data = business_service.apply_treatment(
            outbreak_id=outbreak_id,
            treatment_type=treatment_type_business,
            effectiveness=effectiveness
        )
        
        return TreatmentApplicationResponse(
            outbreak_id=outbreak_id,
            treatment_type=treatment_type,
            effectiveness=effectiveness,
            infected_before=treatment_data.get("infected_before", 0),
            infected_after=treatment_data.get("infected_after", 0),
            transmission_reduction=treatment_data.get("transmission_reduction", 0.0),
            mortality_reduction=treatment_data.get("mortality_reduction", 0.0),
            cost=treatment_data.get("cost", 0.0),
            success=treatment_data.get("success", True)
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply treatment: {str(e)}"
        )


@router.post(
    "/{outbreak_id}/end",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End outbreak",
    description="Manually end an outbreak"
)
async def end_outbreak(
    outbreak_id: UUID = Depends(validate_outbreak_exists),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Manually end an outbreak"""
    try:
        success = infrastructure_service.end_outbreak(outbreak_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Outbreak with ID {outbreak_id} not found"
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
            detail=f"Failed to end outbreak: {str(e)}"
        )


@router.get(
    "/{outbreak_id}/impact",
    response_model=DiseaseImpactResponse,
    summary="Get outbreak impact",
    description="Get the impact assessment for an outbreak"
)
async def get_outbreak_impact(
    outbreak_id: UUID = Depends(validate_outbreak_exists),
    business_service: DiseaseBusinessService = Depends(get_disease_business_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get the impact assessment for an outbreak"""
    try:
        impact_data = business_service.assess_outbreak_impact(outbreak_id)
        
        return DiseaseImpactResponse(
            outbreak_id=outbreak_id,
            total_affected=impact_data.total_affected,
            mortality_rate=impact_data.mortality_rate,
            economic_impact=impact_data.economic_impact,
            social_impact=impact_data.social_impact,
            duration_days=impact_data.duration_days,
            peak_infected=impact_data.peak_infected,
            severity_classification=impact_data.severity_classification,
            affected_demographics=impact_data.affected_demographics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get outbreak impact: {str(e)}"
        )


@router.get(
    "/active",
    response_model=OutbreakListResponse,
    summary="Get active outbreaks",
    description="Get all currently active outbreaks"
)
async def get_active_outbreaks(
    pagination: dict = Depends(get_pagination_params),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get all currently active outbreaks"""
    try:
        outbreaks = infrastructure_service.get_active_outbreaks()
        
        # Apply pagination
        total = len(outbreaks)
        start = (pagination["page"] - 1) * pagination["size"]
        end = start + pagination["size"]
        paginated_outbreaks = outbreaks[start:end]
        pages = (total + pagination["size"] - 1) // pagination["size"]
        
        return OutbreakListResponse(
            outbreaks=[OutbreakResponse(**outbreak) for outbreak in paginated_outbreaks],
            total=total,
            page=pagination["page"],
            size=pagination["size"],
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get active outbreaks: {str(e)}"
        ) 