"""FastAPI application entry point."""

from datetime import datetime
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.responses import PlainTextResponse

from .database import get_db
from .cloud_cost.services import CostMonitorService, CleanupMonitorService, BudgetMonitorService
from .api import costs, budgets, cleanup, providers, characters
from .world import router as world_router

app = FastAPI(
    title="Visual DM Backend",
    description="Backend API for Visual DM application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(costs.router, prefix="/api/v1/costs", tags=["costs"])
app.include_router(budgets.router, prefix="/api/v1/budgets", tags=["budgets"])
app.include_router(cleanup.router, prefix="/api/v1/cleanup", tags=["cleanup"])
app.include_router(providers.router, prefix="/api/v1/providers", tags=["providers"])
app.include_router(world_router.router, prefix="/api/v1/world", tags=["world"])
app.include_router(characters.router, prefix="/api/v1/characters", tags=["characters"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup."""
    try:
        # Get database session
        db = next(get_db())
        
        try:
            # Initialize services
            cost_service = CostMonitorService(db)
            cleanup_service = CleanupMonitorService(db)
            budget_service = BudgetMonitorService(db)
            
            # Initialize collectors for each service
            cost_service.initialize_collectors()
            cleanup_service.initialize_collectors()
        finally:
            # Always close the session
            db.close()
    except Exception as e:
        print(f"Error during startup: {e}")
        # Continue startup even if initialization fails
        pass

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Visual DM Backend API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# ASCII symbols for terrain and weather
TERRAIN_SYMBOLS = {
    'plains': '.',
    'forest': '*',
    'mountain': '^',
    'water': '~',
    'desert': ':',
    'urban': '#',
}
WEATHER_OVERLAYS = {
    'rain': '[34m~[0m',  # Blue ~
    'snow': '*',
    'fog': '#',
    'storm': 'S',
    'windy': 'w',
    'clear': '',
}

class HexCell:
    def __init__(self, q, r, terrain='plains', elevation=0, discovered=True, weather=None):
        self.q = q
        self.r = r
        self.terrain = terrain
        self.elevation = elevation
        self.discovered = discovered
        self.weather = weather

class HexGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cells = {}
        for r in range(height):
            for q in range(width):
                self.cells[(q, r)] = HexCell(q, r)
    def get(self, q, r):
        return self.cells.get((q, r))

# Simple noise for terrain
import random

def pseudo_random(q, r, seed):
    return random.Random(q * 374761393 + r * 668265263 + seed * 982451653).random()

def generate_region_terrain(grid, seed=42):
    for r in range(grid.height):
        for q in range(grid.width):
            cell = grid.get(q, r)
            n = pseudo_random(q, r, seed)
            if n < 0.05:
                cell.terrain = 'water'
            elif n > 0.7:
                cell.terrain = 'mountain'
            elif n > 0.4:
                cell.terrain = 'forest'
            elif n < 0.1:
                cell.terrain = 'desert'
            elif ((q + r) % 10 == 0):
                cell.terrain = 'urban'
            else:
                cell.terrain = 'plains'

def assign_region_weather(grid, seed=42):
    weather_types = ['clear', 'rain', 'snow', 'fog', 'storm', 'windy']
    for r in range(grid.height):
        for q in range(grid.width):
            n = pseudo_random(q, r, seed + 1000)
            if n < 0.1:
                grid.get(q, r).weather = 'rain'
            elif n < 0.2:
                grid.get(q, r).weather = 'snow'
            elif n < 0.3:
                grid.get(q, r).weather = 'fog'
            elif n < 0.35:
                grid.get(q, r).weather = 'storm'
            elif n < 0.4:
                grid.get(q, r).weather = 'windy'
            else:
                grid.get(q, r).weather = 'clear'

def render_ascii_map(grid, show_weather=True):
    lines = []
    for r in range(grid.height):
        line = ''
        if r % 2 == 1:
            line += ' '
        for q in range(grid.width):
            cell = grid.get(q, r)
            symbol = TERRAIN_SYMBOLS.get(cell.terrain, '?')
            if show_weather and cell.weather and cell.weather != 'clear':
                overlay = WEATHER_OVERLAYS.get(cell.weather, '')
                if overlay:
                    symbol = overlay
            line += symbol + ' '
        lines.append(line.rstrip())
    return '\n'.join(lines)

@app.get("/ascii_map", response_class=PlainTextResponse)
async def ascii_map(
    width: int = Query(10, ge=2, le=50),
    height: int = Query(10, ge=2, le=50),
    seed: int = Query(42),
    show_weather: bool = Query(True)
):
    try:
        grid = HexGrid(width, height)
        generate_region_terrain(grid, seed)
        assign_region_weather(grid, seed)
        ascii_map_str = render_ascii_map(grid, show_weather=show_weather)
        return ascii_map_str
    except Exception as e:
        return PlainTextResponse(f"Error generating ASCII map: {e}", status_code=500) 