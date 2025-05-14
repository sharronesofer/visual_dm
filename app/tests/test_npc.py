import pytest
from flask import Flask
from app import create_app
from app.core.database import db
from flask_jwt_extended import create_access_token

def auth_header(user_id=1):
    token = create_access_token(identity=user_id)
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_create_and_get_npc(client):
    resp = client.post('/api/v1/npcs', json={
        'name': 'Test NPC',
        'type': 'merchant',
        'level': 1
    }, headers=auth_header())
    assert resp.status_code == 201
    npc_id = resp.get_json()['id']
    get_resp = client.get(f'/api/v1/npcs/{npc_id}', headers=auth_header())
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert data['name'] == 'Test NPC'

def test_update_npc(client):
    resp = client.post('/api/v1/npcs', json={
        'name': 'Update NPC',
        'type': 'guard',
        'level': 2
    }, headers=auth_header())
    npc_id = resp.get_json()['id']
    update_resp = client.put(f'/api/v1/npcs/{npc_id}', json={
        'level': 5
    }, headers=auth_header())
    assert update_resp.status_code == 200
    assert update_resp.get_json()['level'] == 5

def test_delete_npc(client):
    resp = client.post('/api/v1/npcs', json={
        'name': 'Delete NPC',
        'type': 'enemy',
        'level': 1
    }, headers=auth_header())
    npc_id = resp.get_json()['id']
    del_resp = client.delete(f'/api/v1/npcs/{npc_id}', headers=auth_header())
    assert del_resp.status_code == 200
    get_resp = client.get(f'/api/v1/npcs/{npc_id}', headers=auth_header())
    assert get_resp.status_code == 404

def test_npc_relationships(client):
    # Create two NPCs
    resp1 = client.post('/api/v1/npcs', json={
        'name': 'NPC1', 'type': 'merchant', 'level': 1
    }, headers=auth_header())
    resp2 = client.post('/api/v1/npcs', json={
        'name': 'NPC2', 'type': 'guard', 'level': 2
    }, headers=auth_header())
    npc1_id = resp1.get_json()['id']
    npc2_id = resp2.get_json()['id']
    # Add relationship
    rel_resp = client.post(f'/api/v1/npcs/{npc1_id}/relationships', json={
        'source_npc_id': npc1_id,
        'target_npc_id': npc2_id,
        'value': 0.5,
        'type': 'friend'
    }, headers=auth_header())
    assert rel_resp.status_code == 201
    # Get relationships
    get_rel = client.get(f'/api/v1/npcs/{npc1_id}/relationships', headers=auth_header())
    assert get_rel.status_code == 200
    rels = get_rel.get_json()
    assert any(r['target_npc_id'] == npc2_id for r in rels)
    # Update relationship
    put_rel = client.put(f'/api/v1/npcs/{npc1_id}/relationships/{npc2_id}', json={
        'value': 1.0
    }, headers=auth_header())
    assert put_rel.status_code == 200

def test_npc_schedule(client):
    resp = client.post('/api/v1/npcs', json={
        'name': 'Schedule NPC', 'type': 'trainer', 'level': 1
    }, headers=auth_header())
    npc_id = resp.get_json()['id']
    # Update schedule
    put_resp = client.put(f'/api/v1/npcs/{npc_id}/schedule', json={
        'schedule': [{'day': 'Monday', 'task': 'train'}]
    }, headers=auth_header())
    assert put_resp.status_code == 200
    # Get schedule
    get_resp = client.get(f'/api/v1/npcs/{npc_id}/schedule', headers=auth_header())
    assert get_resp.status_code == 200
    assert get_resp.get_json()['schedule'][0]['task'] == 'train' 