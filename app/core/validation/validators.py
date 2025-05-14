"""
Validators for server-side validation of user actions.

This module contains basic validators for common data types that can be
composed to create more complex validation logic.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Type
from dataclasses import dataclass
import re
import datetime
from decimal import Decimal
from app.core.api.error_handling.exceptions import ValidationError

@dataclass
class ValidationResult:
    """Result of a validation operation."""
    valid: bool
    errors: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize errors list if not provided."""
        if self.errors is None:
            self.errors = []
    
    @classmethod
    def success(cls) -> 'ValidationResult':
        """Create a successful validation result."""
        return cls(valid=True)
    
    @classmethod
    def failure(cls, field: str, message: str, **details) -> 'ValidationResult':
        """Create a failed validation result with a single error."""
        error = {"field": field, "message": message, **details}
        return cls(valid=False, errors=[error])
    
    def add_error(self, field: str, message: str, **details) -> None:
        """Add an error to the validation result."""
        self.valid = False
        self.errors.append({"field": field, "message": message, **details})
    
    def extend(self, other: 'ValidationResult') -> None:
        """Extend this validation result with errors from another result."""
        if not other.valid:
            self.valid = False
            self.errors.extend(other.errors)


class Validator:
    """Base validator class."""
    
    def __init__(self, field_name: str, required: bool = True, error_message: Optional[str] = None):
        """Initialize validator.
        
        Args:
            field_name: Name of the field being validated
            required: Whether the field is required
            error_message: Custom error message for validation failure
        """
        self.field_name = field_name
        self.required = required
        self.error_message = error_message
    
    def validate(self, value: Any) -> ValidationResult:
        """Validate a value.
        
        Args:
            value: Value to validate
            
        Returns:
            ValidationResult object indicating success or failure
        """
        # Check if value is None and field is required
        if value is None:
            if self.required:
                return ValidationResult.failure(
                    self.field_name,
                    self.error_message or f"{self.field_name} is required"
                )
            return ValidationResult.success()
        
        # Perform validation
        return self._validate_value(value)
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Perform validation on a non-None value.
        
        Args:
            value: Value to validate
            
        Returns:
            ValidationResult object indicating success or failure
        """
        # Base implementation always succeeds - override in subclasses
        return ValidationResult.success()


class StringValidator(Validator):
    """Validator for string values."""
    
    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_values: Optional[List[str]] = None,
        error_message: Optional[str] = None
    ):
        """Initialize string validator.
        
        Args:
            field_name: Name of the field being validated
            required: Whether the field is required
            min_length: Minimum length of the string
            max_length: Maximum length of the string
            pattern: Regex pattern the string must match
            allowed_values: List of allowed values
            error_message: Custom error message for validation failure
        """
        super().__init__(field_name, required, error_message)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(pattern) if pattern else None
        self.allowed_values = allowed_values
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Validate string value."""
        result = ValidationResult.success()
        
        # Check type
        if not isinstance(value, str):
            return ValidationResult.failure(
                self.field_name,
                self.error_message or f"{self.field_name} must be a string"
            )
        
        # Check min length
        if self.min_length is not None and len(value) < self.min_length:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must be at least {self.min_length} characters long",
                min_length=self.min_length,
                actual_length=len(value)
            )
        
        # Check max length
        if self.max_length is not None and len(value) > self.max_length:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must be at most {self.max_length} characters long",
                max_length=self.max_length,
                actual_length=len(value)
            )
        
        # Check pattern
        if self.pattern and not self.pattern.match(value):
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} does not match the required pattern",
                pattern=self.pattern.pattern
            )
        
        # Check allowed values
        if self.allowed_values is not None and value not in self.allowed_values:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must be one of {self.allowed_values}",
                allowed_values=self.allowed_values
            )
        
        return result


class NumberValidator(Validator):
    """Validator for numeric values."""
    
    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_value: Optional[Union[int, float, Decimal]] = None,
        max_value: Optional[Union[int, float, Decimal]] = None,
        is_integer: bool = False,
        error_message: Optional[str] = None
    ):
        """Initialize number validator.
        
        Args:
            field_name: Name of the field being validated
            required: Whether the field is required
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            is_integer: Whether the value must be an integer
            error_message: Custom error message for validation failure
        """
        super().__init__(field_name, required, error_message)
        self.min_value = min_value
        self.max_value = max_value
        self.is_integer = is_integer
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Validate numeric value."""
        result = ValidationResult.success()
        
        # Check type
        if self.is_integer and not isinstance(value, int):
            return ValidationResult.failure(
                self.field_name,
                self.error_message or f"{self.field_name} must be an integer"
            )
        elif not self.is_integer and not isinstance(value, (int, float, Decimal)):
            return ValidationResult.failure(
                self.field_name,
                self.error_message or f"{self.field_name} must be a number"
            )
        
        # Check min value
        if self.min_value is not None and value < self.min_value:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must be at least {self.min_value}",
                min_value=self.min_value,
                actual_value=value
            )
        
        # Check max value
        if self.max_value is not None and value > self.max_value:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must be at most {self.max_value}",
                max_value=self.max_value,
                actual_value=value
            )
        
        return result


class BooleanValidator(Validator):
    """Validator for boolean values."""
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Validate boolean value."""
        if not isinstance(value, bool):
            return ValidationResult.failure(
                self.field_name,
                self.error_message or f"{self.field_name} must be a boolean"
            )
        return ValidationResult.success()


class DateTimeValidator(Validator):
    """Validator for datetime values."""
    
    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_date: Optional[datetime.datetime] = None,
        max_date: Optional[datetime.datetime] = None,
        error_message: Optional[str] = None
    ):
        """Initialize datetime validator.
        
        Args:
            field_name: Name of the field being validated
            required: Whether the field is required
            min_date: Minimum allowed date
            max_date: Maximum allowed date
            error_message: Custom error message for validation failure
        """
        super().__init__(field_name, required, error_message)
        self.min_date = min_date
        self.max_date = max_date
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Validate datetime value."""
        result = ValidationResult.success()
        
        # Check type
        if not isinstance(value, datetime.datetime):
            return ValidationResult.failure(
                self.field_name,
                self.error_message or f"{self.field_name} must be a datetime"
            )
        
        # Check min date
        if self.min_date is not None and value < self.min_date:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must be after {self.min_date.isoformat()}",
                min_date=self.min_date.isoformat(),
                actual_date=value.isoformat()
            )
        
        # Check max date
        if self.max_date is not None and value > self.max_date:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must be before {self.max_date.isoformat()}",
                max_date=self.max_date.isoformat(),
                actual_date=value.isoformat()
            )
        
        return result


class ListValidator(Validator):
    """Validator for list values."""
    
    def __init__(
        self,
        field_name: str,
        required: bool = True,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        item_validator: Optional[Validator] = None,
        error_message: Optional[str] = None
    ):
        """Initialize list validator.
        
        Args:
            field_name: Name of the field being validated
            required: Whether the field is required
            min_length: Minimum length of the list
            max_length: Maximum length of the list
            item_validator: Validator for list items
            error_message: Custom error message for validation failure
        """
        super().__init__(field_name, required, error_message)
        self.min_length = min_length
        self.max_length = max_length
        self.item_validator = item_validator
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Validate list value."""
        result = ValidationResult.success()
        
        # Check type
        if not isinstance(value, list):
            return ValidationResult.failure(
                self.field_name,
                self.error_message or f"{self.field_name} must be a list"
            )
        
        # Check min length
        if self.min_length is not None and len(value) < self.min_length:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must have at least {self.min_length} items",
                min_length=self.min_length,
                actual_length=len(value)
            )
        
        # Check max length
        if self.max_length is not None and len(value) > self.max_length:
            result.add_error(
                self.field_name,
                self.error_message or f"{self.field_name} must have at most {self.max_length} items",
                max_length=self.max_length,
                actual_length=len(value)
            )
        
        # Validate items
        if self.item_validator and result.valid:
            for i, item in enumerate(value):
                item_result = self.item_validator.validate(item)
                if not item_result.valid:
                    for error in item_result.errors:
                        result.add_error(
                            f"{self.field_name}[{i}]",
                            error["message"],
                            **{k: v for k, v in error.items() if k != "message" and k != "field"}
                        )
        
        return result


class DictValidator(Validator):
    """Validator for dictionary values."""
    
    def __init__(
        self,
        field_name: str,
        required: bool = True,
        schema: Optional[Dict[str, Validator]] = None,
        error_message: Optional[str] = None
    ):
        """Initialize dictionary validator.
        
        Args:
            field_name: Name of the field being validated
            required: Whether the field is required
            schema: Dictionary of field validators
            error_message: Custom error message for validation failure
        """
        super().__init__(field_name, required, error_message)
        self.schema = schema or {}
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Validate dictionary value."""
        result = ValidationResult.success()
        
        # Check type
        if not isinstance(value, dict):
            return ValidationResult.failure(
                self.field_name,
                self.error_message or f"{self.field_name} must be an object"
            )
        
        # Validate fields
        if self.schema:
            for field_name, validator in self.schema.items():
                field_value = value.get(field_name)
                field_result = validator.validate(field_value)
                if not field_result.valid:
                    result.extend(field_result)
        
        return result


class CustomValidator(Validator):
    """Validator with custom validation function."""
    
    def __init__(
        self,
        field_name: str,
        required: bool = True,
        validation_fn: Optional[Callable[[Any], Tuple[bool, Optional[str]]]] = None,
        error_message: Optional[str] = None
    ):
        """Initialize custom validator.
        
        Args:
            field_name: Name of the field being validated
            required: Whether the field is required
            validation_fn: Custom validation function
                that returns a tuple of (is_valid, error_message)
            error_message: Custom error message for validation failure
        """
        super().__init__(field_name, required, error_message)
        self.validation_fn = validation_fn
    
    def _validate_value(self, value: Any) -> ValidationResult:
        """Validate value using custom validation function."""
        if self.validation_fn:
            is_valid, error_msg = self.validation_fn(value)
            if not is_valid:
                return ValidationResult.failure(
                    self.field_name,
                    error_msg or self.error_message or f"{self.field_name} validation failed"
                )
        return ValidationResult.success()


def validate_request_data(schema: Dict[str, Validator], data: Dict[str, Any]) -> None:
    """Validate request data against a schema of validators.
    
    Args:
        schema: Dictionary of field validators
        data: Request data to validate
        
    Raises:
        ValidationError: If validation fails
    """
    result = ValidationResult.success()
    
    for field_name, validator in schema.items():
        field_value = data.get(field_name)
        field_result = validator.validate(field_value)
        if not field_result.valid:
            result.extend(field_result)
    
    if not result.valid:
        raise ValidationError(details=result.errors) 