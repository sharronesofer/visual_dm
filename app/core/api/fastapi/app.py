"""FastAPI application setup with documentation."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from .versioning import VersionedAPIRouter
from ..version_manager import VersionManager, VersionStatus, APIVersion
from ..middleware.version_middleware import VersionMiddleware
from ..middleware.rate_limit import RateLimitMiddleware
from ..middleware.cache import CacheMiddleware
from ..middleware.error_monitoring import ErrorMonitoringMiddleware
from ..error_handling.monitoring import ErrorMonitor
from ..error_handling.handlers import setup_error_handlers
from ..docs.swagger_ui import customize_swagger_ui
from ..docs.markdown_generator import MarkdownGenerator

def create_app() -> FastAPI:
    """Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Game Management API",
        description="RESTful API for game world management",
        version="1.0.0",
        docs_url=None,  # Disable default docs to use custom Swagger UI
        redoc_url=None  # Disable ReDoc
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Set up version manager
    version_manager = VersionManager()
    version_manager.add_version(
        APIVersion(
            version="v1",
            status=VersionStatus.STABLE,
            release_date=datetime.utcnow(),
            description="Initial stable release"
        )
    )
    version_manager.add_version(
        APIVersion(
            version="v2",
            status=VersionStatus.BETA,
            release_date=datetime.utcnow(),
            description="Beta release with enhanced features",
            breaking_changes=[
                "Updated response envelope format",
                "Moved relationship endpoints to dedicated routes",
                "Added required authentication for all endpoints"
            ]
        )
    )
    app.state.version_manager = version_manager
    
    # Set up error monitoring
    error_monitor = ErrorMonitor()
    app.state.error_monitor = error_monitor
    
    # Add middleware (order matters)
    app.add_middleware(ErrorMonitoringMiddleware, error_monitor=error_monitor)
    app.add_middleware(VersionMiddleware, version_manager=version_manager)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(CacheMiddleware)
    
    # Set up error handlers
    setup_error_handlers(app)
    
    # Set up custom Swagger UI
    customize_swagger_ui(app)
    
    # Include routers
    v1_router = VersionedAPIRouter(version="v1")
    v2_router = VersionedAPIRouter(version="v2")
    
    # Register routes for each version
    # V1 routes
    from ..routes.v1 import (
        npc_router as npc_v1,
        item_router as item_v1,
        location_router as location_v1,
        quest_router as quest_v1,
        faction_router as faction_v1
    )
    
    v1_router.include_router(npc_v1, prefix="/npcs", tags=["NPCs"])
    v1_router.include_router(item_v1, prefix="/items", tags=["Items"])
    v1_router.include_router(location_v1, prefix="/locations", tags=["Locations"])
    v1_router.include_router(quest_v1, prefix="/quests", tags=["Quests"])
    v1_router.include_router(faction_v1, prefix="/factions", tags=["Factions"])
    
    # V2 routes with enhanced functionality
    from ..routes.v2 import (
        npc_router as npc_v2,
        item_router as item_v2,
        location_router as location_v2,
        quest_router as quest_v2,
        faction_router as faction_v2,
        relationship_router
    )
    
    v2_router.include_router(npc_v2, prefix="/npcs", tags=["NPCs"])
    v2_router.include_router(item_v2, prefix="/items", tags=["Items"])
    v2_router.include_router(location_v2, prefix="/locations", tags=["Locations"])
    v2_router.include_router(quest_v2, prefix="/quests", tags=["Quests"])
    v2_router.include_router(faction_v2, prefix="/factions", tags=["Factions"])
    v2_router.include_router(relationship_router, prefix="/relationships", tags=["Relationships"])
    
    # Include versioned routers in app
    app.include_router(v1_router)
    app.include_router(v2_router)
    
    # Generate Markdown documentation
    markdown_generator = MarkdownGenerator(app)
    markdown_generator.generate_docs()
    
    return app 