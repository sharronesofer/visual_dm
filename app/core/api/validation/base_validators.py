"""Base validation utilities for API requests.

This module provides common validation functions, decorators, and base classes
for request validation across all API endpoints.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel, Field, validator, ValidationError
from datetime import datetime
from enum import Enum

T = TypeVar('T', bound=BaseModel)

class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: Optional[List[Dict[str, Any]]] = None):
        """Initialize validation result.
        
        Args:
            is_valid: Whether the validation passed
            errors: List of validation errors if any
        """
        self.is_valid = is_valid
        self.errors = errors or []

class PaginationValidationMixin:
    """Mixin for validating pagination parameters."""
    
    @validator('page')
    def validate_page(cls, v: int) -> int:
        """Validate page number."""
        if v < 1:
            raise ValueError("Page number must be greater than 0")
        return v
        
    @validator('per_page')
    def validate_per_page(cls, v: int) -> int:
        """Validate items per page."""
        if v < 1:
            raise ValueError("Items per page must be greater than 0")
        if v > 100:
            raise ValueError("Items per page cannot exceed 100")
        return v

class SortValidationMixin:
    """Mixin for validating sort parameters."""
    
    @validator('sort_by')
    def validate_sort_field(cls, v: str, values: Dict[str, Any]) -> str:
        """Validate sort field name."""
        valid_fields = values.get('valid_sort_fields', [])
        if valid_fields and v not in valid_fields:
            raise ValueError(f"Invalid sort field. Valid fields are: {', '.join(valid_fields)}")
        return v
        
    @validator('order')
    def validate_sort_order(cls, v: str) -> str:
        """Validate sort order."""
        valid_orders = ['asc', 'desc']
        if v.lower() not in valid_orders:
            raise ValueError(f"Invalid sort order. Must be one of: {', '.join(valid_orders)}")
        return v.lower()

class FilterValidationMixin:
    """Mixin for validating filter parameters."""
    
    @validator('filters')
    def validate_filters(cls, v: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate filter parameters."""
        valid_filters = values.get('valid_filters', {})
        if not valid_filters:
            return v
            
        for field, value in v.items():
            if field not in valid_filters:
                raise ValueError(f"Invalid filter field: {field}")
            
            expected_type = valid_filters[field]
            if not isinstance(value, expected_type):
                raise ValueError(f"Invalid type for filter {field}. Expected {expected_type.__name__}")
        
        return v

class DateRangeValidationMixin:
    """Mixin for validating date range parameters."""
    
    @validator('start_date')
    def validate_start_date(cls, v: datetime, values: Dict[str, Any]) -> datetime:
        """Validate start date."""
        end_date = values.get('end_date')
        if end_date and v > end_date:
            raise ValueError("Start date cannot be after end date")
        return v
        
    @validator('end_date')
    def validate_end_date(cls, v: datetime, values: Dict[str, Any]) -> datetime:
        """Validate end date."""
        start_date = values.get('start_date')
        if start_date and v < start_date:
            raise ValueError("End date cannot be before start date")
        return v

def validate_id(id: str) -> ValidationResult:
    """Validate an entity ID.
    
    Args:
        id: The ID to validate
        
    Returns:
        ValidationResult indicating if the ID is valid
    """
    if not id or not isinstance(id, str):
        return ValidationResult(False, [{"field": "id", "error": "ID must be a non-empty string"}])
    
    if len(id) > 100:
        return ValidationResult(False, [{"field": "id", "error": "ID cannot exceed 100 characters"}])
    
    return ValidationResult(True)

def validate_name(name: str) -> ValidationResult:
    """Validate an entity name.
    
    Args:
        name: The name to validate
        
    Returns:
        ValidationResult indicating if the name is valid
    """
    if not name or not isinstance(name, str):
        return ValidationResult(False, [{"field": "name", "error": "Name must be a non-empty string"}])
    
    if len(name) > 200:
        return ValidationResult(False, [{"field": "name", "error": "Name cannot exceed 200 characters"}])
    
    return ValidationResult(True)

def validate_description(description: str) -> ValidationResult:
    """Validate an entity description.
    
    Args:
        description: The description to validate
        
    Returns:
        ValidationResult indicating if the description is valid
    """
    if not description or not isinstance(description, str):
        return ValidationResult(False, [{"field": "description", "error": "Description must be a non-empty string"}])
    
    if len(description) > 2000:
        return ValidationResult(False, [{"field": "description", "error": "Description cannot exceed 2000 characters"}])
    
    return ValidationResult(True)

def validate_tags(tags: List[str]) -> ValidationResult:
    """Validate entity tags.
    
    Args:
        tags: The list of tags to validate
        
    Returns:
        ValidationResult indicating if the tags are valid
    """
    if not isinstance(tags, list):
        return ValidationResult(False, [{"field": "tags", "error": "Tags must be a list"}])
    
    errors = []
    for i, tag in enumerate(tags):
        if not isinstance(tag, str):
            errors.append({"field": f"tags[{i}]", "error": "Tag must be a string"})
        elif len(tag) > 50:
            errors.append({"field": f"tags[{i}]", "error": "Tag cannot exceed 50 characters"})
    
    return ValidationResult(not bool(errors), errors)

def validate_metadata(metadata: Dict[str, Any]) -> ValidationResult:
    """Validate entity metadata.
    
    Args:
        metadata: The metadata dictionary to validate
        
    Returns:
        ValidationResult indicating if the metadata is valid
    """
    if not isinstance(metadata, dict):
        return ValidationResult(False, [{"field": "metadata", "error": "Metadata must be a dictionary"}])
    
    errors = []
    for key, value in metadata.items():
        if not isinstance(key, str):
            errors.append({"field": "metadata", "error": "Metadata keys must be strings"})
        elif len(key) > 100:
            errors.append({"field": f"metadata.{key}", "error": "Metadata key cannot exceed 100 characters"})
            
        if isinstance(value, (list, dict)):
            if len(str(value)) > 5000:
                errors.append({"field": f"metadata.{key}", "error": "Metadata value too large"})
        elif isinstance(value, str) and len(value) > 1000:
            errors.append({"field": f"metadata.{key}", "error": "Metadata string value cannot exceed 1000 characters"})
    
    return ValidationResult(not bool(errors), errors) 