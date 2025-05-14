"""FastAPI application entry point."""

from datetime import datetime
from fastapi import FastAPI, Depends, Query, Request
from sqlalchemy.orm import Session
from fastapi.responses import PlainTextResponse, JSONResponse

from .database import get_db
from .cloud_cost.services import CostMonitorService, CleanupMonitorService, BudgetMonitorService
from .api import costs, budgets, cleanup, providers, characters
from .world import router as world_router
from .search import router as search_router
from .search.middleware import SearchSecurityMiddleware
from .search.exceptions import SearchSecurityError
from .core.api.fastapi import setup_error_handlers, version_routes
from .core.middleware.security import setup_security
from .core.middleware.rate_limit import setup_rate_limiting

# Create FastAPI application
app = FastAPI(
    title="Visual DM Backend",
    description="Backend API for Visual DM application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure security (CORS and security headers)
setup_security(app)

# Configure rate limiting (60 requests per minute in production)
setup_rate_limiting(app, requests_per_minute=60)

# Add search security middleware
app.add_middleware(SearchSecurityMiddleware)

# Set up error handlers
setup_error_handlers(app)

# Group v1 routers
v1_routers = [
    costs.router,
    budgets.router,
    cleanup.router,
    providers.router,
    world_router.router,
    characters.router,
    search_router.router
]

# Version the routes
version_routes(app, v1_routers, version='v1', prefix='/api')

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Visual DM Backend API",
        "version": "1.0.0",
        "docs_url": "/api/docs",
        "redoc_url": "/api/redoc",
        "openapi_url": "/api/openapi.json"
    }

# Exception handlers
@app.exception_handler(SearchSecurityError)
async def search_security_exception_handler(
    request: Request,
    exc: SearchSecurityError
) -> JSONResponse:
    """Handle search security exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The exception that was raised
        
    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=403,
        content={
            "detail": str(exc),
            "type": "security_error"
        }
    ) 