"""
Population Validation Service

Technical validation implementation for population data validation.
"""

import logging
import random
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class PopulationValidationService:
    """
    Technical validation service for population data.
    
    Implements the validation protocol expected by the business services.
    """
    
    def validate_population_data(self, population_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize population creation/update data.
        
        Args:
            population_data: Raw population data to validate
            
        Returns:
            Validated and sanitized population data
        """
        validated = {}
        
        # Validate name
        name = population_data.get("name", "").strip()
        if not name:
            raise ValueError("Population name is required")
        if len(name) > 255:
            raise ValueError("Population name must be 255 characters or less")
        validated["name"] = name
        
        # Validate description
        description = population_data.get("description")
        if description is not None:
            description = str(description).strip()
            if len(description) > 1000:
                raise ValueError("Description must be 1000 characters or less")
            validated["description"] = description if description else None
        
        # Validate status
        status = population_data.get("status", "active")
        valid_statuses = ["active", "inactive", "pending", "archived"]
        if status not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        validated["status"] = status
        
        # Validate properties
        properties = population_data.get("properties", {})
        if not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary")
        validated["properties"] = properties
        
        # Validate hidden attributes if present
        hidden_attrs = {}
        for attr_name in ["hidden_ambition", "hidden_integrity", "hidden_discipline", 
                         "hidden_impulsivity", "hidden_pragmatism", "hidden_resilience"]:
            if attr_name in population_data:
                value = population_data[attr_name]
                if not isinstance(value, (int, float)):
                    raise ValueError(f"{attr_name} must be a number")
                if not (1 <= value <= 10):
                    raise ValueError(f"{attr_name} must be between 1 and 10")
                hidden_attrs[attr_name] = int(value)
        
        # Add validated hidden attributes
        validated.update(hidden_attrs)
        
        return validated
    
    def validate_hidden_attributes(self, attributes: Dict[str, int]) -> Dict[str, int]:
        """
        Validate hidden attributes and fill in missing ones.
        
        Args:
            attributes: Dictionary of hidden attributes
            
        Returns:
            Complete set of validated hidden attributes
        """
        validated = {}
        required_attrs = ["hidden_ambition", "hidden_integrity", "hidden_discipline", 
                         "hidden_impulsivity", "hidden_pragmatism", "hidden_resilience"]
        
        for attr_name in required_attrs:
            if attr_name in attributes:
                value = attributes[attr_name]
                if not isinstance(value, (int, float)):
                    raise ValueError(f"{attr_name} must be a number")
                if not (1 <= value <= 10):
                    raise ValueError(f"{attr_name} must be between 1 and 10")
                validated[attr_name] = int(value)
            else:
                # Generate random value for missing attribute
                validated[attr_name] = random.randint(1, 10)
        
        return validated
    
    def generate_hidden_attributes(self) -> Dict[str, int]:
        """
        Generate random hidden attributes.
        
        Returns:
            Dictionary of randomly generated hidden attributes
        """
        return {
            "hidden_ambition": random.randint(1, 10),
            "hidden_integrity": random.randint(1, 10),
            "hidden_discipline": random.randint(1, 10),
            "hidden_impulsivity": random.randint(1, 10),
            "hidden_pragmatism": random.randint(1, 10),
            "hidden_resilience": random.randint(1, 10)
        }
    
    def validate_population_count(self, count: int) -> int:
        """
        Validate population count value.
        
        Args:
            count: Population count to validate
            
        Returns:
            Validated population count
        """
        if not isinstance(count, (int, float)):
            raise ValueError("Population count must be a number")
        
        count = int(count)
        if count < 0:
            raise ValueError("Population count cannot be negative")
        
        return count
    
    def validate_growth_rate(self, rate: float) -> float:
        """
        Validate growth rate value.
        
        Args:
            rate: Growth rate to validate
            
        Returns:
            Validated growth rate
        """
        if not isinstance(rate, (int, float)):
            raise ValueError("Growth rate must be a number")
        
        rate = float(rate)
        if not (-1.0 <= rate <= 1.0):
            raise ValueError("Growth rate must be between -1.0 and 1.0")
        
        return rate
    
    def validate_capacity(self, capacity: int) -> int:
        """
        Validate carrying capacity value.
        
        Args:
            capacity: Carrying capacity to validate
            
        Returns:
            Validated carrying capacity
        """
        if not isinstance(capacity, (int, float)):
            raise ValueError("Carrying capacity must be a number")
        
        capacity = int(capacity)
        if capacity <= 0:
            raise ValueError("Carrying capacity must be positive")
        
        return capacity


def create_population_validation_service() -> PopulationValidationService:
    """Factory function to create population validation service"""
    return PopulationValidationService() 