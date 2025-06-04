"""
Core WebSocket Manager - Unified WebSocket management for backend systems.

This module provides a centralized WebSocket management interface that can be used
by various backend systems for real-time communication with Unity frontend.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

# Configure logger
logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Unified WebSocket manager for backend systems.
    
    Provides channel-based subscriptions, connection management, and
    broadcasting capabilities for real-time communication with Unity frontend.
    """
    
    def __init__(self):
        # Active WebSocket connections
        self.connections: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Channel subscriptions: channel -> set of websockets
        self.channel_subscribers: Dict[str, Set[WebSocket]] = {}
        
        # Client subscriptions: websocket -> set of channels
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        
        # Connection statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "channels_created": 0
        }
        
        logger.info("WebSocketManager initialized")
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None) -> str:
        """
        Accept a WebSocket connection and initialize client data.
        
        Args:
            websocket: WebSocket connection
            client_id: Optional client identifier
            
        Returns:
            str: The assigned client ID
        """
        await websocket.accept()
        
        # Generate client ID if not provided
        if not client_id:
            client_id = f"client_{uuid.uuid4().hex[:8]}"
        
        # Store connection info
        self.connections[websocket] = {
            "client_id": client_id,
            "connected_at": datetime.utcnow(),
            "channels": set(),
            "last_activity": datetime.utcnow()
        }
        
        # Initialize subscriptions
        self.subscriptions[websocket] = set()
        
        # Update stats
        self.stats["total_connections"] += 1
        self.stats["active_connections"] = len(self.connections)
        
        logger.info(f"WebSocket client connected: {client_id}")
        
        # Send welcome message
        await self._send_to_websocket(websocket, {
            "type": "connection_established",
            "payload": {
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
                "server_info": {
                    "version": "1.0",
                    "capabilities": ["channel_subscription", "real_time_updates"]
                }
            }
        })
        
        return client_id
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Handle WebSocket disconnection and cleanup.
        
        Args:
            websocket: WebSocket connection to disconnect
        """
        if websocket in self.connections:
            client_id = self.connections[websocket]["client_id"]
            
            # Remove from all channel subscriptions
            for channel in self.subscriptions.get(websocket, set()):
                if channel in self.channel_subscribers:
                    self.channel_subscribers[channel].discard(websocket)
            
            # Clean up connection data
            del self.connections[websocket]
            if websocket in self.subscriptions:
                del self.subscriptions[websocket]
            
            # Update stats
            self.stats["active_connections"] = len(self.connections)
            
            logger.info(f"WebSocket client disconnected: {client_id}")
    
    async def subscribe_to_channel(self, websocket: WebSocket, channel: str) -> bool:
        """
        Subscribe a WebSocket to a channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name to subscribe to
            
        Returns:
            bool: True if subscription was successful
        """
        if websocket not in self.connections:
            logger.warning("Attempted to subscribe non-connected WebSocket")
            return False
        
        # Create channel if it doesn't exist
        if channel not in self.channel_subscribers:
            self.channel_subscribers[channel] = set()
            self.stats["channels_created"] += 1
            logger.info(f"Created new WebSocket channel: {channel}")
        
        # Add to channel subscribers
        self.channel_subscribers[channel].add(websocket)
        
        # Add to client subscriptions
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()
        self.subscriptions[websocket].add(channel)
        
        # Update connection info
        if websocket in self.connections:
            self.connections[websocket]["channels"].add(channel)
            self.connections[websocket]["last_activity"] = datetime.utcnow()
        
        client_id = self.connections.get(websocket, {}).get("client_id", "unknown")
        logger.info(f"WebSocket client {client_id} subscribed to channel: {channel}")
        
        # Send subscription confirmation
        await self._send_to_websocket(websocket, {
            "type": "subscription_confirmed",
            "payload": {
                "channel": channel,
                "subscribed_channels": list(self.subscriptions[websocket])
            }
        })
        
        return True
    
    async def unsubscribe_from_channel(self, websocket: WebSocket, channel: str) -> bool:
        """
        Unsubscribe a WebSocket from a channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name to unsubscribe from
            
        Returns:
            bool: True if unsubscription was successful
        """
        if websocket not in self.connections:
            logger.warning("Attempted to unsubscribe non-connected WebSocket")
            return False
        
        # Remove from channel subscribers
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(websocket)
        
        # Remove from client subscriptions
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(channel)
        
        # Update connection info
        if websocket in self.connections:
            self.connections[websocket]["channels"].discard(channel)
            self.connections[websocket]["last_activity"] = datetime.utcnow()
        
        client_id = self.connections.get(websocket, {}).get("client_id", "unknown")
        logger.info(f"WebSocket client {client_id} unsubscribed from channel: {channel}")
        
        # Send unsubscription confirmation
        await self._send_to_websocket(websocket, {
            "type": "unsubscription_confirmed",
            "payload": {
                "channel": channel,
                "subscribed_channels": list(self.subscriptions.get(websocket, set()))
            }
        })
        
        return True
    
    async def broadcast_to_channel(self, channel: str, message: Dict[str, Any]) -> int:
        """
        Broadcast a message to all subscribers of a channel.
        
        Args:
            channel: Channel name
            message: Message to broadcast
            
        Returns:
            int: Number of clients that received the message
        """
        if channel not in self.channel_subscribers:
            logger.warning(f"Attempted to broadcast to unknown channel: {channel}")
            return 0
        
        # Add channel and metadata to message
        message_with_metadata = {
            **message,
            "channel": channel,
            "broadcast_timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast to all subscribers
        subscribers = self.channel_subscribers[channel].copy()
        successful_sends = 0
        disconnected_websockets = []
        
        for websocket in subscribers:
            try:
                await self._send_to_websocket(websocket, message_with_metadata)
                successful_sends += 1
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected_websockets.append(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected_websockets:
            await self.disconnect(websocket)
        
        # Update stats
        self.stats["messages_sent"] += successful_sends
        
        logger.debug(f"Broadcasted message to {successful_sends} clients on channel: {channel}")
        return successful_sends
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> bool:
        """
        Send a message to a specific client.
        
        Args:
            client_id: Client identifier
            message: Message to send
            
        Returns:
            bool: True if message was sent successfully
        """
        # Find the WebSocket for this client
        target_websocket = None
        for websocket, connection_info in self.connections.items():
            if connection_info["client_id"] == client_id:
                target_websocket = websocket
                break
        
        if not target_websocket:
            logger.warning(f"Client not found: {client_id}")
            return False
        
        try:
            await self._send_to_websocket(target_websocket, message)
            self.stats["messages_sent"] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to send message to client {client_id}: {e}")
            await self.disconnect(target_websocket)
            return False
    
    async def handle_message(self, websocket: WebSocket, message: str) -> None:
        """
        Handle incoming WebSocket message.
        
        Args:
            websocket: WebSocket connection
            message: Raw message string
        """
        if websocket not in self.connections:
            logger.warning("Received message from non-connected WebSocket")
            return
        
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("payload", {})
            
            # Update last activity
            self.connections[websocket]["last_activity"] = datetime.utcnow()
            self.stats["messages_received"] += 1
            
            # Handle standard message types
            if message_type == "subscribe":
                channel = payload.get("channel")
                if channel:
                    await self.subscribe_to_channel(websocket, channel)
                else:
                    await self._send_error(websocket, "Channel name required for subscription")
            
            elif message_type == "unsubscribe":
                channel = payload.get("channel")
                if channel:
                    await self.unsubscribe_from_channel(websocket, channel)
                else:
                    await self._send_error(websocket, "Channel name required for unsubscription")
            
            elif message_type == "ping":
                await self._send_to_websocket(websocket, {
                    "type": "pong",
                    "payload": {"timestamp": datetime.utcnow().isoformat()}
                })
            
            elif message_type == "get_status":
                await self._send_status(websocket)
            
            else:
                logger.debug(f"Unhandled message type: {message_type}")
                
        except json.JSONDecodeError as e:
            await self._send_error(websocket, f"Invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self._send_error(websocket, "Internal server error")
    
    async def _send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """
        Send a message to a specific WebSocket.
        
        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        try:
            # Add message_id and timestamp if not present
            if "message_id" not in message:
                message["message_id"] = str(uuid.uuid4())
            
            if "timestamp" not in message:
                message["timestamp"] = datetime.utcnow().isoformat()
            
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            raise
    
    async def _send_error(self, websocket: WebSocket, error_message: str) -> None:
        """Send an error message to a WebSocket."""
        await self._send_to_websocket(websocket, {
            "type": "error",
            "payload": {"message": error_message}
        })
    
    async def _send_status(self, websocket: WebSocket) -> None:
        """Send system status to a WebSocket."""
        try:
            client_info = self.connections.get(websocket, {})
            status = {
                "client_id": client_info.get("client_id", "unknown"),
                "connected_at": client_info.get("connected_at", datetime.utcnow()).isoformat(),
                "subscribed_channels": list(self.subscriptions.get(websocket, set())),
                "system_stats": self.stats.copy(),
                "available_channels": list(self.channel_subscribers.keys())
            }
            
            await self._send_to_websocket(websocket, {
                "type": "status_response",
                "payload": status
            })
            
        except Exception as e:
            logger.error(f"Error sending status: {e}")
            await self._send_error(websocket, "Failed to get status")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            **self.stats,
            "channels": {
                channel: len(subscribers) 
                for channel, subscribers in self.channel_subscribers.items()
            },
            "active_connections": len(self.connections)
        }
    
    def get_channel_info(self, channel: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific channel."""
        if channel not in self.channel_subscribers:
            return None
        
        subscribers = self.channel_subscribers[channel]
        return {
            "channel": channel,
            "subscriber_count": len(subscribers),
            "subscribers": [
                self.connections[ws]["client_id"] 
                for ws in subscribers 
                if ws in self.connections
            ]
        }

# Global WebSocket manager instance
_websocket_manager: Optional[WebSocketManager] = None

def get_websocket_manager() -> WebSocketManager:
    """Get or create the global WebSocket manager instance."""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = WebSocketManager()
    return _websocket_manager 