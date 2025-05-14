"""Budget management API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..cloud_cost.services import BudgetMonitorService
from . import schemas
from ..core.api.fastapi import APIResponse, APIError, NotFoundError

router = APIRouter(tags=["budgets"])

@router.post("/", response_model=APIResponse[schemas.Budget])
async def create_budget(
    budget: schemas.BudgetCreate,
    db: Session = Depends(get_db)
):
    """Create a new budget."""
    try:
        service = BudgetMonitorService(db)
        data = service.create_budget(
            name=budget.name,
            amount=budget.amount,
            currency=budget.currency,
            period=budget.period,
            scope_type=budget.scope_type,
            scope_id=budget.scope_id,
            alert_thresholds=budget.alert_thresholds
        )
        return APIResponse.created(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.get("/", response_model=APIResponse[List[schemas.BudgetStatus]])
async def get_all_budgets(
    active_only: bool = Query(True, description="Only include active budgets"),
    db: Session = Depends(get_db)
):
    """Get status of all budgets."""
    try:
        service = BudgetMonitorService(db)
        data = service.get_all_budget_statuses(active_only)
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.get("/{budget_id}", response_model=APIResponse[schemas.BudgetStatus])
async def get_budget_status(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """Get status of a specific budget."""
    try:
        service = BudgetMonitorService(db)
        status = service.get_budget_status(budget_id)
        if not status:
            raise NotFoundError("Budget not found")
        return APIResponse.success(data=status)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.put("/{budget_id}", response_model=APIResponse[schemas.Budget])
async def update_budget(
    budget_id: int,
    budget: schemas.BudgetUpdate,
    db: Session = Depends(get_db)
):
    """Update a budget."""
    try:
        service = BudgetMonitorService(db)
        updated = service.update_budget(budget_id, **budget.dict(exclude_unset=True))
        if not updated:
            raise NotFoundError("Budget not found")
        return APIResponse.success(data=updated)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.delete("/{budget_id}", response_model=APIResponse[dict])
async def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """Delete a budget."""
    try:
        service = BudgetMonitorService(db)
        if not service.delete_budget(budget_id):
            raise NotFoundError("Budget not found")
        return APIResponse.success(data={"message": "Budget deleted successfully"})
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.get("/{budget_id}/forecast", response_model=APIResponse[schemas.BudgetForecast])
async def get_budget_forecast(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """Get spending forecast for a budget."""
    try:
        service = BudgetMonitorService(db)
        forecast = service.get_budget_forecast(budget_id)
        if not forecast:
            raise NotFoundError("Budget not found")
        return APIResponse.success(data=forecast)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.get("/{budget_id}/history", response_model=APIResponse[List[schemas.BudgetHistory]])
async def get_budget_history(
    budget_id: int,
    months: int = Query(12, description="Number of months of history to return"),
    db: Session = Depends(get_db)
):
    """Get historical budget performance."""
    try:
        service = BudgetMonitorService(db)
        history = service.get_budget_history(budget_id, months)
        if not history and months > 0:
            raise NotFoundError("Budget not found")
        return APIResponse.success(data=history)
    except NotFoundError:
        raise
    except Exception as e:
        raise APIError(str(e))

@router.get("/alerts", response_model=APIResponse[List[schemas.BudgetAlert]])
async def check_budget_alerts(
    db: Session = Depends(get_db)
):
    """Check all budgets and create alerts if thresholds are exceeded."""
    try:
        service = BudgetMonitorService(db)
        data = service.check_budget_alerts()
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e)) 