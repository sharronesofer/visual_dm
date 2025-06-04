"""
World State WebSocket Handler - Real-time Communication

Provides WebSocket-based real-time synchronization for world state
as specified in the Development Bible WebSocket protocol.
"""

import json
import asyncio
import logging
from typing import Dict, Any, List, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

from backend.systems.world_state.services.services import WorldStateService, create_world_state_service
from backend.systems.world_state.world_types import StateCategory, WorldRegion


logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WebSocket message types as per Bible specification"""
    # Client to Server
    SUBSCRIBE_REGION = "subscribe_region"
    SUBSCRIBE_CATEGORY = "subscribe_category"
    UNSUBSCRIBE_REGION = "unsubscribe_region"
    UNSUBSCRIBE_CATEGORY = "unsubscribe_category"
    GET_STATE = "get_state"
    SET_STATE_VARIABLE = "set_state_variable"
    
    # Server to Client
    WORLD_STATE_INIT = "world_state_init"
    WORLD_STATE_VARIABLE_CHANGED = "world_state_variable_changed"
    CONNECTION_STATUS = "connection_status"
    ERROR = "error"


class WebSocketClient:
    """Represents a connected WebSocket client with subscriptions"""
    
    def __init__(self, websocket: WebSocket, client_id: str):
        self.websocket = websocket
        self.client_id = client_id
        self.subscribed_regions: Set[str] = set()
        self.subscribed_categories: Set[StateCategory] = set()
        self.connected_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    async def send_message(self, message_type: MessageType, data: Any):
        """Send a message to the client"""
        try:
            message = {
                "type": message_type.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.websocket.send_text(json.dumps(message, default=str))
            self.last_activity = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to send message to client {self.client_id}: {e}")
            raise
    
    def should_receive_update(self, region_id: Optional[str], category: StateCategory) -> bool:
        """Check if client should receive a state update"""
        # Check region subscription
        region_match = (
            not self.subscribed_regions or  # No region filter
            (region_id and region_id in self.subscribed_regions) or
            "global" in self.subscribed_regions
        )
        
        # Check category subscription
        category_match = (
            not self.subscribed_categories or  # No category filter
            category in self.subscribed_categories
        )
        
        return region_match and category_match


class WorldStateWebSocketManager:
    """Manages WebSocket connections and real-time state synchronization"""
    
    def __init__(self):
        self.clients: Dict[str, WebSocketClient] = {}
        self.world_state_service: Optional[WorldStateService] = None
        self._client_counter = 0
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the WebSocket manager"""
        try:
            self.world_state_service = await create_world_state_service()
            if not self.world_state_service._initialized:
                await self.world_state_service.initialize()
            
            # Subscribe to state change events
            await self.world_state_service.subscribe_to_state_changes(
                self._on_state_changed,
                'state_changed'
            )
            
            # Start cleanup task
            self._cleanup_task = asyncio.create_task(self._cleanup_inactive_clients())
            
            logger.info("WorldStateWebSocketManager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize WebSocketManager: {e}")
            raise
    
    async def connect_client(self, websocket: WebSocket) -> str:
        """Connect a new WebSocket client"""
        await websocket.accept()
        
        self._client_counter += 1
        client_id = f"client_{self._client_counter}_{int(datetime.utcnow().timestamp())}"
        
        client = WebSocketClient(websocket, client_id)
        self.clients[client_id] = client
        
        # Send initial connection status
        await client.send_message(MessageType.CONNECTION_STATUS, {
            "status": "connected",
            "client_id": client_id,
            "server_time": datetime.utcnow().isoformat()
        })
        
        # Send initial world state
        await self._send_initial_state(client)
        
        logger.info(f"Client {client_id} connected. Total clients: {len(self.clients)}")
        return client_id
    
    async def disconnect_client(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client {client_id} disconnected. Total clients: {len(self.clients)}")
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming WebSocket message from client"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            message_data = data.get("data", {})
            
            client = self.clients.get(client_id)
            if not client:
                logger.warning(f"Received message from unknown client {client_id}")
                return
            
            client.last_activity = datetime.utcnow()
            
            # Route message to appropriate handler
            if message_type == MessageType.SUBSCRIBE_REGION.value:
                await self._handle_subscribe_region(client, message_data)
            elif message_type == MessageType.SUBSCRIBE_CATEGORY.value:
                await self._handle_subscribe_category(client, message_data)
            elif message_type == MessageType.UNSUBSCRIBE_REGION.value:
                await self._handle_unsubscribe_region(client, message_data)
            elif message_type == MessageType.UNSUBSCRIBE_CATEGORY.value:
                await self._handle_unsubscribe_category(client, message_data)
            elif message_type == MessageType.GET_STATE.value:
                await self._handle_get_state(client, message_data)
            elif message_type == MessageType.SET_STATE_VARIABLE.value:
                await self._handle_set_state_variable(client, message_data)
            else:
                await self._send_error(client, f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self._send_error(self.clients.get(client_id), "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
            await self._send_error(self.clients.get(client_id), f"Internal error: {str(e)}")
    
    async def _send_initial_state(self, client: WebSocketClient):
        """Send initial world state to a newly connected client"""
        try:
            if not self.world_state_service:
                return
            
            # Get current state
            state_data = await self.world_state_service.query_state()
            
            # Organize state by category and region
            organized_state = {
                "ENVIRONMENT": {"GLOBAL": {}},
                "POLITICS": {"GLOBAL": {}},
                "ECONOMY": {"GLOBAL": {}},
                "SOCIAL": {"GLOBAL": {}},
                "MILITARY": {"GLOBAL": {}},
                "RELIGIOUS": {"GLOBAL": {}},
                "MAGICAL": {"GLOBAL": {}},
                "QUEST": {"GLOBAL": {}},
                "OTHER": {"GLOBAL": {}}
            }
            
            # Organize data by category and region
            for key, value in state_data.items():
                # Simple categorization based on key prefix
                if key.startswith("faction.") or key.startswith("politics."):
                    category = "POLITICS"
                elif key.startswith("economy.") or key.startswith("resources."):
                    category = "ECONOMY"
                elif key.startswith("weather.") or key.startswith("environment."):
                    category = "ENVIRONMENT"
                elif key.startswith("quest."):
                    category = "QUEST"
                elif key.startswith("magic."):
                    category = "MAGICAL"
                elif key.startswith("military.") or key.startswith("war."):
                    category = "MILITARY"
                elif key.startswith("religion."):
                    category = "RELIGIOUS"
                elif key.startswith("social.") or key.startswith("population."):
                    category = "SOCIAL"
                else:
                    category = "OTHER"
                
                # For now, assume everything is GLOBAL - TODO: Parse region from key
                region = "GLOBAL"
                
                if category not in organized_state:
                    organized_state[category] = {}
                if region not in organized_state[category]:
                    organized_state[category][region] = {}
                
                organized_state[category][region][key] = value
            
            await client.send_message(MessageType.WORLD_STATE_INIT, {
                "state": organized_state
            })
            
        except Exception as e:
            logger.error(f"Failed to send initial state to {client.client_id}: {e}")
    
    async def _handle_subscribe_region(self, client: WebSocketClient, data: Dict[str, Any]):
        """Handle region subscription request"""
        regions = data.get("regions", [])
        for region in regions:
            client.subscribed_regions.add(region)
        
        await client.send_message(MessageType.CONNECTION_STATUS, {
            "status": "subscribed_regions",
            "regions": list(client.subscribed_regions)
        })
    
    async def _handle_subscribe_category(self, client: WebSocketClient, data: Dict[str, Any]):
        """Handle category subscription request"""
        categories = data.get("categories", [])
        for category_str in categories:
            try:
                category = StateCategory(category_str.lower())
                client.subscribed_categories.add(category)
            except ValueError:
                await self._send_error(client, f"Invalid category: {category_str}")
                return
        
        await client.send_message(MessageType.CONNECTION_STATUS, {
            "status": "subscribed_categories",
            "categories": [cat.value for cat in client.subscribed_categories]
        })
    
    async def _handle_unsubscribe_region(self, client: WebSocketClient, data: Dict[str, Any]):
        """Handle region unsubscription request"""
        regions = data.get("regions", [])
        for region in regions:
            client.subscribed_regions.discard(region)
        
        await client.send_message(MessageType.CONNECTION_STATUS, {
            "status": "unsubscribed_regions",
            "regions": list(client.subscribed_regions)
        })
    
    async def _handle_unsubscribe_category(self, client: WebSocketClient, data: Dict[str, Any]):
        """Handle category unsubscription request"""
        categories = data.get("categories", [])
        for category_str in categories:
            try:
                category = StateCategory(category_str.lower())
                client.subscribed_categories.discard(category)
            except ValueError:
                pass  # Ignore invalid categories
        
        await client.send_message(MessageType.CONNECTION_STATUS, {
            "status": "unsubscribed_categories",
            "categories": [cat.value for cat in client.subscribed_categories]
        })
    
    async def _handle_get_state(self, client: WebSocketClient, data: Dict[str, Any]):
        """Handle get state request"""
        try:
            regions = data.get("regions", [])
            categories = data.get("categories", [])
            
            # Get filtered state data
            if regions:
                state_data = {}
                for region_id in regions:
                    region_state = await self.world_state_service.get_region_state(region_id)
                    state_data.update(region_state)
            else:
                state_data = await self.world_state_service.query_state()
            
            # Filter by categories if specified
            if categories:
                filtered_data = {}
                for key, value in state_data.items():
                    if any(cat in key.lower() for cat in categories):
                        filtered_data[key] = value
                state_data = filtered_data
            
            await client.send_message(MessageType.WORLD_STATE_INIT, {
                "state": state_data,
                "filtered": True
            })
            
        except Exception as e:
            await self._send_error(client, f"Failed to get state: {str(e)}")
    
    async def _handle_set_state_variable(self, client: WebSocketClient, data: Dict[str, Any]):
        """Handle set state variable request"""
        try:
            key = data.get("key")
            value = data.get("value")
            region_id = data.get("region_id")
            category_str = data.get("category", "other")
            reason = data.get("reason", f"Client {client.client_id} update")
            
            if not key:
                await self._send_error(client, "Missing required field: key")
                return
            
            # Parse category
            try:
                category = StateCategory(category_str.lower())
            except ValueError:
                category = StateCategory.OTHER
            
            # Set state variable
            success = await self.world_state_service.set_state_variable(
                key=key,
                value=value,
                region_id=region_id,
                category=category,
                reason=reason,
                user_id=client.client_id
            )
            
            if success:
                await client.send_message(MessageType.CONNECTION_STATUS, {
                    "status": "state_updated",
                    "key": key,
                    "value": value
                })
            else:
                await self._send_error(client, f"Failed to update state variable: {key}")
                
        except Exception as e:
            await self._send_error(client, f"Failed to set state variable: {str(e)}")
    
    async def _send_error(self, client: Optional[WebSocketClient], error_message: str):
        """Send error message to client"""
        if client:
            try:
                await client.send_message(MessageType.ERROR, {
                    "error": error_message,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                logger.error(f"Failed to send error to client {client.client_id}: {e}")
    
    async def _on_state_changed(self, event_data: Dict[str, Any]):
        """Handle state change events and broadcast to subscribed clients"""
        try:
            key = event_data.get('key')
            old_value = event_data.get('old_value')
            new_value = event_data.get('new_value')
            region_id = event_data.get('region_id')
            category = event_data.get('category', StateCategory.OTHER)
            reason = event_data.get('reason')
            
            # Create state change message
            change_message = {
                "variable": {
                    "key": key,
                    "value": new_value,
                    "old_value": old_value,
                    "category": category.value if isinstance(category, StateCategory) else str(category),
                    "region": "GLOBAL",  # TODO: Map region_id to WorldRegion
                    "region_id": region_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "system",
                    "reason": reason
                }
            }
            
            # Broadcast to subscribed clients
            disconnected_clients = []
            for client_id, client in self.clients.items():
                try:
                    if client.should_receive_update(region_id, category):
                        await client.send_message(
                            MessageType.WORLD_STATE_VARIABLE_CHANGED,
                            change_message
                        )
                except Exception as e:
                    logger.error(f"Failed to send update to client {client_id}: {e}")
                    disconnected_clients.append(client_id)
            
            # Clean up disconnected clients
            for client_id in disconnected_clients:
                await self.disconnect_client(client_id)
                
        except Exception as e:
            logger.error(f"Error broadcasting state change: {e}")
    
    async def _cleanup_inactive_clients(self):
        """Periodic cleanup of inactive clients"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                now = datetime.utcnow()
                inactive_clients = []
                
                for client_id, client in self.clients.items():
                    # Remove clients inactive for more than 1 hour
                    if (now - client.last_activity).seconds > 3600:
                        inactive_clients.append(client_id)
                
                for client_id in inactive_clients:
                    logger.info(f"Removing inactive client {client_id}")
                    await self.disconnect_client(client_id)
                    
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    async def shutdown(self):
        """Shutdown the WebSocket manager"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Disconnect all clients
        for client_id in list(self.clients.keys()):
            await self.disconnect_client(client_id)
        
        logger.info("WorldStateWebSocketManager shutdown complete")


# Global WebSocket manager instance
websocket_manager = WorldStateWebSocketManager()


async def handle_websocket_connection(websocket: WebSocket):
    """Main WebSocket connection handler"""
    client_id = None
    try:
        # Initialize manager if needed
        if not websocket_manager.world_state_service:
            await websocket_manager.initialize()
        
        # Connect client
        client_id = await websocket_manager.connect_client(websocket)
        
        # Handle messages
        while True:
            message = await websocket.receive_text()
            await websocket_manager.handle_message(client_id, message)
            
    except WebSocketDisconnect:
        logger.info(f"Client {client_id} disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
    finally:
        if client_id:
            await websocket_manager.disconnect_client(client_id) 