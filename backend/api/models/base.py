"""
Base models for the Visual DM API.

This module defines the base models and interfaces used across the API.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union, TypeVar, Generic
from datetime import datetime
import uuid


class BaseEntity(BaseModel):
    """Base model for all entities in the system"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            uuid.UUID: lambda id: str(id)
        }


class TimestampMixin(BaseModel):
    """Mixin for adding timestamp fields to models"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('updated_at', always=True)
    def set_updated_at(cls, v, values):
        """Ensure updated_at is always set to current time when model changes"""
        return datetime.utcnow()


class NameDescriptionMixin(BaseModel):
    """Mixin for adding name and description fields to models"""
    name: str
    description: Optional[str] = None


class StatBlock(BaseModel):
    """Common stat block for characters, NPCs, etc."""
    strength: int = Field(..., ge=1, le=30)
    dexterity: int = Field(..., ge=1, le=30)
    constitution: int = Field(..., ge=1, le=30)
    intelligence: int = Field(..., ge=1, le=30)
    wisdom: int = Field(..., ge=1, le=30)
    charisma: int = Field(..., ge=1, le=30)


class Position(BaseModel):
    """2D or 3D position"""
    x: float
    y: float
    z: Optional[float] = None


class Metadata(BaseModel):
    """Generic metadata container for entities"""
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)
    source: Optional[str] = None
    version: Optional[str] = None


# Common response model type definitions
T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope"""
    data: T
    meta: Dict[str, Any] = Field(default_factory=dict)


class PaginatedList(BaseModel, Generic[T]):
    """Paginated list response format"""
    items: List[T]
    total: int
    page: int = 1
    page_size: int
    next_page: Optional[str] = None
    prev_page: Optional[str] = None


class ValidationError(BaseModel):
    """Individual validation error"""
    field: str
    message: str


class ErrorDetail(BaseModel):
    """Error details for API responses"""
    code: str
    message: str
    details: Optional[Union[List[ValidationError], Dict[str, Any], str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Simple success response"""
    success: bool = True
    message: Optional[str] = None


class MetaData(BaseModel):
    """Metadata for API responses"""
    # Can be extended with metadata fields like request_id, etc.
    pass


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper for any data type"""
    data: T
    meta: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class SuccessResponse(BaseModel):
    """Standard success response for operations without data return"""
    success: bool = True
    message: str


class ErrorDetail(BaseModel):
    """Standard error response format"""
    error: str
    error_code: str
    details: Optional[List[Dict[str, Any]]] = None
    message: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "error_code": "invalid_input",
                "message": "One or more fields failed validation",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format"
                    }
                ]
            }
        } 