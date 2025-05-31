"""
Magic System WebSocket Integration for Unity Frontend

Provides real-time communication for:
- Spell casting events
- Effect expiration notifications  
- Spell slot updates
- Concentration breaking alerts
"""

from typing import Dict, List
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime

class MagicWebSocketManager:
    """Manages WebSocket connections for magic system events."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, character_id: str):
        """Connect a WebSocket for a character."""
        await websocket.accept()
        if character_id not in self.active_connections:
            self.active_connections[character_id] = []
        self.active_connections[character_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, character_id: str):
        """Disconnect a WebSocket."""
        if character_id in self.active_connections:
            self.active_connections[character_id].remove(websocket)
            if not self.active_connections[character_id]:
                del self.active_connections[character_id]
    
    async def send_to_character(self, character_id: str, message: dict):
        """Send message to all connections for a character."""
        if character_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[character_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except:
                    disconnected.append(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[character_id].remove(conn)
    
    async def broadcast_spell_cast(self, caster_id: str, spell_name: str, target_id: str = None, effect_id: str = None):
        """Broadcast spell casting event."""
        message = {
            "type": "spell_cast",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "spell_name": spell_name,
                "caster_id": caster_id,
                "target_id": target_id,
                "effect_id": effect_id
            }
        }
        
        # Send to caster
        await self.send_to_character(caster_id, message)
        
        # Send to target if different
        if target_id and target_id != caster_id:
            await self.send_to_character(target_id, message)
    
    async def broadcast_effect_expired(self, character_id: str, effect_id: str, spell_name: str):
        """Broadcast effect expiration."""
        message = {
            "type": "effect_expired",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "effect_id": effect_id,
                "spell_name": spell_name
            }
        }
        await self.send_to_character(character_id, message)
    
    async def broadcast_spell_slots_updated(self, character_id: str, level: int, remaining_slots: int):
        """Broadcast spell slot updates."""
        message = {
            "type": "spell_slots_updated",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "character_id": character_id,
                "level": level,
                "remaining_slots": remaining_slots
            }
        }
        await self.send_to_character(character_id, message)
    
    async def broadcast_concentration_broken(self, character_id: str, spell_name: str, reason: str):
        """Broadcast concentration breaking."""
        message = {
            "type": "concentration_broken",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "spell_name": spell_name,
                "reason": reason
            }
        }
        await self.send_to_character(character_id, message)

# Global WebSocket manager instance
magic_ws_manager = MagicWebSocketManager()

# WebSocket endpoint
async def magic_websocket_endpoint(websocket: WebSocket, character_id: str):
    """WebSocket endpoint for magic system events."""
    await magic_ws_manager.connect(websocket, character_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Handle any client messages if needed
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        magic_ws_manager.disconnect(websocket, character_id)
