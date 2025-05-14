from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.schemas.cleanup import (
    CleanupRuleCreate, CleanupRuleUpdate, CleanupRuleResponse,
    CleanupEntryCreate, CleanupEntryUpdate, CleanupEntryResponse,
    CleanupSummary, ResourceCleanupStatus, BulkCleanupResponse
)
from app.services.cleanup_service import CleanupService
from app.db.session import get_db
from app.core.api.fastapi import APIResponse, APIError, NotFoundError

router = APIRouter(tags=["cleanup"])

@router.post("/rules/", response_model=APIResponse[CleanupRuleResponse])
def create_cleanup_rule(
    rule: CleanupRuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new cleanup rule."""
    try:
        cleanup_service = CleanupService(db)
        data = cleanup_service.create_rule(rule)
        return APIResponse.created(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.get("/rules/", response_model=APIResponse[List[CleanupRuleResponse]])
def get_cleanup_rules(
    provider_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all cleanup rules, optionally filtered by provider and status."""
    try:
        cleanup_service = CleanupService(db)
        data = cleanup_service.get_rules(provider_id, is_active)
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.get("/rules/{rule_id}", response_model=APIResponse[CleanupRuleResponse])
def get_cleanup_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific cleanup rule by ID."""
    try:
        cleanup_service = CleanupService(db)
        rule = cleanup_service.get_rule(rule_id)
        if not rule:
            raise NotFoundError("Cleanup rule not found")
        return APIResponse.success(data=rule)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.put("/rules/{rule_id}", response_model=APIResponse[CleanupRuleResponse])
def update_cleanup_rule(
    rule_id: int,
    rule_update: CleanupRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific cleanup rule."""
    try:
        cleanup_service = CleanupService(db)
        updated_rule = cleanup_service.update_rule(rule_id, rule_update)
        if not updated_rule:
            raise NotFoundError("Cleanup rule not found")
        return APIResponse.success(data=updated_rule)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.delete("/rules/{rule_id}", response_model=APIResponse[dict])
def delete_cleanup_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a cleanup rule."""
    try:
        cleanup_service = CleanupService(db)
        if not cleanup_service.delete_rule(rule_id):
            raise NotFoundError("Cleanup rule not found")
        return APIResponse.success(data={"message": "Rule deleted successfully"})
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.post("/entries/", response_model=APIResponse[CleanupEntryResponse])
def create_cleanup_entry(
    entry: CleanupEntryCreate,
    db: Session = Depends(get_db)
):
    """Create a new cleanup entry."""
    try:
        cleanup_service = CleanupService(db)
        data = cleanup_service.create_entry(entry)
        return APIResponse.created(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.get("/entries/", response_model=APIResponse[List[CleanupEntryResponse]])
def get_cleanup_entries(
    provider_id: Optional[int] = None,
    resource_type: Optional[str] = None,
    is_cleaned: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all cleanup entries, optionally filtered."""
    try:
        cleanup_service = CleanupService(db)
        data = cleanup_service.get_entries(provider_id, resource_type, is_cleaned)
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.get("/entries/{entry_id}", response_model=APIResponse[CleanupEntryResponse])
def get_cleanup_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific cleanup entry by ID."""
    try:
        cleanup_service = CleanupService(db)
        entry = cleanup_service.get_entry(entry_id)
        if not entry:
            raise NotFoundError("Cleanup entry not found")
        return APIResponse.success(data=entry)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.put("/entries/{entry_id}", response_model=APIResponse[CleanupEntryResponse])
def update_cleanup_entry(
    entry_id: int,
    entry_update: CleanupEntryUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific cleanup entry."""
    try:
        cleanup_service = CleanupService(db)
        updated_entry = cleanup_service.update_entry(entry_id, entry_update)
        if not updated_entry:
            raise NotFoundError("Cleanup entry not found")
        return APIResponse.success(data=updated_entry)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.get("/summary/", response_model=APIResponse[CleanupSummary])
def get_cleanup_summary(
    db: Session = Depends(get_db)
):
    """Get summary statistics for cleanup operations."""
    try:
        cleanup_service = CleanupService(db)
        data = cleanup_service.get_cleanup_summary()
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.get("/identify/", response_model=APIResponse[List[CleanupEntryResponse]])
def identify_resources_for_cleanup(
    db: Session = Depends(get_db)
):
    """Identify resources that match cleanup rules criteria."""
    try:
        cleanup_service = CleanupService(db)
        data = cleanup_service.identify_resources_for_cleanup()
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.post("/entries/{entry_id}/mark-cleaned", response_model=APIResponse[dict])
def mark_resource_cleaned(
    entry_id: int,
    cleanup_reason: str = Query(..., description="Reason for cleanup"),
    success: bool = Query(True, description="Whether cleanup was successful"),
    db: Session = Depends(get_db)
):
    """Mark a resource as cleaned with status and reason."""
    try:
        cleanup_service = CleanupService(db)
        success, error = cleanup_service.mark_resource_cleaned(entry_id, cleanup_reason, success)
        if not success:
            raise NotFoundError(error or "Failed to mark resource as cleaned")
        return APIResponse.success(data={"message": "Resource marked as cleaned successfully"})
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e)) 