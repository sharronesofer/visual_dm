from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, register_endpoints

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/system", tags=["System"])

# Add more routers here as your API grows
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(items.router, prefix="/items", tags=["Items"])

def init_api(app):
    register_endpoints(app) 