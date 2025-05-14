from typing import Optional, Any, Dict, List, Union
from datetime import datetime
from pydantic import BaseModel, Field

class PaginationParams(BaseModel):
    """Common pagination query parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", description="Sort order (asc/desc)")

class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class ErrorResponse(BaseModel):
    """Standard error response model."""
    status: int = Field(..., description="HTTP status code")
    error: ErrorDetail = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

class SearchParams(BaseModel):
    """Common search query parameters."""
    q: str = Field(..., min_length=1, description="Search query")
    fields: Optional[List[str]] = Field(None, description="Fields to search in")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")

class DateRangeParams(BaseModel):
    """Date range filter parameters."""
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")

class SortParams(BaseModel):
    """Sorting parameters."""
    field: str = Field(..., description="Field to sort by")
    order: str = Field(default="asc", description="Sort order (asc/desc)")

class FilterParams(BaseModel):
    """Common filter parameters."""
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter criteria")
    date_range: Optional[DateRangeParams] = Field(None, description="Date range filter")
    sort: Optional[SortParams] = Field(None, description="Sort parameters")

class BaseRequestModel(BaseModel):
    """Base model for all request bodies."""
    class Config:
        extra = "forbid"  # Forbid extra fields
        anystr_strip_whitespace = True  # Strip whitespace from strings

class BaseResponseModel(BaseModel):
    """Base model for all response bodies."""
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
class SuccessResponse(BaseResponseModel):
    """Standard success response model."""
    status: int = Field(..., description="HTTP status code")
    data: Dict[str, Any] = Field(..., description="Response data")
    message: Optional[str] = Field(None, description="Success message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp") 