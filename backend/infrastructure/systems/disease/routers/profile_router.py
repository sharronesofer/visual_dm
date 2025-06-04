"""
Disease Profile API Router

FastAPI router for disease profile management endpoints.
Provides access to disease profiles from configuration and custom database profiles.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from ..schemas import (
    DiseaseProfileResponse,
    DiseaseProfileListResponse,
    DiseaseTypeEnum
)
from ..dependencies import (
    get_disease_config_loader_dependency,
    get_disease_infrastructure_service_dependency,
    validate_disease_profile_exists,
    require_disease_read_permission,
    require_disease_write_permission,
    get_pagination_params
)
from ..config_loaders.disease_config_loader import DiseaseConfigLoader
from ..services.disease_infrastructure_service import DiseaseInfrastructureService

# Create router
router = APIRouter(
    prefix="/profiles",
    tags=["disease-profiles"],
    responses={
        404: {"description": "Disease profile not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/",
    response_model=DiseaseProfileListResponse,
    summary="List disease profiles",
    description="Get all available disease profiles from configuration"
)
async def list_disease_profiles(
    disease_type: Optional[DiseaseTypeEnum] = Query(None, description="Filter by disease type"),
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """List all available disease profiles"""
    try:
        if disease_type:
            profiles_data = config_loader.get_disease_profiles_by_type(disease_type.value)
        else:
            profiles_data = config_loader.get_disease_profiles()
        
        # Convert to response format
        profiles = []
        for profile_data in profiles_data:
            # Ensure all required fields are present with defaults
            profile = DiseaseProfileResponse(
                id=profile_data.get("id", "unknown"),
                name=profile_data.get("name", "Unknown Disease"),
                disease_type=DiseaseTypeEnum(profile_data.get("disease_type", "fever")),
                description=profile_data.get("description", "No description available"),
                transmission_modes=profile_data.get("transmission_modes", ["airborne"]),
                base_mortality_rate=profile_data.get("mortality_rate", 0.1),
                base_transmission_rate=profile_data.get("transmission_rate", 0.3),
                incubation_period={
                    "min": profile_data.get("incubation_days", 3),
                    "max": profile_data.get("incubation_days", 3)
                },
                recovery_period={
                    "min": profile_data.get("recovery_days", 7),
                    "max": profile_data.get("recovery_days", 7)
                },
                immunity_duration={
                    "min": profile_data.get("immunity_duration_days", 365),
                    "max": profile_data.get("immunity_duration_days", 365)
                },
                environmental_modifiers={
                    "crowding": profile_data.get("crowding_factor", 1.5),
                    "hygiene": profile_data.get("hygiene_factor", 1.3),
                    "healthcare": profile_data.get("healthcare_factor", 0.7),
                    "temperature": profile_data.get("temperature_factor", 1.0),
                    "humidity": profile_data.get("humidity_factor", 1.0),
                    "seasonal": profile_data.get("seasonal_multiplier", 1.0)
                },
                age_susceptibility={
                    "young": profile_data.get("targets_young", False),
                    "old": profile_data.get("targets_old", False),
                    "weak": profile_data.get("targets_weak", False),
                    "healthy": profile_data.get("targets_healthy", False)
                },
                treatment_effectiveness=profile_data.get("treatment_effectiveness", {}),
                properties=profile_data.get("properties", {})
            )
            profiles.append(profile)
        
        return DiseaseProfileListResponse(
            profiles=profiles,
            total=len(profiles)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list disease profiles: {str(e)}"
        )


@router.get(
    "/{profile_id}",
    response_model=DiseaseProfileResponse,
    summary="Get disease profile",
    description="Get a specific disease profile by ID"
)
async def get_disease_profile(
    profile_id: str = Depends(validate_disease_profile_exists),
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get a specific disease profile by ID"""
    try:
        profile_data = config_loader.get_disease_profile_by_id(profile_id)
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disease profile with ID '{profile_id}' not found"
            )
        
        # Convert to response format
        profile = DiseaseProfileResponse(
            id=profile_data.get("id", profile_id),
            name=profile_data.get("name", "Unknown Disease"),
            disease_type=DiseaseTypeEnum(profile_data.get("disease_type", "fever")),
            description=profile_data.get("description", "No description available"),
            transmission_modes=profile_data.get("transmission_modes", ["airborne"]),
            base_mortality_rate=profile_data.get("mortality_rate", 0.1),
            base_transmission_rate=profile_data.get("transmission_rate", 0.3),
            incubation_period={
                "min": profile_data.get("incubation_days", 3),
                "max": profile_data.get("incubation_days", 3)
            },
            recovery_period={
                "min": profile_data.get("recovery_days", 7),
                "max": profile_data.get("recovery_days", 7)
            },
            immunity_duration={
                "min": profile_data.get("immunity_duration_days", 365),
                "max": profile_data.get("immunity_duration_days", 365)
            },
            environmental_modifiers={
                "crowding": profile_data.get("crowding_factor", 1.5),
                "hygiene": profile_data.get("hygiene_factor", 1.3),
                "healthcare": profile_data.get("healthcare_factor", 0.7),
                "temperature": profile_data.get("temperature_factor", 1.0),
                "humidity": profile_data.get("humidity_factor", 1.0),
                "seasonal": profile_data.get("seasonal_multiplier", 1.0)
            },
            age_susceptibility={
                "young": profile_data.get("targets_young", False),
                "old": profile_data.get("targets_old", False),
                "weak": profile_data.get("targets_weak", False),
                "healthy": profile_data.get("targets_healthy", False)
            },
            treatment_effectiveness=profile_data.get("treatment_effectiveness", {}),
            properties=profile_data.get("properties", {})
        )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get disease profile: {str(e)}"
        )


@router.get(
    "/type/{disease_type}",
    response_model=DiseaseProfileListResponse,
    summary="Get profiles by type",
    description="Get all disease profiles of a specific type"
)
async def get_profiles_by_type(
    disease_type: DiseaseTypeEnum,
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get all disease profiles of a specific type"""
    try:
        profiles_data = config_loader.get_disease_profiles_by_type(disease_type.value)
        
        # Convert to response format
        profiles = []
        for profile_data in profiles_data:
            profile = DiseaseProfileResponse(
                id=profile_data.get("id", "unknown"),
                name=profile_data.get("name", "Unknown Disease"),
                disease_type=DiseaseTypeEnum(profile_data.get("disease_type", disease_type.value)),
                description=profile_data.get("description", "No description available"),
                transmission_modes=profile_data.get("transmission_modes", ["airborne"]),
                base_mortality_rate=profile_data.get("mortality_rate", 0.1),
                base_transmission_rate=profile_data.get("transmission_rate", 0.3),
                incubation_period={
                    "min": profile_data.get("incubation_days", 3),
                    "max": profile_data.get("incubation_days", 3)
                },
                recovery_period={
                    "min": profile_data.get("recovery_days", 7),
                    "max": profile_data.get("recovery_days", 7)
                },
                immunity_duration={
                    "min": profile_data.get("immunity_duration_days", 365),
                    "max": profile_data.get("immunity_duration_days", 365)
                },
                environmental_modifiers={
                    "crowding": profile_data.get("crowding_factor", 1.5),
                    "hygiene": profile_data.get("hygiene_factor", 1.3),
                    "healthcare": profile_data.get("healthcare_factor", 0.7),
                    "temperature": profile_data.get("temperature_factor", 1.0),
                    "humidity": profile_data.get("humidity_factor", 1.0),
                    "seasonal": profile_data.get("seasonal_multiplier", 1.0)
                },
                age_susceptibility={
                    "young": profile_data.get("targets_young", False),
                    "old": profile_data.get("targets_old", False),
                    "weak": profile_data.get("targets_weak", False),
                    "healthy": profile_data.get("targets_healthy", False)
                },
                treatment_effectiveness=profile_data.get("treatment_effectiveness", {}),
                properties=profile_data.get("properties", {})
            )
            profiles.append(profile)
        
        return DiseaseProfileListResponse(
            profiles=profiles,
            total=len(profiles)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get disease profiles by type: {str(e)}"
        )


@router.get(
    "/{profile_id}/outbreaks",
    summary="Get profile outbreaks",
    description="Get all outbreaks for a specific disease profile"
)
async def get_profile_outbreaks(
    profile_id: str = Depends(validate_disease_profile_exists),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get all outbreaks for a specific disease profile"""
    try:
        # This would need the outbreak repository to support profile ID lookup
        # For now, return a placeholder indicating this needs implementation
        return {
            "profile_id": profile_id,
            "outbreaks": [],
            "message": "Profile outbreak listing needs to be implemented in outbreak repository"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile outbreaks: {str(e)}"
        )


@router.post(
    "/{profile_id}/create-disease",
    summary="Create disease from profile",
    description="Create a new disease instance based on this profile"
)
async def create_disease_from_profile(
    profile_id: str = Depends(validate_disease_profile_exists),
    name: str = Query(..., description="Name for the new disease instance"),
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    infrastructure_service: DiseaseInfrastructureService = Depends(get_disease_infrastructure_service_dependency),
    _: bool = Depends(require_disease_write_permission)
):
    """Create a new disease instance based on a profile"""
    try:
        profile_data = config_loader.get_disease_profile_by_id(profile_id)
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disease profile with ID '{profile_id}' not found"
            )
        
        # Create disease data from profile
        disease_data = {
            "name": name,
            "description": profile_data.get("description", ""),
            "disease_type": profile_data.get("disease_type", "fever"),
            "status": "active",
            "mortality_rate": profile_data.get("mortality_rate", 0.1),
            "transmission_rate": profile_data.get("transmission_rate", 0.3),
            "incubation_days": profile_data.get("incubation_days", 3),
            "recovery_days": profile_data.get("recovery_days", 7),
            "immunity_duration_days": profile_data.get("immunity_duration_days", 365),
            "crowding_factor": profile_data.get("crowding_factor", 1.5),
            "hygiene_factor": profile_data.get("hygiene_factor", 1.3),
            "healthcare_factor": profile_data.get("healthcare_factor", 0.7),
            "targets_young": profile_data.get("targets_young", False),
            "targets_old": profile_data.get("targets_old", False),
            "targets_weak": profile_data.get("targets_weak", False),
            "properties": {
                **profile_data.get("properties", {}),
                "created_from_profile": profile_id
            }
        }
        
        created_disease = infrastructure_service.create_disease(disease_data)
        
        return {
            "profile_id": profile_id,
            "disease_id": created_disease["id"],
            "disease_name": created_disease["name"],
            "message": f"Disease '{name}' created successfully from profile '{profile_id}'"
        }
        
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
            detail=f"Failed to create disease from profile: {str(e)}"
        )


@router.get(
    "/{profile_id}/effectiveness/{treatment_type}",
    summary="Get treatment effectiveness",
    description="Get the effectiveness of a specific treatment for this disease profile"
)
async def get_treatment_effectiveness(
    profile_id: str = Depends(validate_disease_profile_exists),
    treatment_type: str = Query(..., description="Treatment type to check effectiveness for"),
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get the effectiveness of a specific treatment for this disease profile"""
    try:
        profile_data = config_loader.get_disease_profile_by_id(profile_id)
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disease profile with ID '{profile_id}' not found"
            )
        
        treatment_effectiveness = profile_data.get("treatment_effectiveness", {})
        effectiveness = treatment_effectiveness.get(treatment_type, 0.0)
        
        return {
            "profile_id": profile_id,
            "treatment_type": treatment_type,
            "effectiveness": effectiveness,
            "available_treatments": list(treatment_effectiveness.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get treatment effectiveness: {str(e)}"
        ) 