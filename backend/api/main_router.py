"""
Main API Router

This module organizes and registers all resource routers with proper versioning.
"""

from fastapi import FastAPI
from .core.versioning import create_versioned_api, APIVersion
from .characters.routes import router as characters_router
from .core.base_router import create_api_router

def register_routers(app: FastAPI):
    """
    Register all API routers with the FastAPI application
    
    Args:
        app: The FastAPI application instance
    """
    # Create versioned API
    api = create_versioned_api(app)
    
    # Register resource routers with the v1 API
    api.include_router(characters_router, APIVersion.V1)
    
    # Add other resource routers as they are implemented
    # api.include_router(worlds_router, APIVersion.V1)
    # api.include_router(npcs_router, APIVersion.V1)
    # api.include_router(quests_router, APIVersion.V1)
    # api.include_router(combats_router, APIVersion.V1)
    # api.include_router(locations_router, APIVersion.V1)
    # api.include_router(items_router, APIVersion.V1)
    # api.include_router(factions_router, APIVersion.V1)
    # api.include_router(users_router, APIVersion.V1)
    # api.include_router(auth_router, APIVersion.V1)
    
    # Create API documentation router
    docs_router = create_api_router(
        prefix="/docs",
        tags=["API Documentation"]
    )
    
    @docs_router.get("/endpoints", summary="Get API endpoint documentation")
    async def get_api_docs():
        """Get documentation for all API endpoints"""
        # This could be expanded to return actual API documentation
        # For now, we'll point to the Swagger UI
        return {
            "message": "API documentation is available at /docs or /redoc",
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    
    # Add docs router directly to the app (not versioned)
    app.include_router(docs_router)
    
    # Finalize the API setup
    api.finalize() 