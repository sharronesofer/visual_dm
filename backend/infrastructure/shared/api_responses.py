"""
Standardized API Response System
Following JSON:API conventions and industry best practices
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import uuid
from dataclasses import dataclass
from enum import Enum


class ResponseStatus(Enum):
    """Standard HTTP response statuses"""
    SUCCESS = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    VALIDATION_ERROR = 422
    INTERNAL_ERROR = 500


@dataclass
class ApiError:
    """Standard API error structure"""
    status: str
    code: str
    title: str
    detail: str
    source: Optional[Dict[str, str]] = None
    meta: Optional[Dict[str, Any]] = None


@dataclass
class ApiMeta:
    """Standard API metadata"""
    timestamp: str
    version: str = "1.0"
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())


@dataclass
class PaginationMeta:
    """Pagination metadata"""
    page: int
    per_page: int
    total: int
    total_pages: int


class ApiResponse:
    """
    Standardized API response builder following JSON:API specification
    """
    
    @staticmethod
    def success(
        data: Any,
        meta: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        status: ResponseStatus = ResponseStatus.SUCCESS
    ) -> Dict[str, Any]:
        """
        Create a successful response
        
        Args:
            data: Response data (single resource or list)
            meta: Additional metadata
            links: Related links (pagination, etc.)
            status: HTTP status code
            
        Returns:
            Formatted JSON:API response
        """
        response = {
            "data": data,
            "meta": {
                **ApiMeta(timestamp=datetime.utcnow().isoformat()).__dict__,
                **(meta or {})
            }
        }
        
        if links:
            response["links"] = links
            
        return response
    
    @staticmethod
    def error(
        errors: Union[ApiError, List[ApiError]],
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an error response
        
        Args:
            errors: Single error or list of errors
            meta: Additional metadata
            
        Returns:
            Formatted JSON:API error response
        """
        if isinstance(errors, ApiError):
            errors = [errors]
            
        return {
            "errors": [
                {
                    "status": error.status,
                    "code": error.code,
                    "title": error.title,
                    "detail": error.detail,
                    **({"source": error.source} if error.source else {}),
                    **({"meta": error.meta} if error.meta else {})
                }
                for error in errors
            ],
            "meta": {
                **ApiMeta(timestamp=datetime.utcnow().isoformat()).__dict__,
                **(meta or {})
            }
        }
    
    @staticmethod
    def validation_error(
        field_errors: List[Dict[str, Any]],
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a validation error response
        
        Args:
            field_errors: List of field validation errors
            meta: Additional metadata
            
        Returns:
            Formatted validation error response
        """
        errors = []
        for field_error in field_errors:
            errors.append(ApiError(
                status="422",
                code=field_error.get("code", "VALIDATION_ERROR"),
                title="Validation Failed",
                detail=field_error.get("message", "Validation failed"),
                source={"pointer": f"/data/attributes/{field_error.get('field', 'unknown')}"},
                meta={
                    "field": field_error.get("field"),
                    "current_value": field_error.get("current_value"),
                    "constraints": field_error.get("constraints", {})
                }
            ))
        
        return ApiResponse.error(errors, meta)
    
    @staticmethod
    def paginated(
        data: List[Any],
        pagination: PaginationMeta,
        base_url: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a paginated response
        
        Args:
            data: List of resources
            pagination: Pagination metadata
            base_url: Base URL for pagination links
            meta: Additional metadata
            
        Returns:
            Formatted paginated response
        """
        links = {
            "self": f"{base_url}?page={pagination.page}",
            "first": f"{base_url}?page=1",
            "last": f"{base_url}?page={pagination.total_pages}"
        }
        
        if pagination.page > 1:
            links["prev"] = f"{base_url}?page={pagination.page - 1}"
        if pagination.page < pagination.total_pages:
            links["next"] = f"{base_url}?page={pagination.page + 1}"
        
        response_meta = {
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "total_pages": pagination.total_pages
            },
            **(meta or {})
        }
        
        return ApiResponse.success(data, response_meta, links)
    
    @staticmethod
    def resource(
        resource_type: str,
        resource_id: str,
        attributes: Dict[str, Any],
        relationships: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a single resource response
        
        Args:
            resource_type: Type of resource (e.g., 'character')
            resource_id: Resource identifier
            attributes: Resource attributes
            relationships: Resource relationships
            meta: Additional metadata
            
        Returns:
            Formatted resource response
        """
        data = {
            "type": resource_type,
            "id": resource_id,
            "attributes": attributes
        }
        
        if relationships:
            data["relationships"] = relationships
            
        return ApiResponse.success(data, meta)


class ValidationMessages:
    """
    Centralized validation messages with internationalization support
    """
    
    MESSAGES = {
        "CHARACTER_NAME_TOO_SHORT": {
            "message": "Character name must be at least {min_length} characters",
            "constraints": {"min_length": 2, "max_length": 50}
        },
        "CHARACTER_NAME_TOO_LONG": {
            "message": "Character name cannot exceed {max_length} characters",
            "constraints": {"min_length": 2, "max_length": 50}
        },
        "INVALID_ATTRIBUTE_RANGE": {
            "message": "Attribute {attribute} must be between {min_value} and {max_value}",
            "constraints": {"min_value": -3, "max_value": 5}
        },
        "TOO_MANY_ABILITIES": {
            "message": "Level {level} characters can have at most {max_abilities} abilities",
            "constraints": {"abilities_at_creation": 7, "per_level": 3}
        },
        "RACE_NOT_FOUND": {
            "message": "Race '{race}' is not valid. Available races: {available_races}",
            "constraints": {"available_races": ["human", "elf", "dwarf", "halfling", "gnome", "half-elf", "half-orc", "tiefling"]}
        },
        "BACKGROUND_NOT_FOUND": {
            "message": "Background '{background}' is not valid. Available backgrounds: {available_backgrounds}",
            "constraints": {"available_backgrounds": ["noble", "criminal", "sage", "soldier", "folk_hero"]}
        },
        "REQUIRED_FIELD_MISSING": {
            "message": "Field '{field}' is required",
            "constraints": {}
        },
        "INVALID_UUID_FORMAT": {
            "message": "Field '{field}' must be a valid UUID format",
            "constraints": {"format": "uuid"}
        },
        "LEVEL_OUT_OF_RANGE": {
            "message": "Character level must be between {min_level} and {max_level}",
            "constraints": {"min_level": 1, "max_level": 20}
        },
        "INVALID_SKILL": {
            "message": "Skill '{skill}' is not valid. Available skills: {available_skills}",
            "constraints": {"total_skills": 36}
        }
    }
    
    @classmethod
    def get_validation_error(
        cls,
        error_code: str,
        field: str,
        current_value: Any = None,
        **format_kwargs
    ) -> Dict[str, Any]:
        """
        Get a formatted validation error
        
        Args:
            error_code: Error code key
            field: Field name that failed validation
            current_value: Current value that failed
            **format_kwargs: Values to format into the message
            
        Returns:
            Formatted validation error
        """
        message_data = cls.MESSAGES.get(error_code, {
            "message": f"Validation failed for field '{field}'",
            "constraints": {}
        })
        
        try:
            formatted_message = message_data["message"].format(**format_kwargs)
        except KeyError:
            formatted_message = message_data["message"]
        
        return {
            "field": field,
            "code": error_code,
            "message": formatted_message,
            "current_value": current_value,
            "constraints": message_data["constraints"]
        }


# Convenience functions for common response patterns
def success_response(data: Any, **kwargs) -> Dict[str, Any]:
    """Shorthand for successful response"""
    return ApiResponse.success(data, **kwargs)


def error_response(message: str, code: str = "GENERIC_ERROR", status: str = "500", **kwargs) -> Dict[str, Any]:
    """Shorthand for error response"""
    error = ApiError(
        status=status,
        code=code,
        title="Error",
        detail=message
    )
    return ApiResponse.error(error, **kwargs)


def validation_error_response(field: str, error_code: str, current_value: Any = None, **format_kwargs) -> Dict[str, Any]:
    """Shorthand for validation error response"""
    field_error = ValidationMessages.get_validation_error(
        error_code, field, current_value, **format_kwargs
    )
    return ApiResponse.validation_error([field_error])


def not_found_response(resource_type: str, resource_id: str) -> Dict[str, Any]:
    """Shorthand for not found response"""
    error = ApiError(
        status="404",
        code="RESOURCE_NOT_FOUND",
        title="Resource Not Found",
        detail=f"{resource_type.title()} with ID '{resource_id}' was not found"
    )
    return ApiResponse.error(error) 