import pytest
import asyncio
import websockets
import json

WS_URL = "ws://localhost:8000/ws?token=TEST_TOKEN"

@pytest.mark.asyncio
async def test_websocket_connect_and_auth():
    async with websockets.connect(WS_URL) as ws:
        # Expect auth success message
        msg = await ws.recv()
        data = json.loads(msg)
        assert data["type"] == "auth_success"
        # Send a ping event
        await ws.send(json.dumps({"type": "ping"}))
        msg = await ws.recv()
        data = json.loads(msg)
        assert data["type"] == "pong" 