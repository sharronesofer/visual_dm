"""
Tests for version control models.
"""

import pytest
from datetime import datetime, timezone
from app.core.models.version_control import CodeVersion, TaskVersionLink, ReviewVersionLink

def test_code_version_creation(session, sample_version):
    """Test creating a code version."""
    assert sample_version.id is not None
    assert sample_version.commit_hash == '1234567890123456789012345678901234567890'
    assert sample_version.author == 'Test Author'
    assert sample_version.commit_message == 'Test commit message'
    assert isinstance(sample_version.commit_timestamp, datetime)
    assert sample_version.branch_name == 'main'
    assert sample_version.tag_name == 'v1.0.0'
    assert sample_version.version_metadata == {'key': 'value'}

def test_code_version_to_dict(sample_version):
    """Test converting a code version to dictionary."""
    version_dict = sample_version.to_dict()
    assert version_dict['id'] == sample_version.id
    assert version_dict['commit_hash'] == sample_version.commit_hash
    assert version_dict['author'] == sample_version.author
    assert version_dict['commit_message'] == sample_version.commit_message
    assert version_dict['commit_timestamp'] == sample_version.commit_timestamp.isoformat()
    assert version_dict['branch_name'] == sample_version.branch_name
    assert version_dict['tag_name'] == sample_version.tag_name
    assert version_dict['version_metadata'] == sample_version.version_metadata

def test_task_link_creation(session, sample_task_link):
    """Test creating a task version link."""
    assert sample_task_link.id is not None
    assert sample_task_link.task_id == 1
    assert sample_task_link.version_id is not None
    assert sample_task_link.link_type == 'implementation'
    assert sample_task_link.link_metadata == {'status': 'completed'}

def test_task_link_to_dict(sample_task_link):
    """Test converting a task link to dictionary."""
    link_dict = sample_task_link.to_dict()
    assert link_dict['id'] == sample_task_link.id
    assert link_dict['task_id'] == sample_task_link.task_id
    assert link_dict['version_id'] == sample_task_link.version_id
    assert link_dict['link_type'] == sample_task_link.link_type
    assert link_dict['link_metadata'] == sample_task_link.link_metadata

def test_review_link_creation(session, sample_review_link):
    """Test creating a review version link."""
    assert sample_review_link.id is not None
    assert sample_review_link.review_id == 1
    assert sample_review_link.version_id is not None
    assert sample_review_link.link_type == 'review'
    assert sample_review_link.link_metadata == {'status': 'approved'}

def test_review_link_to_dict(sample_review_link):
    """Test converting a review link to dictionary."""
    link_dict = sample_review_link.to_dict()
    assert link_dict['id'] == sample_review_link.id
    assert link_dict['review_id'] == sample_review_link.review_id
    assert link_dict['version_id'] == sample_review_link.version_id
    assert link_dict['link_type'] == sample_review_link.link_type
    assert link_dict['link_metadata'] == sample_review_link.link_metadata

def test_code_version_relationships(session, sample_version, sample_task_link, sample_review_link):
    """Test relationships between models."""
    # Test task links relationship
    assert len(sample_version.task_links) == 1
    task_link = sample_version.task_links[0]
    assert task_link.id == sample_task_link.id
    assert task_link.task_id == sample_task_link.task_id
    
    # Test review links relationship
    assert len(sample_version.review_links) == 1
    review_link = sample_version.review_links[0]
    assert review_link.id == sample_review_link.id
    assert review_link.review_id == sample_review_link.review_id

def test_code_version_validation(session):
    """Test code version validation."""
    # Test invalid commit hash
    with pytest.raises(ValueError):
        CodeVersion(
            commit_hash='invalid',
            author='Test Author',
            commit_message='Test message',
            commit_timestamp=datetime.now(timezone.utc)
        )
    
    # Test missing required fields
    with pytest.raises(ValueError):
        CodeVersion(
            commit_hash='1234567890123456789012345678901234567890'
        )

def test_link_validation(session, sample_version):
    """Test link validation."""
    # Test invalid link type for task link
    with pytest.raises(ValueError):
        TaskVersionLink(
            task_id=1,
            version_id=sample_version.id,
            link_type='invalid'
        )
    
    # Test invalid link type for review link
    with pytest.raises(ValueError):
        ReviewVersionLink(
            review_id=1,
            version_id=sample_version.id,
            link_type='invalid'
        ) 