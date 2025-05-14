import pytest
from app import create_app, socketio
from flask_jwt_extended import create_access_token
import json

@pytest.fixture
def client():
    app = create_app()
    test_client = socketio.test_client(app)
    yield test_client
    test_client.disconnect()

@pytest.fixture
def auth_client():
    app = create_app()
    with app.app_context():
        token = create_access_token(identity='testuser')
    test_client = socketio.test_client(app, headers={'Authorization': f'Bearer {token}'})
    yield test_client
    test_client.disconnect()

def test_socketio_connect(client):
    received = client.get_received()
    assert any('message' in r['name'] and r['args'][0]['data'] == 'Connected to WebSocket server.' for r in received)

def test_socketio_auth_connect(auth_client):
    received = auth_client.get_received()
    assert any('message' in r['name'] and 'Connected as user' in r['args'][0]['data'] for r in received)

def test_socketio_room_join_leave(auth_client):
    auth_client.emit('join', {'room': 'testroom'})
    join_msgs = [r for r in auth_client.get_received() if r['name'] == 'message']
    assert any('Joined room testroom.' in r['args'][0]['data'] for r in join_msgs)
    auth_client.emit('leave', {'room': 'testroom'})
    leave_msgs = [r for r in auth_client.get_received() if r['name'] == 'message']
    assert any('Left room testroom.' in r['args'][0]['data'] for r in leave_msgs)

def test_socketio_send_message(auth_client):
    auth_client.emit('join', {'room': 'testroom'})
    auth_client.emit('send_message', {'room': 'testroom', 'message': 'hello'})
    msgs = [r for r in auth_client.get_received() if r['name'] == 'message']
    assert any('hello' in r['args'][0]['data'] for r in msgs) 