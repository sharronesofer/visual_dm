"""
Disease System API Schemas

Pydantic models for API request/response validation and serialization.
These schemas define the contract between the API layer and clients.
"""

from .disease_schemas import (
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
    DiseaseSimulationResponse,
    TreatmentApplicationResponse,
    
    # System schemas
    DiseaseSystemStatusResponse,
    
    # Enums
    DiseaseTypeEnum,
    DiseaseStageEnum,
    TransmissionModeEnum,
    TreatmentTypeEnum
)

__all__ = [
    # Base schemas
    'DiseaseBase',
    'DiseaseCreate',
    'DiseaseUpdate', 
    'DiseaseResponse',
    'DiseaseListResponse',
    
    # Outbreak schemas
    'OutbreakBase',
    'OutbreakCreate',
    'OutbreakUpdate',
    'OutbreakResponse',
    'OutbreakListResponse',
    'OutbreakProgressResponse',
    
    # Profile schemas
    'DiseaseProfileResponse',
    'DiseaseProfileListResponse',
    
    # Configuration schemas
    'EnvironmentalFactorsResponse',
    'OutbreakParametersResponse',
    'InterventionEffectivenessResponse',
    
    # Analysis schemas
    'DiseaseImpactResponse',
    'DiseaseSimulationResponse',
    'TreatmentApplicationResponse',
    
    # System schemas
    'DiseaseSystemStatusResponse',
    
    # Enums
    'DiseaseTypeEnum',
    'DiseaseStageEnum',
    'TransmissionModeEnum',
    'TreatmentTypeEnum'
] 