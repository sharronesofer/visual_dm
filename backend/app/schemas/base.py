from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, TypeVar, Optional, List, Dict, Any
from datetime import datetime


# Generic model for database items
T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema with configuration"""
    model_config = ConfigDict(
        from_attributes=True,  # Allow ORM mode
        json_schema_extra={
            "example": {}  # Empty example by default
        }
    )
    

class IDSchema(BaseSchema):
    """Schema with ID field"""
    id: int = Field(..., description="Unique identifier")
    

class TimestampSchema(BaseSchema):
    """Schema with timestamp fields"""
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class PageParams(BaseSchema):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    size: int = Field(10, ge=1, le=100, description="Items per page")


class SortParams(BaseSchema):
    """Sorting parameters"""
    sort_by: str = Field("id", description="Field to sort by")
    sort_order: str = Field("asc", description="Sort order (asc or desc)")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated response schema"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class MessageResponse(BaseSchema):
    """Simple message response"""
    message: str = Field(..., description="Response message")


class ErrorDetail(BaseSchema):
    """Error detail schema"""
    loc: List[str] = Field(..., description="Location of the error")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseSchema):
    """Error response schema"""
    error: bool = Field(True, description="Error flag")
    message: str = Field(..., description="Error message")
    code: int = Field(..., description="HTTP status code")
    details: Dict[str, Any] = Field({}, description="Additional error details") 