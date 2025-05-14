"""WebSocket manager for real-time updates."""

from typing import Dict, Set, Optional, Any
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from .region import RegionManager
from .viewport import ViewportManager
from .renderer import RegionRenderer

class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_viewports: Dict[str, ViewportManager] = {}
        self.client_renderers: Dict[str, RegionRenderer] = {}
        
    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        width: float,
        height: float
    ) -> None:
        """Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            client_id: Unique client identifier
            width: Initial viewport width
            height: Initial viewport height
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # Create viewport and renderer for client
        viewport = ViewportManager(width, height)
        self.client_viewports[client_id] = viewport
        self.client_renderers[client_id] = RegionRenderer(viewport)
        
    def disconnect(self, client_id: str) -> None:
        """Handle client disconnection.
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            del self.client_viewports[client_id]
            del self.client_renderers[client_id]
            
    async def broadcast(self, message: Dict) -> None:
        """Broadcast message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(client_id)
                
        # Clean up disconnected clients
        for client_id in disconnected:
            self.disconnect(client_id)
            
    async def send_personal_message(self, message: Dict, client_id: str) -> None:
        """Send message to specific client.
        
        Args:
            message: Message to send
            client_id: Target client identifier
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except WebSocketDisconnect:
                self.disconnect(client_id)

class WorldStateManager:
    """Manages world state and real-time updates."""
    
    def __init__(self, region_manager: RegionManager):
        """Initialize world state manager.
        
        Args:
            region_manager: Region manager instance
        """
        self.region_manager = region_manager
        self.connections = ConnectionManager()
        
    async def handle_client_message(
        self,
        client_id: str,
        message_type: str,
        data: Dict
    ) -> None:
        """Handle incoming client message.
        
        Args:
            client_id: Client identifier
            message_type: Type of message
            data: Message data
        """
        if message_type == "viewport_update":
            # Update client's viewport
            viewport = self.connections.client_viewports[client_id]
            
            if "size" in data:
                viewport.set_size(data["size"]["width"], data["size"]["height"])
                
            if "center" in data:
                viewport.pan_to(data["center"]["x"], data["center"]["y"])
                
            if "zoom" in data:
                if "focus_point" in data:
                    viewport.zoom_to(
                        data["zoom"],
                        (data["focus_point"]["x"], data["focus_point"]["y"])
                    )
                else:
                    viewport.zoom_to(data["zoom"])
                    
            # Send updated regions in viewport
            await self.send_viewport_update(client_id)
            
        elif message_type == "region_interaction":
            # Handle region interaction
            region_id = data["region_id"]
            action = data["action"]
            
            if action == "select":
                self.region_manager.update_region_property(
                    region_id,
                    "is_selected",
                    True
                )
                # Broadcast selection to all clients
                await self.connections.broadcast({
                    "type": "region_selected",
                    "region_id": region_id
                })
                
            elif action == "hover":
                self.region_manager.update_region_property(
                    region_id,
                    "is_hovered",
                    True
                )
                # Only update hovering client
                await self.send_viewport_update(client_id)
                
            elif action == "unhover":
                self.region_manager.update_region_property(
                    region_id,
                    "is_hovered",
                    False
                )
                # Only update hovering client
                await self.send_viewport_update(client_id)
                
    async def send_viewport_update(self, client_id: str) -> None:
        """Send updated viewport state to client.
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.connections.client_viewports:
            viewport = self.connections.client_viewports[client_id]
            renderer = self.connections.client_renderers[client_id]
            
            # Get visible regions
            visible_regions = self.region_manager.get_regions_in_viewport(viewport.bounds)
            
            # Render regions and labels
            regions_image = renderer.render_regions(visible_regions)
            labels_image = renderer.render_region_labels(visible_regions)
            
            # Send update
            await self.connections.send_personal_message(
                {
                    "type": "viewport_update",
                    "viewport_state": viewport.get_state(),
                    "regions_image": regions_image.hex(),  # Convert bytes to hex string
                    "labels_image": labels_image.hex()
                },
                client_id
            )
            
    async def handle_region_update(self, region_id: str) -> None:
        """Handle region update and notify affected clients.
        
        Args:
            region_id: ID of updated region
        """
        # Get region
        region = self.region_manager.regions.get(region_id)
        if not region:
            return
            
        # Find clients whose viewport intersects with the region
        affected_clients = []
        for client_id, viewport in self.connections.client_viewports.items():
            if region.intersects_viewport(viewport.bounds):
                affected_clients.append(client_id)
                
        # Send updates to affected clients
        for client_id in affected_clients:
            await self.send_viewport_update(client_id) 