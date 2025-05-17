from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException
import asyncio
import json
from typing import Dict, List, Optional, Any, Set
import logging
from datetime import datetime

# Setup logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Keep track of active combat sessions and their connected clients
combat_connections: Dict[str, Set[WebSocket]] = {}


class CombatWebSocketManager:
    """Manager for combat WebSocket connections"""
    
    @staticmethod
    async def connect(websocket: WebSocket, combat_id: str):
        """Add a client to a combat session"""
        await websocket.accept()
        
        if combat_id not in combat_connections:
            combat_connections[combat_id] = set()
        
        combat_connections[combat_id].add(websocket)
        logger.info(f"Client connected to combat {combat_id}")
        
        # Send initial message
        await websocket.send_json({
            "type": "connected",
            "combat_id": combat_id,
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    async def disconnect(websocket: WebSocket, combat_id: str):
        """Remove a client from a combat session"""
        if combat_id in combat_connections:
            try:
                combat_connections[combat_id].remove(websocket)
                logger.info(f"Client disconnected from combat {combat_id}")
                
                # Clean up empty sessions
                if len(combat_connections[combat_id]) == 0:
                    del combat_connections[combat_id]
                    logger.info(f"Removed empty combat session {combat_id}")
            except KeyError:
                pass
    
    @staticmethod
    async def broadcast(combat_id: str, message: Dict[str, Any]):
        """Broadcast a message to all clients in a combat session"""
        if combat_id not in combat_connections:
            return
        
        # Add timestamp to message
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()
        
        # Make a copy since we might modify the set during iteration
        connections = combat_connections[combat_id].copy()
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except RuntimeError:
                # Handle case where connection is closed but not properly removed
                await CombatWebSocketManager.disconnect(websocket, combat_id)


@router.websocket("/combat/{combat_id}/ws")
async def combat_websocket(websocket: WebSocket, combat_id: str):
    """WebSocket endpoint for real-time combat updates"""
    try:
        await CombatWebSocketManager.connect(websocket, combat_id)
        
        # Keep connection alive and handle messages
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Process client message here if needed
                # For now, we're just echoing it back
                await websocket.send_json({
                    "type": "echo",
                    "data": message,
                    "timestamp": datetime.now().isoformat()
                })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        await CombatWebSocketManager.disconnect(websocket, combat_id)
    
    except Exception as e:
        logger.error(f"Error in combat WebSocket: {str(e)}")
        try:
            await websocket.close()
        except RuntimeError:
            pass
        await CombatWebSocketManager.disconnect(websocket, combat_id)


# Helper functions to be called from other parts of the application

async def notify_combat_started(combat_id: str, initiative_order: List[str], current_turn: Dict[str, Any]):
    """Notify all clients that combat has started"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "combat_started",
        "initiative_order": initiative_order,
        "current_turn": current_turn
    })


async def notify_turn_changed(combat_id: str, current_combatant: Dict[str, Any], round_number: int):
    """Notify all clients that the turn has changed"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "turn_changed",
        "current_combatant": current_combatant,
        "round_number": round_number
    })


async def notify_combatant_added(combat_id: str, combatant: Dict[str, Any]):
    """Notify all clients that a combatant has been added"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "combatant_added",
        "combatant": combatant
    })


async def notify_combatant_removed(combat_id: str, combatant_id: str):
    """Notify all clients that a combatant has been removed"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "combatant_removed",
        "combatant_id": combatant_id
    })


async def notify_attack_performed(combat_id: str, attack_result: Dict[str, Any]):
    """Notify all clients that an attack has been performed"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "attack_performed",
        "attack_result": attack_result
    })


async def notify_status_effect_added(combat_id: str, combatant_id: str, effect: Dict[str, Any]):
    """Notify all clients that a status effect has been added"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "status_effect_added",
        "combatant_id": combatant_id,
        "effect": effect
    })


async def notify_status_effect_removed(combat_id: str, combatant_id: str, effect_type: str):
    """Notify all clients that a status effect has been removed"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "status_effect_removed",
        "combatant_id": combatant_id,
        "effect_type": effect_type
    })


async def notify_terrain_updated(combat_id: str, position: List[int], terrain_type: str):
    """Notify all clients that terrain has been updated"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "terrain_updated",
        "position": position,
        "terrain_type": terrain_type
    })


async def notify_combat_ended(combat_id: str):
    """Notify all clients that combat has ended"""
    await CombatWebSocketManager.broadcast(combat_id, {
        "type": "combat_ended"
    }) 