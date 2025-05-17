from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .combat.routes import router as combat_router
from .combat.websocket import router as websocket_router

# Create the FastAPI app
app = FastAPI(
    title="Visual DM API",
    description="API for Visual Dungeon Master application",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(combat_router)
app.include_router(websocket_router)

@app.get("/")
async def root():
    """Root endpoint returning a welcome message"""
    return {"message": "Welcome to the Visual DM API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"} 