from fastapi import APIRouter, Depends
from backend.app.schemas.common import HealthCheck
import platform
import time

router = APIRouter()

# Simple in-memory uptime tracker
START_TIME = time.time()


@router.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns basic health information about the API
    """
    import pkg_resources
    
    # Get fastapi version
    fastapi_version = pkg_resources.get_distribution("fastapi").version
    
    # Calculate uptime
    uptime_seconds = time.time() - START_TIME
    
    return HealthCheck(
        status="healthy",
        version=fastapi_version,
        uptime_seconds=round(uptime_seconds),
        python_version=platform.python_version(),
        environment="development",  # In production, get from environment variable
    ) 