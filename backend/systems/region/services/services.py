"""
Region System Services - Pure Business Logic

This module provides business logic services for the region system
according to the Development Bible standards.
"""

import json
import os
from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime

# Import business models with string-based types per Bible
from backend.systems.region.models import (
    RegionMetadata, ContinentMetadata, RegionProfile, ResourceNode,
    HexCoordinate, DangerLevel, ClimateType, BiomeType, RegionType,
    MetropolisType, get_valid_region_types, get_valid_biome_types, 
    get_valid_resource_types
)

# Domain Models (business logic types)
class RegionData:
    """Business domain region data structure"""
    def __init__(self, 
                 id: UUID,
                 name: str,
                 description: Optional[str] = None,
                 region_type: str = 'wilderness',
                 status: str = 'active',
                 properties: Optional[Dict[str, Any]] = None,
                 dominant_biome: str = 'temperate_forest',
                 climate: str = 'temperate',
                 population: int = 0,
                 area_square_km: float = 0.0,
                 political_stability: float = 0.5,
                 wealth_level: float = 0.5,
                 danger_level: int = 2,
                 exploration_status: float = 0.0,
                 continent_id: Optional[UUID] = None):
        self.id = id
        self.name = name
        self.description = description
        self.region_type = region_type
        self.status = status
        self.properties = properties or {}
        self.dominant_biome = dominant_biome
        self.climate = climate
        self.population = population
        self.area_square_km = area_square_km
        self.political_stability = political_stability
        self.wealth_level = wealth_level
        self.danger_level = danger_level
        self.exploration_status = exploration_status
        self.continent_id = continent_id


class CreateRegionData:
    """Data structure for region creation requests"""
    def __init__(self,
                 name: str,
                 description: Optional[str] = None,
                 region_type: str = "wilderness",  # Use string per Bible
                 dominant_biome: str = "temperate_forest",  # Use string per Bible
                 climate: str = "temperate",  # Use string per Bible
                 continent_id: Optional[str] = None,
                 population: int = 0,
                 properties: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.region_type = region_type
        self.dominant_biome = dominant_biome
        self.climate = climate
        self.continent_id = continent_id
        self.population = population
        self.properties = properties or {}


class UpdateRegionData:
    """Data structure for region update requests"""
    def __init__(self,
                 name: Optional[str] = None,
                 description: Optional[str] = None,
                 region_type: Optional[str] = None,
                 population: Optional[int] = None,
                 wealth_level: Optional[float] = None,
                 political_stability: Optional[float] = None,
                 danger_level: Optional[int] = None,
                 exploration_status: Optional[float] = None,
                 properties: Optional[Dict[str, Any]] = None):
        self._updates = {}
        if name is not None:
            self._updates['name'] = name
        if description is not None:
            self._updates['description'] = description
        if region_type is not None:
            self._updates['region_type'] = region_type
        if population is not None:
            self._updates['population'] = population
        if wealth_level is not None:
            self._updates['wealth_level'] = wealth_level
        if political_stability is not None:
            self._updates['political_stability'] = political_stability
        if danger_level is not None:
            self._updates['danger_level'] = danger_level
        if exploration_status is not None:
            self._updates['exploration_status'] = exploration_status
        if properties is not None:
            self._updates['properties'] = properties
    
    def get_fields(self) -> Dict[str, Any]:
        """Get fields to update"""
        return self._updates


class ContinentData:
    """Business domain continent data structure"""
    def __init__(self,
                 id: UUID,
                 name: str,
                 description: Optional[str] = None,
                 total_area_square_km: float = 0.0,
                 political_situation: str = 'stable',
                 properties: Optional[Dict[str, Any]] = None):
        self.id = id
        self.name = name
        self.description = description
        self.total_area_square_km = total_area_square_km
        self.political_situation = political_situation
        self.properties = properties or {}


# Business Logic Protocols (dependency injection)
class RegionRepository(Protocol):
    """Protocol for region data access"""
    
    def get_by_id(self, region_id: UUID) -> Optional[RegionMetadata]:
        """Get region by ID"""
        ...
    
    def get_by_name(self, name: str) -> Optional[RegionMetadata]:
        """Get region by name"""
        ...
    
    def create(self, region_data: RegionMetadata) -> RegionMetadata:
        """Create a new region"""
        ...
    
    def update(self, region_id: UUID, update_data: Dict[str, Any]) -> Optional[RegionMetadata]:
        """Update existing region"""
        ...
    
    def delete(self, region_id: UUID) -> bool:
        """Delete region"""
        ...
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[RegionMetadata]:
        """List all regions with pagination"""
        ...
    
    def get_by_filters(self, filters: Dict[str, Any], limit: int = 100, offset: int = 0) -> List[RegionMetadata]:
        """List regions with filters"""
        ...
    
    def search_by_name(self, search_term: str, limit: int = 50) -> List[RegionMetadata]:
        """Search regions by name"""
        ...
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get region statistics"""
        ...


class ContinentRepository(Protocol):
    """Protocol for continent data access"""
    
    def get_by_id(self, continent_id: UUID) -> Optional[ContinentMetadata]:
        """Get continent by ID"""
        ...
    
    def get_by_name(self, name: str) -> Optional[ContinentMetadata]:
        """Get continent by name"""
        ...
    
    def create(self, continent_data: ContinentMetadata) -> ContinentMetadata:
        """Create a new continent"""
        ...
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[ContinentMetadata]:
        """List all continents"""
        ...
    
    def update(self, continent_id: UUID, update_data: Dict[str, Any]) -> Optional[ContinentMetadata]:
        """Update existing continent"""
        ...
    
    def delete(self, continent_id: UUID) -> bool:
        """Delete continent"""
        ...


class RegionValidationService:
    """Service for validating region data per business rules - Updated for JSON schema compliance"""
    
    def __init__(self):
        """Initialize validation service with JSON schema data"""
        self._load_json_schema_data()
    
    def _load_json_schema_data(self):
        """Load validation data from JSON schema"""
        try:
            # Path to the region types JSON schema
            schema_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../data/systems/region/region_types.json"
            )
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    self.schema_data = json.load(f)
            else:
                # Fallback to empty schema if file not found
                self.schema_data = {
                    "region_types": {},
                    "biome_types": {},
                    "climate_types": {},
                    "resource_types": {}
                }
        except Exception as e:
            print(f"Warning: Could not load JSON schema: {e}")
            self.schema_data = {
                "region_types": {},
                "biome_types": {},
                "climate_types": {},
                "resource_types": {}
            }
    
    def validate_region_data(self, region_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize region data"""
        validated_data = {}
        
        # Required fields
        if 'name' not in region_data or not region_data['name']:
            raise ValueError("Region name is required")
        
        validated_data['name'] = str(region_data['name']).strip()
        if len(validated_data['name']) > 255:
            raise ValueError("Region name must be 255 characters or less")
        
        # Optional fields with validation
        if 'description' in region_data:
            validated_data['description'] = str(region_data['description']).strip()
        
        if 'region_type' in region_data:
            validated_data['region_type'] = self._validate_region_type(region_data['region_type'])
        
        if 'dominant_biome' in region_data:
            validated_data['dominant_biome'] = self._validate_biome_type(region_data['dominant_biome'])
        
        if 'climate' in region_data:
            validated_data['climate'] = self._validate_climate_type(region_data['climate'])
        
        if 'continent_id' in region_data:
            validated_data['continent_id'] = region_data['continent_id']
        
        if 'population' in region_data:
            if region_data['population'] < 0:
                raise ValueError("Population cannot be negative")
            validated_data['population'] = region_data['population']
        
        # Validate Bible-required fields if present
        if 'level_range' in region_data:
            level_range = region_data['level_range']
            if not isinstance(level_range, (list, tuple)) or len(level_range) != 2:
                raise ValueError("Level range must be a tuple/list of [min, max]")
            if level_range[0] < 1 or level_range[1] > 20 or level_range[0] > level_range[1]:
                raise ValueError("Level range must be valid (1-20, min <= max)")
            validated_data['level_range'] = tuple(level_range)
        
        if 'tension_level' in region_data:
            tension = region_data['tension_level']
            if not 0 <= tension <= 100:
                raise ValueError("Tension level must be between 0 and 100")
            validated_data['tension_level'] = tension
        
        if 'motif_pool' in region_data:
            motif_pool = region_data['motif_pool']
            if len(motif_pool) > 3:
                raise ValueError("Motif pool cannot exceed 3 active motifs")
            if len(set(motif_pool)) != len(motif_pool):
                raise ValueError("Motif pool must contain unique motifs")
            validated_data['motif_pool'] = motif_pool
        
        if 'metropolis_type' in region_data and region_data['metropolis_type']:
            metropolis_type = region_data['metropolis_type']
            valid_types = [e.value for e in MetropolisType]
            if metropolis_type not in valid_types:
                raise ValueError(f"Invalid metropolis type. Must be one of: {', '.join(valid_types)}")
            validated_data['metropolis_type'] = metropolis_type
        
        return validated_data

    def _validate_region_type(self, region_type: str) -> str:
        """Validate region type using JSON schema data"""
        # First check against enum
        valid_types = get_valid_region_types()
        if region_type not in valid_types:
            raise ValueError(f"Invalid region type. Must be one of: {', '.join(valid_types)}")
        
        # If JSON schema is loaded, check if type has definition
        if "region_types" in self.schema_data and region_type in self.schema_data["region_types"]:
            # Type is properly defined in schema
            return region_type
        elif "region_types" in self.schema_data and self.schema_data["region_types"]:
            # Schema loaded but type not found - should warn but not fail
            print(f"Warning: Region type '{region_type}' not found in JSON schema")
        
        return region_type

    def _validate_biome_type(self, biome_type: str) -> str:
        """Validate biome type using JSON schema data"""
        # First check against enum
        valid_biomes = get_valid_biome_types()
        if biome_type not in valid_biomes:
            raise ValueError(f"Invalid biome type. Must be one of: {', '.join(valid_biomes)}")
        
        # If JSON schema is loaded, check if biome has definition
        if "biome_types" in self.schema_data and biome_type in self.schema_data["biome_types"]:
            return biome_type
        elif "biome_types" in self.schema_data and self.schema_data["biome_types"]:
            print(f"Warning: Biome type '{biome_type}' not found in JSON schema")
        
        return biome_type

    def _validate_climate_type(self, climate_type: str) -> str:
        """Validate climate type using JSON schema data"""
        # First check against enum
        try:
            ClimateType(climate_type)
        except ValueError:
            valid_climates = [e.value for e in ClimateType]
            raise ValueError(f"Invalid climate type. Must be one of: {', '.join(valid_climates)}")
        
        return climate_type

    def validate_region_type(self, region_type: str) -> bool:
        """Check if region type is valid"""
        try:
            self._validate_region_type(region_type)
            return True
        except ValueError:
            return False

    def validate_biome_type(self, biome_type: str) -> bool:
        """Check if biome type is valid"""
        try:
            self._validate_biome_type(biome_type)
            return True
        except ValueError:
            return False
    
    def get_region_type_definition(self, region_type: str) -> Optional[Dict[str, Any]]:
        """Get the full JSON schema definition for a region type"""
        if "region_types" in self.schema_data and region_type in self.schema_data["region_types"]:
            return self.schema_data["region_types"][region_type]
        return None
    
    def get_biome_type_definition(self, biome_type: str) -> Optional[Dict[str, Any]]:
        """Get the full JSON schema definition for a biome type"""
        if "biome_types" in self.schema_data and biome_type in self.schema_data["biome_types"]:
            return self.schema_data["biome_types"][biome_type]
        return None
    
    def get_resource_definitions(self) -> Dict[str, Any]:
        """Get all resource type definitions from JSON schema"""
        if "resource_types" in self.schema_data:
            return self.schema_data["resource_types"]
        return {}


class RegionBusinessService:
    """Service class for region business logic - pure business rules"""
    
    def __init__(self, 
                 repository: RegionRepository,
                 validation_service: Optional[RegionValidationService] = None):
        self.repository = repository
        self.validation_service = validation_service or RegionValidationService()

    def create_region(self, create_data: Dict[str, Any]) -> RegionMetadata:
        """Create a new region with business validation"""
        try:
            # Comprehensive validation and sanitization
            validated_data = self.validation_service.validate_region_data(create_data)
            
            # Business rule: Check for existing region with same name
            existing_region = self.repository.get_by_name(validated_data['name'])
            if existing_region:
                raise ValueError(f"Region with name '{validated_data['name']}' already exists")
            
            # Get region type definition from JSON schema for enhanced defaults
            region_type = validated_data.get('region_type', 'wilderness')
            region_def = self.validation_service.get_region_type_definition(region_type)
            
            # Get biome type definition for enhanced profile
            biome_type = validated_data.get('dominant_biome', 'temperate_forest')
            biome_def = self.validation_service.get_biome_type_definition(biome_type)
            
            # Create enhanced region profile using JSON schema data
            profile = self._create_region_profile_from_schema(biome_type, biome_def, validated_data)
            
            # Set realistic defaults from region type definition
            population = validated_data.get('population', 0)
            if population == 0 and region_def and 'population_range' in region_def:
                # Use middle of population range as default
                pop_range = region_def['population_range']
                population = (pop_range[0] + pop_range[1]) // 2
            
            # Create business entity with validated data and enhanced defaults
            region_metadata = RegionMetadata(
                id=uuid4(),
                name=validated_data['name'],
                description=validated_data.get('description'),
                region_type=region_type,
                profile=profile,
                population=population,
                hex_coordinates=[],
                danger_level=DangerLevel.SAFE,
                continent_id=UUID(validated_data['continent_id']) if validated_data.get('continent_id') else None,
                
                # Set enhanced defaults from JSON schema
                wealth_level=self._get_default_wealth_level(region_def),
                political_stability=self._get_default_political_stability(region_def),
                level_range=validated_data.get('level_range', (1, 5)),
                tension_level=validated_data.get('tension_level', 0.0),
                motif_pool=validated_data.get('motif_pool', []),
                metropolis_type=validated_data.get('metropolis_type')
            )
            
            # Generate resources based on biome
            if biome_def and 'resource_abundance' in biome_def:
                region_metadata.resource_nodes = self._generate_resources_from_biome(biome_def)
            
            # Store using repository
            return self.repository.create(region_metadata)
        except Exception as e:
            raise ValueError(f"Failed to create region: {str(e)}")
    
    def _create_region_profile_from_schema(self, biome_type: str, biome_def: Optional[Dict], validated_data: Dict) -> RegionProfile:
        """Create a RegionProfile using JSON schema biome definition"""
        profile = RegionProfile(
            dominant_biome=biome_type,
            climate=ClimateType(validated_data.get('climate', 'temperate')),
            soil_fertility=0.5,
            water_availability=0.5,
            precipitation=500.0,
            humidity=0.5,
            elevation=0.0
        )
        
        # Enhance profile with JSON schema data
        if biome_def:
            profile.fertility_modifier = biome_def.get('fertility_modifier', 1.0)
            profile.water_availability_modifier = biome_def.get('water_availability_modifier', 1.0)
            profile.traversal_difficulty = biome_def.get('traversal_difficulty', 0.5)
            profile.resource_abundance = biome_def.get('resource_abundance', [])
            profile.typical_climates = biome_def.get('typical_climates', [])
            profile.danger_sources = biome_def.get('danger_sources', [])
        
        return profile
    
    def _get_default_wealth_level(self, region_def: Optional[Dict]) -> float:
        """Get default wealth level from region type definition"""
        if region_def and 'wealth_level_range' in region_def:
            wealth_range = region_def['wealth_level_range']
            return (wealth_range[0] + wealth_range[1]) / 2
        return 0.5
    
    def _get_default_political_stability(self, region_def: Optional[Dict]) -> float:
        """Get default political stability from region type definition"""
        if region_def and 'political_stability_range' in region_def:
            stability_range = region_def['political_stability_range']
            return (stability_range[0] + stability_range[1]) / 2
        return 0.5
    
    def _generate_resources_from_biome(self, biome_def: Dict) -> List[ResourceNode]:
        """Generate resource nodes based on biome definition"""
        resources = []
        resource_definitions = self.validation_service.get_resource_definitions()
        
        if 'resource_abundance' in biome_def:
            for resource_type in biome_def['resource_abundance']:
                # Find the resource definition
                resource_def = None
                for category, category_resources in resource_definitions.items():
                    if resource_type in category_resources:
                        resource_def = category_resources[resource_type]
                        resource_def['category'] = category
                        break
                
                if resource_def:
                    # Create resource node with JSON schema data
                    resource_node = ResourceNode(
                        resource_type=resource_type,
                        abundance=0.7,  # Default abundance
                        quality=0.6,    # Default quality
                        accessibility=0.8,  # Default accessibility
                        category=resource_def.get('category'),
                        base_value=resource_def.get('base_value', 1.0),
                        weight=resource_def.get('weight', 1.0),
                        perishable=resource_def.get('perishable', False),
                        preservation_methods=resource_def.get('preservation_methods', []),
                        uses=resource_def.get('uses', [])
                    )
                    resources.append(resource_node)
        
        return resources

    def create_region_with_world_generation(self, 
                                          name: str, 
                                          biome_type: Optional[str] = None,
                                          climate_type: Optional[str] = None) -> RegionMetadata:
        """
        Create a region using world generation for procedural characteristics.
        
        This method integrates with the world generation system to create
        regions with realistic, procedurally generated properties.
        
        Args:
            name: Name for the region
            biome_type: Optional biome type string (e.g., 'forest', 'desert')
            climate_type: Optional climate type string (e.g., 'temperate', 'arid')
            
        Returns:
            RegionMetadata with procedurally generated characteristics
        """
        try:
            # Import world generation system (optional dependency)
            from backend.systems.world_generation.services import create_world_generator
            from backend.systems.region.models import BiomeType, ClimateType
            
            # Convert string types to enums if provided
            biome_enum = None
            if biome_type:
                try:
                    biome_enum = BiomeType(biome_type.upper())
                except ValueError:
                    # If invalid biome type, let world generation pick one
                    pass
            
            climate_enum = None
            if climate_type:
                try:
                    climate_enum = ClimateType(climate_type.upper())
                except ValueError:
                    # If invalid climate type, let world generation pick one
                    pass
            
            # Create world generator and generate region
            world_generator = create_world_generator()
            generated_region = world_generator.create_single_region(
                name=name,
                biome_type=biome_enum,
                climate_type=climate_enum
            )
            
            # Business rule: Check for existing region with same name
            existing_region = self.repository.get_by_name(generated_region.name)
            if existing_region:
                raise ValueError(f"Region with name '{generated_region.name}' already exists")
            
            # Store the generated region using repository
            return self.repository.create(generated_region)
            
        except ImportError:
            # Fallback to basic region creation if world generation not available
            return self.create_region({
                'name': name,
                'description': f'Basic region: {name}',
                'region_type': 'wilderness',
                'dominant_biome': biome_type or 'temperate_forest',
                'climate': climate_type or 'temperate'
            })
        except Exception as e:
            raise ValueError(f"Failed to create region with world generation: {str(e)}")

    def get_region_by_id(self, region_id: UUID) -> Optional[RegionMetadata]:
        """Get region by ID"""
        return self.repository.get_by_id(region_id)

    def get_regions(self, filters: Optional[Dict[str, Any]] = None) -> List[RegionMetadata]:
        """Get regions with optional filters"""
        if filters:
            return self.repository.get_by_filters(filters)
        return self.repository.get_all()

    def update_region(self, region_id: UUID, update_data: Dict[str, Any]) -> RegionMetadata:
        """Update region with validation"""
        try:
            # Validate the update data
            validated_data = self.validation_service.validate_region_data(update_data)
            
            # Business rule: If name is being changed, check for conflicts
            if 'name' in validated_data:
                existing_region = self.repository.get_by_name(validated_data['name'])
                if existing_region and existing_region.id != region_id:
                    raise ValueError(f"Region with name '{validated_data['name']}' already exists")
            
            # Get existing region
            existing_region = self.repository.get_by_id(region_id)
            if not existing_region:
                raise ValueError(f"Region with ID {region_id} not found")
            
            # Update timestamp
            validated_data['updated_at'] = datetime.utcnow()
            
            updated_region = self.repository.update(region_id, validated_data)
            if not updated_region:
                raise ValueError(f"Failed to update region {region_id}")
            
            return updated_region
        except Exception as e:
            raise ValueError(f"Failed to update region: {str(e)}")

    def delete_region(self, region_id: UUID) -> bool:
        """Delete region"""
        try:
            existing_region = self.repository.get_by_id(region_id)
            if not existing_region:
                raise ValueError(f"Region with ID {region_id} not found")
            
            return self.repository.delete(region_id)
        except Exception as e:
            raise ValueError(f"Failed to delete region: {str(e)}")

    def get_regions_by_continent(self, continent_id: UUID) -> List[RegionMetadata]:
        """Get all regions in a continent"""
        filters = {'continent_id': continent_id}
        return self.repository.get_by_filters(filters)

    def search_regions_by_name(self, search_term: str) -> List[RegionMetadata]:
        """Search regions by name"""
        return self.repository.search_by_name(search_term)

    def calculate_region_habitability_score(self, region: RegionMetadata) -> float:
        """Calculate overall habitability score for a region"""
        if not region.profile:
            return 0.5
        
        return region.profile.calculate_habitability()

    def assess_region_development_potential(self, region: RegionMetadata) -> Dict[str, Any]:
        """Assess development potential for a region"""
        habitability = self.calculate_region_habitability_score(region)
        resource_value = region.calculate_total_resource_value()
        
        # Calculate development factors
        geographic_factor = 1.0 - (region.profile.traversal_difficulty if region.profile else 0.5)
        population_factor = min(1.0, region.population / 10000)  # Normalize population
        stability_factor = region.political_stability
        wealth_factor = region.wealth_level
        
        # Overall development potential
        development_potential = (
            habitability * 0.3 +
            geographic_factor * 0.2 +
            population_factor * 0.2 +
            stability_factor * 0.15 +
            wealth_factor * 0.15
        )
        
        return {
            'development_potential': development_potential,
            'habitability_score': habitability,
            'resource_value': resource_value,
            'factors': {
                'geographic': geographic_factor,
                'population': population_factor,
                'stability': stability_factor,
                'wealth': wealth_factor
            },
            'recommendations': self._generate_development_recommendations(region, development_potential)
        }

    def _generate_development_recommendations(self, region: RegionMetadata, potential: float) -> List[str]:
        """Generate development recommendations based on region analysis"""
        recommendations = []
        
        if potential < 0.3:
            recommendations.append("Focus on basic infrastructure and stability")
        elif potential < 0.6:
            recommendations.append("Develop resource extraction and trade routes")
        else:
            recommendations.append("Consider advanced development projects")
        
        if region.political_stability < 0.5:
            recommendations.append("Improve political stability before major investments")
        
        if region.wealth_level < 0.4:
            recommendations.append("Seek external funding for development projects")
        
        return recommendations

    def predict_region_stability_trends(self, region: RegionMetadata) -> Dict[str, Any]:
        """Predict stability trends for a region"""
        current_stability = region.political_stability
        tension = region.tension_level
        wealth = region.wealth_level
        population_density = region.population_density
        
        # Stability factors
        factors = {
            'wealth_effect': wealth * 0.3,  # Wealth generally improves stability
            'tension_effect': -(tension / 100) * 0.4,  # Tension reduces stability
            'population_pressure': -(max(0, population_density - 100) / 1000) * 0.2,  # High density can reduce stability
            'resource_abundance': min(0.1, region.calculate_total_resource_value() / 1000)  # Resources help stability
        }
        
        # Predict trend
        stability_change = sum(factors.values())
        predicted_stability = max(0.0, min(1.0, current_stability + stability_change))
        
        trend = "stable"
        if stability_change > 0.1:
            trend = "improving"
        elif stability_change < -0.1:
            trend = "declining"
        
        return {
            'current_stability': current_stability,
            'predicted_stability': predicted_stability,
            'trend': trend,
            'factors': factors,
            'recommendations': self._generate_stability_recommendations(region, factors)
        }

    def _generate_stability_recommendations(self, region: RegionMetadata, factors: Dict[str, float]) -> List[str]:
        """Generate stability improvement recommendations"""
        recommendations = []
        
        if factors['tension_effect'] < -0.2:
            recommendations.append("Address sources of regional tension")
        
        if factors['wealth_effect'] < 0.1:
            recommendations.append("Improve economic conditions")
        
        if factors['population_pressure'] < -0.1:
            recommendations.append("Manage population density and urban planning")
        
        if region.tension_level > 50:
            recommendations.append("Consider diplomatic intervention")
        
        return recommendations


class ContinentBusinessService:
    """Service class for continent business logic"""
    
    def __init__(self, repository):
        self.repository = repository

    def create_continent(self, name: str, description: str = None) -> ContinentMetadata:
        """Create a new continent"""
        try:
            # Business rule: Check for existing continent with same name
            existing_continent = self.repository.get_by_name(name)
            if existing_continent:
                raise ValueError(f"Continent with name '{name}' already exists")
            
            continent_metadata = ContinentMetadata(
                id=uuid4(),
                name=name,
                description=description or f"Continent: {name}",
                total_area_square_km=0.0,
                political_situation="stable"
            )
            
            return self.repository.create(continent_metadata)
        except Exception as e:
            raise ValueError(f"Failed to create continent: {str(e)}")

    def get_continent_by_id(self, continent_id: UUID) -> Optional[ContinentMetadata]:
        """Get continent by ID"""
        try:
            return self.repository.get_by_id(continent_id)
        except Exception as e:
            raise ValueError(f"Failed to get continent: {str(e)}")

    def get_all_continents(self) -> List[ContinentMetadata]:
        """Get all continents"""
        try:
            return self.repository.get_all()
        except Exception as e:
            raise ValueError(f"Failed to get continents: {str(e)}")

    def update_continent(self, continent_id: UUID, update_data: Dict[str, Any]) -> ContinentMetadata:
        """Update continent"""
        try:
            # Business rule: If name is being changed, check for conflicts
            if 'name' in update_data:
                existing_continent = self.repository.get_by_name(update_data['name'])
                if existing_continent and existing_continent.id != continent_id:
                    raise ValueError(f"Continent with name '{update_data['name']}' already exists")
            
            updated_continent = self.repository.update(continent_id, update_data)
            if not updated_continent:
                raise ValueError(f"Continent with ID {continent_id} not found")
            
            return updated_continent
        except Exception as e:
            raise ValueError(f"Failed to update continent: {str(e)}")

    def delete_continent(self, continent_id: UUID) -> bool:
        """Delete continent"""
        try:
            existing_continent = self.repository.get_by_id(continent_id)
            if not existing_continent:
                raise ValueError(f"Continent with ID {continent_id} not found")
            
            return self.repository.delete(continent_id)
        except Exception as e:
            raise ValueError(f"Failed to delete continent: {str(e)}")


# Factory functions
def create_region_business_service(
    repository: RegionRepository,
    validation_service: Optional[RegionValidationService] = None
) -> RegionBusinessService:
    """Factory function to create RegionBusinessService"""
    return RegionBusinessService(repository, validation_service)


def create_continent_business_service(repository) -> ContinentBusinessService:
    """Factory function to create ContinentBusinessService"""
    return ContinentBusinessService(repository)
