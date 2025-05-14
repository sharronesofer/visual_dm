import pytest
from flask import Flask
from app import create_app
from app.core.database import db
from flask_jwt_extended import create_access_token

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def auth_header(user_id=1):
    token = create_access_token(identity=user_id)
    return {'Authorization': f'Bearer {token}'}

def test_create_and_get_world(client):
    resp = client.post('/api/v1/worlds', json={
        'name': 'Test World',
        'description': 'A world for testing.'
    }, headers=auth_header())
    assert resp.status_code == 201
    world_id = resp.get_json()['id']
    get_resp = client.get(f'/api/v1/worlds/{world_id}', headers=auth_header())
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['name'] == 'Test World'

def test_update_world(client):
    resp = client.post('/api/v1/worlds', json={
        'name': 'Update World',
        'description': 'To be updated.'
    }, headers=auth_header())
    world_id = resp.get_json()['id']
    update_resp = client.put(f'/api/v1/worlds/{world_id}', json={
        'description': 'Updated!'
    }, headers=auth_header())
    assert update_resp.status_code == 200
    assert update_resp.get_json()['description'] == 'Updated!'

def test_delete_world(client):
    resp = client.post('/api/v1/worlds', json={
        'name': 'Delete World',
        'description': 'To be deleted.'
    }, headers=auth_header())
    world_id = resp.get_json()['id']
    del_resp = client.delete(f'/api/v1/worlds/{world_id}', headers=auth_header())
    assert del_resp.status_code == 200
    get_resp = client.get(f'/api/v1/worlds/{world_id}', headers=auth_header())
    assert get_resp.status_code == 404

def test_world_time_update(client):
    resp = client.post('/api/v1/worlds', json={
        'name': 'Time World',
        'description': 'Testing time.'
    }, headers=auth_header())
    world_id = resp.get_json()['id']
    put_resp = client.put(f'/api/v1/worlds/{world_id}/time', json={
        'time': '2025-01-01T00:00:00Z'
    }, headers=auth_header())
    assert put_resp.status_code == 200
    get_resp = client.get(f'/api/v1/worlds/{world_id}/time', headers=auth_header())
    assert get_resp.status_code == 200
    assert '2025-01-01' in get_resp.get_json()['time']

def test_world_weather_update(client):
    resp = client.post('/api/v1/worlds', json={
        'name': 'Weather World',
        'description': 'Testing weather.'
    }, headers=auth_header())
    world_id = resp.get_json()['id']
    put_resp = client.put(f'/api/v1/worlds/{world_id}/weather', json={
        'weather': 'rainy'
    }, headers=auth_header())
    assert put_resp.status_code == 200
    get_resp = client.get(f'/api/v1/worlds/{world_id}/weather', headers=auth_header())
    assert get_resp.status_code == 200
    assert get_resp.get_json()['weather'] == 'rainy' 