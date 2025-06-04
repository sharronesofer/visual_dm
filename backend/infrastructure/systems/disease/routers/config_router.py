"""
Disease Configuration API Router

FastAPI router for disease system configuration endpoints.
Provides access to environmental factors, outbreak parameters, and intervention effectiveness.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from ..schemas import (
    EnvironmentalFactorsResponse,
    OutbreakParametersResponse,
    InterventionEffectivenessResponse
)
from ..dependencies import (
    get_disease_config_loader_dependency,
    get_disease_infrastructure_service_dependency,
    require_disease_read_permission,
    require_disease_admin_permission
)
from ..config_loaders.disease_config_loader import DiseaseConfigLoader
from ..services.disease_infrastructure_service import DiseaseInfrastructureService

# Create router
router = APIRouter(
    prefix="/config",
    tags=["disease-config"],
    responses={
        404: {"description": "Configuration not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.get(
    "/environmental-factors",
    response_model=EnvironmentalFactorsResponse,
    summary="Get environmental factors",
    description="Get environmental factor configuration for disease transmission"
)
async def get_environmental_factors(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get environmental factor configuration"""
    try:
        env_factors = config_loader.get_environmental_factors()
        
        return EnvironmentalFactorsResponse(
            temperature_effects=env_factors.get("temperature_effects", {}),
            humidity_effects=env_factors.get("humidity_effects", {}),
            crowding_multipliers=env_factors.get("crowding_multipliers", {}),
            hygiene_multipliers=env_factors.get("hygiene_multipliers", {}),
            healthcare_multipliers=env_factors.get("healthcare_multipliers", {})
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get environmental factors: {str(e)}"
        )


@router.get(
    "/outbreak-parameters",
    response_model=OutbreakParametersResponse,
    summary="Get outbreak parameters",
    description="Get outbreak parameter configuration for disease progression"
)
async def get_outbreak_parameters(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get outbreak parameter configuration"""
    try:
        outbreak_params = config_loader.get_outbreak_parameters()
        stage_thresholds = config_loader.get_stage_thresholds()
        
        return OutbreakParametersResponse(
            default_initial_infected=1,
            max_outbreak_duration_days=365,
            stage_transition_thresholds=stage_thresholds,
            severity_calculation_weights={
                "mortality_rate": 0.4,
                "transmission_rate": 0.3,
                "affected_population": 0.2,
                "duration": 0.1
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get outbreak parameters: {str(e)}"
        )


@router.get(
    "/intervention-effectiveness",
    response_model=InterventionEffectivenessResponse,
    summary="Get intervention effectiveness",
    description="Get intervention effectiveness configuration for treatments"
)
async def get_intervention_effectiveness(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get intervention effectiveness configuration"""
    try:
        intervention_data = config_loader.get_intervention_effectiveness()
        
        # Build default effectiveness values if not present
        default_effectiveness = {
            "plague": 0.6,
            "fever": 0.7,
            "pox": 0.8,
            "wasting": 0.5,
            "flux": 0.6,
            "sweating_sickness": 0.4,
            "lung_rot": 0.3,
            "bone_fever": 0.5,
            "cursed_blight": 0.2,
            "magical_corruption": 0.1,
            "undead_plague": 0.1
        }
        
        return InterventionEffectivenessResponse(
            quarantine_effectiveness=intervention_data.get("quarantine", default_effectiveness),
            medicine_effectiveness=intervention_data.get("medicine", default_effectiveness),
            ritual_effectiveness=intervention_data.get("ritual", {
                "plague": 0.3,
                "fever": 0.2,
                "cursed_blight": 0.7,
                "magical_corruption": 0.8,
                "undead_plague": 0.9
            }),
            magical_healing_effectiveness=intervention_data.get("magical_healing", {
                "plague": 0.8,
                "fever": 0.9,
                "pox": 0.9,
                "wasting": 0.7,
                "flux": 0.8,
                "cursed_blight": 0.9,
                "magical_corruption": 0.9,
                "undead_plague": 0.6
            }),
            hygiene_improvement_effectiveness=intervention_data.get("hygiene", {
                "plague": 0.5,
                "fever": 0.6,
                "pox": 0.7,
                "flux": 0.8,
                "sweating_sickness": 0.6
            })
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get intervention effectiveness: {str(e)}"
        )


@router.get(
    "/crowding-multipliers",
    summary="Get crowding multipliers",
    description="Get crowding multiplier configuration"
)
async def get_crowding_multipliers(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get crowding multiplier configuration"""
    try:
        multipliers = config_loader.get_crowding_multipliers()
        
        return {
            "crowding_multipliers": multipliers,
            "description": "Multipliers applied to transmission rates based on population density"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get crowding multipliers: {str(e)}"
        )


@router.get(
    "/hygiene-multipliers",
    summary="Get hygiene multipliers",
    description="Get hygiene multiplier configuration"
)
async def get_hygiene_multipliers(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get hygiene multiplier configuration"""
    try:
        multipliers = config_loader.get_hygiene_multipliers()
        
        return {
            "hygiene_multipliers": multipliers,
            "description": "Multipliers applied to transmission rates based on hygiene levels"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get hygiene multipliers: {str(e)}"
        )


@router.get(
    "/healthcare-multipliers",
    summary="Get healthcare multipliers",
    description="Get healthcare multiplier configuration"
)
async def get_healthcare_multipliers(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get healthcare multiplier configuration"""
    try:
        multipliers = config_loader.get_healthcare_multipliers()
        
        return {
            "healthcare_multipliers": multipliers,
            "description": "Multipliers applied to mortality rates based on healthcare quality"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get healthcare multipliers: {str(e)}"
        )


@router.get(
    "/stage-thresholds",
    summary="Get stage thresholds",
    description="Get disease stage transition thresholds"
)
async def get_stage_thresholds(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get disease stage transition thresholds"""
    try:
        thresholds = config_loader.get_stage_thresholds()
        
        return {
            "stage_thresholds": thresholds,
            "description": "Infection rate thresholds for transitioning between outbreak stages"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stage thresholds: {str(e)}"
        )


@router.get(
    "/temperature-effects",
    summary="Get temperature effects",
    description="Get temperature effect configuration"
)
async def get_temperature_effects(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get temperature effect configuration"""
    try:
        effects = config_loader.get_temperature_effects()
        
        return {
            "temperature_effects": effects,
            "description": "Temperature ranges and multipliers affecting disease transmission"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get temperature effects: {str(e)}"
        )


@router.get(
    "/humidity-effects",
    summary="Get humidity effects",
    description="Get humidity effect configuration"
)
async def get_humidity_effects(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get humidity effect configuration"""
    try:
        effects = config_loader.get_humidity_effects()
        
        return {
            "humidity_effects": effects,
            "description": "Humidity ranges and multipliers affecting disease transmission"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get humidity effects: {str(e)}"
        )


@router.post(
    "/reload",
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


@router.get(
    "/validate",
    summary="Validate configuration",
    description="Validate the current disease configuration"
)
async def validate_configuration(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Validate the current disease configuration"""
    try:
        # Basic validation checks
        config = config_loader.load_config()
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        # Check if disease profiles exist
        profiles = config.get("disease_profiles", [])
        if not profiles:
            validation_results["warnings"].append("No disease profiles found")
        else:
            validation_results["info"]["profile_count"] = len(profiles)
        
        # Check environmental factors
        env_factors = config.get("environmental_factors", {})
        if not env_factors:
            validation_results["warnings"].append("No environmental factors configured")
        
        # Check outbreak parameters
        outbreak_params = config.get("outbreak_parameters", {})
        if not outbreak_params:
            validation_results["warnings"].append("No outbreak parameters configured")
        
        # Validate each profile has required fields
        required_profile_fields = ["id", "name", "disease_type"]
        for i, profile in enumerate(profiles):
            for field in required_profile_fields:
                if field not in profile:
                    validation_results["errors"].append(
                        f"Profile {i}: Missing required field '{field}'"
                    )
                    validation_results["valid"] = False
        
        return validation_results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate configuration: {str(e)}"
        )


@router.get(
    "/summary",
    summary="Get configuration summary",
    description="Get a summary of the current disease configuration"
)
async def get_configuration_summary(
    config_loader: DiseaseConfigLoader = Depends(get_disease_config_loader_dependency),
    _: bool = Depends(require_disease_read_permission)
):
    """Get a summary of the current disease configuration"""
    try:
        config = config_loader.load_config()
        
        profiles = config.get("disease_profiles", [])
        profile_types = {}
        for profile in profiles:
            disease_type = profile.get("disease_type", "unknown")
            profile_types[disease_type] = profile_types.get(disease_type, 0) + 1
        
        env_factors = config.get("environmental_factors", {})
        outbreak_params = config.get("outbreak_parameters", {})
        
        return {
            "total_profiles": len(profiles),
            "profile_types": profile_types,
            "environmental_factors_configured": bool(env_factors),
            "outbreak_parameters_configured": bool(outbreak_params),
            "crowding_levels": len(env_factors.get("crowding_multipliers", {})),
            "hygiene_levels": len(env_factors.get("hygiene_multipliers", {})),
            "healthcare_levels": len(env_factors.get("healthcare_multipliers", {})),
            "stage_thresholds": len(outbreak_params.get("stage_thresholds", {}))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get configuration summary: {str(e)}"
        ) 