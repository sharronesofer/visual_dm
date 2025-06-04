"""
Tests for TensionBusinessService - Pure Business Logic

Tests the core business logic for tension calculations, event processing,
and conflict triggers according to Development Bible standards.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from backend.systems.tension.services.tension_business_service import (
    TensionBusinessService,
    TensionState,
    TensionModifier,
    TensionConfig,
    ConflictTrigger,
    RevoltConfig,
    CalculationConstants,
    TensionConfigRepository,
    TensionRepository,
    FactionService,
    EventDispatcher,
    create_tension_business_service
)
from backend.systems.tension.models.tension_events import TensionEvent, TensionEventType


class TestTensionBusinessService:
    """Test class for TensionBusinessService - pure business logic"""

    @pytest.fixture
    def mock_config_repository(self):
        """Mock configuration repository following Protocol pattern"""
        mock_repo = Mock(spec=TensionConfigRepository)
        
        # Default configuration for city location
        default_config = TensionConfig(
            base_tension=0.2,
            decay_rate=0.05,
            max_tension=1.0,
            min_tension=0.1,
            player_impact=1.5,
            npc_impact=1.0,
            environmental_impact=0.5
        )
        mock_repo.get_location_config.return_value = default_config
        
        # Default event impact configuration
        mock_repo.get_event_impact_config.return_value = {
            'base_impact': 0.15,
            'lethal_modifier': 0.3,
            'stealth_modifier': -0.1
        }
        
        # Default calculation constants
        constants = CalculationConstants(
            high_tension_threshold=0.7,
            event_history_hours=24,
            modifier_expiration_check_hours=1,
            severity_thresholds={'minor': 0.1, 'moderate': 0.3, 'major': 0.6, 'extreme': 1.0},
            revolt_probability={'base_threshold': 0.5, 'faction_modifier_per_faction': 0.1, 'tension_multiplier': 2.0},
            tension_limits={'absolute_min': 0.0, 'absolute_max': 1.0}
        )
        mock_repo.get_calculation_constants.return_value = constants
        
        # Default revolt configuration
        revolt_config = RevoltConfig(
            base_probability_threshold=0.5,
            faction_influence_modifier=0.1,
            duration_range_hours=(24, 72),
            casualty_multiplier=1.0,
            economic_impact_factor=0.3
        )
        mock_repo.get_revolt_config.return_value = revolt_config
        
        # Default conflict triggers
        conflict_triggers = [
            ConflictTrigger(
                name="faction_revolt",
                tension_threshold=0.8,
                duration_hours=48,
                faction_requirements={'min_factions': 2, 'power_imbalance': 0.1},
                probability_modifier=1.0
            )
        ]
        mock_repo.get_conflict_triggers.return_value = conflict_triggers
        
        return mock_repo

    @pytest.fixture
    def mock_tension_repository(self):
        """Mock tension state repository following Protocol pattern"""
        mock_repo = Mock(spec=TensionRepository)
        mock_repo.tension_states = {}
        
        def get_tension_state(region_id: str, poi_id: str) -> Optional[TensionState]:
            return mock_repo.tension_states.get(f"{region_id}:{poi_id}")
        
        def save_tension_state(region_id: str, poi_id: str, state: TensionState) -> None:
            mock_repo.tension_states[f"{region_id}:{poi_id}"] = state
        
        def get_all_tension_states() -> Dict[str, Dict[str, TensionState]]:
            result = {}
            for key, state in mock_repo.tension_states.items():
                region_id, poi_id = key.split(':', 1)
                if region_id not in result:
                    result[region_id] = {}
                result[region_id][poi_id] = state
            return result
        
        mock_repo.get_tension_state.side_effect = get_tension_state
        mock_repo.save_tension_state.side_effect = save_tension_state
        mock_repo.get_all_tension_states.side_effect = get_all_tension_states
        
        return mock_repo

    @pytest.fixture
    def mock_faction_service(self):
        """Mock faction service following Protocol pattern"""
        mock_service = Mock(spec=FactionService)
        mock_service.get_factions_in_region.return_value = [
            {'id': 'faction1', 'power_level': 7, 'member_count': 50},
            {'id': 'faction2', 'power_level': 5, 'member_count': 30}
        ]
        return mock_service

    @pytest.fixture
    def mock_event_dispatcher(self):
        """Mock event dispatcher following Protocol pattern"""
        return Mock(spec=EventDispatcher)

    @pytest.fixture
    def business_service(self, mock_config_repository, mock_tension_repository, mock_faction_service, mock_event_dispatcher):
        """Create TensionBusinessService with mocked dependencies"""
        return TensionBusinessService(
            config_repository=mock_config_repository,
            tension_repository=mock_tension_repository,
            faction_service=mock_faction_service,
            event_dispatcher=mock_event_dispatcher
        )

    def test_factory_function(self, mock_config_repository, mock_tension_repository):
        """Test the factory function creates service correctly"""
        service = create_tension_business_service(
            mock_config_repository,
            mock_tension_repository
        )
        
        assert isinstance(service, TensionBusinessService)
        assert service.config_repository == mock_config_repository
        assert service.tension_repository == mock_tension_repository

    def test_calculate_tension_new_location(self, business_service):
        """Test tension calculation for a new location initializes correctly"""
        current_time = datetime.utcnow()
        
        # Calculate tension for new location
        tension = business_service.calculate_tension("region1", "poi1", current_time)
        
        # Should return base tension for new location (0.2 for city)
        assert tension == 0.2
        assert business_service.stats['total_tension_updates'] == 1

    def test_calculate_tension_with_decay(self, business_service, mock_tension_repository):
        """Test tension calculation applies time-based decay correctly"""
        current_time = datetime.utcnow()
        past_time = current_time - timedelta(hours=2)
        
        # Create existing state with higher tension
        initial_state = TensionState(
            current_level=0.8,
            base_level=0.2,
            last_updated=past_time,
            recent_events=[],
            modifiers={}
        )
        mock_tension_repository.tension_states["region1:poi1"] = initial_state
        
        # Calculate tension (should apply decay)
        tension = business_service.calculate_tension("region1", "poi1", current_time)
        
        # With decay rate 0.05/hour and 2 hours elapsed: 0.8 - (0.05 * 2) = 0.7
        # But clamped to min_tension of 0.1
        expected_tension = max(0.1, 0.8 - (0.05 * 2))
        assert tension == expected_tension

    def test_calculate_tension_with_modifiers(self, business_service, mock_tension_repository):
        """Test tension calculation applies temporary modifiers correctly"""
        current_time = datetime.utcnow()
        future_time = current_time + timedelta(hours=2)
        
        # Create state with active modifier
        modifier = TensionModifier(
            modifier_type="festival_bonus",
            value=-0.2,
            expiration_time=future_time,
            source="test"
        )
        
        initial_state = TensionState(
            current_level=0.6,
            base_level=0.2,
            last_updated=current_time,
            recent_events=[],
            modifiers={"festival_bonus": modifier}
        )
        mock_tension_repository.tension_states["region1:poi1"] = initial_state
        
        # Calculate tension (should apply modifier)
        tension = business_service.calculate_tension("region1", "poi1", current_time)
        
        # 0.6 + (-0.2) = 0.4, but clamped to min_tension 0.1
        assert abs(tension - 0.4) < 0.001  # Use approximate comparison for floating point

    def test_calculate_tension_removes_expired_modifiers(self, business_service, mock_tension_repository):
        """Test tension calculation removes expired modifiers"""
        current_time = datetime.utcnow()
        past_time = current_time - timedelta(hours=1)
        
        # Create state with expired modifier
        expired_modifier = TensionModifier(
            modifier_type="expired_modifier",
            value=0.3,
            expiration_time=past_time,
            source="test"
        )
        
        initial_state = TensionState(
            current_level=0.5,
            base_level=0.2,
            last_updated=current_time,
            recent_events=[],
            modifiers={"expired_modifier": expired_modifier}
        )
        mock_tension_repository.tension_states["region1:poi1"] = initial_state
        
        # Calculate tension
        business_service.calculate_tension("region1", "poi1", current_time)
        
        # Check that expired modifier was removed
        updated_state = mock_tension_repository.tension_states["region1:poi1"]
        assert "expired_modifier" not in updated_state.modifiers
        assert business_service.stats['modifiers_expired'] == 1

    def test_update_tension_from_event_player_combat(self, business_service):
        """Test tension update from player combat event"""
        current_time = datetime.utcnow()
        
        # Update tension from player combat event
        event_data = {'lethal': True, 'stealth': False}
        final_tension = business_service.update_tension_from_event(
            "region1", "poi1", TensionEventType.PLAYER_COMBAT, event_data, current_time
        )
        
        # Should be base tension (0.2) + base_impact (0.15) + lethal_modifier (0.3) = 0.65
        # Affected by player_impact multiplier (1.5): 0.15 * 1.5 + 0.3 * 1.5 = 0.675
        # So final: 0.2 + 0.675 = 0.875, clamped to max 1.0
        assert final_tension > 0.2  # Should be higher than base
        assert final_tension <= 1.0  # Should not exceed max

    def test_update_tension_from_event_string_conversion(self, business_service):
        """Test tension update handles string event types correctly"""
        current_time = datetime.utcnow()
        
        # Update tension using string event type
        event_data = {'lethal': False}
        final_tension = business_service.update_tension_from_event(
            "region1", "poi1", "player_combat", event_data, current_time
        )
        
        # Should successfully convert string to enum and process
        assert final_tension > 0.2  # Should be higher than base tension

    def test_check_conflict_triggers_high_tension(self, business_service, mock_tension_repository):
        """Test conflict trigger detection when tension is high"""
        current_time = datetime.utcnow()
        
        # Set up high tension state
        high_tension_state = TensionState(
            current_level=0.85,  # Above faction_revolt threshold of 0.8
            base_level=0.2,
            last_updated=current_time,
            recent_events=[],
            modifiers={}
        )
        mock_tension_repository.tension_states["region1:poi1"] = high_tension_state
        
        # Check for conflict triggers
        conflicts = business_service.check_conflict_triggers("region1", current_time)
        
        # Should detect at least one conflict trigger
        assert len(conflicts) > 0
        conflict = conflicts[0]
        assert conflict['trigger_name'] == 'faction_revolt'
        assert conflict['triggered'] is True

    def test_get_regions_by_tension_filters_correctly(self, business_service, mock_tension_repository):
        """Test filtering regions by tension level"""
        current_time = datetime.utcnow()
        
        # Set up multiple regions with different tension levels
        states = {
            "region1:poi1": TensionState(0.3, 0.2, current_time, [], {}),  # Low tension
            "region1:poi2": TensionState(0.8, 0.2, current_time, [], {}),  # High tension
            "region2:poi1": TensionState(0.5, 0.2, current_time, [], {}),  # Medium tension
        }
        mock_tension_repository.tension_states.update(states)
        
        # Filter for high tension regions (0.7-1.0)
        high_tension_regions = business_service.get_regions_by_tension(0.7, 1.0, current_time)
        
        # Should find region1 (has poi2 with 0.8 tension)
        assert len(high_tension_regions) == 1
        assert high_tension_regions[0]['region_id'] == 'region1'

    def test_add_tension_modifier(self, business_service):
        """Test adding temporary tension modifier"""
        # Add a festival modifier
        business_service.add_tension_modifier(
            "region1", "poi1", "festival", -0.2, 24.0, "test_festival"
        )
        
        # Calculate tension to verify modifier is applied
        current_time = datetime.utcnow()
        tension = business_service.calculate_tension("region1", "poi1", current_time)
        
        # Base tension (0.2) + modifier (-0.2) = 0.0, but clamped to min (0.1)
        assert tension == 0.1

    def test_decay_all_tension_processes_all_regions(self, business_service, mock_tension_repository):
        """Test global tension decay processes all regions"""
        current_time = datetime.utcnow()
        
        # Set up multiple regions
        states = {
            "region1:poi1": TensionState(0.8, 0.2, current_time, [], {}),
            "region1:poi2": TensionState(0.7, 0.2, current_time, [], {}),
            "region2:poi1": TensionState(0.9, 0.2, current_time, [], {}),
        }
        mock_tension_repository.tension_states.update(states)
        
        # Run global decay
        stats = business_service.decay_all_tension(current_time)
        
        # Should process all regions and POIs
        assert stats['regions_processed'] == 2  # region1, region2
        assert stats['pois_processed'] == 3     # 3 total POIs

    def test_calculate_faction_power_score(self, business_service):
        """Test faction power calculation for tension context"""
        faction_data = {
            'power_level': 8.0,
            'member_count': 150,
            'territory_control': 0.4
        }
        
        power_score = business_service.calculate_faction_power_score(faction_data)
        
        # Should return a reasonable power score
        assert isinstance(power_score, float)
        assert 0.0 <= power_score <= 10.0

    def test_business_logic_isolation(self, business_service):
        """Test that business service doesn't perform I/O operations directly"""
        # This test verifies that the business service follows pure business logic principles
        # by ensuring it only interacts through the provided repository protocols
        
        # The service should only interact with its injected dependencies
        assert hasattr(business_service, 'config_repository')
        assert hasattr(business_service, 'tension_repository')
        assert hasattr(business_service, 'faction_service')
        assert hasattr(business_service, 'event_dispatcher')
        
        # All methods should be synchronous (pure business logic)
        import inspect
        service_methods = [method for method in dir(business_service) 
                          if not method.startswith('_') and callable(getattr(business_service, method))]
        
        for method_name in service_methods:
            method = getattr(business_service, method_name)
            if callable(method):
                # Should not be async (pure business logic should be synchronous)
                assert not inspect.iscoroutinefunction(method), f"Method {method_name} should not be async"

    def test_stats_tracking(self, business_service):
        """Test that business service tracks statistics correctly"""
        current_time = datetime.utcnow()
        
        # Initial stats
        initial_updates = business_service.stats['total_tension_updates']
        
        # Perform operations
        business_service.calculate_tension("region1", "poi1", current_time)
        business_service.calculate_tension("region1", "poi2", current_time)
        
        # Stats should be updated
        assert business_service.stats['total_tension_updates'] == initial_updates + 2
        assert 'last_global_update' in business_service.stats


class TestTensionDomainModels:
    """Test tension domain models for correct behavior"""

    def test_tension_modifier_creation(self):
        """Test TensionModifier creation and attributes"""
        expiration = datetime.utcnow() + timedelta(hours=2)
        modifier = TensionModifier(
            modifier_type="festival",
            value=-0.3,
            expiration_time=expiration,
            source="annual_harvest"
        )
        
        assert modifier.modifier_type == "festival"
        assert modifier.value == -0.3
        assert modifier.expiration_time == expiration
        assert modifier.source == "annual_harvest"

    def test_tension_state_creation(self):
        """Test TensionState creation and attributes"""
        current_time = datetime.utcnow()
        state = TensionState(
            current_level=0.6,
            base_level=0.2,
            last_updated=current_time,
            recent_events=[],
            modifiers={}
        )
        
        assert state.current_level == 0.6
        assert state.base_level == 0.2
        assert state.last_updated == current_time
        assert isinstance(state.recent_events, list)
        assert isinstance(state.modifiers, dict)

    def test_tension_config_creation(self):
        """Test TensionConfig creation and attributes"""
        config = TensionConfig(
            base_tension=0.2,
            decay_rate=0.05,
            max_tension=1.0,
            min_tension=0.1,
            player_impact=1.5,
            npc_impact=1.0,
            environmental_impact=0.5
        )
        
        assert config.base_tension == 0.2
        assert config.decay_rate == 0.05
        assert config.max_tension == 1.0
        assert config.min_tension == 0.1
        assert config.player_impact == 1.5

    def test_conflict_trigger_creation(self):
        """Test ConflictTrigger creation and attributes"""
        trigger = ConflictTrigger(
            name="faction_revolt",
            tension_threshold=0.8,
            duration_hours=48,
            faction_requirements={'min_factions': 2},
            probability_modifier=1.0
        )
        
        assert trigger.name == "faction_revolt"
        assert trigger.tension_threshold == 0.8
        assert trigger.duration_hours == 48
        assert isinstance(trigger.faction_requirements, dict)
        assert trigger.probability_modifier == 1.0 