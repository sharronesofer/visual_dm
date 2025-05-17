from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import json
import asyncio
from datetime import datetime

# Import API router registration
from .api.main_router import register_routers
from .api.core.error_handlers import setup_error_handlers

# Create FastAPI application with improved metadata
app = FastAPI(
    title="Visual DM API",
    description="API for Visual DM, a virtual dungeon master assistant that helps manage tabletop RPG campaigns.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.map_state: Dict = {
            "markers": [],
            "center": {"lat": 51.505, "lng": -0.09},
            "zoom": 13
        }

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send current state to new connection
        await websocket.send_json({"type": "state", "data": self.map_state})

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Update internal state based on message type
        if message.get("type") == "marker_add":
            self.map_state["markers"].append(message["data"])
        elif message.get("type") == "marker_update":
            for i, marker in enumerate(self.map_state["markers"]):
                if marker["id"] == message["data"]["id"]:
                    self.map_state["markers"][i] = message["data"]
                    break
        elif message.get("type") == "marker_remove":
            self.map_state["markers"] = [
                m for m in self.map_state["markers"] 
                if m["id"] != message["data"]["id"]
            ]
        elif message.get("type") == "view_update":
            self.map_state["center"] = message["data"]["center"]
            self.map_state["zoom"] = message["data"]["zoom"]

        # Broadcast to all connected clients
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                # Remove failed connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing basic API information.
    
    Returns:
        A simple welcome message with links to documentation.
    """
    return {
        "message": "Welcome to Visual DM Backend API",
        "documentation": "/docs",
        "alternative_docs": "/redoc",
        "openapi_schema": "/openapi.json"
    }

@app.websocket("/ws", tags=["WebSocket"])
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time communication.
    
    This endpoint allows clients to connect via WebSocket for real-time
    updates and map synchronization.
    
    Args:
        websocket: The WebSocket connection.
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            # Add timestamp to all messages
            message["timestamp"] = datetime.utcnow().isoformat()
            await manager.broadcast(message)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({
            "type": "system",
            "data": {"message": "Client disconnected"},
            "timestamp": datetime.utcnow().isoformat()
        })

# Set up global error handlers
setup_error_handlers(app)

# Register API routers
register_routers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 