"""
Religion WebSocket Manager - Real-time WebSocket communication for religion system.

This module provides WebSocket management and real-time event broadcasting
for religion system updates, integrated with the religion event system.
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect

# Import religion events from infrastructure
from backend.infrastructure.systems.religion.events.religion_events import (
    ReligionEventType, MembershipEventType, DevotionEventType,
    NarrativeEventType, InfluenceEventType
)

# Set up logging
logger = logging.getLogger(__name__)

class ReligionWebSocketManager:
    """
    WebSocket manager for religion system real-time communication.
    
    Manages WebSocket connections, channel subscriptions, and automatic
    event broadcasting integrated with the religion event system.
    """
    
    def __init__(self):
        # Active WebSocket connections
        self.connections: Dict[WebSocket, Dict[str, Any]] = {}
        
        # Channel subscriptions: channel -> set of websockets
        self.channel_subscribers: Dict[str, Set[WebSocket]] = {
            "religion": set(),           # Core religion events
            "membership": set(),         # Membership and devotion changes
            "religious_events": set(),   # Rituals, conversions, conflicts
            "religious_narrative": set(), # Story events and narratives
            "religious_influence": set() # Regional influence changes
        }
        
        # Client subscriptions: websocket -> set of channels
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        
        # Religion service reference (set when available)
        self.religion_service = None
        
        # Event publisher reference (set when available)
        self.event_publisher = None
        
        # Initialize event handlers
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Set up automatic event broadcasting from religion event system."""
        
        # Core religion events -> religion channel
        self._religion_event_handlers = {
            ReligionEventType.CREATED: self._handle_religion_event,
            ReligionEventType.UPDATED: self._handle_religion_event,
            ReligionEventType.DELETED: self._handle_religion_event,
        }
        
        # Membership events -> membership channel
        self._membership_event_handlers = {
            MembershipEventType.CREATED: self._handle_membership_event,
            MembershipEventType.UPDATED: self._handle_membership_event,
            MembershipEventType.DELETED: self._handle_membership_event,
            MembershipEventType.CONVERSION: self._handle_membership_event,
        }
        
        # Devotion events -> religious_events channel
        self._devotion_event_handlers = {
            DevotionEventType.DEVOTION_INCREASED: self._handle_devotion_event,
            DevotionEventType.DEVOTION_DECREASED: self._handle_devotion_event,
            DevotionEventType.RITUAL_PERFORMED: self._handle_devotion_event,
        }
        
        # Narrative events -> religious_narrative channel
        self._narrative_event_handlers = {
            NarrativeEventType.RELIGIOUS_NARRATIVE: self._handle_narrative_event,
            NarrativeEventType.SCHISM: self._handle_narrative_event,
        }
        
        # Influence events -> religious_influence channel
        self._influence_event_handlers = {
            InfluenceEventType.INFLUENCE_SPREAD: self._handle_influence_event,
            InfluenceEventType.CONFLICT: self._handle_influence_event,
        }
    
    async def _handle_religion_event(self, event_data: Dict[str, Any]):
        """Handle religion events and broadcast to religion channel."""
        await self._broadcast_to_channel("religion", {
            "type": "religion_event",
            "event_type": event_data.get("event_type"),
            "payload": event_data.get("data", {}),
            "timestamp": event_data.get("timestamp"),
            "message_id": event_data.get("message_id")
        })
    
    async def _handle_membership_event(self, event_data: Dict[str, Any]):
        """Handle membership events and broadcast to membership channel."""
        await self._broadcast_to_channel("membership", {
            "type": "membership_event",
            "event_type": event_data.get("event_type"),
            "payload": event_data.get("data", {}),
            "timestamp": event_data.get("timestamp"),
            "message_id": event_data.get("message_id")
        })
    
    async def _handle_devotion_event(self, event_data: Dict[str, Any]):
        """Handle devotion events and broadcast to religious_events channel."""
        await self._broadcast_to_channel("religious_events", {
            "type": "devotion_event",
            "event_type": event_data.get("event_type"),
            "payload": event_data.get("data", {}),
            "timestamp": event_data.get("timestamp"),
            "message_id": event_data.get("message_id")
        })
    
    async def _handle_narrative_event(self, event_data: Dict[str, Any]):
        """Handle narrative events and broadcast to religious_narrative channel."""
        await self._broadcast_to_channel("religious_narrative", {
            "type": "narrative_event",
            "event_type": event_data.get("event_type"),
            "payload": event_data.get("data", {}),
            "timestamp": event_data.get("timestamp"),
            "message_id": event_data.get("message_id")
        })
    
    async def _handle_influence_event(self, event_data: Dict[str, Any]):
        """Handle influence events and broadcast to religious_influence channel."""
        await self._broadcast_to_channel("religious_influence", {
            "type": "influence_event",
            "event_type": event_data.get("event_type"),
            "payload": event_data.get("data", {}),
            "timestamp": event_data.get("timestamp"),
            "message_id": event_data.get("message_id")
        })
    
    async def connect(self, websocket: WebSocket, client_id: Optional[str] = None):
        """
        Accept a WebSocket connection and initialize client data.
        
        Args:
            websocket: WebSocket connection
            client_id: Optional client identifier
        """
        await websocket.accept()
        
        # Store connection info
        self.connections[websocket] = {
            "client_id": client_id or f"client_{id(websocket)}",
            "connected_at": asyncio.get_event_loop().time(),
            "channels": set()
        }
        
        # Initialize subscriptions
        self.subscriptions[websocket] = set()
        
        logger.info(f"Religion WebSocket client connected: {self.connections[websocket]['client_id']}")
        
        # Send welcome message
        await self._send_to_websocket(websocket, {
            "type": "connection_established",
            "payload": {
                "client_id": self.connections[websocket]["client_id"],
                "available_channels": list(self.channel_subscribers.keys()),
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    async def disconnect(self, websocket: WebSocket):
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
            del self.subscriptions[websocket]
            
            logger.info(f"Religion WebSocket client disconnected: {client_id}")
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """
        Subscribe a WebSocket to a channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name to subscribe to
        """
        if channel not in self.channel_subscribers:
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {
                    "message": f"Invalid channel: {channel}",
                    "available_channels": list(self.channel_subscribers.keys())
                }
            })
            return
        
        # Add to channel subscribers
        self.channel_subscribers[channel].add(websocket)
        
        # Add to client subscriptions
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()
        self.subscriptions[websocket].add(channel)
        
        # Update connection info
        if websocket in self.connections:
            self.connections[websocket]["channels"].add(channel)
        
        client_id = self.connections.get(websocket, {}).get("client_id", "unknown")
        logger.info(f"Religion WebSocket client {client_id} subscribed to channel: {channel}")
        
        # Send subscription confirmation
        await self._send_to_websocket(websocket, {
            "type": "subscription_confirmed",
            "payload": {
                "channel": channel,
                "subscribed_channels": list(self.subscriptions[websocket])
            }
        })
    
    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """
        Unsubscribe a WebSocket from a channel.
        
        Args:
            websocket: WebSocket connection
            channel: Channel name to unsubscribe from
        """
        # Remove from channel subscribers
        if channel in self.channel_subscribers:
            self.channel_subscribers[channel].discard(websocket)
        
        # Remove from client subscriptions
        if websocket in self.subscriptions:
            self.subscriptions[websocket].discard(channel)
        
        # Update connection info
        if websocket in self.connections:
            self.connections[websocket]["channels"].discard(channel)
        
        client_id = self.connections.get(websocket, {}).get("client_id", "unknown")
        logger.info(f"Religion WebSocket client {client_id} unsubscribed from channel: {channel}")
        
        # Send unsubscription confirmation
        await self._send_to_websocket(websocket, {
            "type": "unsubscription_confirmed",
            "payload": {
                "channel": channel,
                "subscribed_channels": list(self.subscriptions.get(websocket, set()))
            }
        })
    
    async def handle_message(self, websocket: WebSocket, message: str):
        """
        Handle incoming WebSocket message.
        
        Args:
            websocket: WebSocket connection
            message: Raw message string
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")
            payload = data.get("payload", {})
            
            if message_type == "subscribe":
                channel = payload.get("channel")
                if channel:
                    await self.subscribe(websocket, channel)
                else:
                    await self._send_to_websocket(websocket, {
                        "type": "error",
                        "payload": {"message": "Channel name required for subscription"}
                    })
            
            elif message_type == "unsubscribe":
                channel = payload.get("channel")
                if channel:
                    await self.unsubscribe(websocket, channel)
                else:
                    await self._send_to_websocket(websocket, {
                        "type": "error",
                        "payload": {"message": "Channel name required for unsubscription"}
                    })
            
            elif message_type == "ping":
                await self._send_to_websocket(websocket, {
                    "type": "pong",
                    "payload": {"timestamp": asyncio.get_event_loop().time()}
                })
            
            elif message_type == "request_status":
                await self._send_religion_status(websocket)
            
            elif message_type == "request_religion_data":
                religion_id = payload.get("religion_id")
                await self._send_religion_data(websocket, religion_id)
            
            elif message_type == "request_membership_data":
                character_id = payload.get("character_id")
                await self._send_membership_data(websocket, character_id)
            
            else:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "payload": {"message": f"Unknown message type: {message_type}"}
                })
                
        except json.JSONDecodeError as e:
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {"message": f"Invalid JSON: {str(e)}"}
            })
        except Exception as e:
            logger.error(f"Error handling religion WebSocket message: {e}")
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {"message": "Internal server error"}
            })
    
    # Broadcasting methods
    async def broadcast_religion_update(self, religion_data: Dict[str, Any]):
        """Broadcast a religion update to all religion channel subscribers."""
        await self._broadcast_to_channel("religion", {
            "type": "religion_update",
            "payload": religion_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_membership_update(self, membership_data: Dict[str, Any]):
        """Broadcast a membership update to all membership channel subscribers."""
        await self._broadcast_to_channel("membership", {
            "type": "membership_update",
            "payload": membership_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_religious_event(self, event_data: Dict[str, Any]):
        """Broadcast a religious event to all religious_events channel subscribers."""
        await self._broadcast_to_channel("religious_events", {
            "type": "religious_event",
            "payload": event_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_religious_narrative(self, narrative_data: Dict[str, Any]):
        """Broadcast a religious narrative to all religious_narrative channel subscribers."""
        await self._broadcast_to_channel("religious_narrative", {
            "type": "religious_narrative",
            "payload": narrative_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def broadcast_religious_influence(self, influence_data: Dict[str, Any]):
        """Broadcast a religious influence update to all religious_influence channel subscribers."""
        await self._broadcast_to_channel("religious_influence", {
            "type": "religious_influence",
            "payload": influence_data,
            "timestamp": asyncio.get_event_loop().time()
        })
    
    async def _broadcast_to_channel(self, channel: str, message: Dict[str, Any]):
        """
        Broadcast a message to all subscribers of a channel.
        
        Args:
            channel: Channel name
            message: Message to broadcast
        """
        if channel not in self.channel_subscribers:
            logger.warning(f"Attempt to broadcast to unknown channel: {channel}")
            return
        
        # Add channel to message
        message["channel"] = channel
        
        # Broadcast to all subscribers
        subscribers = self.channel_subscribers[channel].copy()
        disconnected_websockets = []
        
        for websocket in subscribers:
            try:
                await self._send_to_websocket(websocket, message)
            except Exception as e:
                logger.warning(f"Failed to send message to WebSocket: {e}")
                disconnected_websockets.append(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected_websockets:
            await self.disconnect(websocket)
    
    async def _send_to_websocket(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket.
        
        Args:
            websocket: WebSocket connection
            message: Message to send
        """
        try:
            # Add message_id if not present
            if "message_id" not in message:
                import uuid
                message["message_id"] = str(uuid.uuid4())
            
            # Add timestamp if not present
            if "timestamp" not in message:
                from datetime import datetime
                message["timestamp"] = datetime.utcnow().isoformat()
            
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
            raise
    
    async def _send_religion_status(self, websocket: WebSocket):
        """Send religion system status to a WebSocket."""
        try:
            status = {
                "active_connections": len(self.connections),
                "channel_subscriptions": {
                    channel: len(subscribers) 
                    for channel, subscribers in self.channel_subscribers.items()
                },
                "available_channels": list(self.channel_subscribers.keys()),
                "religion_service_available": self.religion_service is not None,
                "event_publisher_available": self.event_publisher is not None
            }
            
            await self._send_to_websocket(websocket, {
                "type": "religion_status",
                "payload": status
            })
            
        except Exception as e:
            logger.error(f"Error sending religion status: {e}")
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {"message": "Failed to get religion status"}
            })
    
    async def _send_religion_data(self, websocket: WebSocket, religion_id: Optional[str]):
        """Send religion data to a WebSocket."""
        try:
            if not self.religion_service:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "payload": {"message": "Religion service not available"}
                })
                return
            
            if religion_id:
                # Send specific religion data
                religion = await self.religion_service.get_religion(religion_id)
                if religion:
                    await self._send_to_websocket(websocket, {
                        "type": "religion_data",
                        "payload": {
                            "religion_id": religion_id,
                            "religion": religion.dict() if hasattr(religion, 'dict') else religion
                        }
                    })
                else:
                    await self._send_to_websocket(websocket, {
                        "type": "error",
                        "payload": {"message": f"Religion {religion_id} not found"}
                    })
            else:
                # Send all religions data
                religions = await self.religion_service.list_religions()
                await self._send_to_websocket(websocket, {
                    "type": "religions_list",
                    "payload": {
                        "religions": [r.dict() if hasattr(r, 'dict') else r for r in religions]
                    }
                })
                
        except Exception as e:
            logger.error(f"Error sending religion data: {e}")
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {"message": "Failed to get religion data"}
            })
    
    async def _send_membership_data(self, websocket: WebSocket, character_id: Optional[str]):
        """Send membership data to a WebSocket."""
        try:
            if not self.religion_service:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "payload": {"message": "Religion service not available"}
                })
                return
            
            if character_id:
                # Send character's religious memberships
                # This would require a method in religion service to get character memberships
                await self._send_to_websocket(websocket, {
                    "type": "membership_data",
                    "payload": {
                        "character_id": character_id,
                        "memberships": []  # Placeholder - would get actual data from service
                    }
                })
            else:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "payload": {"message": "Character ID required for membership data"}
                })
                
        except Exception as e:
            logger.error(f"Error sending membership data: {e}")
            await self._send_to_websocket(websocket, {
                "type": "error",
                "payload": {"message": "Failed to get membership data"}
            })

# Global religion WebSocket manager instance
religion_websocket_manager = ReligionWebSocketManager()

# Helper functions for triggering WebSocket events from other parts of the system
async def notify_religion_updated(religion_data: Dict[str, Any]):
    """Notify WebSocket clients of religion update."""
    await religion_websocket_manager.broadcast_religion_update(religion_data)

async def notify_membership_updated(membership_data: Dict[str, Any]):
    """Notify WebSocket clients of membership update."""
    await religion_websocket_manager.broadcast_membership_update(membership_data)

async def notify_religious_event(event_data: Dict[str, Any]):
    """Notify WebSocket clients of religious event."""
    await religion_websocket_manager.broadcast_religious_event(event_data)

async def notify_religious_narrative(narrative_data: Dict[str, Any]):
    """Notify WebSocket clients of religious narrative."""
    await religion_websocket_manager.broadcast_religious_narrative(narrative_data)

async def notify_religious_influence(influence_data: Dict[str, Any]):
    """Notify WebSocket clients of religious influence update."""
    await religion_websocket_manager.broadcast_religious_influence(influence_data) 