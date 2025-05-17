"""WebSocket manager for real-time updates."""

from typing import Dict, Set, Optional, Any, List
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect, Depends, status
from fastapi.responses import JSONResponse
from .region import RegionManager
from .viewport import ViewportManager
from .renderer import RegionRenderer
from backend.app.core.security import decode_access_token
import time

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

class ChannelManager:
    """Manages topic/channel-based subscriptions and message routing."""
    def __init__(self):
        self.channels: Dict[str, Set[str]] = {}  # channel -> set of client_ids
        self.client_channels: Dict[str, Set[str]] = {}  # client_id -> set of channels

    def subscribe(self, client_id: str, channel: str):
        self.channels.setdefault(channel, set()).add(client_id)
        self.client_channels.setdefault(client_id, set()).add(channel)

    def unsubscribe(self, client_id: str, channel: str):
        if channel in self.channels:
            self.channels[channel].discard(client_id)
            if not self.channels[channel]:
                del self.channels[channel]
        if client_id in self.client_channels:
            self.client_channels[client_id].discard(channel)
            if not self.client_channels[client_id]:
                del self.client_channels[client_id]

    def get_channels(self, client_id: str) -> Set[str]:
        return self.client_channels.get(client_id, set())

    def get_clients(self, channel: str) -> Set[str]:
        return self.channels.get(channel, set())

class PresenceManager:
    """Tracks online status, last activity, typing indicators."""
    def __init__(self):
        self.online: Dict[str, float] = {}  # client_id -> last seen timestamp
        self.typing: Set[str] = set()

    def set_online(self, client_id: str):
        self.online[client_id] = time.time()

    def set_offline(self, client_id: str):
        if client_id in self.online:
            del self.online[client_id]
        self.typing.discard(client_id)

    def set_typing(self, client_id: str, is_typing: bool):
        if is_typing:
            self.typing.add(client_id)
        else:
            self.typing.discard(client_id)

    def is_online(self, client_id: str) -> bool:
        return client_id in self.online

    def get_last_seen(self, client_id: str) -> Optional[float]:
        return self.online.get(client_id)

    def is_typing(self, client_id: str) -> bool:
        return client_id in self.typing

class EventSchemas:
    """Defines event schemas for notifications, updates, errors."""
    @staticmethod
    def notification(message: str, level: str = "info", data: Optional[dict] = None):
        return {"type": "notification", "level": level, "message": message, "data": data or {}}

    @staticmethod
    def error(message: str, code: int = 400):
        return {"type": "error", "message": message, "code": code}

    @staticmethod
    def presence(client_id: str, online: bool, last_seen: Optional[float] = None):
        return {"type": "presence", "client_id": client_id, "online": online, "last_seen": last_seen}

    @staticmethod
    def typing(client_id: str, is_typing: bool):
        return {"type": "typing", "client_id": client_id, "is_typing": is_typing}

# Extend ConnectionManager for JWT auth, channel, and presence
class ExtendedConnectionManager(ConnectionManager):
    def __init__(self):
        super().__init__()
        self.channel_manager = ChannelManager()
        self.presence_manager = PresenceManager()
        self.message_queues: Dict[str, List[dict]] = {}  # client_id -> queued messages

    async def connect(self, websocket: WebSocket, token: str, client_id: str, width: float, height: float):
        # JWT authentication
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            if not user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.presence_manager.set_online(client_id)
        self.channel_manager.subscribe(client_id, f"user:{client_id}")  # auto-subscribe to personal channel
        viewport = ViewportManager(width, height)
        self.client_viewports[client_id] = viewport
        self.client_renderers[client_id] = RegionRenderer(viewport)
        # Deliver queued messages if any
        if client_id in self.message_queues:
            for msg in self.message_queues[client_id]:
                await websocket.send_json(msg)
            del self.message_queues[client_id]

    def disconnect(self, client_id: str):
        super().disconnect(client_id)
        self.presence_manager.set_offline(client_id)
        # Remove from all channels
        for channel in list(self.channel_manager.get_channels(client_id)):
            self.channel_manager.unsubscribe(client_id, channel)

    async def send_channel_message(self, message: dict, channel: str):
        for client_id in self.channel_manager.get_clients(channel):
            await self.send_personal_message(message, client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except WebSocketDisconnect:
                self.disconnect(client_id)
        else:
            # Queue message for offline clients
            self.message_queues.setdefault(client_id, []).append(message)

# FastAPI WebSocket endpoint
from fastapi import APIRouter
router = APIRouter()

manager = ExtendedConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Expect query params: token, client_id, width, height
    token = websocket.query_params.get("token")
    client_id = websocket.query_params.get("client_id")
    width = float(websocket.query_params.get("width", 800))
    height = float(websocket.query_params.get("height", 600))
    await manager.connect(websocket, token, client_id, width, height)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle subscription, presence, typing, etc.
            msg_type = data.get("type")
            if msg_type == "subscribe":
                channel = data.get("channel")
                if channel:
                    manager.channel_manager.subscribe(client_id, channel)
            elif msg_type == "unsubscribe":
                channel = data.get("channel")
                if channel:
                    manager.channel_manager.unsubscribe(client_id, channel)
            elif msg_type == "typing":
                is_typing = data.get("is_typing", False)
                manager.presence_manager.set_typing(client_id, is_typing)
                await manager.send_channel_message(EventSchemas.typing(client_id, is_typing), f"user:{client_id}")
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            # ... handle other message types (viewport, region, etc.) ...
            else:
                await manager.handle_client_message(client_id, msg_type, data)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# TODO: Move channel, presence, and event schema classes to their own modules for maintainability.
# TODO: Add persistent subscription storage for reconnects.
# TODO: Add more robust error handling and logging.
# TODO: Add unit/integration tests for all new features. 