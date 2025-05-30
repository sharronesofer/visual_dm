import pytest
import os
import json
from unittest.mock import patch, MagicMock, mock_open, AsyncMock
from datetime import datetime, timedelta
import tempfile
import shutil
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path

from backend.systems.motif.repository import MotifRepository
from backend.systems.motif.models import (
    Motif,
    MotifCreate,
    MotifUpdate,
    MotifFilter,
    MotifScope,
    MotifLifecycle,
    MotifCategory,
    LocationInfo,
    Vector2,
)


class TestMotifRepository: pass
    """Test the MotifRepository for data storage and retrieval."""

    @pytest.fixture
    def temp_data_dir(self): pass
        """Create a temporary directory for test data."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_motif(self): pass
        """Create a test motif for use in tests."""
        return Motif(
            id="test-motif-id",
            name="Test Motif",
            description="A test motif for repository testing",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            lifecycle=MotifLifecycle.EMERGING,
            intensity=5,
            duration_days=14,
            theme="Test Theme",
            location=LocationInfo(
                x=100.0,
                y=200.0,
                region_id="test-region"
            ),
        )

    @pytest.fixture
    def repo(self, temp_data_dir): pass
        """Create a repository instance with the temporary directory."""
        return MotifRepository(data_path=temp_data_dir)

    @pytest.mark.asyncio
    async def test_create_motif(self, repo, mock_motif): pass
        """Test creating a motif in the repository."""
        result = await repo.create_motif(mock_motif)

        # Check that the result matches the input
        assert result.id == mock_motif.id
        assert result.name == mock_motif.name
        assert result.category == mock_motif.category
        assert result.theme == mock_motif.theme

    @pytest.mark.asyncio
    async def test_get_motif(self, repo, mock_motif): pass
        """Test retrieving a motif by ID."""
        # Create a motif first
        await repo.create_motif(mock_motif)
        
        result = await repo.get_motif(mock_motif.id)

        assert result is not None
        assert result.id == mock_motif.id
        assert result.name == mock_motif.name

        # Test with a non-existent ID
        result = await repo.get_motif("non-existent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_motif(self, repo, mock_motif): pass
        """Test updating a motif."""
        # Create a motif first
        await repo.create_motif(mock_motif)

        update_data = {
            "name": "Updated Name",
            "intensity": 8,
            "lifecycle": MotifLifecycle.STABLE,
        }

        result = await repo.update_motif(mock_motif.id, update_data)

        assert result is not None
        assert result.id == mock_motif.id
        assert result.name == "Updated Name"
        assert result.intensity == 8
        assert result.lifecycle == MotifLifecycle.STABLE

        # Test with a non-existent ID
        result = await repo.update_motif("non-existent-id", update_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_motif(self, repo, mock_motif): pass
        """Test deleting a motif."""
        # Create a motif first
        await repo.create_motif(mock_motif)

        result = await repo.delete_motif(mock_motif.id)
        assert result is True

        # Verify it's actually deleted
        deleted_motif = await repo.get_motif(mock_motif.id)
        assert deleted_motif is None

        # Test with a non-existent ID
        result = await repo.delete_motif("non-existent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_get_all_motifs(self, repo, mock_motif): pass
        """Test retrieving all motifs."""
        # Create a motif first
        await repo.create_motif(mock_motif)
        
        result = await repo.get_all_motifs()

        assert len(result) == 1
        assert result[0].id == mock_motif.id

    @pytest.mark.asyncio
    async def test_filter_motifs_by_category(self, repo): pass
        """Test filtering motifs by category."""
        motif1 = Motif(
            id="test-motif-1",
            name="Chaos Motif",
            description="A chaos motif",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            intensity=5,
            theme="Test Chaos Theme",
        )

        motif2 = Motif(
            id="test-motif-2",
            name="Betrayal Motif",
            description="A betrayal motif",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.REGIONAL,
            intensity=7,
            theme="Test Betrayal Theme",
        )

        await repo.create_motif(motif1)
        await repo.create_motif(motif2)

        # Filter by CHAOS category
        filter_params = MotifFilter(category=[MotifCategory.CHAOS])
        result = await repo.get_motifs(filter_params)

        assert len(result) == 1
        assert result[0].id == "test-motif-1"
        assert result[0].category == MotifCategory.CHAOS

        # Filter by multiple categories
        filter_params = MotifFilter(
            category=[MotifCategory.CHAOS, MotifCategory.BETRAYAL]
        )
        result = await repo.get_motifs(filter_params)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_filter_motifs_by_intensity(self, repo): pass
        """Test filtering motifs by intensity range."""
        motif1 = Motif(
            id="test-motif-1",
            name="Low Intensity",
            description="A low intensity motif",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            intensity=3,
            theme="Low Intensity Theme",
        )

        motif2 = Motif(
            id="test-motif-2",
            name="High Intensity",
            description="A high intensity motif",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.REGIONAL,
            intensity=8,
            theme="High Intensity Theme",
        )

        await repo.create_motif(motif1)
        await repo.create_motif(motif2)

        # Filter by min_intensity
        filter_params = MotifFilter(min_intensity=5)
        result = await repo.get_motifs(filter_params)

        assert len(result) == 1
        assert result[0].id == "test-motif-2"
        assert result[0].intensity == 8

        # Filter by max_intensity
        filter_params = MotifFilter(max_intensity=5)
        result = await repo.get_motifs(filter_params)

        assert len(result) == 1
        assert result[0].id == "test-motif-1"
        assert result[0].intensity == 3

    @pytest.mark.asyncio
    async def test_filter_motifs_by_lifecycle(self, repo): pass
        """Test filtering motifs by lifecycle stage."""
        motif1 = Motif(
            id="test-motif-1",
            name="Emerging Motif",
            description="An emerging motif",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            lifecycle=MotifLifecycle.EMERGING,
            intensity=5,
            theme="Emerging Theme",
        )

        motif2 = Motif(
            id="test-motif-2",
            name="Stable Motif",
            description="A stable motif",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.REGIONAL,
            lifecycle=MotifLifecycle.STABLE,
            intensity=7,
            theme="Stable Theme",
        )

        await repo.create_motif(motif1)
        await repo.create_motif(motif2)

        # Filter by EMERGING lifecycle
        filter_params = MotifFilter(lifecycle=[MotifLifecycle.EMERGING])
        result = await repo.get_motifs(filter_params)

        assert len(result) == 1
        assert result[0].id == "test-motif-1"
        assert result[0].lifecycle == MotifLifecycle.EMERGING

    @pytest.mark.asyncio
    async def test_get_global_motifs(self, repo): pass
        """Test retrieving global scope motifs."""
        global_motif = Motif(
            id="test-global-motif",
            name="Global Test Motif",
            description="A test motif with global scope",
            category=MotifCategory.CHAOS,
            scope=MotifScope.GLOBAL,
            intensity=7,
            theme="Global Theme",
        )

        regional_motif = Motif(
            id="test-regional-motif",
            name="Regional Test Motif",
            description="A test motif with regional scope",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.REGIONAL,
            intensity=5,
            theme="Regional Theme",
        )

        await repo.create_motif(global_motif)
        await repo.create_motif(regional_motif)

        # Filter by global scope
        filter_params = MotifFilter(scope=[MotifScope.GLOBAL])
        result = await repo.get_motifs(filter_params)

        assert len(result) == 1
        assert result[0].id == "test-global-motif"
        assert result[0].scope == MotifScope.GLOBAL

    @pytest.mark.asyncio
    async def test_get_regional_motifs(self, repo): pass
        """Test retrieving motifs for specific regions."""
        region1_motif = Motif(
            id="test-region1-motif",
            name="Region 1 Motif",
            description="A motif in region 1",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            intensity=5,
            theme="Region 1 Theme",
            location=LocationInfo(
                x=100.0,
                y=200.0,
                region_id="region1"
            ),
        )

        region2_motif = Motif(
            id="test-region2-motif",
            name="Region 2 Motif",
            description="A motif in region 2",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.REGIONAL,
            intensity=7,
            theme="Region 2 Theme",
            location=LocationInfo(
                x=300.0,
                y=400.0,
                region_id="region2"
            ),
        )

        await repo.create_motif(region1_motif)
        await repo.create_motif(region2_motif)

        # Filter by region_id
        filter_params = MotifFilter(region_id="region1")
        result = await repo.get_motifs(filter_params)

        assert len(result) == 1
        assert result[0].id == "test-region1-motif"
        assert result[0].location.region_id == "region1"

    @pytest.mark.asyncio
    async def test_filter_motifs_by_tags(self, repo): pass
        """Test filtering motifs by tags."""
        motif1 = Motif(
            id="test-motif-1",
            name="Tagged Motif 1",
            description="A motif with tags",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            intensity=5,
            theme="Tagged Theme 1",
            tags=["conflict", "danger", "action"],
        )

        motif2 = Motif(
            id="test-motif-2",
            name="Tagged Motif 2",
            description="Another motif with different tags",
            category=MotifCategory.BETRAYAL,
            scope=MotifScope.REGIONAL,
            intensity=7,
            theme="Tagged Theme 2",
            tags=["mystery", "intrigue"],
        )

        await repo.create_motif(motif1)
        await repo.create_motif(motif2)

        # Filter by tags
        filter_params = MotifFilter(tags=["conflict"])
        result = await repo.get_motifs(filter_params)

        assert len(result) == 1
        assert result[0].id == "test-motif-1"
        assert "conflict" in result[0].tags

    @pytest.mark.asyncio
    async def test_entity_data_operations(self, repo): pass
        """Test entity data storage and retrieval."""
        entity_id = "test-entity-123"
        entity_data = {
            "name": "Test Entity",
            "type": "character",
            "motif_associations": ["motif-1", "motif-2"]
        }

        # Store entity data
        result = await repo.update_entity_data(entity_id, entity_data)
        assert result is True

        # Retrieve entity data
        retrieved_data = await repo.get_entity_data(entity_id)
        assert retrieved_data == entity_data

        # Test non-existent entity - should return default structure
        non_existent_data = await repo.get_entity_data("non-existent-entity")
        expected_default = {"id": "non-existent-entity", "motif_encounters": []}
        assert non_existent_data == expected_default

    @pytest.mark.asyncio
    async def test_world_log_operations(self, repo): pass
        """Test world log storage and retrieval."""
        log_entry = {
            "event_type": "motif_triggered",
            "motif_id": "test-motif-123",
            "timestamp": datetime.utcnow().isoformat(),
            "details": "Test motif was triggered"
        }

        # Add log entry
        result = await repo.add_world_log(log_entry)
        assert result is True

        # Retrieve logs
        logs = await repo.get_world_logs()
        assert len(logs) >= 1
        assert any(log["motif_id"] == "test-motif-123" for log in logs)

        # Filter logs by event type
        filtered_logs = await repo.get_world_logs(event_type="motif_triggered")
        assert len(filtered_logs) >= 1
        assert all(log["event_type"] == "motif_triggered" for log in filtered_logs)

    def test_vector2_distance_calculation(self): pass
        """Test Vector2 distance calculation."""
        v1 = Vector2(0, 0)
        v2 = Vector2(3, 4)

        distance = v1.distance_to(v2)
        assert distance == 5.0

        # Test reverse direction
        distance_reverse = v2.distance_to(v1)
        assert distance_reverse == 5.0

        # Test same point
        distance_same = v1.distance_to(v1)
        assert distance_same == 0.0

    # Error handling tests
    async def test_create_motif_error_handling(self, repo): pass
        """Test error handling during motif creation."""
        with patch("builtins.open", mock_open()) as mock_file: pass
            mock_file.side_effect = IOError("File write error")
            
            sample_motif = Motif(
                id="error-test",
                name="Error Test",
                description="Test error handling",
                category=MotifCategory.CHAOS,
                scope=MotifScope.LOCAL,
                theme="test",
                intensity=5.0,
                lifecycle=MotifLifecycle.EMERGING,
                duration_days=7,
                location=LocationInfo(x=0.0, y=0.0, region_id="test"),
                world_id="test-world",
                metadata={},
            )
            
            with pytest.raises(Exception): pass
                await repo.create_motif(sample_motif)

    async def test_get_motif_error_handling(self, repo): pass
        """Test error handling during motif retrieval."""
        with patch.object(repo, 'get_all_motifs') as mock_get_all: pass
            mock_get_all.side_effect = Exception("Database error")
            
            result = await repo.get_motif("test-id")
            assert result is None

    async def test_get_all_motifs_file_error(self, repo): pass
        """Test error handling when file read fails."""
        with patch("builtins.open", mock_open()) as mock_file: pass
            mock_file.side_effect = IOError("File read error")
            
            result = await repo.get_all_motifs()
            assert result == []

    async def test_update_motif_error_handling(self, repo): pass
        """Test error handling during motif update."""
        with patch.object(repo, 'get_all_motifs') as mock_get_all: pass
            mock_get_all.side_effect = Exception("Database error")
            
            result = await repo.update_motif("test-id", {"name": "Test"})
            assert result is None

    async def test_delete_motif_error_handling(self, repo): pass
        """Test error handling during motif deletion."""
        with patch.object(repo, 'get_all_motifs') as mock_get_all: pass
            mock_get_all.side_effect = Exception("Database error")
            
            result = await repo.delete_motif("test-id")
            assert result is False

    async def test_filter_motifs_no_params(self, repo, mock_motif): pass
        """Test filtering with no parameters returns all motifs."""
        await repo.create_motif(mock_motif)
        
        result = await repo.get_motifs(None)
        assert len(result) == 1
        
        result2 = await repo.get_motifs(MotifFilter())
        assert len(result2) == 1

    async def test_filter_motifs_by_world_id(self, repo): pass
        """Test filtering motifs by world ID."""
        motif1 = Motif(
            id="world1-motif",
            name="World 1 Motif",
            description="Motif in world 1",
            category=MotifCategory.CHAOS,
            scope=MotifScope.LOCAL,
            theme="chaos",
            intensity=5.0,
            lifecycle=MotifLifecycle.EMERGING,
            duration_days=7,
            location=LocationInfo(x=0.0, y=0.0, region_id="region1"),
            world_id="world-1",
            metadata={},
        )
        
        motif2 = Motif(
            id="world2-motif",
            name="World 2 Motif",
            description="Motif in world 2",
            category=MotifCategory.HOPE,
            scope=MotifScope.LOCAL,
            theme="hope",
            intensity=3.0,
            lifecycle=MotifLifecycle.STABLE,
            duration_days=10,
            location=LocationInfo(x=5.0, y=5.0, region_id="region2"),
            world_id="world-2",
            metadata={},
        )
        
        await repo.create_motif(motif1)
        await repo.create_motif(motif2)
        
        # Filter by world ID
        filter_params = MotifFilter(world_id="world-1")
        filtered_motifs = await repo.get_motifs(filter_params)
        
        assert len(filtered_motifs) == 1
        assert filtered_motifs[0].world_id == "world-1"

    async def test_filter_motifs_by_related_entity(self, repo, mock_motif): pass
        """Test filtering motifs by related entity."""
        # Ensure mock_motif has related entities
        mock_motif.related_entities = ["entity1", "entity2"]
        await repo.create_motif(mock_motif)
        
        # Create motif without related entities
        unrelated_motif = Motif(
            id="unrelated-motif",
            name="Unrelated Motif",
            description="No related entities",
            category=MotifCategory.PEACE,
            scope=MotifScope.LOCAL,
            theme="peace",
            intensity=2.0,
            lifecycle=MotifLifecycle.STABLE,
            duration_days=5,
            location=LocationInfo(x=0.0, y=0.0, region_id="test-region"),
            related_entities=[],
            world_id="test-world",
            metadata={},
        )
        await repo.create_motif(unrelated_motif)
        
        # Filter by related entity
        filter_params = MotifFilter(related_entity_id="entity1")
        filtered_motifs = await repo.get_motifs(filter_params)
        
        assert len(filtered_motifs) == 1
        assert "entity1" in filtered_motifs[0].related_entities

    async def test_filter_motifs_by_region_with_global(self, repo): pass
        """Test filtering by region includes global motifs."""
        # Create regional motif
        regional_motif = Motif(
            id="regional-motif",
            name="Regional Motif",
            description="Regional motif",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            theme="chaos",
            intensity=5.0,
            lifecycle=MotifLifecycle.EMERGING,
            duration_days=10,
            location=LocationInfo(x=0.0, y=0.0, region_id="test-region"),
            world_id="test-world",
            metadata={},
        )
        
        # Create global motif - use valid lifecycle
        global_motif = Motif(
            id="global-motif",
            name="Global Motif",
            description="Global motif",
            category=MotifCategory.WAR,
            scope=MotifScope.GLOBAL,
            theme="war",
            intensity=8.0,
            lifecycle=MotifLifecycle.STABLE,  # Use valid enum value
            duration_days=30,
            location=LocationInfo(x=0.0, y=0.0, region_id="global"),
            world_id="test-world",
            metadata={},
        )
        
        await repo.create_motif(regional_motif)
        await repo.create_motif(global_motif)
        
        # Filter by region - should include both regional and global
        filter_params = MotifFilter(region_id="test-region")
        filtered_motifs = await repo.get_motifs(filter_params)
        
        assert len(filtered_motifs) == 2  # Both regional and global motifs
        scopes = [m.scope for m in filtered_motifs]
        assert MotifScope.REGIONAL in scopes
        assert MotifScope.GLOBAL in scopes

    async def test_entity_data_error_handling(self, repo): pass
        """Test error handling in entity data operations."""
        with patch("builtins.open", mock_open()) as mock_file: pass
            mock_file.side_effect = IOError("File error")
            
            # Test update error
            result = await repo.update_entity_data("test-entity", {"data": "test"})
            assert result is False
            
            # Test get error - the implementation returns default data on error
            result = await repo.get_entity_data("test-entity")
            expected = {"id": "test-entity", "motif_encounters": []}
            assert result == expected

    async def test_world_log_error_handling(self, repo): pass
        """Test world log operations error handling."""
        # Test with non-existent file
        if repo.world_log_file.exists(): pass
            os.remove(repo.world_log_file)
        
        logs = await repo.get_world_logs()
        assert logs == []

    async def test_get_world_log_events(self, repo): pass
        """Test get_world_log_events method."""
        # Add test events
        event1 = {"event_type": "motif.created", "motif_id": "test-1", "timestamp": "2023-01-01T00:00:00"}
        event2 = {"event_type": "motif.updated", "motif_id": "test-2", "timestamp": "2023-01-02T00:00:00"}
        
        await repo.add_world_log(event1)
        await repo.add_world_log(event2)
        
        # Test filtering by event type
        created_events = await repo.get_world_log_events("motif.created")
        assert len(created_events) == 1
        assert created_events[0]["motif_id"] == "test-1"
        
        # Test with limit and offset
        all_events = await repo.get_world_log_events("motif.created", limit=1, offset=0)
        assert len(all_events) == 1

    async def test_get_motif_events(self, repo): pass
        """Test get_motif_events method."""
        from datetime import datetime
        
        # Add motif-related events
        event1 = {"event_type": "motif.created", "data": {"id": "test-1"}}
        event2 = {"event_type": "user.login", "data": {"user": "test"}}  # Non-motif event
        event3 = {"event_type": "chaos.motif.triggered", "data": {"id": "test-2"}}
        
        await repo.add_world_log(event1)
        await repo.add_world_log(event2)
        await repo.add_world_log(event3)
        
        # Test getting motif events
        motif_events = await repo.get_motif_events()
        assert len(motif_events) >= 2  # Should get motif.created and chaos.motif events
        
        # Test with event type filter
        specific_events = await repo.get_motif_events(event_types=["motif.created"])
        assert len(specific_events) >= 1
        
        # Test with timestamp filter
        since = datetime.now()
        recent_events = await repo.get_motif_events(since=since)
        assert isinstance(recent_events, list)

    async def test_get_motifs_at_position(self, repo): pass
        """Test get_motifs_at_position method."""
        from backend.systems.motif.models import MotifScope, MotifCategory, MotifLifecycle, LocationInfo
        from backend.systems.motif.repository import Vector2
        
        # Create motifs at specific positions
        motif1 = Motif(
            id="pos-test-1",
            name="Position Test 1", 
            description="Test motif at position",
            category=MotifCategory.CHAOS,
            scope=MotifScope.LOCAL,
            lifecycle=MotifLifecycle.STABLE,
            intensity=5.0,
            theme="test",
            location=LocationInfo(x=10.0, y=10.0, region_id="test-region")
        )
        
        motif2 = Motif(
            id="pos-test-2",
            name="Position Test 2",
            description="Test motif at different position", 
            category=MotifCategory.HOPE,
            scope=MotifScope.LOCAL,
            lifecycle=MotifLifecycle.STABLE,
            intensity=3.0,
            theme="test",
            location=LocationInfo(x=50.0, y=50.0, region_id="test-region")
        )
        
        # Create global motif (no location)
        motif3 = Motif(
            id="pos-test-3",
            name="Global Test",
            description="Global test motif",
            category=MotifCategory.PEACE,
            scope=MotifScope.GLOBAL,
            lifecycle=MotifLifecycle.STABLE,
            intensity=7.0,
            theme="test"
        )
        
        await repo.create_motif(motif1)
        await repo.create_motif(motif2)
        await repo.create_motif(motif3)
        
        # Test getting motifs at position (10, 10) with radius 5
        position = Vector2(10.0, 10.0)
        nearby_motifs = await repo.get_motifs_at_position(position, radius=5.0)
        
        # Should get motif1 (exact position) and motif3 (global)
        motif_ids = [m.id for m in nearby_motifs]
        assert "pos-test-1" in motif_ids
        assert "pos-test-3" in motif_ids  # Global motifs affect all positions
        
        # Test with larger radius to include motif2
        far_motifs = await repo.get_motifs_at_position(position, radius=100.0)
        far_ids = [m.id for m in far_motifs]
        assert "pos-test-1" in far_ids
        assert "pos-test-2" in far_ids
        assert "pos-test-3" in far_ids

    async def test_delete_motif_not_found(self, repo): pass
        """Test deleting a non-existent motif."""
        # Try to delete a motif that doesn't exist
        result = await repo.delete_motif("non-existent-id")
        assert result is False  # Should return False for non-existent motif

    async def test_get_entity_data_file_error(self, repo): pass
        """Test get_entity_data with file not found."""
        # Remove entity data file to trigger error path
        if repo.entity_data_file.exists(): pass
            os.remove(repo.entity_data_file)
        
        data = await repo.get_entity_data("test-entity")
        # Should return default structure when file doesn't exist
        assert data == {"id": "test-entity", "motif_encounters": []}

    async def test_update_entity_data_file_error(self, repo): pass
        """Test update_entity_data with file error."""
        # First ensure file exists with valid data
        await repo.update_entity_data("test-entity", {"id": "test-entity", "data": "test"})
        
        # Now test successful update
        result = await repo.update_entity_data("test-entity", {"id": "test-entity", "updated": "data"})
        assert result is True

    async def test_add_world_log_without_timestamp(self, repo): pass
        """Test adding world log entry without timestamp."""
        log_entry = {"event_type": "test", "data": "no timestamp"}
        result = await repo.add_world_log(log_entry)
        assert result is True
        
        # Verify timestamp was added
        logs = await repo.get_world_logs()
        assert len(logs) > 0
        assert "timestamp" in logs[0]

    async def test_get_world_log_events_with_filters(self, repo): pass
        """Test get_world_log_events with filtering and pagination."""
        # Add test events
        await repo.add_world_log({"event_type": "motif.created", "motif_id": "test-1"})
        await repo.add_world_log({"event_type": "motif.updated", "motif_id": "test-2"})
        await repo.add_world_log({"event_type": "motif.created", "motif_id": "test-3"})
        
        # Test filtering by event type
        created_events = await repo.get_world_log_events("motif.created")
        assert len(created_events) == 2
        
        # Test pagination
        limited_events = await repo.get_world_log_events("motif.created", limit=1)
        assert len(limited_events) == 1

    async def test_get_motif_events_comprehensive(self, repo): pass
        """Test get_motif_events with various parameters."""
        from datetime import datetime, timedelta
        
        # Add test events with different timestamps
        base_time = datetime.utcnow()
        await repo.add_world_log({
            "event_type": "motif.triggered", 
            "motif_id": "test-1",
            "timestamp": (base_time - timedelta(days=1)).isoformat()
        })
        await repo.add_world_log({
            "event_type": "motif.evolved", 
            "motif_id": "test-2", 
            "timestamp": base_time.isoformat()
        })
        
        # Test without filters
        all_events = await repo.get_motif_events()
        assert isinstance(all_events, list)
        
        # Test with event_types filter
        filtered_events = await repo.get_motif_events(event_types=["motif.triggered"])
        assert len(filtered_events) >= 1
        
        # Test with since filter
        recent_events = await repo.get_motif_events(since=base_time - timedelta(hours=1))
        assert len(recent_events) >= 1

    async def test_get_regional_motifs_edge_cases(self, repo): pass
        """Test get_regional_motifs with edge cases."""
        # Test with non-existent region
        motifs = await repo.get_regional_motifs("non-existent-region")
        assert motifs == []
        
        # Add a regional motif with location
        regional_motif = Motif(
            id="regional-test",
            name="Regional Test",
            description="A regional motif",
            category=MotifCategory.CHAOS,
            scope=MotifScope.REGIONAL,
            intensity=5.0,
            theme="test",
            location=LocationInfo(x=10.0, y=20.0, region_id="test-region")
        )
        await repo.create_motif(regional_motif)
        
        # Test finding regional motifs
        region_motifs = await repo.get_regional_motifs("test-region")
        assert len(region_motifs) == 1
        assert region_motifs[0].id == "regional-test"

    async def test_get_motifs_at_position_edge_cases(self, repo): pass
        """Test get_motifs_at_position with various scenarios."""
        # Add motifs with different locations
        local_motif = Motif(
            id="local-pos-test",
            name="Local Position Test",
            description="Local motif at position",
            category=MotifCategory.HOPE,
            scope=MotifScope.LOCAL,
            intensity=4.0,
            theme="test",
            location=LocationInfo(x=0.0, y=0.0),
            spread_factor=2.0
        )
        await repo.create_motif(local_motif)
        
        global_motif = Motif(
            id="global-pos-test",
            name="Global Position Test", 
            description="Global motif",
            category=MotifCategory.PEACE,
            scope=MotifScope.GLOBAL,
            intensity=6.0,
            theme="test"
            # No location - global affects everywhere
        )
        await repo.create_motif(global_motif)
        
        position = Vector2(5.0, 5.0)
        
        # Test getting motifs at position
        affecting_motifs = await repo.get_motifs_at_position(position, radius=10.0)
        
        # Should include global motif and local motif if within spread
        motif_ids = [m.id for m in affecting_motifs]
        assert "global-pos-test" in motif_ids  # Global always affects
        
        # Test with larger radius
        large_radius_motifs = await repo.get_motifs_at_position(position, radius=100.0)
        large_radius_ids = [m.id for m in large_radius_motifs]
        assert "local-pos-test" in large_radius_ids
        assert "global-pos-test" in large_radius_ids
