from flask_socketio import SocketIO, emit
from app.websockets.payloads import EventPayload, validate_payload
from app.websockets.event_types import EventType
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('websockets.broadcast')

# Room naming conventions:
#   world-{id}: World-level events
#   location-{id}: Location-specific events
#   combat-{id}: Combat session events
#   user_{id}: User-specific notifications

def broadcast_global(socketio: SocketIO, payload: EventPayload):
    """Broadcast an event to all connected clients."""
    if not validate_payload(payload):
        logger.error('Invalid payload for global broadcast')
        return
    socketio.emit('event', payload.__dict__)

def broadcast_room(socketio: SocketIO, room: str, payload: EventPayload):
    """Broadcast an event to a specific room."""
    if not validate_payload(payload):
        logger.error(f'Invalid payload for room broadcast: {room}')
        return
    if not is_valid_room_name(room):
        logger.error(f'Invalid room name: {room}')
        return
    socketio.emit('event', payload.__dict__, room=room)

def broadcast_user(socketio: SocketIO, user_id: str, payload: EventPayload):
    """Broadcast an event to a specific user (by user_id)."""
    if not validate_payload(payload):
        logger.error(f'Invalid payload for user broadcast: {user_id}')
        return
    room = f'user_{user_id}'
    socketio.emit('event', payload.__dict__, room=room)

def is_valid_room_name(room: str) -> bool:
    """Validate room naming conventions."""
    return (
        room.startswith('world-') or
        room.startswith('location-') or
        room.startswith('combat-') or
        room.startswith('user_')
    )

# Event filtering and queuing stubs (to be implemented in future subtasks)
def filter_event_for_client(event_type: EventType, client_filters: Optional[Dict[str, Any]]) -> bool:
    # Stub: always return True for now
    return True

def queue_event(event: EventPayload):
    # Stub: implement in-memory or Redis queue for high-volume events
    pass

# Combat room management helpers
def create_combat_room(socketio: SocketIO, combat_id: str):
    """Create a new combat room (no-op, room is created on join in SocketIO)."""
    # Room is implicitly created when a user joins
    logger.info(f'Combat room created: combat-{combat_id}')
    return f'combat-{combat_id}'

def join_combat_room(socketio: SocketIO, client_id: str, combat_id: str, is_spectator: bool = False):
    """Join a combat room, optionally as a spectator."""
    room = f'combat-{combat_id}'
    # In actual handler, use join_room(room)
    logger.info(f'Client {client_id} joined combat room {room} (spectator={is_spectator})')
    # Add logic to track spectators if needed
    return room

def leave_combat_room(socketio: SocketIO, client_id: str, combat_id: str):
    """Leave a combat room."""
    room = f'combat-{combat_id}'
    # In actual handler, use leave_room(room)
    logger.info(f'Client {client_id} left combat room {room}')
    return room

# Event emission stubs for combat and NPC events
def emit_turn_change(socketio: SocketIO, room: str, payload):
    """Emit a turn change event to a combat room."""
    socketio.emit('combat_turn_change', payload.__dict__, room=room)

def emit_initiative_update(socketio: SocketIO, room: str, payload):
    """Emit an initiative update event to a combat room."""
    socketio.emit('combat_initiative_update', payload.__dict__, room=room)

def emit_combat_result(socketio: SocketIO, room: str, payload):
    """Emit a combat result event to a combat room."""
    socketio.emit('combat_result', payload.__dict__, room=room)

def emit_combat_summary(socketio: SocketIO, room: str, payload):
    """Emit a combat summary event to a combat room."""
    socketio.emit('combat_summary', payload.__dict__, room=room)

def emit_npc_location_change(socketio: SocketIO, room: str, payload):
    """Emit an NPC location change event to a location room."""
    socketio.emit('npc_location_change', payload.__dict__, room=room)

def emit_npc_behavior_change(socketio: SocketIO, room: str, payload):
    """Emit an NPC behavior change event to a location room."""
    socketio.emit('npc_behavior_change', payload.__dict__, room=room)

def emit_time_change(socketio: SocketIO, world_id: str, payload):
    """Emit a time change event to the world room."""
    room = f'world-{world_id}'
    socketio.emit('world_time_change', payload.__dict__, room=room)

def emit_weather_update(socketio: SocketIO, world_id: str, payload):
    """Emit a weather update event to the world room."""
    room = f'world-{world_id}'
    socketio.emit('world_weather_update', payload.__dict__, room=room)

def emit_faction_update(socketio: SocketIO, faction_id: str, payload):
    """Emit a faction update event to the faction room (or global if needed)."""
    room = f'faction-{faction_id}'
    socketio.emit('faction_update', payload.__dict__, room=room)

def emit_global_event(socketio: SocketIO, payload):
    """Emit a global event announcement to all clients."""
    socketio.emit('global_event', payload.__dict__)

def emit_quest_available(socketio: SocketIO, eligible_players: list, payload):
    """Emit a quest available event to eligible players only."""
    for player_id in eligible_players:
        room = f'user_{player_id}'
        socketio.emit('quest_available', payload.__dict__, room=room)

def emit_quest_progress(socketio: SocketIO, player_id: str, payload):
    """Emit a quest progress event to a specific player."""
    room = f'user_{player_id}'
    socketio.emit('quest_progress', payload.__dict__, room=room)

def emit_quest_complete(socketio: SocketIO, player_id: str, payload):
    """Emit a quest complete event to a specific player."""
    room = f'user_{player_id}'
    socketio.emit('quest_complete', payload.__dict__, room=room) 