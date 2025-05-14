"""
Tests for NPC version control functionality.
"""

import pytest
from datetime import datetime
from app.core.models.npc import NPC, NPCType, NPCDisposition
from app.core.models.npc_version import NPCVersion
from app.core.services.npc_version_service import NPCVersionService
from app.core.database import db

@pytest.fixture
def test_npc(app):
    """Create a test NPC."""
    with app.app_context():
        npc = NPC(
            name="Test NPC",
            type=NPCType.MERCHANT.value,
            level=5,
            disposition=NPCDisposition.NEUTRAL.value,
            base_disposition=0.0,
            level_requirement=1,
            interaction_cooldown=300,
            schedule=[{"time": "09:00", "activity": "open_shop"}],
            dialogue_options={"greeting": "Hello traveler!"},
            behavior_flags={"is_merchant": True},
            inventory=[{"item_id": 1, "quantity": 10}],
            trade_inventory=[{"item_id": 2, "quantity": 5}],
            goals={"daily": ["open_shop", "close_shop"]},
            relationships={},
            memories=[]
        )
        db.session.add(npc)
        db.session.commit()
        return npc

def test_create_npc_version(test_npc, app):
    """Test creating a new NPC version."""
    with app.app_context():
        version = NPCVersionService.create_version(
            npc=test_npc,
            change_type="creation",
            change_description="Initial version",
            changed_fields=["name", "type", "level"]
        )
        
        assert version.npc_id == test_npc.id
        assert version.version_number == 1
        assert version.name == test_npc.name
        assert version.type == test_npc.type
        assert version.level == test_npc.level
        assert version.change_type == "creation"
        assert "name" in version.changed_fields

def test_update_npc_creates_version(test_npc, app):
    """Test that updating an NPC creates a new version."""
    with app.app_context():
        # Create initial version
        initial_version = NPCVersionService.create_version(
            npc=test_npc,
            change_type="creation",
            change_description="Initial version",
            changed_fields=["name", "type", "level"]
        )
        
        # Update NPC
        test_npc.name = "Updated NPC"
        test_npc.level = 6
        db.session.commit()
        
        # Create version for update
        update_version = NPCVersionService.create_version(
            npc=test_npc,
            change_type="update",
            change_description="Updated name and level",
            changed_fields=["name", "level"]
        )
        
        assert update_version.version_number == 2
        assert update_version.name == "Updated NPC"
        assert update_version.level == 6
        assert "name" in update_version.changed_fields
        assert "level" in update_version.changed_fields

def test_revert_npc_version(test_npc, app):
    """Test reverting an NPC to a previous version."""
    with app.app_context():
        # Create initial version
        initial_version = NPCVersionService.create_version(
            npc=test_npc,
            change_type="creation",
            change_description="Initial version",
            changed_fields=["name", "type", "level"]
        )
        
        # Update NPC and create new version
        test_npc.name = "Updated NPC"
        test_npc.level = 6
        db.session.commit()
        
        update_version = NPCVersionService.create_version(
            npc=test_npc,
            change_type="update",
            change_description="Updated name and level",
            changed_fields=["name", "level"]
        )
        
        # Revert to initial version
        NPCVersionService.revert_to_version(test_npc, initial_version)
        db.session.commit()
        
        # Check that NPC was reverted
        assert test_npc.name == "Test NPC"
        assert test_npc.level == 5
        
        # Check that revert created a new version
        revert_version = NPCVersion.query.filter_by(npc_id=test_npc.id).order_by(NPCVersion.version_number.desc()).first()
        assert revert_version.version_number == 3
        assert revert_version.change_type == "revert"
        assert revert_version.name == "Test NPC"
        assert revert_version.level == 5

def test_compare_npc_versions(test_npc, app):
    """Test comparing two NPC versions."""
    with app.app_context():
        # Create initial version
        initial_version = NPCVersionService.create_version(
            npc=test_npc,
            change_type="creation",
            change_description="Initial version",
            changed_fields=["name", "type", "level"]
        )
        
        # Update NPC and create new version
        test_npc.name = "Updated NPC"
        test_npc.level = 6
        test_npc.dialogue_options = {"greeting": "Welcome to my shop!"}
        db.session.commit()
        
        update_version = NPCVersionService.create_version(
            npc=test_npc,
            change_type="update",
            change_description="Updated multiple fields",
            changed_fields=["name", "level", "dialogue_options"]
        )
        
        # Compare versions
        differences = NPCVersionService.compare_versions(initial_version, update_version)
        
        assert len(differences) == 3
        assert any(d["field"] == "name" and d["version1"] == "Test NPC" and d["version2"] == "Updated NPC" for d in differences)
        assert any(d["field"] == "level" and d["version1"] == 5 and d["version2"] == 6 for d in differences)
        assert any(d["field"] == "dialogue_options" for d in differences)

def test_get_npc_version_history(test_npc, app):
    """Test getting version history for an NPC."""
    with app.app_context():
        # Create multiple versions
        versions = []
        
        # Initial version
        versions.append(NPCVersionService.create_version(
            npc=test_npc,
            change_type="creation",
            change_description="Initial version",
            changed_fields=["name", "type", "level"]
        ))
        
        # Update 1
        test_npc.name = "Updated NPC"
        db.session.commit()
        versions.append(NPCVersionService.create_version(
            npc=test_npc,
            change_type="update",
            change_description="Updated name",
            changed_fields=["name"]
        ))
        
        # Update 2
        test_npc.level = 6
        db.session.commit()
        versions.append(NPCVersionService.create_version(
            npc=test_npc,
            change_type="update",
            change_description="Updated level",
            changed_fields=["level"]
        ))
        
        # Get history
        history = NPCVersion.query.filter_by(npc_id=test_npc.id).order_by(NPCVersion.version_number).all()
        
        assert len(history) == 3
        assert history[0].version_number == 1
        assert history[0].change_type == "creation"
        assert history[1].version_number == 2
        assert "name" in history[1].changed_fields
        assert history[2].version_number == 3
        assert "level" in history[2].changed_fields 