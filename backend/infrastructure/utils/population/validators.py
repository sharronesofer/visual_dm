"""
Population Validation Service - Infrastructure

This module provides validation services for the population system
according to the Development Bible standards.
"""

from typing import Dict, Any, Optional
import random
from uuid import UUID


class DefaultPopulationValidationService:
    """Default implementation of population validation service"""
    
    def validate_population_data(self, population_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate population creation/update data"""
        validated_data = {}
        
        # Validate name (required)
        if not population_data.get('name'):
            raise ValueError("Population name is required")
        
        name = population_data['name'].strip()
        if len(name) < 2:
            raise ValueError("Population name must be at least 2 characters")
        if len(name) > 100:
            raise ValueError("Population name must not exceed 100 characters")
        
        validated_data['name'] = name
        
        # Validate description (optional)
        description = population_data.get('description')
        if description:
            description = description.strip()
            if len(description) > 1000:
                raise ValueError("Population description must not exceed 1000 characters")
            validated_data['description'] = description
        
        # Validate status
        valid_statuses = ['active', 'inactive', 'archived', 'displaced', 'extinct']
        status = population_data.get('status', 'active')
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        validated_data['status'] = status
        
        # Validate properties (optional dict)
        properties = population_data.get('properties', {})
        if not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary")
        validated_data['properties'] = properties
        
        # Validate population count (optional, but must be positive if provided)
        population_count = population_data.get('population_count')
        if population_count is not None:
            if not isinstance(population_count, int) or population_count < 0:
                raise ValueError("Population count must be a non-negative integer")
            if population_count > 10_000_000:  # Business rule: reasonable upper limit
                raise ValueError("Population count exceeds maximum allowed value (10,000,000)")
            validated_data['population_count'] = population_count
        
        # Validate capacity (optional, but must be positive if provided)
        capacity = population_data.get('capacity')
        if capacity is not None:
            if not isinstance(capacity, int) or capacity < 0:
                raise ValueError("Capacity must be a non-negative integer")
            if capacity > 50_000_000:  # Business rule: reasonable upper limit
                raise ValueError("Capacity exceeds maximum allowed value (50,000,000)")
            validated_data['capacity'] = capacity
        
        # Business rule: Capacity should be >= population count if both provided
        if (population_count is not None and capacity is not None and 
            population_count > capacity):
            raise ValueError("Population count cannot exceed capacity")
        
        # Validate state (optional)
        valid_states = [
            'stable', 'growing', 'declining', 'stagnant', 'migrating', 
            'under_stress', 'recovering', 'flourishing', 'critical'
        ]
        state = population_data.get('state', 'stable')
        if state not in valid_states:
            raise ValueError(f"Invalid state. Must be one of: {', '.join(valid_states)}")
        validated_data['state'] = state
        
        # Validate resources (optional dict)
        resources = population_data.get('resources', {})
        if not isinstance(resources, dict):
            raise ValueError("Resources must be a dictionary")
        
        # Validate resource values
        for resource_name, resource_value in resources.items():
            if not isinstance(resource_name, str):
                raise ValueError("Resource names must be strings")
            if not isinstance(resource_value, (int, float)):
                raise ValueError(f"Resource value for '{resource_name}' must be a number")
            if resource_value < 0:
                raise ValueError(f"Resource value for '{resource_name}' cannot be negative")
        
        validated_data['resources'] = resources
        
        return validated_data
    
    def validate_demographic_attributes(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Validate demographic attributes"""
        validated_attrs = {}
        
        # Validate population count
        population_count = attributes.get('population_count')
        if population_count is not None:
            if not isinstance(population_count, int) or population_count < 0:
                raise ValueError("Population count must be a non-negative integer")
            validated_attrs['population_count'] = population_count
        
        # Validate capacity
        capacity = attributes.get('capacity')
        if capacity is not None:
            if not isinstance(capacity, int) or capacity < 0:
                raise ValueError("Capacity must be a non-negative integer")
            validated_attrs['capacity'] = capacity
        
        # Validate growth rate
        growth_rate = attributes.get('growth_rate')
        if growth_rate is not None:
            if not isinstance(growth_rate, (int, float)):
                raise ValueError("Growth rate must be a number")
            if growth_rate < -1.0 or growth_rate > 1.0:
                raise ValueError("Growth rate must be between -1.0 and 1.0")
            validated_attrs['growth_rate'] = growth_rate
        
        # Validate state
        state = attributes.get('state')
        if state is not None:
            valid_states = [
                'stable', 'growing', 'declining', 'stagnant', 'migrating', 
                'under_stress', 'recovering', 'flourishing', 'critical'
            ]
            if state not in valid_states:
                raise ValueError(f"Invalid state. Must be one of: {', '.join(valid_states)}")
            validated_attrs['state'] = state
        
        # Validate resources
        resources = attributes.get('resources')
        if resources is not None:
            if not isinstance(resources, dict):
                raise ValueError("Resources must be a dictionary")
            
            for resource_name, resource_value in resources.items():
                if not isinstance(resource_name, str):
                    raise ValueError("Resource names must be strings")
                if not isinstance(resource_value, (int, float)):
                    raise ValueError(f"Resource value for '{resource_name}' must be a number")
                if resource_value < 0:
                    raise ValueError(f"Resource value for '{resource_name}' cannot be negative")
            
            validated_attrs['resources'] = resources
        
        return validated_attrs
    
    def generate_default_attributes(self) -> Dict[str, Any]:
        """Generate default population attributes"""
        return {
            'population_count': random.randint(100, 1000),  # Random starting population
            'capacity': random.randint(1000, 5000),  # Random capacity
            'state': 'stable',
            'resources': {
                'food': random.uniform(0.5, 1.0),  # Food availability ratio
                'water': random.uniform(0.5, 1.0),  # Water availability ratio
                'shelter': random.uniform(0.5, 1.0),  # Shelter availability ratio
                'medicine': random.uniform(0.1, 0.5)  # Medicine availability ratio
            }
        }


def create_population_validation_service() -> DefaultPopulationValidationService:
    """Factory function to create population validation service"""
    return DefaultPopulationValidationService() 