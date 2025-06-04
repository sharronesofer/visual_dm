"""
Disease System Facade Service

Facade service for disease operations - adapts business service to API expectations.
Compatible with existing patterns while leveraging the new business service architecture.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from ..models.disease_models import (
    DiseaseType,
    DiseaseStage,
    CreateDiseaseData,
    UpdateDiseaseData,
    TreatmentType
)
from ..services.disease_business_service import DiseaseBusinessService


class DiseaseService:
    """Facade service for disease operations - adapts business service to API expectations"""
    
    def __init__(self, db_session):
        """Initialize with database session (for compatibility with existing patterns)"""
        self.db_session = db_session
        
        # Initialize the repository and business service
        from backend.infrastructure.systems.disease.repositories.disease_repository import SQLAlchemyDiseaseRepository
        from backend.infrastructure.systems.disease.repositories.disease_profile_repository import SQLAlchemyDiseaseProfileRepository
        from backend.infrastructure.systems.disease.repositories.outbreak_repository import SQLAlchemyOutbreakRepository
        from backend.infrastructure.systems.disease.services.disease_validation_service import DefaultDiseaseValidationService
        
        self.disease_repository = SQLAlchemyDiseaseRepository(db_session)
        self.profile_repository = SQLAlchemyDiseaseProfileRepository(db_session)
        self.outbreak_repository = SQLAlchemyOutbreakRepository(db_session)
        self.validation_service = DefaultDiseaseValidationService()
        
        # TODO: Initialize event dispatcher
        self.event_dispatcher = None
        
        self.business_service = DiseaseBusinessService(
            self.disease_repository,
            self.profile_repository,
            self.outbreak_repository,
            self.validation_service,
            self.event_dispatcher
        )
    
    async def create_disease(self, request) -> 'DiseaseResponse':
        """Create a new disease"""
        try:
            # Convert API request to business data
            create_data = CreateDiseaseData(
                name=request.name,
                description=getattr(request, 'description', None),
                disease_type=getattr(request, 'disease_type', DiseaseType.FEVER),
                status=getattr(request, 'status', 'active'),
                mortality_rate=getattr(request, 'mortality_rate', None),
                transmission_rate=getattr(request, 'transmission_rate', None),
                incubation_days=getattr(request, 'incubation_days', None),
                recovery_days=getattr(request, 'recovery_days', None),
                immunity_duration_days=getattr(request, 'immunity_duration_days', None),
                crowding_factor=getattr(request, 'crowding_factor', None),
                hygiene_factor=getattr(request, 'hygiene_factor', None),
                healthcare_factor=getattr(request, 'healthcare_factor', None),
                targets_young=getattr(request, 'targets_young', None),
                targets_old=getattr(request, 'targets_old', None),
                targets_weak=getattr(request, 'targets_weak', None),
                properties=getattr(request, 'properties', {})
            )
            
            # Create via business service
            disease_data = self.business_service.create_disease(create_data)
            
            # Convert back to API response
            from backend.infrastructure.systems.disease.models.disease_models import DiseaseResponse
            return DiseaseResponse(
                id=disease_data.id,
                name=disease_data.name,
                description=disease_data.description,
                disease_type=disease_data.disease_type,
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
                created_at=disease_data.created_at or datetime.utcnow(),
                updated_at=disease_data.updated_at,
                is_active=disease_data.status == 'active',
                properties=disease_data.properties
            )
            
        except ValueError as e:
            raise Exception(f"Disease creation failed: {str(e)}")
    
    async def get_disease_by_id(self, disease_id: UUID) -> Optional['DiseaseResponse']:
        """Get disease by ID"""
        disease_data = self.business_service.get_disease_by_id(disease_id)
        if not disease_data:
            return None
            
        from backend.infrastructure.systems.disease.models.disease_models import DiseaseResponse
        return DiseaseResponse(
            id=disease_data.id,
            name=disease_data.name,
            description=disease_data.description,
            disease_type=disease_data.disease_type,
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
            created_at=disease_data.created_at or datetime.utcnow(),
            updated_at=disease_data.updated_at,
            is_active=disease_data.status == 'active',
            properties=disease_data.properties
        )
    
    async def update_disease(self, disease_id: UUID, request) -> 'DiseaseResponse':
        """Update existing disease"""
        try:
            # Convert API request to business data
            update_fields = {}
            for field in ['name', 'description', 'disease_type', 'status', 'properties',
                         'mortality_rate', 'transmission_rate', 'incubation_days',
                         'recovery_days', 'immunity_duration_days', 'crowding_factor',
                         'hygiene_factor', 'healthcare_factor', 'targets_young',
                         'targets_old', 'targets_weak']:
                if hasattr(request, field):
                    value = getattr(request, field)
                    if value is not None:
                        update_fields[field] = value
            
            update_data = UpdateDiseaseData(update_fields=update_fields)
            
            # Update via business service
            disease_data = self.business_service.update_disease(disease_id, update_data)
            
            # Convert back to API response
            from backend.infrastructure.systems.disease.models.disease_models import DiseaseResponse
            return DiseaseResponse(
                id=disease_data.id,
                name=disease_data.name,
                description=disease_data.description,
                disease_type=disease_data.disease_type,
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
                created_at=disease_data.created_at or datetime.utcnow(),
                updated_at=disease_data.updated_at or datetime.utcnow(),
                is_active=disease_data.status == 'active',
                properties=disease_data.properties
            )
            
        except ValueError as e:
            raise Exception(f"Disease update failed: {str(e)}")
    
    async def delete_disease(self, disease_id: UUID) -> bool:
        """Delete disease"""
        try:
            return self.business_service.delete_disease(disease_id)
        except ValueError as e:
            raise Exception(f"Disease deletion failed: {str(e)}")
    
    async def list_diseases(self, page: int = 1, size: int = 50, 
                           status_filter: Optional[str] = None, 
                           disease_type_filter: Optional[DiseaseType] = None):
        """List diseases with pagination"""
        diseases_data, total = self.business_service.list_diseases(page, size, status_filter, disease_type_filter)
        
        from backend.infrastructure.systems.disease.models.disease_models import DiseaseResponse, DiseaseListResponse
        
        disease_responses = []
        for disease_data in diseases_data:
            disease_responses.append(DiseaseResponse(
                id=disease_data.id,
                name=disease_data.name,
                description=disease_data.description,
                disease_type=disease_data.disease_type,
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
                created_at=disease_data.created_at or datetime.utcnow(),
                updated_at=disease_data.updated_at,
                is_active=disease_data.status == 'active',
                properties=disease_data.properties
            ))
        
        return DiseaseListResponse(
            items=disease_responses,
            total=total,
            page=page,
            size=size,
            has_next=(page * size) < total,
            has_prev=page > 1
        )
    
    # Outbreak management methods
    
    async def introduce_outbreak(self, disease_type: DiseaseType, 
                               region_id: Optional[UUID] = None,
                               population_id: Optional[UUID] = None,
                               initial_infected: int = 1,
                               environmental_factors: Optional[Dict[str, float]] = None):
        """Introduce a new disease outbreak"""
        try:
            outbreak = self.business_service.introduce_outbreak(
                disease_type, region_id, population_id, initial_infected, environmental_factors
            )
            
            from backend.infrastructure.systems.disease.models.disease_models import OutbreakResponse
            return OutbreakResponse(
                id=outbreak.id,
                disease_profile_id=outbreak.disease_profile_id,
                region_id=outbreak.region_id,
                population_id=outbreak.population_id,
                stage=outbreak.stage,
                is_active=outbreak.is_active,
                infected_count=outbreak.infected_count,
                recovered_count=outbreak.recovered_count,
                death_count=outbreak.death_count,
                immune_count=outbreak.immune_count,
                days_active=outbreak.days_active,
                peak_infected=outbreak.peak_infected,
                peak_day=outbreak.peak_day,
                active_treatments=[t.value for t in outbreak.active_treatments],
                quarantine_active=outbreak.quarantine_active,
                start_date=outbreak.start_date,
                end_date=outbreak.end_date
            )
            
        except ValueError as e:
            raise Exception(f"Outbreak introduction failed: {str(e)}")
    
    async def progress_outbreak(self, outbreak_id: UUID, total_population: int,
                              environmental_factors: Optional[Dict[str, float]] = None):
        """Progress an outbreak by one day"""
        try:
            return self.business_service.progress_outbreak(outbreak_id, total_population, environmental_factors)
        except ValueError as e:
            raise Exception(f"Outbreak progression failed: {str(e)}")
    
    async def apply_treatment(self, outbreak_id: UUID, treatment_type: TreatmentType, 
                            effectiveness: float = 1.0):
        """Apply treatment to an outbreak"""
        try:
            return self.business_service.apply_treatment(outbreak_id, treatment_type, effectiveness)
        except ValueError as e:
            raise Exception(f"Treatment application failed: {str(e)}")
    
    async def assess_outbreak_impact(self, outbreak_id: UUID):
        """Assess the full impact of an outbreak"""
        try:
            impact_assessment = self.business_service.assess_outbreak_impact(outbreak_id)
            
            return {
                'outbreak_id': str(impact_assessment.outbreak_id),
                'assessment_date': impact_assessment.assessment_date.isoformat(),
                'population_impact': {
                    'mortality_rate': impact_assessment.population_mortality_rate,
                    'morbidity_rate': impact_assessment.population_morbidity_rate,
                    'demographic_impact': impact_assessment.demographic_impact
                },
                'economic_impact': {
                    'productivity_loss': impact_assessment.productivity_loss,
                    'trade_disruption': impact_assessment.trade_disruption,
                    'treatment_costs': impact_assessment.treatment_costs,
                    'infrastructure_damage': impact_assessment.infrastructure_damage,
                    'score': impact_assessment.economic_impact_score()
                },
                'social_impact': {
                    'social_cohesion_impact': impact_assessment.social_cohesion_impact,
                    'migration_pressure': impact_assessment.migration_pressure,
                    'civil_unrest_risk': impact_assessment.civil_unrest_risk,
                    'score': impact_assessment.social_impact_score()
                },
                'political_impact': {
                    'government_stability_impact': impact_assessment.government_stability_impact,
                    'faction_relations_impact': {str(k): v for k, v in impact_assessment.faction_relations_impact.items()},
                    'score': impact_assessment.political_impact_score()
                },
                'long_term_consequences': {
                    'population_trauma': impact_assessment.population_trauma,
                    'economic_recovery_time': impact_assessment.economic_recovery_time,
                    'social_recovery_time': impact_assessment.social_recovery_time
                },
                'total_impact_score': impact_assessment.total_impact_score()
            }
            
        except ValueError as e:
            raise Exception(f"Impact assessment failed: {str(e)}")
    
    # Integration methods for other systems
    
    async def get_active_outbreaks_for_population(self, population_id: UUID):
        """Get active outbreaks affecting a population"""
        try:
            outbreaks = self.outbreak_repository.list_outbreaks_by_population(population_id)
            active_outbreaks = [o for o in outbreaks if o.is_active]
            
            from backend.infrastructure.systems.disease.models.disease_models import OutbreakResponse
            
            return [OutbreakResponse(
                id=outbreak.id,
                disease_profile_id=outbreak.disease_profile_id,
                region_id=outbreak.region_id,
                population_id=outbreak.population_id,
                stage=outbreak.stage,
                is_active=outbreak.is_active,
                infected_count=outbreak.infected_count,
                recovered_count=outbreak.recovered_count,
                death_count=outbreak.death_count,
                immune_count=outbreak.immune_count,
                days_active=outbreak.days_active,
                peak_infected=outbreak.peak_infected,
                peak_day=outbreak.peak_day,
                active_treatments=[t.value for t in outbreak.active_treatments],
                quarantine_active=outbreak.quarantine_active,
                start_date=outbreak.start_date,
                end_date=outbreak.end_date
            ) for outbreak in active_outbreaks]
            
        except Exception as e:
            raise Exception(f"Failed to get active outbreaks: {str(e)}")
    
    async def get_active_outbreaks_for_region(self, region_id: UUID):
        """Get active outbreaks in a region"""
        try:
            outbreaks = self.outbreak_repository.list_active_outbreaks(region_id)
            
            from backend.infrastructure.systems.disease.models.disease_models import OutbreakResponse
            
            return [OutbreakResponse(
                id=outbreak.id,
                disease_profile_id=outbreak.disease_profile_id,
                region_id=outbreak.region_id,
                population_id=outbreak.population_id,
                stage=outbreak.stage,
                is_active=outbreak.is_active,
                infected_count=outbreak.infected_count,
                recovered_count=outbreak.recovered_count,
                death_count=outbreak.death_count,
                immune_count=outbreak.immune_count,
                days_active=outbreak.days_active,
                peak_infected=outbreak.peak_infected,
                peak_day=outbreak.peak_day,
                active_treatments=[t.value for t in outbreak.active_treatments],
                quarantine_active=outbreak.quarantine_active,
                start_date=outbreak.start_date,
                end_date=outbreak.end_date
            ) for outbreak in outbreaks]
            
        except Exception as e:
            raise Exception(f"Failed to get regional outbreaks: {str(e)}")
    
    # Legacy compatibility methods (for existing population system integration)
    
    async def _get_by_name(self, name: str):
        """Get disease by name (legacy compatibility)"""
        return self.disease_repository.get_disease_by_name(name)
        
    async def _get_entity_by_id(self, disease_id: UUID):
        """Get disease entity by ID (legacy compatibility)"""
        return self.business_service.get_disease_by_id(disease_id) 