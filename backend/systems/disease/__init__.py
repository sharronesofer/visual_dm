"""
Disease System - Core Business Logic

A comprehensive disease and epidemic modeling system that simulates
the spread, progression, and impact of diseases across populations,
regions, and other game systems.

This system handles:
- Disease types and characteristics
- Outbreak simulation and progression
- Environmental factors affecting transmission
- Cross-system integration (population, quest, faction, economy)
- Quarantine and treatment mechanics
- Historical disease tracking

Architecture:
- Pure business logic (no infrastructure dependencies)
- Protocol-based dependency injection
- Comprehensive disease modeling
- Event-driven system integration
"""

from .services.disease_service import DiseaseService
from .models.disease_models import (
    DiseaseType,
    DiseaseStage,
    DiseaseProfile,
    DiseaseOutbreak,
    DiseaseData,
    CreateDiseaseData,
    UpdateDiseaseData
)
from .services.disease_business_service import (
    DiseaseBusinessService,
    create_disease_business_service
)

__all__ = [
    'DiseaseService',
    'DiseaseType',
    'DiseaseStage', 
    'DiseaseProfile',
    'DiseaseOutbreak',
    'DiseaseData',
    'CreateDiseaseData',
    'UpdateDiseaseData',
    'DiseaseBusinessService',
    'create_disease_business_service'
] 