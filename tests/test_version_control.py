"""
Tests for the version control system.
"""

import pytest
from datetime import datetime, timezone
from app.core.models.version_control import CodeVersion, TaskVersionLink, ReviewVersionLink
from app.core.services.version_control_service import VersionControlService
from app.core.exceptions import VersionControlError

@pytest.fixture
def sample_version_data():
    """Fixture providing sample version data."""
    return {
        'commit_hash': '1234567890123456789012345678901234567890',
        'author': 'Test Author',
        'commit_message': 'Test commit message',
        'commit_timestamp': datetime.now(timezone.utc),
        'branch_name': 'main',
        'tag_name': 'v1.0.0',
        'metadata': {'key': 'value'}
    }

def test_create_version(db_session, sample_version_data):
    """Test creating a new code version."""
    version = VersionControlService.create_version(**sample_version_data)
    
    assert version.id is not None
    assert version.commit_hash == sample_version_data['commit_hash']
    assert version.author == sample_version_data['author']
    assert version.commit_message == sample_version_data['commit_message']
    assert version.branch_name == sample_version_data['branch_name']
    assert version.tag_name == sample_version_data['tag_name']
    assert version.metadata == sample_version_data['metadata']

def test_create_version_duplicate_hash(db_session, sample_version_data):
    """Test that creating a version with duplicate commit hash fails."""
    VersionControlService.create_version(**sample_version_data)
    
    with pytest.raises(VersionControlError):
        VersionControlService.create_version(**sample_version_data)

def test_link_task_to_version(db_session, sample_version_data):
    """Test linking a task to a version."""
    version = VersionControlService.create_version(**sample_version_data)
    task_id = 1
    
    link = VersionControlService.link_task_to_version(
        task_id=task_id,
        version_id=version.id,
        link_type='implementation',
        metadata={'status': 'completed'}
    )
    
    assert link.id is not None
    assert link.task_id == task_id
    assert link.version_id == version.id
    assert link.link_type == 'implementation'
    assert link.metadata == {'status': 'completed'}

def test_link_review_to_version(db_session, sample_version_data):
    """Test linking a review to a version."""
    version = VersionControlService.create_version(**sample_version_data)
    review_id = 1
    
    link = VersionControlService.link_review_to_version(
        review_id=review_id,
        version_id=version.id,
        link_type='review',
        metadata={'status': 'approved'}
    )
    
    assert link.id is not None
    assert link.review_id == review_id
    assert link.version_id == version.id
    assert link.link_type == 'review'
    assert link.metadata == {'status': 'approved'}

def test_get_task_versions(db_session, sample_version_data):
    """Test getting versions linked to a task."""
    version1 = VersionControlService.create_version(**sample_version_data)
    version2 = VersionControlService.create_version(
        **{**sample_version_data, 'commit_hash': '2' * 40}
    )
    task_id = 1
    
    VersionControlService.link_task_to_version(task_id=task_id, version_id=version1.id)
    VersionControlService.link_task_to_version(task_id=task_id, version_id=version2.id)
    
    versions = VersionControlService.get_task_versions(task_id)
    assert len(versions) == 2
    assert versions[0].id in [version1.id, version2.id]
    assert versions[1].id in [version1.id, version2.id]

def test_get_review_versions(db_session, sample_version_data):
    """Test getting versions linked to a review."""
    version1 = VersionControlService.create_version(**sample_version_data)
    version2 = VersionControlService.create_version(
        **{**sample_version_data, 'commit_hash': '2' * 40}
    )
    review_id = 1
    
    VersionControlService.link_review_to_version(review_id=review_id, version_id=version1.id)
    VersionControlService.link_review_to_version(review_id=review_id, version_id=version2.id)
    
    versions = VersionControlService.get_review_versions(review_id)
    assert len(versions) == 2
    assert versions[0].id in [version1.id, version2.id]
    assert versions[1].id in [version1.id, version2.id]

def test_get_version_tasks(db_session, sample_version_data):
    """Test getting tasks linked to a version."""
    version = VersionControlService.create_version(**sample_version_data)
    task_ids = [1, 2]
    
    for task_id in task_ids:
        VersionControlService.link_task_to_version(task_id=task_id, version_id=version.id)
    
    linked_task_ids = VersionControlService.get_version_tasks(version.id)
    assert set(linked_task_ids) == set(task_ids)

def test_get_version_reviews(db_session, sample_version_data):
    """Test getting reviews linked to a version."""
    version = VersionControlService.create_version(**sample_version_data)
    review_ids = [1, 2]
    
    for review_id in review_ids:
        VersionControlService.link_review_to_version(review_id=review_id, version_id=version.id)
    
    linked_review_ids = VersionControlService.get_version_reviews(version.id)
    assert set(linked_review_ids) == set(review_ids)

def test_update_version_metadata(db_session, sample_version_data):
    """Test updating version metadata."""
    version = VersionControlService.create_version(**sample_version_data)
    new_metadata = {'new_key': 'new_value'}
    
    updated_version = VersionControlService.update_version_metadata(version.id, new_metadata)
    assert updated_version.metadata == {**sample_version_data['metadata'], **new_metadata}

def test_delete_task_link(db_session, sample_version_data):
    """Test deleting a task link."""
    version = VersionControlService.create_version(**sample_version_data)
    task_id = 1
    
    link = VersionControlService.link_task_to_version(task_id=task_id, version_id=version.id)
    VersionControlService.delete_version_link('task', link.id)
    
    versions = VersionControlService.get_task_versions(task_id)
    assert len(versions) == 0

def test_delete_review_link(db_session, sample_version_data):
    """Test deleting a review link."""
    version = VersionControlService.create_version(**sample_version_data)
    review_id = 1
    
    link = VersionControlService.link_review_to_version(review_id=review_id, version_id=version.id)
    VersionControlService.delete_version_link('review', link.id)
    
    versions = VersionControlService.get_review_versions(review_id)
    assert len(versions) == 0

def test_get_version_by_commit_hash(db_session, sample_version_data):
    """Test getting a version by commit hash."""
    version = VersionControlService.create_version(**sample_version_data)
    
    found_version = VersionControlService.get_version_by_commit_hash(sample_version_data['commit_hash'])
    assert found_version.id == version.id

def test_get_versions_by_branch(db_session, sample_version_data):
    """Test getting versions by branch name."""
    version1 = VersionControlService.create_version(**sample_version_data)
    version2 = VersionControlService.create_version(
        **{**sample_version_data, 'commit_hash': '2' * 40}
    )
    
    versions = VersionControlService.get_versions_by_branch(sample_version_data['branch_name'])
    assert len(versions) == 2
    assert versions[0].id in [version1.id, version2.id]
    assert versions[1].id in [version1.id, version2.id]

def test_get_versions_by_tag(db_session, sample_version_data):
    """Test getting versions by tag name."""
    version1 = VersionControlService.create_version(**sample_version_data)
    version2 = VersionControlService.create_version(
        **{**sample_version_data, 'commit_hash': '2' * 40}
    )
    
    versions = VersionControlService.get_versions_by_tag(sample_version_data['tag_name'])
    assert len(versions) == 2
    assert versions[0].id in [version1.id, version2.id]
    assert versions[1].id in [version1.id, version2.id]

def test_invalid_version_id(db_session):
    """Test operations with invalid version ID."""
    with pytest.raises(VersionControlError):
        VersionControlService.update_version_metadata(999, {'key': 'value'})

def test_invalid_link_type(db_session):
    """Test delete_version_link with invalid link type."""
    with pytest.raises(VersionControlError):
        VersionControlService.delete_version_link('invalid', 1)

def test_invalid_link_id(db_session):
    """Test delete_version_link with invalid link ID."""
    with pytest.raises(VersionControlError):
        VersionControlService.delete_version_link('task', 999) 