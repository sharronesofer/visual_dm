import pytest
from flask import Flask
from app import create_app
from app.auth.models import User
from app.core.database import db
from flask_jwt_extended import decode_token

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_register_success(client):
    resp = client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'User registered successfully.' in data['message']

def test_register_duplicate(client):
    client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123'
    })
    resp = client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123'
    })
    assert resp.status_code == 409

def test_login_success(client):
    client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123'
    })
    resp = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'Password123'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_invalid(client):
    resp = client.post('/api/v1/auth/login', json={
        'username': 'nouser',
        'password': 'badpass'
    })
    assert resp.status_code == 401

def test_me_requires_auth(client):
    resp = client.get('/api/v1/auth/me')
    assert resp.status_code == 401

def test_me_success(client):
    client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123'
    })
    login_resp = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'Password123'
    })
    access_token = login_resp.get_json()['access_token']
    resp = client.get('/api/v1/auth/me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['username'] == 'testuser'

def test_refresh_success(client):
    client.post('/api/v1/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Password123'
    })
    login_resp = client.post('/api/v1/auth/login', json={
        'username': 'testuser',
        'password': 'Password123'
    })
    refresh_token = login_resp.get_json()['refresh_token']
    resp = client.post('/api/v1/auth/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'access_token' in data

def test_password_reset_stub(client):
    resp = client.post('/api/v1/auth/password-reset', json={
        'email': 'test@example.com'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'Password reset instructions sent' in data['message']

def test_password_reset_confirm_stub(client):
    resp = client.post('/api/v1/auth/password-reset-confirm', json={
        'token': 'sometoken',
        'new_password': 'NewPassword123'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'Password has been reset' in data['message'] 