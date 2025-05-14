from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CleanupRuleBase(BaseModel):
    name: str = Field(..., description="Name of the cleanup rule")
    resource_type: str = Field(..., description="Type of cloud resource this rule applies to")
    provider_id: int = Field(..., description="ID of the cloud provider")
    idle_threshold_days: int = Field(..., description="Number of days of inactivity before cleanup")
    cost_threshold: Optional[float] = Field(None, description="Cost threshold for cleanup (optional)")
    is_active: bool = Field(True, description="Whether the rule is currently active")

class CleanupRuleCreate(CleanupRuleBase):
    pass

class CleanupRuleUpdate(BaseModel):
    name: Optional[str] = None
    idle_threshold_days: Optional[int] = None
    cost_threshold: Optional[float] = None
    is_active: Optional[bool] = None

class CleanupRuleResponse(CleanupRuleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CleanupEntryBase(BaseModel):
    resource_id: str = Field(..., description="ID of the cloud resource")
    provider_id: int = Field(..., description="ID of the cloud provider")
    resource_type: str = Field(..., description="Type of cloud resource")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    estimated_cost: Optional[float] = Field(None, description="Estimated monthly cost")
    cleanup_reason: Optional[str] = Field(None, description="Reason for cleanup")
    rule_id: Optional[int] = Field(None, description="ID of the associated cleanup rule")

class CleanupEntryCreate(CleanupEntryBase):
    pass

class CleanupEntryUpdate(BaseModel):
    last_accessed: Optional[datetime] = None
    estimated_cost: Optional[float] = None
    is_cleaned: Optional[bool] = None
    cleaned_at: Optional[datetime] = None
    cleanup_reason: Optional[str] = None

class CleanupEntryResponse(CleanupEntryBase):
    id: int
    is_cleaned: bool
    cleaned_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class CleanupSummary(BaseModel):
    total_resources: int = Field(..., description="Total number of resources tracked")
    cleaned_resources: int = Field(..., description="Number of resources cleaned up")
    estimated_savings: float = Field(..., description="Estimated monthly cost savings")
    active_rules: int = Field(..., description="Number of active cleanup rules")

class ResourceCleanupStatus(BaseModel):
    resource_id: str
    resource_type: str
    cleanup_status: str = Field(..., description="Status of cleanup: pending, in_progress, completed, failed")
    status_message: Optional[str] = None
    timestamp: datetime

class BulkCleanupResponse(BaseModel):
    successful: List[ResourceCleanupStatus]
    failed: List[ResourceCleanupStatus]
    total_processed: int 