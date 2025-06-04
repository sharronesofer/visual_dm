"""
Main FastAPI application entry point

Sets up the FastAPI application with all routers and middleware for the game backend.
Includes autonomous NPC management endpoints for monitoring and administration.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from backend.api.endpoints import npc_autonomous
from backend.systems.npc.services.autonomous_scheduler_service import autonomous_scheduler
# Add rumor system router
from backend.infrastructure.systems.rumor.routers.rumor_router import router as rumor_router
# Add chaos system router  
from backend.infrastructure.systems.chaos.api.chaos_router import router as chaos_router
# Add diplomacy AI router
from backend.infrastructure.api.diplomacy_ai_router import router as diplomacy_ai_router
# Add regular diplomacy router
from backend.infrastructure.api.diplomacy_router import router as diplomacy_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting FastAPI application")
    
    # Start the autonomous NPC scheduler
    try:
        autonomous_scheduler.start_scheduler()
        logger.info("Autonomous NPC scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start autonomous scheduler: {e}")
    
    # Initialize chaos system
    try:
        from backend.systems.chaos.services.chaos_service import ChaosService
        from backend.systems.chaos.core.config import ChaosConfig
        
        chaos_config = ChaosConfig()
        chaos_service = ChaosService(chaos_config)
        await chaos_service.initialize()
        await chaos_service.start()
        logger.info("Chaos system initialized and started successfully")
        
        # Store reference for shutdown
        app.state.chaos_service = chaos_service
    except Exception as e:
        logger.error(f"Failed to start chaos system: {e}")
    
    # Initialize AI diplomacy system
    try:
        logger.info("AI Diplomacy system loaded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI diplomacy system: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application")
    
    # Stop chaos system
    try:
        if hasattr(app.state, 'chaos_service'):
            await app.state.chaos_service.stop()
            logger.info("Chaos system stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop chaos system: {e}")
    
    # Stop the autonomous NPC scheduler
    try:
        autonomous_scheduler.stop_scheduler()
        logger.info("Autonomous NPC scheduler stopped successfully")
    except Exception as e:
        logger.error(f"Failed to stop autonomous scheduler: {e}")


# Create FastAPI application
app = FastAPI(
    title="Game Backend API",
    description="Comprehensive game backend with autonomous NPC management and AI-powered diplomacy",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "scheduler_running": autonomous_scheduler.is_running,
        "ai_diplomacy": "active",
        "message": "Game backend is operational"
    }


# Include routers
app.include_router(npc_autonomous.router)
app.include_router(rumor_router, prefix="/api")
app.include_router(chaos_router, prefix="/api")
app.include_router(diplomacy_router, prefix="/api")
app.include_router(diplomacy_ai_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Game Backend API",
        "version": "1.0.0",
        "autonomous_npc_system": "active",
        "chaos_system": "active",
        "ai_diplomacy_system": "active",
        "scheduler_status": "running" if autonomous_scheduler.is_running else "stopped",
        "endpoints": {
            "autonomous_npc": "/api/npc/autonomous",
            "admin_dashboard": "/api/npc/autonomous/admin/dashboard",
            "system_health": "/api/npc/autonomous/admin/system-health",
            "scheduler_management": "/api/npc/autonomous/admin/scheduler",
            "rumors": "/api/rumors",
            "rumor_statistics": "/api/rumors/statistics/summary",
            "chaos_status": "/api/chaos/status",
            "chaos_events": "/api/chaos/events/active",
            "chaos_pressure": "/api/chaos/pressure/summary",
            "chaos_health": "/api/chaos/health",
            "diplomacy": "/api/diplomacy",
            "diplomacy_ai": "/api/diplomacy/ai",
            "ai_treaty_evaluation": "/api/diplomacy/ai/treaties/evaluate",
            "ai_treaty_optimization": "/api/diplomacy/ai/treaties/optimize",
            "ai_decision_engine": "/api/diplomacy/ai/decisions/evaluate-all/{faction_id}",
            "ai_negotiation": "/api/diplomacy/ai/negotiations/ai-response",
            "ai_batch_decisions": "/api/diplomacy/ai/batch/auto-decisions",
            "ai_system_status": "/api/diplomacy/ai/status"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 