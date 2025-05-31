"""
Main entry point for the Visual DM backend.

This file initializes the FastAPI application, configures middleware,
includes all routers, and sets up startup and shutdown events.
"""

import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import List, Dict, Any

# Import API routers
# from backend.api.routers import register_routers # Commenting out the old way
from backend.systems.combat.routers.combat_router import router as combat_router  # Import the new combat router

# Import character router
try:
    from backend.systems.character.routers.character_router import router as character_router
except ImportError:
    character_router = None

# Import error reporting router
try:
    from backend.systems.error_reporting.router import router as error_reporting_router
except ImportError:
    error_reporting_router = None

# Import save/load endpoints
try:
    from backend.systems.world_state.api.save_load_endpoints import router as save_load_router
except ImportError:
    save_load_router = None

# Import performance monitoring system
try:
    from backend.systems.performance.router import router as performance_router
    from backend.systems.performance.monitoring_middleware import PerformanceMiddleware
except ImportError:
    performance_router = None
    PerformanceMiddleware = None

# Temporarily disable problematic routers for basic startup test
# from backend.systems.region.router import (
#     router as region_router,
# )  # Import region router
# from backend.systems.world_generation.router import (
#     router as world_generation_router,
# )  # Import world_gen router
# from backend.systems.character.routers import (
#     relationship_router,
# )  # Import canonical relationship router

# Try importing safer routers
try:
    from backend.systems.quest import quest_api_router  # Import consolidated quest router
except ImportError:
    quest_api_router = None

try:
    from backend.systems.population import population_router  # Import population router
except ImportError:
    population_router = None

try:
    from backend.infrastructure.auth.auth_user.routers.auth_router import router as auth_router  # Import auth router
except ImportError:
    auth_router = None

# Temporarily disable motif router due to syntax errors
# try:
#     from backend.systems.motif.router import router as motif_router  # Import motif router
# except ImportError:
motif_router = None

try:
    from backend.systems.arc.routers.arc_router import router as arc_router  # Import arc router
except ImportError:
    arc_router = None

# Import system modules
try:
    from backend.systems.time.services.time_manager import TimeManager
    from backend.systems.time.routers import time_router
except ImportError:
    class TimeManager:
        def advance_time(self, amount):
            pass
        def get_current_time(self):
            return {"time": "mock"}
    time_router = None

try:
    from backend.infrastructure.analytics import register_with_event_system
except ImportError:
    def register_with_event_system():
        return "mock analytics"

# Import analytics router
try:
    from backend.infrastructure.analytics.routers.router import router as analytics_router
except ImportError:
    analytics_router = None

# Import LLM router
try:
    from backend.infrastructure.llm.api.llm_router import router as llm_router
except ImportError:
    llm_router = None


def create_app() -> FastAPI:
    """
    Create a new FastAPI application instance.
    
    Returns:
        FastAPI: A configured FastAPI application.
    """
    # Create FastAPI app
    app = FastAPI(
        title="Visual DM",
        description="Backend API for the Visual DM application",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add performance monitoring middleware
    if PerformanceMiddleware:
        app.add_middleware(
            PerformanceMiddleware,
            enable_detailed_logging=True,
            exclude_paths=["/health", "/docs", "/openapi.json", "/performance/ws"]
        )
    
    # Register all routers
    # register_routers(app) # Commenting out the old way
    app.include_router(combat_router)  # Include the new combat router directly
    # app.include_router(region_router)
    # app.include_router(world_generation_router)
    # app.include_router(relationship_router)  # Include the canonical relationship router
    
    # Include optional routers if available
    if quest_api_router:
        app.include_router(quest_api_router)  # Include the consolidated quest router
    if population_router:
        app.include_router(population_router)  # Include the population router
    if time_router:
        app.include_router(time_router)  # Include the time system router
    if auth_router:
        app.include_router(auth_router)  # Include the auth system router
    if motif_router:
        app.include_router(motif_router)  # Include the motif router
    if arc_router:
        app.include_router(arc_router)  # Include the arc router
    if character_router:
        app.include_router(character_router)  # Include the character service router
    if save_load_router:
        app.include_router(save_load_router)  # Include the save/load router
    
    # Include performance monitoring router
    if performance_router:
        app.include_router(performance_router)  # Include the performance monitoring router
    
    # Include error reporting router
    if error_reporting_router:
        app.include_router(error_reporting_router)  # Include the error reporting router
    
    # Include analytics router
    if analytics_router:
        app.include_router(analytics_router)  # Include the analytics router
    
    # Include LLM router
    if llm_router:
        app.include_router(llm_router)  # Include the LLM router
    
    # Basic routes
    @app.get("/")
    async def root():
        return {"message": "Welcome to Visual DM Backend API"}
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        print("Starting Visual DM backend...")
        
        # Initialize database tables
        try:
            # Import all models to ensure they're registered with Base
            print("Importing character models...")
            from backend.systems.character.models import Character
            # from backend.systems.character.models.character_progression import CharacterProgression
            
            # Import database directly using importlib to avoid async session issues
            import importlib.util
            import os
            db_file_path = os.path.join(os.path.dirname(__file__), 'systems', 'shared', 'database.py')
            spec = importlib.util.spec_from_file_location("sync_database", db_file_path)
            sync_db = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sync_db)
            
            print("Creating database tables...")
            sync_db.Base.metadata.create_all(bind=sync_db.engine)
            print("Database tables initialized successfully")
            
            # Test the character table exists
            session = sync_db.SessionLocal()
            try:
                count = session.query(Character).count()
                print(f"Character table verified - contains {count} characters")
            except Exception as e:
                print(f"Warning: Could not query character table: {e}")
            finally:
                session.close()
                
        except Exception as e:
            print(f"Warning: Database initialization failed: {e}")
            import traceback
            print(traceback.format_exc())
        
        # Initialize analytics service with event system integration
        analytics_service = register_with_event_system()
        print(f"Analytics service initialized: {analytics_service}")
        
        # Initialize error reporting service
        if error_reporting_router:
            try:
                from backend.systems.error_reporting.service import get_error_reporting_service
                error_service = get_error_reporting_service()
                print("Error reporting service initialized successfully")
            except Exception as e:
                print(f"Warning: Error reporting service initialization failed: {e}")
        
        # Initialize services here
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up resources on shutdown."""
        print("Shutting down Visual DM backend...")
        # Clean up resources here
    
    return app


# Global connection manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

# Initialize service managers
time_manager = TimeManager()

# Create the app
app = create_app()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process message based on type
            if message.get("type") == "time_advance":
                time_manager.advance_time(message.get("amount", 1))
                current_time = time_manager.get_current_time()
                await manager.broadcast({"type": "time_update", "data": current_time})
            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong", "data": "Server is alive"})
            else:
                await websocket.send_json(
                    {"type": "error", "data": "Unknown message type"}
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(
            {"type": "system_message", "data": "A client has disconnected"}
        )


# Run with: uvicorn backend.main:app --reload
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
