"""
POI System Services - Pure Business Logic

This module provides business logic services for the POI system
according to the Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime


# Domain Models (business logic types)
class PoiData:
    """Business domain POI data structure"""
    def __init__(self, 
                 id: UUID,
                 name: str,
                 description: Optional[str] = None,
                 poi_type: str = 'village',
                 state: str = 'active',
                 properties: Optional[Dict[str, Any]] = None,
                 population: int = 0,
                 max_population: int = 100,
                 prosperity_level: float = 0.5,
                 happiness: float = 0.5):
        self.id = id
        self.name = name
        self.description = description
        self.poi_type = poi_type
        self.state = state
        self.properties = properties or {}
        self.population = population
        self.max_population = max_population
        self.prosperity_level = prosperity_level
        self.happiness = happiness

    def get_capacity_ratio(self) -> float:
        """Get population capacity ratio"""
        if self.max_population == 0:
            return 0.0
        return self.population / self.max_population

    def is_overcrowded(self) -> bool:
        """Check if POI is overcrowded"""
        return self.get_capacity_ratio() > 0.9

    def is_underpopulated(self) -> bool:
        """Check if POI is underpopulated"""
        return self.get_capacity_ratio() < 0.3


class CreatePoiData:
    """Business domain data for POI creation"""
    def __init__(self, 
                 name: str,
                 description: Optional[str] = None,
                 poi_type: str = 'village',
                 state: str = 'active',
                 properties: Optional[Dict[str, Any]] = None,
                 population: int = 0,
                 max_population: int = 100):
        self.name = name
        self.description = description
        self.poi_type = poi_type
        self.state = state
        self.properties = properties or {}
        self.population = population
        self.max_population = max_population


class UpdatePoiData:
    """Business domain data for POI updates"""
    def __init__(self, **update_fields):
        self.update_fields = update_fields

    def get_fields(self) -> Dict[str, Any]:
        return self.update_fields


# Business Logic Protocols (dependency injection)
class PoiRepository(Protocol):
    """Protocol for POI data access"""
    
    def get_poi_by_id(self, poi_id: UUID) -> Optional[PoiData]:
        """Get POI by ID"""
        ...
    
    def get_poi_by_name(self, name: str) -> Optional[PoiData]:
        """Get POI by name"""
        ...
    
    def create_poi(self, poi_data: PoiData) -> PoiData:
        """Create a new POI"""
        ...
    
    def update_poi(self, poi_data: PoiData) -> PoiData:
        """Update existing POI"""
        ...
    
    def delete_poi(self, poi_id: UUID) -> bool:
        """Delete POI"""
        ...
    
    def list_pois(self, 
                 page: int = 1, 
                 size: int = 50, 
                 state: Optional[str] = None,
                 search: Optional[str] = None) -> Tuple[List[PoiData], int]:
        """List POIs with pagination"""
        ...
    
    def get_poi_statistics(self) -> Dict[str, Any]:
        """Get POI statistics"""
        ...


class PoiValidationService(Protocol):
    """Protocol for POI validation"""
    
    def validate_poi_data(self, poi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate POI creation/update data"""
        ...
    
    def validate_population_limits(self, population: int, max_population: int) -> bool:
        """Validate population constraints"""
        ...


class PoiBusinessService:
    """Service class for POI business logic - pure business rules"""
    
    def __init__(self, 
                 poi_repository: PoiRepository,
                 validation_service: PoiValidationService):
        self.poi_repository = poi_repository
        self.validation_service = validation_service

    def create_poi(
        self, 
        create_data: CreatePoiData,
        user_id: Optional[UUID] = None
    ) -> PoiData:
        """Create a new POI with business validation"""
        # Convert to dict for validation
        poi_data_dict = {
            'name': create_data.name,
            'description': create_data.description,
            'poi_type': create_data.poi_type,
            'state': create_data.state,
            'properties': create_data.properties,
            'population': create_data.population,
            'max_population': create_data.max_population
        }
        
        # Comprehensive validation and sanitization
        validated_data = self.validation_service.validate_poi_data(poi_data_dict)
        
        # Business rule: Check for existing POI with same name
        existing_poi = self.poi_repository.get_poi_by_name(validated_data['name'])
        if existing_poi:
            raise ValueError(f"POI with name '{validated_data['name']}' already exists")
        
        # Business rule: Validate population constraints
        population = validated_data.get('population', 0)
        max_population = validated_data.get('max_population', 100)
        if not self.validation_service.validate_population_limits(population, max_population):
            raise ValueError("Population exceeds maximum capacity")
        
        # Create business entity with validated data
        poi_entity = PoiData(
            id=uuid4(),
            name=validated_data['name'],
            description=validated_data.get('description'),
            poi_type=validated_data.get('poi_type', 'village'),
            state=validated_data.get('state', 'active'),
            properties=validated_data.get('properties', {}),
            population=population,
            max_population=max_population,
            prosperity_level=0.5,  # Default starting prosperity
            happiness=0.5  # Default starting happiness
        )
        
        # Business rule: Add user tracking if provided
        if user_id:
            poi_entity.properties = poi_entity.properties or {}
            poi_entity.properties['created_by'] = str(user_id)
        
        # Persist via repository
        return self.poi_repository.create_poi(poi_entity)

    def get_poi_by_id(self, poi_id: UUID) -> Optional[PoiData]:
        """Get POI by ID"""
        return self.poi_repository.get_poi_by_id(poi_id)

    def update_poi(
        self, 
        poi_id: UUID, 
        update_data: UpdatePoiData
    ) -> PoiData:
        """Update existing POI with business rules"""
        # Business rule: POI must exist
        entity = self.poi_repository.get_poi_by_id(poi_id)
        if not entity:
            raise ValueError(f"POI {poi_id} not found")
        
        # Apply updates with business validation
        update_fields = update_data.get_fields()
        if update_fields:
            # Business rule: Validate population changes
            if 'population' in update_fields or 'max_population' in update_fields:
                new_population = update_fields.get('population', entity.population)
                new_max_population = update_fields.get('max_population', entity.max_population)
                if not self.validation_service.validate_population_limits(new_population, new_max_population):
                    raise ValueError("Population update violates capacity constraints")
            
            # Apply updates
            for field, value in update_fields.items():
                setattr(entity, field, value)
        
        return self.poi_repository.update_poi(entity)

    def delete_poi(self, poi_id: UUID) -> bool:
        """Soft delete POI with business rules"""
        # Business rule: POI must exist
        entity = self.poi_repository.get_poi_by_id(poi_id)
        if not entity:
            raise ValueError(f"POI {poi_id} not found")
        
        return self.poi_repository.delete_poi(poi_id)

    def list_pois(
        self,
        page: int = 1,
        size: int = 50,
        state: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[PoiData], int]:
        """List POIs with pagination and filtering"""
        return self.poi_repository.list_pois(page, size, state, search)

    def get_poi_statistics(self) -> Dict[str, Any]:
        """Get POI statistics"""
        return self.poi_repository.get_poi_statistics()

    def calculate_poi_prosperity_score(self, poi: PoiData) -> float:
        """Business logic: Calculate prosperity score for a POI"""
        # Business rule: Prosperity based on population ratio and happiness
        capacity_ratio = poi.get_capacity_ratio()
        
        # Optimal capacity is around 70-80%
        if 0.7 <= capacity_ratio <= 0.8:
            capacity_score = 1.0
        elif capacity_ratio < 0.7:
            capacity_score = capacity_ratio / 0.7
        else:
            # Overcrowding reduces prosperity
            capacity_score = max(0.1, 1.0 - (capacity_ratio - 0.8) * 2)
        
        # Combine with happiness
        prosperity_score = (capacity_score * 0.6 + poi.happiness * 0.4)
        
        return round(prosperity_score, 2)

    def assess_poi_growth_potential(self, poi: PoiData) -> Dict[str, Any]:
        """Business logic: Assess growth potential of a POI"""
        capacity_ratio = poi.get_capacity_ratio()
        
        # Growth factors
        space_available = 1.0 - capacity_ratio
        happiness_factor = poi.happiness
        prosperity_factor = poi.prosperity_level
        
        # Overall growth potential
        growth_potential = (space_available * 0.4 + happiness_factor * 0.3 + prosperity_factor * 0.3)
        
        # Determine growth category
        if growth_potential >= 0.8:
            category = "high_growth"
        elif growth_potential >= 0.6:
            category = "moderate_growth"
        elif growth_potential >= 0.4:
            category = "slow_growth"
        elif growth_potential >= 0.2:
            category = "stagnant"
        else:
            category = "declining"
        
        return {
            "growth_potential": round(growth_potential, 2),
            "category": category,
            "space_available": round(space_available, 2),
            "happiness_factor": round(happiness_factor, 2),
            "prosperity_factor": round(prosperity_factor, 2),
            "recommended_actions": self._get_growth_recommendations(category, poi)
        }

    def _get_growth_recommendations(self, category: str, poi: PoiData) -> List[str]:
        """Helper method to get growth recommendations"""
        recommendations = []
        
        if category == "declining":
            recommendations.extend([
                "Investigate causes of population decline",
                "Improve basic services and infrastructure",
                "Address happiness and prosperity issues"
            ])
        elif category == "stagnant":
            recommendations.extend([
                "Invest in economic development",
                "Improve quality of life amenities",
                "Consider expansion projects"
            ])
        elif category in ["slow_growth", "moderate_growth"]:
            recommendations.extend([
                "Continue current development strategies",
                "Plan for infrastructure expansion",
                "Monitor resource availability"
            ])
        elif category == "high_growth":
            recommendations.extend([
                "Prepare for rapid expansion",
                "Ensure adequate infrastructure capacity",
                "Plan for increased resource demands"
            ])
        
        # Add specific recommendations based on POI state
        if poi.is_overcrowded():
            recommendations.append("Address overcrowding through expansion or population management")
        elif poi.is_underpopulated():
            recommendations.append("Implement population attraction initiatives")
        
        return recommendations


def create_poi_business_service(
    poi_repository: PoiRepository,
    validation_service: PoiValidationService
) -> PoiBusinessService:
    """Factory function to create POI business service"""
    return PoiBusinessService(poi_repository, validation_service)
