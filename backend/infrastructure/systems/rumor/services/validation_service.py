"""
Infrastructure Validation Services for Rumor System

This module provides concrete implementations of validation services
that implement the business logic protocols.
"""

from typing import Dict, Any, List
from backend.systems.rumor.services.services import RumorValidationService as ValidationServiceProtocol
from backend.systems.rumor.utils.rumor_rules import get_rumor_config


class DefaultRumorValidationService(ValidationServiceProtocol):
    """
    Default implementation of rumor validation service.
    Uses configuration from JSON files for validation rules.
    """
    
    def validate_rumor_data(self, rumor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate rumor creation/update data"""
        validated = rumor_data.copy()
        
        # Get validation config
        config = get_rumor_config()
        validation_config = config.get('validation', {})
        
        # Validate content length
        content = validated.get('content', '')
        max_length = validation_config.get('max_content_length', 500)
        min_length = validation_config.get('min_content_length', 10)
        
        if len(content) > max_length:
            raise ValueError(f"Content too long. Maximum {max_length} characters.")
        if len(content) < min_length:
            raise ValueError(f"Content too short. Minimum {min_length} characters.")
        
        # Validate originator_id
        originator_id = validated.get('originator_id', '')
        if not originator_id or len(originator_id.strip()) == 0:
            raise ValueError("Originator ID is required")
        
        # Validate truth_value
        truth_value = validated.get('truth_value', 0.5)
        if not isinstance(truth_value, (int, float)) or truth_value < 0.0 or truth_value > 1.0:
            raise ValueError("Truth value must be between 0.0 and 1.0")
        
        return validated
    
    def validate_severity(self, severity: str) -> str:
        """Validate rumor severity"""
        config = get_rumor_config()
        validation_config = config.get('validation', {})
        valid_severities = validation_config.get('severity_levels', [
            'trivial', 'minor', 'moderate', 'major', 'critical'
        ])
        
        if severity not in valid_severities:
            raise ValueError(f"Invalid severity '{severity}'. Must be one of: {valid_severities}")
        
        return severity
    
    def validate_categories(self, categories: List[str]) -> List[str]:
        """Validate rumor categories"""
        if not isinstance(categories, list):
            raise ValueError("Categories must be a list")
        
        # Ensure all categories are strings
        validated_categories = []
        for category in categories:
            if not isinstance(category, str):
                raise ValueError("All categories must be strings")
            
            # Clean and validate category
            clean_category = category.strip().lower()
            if clean_category:
                validated_categories.append(clean_category)
        
        return validated_categories


# Factory function for dependency injection
def create_rumor_validation_service() -> DefaultRumorValidationService:
    """Factory function to create rumor validation service"""
    return DefaultRumorValidationService() 