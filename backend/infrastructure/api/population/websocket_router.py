"""
Population System WebSocket Router

Provides real-time communication between the population system and Unity clients.
Includes disease outbreak notifications, population state changes, and quest opportunities.
"""

import json
import asyncio
import logging
from typing import Dict, List, Set, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.websockets import WebSocketState

from backend.systems.population.utils.disease_models import (
    DISEASE_ENGINE,
    DiseaseType,
    DiseaseStage
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["population-websockets"])


class PopulationWebSocketManager:
    """Manages WebSocket connections for population system real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.population_subscribers: Dict[str, Set[str]] = {}  # population_id -> set of connection_ids
        self.global_subscribers: Set[str] = set()  # connections interested in all population events
        
    async def connect(self, websocket: WebSocket, connection_id: str) -> bool:
        """Accept a WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections[connection_id] = websocket
            logger.info(f"WebSocket connection established: {connection_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection {connection_id}: {str(e)}")
            return False
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
        # Remove from all subscriptions
        self.global_subscribers.discard(connection_id)
        for subscribers in self.population_subscribers.values():
            subscribers.discard(connection_id)
            
        logger.info(f"WebSocket connection disconnected: {connection_id}")
    
    def subscribe_to_population(self, connection_id: str, population_id: str):
        """Subscribe a connection to updates for a specific population"""
        if population_id not in self.population_subscribers:
            self.population_subscribers[population_id] = set()
        self.population_subscribers[population_id].add(connection_id)
        logger.info(f"Connection {connection_id} subscribed to population {population_id}")
    
    def subscribe_to_global(self, connection_id: str):
        """Subscribe a connection to all population system events"""
        self.global_subscribers.add(connection_id)
        logger.info(f"Connection {connection_id} subscribed to global population events")
    
    def unsubscribe_from_population(self, connection_id: str, population_id: str):
        """Unsubscribe a connection from a specific population"""
        if population_id in self.population_subscribers:
            self.population_subscribers[population_id].discard(connection_id)
            if not self.population_subscribers[population_id]:
                del self.population_subscribers[population_id]
        logger.info(f"Connection {connection_id} unsubscribed from population {population_id}")
    
    def unsubscribe_from_global(self, connection_id: str):
        """Unsubscribe a connection from global events"""
        self.global_subscribers.discard(connection_id)
        logger.info(f"Connection {connection_id} unsubscribed from global events")
    
    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific connection"""
        if connection_id not in self.active_connections:
            return False
            
        websocket = self.active_connections[connection_id]
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(json.dumps(message))
                return True
        except Exception as e:
            logger.error(f"Error sending message to connection {connection_id}: {str(e)}")
            self.disconnect(connection_id)
        return False
    
    async def broadcast_to_population(self, population_id: str, message: Dict[str, Any]):
        """Broadcast a message to all subscribers of a specific population"""
        if population_id in self.population_subscribers:
            subscribers = self.population_subscribers[population_id].copy()
            tasks = []
            for connection_id in subscribers:
                tasks.append(self.send_to_connection(connection_id, message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_global(self, message: Dict[str, Any]):
        """Broadcast a message to all global subscribers"""
        if self.global_subscribers:
            tasks = []
            for connection_id in self.global_subscribers.copy():
                tasks.append(self.send_to_connection(connection_id, message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_disease_outbreak(self, population_id: str, disease_type: DiseaseType, outbreak_data: Dict[str, Any]):
        """Broadcast disease outbreak notification"""
        message = {
            "type": "disease_outbreak",
            "timestamp": datetime.utcnow().isoformat(),
            "population_id": population_id,
            "disease_type": disease_type.value,
            "outbreak_data": outbreak_data,
            "priority": "high"
        }
        
        # Send to population subscribers and global subscribers
        await asyncio.gather(
            self.broadcast_to_population(population_id, message),
            self.broadcast_global(message),
            return_exceptions=True
        )
    
    async def broadcast_disease_stage_change(self, population_id: str, disease_type: DiseaseType, old_stage: DiseaseStage, new_stage: DiseaseStage):
        """Broadcast disease stage progression"""
        message = {
            "type": "disease_stage_change",
            "timestamp": datetime.utcnow().isoformat(),
            "population_id": population_id,
            "disease_type": disease_type.value,
            "old_stage": old_stage.value,
            "new_stage": new_stage.value,
            "priority": "medium"
        }
        
        await asyncio.gather(
            self.broadcast_to_population(population_id, message),
            self.broadcast_global(message),
            return_exceptions=True
        )
    
    async def broadcast_quest_opportunities(self, population_id: str, quest_opportunities: List[Dict[str, Any]]):
        """Broadcast new quest opportunities"""
        if not quest_opportunities:
            return
            
        message = {
            "type": "quest_opportunities",
            "timestamp": datetime.utcnow().isoformat(),
            "population_id": population_id,
            "quest_count": len(quest_opportunities),
            "quests": quest_opportunities,
            "priority": "medium"
        }
        
        await asyncio.gather(
            self.broadcast_to_population(population_id, message),
            self.broadcast_global(message),
            return_exceptions=True
        )
    
    async def broadcast_population_change(self, population_id: str, old_count: int, new_count: int, change_reason: str):
        """Broadcast population count changes"""
        change_amount = new_count - old_count
        change_percentage = (change_amount / old_count * 100) if old_count > 0 else 0
        
        message = {
            "type": "population_change",
            "timestamp": datetime.utcnow().isoformat(),
            "population_id": population_id,
            "old_count": old_count,
            "new_count": new_count,
            "change_amount": change_amount,
            "change_percentage": round(change_percentage, 2),
            "change_reason": change_reason,
            "priority": "low" if abs(change_percentage) < 5 else "medium"
        }
        
        await asyncio.gather(
            self.broadcast_to_population(population_id, message),
            self.broadcast_global(message),
            return_exceptions=True
        )

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections"""
        return {
            "total_connections": len(self.active_connections),
            "global_subscribers": len(self.global_subscribers),
            "population_subscriptions": {
                pop_id: len(subscribers) 
                for pop_id, subscribers in self.population_subscribers.items()
            },
            "active_connection_ids": list(self.active_connections.keys())
        }


# Global WebSocket manager instance
ws_manager = PopulationWebSocketManager()


@router.websocket("/population")
async def population_websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for population system real-time updates
    
    Message types received from client:
    - {"action": "subscribe_population", "population_id": "id"}
    - {"action": "subscribe_global"}
    - {"action": "unsubscribe_population", "population_id": "id"}
    - {"action": "unsubscribe_global"}
    - {"action": "ping"}
    
    Message types sent to client:
    - disease_outbreak: New disease outbreak started
    - disease_stage_change: Disease progression stage changed
    - quest_opportunities: New quests available from population events
    - population_change: Population count changed
    - pong: Response to ping
    - error: Error message
    """
    connection_id = f"conn_{datetime.utcnow().timestamp()}"
    
    try:
        # Accept connection
        if not await ws_manager.connect(websocket, connection_id):
            return
        
        # Send initial connection confirmation
        await ws_manager.send_to_connection(connection_id, {
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat(),
            "available_actions": [
                "subscribe_population",
                "subscribe_global", 
                "unsubscribe_population",
                "unsubscribe_global",
                "ping"
            ]
        })
        
        # Listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                action = message.get("action")
                
                if action == "subscribe_population":
                    population_id = message.get("population_id")
                    if population_id:
                        ws_manager.subscribe_to_population(connection_id, population_id)
                        await ws_manager.send_to_connection(connection_id, {
                            "type": "subscription_confirmed",
                            "action": "subscribe_population",
                            "population_id": population_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        await ws_manager.send_to_connection(connection_id, {
                            "type": "error",
                            "message": "population_id required for subscribe_population action"
                        })
                
                elif action == "subscribe_global":
                    ws_manager.subscribe_to_global(connection_id)
                    await ws_manager.send_to_connection(connection_id, {
                        "type": "subscription_confirmed",
                        "action": "subscribe_global",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif action == "unsubscribe_population":
                    population_id = message.get("population_id")
                    if population_id:
                        ws_manager.unsubscribe_from_population(connection_id, population_id)
                        await ws_manager.send_to_connection(connection_id, {
                            "type": "unsubscription_confirmed",
                            "action": "unsubscribe_population",
                            "population_id": population_id,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                elif action == "unsubscribe_global":
                    ws_manager.unsubscribe_from_global(connection_id)
                    await ws_manager.send_to_connection(connection_id, {
                        "type": "unsubscription_confirmed",
                        "action": "unsubscribe_global",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif action == "ping":
                    await ws_manager.send_to_connection(connection_id, {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                else:
                    await ws_manager.send_to_connection(connection_id, {
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })
                    
            except json.JSONDecodeError:
                await ws_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                await ws_manager.send_to_connection(connection_id, {
                    "type": "error",
                    "message": "Internal error processing message"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        ws_manager.disconnect(connection_id)


@router.get("/connections/stats")
async def get_websocket_stats():
    """
    Get statistics about current WebSocket connections
    
    Returns:
        Connection statistics including subscriber counts
    """
    try:
        stats = ws_manager.get_connection_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting WebSocket stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get WebSocket stats: {str(e)}")


@router.post("/broadcast/test")
async def test_broadcast(
    message_type: str,
    population_id: Optional[str] = None,
    test_message: str = "Test broadcast message"
):
    """
    Test endpoint for broadcasting messages to WebSocket clients
    
    Args:
        message_type: Type of test message to broadcast
        population_id: Population ID for targeted broadcast (optional)
        test_message: Custom test message content
        
    Returns:
        Broadcast result
    """
    try:
        message = {
            "type": "test_message",
            "message_type": message_type,
            "content": test_message,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "low"
        }
        
        if population_id:
            await ws_manager.broadcast_to_population(population_id, message)
            return {
                "success": True,
                "message": f"Test message broadcasted to population {population_id}",
                "recipients": len(ws_manager.population_subscribers.get(population_id, set()))
            }
        else:
            await ws_manager.broadcast_global(message)
            return {
                "success": True,
                "message": "Test message broadcasted globally",
                "recipients": len(ws_manager.global_subscribers)
            }
            
    except Exception as e:
        logger.error(f"Error testing broadcast: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to test broadcast: {str(e)}")


# Health check for WebSocket system
@router.get("/health")
async def websocket_system_health():
    """
    Health check for the WebSocket system
    
    Returns:
        WebSocket system health status
    """
    try:
        stats = ws_manager.get_connection_stats()
        return {
            "status": "healthy",
            "system": "population_websockets",
            "active_connections": stats["total_connections"],
            "global_subscribers": stats["global_subscribers"],
            "population_subscriptions": len(stats["population_subscriptions"]),
            "capabilities": [
                "real_time_disease_outbreak_notifications",
                "population_change_broadcasts",
                "quest_opportunity_updates",
                "targeted_population_subscriptions",
                "global_event_subscriptions",
                "connection_management"
            ],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"WebSocket health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"WebSocket system unhealthy: {str(e)}")


# Export the manager for use by other parts of the system
__all__ = ["router", "ws_manager"] 