"""
Tests for location version control functionality.
"""

import pytest
from datetime import datetime, timedelta
from app.core.models.location import Location
from app.core.models.location_version import LocationVersion, LocationChangeLog
from app.core.services.location_version_service import LocationVersionService
from app.core.database import db

@pytest.fixture
def version_service():
    return LocationVersionService()

@pytest.fixture
def test_location(db_session):
    location = Location(
        name="Test Location",
        description="Test Description",
        type="city",
        is_discovered=True,
        x_coordinate=10.0,
        y_coordinate=20.0
    )
    db_session.add(location)
    db_session.commit()
    return location

def test_create_initial_version(version_service, test_location):
    """Test creating initial version for a location."""
    version = version_service.create_initial_version(test_location, "test_user")
    
    assert version is not None
    assert version.version_number == 1
    assert version.location_id == test_location.id
    assert version.change_type == "creation"
    assert version.changed_by == "test_user"
    assert version.data["name"] == test_location.name
    assert version.data["description"] == test_location.description

def test_update_location(version_service, test_location):
    """Test updating a location creates new version."""
    # Create initial version
    version_service.create_initial_version(test_location, "test_user")
    
    # Update location
    updates = {
        "name": "Updated Location",
        "description": "Updated Description"
    }
    
    version, logs = version_service.update_location(
        location=test_location,
        updates=updates,
        change_reason="Test update",
        changed_by="test_user"
    )
    
    assert version is not None
    assert version.version_number == 2
    assert version.change_type == "update"
    assert len(logs) == 2  # Two fields changed
    
    name_change = next(log for log in logs if log.field_name == "name")
    assert name_change.old_value == "Test Location"
    assert name_change.new_value == "Updated Location"

def test_get_version_history(version_service, test_location):
    """Test retrieving version history."""
    # Create initial version
    v1 = version_service.create_initial_version(test_location, "test_user")
    
    # Make updates
    updates = {"name": "Updated Location"}
    v2, _ = version_service.update_location(
        location=test_location,
        updates=updates,
        change_reason="Test update",
        changed_by="test_user"
    )
    
    versions = version_service.get_version_history(test_location.id)
    assert len(versions) == 2
    assert versions[0].id == v1.id
    assert versions[1].id == v2.id

def test_revert_location(version_service, test_location):
    """Test reverting location to previous version."""
    # Create initial version
    version_service.create_initial_version(test_location, "test_user")
    original_name = test_location.name
    
    # Make an update
    updates = {"name": "Updated Location"}
    version_service.update_location(
        location=test_location,
        updates=updates,
        change_reason="Test update",
        changed_by="test_user"
    )
    
    # Revert to version 1
    version = version_service.revert_location(
        location=test_location,
        version_number=1,
        change_reason="Test revert"
    )
    
    assert version is not None
    assert version.version_number == 3  # Should create new version
    assert test_location.name == original_name

def test_get_changes_between_versions(version_service, test_location):
    """Test getting changes between versions."""
    # Create initial version
    version_service.create_initial_version(test_location, "test_user")
    
    # Make multiple updates
    updates1 = {"name": "First Update"}
    version_service.update_location(
        location=test_location,
        updates=updates1,
        change_reason="First update",
        changed_by="test_user"
    )
    
    updates2 = {"description": "Updated Description"}
    version_service.update_location(
        location=test_location,
        updates=updates2,
        change_reason="Second update",
        changed_by="test_user"
    )
    
    changes = version_service.get_changes_between_versions(
        location_id=test_location.id,
        from_version=1,
        to_version=3
    )
    
    assert len(changes) == 2  # Two fields changed across versions
    assert any(c.field_name == "name" for c in changes)
    assert any(c.field_name == "description" for c in changes)

def test_get_location_at_date(version_service, test_location):
    """Test getting location state at specific date."""
    # Create initial version
    start_time = datetime.utcnow()
    version_service.create_initial_version(test_location, "test_user")
    original_name = test_location.name
    
    # Make an update after a delay
    middle_time = datetime.utcnow() + timedelta(seconds=1)
    updates = {"name": "Updated Location"}
    version_service.update_location(
        location=test_location,
        updates=updates,
        change_reason="Test update",
        changed_by="test_user"
    )
    
    # Get version at start time
    version = version_service.get_location_at_date(
        location_id=test_location.id,
        target_date=middle_time
    )
    
    assert version is not None
    assert version.data["name"] == original_name

def test_no_version_created_for_no_changes(version_service, test_location):
    """Test that no new version is created when no actual changes are made."""
    # Create initial version
    version_service.create_initial_version(test_location, "test_user")
    
    # Try to update with same values
    updates = {
        "name": test_location.name,
        "description": test_location.description
    }
    
    version, logs = version_service.update_location(
        location=test_location,
        updates=updates,
        change_reason="No changes",
        changed_by="test_user"
    )
    
    assert version is None
    assert len(logs) == 0

def test_version_created_for_deletion(version_service, test_location):
    """Test that a final version is created when deleting a location."""
    # Create initial version
    version_service.create_initial_version(test_location, "test_user")
    
    # Create deletion version
    version = test_location.create_version(
        change_type="deletion",
        change_reason="Location deleted",
        changed_by="test_user"
    )
    
    assert version is not None
    assert version.version_number == 2
    assert version.change_type == "deletion" 