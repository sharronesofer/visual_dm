from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import logging
from typing import Dict
import threading
import time
from datetime import datetime

logger = logging.getLogger('websockets')

# In-memory connection registry (for development)
connection_registry: Dict[str, Dict] = {}

HEARTBEAT_INTERVAL = 20  # seconds
HEARTBEAT_TIMEOUT = 60   # seconds

# Add last-seen and session info to registry
def update_last_seen(sid):
    connection_registry[sid]['last_seen'] = datetime.utcnow()

def get_initial_state_for_user(user_id):
    # Stub: return initial state snapshot for user
    return {'rooms': [], 'subscriptions': []}

def get_missed_events_for_user(user_id, since):
    # Stub: return list of missed events since 'since' timestamp
    return []

def start_heartbeat_thread(socketio):
    def heartbeat_loop():
        while True:
            time.sleep(HEARTBEAT_INTERVAL)
            now = datetime.utcnow()
            for sid, info in list(connection_registry.items()):
                last_seen = info.get('last_seen', now)
                if (now - last_seen).total_seconds() > HEARTBEAT_TIMEOUT:
                    logger.warning(f"Disconnecting inactive client: {sid}")
                    socketio.emit('error', {'error': 'Heartbeat timeout'}, room=sid)
                    socketio.server.disconnect(sid)
                else:
                    socketio.emit('heartbeat', {'timestamp': now.isoformat() + 'Z'}, room=sid)
    thread = threading.Thread(target=heartbeat_loop, daemon=True)
    thread.start()

# Call this once after registering events
heartbeat_thread_started = False

def register_socketio_events(socketio: SocketIO):
    """Register all WebSocket event handlers with the given SocketIO instance."""

    @socketio.on('connect')
    def handle_connect():
        """Handle new WebSocket connection with authentication."""
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if not user_id:
                emit('error', {'error': 'Authentication required'})
                disconnect()
                return
            # Register connection
            sid = request.sid
            connection_registry[sid] = {'user_id': user_id}
            logger.info(f'User {user_id} connected (sid={sid})')
            emit('message', {'data': f'Connected as user {user_id}.'})
        except Exception as e:
            logger.error(f'WebSocket connect error: {e}')
            emit('error', {'error': 'Connection failed'})
            disconnect()

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnect and cleanup registry."""
        sid = request.sid
        user_id = connection_registry.get(sid, {}).get('user_id')
        if sid in connection_registry:
            del connection_registry[sid]
        logger.info(f'Client disconnected (sid={sid}, user_id={user_id})')

    @socketio.on('join')
    def handle_join(data):
        """Join a named room and notify others."""
        room = data.get('room')
        sid = request.sid
        user_id = connection_registry.get(sid, {}).get('user_id')
        if room and user_id:
            join_room(room)
            logger.info(f'User {user_id} joined room {room}')
            emit('message', {'data': f'User {user_id} joined room {room}.'}, room=room)
        else:
            emit('error', {'error': 'Room join failed: missing room or user.'})

    @socketio.on('leave')
    def handle_leave(data):
        """Leave a named room and notify others."""
        room = data.get('room')
        sid = request.sid
        user_id = connection_registry.get(sid, {}).get('user_id')
        if room and user_id:
            leave_room(room)
            logger.info(f'User {user_id} left room {room}')
            emit('message', {'data': f'User {user_id} left room {room}.'}, room=room)
        else:
            emit('error', {'error': 'Room leave failed: missing room or user.'})

    @socketio.on('send_message')
    def handle_send_message(data):
        """Send a message to a room."""
        room = data.get('room')
        message = data.get('message')
        sid = request.sid
        user_id = connection_registry.get(sid, {}).get('user_id')
        if room and message and user_id:
            emit('message', {'data': message, 'from': user_id}, room=room)
        else:
            emit('error', {'error': 'Send message failed: missing room, message, or user.'})

    @socketio.on('ping')
    def handle_ping():
        """Respond to ping with pong for connection verification."""
        emit('pong', {'data': 'pong'})

    @socketio.on('pong')
    def handle_pong():
        """Handle pong from client, update last-seen timestamp."""
        sid = request.sid
        if sid in connection_registry:
            update_last_seen(sid)
            logger.info(f'Received pong from {sid}')

    @socketio.on('reconnect')
    def handle_reconnect(data):
        """Handle client reconnection, resync state and missed events."""
        sid = request.sid
        user_id = data.get('user_id')
        last_seen = data.get('last_seen')
        logger.info(f'User {user_id} reconnected (sid={sid})')
        connection_registry[sid] = {'user_id': user_id, 'last_seen': datetime.utcnow()}
        # Send initial state
        state = get_initial_state_for_user(user_id)
        emit('initial_state', state)
        # Replay missed events (stub)
        missed_events = get_missed_events_for_user(user_id, last_seen)
        for event in missed_events:
            emit('event', event, room=sid)

    # On connect, send initial state
    orig_handle_connect = handle_connect
    def new_handle_connect():
        orig_handle_connect()
        sid = request.sid
        user_id = connection_registry.get(sid, {}).get('user_id')
        if user_id:
            state = get_initial_state_for_user(user_id)
            emit('initial_state', state)
    register_socketio_events.handle_connect = new_handle_connect

    # Start heartbeat thread once
    if not heartbeat_thread_started:
        start_heartbeat_thread(socketio)
        heartbeat_thread_started = True

    # Utility functions
    def emit_to_room(room, event, data):
        """Emit an event to a specific room."""
        emit(event, data, room=room)

    def emit_to_user(user_id, event, data):
        """Emit an event to a specific user (by user_id)."""
        # Find all sids for this user
        for sid, info in connection_registry.items():
            if info.get('user_id') == user_id:
                emit(event, data, room=sid)

    # Stubs for analytics, rate limiting, missed event replay
    # TODO: Implement analytics collection, per-client rate limiting, missed event storage/replay

    # Add more event handlers as needed for future subtasks 