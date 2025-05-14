import pytest
import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from typing import List, Dict, Any
from datetime import datetime

from app.websocket.chat import ChatManager, get_chat_manager
from app.models.chat import ChatMessage, ChatRoom
from tests.utils.test_utils import AsyncTestUtils, DBTestUtils

# Test data
TEST_ROOM = "test-room"
TEST_USER = "test-user"
TEST_MESSAGE = "Hello, World!"

@pytest.fixture
def chat_manager():
    """Create a fresh ChatManager instance for each test."""
    return ChatManager()

@pytest.fixture
def app(chat_manager: ChatManager) -> FastAPI:
    """Create a test FastAPI application with WebSocket endpoints."""
    from app.main import app
    app.dependency_overrides[get_chat_manager] = lambda: chat_manager
    return app

@pytest.fixture
def test_client(app: FastAPI) -> TestClient:
    """Create a TestClient instance."""
    return TestClient(app)

class TestChatWebSocket:
    @pytest.mark.asyncio
    async def test_connect_to_chat(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/{TEST_USER}") as websocket:
            data = await AsyncTestUtils.websocket_receive_json(websocket)
            assert data["type"] == "connection_established"
            assert data["user"] == TEST_USER
            assert data["room"] == TEST_ROOM

    @pytest.mark.asyncio
    async def test_disconnect_from_chat(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/{TEST_USER}"):
            pass  # WebSocket will disconnect when exiting context

        # Verify user was removed from room
        assert not chat_manager.get_users_in_room(TEST_ROOM)

    @pytest.mark.asyncio
    async def test_send_and_receive_message(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user1") as websocket1:
            async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user2") as websocket2:
                # Skip connection messages
                await AsyncTestUtils.websocket_receive_json(websocket1)
                await AsyncTestUtils.websocket_receive_json(websocket2)

                # Send message from user1
                await AsyncTestUtils.websocket_send_json(websocket1, {
                    "type": "message",
                    "content": TEST_MESSAGE
                })

                # Both users should receive the message
                for websocket in [websocket1, websocket2]:
                    data = await AsyncTestUtils.websocket_receive_json(websocket)
                    assert data["type"] == "chat_message"
                    assert data["content"] == TEST_MESSAGE
                    assert data["user"] == "user1"
                    assert data["room"] == TEST_ROOM
                    assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_user_join_notification(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user1") as websocket1:
            await AsyncTestUtils.websocket_receive_json(websocket1)  # Skip connection message

            async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user2") as websocket2:
                # user1 should receive user2's join notification
                data = await AsyncTestUtils.websocket_receive_json(websocket1)
                assert data["type"] == "user_joined"
                assert data["user"] == "user2"
                assert data["room"] == TEST_ROOM

    @pytest.mark.asyncio
    async def test_user_leave_notification(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user1") as websocket1:
            await AsyncTestUtils.websocket_receive_json(websocket1)  # Skip connection message

            # Connect and immediately disconnect user2
            async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user2"):
                await AsyncTestUtils.websocket_receive_json(websocket1)  # Skip join notification

            # user1 should receive user2's leave notification
            data = await AsyncTestUtils.websocket_receive_json(websocket1)
            assert data["type"] == "user_left"
            assert data["user"] == "user2"
            assert data["room"] == TEST_ROOM

    @pytest.mark.asyncio
    async def test_get_room_history(self, app: FastAPI, chat_manager: ChatManager, db_test_utils: DBTestUtils):
        # Create some test messages in the database
        messages = [
            ChatMessage(
                room=TEST_ROOM,
                user=TEST_USER,
                content=f"Message {i}",
                timestamp=datetime.utcnow()
            ) for i in range(3)
        ]
        await db_test_utils.create_chat_messages(messages)

        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/{TEST_USER}") as websocket:
            await AsyncTestUtils.websocket_receive_json(websocket)  # Skip connection message

            # Request message history
            await AsyncTestUtils.websocket_send_json(websocket, {
                "type": "get_history"
            })

            # Verify received history
            data = await AsyncTestUtils.websocket_receive_json(websocket)
            assert data["type"] == "chat_history"
            assert len(data["messages"]) == 3
            for i, msg in enumerate(data["messages"]):
                assert msg["content"] == f"Message {i}"
                assert msg["user"] == TEST_USER
                assert msg["room"] == TEST_ROOM

    @pytest.mark.asyncio
    async def test_multiple_rooms(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/room1/user1") as websocket1:
            async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/room2/user2") as websocket2:
                # Skip connection messages
                await AsyncTestUtils.websocket_receive_json(websocket1)
                await AsyncTestUtils.websocket_receive_json(websocket2)

                # Send message in room1
                await AsyncTestUtils.websocket_send_json(websocket1, {
                    "type": "message",
                    "content": "Message in room1"
                })

                # Only user1 should receive it
                data = await AsyncTestUtils.websocket_receive_json(websocket1)
                assert data["type"] == "chat_message"
                assert data["content"] == "Message in room1"

                # user2 should not receive any message
                with pytest.raises(asyncio.TimeoutError):
                    await AsyncTestUtils.websocket_receive_json(websocket2, timeout=1.0)

    @pytest.mark.asyncio
    async def test_invalid_message_format(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/{TEST_USER}") as websocket:
            await AsyncTestUtils.websocket_receive_json(websocket)  # Skip connection message

            # Send invalid message
            await AsyncTestUtils.websocket_send_json(websocket, {
                "type": "invalid_type",
                "content": "This should fail"
            })

            # Should receive error message
            data = await AsyncTestUtils.websocket_receive_json(websocket)
            assert data["type"] == "error"
            assert "Invalid message type" in data["message"]

    @pytest.mark.asyncio
    async def test_rate_limiting(self, app: FastAPI, chat_manager: ChatManager):
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/{TEST_USER}") as websocket:
            await AsyncTestUtils.websocket_receive_json(websocket)  # Skip connection message

            # Send messages rapidly
            for _ in range(10):
                await AsyncTestUtils.websocket_send_json(websocket, {
                    "type": "message",
                    "content": "Rapid message"
                })

            # Should receive rate limit error
            data = await AsyncTestUtils.websocket_receive_json(websocket)
            assert data["type"] == "error"
            assert "Rate limit exceeded" in data["message"]

    @pytest.mark.asyncio
    async def test_reconnection(self, app: FastAPI, chat_manager: ChatManager):
        # First connection
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/{TEST_USER}") as websocket1:
            await AsyncTestUtils.websocket_receive_json(websocket1)  # Skip connection message

        # Reconnect with same user
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/{TEST_USER}") as websocket2:
            data = await AsyncTestUtils.websocket_receive_json(websocket2)
            assert data["type"] == "connection_established"
            assert "reconnected" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_room_capacity(self, app: FastAPI, chat_manager: ChatManager):
        # Set room capacity
        chat_manager.set_room_capacity(TEST_ROOM, 2)

        # Connect two users successfully
        async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user1") as websocket1:
            async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user2") as websocket2:
                # Try to connect third user
                with pytest.raises(Exception) as exc:
                    async with AsyncTestUtils.websocket_connect(app, f"/ws/chat/{TEST_ROOM}/user3"):
                        pass
                assert "Room is full" in str(exc.value) 