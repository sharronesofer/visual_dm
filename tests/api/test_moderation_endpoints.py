"""Tests for moderation API endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.models.user import User, Role
from app.core.models.infraction import Infraction
from app.core.models.consequence import Consequence
from app.core.models.appeal import Appeal
from app.core.enums import InfractionSeverity, ConsequenceType, AppealStatus
from app.core.auth import create_access_token
from app.core.database import db

client = TestClient(app)

@pytest.fixture
def admin_token(db_session):
    """Create an admin user and return their auth token."""
    admin_role = Role(name='admin')
    db_session.add(admin_role)
    
    admin = User(
        username='admin',
        email='admin@test.com',
        role=admin_role
    )
    admin.set_password('adminpass')
    db_session.add(admin)
    db_session.commit()
    
    return create_access_token(data={'sub': admin.email})

@pytest.fixture
def mod_token(db_session):
    """Create a moderator user and return their auth token."""
    mod_role = Role(name='moderator')
    db_session.add(mod_role)
    
    mod = User(
        username='moderator',
        email='mod@test.com',
        role=mod_role
    )
    mod.set_password('modpass')
    db_session.add(mod)
    db_session.commit()
    
    return create_access_token(data={'sub': mod.email})

@pytest.fixture
def test_infraction(db_session):
    """Create a test infraction."""
    infraction = Infraction(
        player_id=1,
        character_id=1,
        type='COMBAT_GRIEFING',
        severity=InfractionSeverity.MODERATE,
        description='Test infraction',
        created_at=datetime.utcnow()
    )
    db_session.add(infraction)
    db_session.commit()
    return infraction

@pytest.fixture
def test_appeal(db_session, test_infraction):
    """Create a test appeal."""
    appeal = Appeal(
        infraction_id=test_infraction.id,
        player_id=1,
        reason='Test appeal reason',
        evidence='Test evidence',
        status=AppealStatus.PENDING,
        submitted_at=datetime.utcnow()
    )
    db_session.add(appeal)
    db_session.commit()
    return appeal

def test_list_infractions_requires_auth(db_session):
    """Test that listing infractions requires authentication."""
    response = client.get('/api/moderation/infractions')
    assert response.status_code == 401

def test_list_infractions_requires_mod_role(db_session):
    """Test that listing infractions requires moderator role."""
    token = create_access_token(data={'sub': 'user@test.com'})
    response = client.get(
        '/api/moderation/infractions',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403

def test_list_infractions_as_mod(mod_token, test_infraction):
    """Test listing infractions as moderator."""
    response = client.get(
        '/api/moderation/infractions',
        headers={'Authorization': f'Bearer {mod_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['type'] == 'COMBAT_GRIEFING'

def test_get_infraction_details(mod_token, test_infraction):
    """Test getting detailed infraction information."""
    response = client.get(
        f'/api/moderation/infractions/{test_infraction.id}',
        headers={'Authorization': f'Bearer {mod_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == test_infraction.id
    assert data['type'] == 'COMBAT_GRIEFING'
    assert data['severity'] == 'MODERATE'

def test_update_infraction_severity(admin_token, test_infraction):
    """Test updating infraction severity."""
    response = client.patch(
        f'/api/moderation/infractions/{test_infraction.id}',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={'severity': 'MAJOR'}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['severity'] == 'MAJOR'

def test_list_appeals(mod_token, test_appeal):
    """Test listing appeals."""
    response = client.get(
        '/api/moderation/appeals',
        headers={'Authorization': f'Bearer {mod_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['status'] == 'PENDING'

def test_process_appeal_approval(mod_token, test_appeal):
    """Test approving an appeal."""
    response = client.post(
        f'/api/moderation/appeals/{test_appeal.id}/process',
        headers={'Authorization': f'Bearer {mod_token}'},
        json={
            'status': 'APPROVED',
            'response': 'Appeal approved based on evidence'
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'APPROVED'
    assert data['response'] == 'Appeal approved based on evidence'

def test_process_appeal_rejection(mod_token, test_appeal):
    """Test rejecting an appeal."""
    response = client.post(
        f'/api/moderation/appeals/{test_appeal.id}/process',
        headers={'Authorization': f'Bearer {mod_token}'},
        json={
            'status': 'REJECTED',
            'response': 'Insufficient evidence'
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'REJECTED'
    assert data['response'] == 'Insufficient evidence'

def test_get_moderation_stats(admin_token, test_infraction, test_appeal):
    """Test getting moderation statistics."""
    response = client.get(
        '/api/moderation/stats',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['total_infractions'] == 1
    assert data['pending_appeals'] == 1

def test_get_player_history(mod_token, test_infraction):
    """Test getting player infraction history."""
    response = client.get(
        '/api/moderation/players/1/history',
        headers={'Authorization': f'Bearer {mod_token}'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['infractions']) == 1
    assert data['total_infractions'] == 1

def test_bulk_process_appeals(admin_token, db_session):
    """Test bulk processing of appeals."""
    # Create multiple appeals
    appeals = []
    for i in range(3):
        appeal = Appeal(
            infraction_id=test_infraction.id,
            player_id=1,
            reason=f'Test appeal {i}',
            evidence='Test evidence',
            status=AppealStatus.PENDING,
            submitted_at=datetime.utcnow()
        )
        db_session.add(appeal)
        appeals.append(appeal)
    db_session.commit()

    response = client.post(
        '/api/moderation/appeals/bulk-process',
        headers={'Authorization': f'Bearer {admin_token}'},
        json={
            'appeal_ids': [a.id for a in appeals],
            'status': 'REJECTED',
            'response': 'Bulk rejection'
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['processed']) == 3
    assert all(a['status'] == 'REJECTED' for a in data['processed']) 