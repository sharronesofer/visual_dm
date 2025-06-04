"""
Comprehensive tests for WorldStateManager with temporal versioning and regional state management.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from backend.systems.world_state.manager import (
    WorldStateManager, 
    RegionalSnapshot, 
    HistoricalSummary,
    SnapshotLevel,
    WorldStateRepository
)
from backend.systems.world_state.world_types import StateCategory, WorldRegion


class MockRepository(WorldStateRepository):
    """Mock repository for testing"""
    
    def __init__(self):
        self.states = {}
        self.snapshots = {}
        self.summaries = {}
        self.changes = []
    
    async def save_state(self, state):
        self.states['current'] = state
        return True
    
    async def load_state(self):
        return self.states.get('current')
    
    async def save_snapshot(self, snapshot):
        region_snapshots = self.snapshots.get(snapshot.region_id, [])
        region_snapshots.append(snapshot)
        self.snapshots[snapshot.region_id] = region_snapshots
        return True
    
    async def load_snapshots(self, region_id, start_time, end_time):
        region_snapshots = self.snapshots.get(region_id, [])
        return [s for s in region_snapshots 
                if start_time <= s.timestamp <= end_time]
    
    async def save_summary(self, summary):
        period_summaries = self.summaries.get(summary.period_type, [])
        period_summaries.append(summary)
        self.summaries[summary.period_type] = period_summaries
        return True
    
    async def load_summaries(self, period_type, start_time, end_time):
        period_summaries = self.summaries.get(period_type, [])
        return [s for s in period_summaries 
                if s.period_start <= end_time and s.period_end >= start_time]
    
    async def delete_changes_before(self, timestamp):
        initial_count = len(self.changes)
        self.changes = [c for c in self.changes 
                       if c.get('timestamp', datetime.min) >= timestamp]
        return initial_count - len(self.changes)


@pytest.fixture
async def manager():
    """Create a WorldStateManager instance for testing"""
    WorldStateManager.reset_instance()
    repository = MockRepository()
    manager = await WorldStateManager.get_instance(repository)
    return manager


@pytest.fixture
async def populated_manager():
    """Create a manager with some test data"""
    WorldStateManager.reset_instance()
    repository = MockRepository()
    manager = await WorldStateManager.get_instance(repository)
    
    # Add some test data
    await manager.set_state("global.population", 1000, category=StateCategory.SOCIAL)
    await manager.set_state("test_region.buildings", 5, "test_region", StateCategory.OTHER)
    await manager.set_state("test_region.resources.gold", 500, "test_region", StateCategory.ECONOMIC)
    
    return manager


class TestWorldStateManagerCore:
    """Test core state operations"""
    
    @pytest.mark.asyncio
    async def test_singleton_pattern(self):
        """Test that WorldStateManager is a proper singleton"""
        WorldStateManager.reset_instance()
        
        manager1 = await WorldStateManager.get_instance()
        manager2 = await WorldStateManager.get_instance()
        
        assert manager1 is manager2
    
    @pytest.mark.asyncio
    async def test_set_and_get_state(self, manager):
        """Test basic state setting and getting"""
        key = "test.variable"
        value = "test_value"
        
        await manager.set_state(key, value)
        result = await manager.get_state(key)
        
        assert result == value
    
    @pytest.mark.asyncio
    async def test_regional_state(self, manager):
        """Test regional state management"""
        region_id = "test_region"
        key = "population"
        value = 1000
        
        await manager.set_state(key, value, region_id)
        result = await manager.get_state(key, region_id)
        
        assert result == value
        
        # Ensure global state is separate
        global_result = await manager.get_state(key)
        assert global_result is None
    
    @pytest.mark.asyncio
    async def test_state_change_tracking(self, manager):
        """Test that state changes are properly tracked"""
        key = "test.counter"
        
        await manager.set_state(key, 1)
        await manager.set_state(key, 2)
        await manager.set_state(key, 3)
        
        # Check that changes were recorded
        changes = manager.current_state.change_history
        relevant_changes = [c for c in changes if c.state_key == key]
        
        assert len(relevant_changes) == 3
        assert relevant_changes[-1].new_value == 3
        assert relevant_changes[-1].old_value == 2
    
    @pytest.mark.asyncio
    async def test_query_state(self, populated_manager):
        """Test state querying with filters"""
        manager = populated_manager
        
        # Query all state
        all_state = await manager.query_state({})
        assert "global.population" in all_state
        
        # Query regional state
        regional_state = await manager.query_state({}, "test_region")
        assert "buildings" in regional_state
        assert "resources.gold" in regional_state
        
        # Query with key pattern
        resource_state = await manager.query_state({"key_pattern": "resource"}, "test_region")
        assert "resources.gold" in resource_state
        assert "buildings" not in resource_state


class TestSnapshotsAndVersioning:
    """Test temporal versioning and snapshot functionality"""
    
    @pytest.mark.asyncio
    async def test_create_snapshot(self, populated_manager):
        """Test snapshot creation"""
        manager = populated_manager
        region_id = "test_region"
        
        snapshot = await manager.create_snapshot(region_id)
        
        assert snapshot.region_id == region_id
        assert isinstance(snapshot.timestamp, datetime)
        assert "buildings" in snapshot.local_state
        assert "resources.gold" in snapshot.local_state
        assert snapshot.global_context  # Should include global context
    
    @pytest.mark.asyncio
    async def test_multiple_snapshots(self, populated_manager):
        """Test creating multiple snapshots over time"""
        manager = populated_manager
        region_id = "test_region"
        
        # Create first snapshot
        snapshot1 = await manager.create_snapshot(region_id)
        
        # Modify state
        await manager.set_state("buildings", 10, region_id)
        await asyncio.sleep(0.01)  # Small delay to ensure different timestamps
        
        # Create second snapshot
        snapshot2 = await manager.create_snapshot(region_id)
        
        assert len(manager.regional_snapshots[region_id]) == 2
        assert snapshot1.local_state["buildings"] == 5
        assert snapshot2.local_state["buildings"] == 10
        assert snapshot2.timestamp > snapshot1.timestamp
    
    @pytest.mark.asyncio
    async def test_rollback_to_snapshot(self, populated_manager):
        """Test rolling back to a previous snapshot"""
        manager = populated_manager
        region_id = "test_region"
        
        # Create snapshot
        snapshot = await manager.create_snapshot(region_id)
        original_buildings = await manager.get_state("buildings", region_id)
        
        # Modify state
        await manager.set_state("buildings", 999, region_id)
        modified_buildings = await manager.get_state("buildings", region_id)
        assert modified_buildings == 999
        
        # Rollback
        success = await manager.rollback_to_snapshot(region_id, snapshot.snapshot_id)
        assert success
        
        # Verify rollback
        current_buildings = await manager.get_state("buildings", region_id)
        assert current_buildings == original_buildings
    
    @pytest.mark.asyncio
    async def test_historical_state_reconstruction(self, populated_manager):
        """Test reconstructing historical state"""
        manager = populated_manager
        region_id = "test_region"
        
        # Create snapshot
        snapshot_time = datetime.utcnow()
        snapshot = await manager.create_snapshot(region_id)
        
        # Make changes after snapshot
        await manager.set_state("buildings", 15, region_id, reason="Expansion")
        await manager.set_state("resources.gold", 750, region_id, reason="Trade profit")
        
        # Reconstruct state at snapshot time
        historical_state = await manager.get_historical_state(region_id, snapshot_time)
        
        assert historical_state is not None
        assert historical_state["regional_state"]["buildings"] == 5
        assert historical_state["regional_state"]["resources.gold"] == 500
        assert historical_state["base_snapshot_id"] == snapshot.snapshot_id


class TestHierarchicalSummarization:
    """Test hierarchical batch summarization functionality"""
    
    @pytest.mark.asyncio
    async def test_summarization_config(self, manager):
        """Test that summarization configuration is properly set"""
        assert SnapshotLevel.DAILY in manager.summarization_schedule
        assert SnapshotLevel.WEEKLY in manager.summarization_schedule
        assert SnapshotLevel.MONTHLY in manager.summarization_schedule
        
        daily_config = manager.summarization_schedule[SnapshotLevel.DAILY]
        assert daily_config['frequency_days'] == 1
        assert daily_config['retention_days'] == 7
    
    @pytest.mark.asyncio
    async def test_significant_change_detection(self, manager):
        """Test detection of significant changes"""
        from backend.systems.world_state.world_types import WorldStateChange, StateChangeType
        
        # Political change (should be significant)
        political_change = WorldStateChange(
            change_type=StateChangeType.UPDATED,
            state_key="faction.control",
            old_value="neutral",
            new_value="hostile",
            category=StateCategory.POLITICAL
        )
        
        # Other change (should not be significant)
        other_change = WorldStateChange(
            change_type=StateChangeType.UPDATED,
            state_key="weather.temperature",
            old_value=20,
            new_value=22,
            category=StateCategory.ENVIRONMENTAL
        )
        
        assert manager._is_significant_change(political_change)
        assert not manager._is_significant_change(other_change)
    
    @pytest.mark.asyncio
    async def test_period_summary_creation(self, populated_manager):
        """Test creating period summaries"""
        manager = populated_manager
        
        # Generate some changes
        now = datetime.utcnow()
        period_start = now - timedelta(days=1)
        period_end = now
        
        # Add changes to history
        from backend.systems.world_state.world_types import WorldStateChange, StateChangeType
        
        changes = [
            WorldStateChange(
                change_type=StateChangeType.UPDATED,
                state_key="test.key1",
                old_value=1,
                new_value=2,
                category=StateCategory.POLITICAL,
                entity_id="test_region",
                timestamp=period_start + timedelta(hours=6)
            ),
            WorldStateChange(
                change_type=StateChangeType.UPDATED,
                state_key="test.key2",
                old_value=10,
                new_value=20,
                category=StateCategory.ECONOMIC,
                entity_id="test_region",
                timestamp=period_start + timedelta(hours=12)
            )
        ]
        
        summary = await manager._create_period_summary(
            "test_region", SnapshotLevel.DAILY, period_start, period_end, changes
        )
        
        assert summary.period_type == "daily"
        assert summary.regions_affected == ["test_region"]
        assert summary.original_change_count == 2
        assert len(summary.key_changes) <= 2  # Might filter some changes
        assert summary.compression_ratio <= 1.0


class TestEventSystem:
    """Test event subscription and triggering"""
    
    @pytest.mark.asyncio
    async def test_event_subscription(self, manager):
        """Test subscribing to events"""
        events_received = []
        
        async def event_handler(data):
            events_received.append(data)
        
        # Subscribe to events
        await manager.subscribe_to_events('state_changed', event_handler)
        
        # Trigger a state change
        await manager.set_state("test.event", "value")
        
        # Wait a bit for async event processing
        await asyncio.sleep(0.01)
        
        assert len(events_received) == 1
        assert events_received[0]['key'] == "test.event"
        assert events_received[0]['new_value'] == "value"
    
    @pytest.mark.asyncio
    async def test_auto_snapshot_on_significant_change(self, manager):
        """Test that significant changes trigger automatic snapshots"""
        region_id = "test_region"
        
        # Make a significant change (political category)
        await manager.set_state(
            "faction.control", "player", region_id, 
            StateCategory.POLITICAL, "Player conquered region"
        )
        
        # Check that snapshot was created
        snapshots = manager.regional_snapshots.get(region_id, [])
        assert len(snapshots) > 0
        
        # Find auto-snapshot
        auto_snapshots = [s for s in snapshots 
                         if s.metadata.get('type') == 'auto_snapshot']
        assert len(auto_snapshots) > 0


class TestPersistence:
    """Test persistence operations"""
    
    @pytest.mark.asyncio
    async def test_save_and_load_state(self, populated_manager):
        """Test saving and loading state"""
        manager = populated_manager
        
        # Save state
        success = await manager.save_to_repository()
        assert success
        
        # Verify data was saved to repository
        repository = manager.repository
        assert 'current' in repository.states
        
        # Create new manager and load state
        WorldStateManager.reset_instance()
        new_manager = await WorldStateManager.get_instance(repository)
        loaded = await new_manager.load_from_repository()
        assert loaded
        
        # Verify loaded state
        population = await new_manager.get_state("global.population")
        assert population == 1000
    
    @pytest.mark.asyncio
    async def test_snapshot_persistence(self, populated_manager):
        """Test snapshot persistence"""
        manager = populated_manager
        region_id = "test_region"
        
        # Create snapshot
        snapshot = await manager.create_snapshot(region_id)
        
        # Verify snapshot was saved to repository
        repository = manager.repository
        assert region_id in repository.snapshots
        assert len(repository.snapshots[region_id]) == 1
        assert repository.snapshots[region_id][0].snapshot_id == snapshot.snapshot_id


class TestBusinessRulesAndValidation:
    """Test business rules and validation logic"""
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, manager):
        """Test thread safety with concurrent access"""
        tasks = []
        
        # Create multiple concurrent tasks
        for i in range(10):
            task = asyncio.create_task(
                manager.set_state(f"concurrent.key{i}", f"value{i}")
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Verify all values were set correctly
        for i in range(10):
            value = await manager.get_state(f"concurrent.key{i}")
            assert value == f"value{i}"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, manager):
        """Test error handling for invalid operations"""
        # Test rollback to non-existent snapshot
        success = await manager.rollback_to_snapshot("nonexistent_region", "fake_id")
        assert not success
        
        # Test getting historical state for non-existent region
        historical = await manager.get_historical_state(
            "nonexistent_region", datetime.utcnow()
        )
        assert historical is None


class TestIntegration:
    """Integration tests for complete workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, manager):
        """Test a complete workflow from creation to summarization"""
        region_id = "integration_test_region"
        
        # 1. Create initial state
        await manager.set_state("population", 100, region_id, StateCategory.SOCIAL)
        await manager.set_state("military.strength", 50, region_id, StateCategory.MILITARY)
        
        # 2. Create snapshot
        snapshot1 = await manager.create_snapshot(region_id)
        
        # 3. Make significant changes
        await manager.set_state("population", 150, region_id, StateCategory.SOCIAL, "Growth")
        await manager.set_state("military.strength", 75, region_id, StateCategory.MILITARY, "Training")
        
        # 4. Create another snapshot
        snapshot2 = await manager.create_snapshot(region_id)
        
        # 5. Test historical reconstruction
        historical = await manager.get_historical_state(region_id, snapshot1.timestamp)
        assert historical["regional_state"]["population"] == 100
        assert historical["regional_state"]["military.strength"] == 50
        
        # 6. Test rollback
        await manager.rollback_to_snapshot(region_id, snapshot1.snapshot_id)
        current_pop = await manager.get_state("population", region_id)
        assert current_pop == 100
        
        # 7. Test summarization
        results = await manager.process_batch_summarization(force=True)
        assert isinstance(results, dict)
    
    @pytest.mark.asyncio
    async def test_tick_processing(self, populated_manager):
        """Test tick processing with effects and summarization"""
        manager = populated_manager
        
        # Add some active effects
        from backend.systems.world_state.world_types import ActiveEffect
        
        # Create an expired effect
        expired_effect = ActiveEffect(
            name="Test Effect",
            effect_type="temporary_bonus",
            target="test_region",
            expires_at=datetime.utcnow() - timedelta(minutes=1)
        )
        
        manager.current_state.active_effects.append(expired_effect)
        
        # Process tick
        await manager.process_tick()
        
        # Verify expired effect was removed
        assert len(manager.current_state.active_effects) == 0


if __name__ == "__main__":
    pytest.main([__file__]) 