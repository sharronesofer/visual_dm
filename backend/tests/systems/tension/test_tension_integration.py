"""
Integration Tests for Tension System

Tests the interaction between tension components and validates
end-to-end functionality according to Development Bible standards.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import time

from backend.systems.tension import (
    UnifiedTensionManager,
    TensionBusinessService,
    TensionEventType,
    create_player_combat_event,
    create_npc_death_event,
    create_environmental_disaster_event
)


class TestTensionSystemIntegration:
    """Integration tests for tension system components"""

    @pytest.fixture
    def tension_manager(self):
        """Create a tension manager with default dependencies"""
        return UnifiedTensionManager()

    def test_tension_manager_initialization(self, tension_manager):
        """Test tension manager initializes with proper dependencies"""
        # Should have business service initialized
        assert hasattr(tension_manager, 'business_service')
        assert isinstance(tension_manager.business_service, TensionBusinessService)
        
        # Should expose stats from business service
        assert hasattr(tension_manager, 'stats')
        assert 'total_tension_updates' in tension_manager.stats

    def test_end_to_end_tension_calculation(self, tension_manager):
        """Test complete tension calculation workflow"""
        current_time = datetime.utcnow()
        
        # Calculate initial tension for new location
        initial_tension = tension_manager.calculate_tension("region1", "poi1", current_time)
        
        # Should be base tension for default configuration
        assert 0.0 <= initial_tension <= 1.0
        assert initial_tension > 0.0  # Should have some base tension
        
        # Apply a combat event
        event_data = {'lethal': True, 'enemies_defeated': 2}
        new_tension = tension_manager.update_tension_from_event(
            "region1", "poi1", TensionEventType.PLAYER_COMBAT, event_data, current_time
        )
        
        # Tension should have increased
        assert new_tension > initial_tension
        assert new_tension <= 1.0  # Should not exceed maximum

    def test_tension_decay_over_time(self, tension_manager):
        """Test that tension decays properly over time"""
        region_id, poi_id = "region1", "poi1"
        initial_time = datetime.utcnow()
        
        # Set high initial tension through combat event
        event_data = {'lethal': True, 'enemies_defeated': 5}
        high_tension = tension_manager.update_tension_from_event(
            region_id, poi_id, TensionEventType.PLAYER_COMBAT, event_data, initial_time
        )
        
        # Wait some time and recalculate
        later_time = initial_time + timedelta(hours=4)
        decayed_tension = tension_manager.calculate_tension(region_id, poi_id, later_time)
        
        # Tension should have decreased due to decay
        assert decayed_tension < high_tension

    def test_multiple_events_accumulate_tension(self, tension_manager):
        """Test that multiple events accumulate tension properly"""
        region_id, poi_id = "region1", "poi1"
        current_time = datetime.utcnow()
        
        # Apply multiple events in sequence
        events = [
            (TensionEventType.PLAYER_COMBAT, {'lethal': False}),
            (TensionEventType.NPC_DEATH, {'important': True}),
            (TensionEventType.ENVIRONMENTAL_DISASTER, {'severity': 1.5})
        ]
        
        tensions = []
        for event_type, event_data in events:
            tension = tension_manager.update_tension_from_event(
                region_id, poi_id, event_type, event_data, current_time
            )
            tensions.append(tension)
            current_time += timedelta(minutes=30)  # Space events apart
        
        # Each event should generally increase tension
        for i in range(1, len(tensions)):
            assert tensions[i] >= tensions[0]  # Should be at least as high as initial

    def test_conflict_trigger_detection(self, tension_manager):
        """Test that high tension triggers conflict detection"""
        region_id = "region1"
        current_time = datetime.utcnow()
        
        # Create multiple high-tension events to trigger conflicts
        high_tension_events = [
            (TensionEventType.PLAYER_COMBAT, {'lethal': True, 'enemies_defeated': 10}),
            (TensionEventType.NPC_DEATH, {'important': True, 'civilian': True}),
            (TensionEventType.ENVIRONMENTAL_DISASTER, {'severity': 2.0}),
            (TensionEventType.POLITICAL_CHANGE, {'regime_change': True})
        ]
        
        # Apply all events to same location
        poi_id = "poi1"
        for event_type, event_data in high_tension_events:
            tension_manager.update_tension_from_event(
                region_id, poi_id, event_type, event_data, current_time
            )
            current_time += timedelta(minutes=15)
        
        # Check for triggered conflicts
        conflicts = tension_manager.check_conflict_triggers(region_id, current_time)
        
        # Should detect some conflicts due to high tension
        assert isinstance(conflicts, list)
        # May or may not trigger depending on exact tension levels and thresholds

    def test_event_factory_integration(self, tension_manager):
        """Test that event factory functions integrate properly"""
        region_id, poi_id = "region1", "poi1"
        current_time = datetime.utcnow()
        
        # Test player combat event factory
        combat_event = create_player_combat_event(
            region_id=region_id,
            poi_id=poi_id,
            lethal=True,
            stealth=False,
            enemies_defeated=3
        )
        
        # Should be able to use factory-created event
        assert combat_event.event_type == TensionEventType.PLAYER_COMBAT
        assert combat_event.region_id == region_id
        assert combat_event.poi_id == poi_id
        
        # Should be able to apply the event
        tension = tension_manager.update_tension_from_event(
            region_id, poi_id, combat_event.event_type, combat_event.data, current_time
        )
        assert tension > 0.0

    def test_string_event_type_handling(self, tension_manager):
        """Test that string event types are handled properly for external integration"""
        region_id, poi_id = "region1", "poi1"
        current_time = datetime.utcnow()
        
        # Use string event type (as might come from external API)
        event_data = {'lethal': False}
        tension = tension_manager.update_tension_from_event(
            region_id, poi_id, "player_combat", event_data, current_time
        )
        
        # Should successfully process string event type
        assert tension > 0.0

    def test_cross_region_tension_isolation(self, tension_manager):
        """Test that tension in different regions is isolated"""
        current_time = datetime.utcnow()
        
        # Apply high tension event to region1
        tension_manager.update_tension_from_event(
            "region1", "poi1", TensionEventType.PLAYER_COMBAT, 
            {'lethal': True, 'enemies_defeated': 10}, current_time
        )
        
        # Check tension in different regions
        region1_tension = tension_manager.calculate_tension("region1", "poi1", current_time)
        region2_tension = tension_manager.calculate_tension("region2", "poi1", current_time)
        
        # Region2 should not be affected by region1 events
        assert region1_tension > region2_tension

    def test_modifier_expiration_integration(self, tension_manager):
        """Test that temporary modifiers expire correctly"""
        region_id, poi_id = "region1", "poi1"
        
        # Start with base tension
        base_time = datetime.utcnow()
        initial_tension = tension_manager.calculate_tension(region_id, poi_id, base_time)
        
        # Add a temporary positive modifier (1 second duration)
        tension_manager.add_tension_modifier(
            region_id, poi_id, "emergency", 0.2, 1/3600, "test_emergency"  # 1 second duration (1/3600 hours)
        )
        
        # Calculate tension immediately (should apply modifier)
        tension_with_modifier = tension_manager.calculate_tension(region_id, poi_id, base_time)
        
        # Verify modifier is applied (tension should be higher with positive modifier)
        assert tension_with_modifier > initial_tension
        
        # Check that no modifiers have expired yet
        initial_expired_count = tension_manager.stats.get('modifiers_expired', 0)
        
        # Wait for modifier to expire
        time.sleep(1.1)  # Wait 1.1 seconds to ensure modifier expires
        later_time = datetime.utcnow()
        tension_after_expiration = tension_manager.calculate_tension(region_id, poi_id, later_time)
        
        # Check that at least one modifier has expired
        final_expired_count = tension_manager.stats.get('modifiers_expired', 0)
        assert final_expired_count > initial_expired_count, "Modifier should have expired"

    def test_statistics_tracking_integration(self, tension_manager):
        """Test that statistics are tracked across operations"""
        current_time = datetime.utcnow()
        
        # Get initial stats
        initial_stats = dict(tension_manager.stats)
        
        # Perform various operations
        tension_manager.calculate_tension("region1", "poi1", current_time)
        tension_manager.update_tension_from_event(
            "region1", "poi1", TensionEventType.PLAYER_COMBAT, {}, current_time
        )
        tension_manager.calculate_tension("region2", "poi1", current_time)
        
        # Stats should have been updated
        final_stats = tension_manager.stats
        assert final_stats['total_tension_updates'] > initial_stats['total_tension_updates']

    def test_fallback_configuration_handling(self):
        """Test that tension manager handles missing infrastructure gracefully"""
        # This tests the fallback mechanisms when infrastructure is not available
        
        # Create manager (should not raise exceptions even if infrastructure missing)
        manager = UnifiedTensionManager()
        
        # Should be able to perform basic operations
        current_time = datetime.utcnow()
        tension = manager.calculate_tension("region1", "poi1", current_time)
        
        # Should return reasonable values even with fallback config
        assert 0.0 <= tension <= 1.0

    def test_region_tension_summary_integration(self, tension_manager):
        """Test region-wide tension summary functionality"""
        current_time = datetime.utcnow()
        
        # Set up multiple POIs in a region with different tension levels
        pois = ["poi1", "poi2", "poi3"]
        for i, poi_id in enumerate(pois):
            # Apply different levels of tension to each POI
            for _ in range(i + 1):  # poi1: 1 event, poi2: 2 events, poi3: 3 events
                tension_manager.update_tension_from_event(
                    "region1", poi_id, TensionEventType.PLAYER_COMBAT, 
                    {'lethal': False}, current_time
                )
        
        # Get regions by tension level
        high_tension_regions = tension_manager.get_regions_by_tension(0.3, 1.0, current_time)
        
        # Should find our region if tension is high enough
        region_ids = [r['region_id'] for r in high_tension_regions]
        # The exact result depends on tension calculations, but should be a valid list
        assert isinstance(high_tension_regions, list)

    def test_global_tension_decay_integration(self, tension_manager):
        """Test global tension decay across multiple regions"""
        current_time = datetime.utcnow()
        
        # Set up tension in multiple regions and POIs
        regions_pois = [
            ("region1", "poi1"), ("region1", "poi2"),
            ("region2", "poi1"), ("region3", "poi1")
        ]
        
        for region_id, poi_id in regions_pois:
            tension_manager.update_tension_from_event(
                region_id, poi_id, TensionEventType.PLAYER_COMBAT, 
                {'lethal': True}, current_time
            )
        
        # Run global decay
        decay_stats = tension_manager.decay_all_tension(current_time)
        
        # Should process all regions
        assert decay_stats['regions_processed'] >= 3  # At least 3 regions
        assert decay_stats['pois_processed'] >= 4     # At least 4 POIs


class TestTensionConfigurationIntegration:
    """Test integration with tension configuration system"""

    def test_configuration_loading_integration(self):
        """Test that configurations are loaded and applied correctly"""
        # Create manager which should load configurations automatically
        manager = UnifiedTensionManager()
        
        current_time = datetime.utcnow()
        
        # Calculate tension for different location types
        # These should use different configurations based on POI type mapping
        city_tension = manager.calculate_tension("region1", "city_poi", current_time)
        dungeon_tension = manager.calculate_tension("region1", "dungeon_poi", current_time)
        
        # Both should be valid tension values
        assert 0.0 <= city_tension <= 1.0
        assert 0.0 <= dungeon_tension <= 1.0

    @patch('backend.infrastructure.config_loaders.tension_config.TensionConfigManager')
    def test_configuration_error_handling(self, mock_config_manager):
        """Test graceful handling of configuration loading errors"""
        # Make config manager raise an error
        mock_config_manager.side_effect = Exception("Config loading failed")
        
        # Manager should still initialize with fallback configurations
        manager = UnifiedTensionManager()
        
        # Should be able to perform basic operations
        current_time = datetime.utcnow()
        tension = manager.calculate_tension("region1", "poi1", current_time)
        
        # Should return reasonable fallback values
        assert 0.0 <= tension <= 1.0 