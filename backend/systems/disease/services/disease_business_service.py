"""
Disease System Business Service - Pure Business Logic

Core business logic service for disease operations following
Development Bible standards with protocol-based dependency injection.
"""

from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import random
import math

from ..models.disease_models import (
    DiseaseType,
    DiseaseStage,
    DiseaseProfile,
    DiseaseOutbreak,
    DiseaseData,
    CreateDiseaseData,
    UpdateDiseaseData,
    DiseaseSimulationState,
    DiseaseImpactAssessment,
    TransmissionMode,
    TreatmentType
)


# Business Logic Protocols (dependency injection)
class DiseaseRepository(Protocol):
    """Protocol for disease data access"""
    
    def get_disease_by_id(self, disease_id: UUID) -> Optional[DiseaseData]:
        """Get disease by ID"""
        ...
    
    def get_disease_by_name(self, name: str) -> Optional[DiseaseData]:
        """Get disease by name"""
        ...
    
    def create_disease(self, disease_data: DiseaseData) -> DiseaseData:
        """Create a new disease"""
        ...
    
    def update_disease(self, disease_data: DiseaseData) -> DiseaseData:
        """Update existing disease"""
        ...
    
    def delete_disease(self, disease_id: UUID) -> bool:
        """Delete disease"""
        ...
    
    def list_diseases(self, 
                     page: int = 1, 
                     size: int = 50, 
                     status: Optional[str] = None,
                     disease_type: Optional[DiseaseType] = None) -> Tuple[List[DiseaseData], int]:
        """List diseases with pagination"""
        ...


class DiseaseProfileRepository(Protocol):
    """Protocol for disease profile data access"""
    
    def get_profile_by_id(self, profile_id: UUID) -> Optional[DiseaseProfile]:
        """Get disease profile by ID"""
        ...
    
    def get_profile_by_type(self, disease_type: DiseaseType) -> Optional[DiseaseProfile]:
        """Get disease profile by type"""
        ...
    
    def list_profiles(self) -> List[DiseaseProfile]:
        """List all disease profiles"""
        ...


class OutbreakRepository(Protocol):
    """Protocol for outbreak data access"""
    
    def get_outbreak_by_id(self, outbreak_id: UUID) -> Optional[DiseaseOutbreak]:
        """Get outbreak by ID"""
        ...
    
    def create_outbreak(self, outbreak: DiseaseOutbreak) -> DiseaseOutbreak:
        """Create new outbreak"""
        ...
    
    def update_outbreak(self, outbreak: DiseaseOutbreak) -> DiseaseOutbreak:
        """Update existing outbreak"""
        ...
    
    def list_active_outbreaks(self, region_id: Optional[UUID] = None) -> List[DiseaseOutbreak]:
        """List active outbreaks"""
        ...
    
    def list_outbreaks_by_population(self, population_id: UUID) -> List[DiseaseOutbreak]:
        """List outbreaks affecting a population"""
        ...


class DiseaseValidationService(Protocol):
    """Protocol for disease validation"""
    
    def validate_disease_data(self, disease_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate disease creation/update data"""
        ...
    
    def validate_outbreak_data(self, outbreak_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate outbreak data"""
        ...


class EventDispatcher(Protocol):
    """Protocol for event dispatching"""
    
    def dispatch_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Dispatch an event"""
        ...


class DiseaseBusinessService:
    """Service class for disease business logic - pure business rules"""
    
    def __init__(self, 
                 disease_repository: DiseaseRepository,
                 profile_repository: DiseaseProfileRepository,
                 outbreak_repository: OutbreakRepository,
                 validation_service: DiseaseValidationService,
                 event_dispatcher: Optional[EventDispatcher] = None):
        self.disease_repository = disease_repository
        self.profile_repository = profile_repository
        self.outbreak_repository = outbreak_repository
        self.validation_service = validation_service
        self.event_dispatcher = event_dispatcher

    def create_disease(self, create_data: CreateDiseaseData) -> DiseaseData:
        """Create a new disease with business validation"""
        # Convert to dict for validation
        disease_data_dict = {
            'name': create_data.name,
            'description': create_data.description,
            'disease_type': create_data.disease_type.value if isinstance(create_data.disease_type, DiseaseType) else create_data.disease_type,
            'status': create_data.status,
            'properties': create_data.properties
        }
        
        # Add optional characteristics if provided
        optional_fields = [
            'mortality_rate', 'transmission_rate', 'incubation_days',
            'recovery_days', 'immunity_duration_days', 'crowding_factor',
            'hygiene_factor', 'healthcare_factor', 'targets_young',
            'targets_old', 'targets_weak'
        ]
        
        for field in optional_fields:
            value = getattr(create_data, field, None)
            if value is not None:
                disease_data_dict[field] = value
        
        # Business rule: Check for existing disease with same name
        existing_disease = self.disease_repository.get_disease_by_name(create_data.name)
        if existing_disease:
            raise ValueError(f"Disease with name '{create_data.name}' already exists")
        
        # Validate data
        validated_data = self.validation_service.validate_disease_data(disease_data_dict)
        
        # Create business entity
        disease_entity = DiseaseData(
            id=uuid4(),
            name=validated_data['name'],
            description=validated_data.get('description'),
            disease_type=DiseaseType(validated_data['disease_type']),
            status=validated_data.get('status', 'active'),
            mortality_rate=validated_data.get('mortality_rate', 0.1),
            transmission_rate=validated_data.get('transmission_rate', 0.3),
            incubation_days=validated_data.get('incubation_days', 3),
            recovery_days=validated_data.get('recovery_days', 7),
            immunity_duration_days=validated_data.get('immunity_duration_days', 365),
            crowding_factor=validated_data.get('crowding_factor', 1.5),
            hygiene_factor=validated_data.get('hygiene_factor', 1.3),
            healthcare_factor=validated_data.get('healthcare_factor', 0.7),
            targets_young=validated_data.get('targets_young', False),
            targets_old=validated_data.get('targets_old', False),
            targets_weak=validated_data.get('targets_weak', False),
            created_at=datetime.utcnow(),
            properties=validated_data.get('properties', {})
        )
        
        # Persist via repository
        created_disease = self.disease_repository.create_disease(disease_entity)
        
        # Dispatch event
        if self.event_dispatcher:
            self.event_dispatcher.dispatch_event('disease_created', {
                'disease_id': str(created_disease.id),
                'disease_type': created_disease.disease_type.value,
                'name': created_disease.name
            })
        
        return created_disease

    def get_disease_by_id(self, disease_id: UUID) -> Optional[DiseaseData]:
        """Get disease by ID"""
        return self.disease_repository.get_disease_by_id(disease_id)

    def update_disease(self, disease_id: UUID, update_data: UpdateDiseaseData) -> DiseaseData:
        """Update existing disease with business rules"""
        # Business rule: Disease must exist
        entity = self.disease_repository.get_disease_by_id(disease_id)
        if not entity:
            raise ValueError(f"Disease {disease_id} not found")
        
        # Apply updates
        update_fields = update_data.get_fields()
        if update_fields:
            for field, value in update_fields.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
            
            entity.updated_at = datetime.utcnow()
        
        updated_disease = self.disease_repository.update_disease(entity)
        
        # Dispatch event
        if self.event_dispatcher:
            self.event_dispatcher.dispatch_event('disease_updated', {
                'disease_id': str(updated_disease.id),
                'updated_fields': list(update_fields.keys())
            })
        
        return updated_disease

    def delete_disease(self, disease_id: UUID) -> bool:
        """Delete disease with business rules"""
        # Business rule: Disease must exist
        entity = self.disease_repository.get_disease_by_id(disease_id)
        if not entity:
            raise ValueError(f"Disease {disease_id} not found")
        
        # Business rule: Check for active outbreaks
        active_outbreaks = self.outbreak_repository.list_active_outbreaks()
        for outbreak in active_outbreaks:
            if outbreak.disease_profile_id == disease_id:
                raise ValueError(f"Cannot delete disease {disease_id}: active outbreaks exist")
        
        result = self.disease_repository.delete_disease(disease_id)
        
        # Dispatch event
        if self.event_dispatcher and result:
            self.event_dispatcher.dispatch_event('disease_deleted', {
                'disease_id': str(disease_id)
            })
        
        return result

    def list_diseases(self, page: int = 1, size: int = 50, 
                     status: Optional[str] = None,
                     disease_type: Optional[DiseaseType] = None) -> Tuple[List[DiseaseData], int]:
        """List diseases with pagination and filtering"""
        return self.disease_repository.list_diseases(page, size, status, disease_type)

    def introduce_outbreak(self, 
                          disease_type: DiseaseType,
                          region_id: Optional[UUID] = None,
                          population_id: Optional[UUID] = None,
                          initial_infected: int = 1,
                          environmental_factors: Optional[Dict[str, float]] = None) -> DiseaseOutbreak:
        """Introduce a new disease outbreak"""
        # Get disease profile
        profile = self.profile_repository.get_profile_by_type(disease_type)
        if not profile:
            raise ValueError(f"No profile found for disease type: {disease_type}")
        
        # Create outbreak
        outbreak = DiseaseOutbreak(
            id=uuid4(),
            disease_profile_id=profile.id,
            region_id=region_id,
            population_id=population_id,
            stage=DiseaseStage.EMERGING,
            infected_count=initial_infected,
            start_date=datetime.utcnow()
        )
        
        # Apply environmental factors
        if environmental_factors:
            outbreak.current_crowding_modifier = environmental_factors.get('crowding', 1.0)
            outbreak.current_hygiene_modifier = environmental_factors.get('hygiene', 1.0)
            outbreak.current_healthcare_modifier = environmental_factors.get('healthcare', 1.0)
            outbreak.current_seasonal_modifier = environmental_factors.get('seasonal', 1.0)
            outbreak.current_temperature_modifier = environmental_factors.get('temperature', 1.0)
            outbreak.current_humidity_modifier = environmental_factors.get('humidity', 1.0)
        
        # Persist outbreak
        created_outbreak = self.outbreak_repository.create_outbreak(outbreak)
        
        # Dispatch event
        if self.event_dispatcher:
            self.event_dispatcher.dispatch_event('outbreak_started', {
                'outbreak_id': str(created_outbreak.id),
                'disease_type': disease_type.value,
                'region_id': str(region_id) if region_id else None,
                'population_id': str(population_id) if population_id else None,
                'initial_infected': initial_infected
            })
        
        return created_outbreak

    def progress_outbreak(self, outbreak_id: UUID, 
                         total_population: int,
                         environmental_factors: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Progress an outbreak by one day"""
        # Get outbreak and profile
        outbreak = self.outbreak_repository.get_outbreak_by_id(outbreak_id)
        if not outbreak:
            raise ValueError(f"Outbreak {outbreak_id} not found")
        
        if not outbreak.is_active:
            return {"status": "inactive", "message": "Outbreak is not active"}
        
        profile = self.profile_repository.get_profile_by_id(outbreak.disease_profile_id)
        if not profile:
            raise ValueError(f"Disease profile {outbreak.disease_profile_id} not found")
        
        # Calculate new infections
        susceptible_population = total_population - outbreak.infected_count - outbreak.recovered_count - outbreak.death_count
        
        if susceptible_population <= 0:
            outbreak.stage = DiseaseStage.DECLINING
            outbreak.is_active = False
            self.outbreak_repository.update_outbreak(outbreak)
            return {"status": "completed", "message": "No susceptible population remains"}
        
        # Calculate transmission rate with modifiers
        effective_transmission_rate = self._calculate_effective_transmission_rate(profile, outbreak, environmental_factors)
        
        # Calculate new infections using SIR model principles
        new_infections = min(
            susceptible_population,
            int(outbreak.infected_count * effective_transmission_rate * (susceptible_population / total_population))
        )
        
        # Calculate recoveries and deaths from existing infected
        recovery_rate = 1.0 / profile.recovery_days
        mortality_rate = profile.mortality_rate
        
        # People who finish their infection period
        people_finishing_infection = int(outbreak.infected_count * recovery_rate)
        new_deaths = int(people_finishing_infection * mortality_rate)
        new_recoveries = people_finishing_infection - new_deaths
        
        # Update outbreak statistics
        outbreak.infected_count += new_infections - people_finishing_infection
        outbreak.recovered_count += new_recoveries
        outbreak.death_count += new_deaths
        outbreak.days_active += 1
        
        # Track peak
        if outbreak.infected_count > outbreak.peak_infected:
            outbreak.peak_infected = outbreak.infected_count
            outbreak.peak_day = outbreak.days_active
        
        # Update stage
        outbreak.stage = self._calculate_outbreak_stage(outbreak, total_population)
        
        # Check if outbreak should end
        if outbreak.infected_count <= 0:
            outbreak.is_active = False
            outbreak.end_date = datetime.utcnow()
        
        # Persist changes
        updated_outbreak = self.outbreak_repository.update_outbreak(outbreak)
        
        # Dispatch events
        if self.event_dispatcher:
            self.event_dispatcher.dispatch_event('outbreak_progressed', {
                'outbreak_id': str(outbreak_id),
                'day': outbreak.days_active,
                'new_infections': new_infections,
                'new_deaths': new_deaths,
                'new_recoveries': new_recoveries,
                'current_stage': outbreak.stage.value,
                'total_infected': outbreak.infected_count,
                'total_deaths': outbreak.death_count
            })
            
            # Stage change events
            if new_deaths > 0:
                self.event_dispatcher.dispatch_event('outbreak_deaths', {
                    'outbreak_id': str(outbreak_id),
                    'deaths': new_deaths,
                    'total_deaths': outbreak.death_count
                })
        
        return {
            'status': 'progressed',
            'day': outbreak.days_active,
            'new_infections': new_infections,
            'new_deaths': new_deaths,
            'new_recoveries': new_recoveries,
            'current_infected': outbreak.infected_count,
            'total_deaths': outbreak.death_count,
            'stage': outbreak.stage.value,
            'is_active': outbreak.is_active
        }

    def apply_treatment(self, outbreak_id: UUID, treatment_type: TreatmentType, 
                       effectiveness: float = 1.0) -> Dict[str, Any]:
        """Apply treatment to an outbreak"""
        outbreak = self.outbreak_repository.get_outbreak_by_id(outbreak_id)
        if not outbreak:
            raise ValueError(f"Outbreak {outbreak_id} not found")
        
        profile = self.profile_repository.get_profile_by_id(outbreak.disease_profile_id)
        if not profile:
            raise ValueError(f"Disease profile {outbreak.disease_profile_id} not found")
        
        # Check if treatment is effective for this disease
        base_effectiveness = profile.treatment_effectiveness.get(treatment_type, 0.5)
        actual_effectiveness = min(1.0, base_effectiveness * effectiveness)
        
        # Add treatment if not already active
        if treatment_type not in outbreak.active_treatments:
            outbreak.active_treatments.append(treatment_type)
        
        # Update treatment effectiveness
        outbreak.treatment_effectiveness = min(1.0, outbreak.treatment_effectiveness + actual_effectiveness * 0.1)
        
        # Special handling for quarantine
        if treatment_type == TreatmentType.QUARANTINE:
            outbreak.quarantine_active = True
            outbreak.quarantine_effectiveness = actual_effectiveness
        
        # Persist changes
        updated_outbreak = self.outbreak_repository.update_outbreak(outbreak)
        
        # Dispatch event
        if self.event_dispatcher:
            self.event_dispatcher.dispatch_event('treatment_applied', {
                'outbreak_id': str(outbreak_id),
                'treatment_type': treatment_type.value,
                'effectiveness': actual_effectiveness
            })
        
        return {
            'treatment_applied': treatment_type.value,
            'effectiveness': actual_effectiveness,
            'total_treatment_effectiveness': outbreak.treatment_effectiveness
        }

    def assess_outbreak_impact(self, outbreak_id: UUID) -> DiseaseImpactAssessment:
        """Assess the full impact of an outbreak"""
        outbreak = self.outbreak_repository.get_outbreak_by_id(outbreak_id)
        if not outbreak:
            raise ValueError(f"Outbreak {outbreak_id} not found")
        
        profile = self.profile_repository.get_profile_by_id(outbreak.disease_profile_id)
        if not profile:
            raise ValueError(f"Disease profile {outbreak.disease_profile_id} not found")
        
        # Calculate population impact
        total_affected = outbreak.infected_count + outbreak.recovered_count + outbreak.death_count
        population_mortality_rate = outbreak.death_count / max(1, total_affected)
        population_morbidity_rate = total_affected / max(1, total_affected + 1000)  # Estimate total population
        
        # Calculate economic impact
        productivity_loss = min(1.0, profile.productivity_impact * (total_affected / 1000))
        trade_disruption = outbreak.trade_disruption
        treatment_costs = outbreak.economic_damage
        
        # Calculate social impact (estimates based on outbreak severity)
        outbreak_severity = self._calculate_outbreak_severity(outbreak, profile)
        social_cohesion_impact = min(1.0, outbreak_severity * 0.3)
        migration_pressure = min(1.0, outbreak_severity * 0.2)
        civil_unrest_risk = min(1.0, outbreak_severity * 0.4)
        
        # Political impact
        government_stability_impact = min(1.0, outbreak_severity * 0.5)
        
        return DiseaseImpactAssessment(
            outbreak_id=outbreak_id,
            assessment_date=datetime.utcnow(),
            population_mortality_rate=population_mortality_rate,
            population_morbidity_rate=population_morbidity_rate,
            demographic_impact={'general': population_morbidity_rate},
            productivity_loss=productivity_loss,
            trade_disruption=trade_disruption,
            treatment_costs=treatment_costs,
            infrastructure_damage=0.0,  # TODO: Calculate based on outbreak duration
            social_cohesion_impact=social_cohesion_impact,
            migration_pressure=migration_pressure,
            civil_unrest_risk=civil_unrest_risk,
            government_stability_impact=government_stability_impact,
            faction_relations_impact={},  # TODO: Calculate faction impacts
            population_trauma=min(1.0, outbreak_severity * 0.6),
            economic_recovery_time=int(outbreak.days_active * 2),
            social_recovery_time=int(outbreak.days_active * 3)
        )

    def _calculate_effective_transmission_rate(self, profile: DiseaseProfile, 
                                             outbreak: DiseaseOutbreak,
                                             environmental_factors: Optional[Dict[str, float]] = None) -> float:
        """Calculate effective transmission rate with all modifiers"""
        base_rate = profile.transmission_rate
        
        # Apply outbreak modifiers
        rate = base_rate
        rate *= outbreak.current_crowding_modifier
        rate *= outbreak.current_hygiene_modifier  
        rate *= outbreak.current_healthcare_modifier
        rate *= outbreak.current_seasonal_modifier
        rate *= outbreak.current_temperature_modifier
        rate *= outbreak.current_humidity_modifier
        
        # Apply treatment effects
        if outbreak.treatment_effectiveness > 0:
            rate *= (1.0 - outbreak.treatment_effectiveness * 0.5)
        
        # Apply quarantine effects
        if outbreak.quarantine_active:
            rate *= (1.0 - outbreak.quarantine_effectiveness * 0.7)
        
        # Apply additional environmental factors
        if environmental_factors:
            for factor, multiplier in environmental_factors.items():
                rate *= multiplier
        
        return max(0.0, min(1.0, rate))

    def _calculate_outbreak_stage(self, outbreak: DiseaseOutbreak, total_population: int) -> DiseaseStage:
        """Calculate current outbreak stage"""
        infection_rate = outbreak.infected_count / max(1, total_population)
        
        if outbreak.infected_count == 0:
            return DiseaseStage.ERADICATED
        elif infection_rate < 0.001:  # Less than 0.1%
            return DiseaseStage.EMERGING
        elif infection_rate < 0.01:   # Less than 1%
            return DiseaseStage.SPREADING
        elif infection_rate < 0.05:   # Less than 5%
            return DiseaseStage.PEAK
        else:
            return DiseaseStage.DECLINING

    def _calculate_outbreak_severity(self, outbreak: DiseaseOutbreak, profile: DiseaseProfile) -> float:
        """Calculate outbreak severity score (0.0-1.0)"""
        # Factors: mortality rate, infection rate, duration
        mortality_severity = profile.mortality_rate
        infection_severity = min(1.0, outbreak.peak_infected / 1000)
        duration_severity = min(1.0, outbreak.days_active / 100)
        
        return (mortality_severity * 0.5 + infection_severity * 0.3 + duration_severity * 0.2)


def create_disease_business_service(
    disease_repository: DiseaseRepository,
    profile_repository: DiseaseProfileRepository,
    outbreak_repository: OutbreakRepository,
    validation_service: DiseaseValidationService,
    event_dispatcher: Optional[EventDispatcher] = None
) -> DiseaseBusinessService:
    """Factory function to create disease business service"""
    return DiseaseBusinessService(
        disease_repository, 
        profile_repository, 
        outbreak_repository, 
        validation_service, 
        event_dispatcher
    ) 