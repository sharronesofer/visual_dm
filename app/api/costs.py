"""Cost monitoring API endpoints."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..cloud_cost.services import CostMonitorService
from .schemas import CostSummary, CostTrend, CostEntry
from ..core.api.fastapi import APIResponse, APIError

router = APIRouter(tags=["costs"])

@router.get("/summary", response_model=APIResponse[List[CostSummary]])
async def get_cost_summary(
    start_time: datetime = Query(..., description="Start time for cost summary"),
    end_time: datetime = Query(..., description="End time for cost summary"),
    group_by: Optional[str] = Query(None, description="Group results by: service, provider, day, month"),
    provider_id: Optional[int] = Query(None, description="Filter by specific provider"),
    db: Session = Depends(get_db)
):
    """Get cost summary for specified period."""
    try:
        service = CostMonitorService(db)
        data = service.get_cost_summary(start_time, end_time, group_by, provider_id)
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e))

@router.post("/collect", response_model=APIResponse[List[CostEntry]])
async def collect_costs(
    start_time: datetime = Query(..., description="Start time for cost collection"),
    end_time: datetime = Query(..., description="End time for cost collection"),
    provider_id: Optional[int] = Query(None, description="Collect from specific provider"),
    filters: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Collect cost data from cloud providers."""
    try:
        service = CostMonitorService(db)
        service.initialize_collectors()
        data = service.collect_costs(start_time, end_time, provider_id, filters)
        return APIResponse.success(data=data)
    except Exception as e:
        raise APIError(str(e)) 