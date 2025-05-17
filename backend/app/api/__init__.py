# Auto-generated during TypeScript to Python migration

"""API routes package."""

from fastapi import APIRouter, FastAPI

from .auth import router as auth_router
from .characters import router as characters_router
from .costs import router as costs_router
from .budgets import router as budgets_router
from .cleanup import router as cleanup_router
from .providers import router as providers_router
from .endpoints.dialogue import router as dialogue_router
from backend.app.world.websocket import router as websocket_router

# Create the main API router
api_router = APIRouter()

# Include all API routers
api_router.include_router(auth_router)
api_router.include_router(characters_router)
api_router.include_router(costs_router)
api_router.include_router(budgets_router)
api_router.include_router(cleanup_router)
api_router.include_router(providers_router)
api_router.include_router(dialogue_router)
api_router.include_router(websocket_router)

__all__ = ["api_router"]

# This file is intentionally left empty to make the directory a proper Python package

def get_app() -> FastAPI:
    app = FastAPI()
    # ... existing routers ...
    app.include_router(websocket_router)
    return app
