from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum

# Generic type for data models
T = TypeVar("T")


class StatusEnum(str, Enum):
    """Common status values"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    PROCESSING = "processing"


class APIResponse(BaseModel):
    """Generic API response model"""
    status: StatusEnum = StatusEnum.SUCCESS
    message: str = "Operation completed successfully"
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DataResponse(APIResponse, Generic[T]):
    """API response containing data"""
    data: T


class ErrorResponse(APIResponse):
    """API error response"""
    status: StatusEnum = StatusEnum.ERROR
    message: str = "An error occurred"
    errors: Optional[List[Dict[str, Any]]] = None


class PaginationParams(BaseModel):
    """Common pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number, starting from 1")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    

class PaginatedResponse(DataResponse, Generic[T]):
    """Paginated API response"""
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: Optional[int] = None
    python_version: Optional[str] = None
    environment: Optional[str] = None 