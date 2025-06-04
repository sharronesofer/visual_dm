"""
Religion WebSocket Routes

This module provides WebSocket routes for the religion system.
"""

import logging
import json
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse

# Import WebSocket manager from infrastructure
from backend.infrastructure.systems.religion.websocket.websocket_manager import religion_websocket_manager

# Set up logging
logger = logging.getLogger(__name__)

# Create WebSocket router
religion_websocket_router = APIRouter(prefix="/ws/religion", tags=["religion-websocket"])

@religion_websocket_router.websocket("/connect")
async def religion_websocket_endpoint(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None),
    client_type: Optional[str] = Query("player")
):
    """
    Main WebSocket endpoint for religion system real-time communication.
    
    Query Parameters:
        client_id: Unique identifier for the client
        client_type: Type of client (player, admin, observer)
    
    Supported Channels:
        - religion: Core religion creation, updates, and deletion events
        - membership: Religious membership and devotion changes
        - religious_events: Religious rituals, conversions, and conflicts
        - religious_narrative: Religious story events and narratives
        - religious_influence: Regional religious influence changes
    
    Message Format:
        {
            "type": "message_type",
            "payload": { ... },
            "channel": "channel_name" (for broadcasts),
            "timestamp": "2024-01-01T12:00:00Z",
            "message_id": "uuid"
        }
    
    Subscription Messages:
        - {"type": "subscribe", "payload": {"channel": "religion"}}
        - {"type": "unsubscribe", "payload": {"channel": "membership"}}
        - {"type": "ping", "payload": {}}
        - {"type": "request_status", "payload": {}}
        - {"type": "request_religion_data", "payload": {"religion_id": "uuid"}}
        - {"type": "request_membership_data", "payload": {"character_id": "uuid"}}
    """
    await religion_websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await religion_websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"Religion WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in religion WebSocket connection: {e}")
    finally:
        # Clean up connection
        await religion_websocket_manager.disconnect(websocket)

@religion_websocket_router.websocket("/region/{region_id}")
async def region_religion_websocket(
    websocket: WebSocket,
    region_id: int,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint specifically for religious updates in a region.
    
    Args:
        region_id: Region ID to monitor religious activities for
        client_id: Optional client identifier
    
    This endpoint automatically subscribes to relevant religious channels
    for the specified region and provides regional filtering.
    """
    await religion_websocket_manager.connect(websocket, client_id)
    
    try:
        # Auto-subscribe to relevant channels for this region
        await religion_websocket_manager.subscribe(websocket, "religion")
        await religion_websocket_manager.subscribe(websocket, "religious_events")
        await religion_websocket_manager.subscribe(websocket, "religious_influence")
        
        # Send initial region religious data
        await religion_websocket_manager._send_to_websocket(websocket, {
            "type": "region_religion_status",
            "payload": {
                "region_id": region_id,
                "message": f"Connected to religious updates for region {region_id}",
                "subscribed_channels": ["religion", "religious_events", "religious_influence"]
            }
        })
        
        while True:
            # Wait for message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await religion_websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"Region religion WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in region religion WebSocket connection: {e}")
    finally:
        # Clean up connection
        await religion_websocket_manager.disconnect(websocket)

@religion_websocket_router.websocket("/character/{character_id}")
async def character_religion_websocket(
    websocket: WebSocket,
    character_id: str,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for character-specific religious activity updates.
    
    Args:
        character_id: Character ID to monitor religious activities for
        client_id: Optional client identifier
    
    This endpoint automatically subscribes to membership and religious_events channels
    for the specified character.
    """
    await religion_websocket_manager.connect(websocket, client_id)
    
    try:
        # Auto-subscribe to character-relevant channels
        await religion_websocket_manager.subscribe(websocket, "membership")
        await religion_websocket_manager.subscribe(websocket, "religious_events")
        await religion_websocket_manager.subscribe(websocket, "religious_narrative")
        
        # Send initial character religious data
        try:
            await religion_websocket_manager._send_membership_data(websocket, character_id)
        except Exception as e:
            logger.warning(f"Could not send initial character religious data: {e}")
        
        # Send connection confirmation
        await religion_websocket_manager._send_to_websocket(websocket, {
            "type": "character_religion_status",
            "payload": {
                "character_id": character_id,
                "message": f"Connected to religious updates for character {character_id}",
                "subscribed_channels": ["membership", "religious_events", "religious_narrative"]
            }
        })
        
        while True:
            # Wait for message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await religion_websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"Character religion WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in character religion WebSocket connection: {e}")
    finally:
        # Clean up connection
        await religion_websocket_manager.disconnect(websocket)

@religion_websocket_router.websocket("/narrative")
async def religion_narrative_websocket(
    websocket: WebSocket,
    client_id: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time religious narrative and story events.
    
    Args:
        client_id: Optional client identifier
    
    This endpoint automatically subscribes to religious_narrative channel
    for story events, religious character development, and narrative triggers.
    """
    await religion_websocket_manager.connect(websocket, client_id)
    
    try:
        # Auto-subscribe to narrative channels
        await religion_websocket_manager.subscribe(websocket, "religious_narrative")
        await religion_websocket_manager.subscribe(websocket, "religious_events")
        
        # Send connection confirmation
        await religion_websocket_manager._send_to_websocket(websocket, {
            "type": "narrative_connection_status",
            "payload": {
                "message": "Connected to religious narrative updates",
                "subscribed_channels": ["religious_narrative", "religious_events"]
            }
        })
        
        while True:
            # Wait for message from client
            message = await websocket.receive_text()
            
            # Handle the message
            await religion_websocket_manager.handle_message(websocket, message)
            
    except WebSocketDisconnect:
        logger.info(f"Religion narrative WebSocket client disconnected: {client_id}")
    except Exception as e:
        logger.error(f"Error in religion narrative WebSocket connection: {e}")
    finally:
        # Clean up connection
        await religion_websocket_manager.disconnect(websocket)

# Helper functions for triggering WebSocket events from other parts of the system

async def trigger_religion_update(religion_data: dict):
    """Trigger a religion update WebSocket broadcast."""
    await religion_websocket_manager.broadcast_religion_update(religion_data)

async def trigger_membership_update(membership_data: dict):
    """Trigger a membership update WebSocket broadcast."""
    await religion_websocket_manager.broadcast_membership_update(membership_data)

async def trigger_religious_event(event_data: dict):
    """Trigger a religious event WebSocket broadcast."""
    await religion_websocket_manager.broadcast_religious_event(event_data)

async def trigger_religious_narrative(narrative_data: dict):
    """Trigger a religious narrative WebSocket broadcast."""
    await religion_websocket_manager.broadcast_religious_narrative(narrative_data)

async def trigger_religious_influence(influence_data: dict):
    """Trigger a religious influence WebSocket broadcast."""
    await religion_websocket_manager.broadcast_religious_influence(influence_data)

# Connection status endpoint
async def get_religion_websocket_status():
    """Get current religion WebSocket connection status."""
    return {
        "active_connections": len(religion_websocket_manager.connections),
        "total_subscriptions": sum(len(subs) for subs in religion_websocket_manager.subscriptions.values()),
        "channels": list(religion_websocket_manager.channel_subscribers.keys()),
        "channel_counts": {
            channel: len(subscribers) 
            for channel, subscribers in religion_websocket_manager.channel_subscribers.items()
        },
        "religion_service_available": religion_websocket_manager.religion_service is not None,
        "event_publisher_available": religion_websocket_manager.event_publisher is not None
    } 