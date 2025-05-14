"""API request and response schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class CloudProviderBase(BaseModel):
    """Base schema for cloud provider."""
    name: str = Field(..., description="Name of the cloud provider (e.g., 'AWS', 'GCP', 'Azure')")
    credentials: dict = Field(..., description="Provider-specific credentials")
    is_active: bool = Field(True, description="Whether the provider is active")

class CloudProviderCreate(CloudProviderBase):
    """Schema for creating a cloud provider."""
    pass

class CloudProvider(CloudProviderBase):
    """Schema for cloud provider response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class CloudProviderUpdate(BaseModel):
    """Schema for updating a cloud provider."""
    name: Optional[str] = Field(None, description="Name of the cloud provider")
    credentials: Optional[dict] = Field(None, description="Provider-specific credentials")
    is_active: Optional[bool] = Field(None, description="Whether the provider is active")

class CloudProviderResponse(CloudProviderBase):
    """Schema for cloud provider response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class CostEntryBase(BaseModel):
    """Base schema for cost entry."""
    provider_id: int = Field(..., description="ID of the cloud provider")
    service: str = Field(..., description="Service name (e.g., 'EC2', 'S3')")
    amount: float = Field(..., description="Cost amount")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    timestamp: datetime = Field(..., description="When the cost was incurred")
    resource_id: Optional[str] = Field(None, description="ID of the resource")
    tags: dict = Field(default_factory=dict, description="Resource tags")

class CostEntryCreate(CostEntryBase):
    """Schema for creating a cost entry."""
    pass

class CostEntry(CostEntryBase):
    """Schema for cost entry response."""
    id: int
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class BudgetBase(BaseModel):
    """Base schema for budget."""
    name: str = Field(..., description="Budget name")
    amount: float = Field(..., description="Budget amount")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    period: str = Field(..., description="Budget period (monthly, quarterly, yearly)")
    scope: str = Field(..., description="Budget scope (project, team, service)")
    scope_id: str = Field(..., description="ID within the scope (e.g., project ID)")
    alert_threshold: float = Field(..., description="Alert threshold percentage")
    start_date: datetime = Field(..., description="Budget start date")
    end_date: Optional[datetime] = Field(None, description="Budget end date")

class BudgetCreate(BudgetBase):
    """Schema for creating a budget."""
    pass

class Budget(BudgetBase):
    """Schema for budget response."""
    id: int
    created_at: datetime
    updated_at: datetime
    current_usage: float = Field(0.0, description="Current usage amount")
    usage_percentage: float = Field(0.0, description="Usage as percentage of budget")

    class Config:
        """Pydantic config."""
        from_attributes = True

class BudgetAlert(BaseModel):
    """Schema for budget alert."""
    id: int
    budget_id: int = Field(..., description="ID of the budget")
    threshold: float = Field(..., description="Threshold percentage that triggered the alert")
    current_usage: float = Field(..., description="Current usage amount")
    triggered_at: datetime = Field(..., description="When the alert was triggered")

    class Config:
        """Pydantic config."""
        from_attributes = True

class CleanupEntryBase(BaseModel):
    """Base schema for cleanup entry."""
    provider_id: int = Field(..., description="ID of the cloud provider")
    resource_id: str = Field(..., description="ID of the resource")
    resource_type: str = Field(..., description="Type of resource (e.g., 'instance', 'volume')")
    estimated_savings: float = Field(..., description="Estimated monthly savings")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    reason: str = Field(..., description="Reason for cleanup recommendation")
    status: str = Field(..., description="Cleanup status")

class CleanupEntryCreate(CleanupEntryBase):
    """Schema for creating a cleanup entry."""
    pass

class CleanupEntry(CleanupEntryBase):
    """Schema for cleanup entry response."""
    id: int
    created_at: datetime
    updated_at: datetime
    cleaned_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class CleanupEntryUpdate(BaseModel):
    """Schema for updating a cleanup entry."""
    status: Optional[str] = Field(None, description="Cleanup status")
    cleaned_at: Optional[datetime] = Field(None, description="When the resource was cleaned up")

class CostSummary(BaseModel):
    """Schema for cost summary response."""
    total_cost: float = Field(..., description="Total cost")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    period_start: datetime = Field(..., description="Start of the period")
    period_end: datetime = Field(..., description="End of the period")
    by_service: dict = Field(..., description="Costs broken down by service")
    by_provider: dict = Field(..., description="Costs broken down by provider")

class CostTrend(BaseModel):
    """Schema for cost trend data point."""
    timestamp: datetime = Field(..., description="Timestamp for the data point")
    amount: float = Field(..., description="Cost amount")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    service: Optional[str] = Field(None, description="Service name if filtered by service")
    provider_id: Optional[int] = Field(None, description="Provider ID if filtered by provider")

class BudgetStatus(BaseModel):
    """Schema for budget status response."""
    id: int
    name: str = Field(..., description="Budget name")
    amount: float = Field(..., description="Budget amount")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    period: str = Field(..., description="Budget period (monthly, quarterly, yearly)")
    scope: str = Field(..., description="Budget scope (project, team, service)")
    scope_id: str = Field(..., description="ID within the scope (e.g., project ID)")
    alert_threshold: float = Field(..., description="Alert threshold percentage")
    current_usage: float = Field(0.0, description="Current usage amount")
    usage_percentage: float = Field(0.0, description="Usage as percentage of budget")
    status: str = Field(..., description="Budget status (e.g., 'ok', 'warning', 'exceeded')")
    last_updated: datetime = Field(..., description="When the status was last updated")

    class Config:
        """Pydantic config."""
        from_attributes = True

class BudgetUpdate(BaseModel):
    """Schema for updating a budget."""
    name: Optional[str] = Field(None, description="Budget name")
    amount: Optional[float] = Field(None, description="Budget amount")
    currency: Optional[str] = Field(None, description="Currency code (e.g., 'USD')")
    period: Optional[str] = Field(None, description="Budget period (monthly, quarterly, yearly)")
    scope: Optional[str] = Field(None, description="Budget scope (project, team, service)")
    scope_id: Optional[str] = Field(None, description="ID within the scope (e.g., project ID)")
    alert_threshold: Optional[float] = Field(None, description="Alert threshold percentage")
    start_date: Optional[datetime] = Field(None, description="Budget start date")
    end_date: Optional[datetime] = Field(None, description="Budget end date")

class BudgetForecast(BaseModel):
    """Schema for budget forecast response."""
    budget_id: int = Field(..., description="ID of the budget")
    current_usage: float = Field(..., description="Current usage amount")
    projected_usage: float = Field(..., description="Projected usage by end of period")
    projected_overage: Optional[float] = Field(None, description="Projected amount over budget")
    projected_date_exceeded: Optional[datetime] = Field(None, description="Date when budget is projected to be exceeded")
    confidence_score: float = Field(..., description="Confidence score of the forecast (0-1)")
    forecast_data: List[dict] = Field(..., description="Daily/weekly forecast data points")
    last_updated: datetime = Field(..., description="When the forecast was last updated")

    class Config:
        """Pydantic config."""
        from_attributes = True

class BudgetHistory(BaseModel):
    """Schema for budget history response."""
    budget_id: int = Field(..., description="ID of the budget")
    period_start: datetime = Field(..., description="Start of the period")
    period_end: datetime = Field(..., description="End of the period")
    amount: float = Field(..., description="Budget amount")
    actual_usage: float = Field(..., description="Actual usage amount")
    usage_percentage: float = Field(..., description="Usage as percentage of budget")
    status: str = Field(..., description="Budget status for the period")
    alerts: List[dict] = Field(default_factory=list, description="Alerts triggered during the period")

    class Config:
        """Pydantic config."""
        from_attributes = True

class ResourceUsage(BaseModel):
    """Schema for resource usage response."""
    resource_id: str = Field(..., description="ID of the resource")
    resource_type: str = Field(..., description="Type of resource")
    usage_metrics: dict = Field(..., description="Usage metrics")
    cost: float = Field(..., description="Current cost")
    currency: str = Field(..., description="Currency code (e.g., 'USD')")
    last_used: datetime = Field(..., description="When the resource was last used")

class CleanupRuleBase(BaseModel):
    """Base schema for cleanup rule."""
    name: str = Field(..., description="Name of the cleanup rule")
    provider_id: int = Field(..., description="ID of the cloud provider")
    resource_type: str = Field(..., description="Type of resource to monitor")
    conditions: dict = Field(..., description="Conditions that trigger cleanup")
    action: str = Field(..., description="Action to take (e.g., 'terminate', 'stop')")
    is_active: bool = Field(True, description="Whether the rule is active")

class CleanupRuleCreate(CleanupRuleBase):
    """Schema for creating a cleanup rule."""
    pass

class CleanupRuleUpdate(BaseModel):
    """Schema for updating a cleanup rule."""
    name: Optional[str] = Field(None, description="Name of the cleanup rule")
    provider_id: Optional[int] = Field(None, description="ID of the cloud provider")
    resource_type: Optional[str] = Field(None, description="Type of resource to monitor")
    conditions: Optional[dict] = Field(None, description="Conditions that trigger cleanup")
    action: Optional[str] = Field(None, description="Action to take")
    is_active: Optional[bool] = Field(None, description="Whether the rule is active")

class CleanupRuleResponse(CleanupRuleBase):
    """Schema for cleanup rule response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class CleanupEntryResponse(CleanupEntry):
    """Schema for cleanup entry response."""
    pass 