from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Set, Optional, List
from datetime import datetime, timedelta
import asyncio
import json

from app.models.chat import ChatMessage, ChatRoom
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

class RateLimiter:
    def __init__(self, messages_per_minute: int = 60):
        self.messages_per_minute = messages_per_minute
        self.message_times: Dict[str, List[datetime]] = {}

    def can_send_message(self, user_id: str) -> bool:
        now = datetime.utcnow()
        if user_id not in self.message_times:
            self.message_times[user_id] = []

        # Remove messages older than 1 minute
        self.message_times[user_id] = [
            t for t in self.message_times[user_id]
            if now - t < timedelta(minutes=1)
        ]

        # Check if user has exceeded rate limit
        if len(self.message_times[user_id]) >= self.messages_per_minute:
            return False

        self.message_times[user_id].append(now)
        return True

class ChatManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        self.room_capacities: Dict[str, int] = {}
        self.rate_limiter = RateLimiter()

    def set_room_capacity(self, room: str, capacity: int):
        self.room_capacities[room] = capacity

    def get_room_capacity(self, room: str) -> int:
        return self.room_capacities.get(room, float('inf'))

    def get_users_in_room(self, room: str) -> Set[str]:
        return set(self.active_connections.get(room, {}).keys())

    async def connect(self, websocket: WebSocket, room: str, user: str) -> bool:
        if room not in self.active_connections:
            self.active_connections[room] = {}

        # Check room capacity
        if len(self.active_connections[room]) >= self.get_room_capacity(room):
            raise Exception("Room is full")

        await websocket.accept()

        # Handle reconnection
        is_reconnection = user in self.active_connections[room]
        if is_reconnection:
            # Close old connection
            try:
                await self.active_connections[room][user].close()
            except:
                pass

        self.active_connections[room][user] = websocket

        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "user": user,
            "room": room,
            "message": "Reconnected to chat" if is_reconnection else "Connected to chat"
        }, websocket)

        if not is_reconnection:
            # Notify others about new user
            await self.broadcast_to_room(room, {
                "type": "user_joined",
                "user": user,
                "room": room
            }, exclude_user=user)

        return is_reconnection

    async def disconnect(self, room: str, user: str):
        if room in self.active_connections and user in self.active_connections[room]:
            # Remove user from room
            del self.active_connections[room][user]
            if not self.active_connections[room]:
                del self.active_connections[room]

            # Notify others about user leaving
            await self.broadcast_to_room(room, {
                "type": "user_left",
                "user": user,
                "room": room
            })

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_room(self, room: str, message: dict, exclude_user: Optional[str] = None):
        if room in self.active_connections:
            for user, connection in self.active_connections[room].items():
                if exclude_user is None or user != exclude_user:
                    try:
                        await connection.send_json(message)
                    except:
                        # Handle disconnected clients
                        await self.disconnect(room, user)

    async def handle_chat_message(self, room: str, user: str, content: str, db: AsyncSession):
        # Check rate limit
        if not self.rate_limiter.can_send_message(user):
            await self.send_personal_message({
                "type": "error",
                "message": "Rate limit exceeded. Please wait before sending more messages."
            }, self.active_connections[room][user])
            return

        # Create and save message
        message = ChatMessage(
            room=room,
            user=user,
            content=content,
            timestamp=datetime.utcnow()
        )
        db.add(message)
        await db.commit()

        # Broadcast message to room
        await self.broadcast_to_room(room, {
            "type": "chat_message",
            "content": content,
            "user": user,
            "room": room,
            "timestamp": message.timestamp.isoformat()
        })

    async def handle_get_history(self, room: str, user: str, db: AsyncSession):
        # Get room history from database
        messages = await db.query(ChatMessage).filter(
            ChatMessage.room == room
        ).order_by(ChatMessage.timestamp.desc()).limit(50).all()

        # Send history to user
        await self.send_personal_message({
            "type": "chat_history",
            "messages": [{
                "content": msg.content,
                "user": msg.user,
                "room": msg.room,
                "timestamp": msg.timestamp.isoformat()
            } for msg in messages]
        }, self.active_connections[room][user])

# FastAPI dependency to get ChatManager instance
_chat_manager = ChatManager()

def get_chat_manager() -> ChatManager:
    return _chat_manager

async def handle_websocket(
    websocket: WebSocket,
    room: str,
    user: str,
    chat_manager: ChatManager = Depends(get_chat_manager),
    db: AsyncSession = Depends(get_db)
):
    try:
        is_reconnection = await chat_manager.connect(websocket, room, user)

        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get("type")

                if message_type == "message":
                    await chat_manager.handle_chat_message(
                        room=room,
                        user=user,
                        content=data["content"],
                        db=db
                    )
                elif message_type == "get_history":
                    await chat_manager.handle_get_history(room, user, db)
                else:
                    await chat_manager.send_personal_message({
                        "type": "error",
                        "message": f"Invalid message type: {message_type}"
                    }, websocket)

            except json.JSONDecodeError:
                await chat_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid message format"
                }, websocket)

    except WebSocketDisconnect:
        await chat_manager.disconnect(room, user)
    except Exception as e:
        # Handle any other errors
        try:
            await websocket.close()
        except:
            pass
        await chat_manager.disconnect(room, user)
        raise e 