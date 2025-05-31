"""
Crafting Schemas

Pydantic models for core crafting operation requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from enum import Enum

class CraftingStatus(str, Enum):
    """Enumeration of crafting operation statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class QualityLevel(str, Enum):
    """Enumeration of item quality levels."""
    POOR = "poor"
    NORMAL = "normal"
    GOOD = "good"
    EXCELLENT = "excellent"
    EXCEPTIONAL = "exceptional"
    MASTERWORK = "masterwork"
    LEGENDARY = "legendary"

class CraftingStartSchema(BaseModel):
    """Schema for starting a crafting operation."""
    recipe_id: uuid.UUID = Field(..., description="Recipe to craft")
    character_id: str = Field(..., description="Character performing the crafting")
    station_id: Optional[uuid.UUID] = Field(None, description="Station to use for crafting")
    quantity: int = Field(ge=1, le=100, default=1, description="Number of items to craft")
    ingredients: Dict[str, int] = Field(default_factory=dict, description="Specific ingredients to use")
    tools: Dict[str, str] = Field(default_factory=dict, description="Specific tools to use")
    priority: int = Field(ge=1, le=10, default=5, description="Crafting priority (1=low, 10=high)")
    auto_complete: bool = Field(default=True, description="Auto-complete when finished")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")

class CraftingStartResponseSchema(BaseModel):
    """Schema for crafting start responses."""
    crafting_id: str = Field(..., description="Unique crafting operation ID")
    recipe_id: uuid.UUID = Field(..., description="Recipe being crafted")
    character_id: str = Field(..., description="Character performing the crafting")
    station_id: Optional[uuid.UUID] = Field(None, description="Station being used")
    quantity: int = Field(..., description="Number of items being crafted")
    status: CraftingStatus = Field(..., description="Current status")
    start_time: datetime = Field(..., description="When crafting started")
    estimated_completion: datetime = Field(..., description="Estimated completion time")
    estimated_duration: int = Field(..., description="Estimated duration in seconds")
    efficiency_multiplier: float = Field(default=1.0, description="Applied efficiency multiplier")
    quality_bonus: float = Field(default=0.0, description="Applied quality bonus")
    experience_multiplier: float = Field(default=1.0, description="Experience multiplier")
    ingredients_consumed: Dict[str, int] = Field(default_factory=dict, description="Ingredients consumed")
    tools_used: Dict[str, str] = Field(default_factory=dict, description="Tools being used")

class CraftingProgressSchema(BaseModel):
    """Schema for crafting progress updates."""
    crafting_id: str = Field(..., description="Crafting operation ID")
    progress_percentage: float = Field(ge=0.0, le=100.0, description="Completion percentage")
    current_step: str = Field(default="", description="Current crafting step")
    steps_completed: int = Field(ge=0, description="Number of steps completed")
    total_steps: int = Field(ge=1, description="Total number of steps")
    time_elapsed: int = Field(ge=0, description="Time elapsed in seconds")
    time_remaining: int = Field(ge=0, description="Estimated time remaining in seconds")
    quality_indicators: Dict[str, Any] = Field(default_factory=dict, description="Quality indicators")
    events: List[str] = Field(default_factory=list, description="Recent crafting events")

class CraftingStatusResponseSchema(BaseModel):
    """Schema for crafting status responses."""
    crafting_id: str = Field(..., description="Crafting operation ID")
    recipe_id: uuid.UUID = Field(..., description="Recipe being crafted")
    character_id: str = Field(..., description="Character performing the crafting")
    station_id: Optional[uuid.UUID] = Field(None, description="Station being used")
    quantity: int = Field(..., description="Number of items being crafted")
    status: CraftingStatus = Field(..., description="Current status")
    start_time: datetime = Field(..., description="When crafting started")
    completion_time: Optional[datetime] = Field(None, description="When crafting completed")
    progress: CraftingProgressSchema = Field(..., description="Current progress")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="Crafting results if completed")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class CraftingCompleteSchema(BaseModel):
    """Schema for completing a crafting operation."""
    crafting_id: str = Field(..., description="Crafting operation ID")
    character_id: str = Field(..., description="Character completing the crafting")
    force_complete: bool = Field(default=False, description="Force completion even if not ready")
    quality_override: Optional[QualityLevel] = Field(None, description="Override quality calculation")

class CraftingResultItemSchema(BaseModel):
    """Schema for individual crafting result items."""
    item_id: str = Field(..., description="ID of the produced item")
    quantity: int = Field(ge=1, description="Quantity produced")
    quality: QualityLevel = Field(..., description="Quality of the produced item")
    durability: Optional[float] = Field(None, ge=0.0, le=100.0, description="Item durability percentage")
    enchantments: List[str] = Field(default_factory=list, description="Applied enchantments")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Special properties")
    crafted_by: str = Field(..., description="Character who crafted the item")
    crafted_at: datetime = Field(..., description="When the item was crafted")
    recipe_used: uuid.UUID = Field(..., description="Recipe used to craft the item")
    station_used: Optional[uuid.UUID] = Field(None, description="Station used for crafting")

class CraftingCompleteResponseSchema(BaseModel):
    """Schema for crafting completion responses."""
    crafting_id: str = Field(..., description="Crafting operation ID")
    success: bool = Field(..., description="Whether crafting was successful")
    status: CraftingStatus = Field(..., description="Final status")
    completion_time: datetime = Field(..., description="When crafting completed")
    total_duration: int = Field(..., description="Total crafting duration in seconds")
    items_produced: List[CraftingResultItemSchema] = Field(default_factory=list, description="Items produced")
    experience_gained: Dict[str, int] = Field(default_factory=dict, description="Experience gained by skill")
    achievements_unlocked: List[str] = Field(default_factory=list, description="Achievements unlocked")
    recipes_discovered: List[uuid.UUID] = Field(default_factory=list, description="New recipes discovered")
    materials_returned: Dict[str, int] = Field(default_factory=dict, description="Unused materials returned")
    tools_durability: Dict[str, float] = Field(default_factory=dict, description="Tool durability after use")
    message: str = Field(default="", description="Completion message")

class CraftingCancelSchema(BaseModel):
    """Schema for cancelling a crafting operation."""
    crafting_id: str = Field(..., description="Crafting operation ID")
    character_id: str = Field(..., description="Character cancelling the crafting")
    reason: str = Field(default="", description="Reason for cancellation")
    return_materials: bool = Field(default=True, description="Whether to return consumed materials")

class CraftingCancelResponseSchema(BaseModel):
    """Schema for crafting cancellation responses."""
    crafting_id: str = Field(..., description="Crafting operation ID")
    cancelled: bool = Field(..., description="Whether cancellation was successful")
    cancellation_time: datetime = Field(..., description="When crafting was cancelled")
    materials_returned: Dict[str, int] = Field(default_factory=dict, description="Materials returned")
    partial_results: List[CraftingResultItemSchema] = Field(default_factory=list, description="Partial results if any")
    experience_gained: Dict[str, int] = Field(default_factory=dict, description="Partial experience gained")
    message: str = Field(default="", description="Cancellation message")

class CraftingQueueSchema(BaseModel):
    """Schema for crafting queue requests."""
    character_id: str = Field(..., description="Character ID")
    include_completed: bool = Field(default=False, description="Include completed operations")
    include_failed: bool = Field(default=False, description="Include failed operations")
    limit: int = Field(ge=1, le=100, default=20, description="Maximum number of operations to return")

class CraftingQueueResponseSchema(BaseModel):
    """Schema for crafting queue responses."""
    character_id: str = Field(..., description="Character ID")
    active_operations: List[CraftingStatusResponseSchema] = Field(default_factory=list, description="Active crafting operations")
    queued_operations: List[CraftingStatusResponseSchema] = Field(default_factory=list, description="Queued operations")
    completed_operations: List[CraftingStatusResponseSchema] = Field(default_factory=list, description="Recently completed operations")
    total_active: int = Field(default=0, description="Total active operations")
    total_queued: int = Field(default=0, description="Total queued operations")
    estimated_queue_time: int = Field(default=0, description="Estimated time to process queue in seconds")

class CraftingBatchSchema(BaseModel):
    """Schema for batch crafting operations."""
    recipes: List[CraftingStartSchema] = Field(..., min_items=1, max_items=10, description="Recipes to craft in batch")
    character_id: str = Field(..., description="Character performing the batch crafting")
    sequential: bool = Field(default=True, description="Whether to craft sequentially or in parallel")
    auto_manage_resources: bool = Field(default=True, description="Auto-manage ingredient allocation")
    priority: int = Field(ge=1, le=10, default=5, description="Batch priority")

class CraftingBatchResponseSchema(BaseModel):
    """Schema for batch crafting responses."""
    batch_id: str = Field(..., description="Batch operation ID")
    character_id: str = Field(..., description="Character performing the batch")
    crafting_operations: List[CraftingStartResponseSchema] = Field(..., description="Individual crafting operations")
    total_operations: int = Field(..., description="Total number of operations in batch")
    estimated_total_time: int = Field(..., description="Estimated total time for batch in seconds")
    sequential: bool = Field(..., description="Whether batch is sequential")
    status: CraftingStatus = Field(..., description="Batch status")
    created_at: datetime = Field(..., description="When batch was created") 