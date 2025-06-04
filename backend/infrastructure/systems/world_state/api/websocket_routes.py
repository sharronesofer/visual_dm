"""
WebSocket endpoints for real-time World State events

Provides live event streaming for Unity frontend and other real-time consumers.
"""

from typing import Dict, Set, Optional, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from uuid import UUID
import json
import asyncio
import logging
from datetime import datetime

from backend.systems.world_state.services.services import WorldStateService, create_world_state_service
from backend.systems.world_state.world_types import StateCategory

router = APIRouter(prefix="/api/v1/world-state/ws", tags=["world-state-websocket"])
logger = logging.getLogger(__name__)

# Connection manager for WebSocket clients
class WorldStateConnectionManager:
    """Manages WebSocket connections for world state events"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Subscriptions by region
        self.region_subscribers: Dict[str, Set[str]] = {}
        
        # Subscriptions by faction
        self.faction_subscribers: Dict[str, Set[str]] = {}
        
        # Subscriptions by event category
        self.category_subscribers: Dict[StateCategory, Set[str]] = {}
        
        # Global subscribers (all events)
        self.global_subscribers: Set[str] = set()
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"WebSocket connected: {connection_id}")
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from all subscriptions
        for region_subs in self.region_subscribers.values():
            region_subs.discard(connection_id)
        
        for faction_subs in self.faction_subscribers.values():
            faction_subs.discard(connection_id)
        
        for category_subs in self.category_subscribers.values():
            category_subs.discard(connection_id)
        
        self.global_subscribers.discard(connection_id)
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    def subscribe_to_region(self, connection_id: str, region_id: str):
        """Subscribe connection to region events"""
        if region_id not in self.region_subscribers:
            self.region_subscribers[region_id] = set()
        self.region_subscribers[region_id].add(connection_id)
    
    def subscribe_to_faction(self, connection_id: str, faction_id: str):
        """Subscribe connection to faction events"""
        if faction_id not in self.faction_subscribers:
            self.faction_subscribers[faction_id] = set()
        self.faction_subscribers[faction_id].add(connection_id)
    
    def subscribe_to_category(self, connection_id: str, category: StateCategory):
        """Subscribe connection to category events"""
        if category not in self.category_subscribers:
            self.category_subscribers[category] = set()
        self.category_subscribers[category].add(connection_id)
    
    def subscribe_globally(self, connection_id: str):
        """Subscribe connection to all events"""
        self.global_subscribers.add(connection_id)
    
    async def send_to_connection(self, connection_id: str, message: dict):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send to connection {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def broadcast_event(self, event_data: dict):
        """Broadcast event to relevant subscribers"""
        event_type = event_data.get('type', '')
        region_id = event_data.get('region_id')
        faction_id = event_data.get('faction_id')
        category = event_data.get('category')
        
        # Collect all relevant subscribers
        subscribers = set()
        
        # Global subscribers get everything
        subscribers.update(self.global_subscribers)
        
        # Region subscribers
        if region_id and region_id in self.region_subscribers:
            subscribers.update(self.region_subscribers[region_id])
        
        # Faction subscribers
        if faction_id and faction_id in self.faction_subscribers:
            subscribers.update(self.faction_subscribers[faction_id])
        
        # Category subscribers
        if category:
            try:
                cat_enum = StateCategory(category)
                if cat_enum in self.category_subscribers:
                    subscribers.update(self.category_subscribers[cat_enum])
            except ValueError:
                pass
        
        # Send to all relevant subscribers
        for connection_id in subscribers:
            await self.send_to_connection(connection_id, event_data)
        
        logger.debug(f"Broadcasted {event_type} to {len(subscribers)} subscribers")

# Global connection manager
connection_manager = WorldStateConnectionManager()

async def get_world_state_service() -> WorldStateService:
    """Get world state service for event subscription"""
    return await create_world_state_service()

@router.websocket("/events")
async def websocket_events(
    websocket: WebSocket,
    connection_id: str = Query(..., description="Unique connection identifier"),
    regions: Optional[str] = Query(None, description="Comma-separated region IDs to subscribe to"),
    factions: Optional[str] = Query(None, description="Comma-separated faction IDs to subscribe to"),
    categories: Optional[str] = Query(None, description="Comma-separated categories to subscribe to"),
    global_events: bool = Query(False, description="Subscribe to all events")
):
    """
    WebSocket endpoint for real-time world state events
    
    Clients can subscribe to:
    - Specific regions (regions=region1,region2)
    - Specific factions (factions=faction-uuid-1,faction-uuid-2) 
    - Event categories (categories=POLITICAL,MILITARY)
    - All events (global_events=true)
    """
    await connection_manager.connect(websocket, connection_id)
    
    try:
        # Process subscriptions
        if global_events:
            connection_manager.subscribe_globally(connection_id)
        
        if regions:
            for region_id in regions.split(','):
                connection_manager.subscribe_to_region(connection_id, region_id.strip())
        
        if factions:
            for faction_id in factions.split(','):
                connection_manager.subscribe_to_faction(connection_id, faction_id.strip())
        
        if categories:
            for category_str in categories.split(','):
                try:
                    category = StateCategory(category_str.strip())
                    connection_manager.subscribe_to_category(connection_id, category)
                except ValueError:
                    logger.warning(f"Invalid category: {category_str}")
        
        # Send welcome message
        welcome_msg = {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "subscriptions": {
                "global": global_events,
                "regions": regions.split(',') if regions else [],
                "factions": factions.split(',') if factions else [],
                "categories": categories.split(',') if categories else []
            }
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for client message (e.g., ping, subscription updates)
                data = await websocket.receive_text()
                message = json.loads(data)
                
                if message.get('type') == 'ping':
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                elif message.get('type') == 'subscribe_region':
                    region_id = message.get('region_id')
                    if region_id:
                        connection_manager.subscribe_to_region(connection_id, region_id)
                        await websocket.send_text(json.dumps({
                            "type": "subscription_confirmed",
                            "subscription_type": "region",
                            "region_id": region_id
                        }))
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error(f"WebSocket error for {connection_id}: {e}")
                await websocket.send_text(json.dumps({
                    "type": "error", 
                    "message": str(e)
                }))
                break
    
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(connection_id)

@router.websocket("/region/{region_id}")
async def websocket_region_events(
    websocket: WebSocket,
    region_id: str,
    connection_id: str = Query(..., description="Unique connection identifier")
):
    """WebSocket endpoint for events specific to a region"""
    await connection_manager.connect(websocket, connection_id)
    connection_manager.subscribe_to_region(connection_id, region_id)
    
    try:
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "region_connection_established",
            "connection_id": connection_id,
            "region_id": region_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get('type') == 'ping':
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "region_id": region_id,
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.disconnect(connection_id)

# Event broadcasting functions (to be called by the world state service)
async def broadcast_state_change(
    key: str,
    old_value: any,
    new_value: any,
    region_id: Optional[str] = None,
    category: Optional[StateCategory] = None,
    user_id: Optional[str] = None
):
    """Broadcast state change event to WebSocket clients"""
    event_data = {
        "type": "state_changed",
        "key": key,
        "old_value": old_value,
        "new_value": new_value,
        "region_id": region_id,
        "category": category.value if category else None,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await connection_manager.broadcast_event(event_data)

async def broadcast_world_event(
    event_type: str,
    description: str,
    affected_regions: Optional[List[str]] = None,
    category: Optional[StateCategory] = None,
    metadata: Optional[dict] = None
):
    """Broadcast world event to WebSocket clients"""
    event_data = {
        "type": "world_event",
        "event_type": event_type,
        "description": description,
        "affected_regions": affected_regions or [],
        "category": category.value if category else None,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add faction_id if present in metadata
    if metadata and 'faction_id' in metadata:
        event_data['faction_id'] = metadata['faction_id']
    
    await connection_manager.broadcast_event(event_data)

async def broadcast_faction_event(
    faction_id: str,
    event_type: str,
    description: str,
    affected_regions: Optional[List[str]] = None,
    metadata: Optional[dict] = None
):
    """Broadcast faction-specific event to WebSocket clients"""
    event_data = {
        "type": "faction_event",
        "faction_id": faction_id,
        "event_type": event_type,
        "description": description,
        "affected_regions": affected_regions or [],
        "category": StateCategory.POLITICAL.value,
        "metadata": metadata or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await connection_manager.broadcast_event(event_data)

# Health check for WebSocket service
@router.get("/health")
async def websocket_health():
    """WebSocket service health check"""
    return {
        "status": "healthy",
        "active_connections": len(connection_manager.active_connections),
        "total_subscriptions": {
            "regions": sum(len(subs) for subs in connection_manager.region_subscribers.values()),
            "factions": sum(len(subs) for subs in connection_manager.faction_subscribers.values()),
            "categories": sum(len(subs) for subs in connection_manager.category_subscribers.values()),
            "global": len(connection_manager.global_subscribers)
        }
    } 