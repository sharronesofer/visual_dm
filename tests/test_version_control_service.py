"""
Tests for version control service.
"""

import pytest
from datetime import datetime, timezone
from app.core.services.version_control_service import VersionControlService
from app.core.exceptions import VersionControlError

def test_create_version(session):
    """Test creating a version."""
    version = VersionControlService.create_version(
        commit_hash='1234567890123456789012345678901234567890',
        author='Test Author',
        commit_message='Test commit message',
        commit_timestamp=datetime.now(timezone.utc),
        branch_name='main',
        tag_name='v1.0.0',
        metadata={'key': 'value'}
    )
    
    assert version.id is not None
    assert version.commit_hash == '1234567890123456789012345678901234567890'
    assert version.author == 'Test Author'
    assert version.branch_name == 'main'

def test_get_version_by_commit_hash(session, sample_version):
    """Test retrieving a version by commit hash."""
    version = VersionControlService.get_version_by_commit_hash(sample_version.commit_hash)
    assert version is not None
    assert version.id == sample_version.id
    
    # Test non-existent commit hash
    version = VersionControlService.get_version_by_commit_hash('nonexistent')
    assert version is None

def test_link_task_to_version(session, sample_version):
    """Test linking a task to a version."""
    link = VersionControlService.link_task_to_version(
        task_id=1,
        version_id=sample_version.id,
        link_type='implementation',
        metadata={'status': 'completed'}
    )
    
    assert link.id is not None
    assert link.task_id == 1
    assert link.version_id == sample_version.id
    assert link.link_type == 'implementation'
    
    # Test linking same task again
    with pytest.raises(VersionControlError):
        VersionControlService.link_task_to_version(
            task_id=1,
            version_id=sample_version.id,
            link_type='implementation'
        )

def test_link_review_to_version(session, sample_version):
    """Test linking a review to a version."""
    link = VersionControlService.link_review_to_version(
        review_id=1,
        version_id=sample_version.id,
        link_type='review',
        metadata={'status': 'approved'}
    )
    
    assert link.id is not None
    assert link.review_id == 1
    assert link.version_id == sample_version.id
    assert link.link_type == 'review'
    
    # Test linking same review again
    with pytest.raises(VersionControlError):
        VersionControlService.link_review_to_version(
            review_id=1,
            version_id=sample_version.id,
            link_type='review'
        )

def test_get_tasks_for_version(session, sample_version, sample_task_link):
    """Test getting tasks linked to a version."""
    tasks = VersionControlService.get_tasks_for_version(sample_version.commit_hash)
    assert len(tasks) == 1
    assert tasks[0].id == sample_task_link.id
    assert tasks[0].task_id == sample_task_link.task_id

def test_get_reviews_for_version(session, sample_version, sample_review_link):
    """Test getting reviews linked to a version."""
    reviews = VersionControlService.get_reviews_for_version(sample_version.commit_hash)
    assert len(reviews) == 1
    assert reviews[0].id == sample_review_link.id
    assert reviews[0].review_id == sample_review_link.review_id

def test_get_versions_for_task(session, sample_version, sample_task_link):
    """Test getting versions linked to a task."""
    versions = VersionControlService.get_versions_for_task(sample_task_link.task_id)
    assert len(versions) == 1
    assert versions[0].id == sample_version.id
    assert versions[0].commit_hash == sample_version.commit_hash

def test_get_versions_for_review(session, sample_version, sample_review_link):
    """Test getting versions linked to a review."""
    versions = VersionControlService.get_versions_for_review(sample_review_link.review_id)
    assert len(versions) == 1
    assert versions[0].id == sample_version.id
    assert versions[0].commit_hash == sample_version.commit_hash

def test_update_version_metadata(session, sample_version):
    """Test updating version metadata."""
    new_metadata = {'key': 'new_value', 'new_key': 'value'}
    version = VersionControlService.update_version_metadata(
        sample_version.commit_hash,
        new_metadata
    )
    
    assert version.metadata == new_metadata
    
    # Test updating non-existent version
    with pytest.raises(VersionControlError):
        VersionControlService.update_version_metadata('nonexistent', {})

def test_update_task_link_metadata(session, sample_task_link):
    """Test updating task link metadata."""
    new_metadata = {'status': 'in-progress', 'notes': 'Updated'}
    link = VersionControlService.update_task_link_metadata(
        sample_task_link.id,
        new_metadata
    )
    
    assert link.metadata == new_metadata
    
    # Test updating non-existent link
    with pytest.raises(VersionControlError):
        VersionControlService.update_task_link_metadata(9999, {})

def test_update_review_link_metadata(session, sample_review_link):
    """Test updating review link metadata."""
    new_metadata = {'status': 'rejected', 'notes': 'Needs work'}
    link = VersionControlService.update_review_link_metadata(
        sample_review_link.id,
        new_metadata
    )
    
    assert link.metadata == new_metadata
    
    # Test updating non-existent link
    with pytest.raises(VersionControlError):
        VersionControlService.update_review_link_metadata(9999, {})

def test_delete_task_link(session, sample_task_link):
    """Test deleting a task link."""
    VersionControlService.delete_task_link(sample_task_link.id)
    
    # Verify link is deleted
    assert session.query(TaskVersionLink).get(sample_task_link.id) is None
    
    # Test deleting non-existent link
    with pytest.raises(VersionControlError):
        VersionControlService.delete_task_link(9999)

def test_delete_review_link(session, sample_review_link):
    """Test deleting a review link."""
    VersionControlService.delete_review_link(sample_review_link.id)
    
    # Verify link is deleted
    assert session.query(ReviewVersionLink).get(sample_review_link.id) is None
    
    # Test deleting non-existent link
    with pytest.raises(VersionControlError):
        VersionControlService.delete_review_link(9999) 