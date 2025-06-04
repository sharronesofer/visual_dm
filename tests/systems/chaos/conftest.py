"""
Pytest configuration for Chaos System tests

Provides common fixtures, test configuration, and setup for all chaos system tests.
"""

import pytest
import asyncio
import logging
from unittest.mock import Mock, AsyncMock
from pathlib import Path

from backend.systems.chaos.core.config import ChaosConfig


# Configure logging for tests
logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Create a test-optimized chaos configuration"""
    config = ChaosConfig()
    
    # Faster intervals for testing
    config.system_config.health_check_interval = 0.1
    config.system_config.performance_metrics_window = 10
    config.system_config.max_error_history = 50
    
    # Faster warning durations
    config.warning_config.rumor_duration_hours = 0.001
    config.warning_config.early_warning_duration_hours = 0.001
    config.warning_config.imminent_duration_hours = 0.001
    config.warning_config.escalation_probability = 0.8
    
    # Faster narrative analysis
    config.narrative_config.analysis_interval_seconds = 0.1
    config.narrative_config.history_retention_hours = 1.0
    config.narrative_config.tension_decay_rate = 0.1
    config.narrative_config.engagement_update_threshold = 0.05
    
    # Simplified event types for testing
    config.event_config.event_types = [
        "economic_crisis",
        "political_upheaval", 
        "social_unrest",
        "environmental_disaster",
        "diplomatic_crisis",
        "temporal_anomaly"
    ]
    
    return config


@pytest.fixture
def mock_external_systems():
    """Create mocks for external systems that chaos system integrates with"""
    return {
        'faction_system': AsyncMock(),
        'economic_system': AsyncMock(),
        'political_system': AsyncMock(),
        'social_system': AsyncMock(),
        'environmental_system': AsyncMock(),
        'diplomatic_system': AsyncMock(),
        'temporal_system': AsyncMock()
    }


@pytest.fixture
def sample_pressure_data():
    """Create sample pressure data for testing"""
    return {
        'economic': 0.5,
        'political': 0.4,
        'social': 0.3,
        'environmental': 0.2,
        'diplomatic': 0.6,
        'temporal': 0.1
    }


@pytest.fixture
def sample_narrative_context():
    """Create sample narrative context for testing"""
    return {
        'current_story_beats': ['exposition', 'rising_action'],
        'dramatic_tension_level': 0.6,
        'recent_major_events': ['economic_downturn'],
        'narrative_themes': ['political_intrigue', 'economic_drama'],
        'player_engagement_level': 0.7,
        'active_storylines': ['faction_conflict', 'trade_war']
    }


@pytest.fixture
def sample_cascade_data():
    """Create sample cascade relationship data for testing"""
    return {
        'economic_crisis': {
            'probability': 0.7,
            'targets': ['social_unrest', 'political_instability'],
            'delay_hours': 0.5,
            'severity_multiplier': 0.8
        },
        'political_upheaval': {
            'probability': 0.6,
            'targets': ['diplomatic_crisis', 'social_unrest'],
            'delay_hours': 1.0,
            'severity_multiplier': 0.9
        },
        'social_unrest': {
            'probability': 0.5,
            'targets': ['political_upheaval'],
            'delay_hours': 2.0,
            'severity_multiplier': 0.6
        }
    }


@pytest.fixture
def sample_warning_sequence():
    """Create sample warning escalation sequence for testing"""
    return [
        {
            'phase': 'rumor',
            'duration_hours': 0.001,
            'escalation_probability': 0.8,
            'description': 'Rumors of potential crisis'
        },
        {
            'phase': 'early_warning',
            'duration_hours': 0.001,
            'escalation_probability': 0.9,
            'description': 'Early warning signs detected'
        },
        {
            'phase': 'imminent',
            'duration_hours': 0.001,
            'escalation_probability': 1.0,
            'description': 'Crisis is imminent'
        }
    ]


@pytest.fixture
def sample_narrative_themes():
    """Create sample narrative themes for testing"""
    return {
        'political_intrigue': {
            'name': 'Political Intrigue',
            'description': 'Complex political maneuvering and power struggles',
            'priority': 'central',
            'weight_modifier': 1.5,
            'related_events': ['political_upheaval', 'faction_conflict'],
            'duration_hours': 48.0
        },
        'economic_drama': {
            'name': 'Economic Drama',
            'description': 'Financial crises and economic upheaval',
            'priority': 'supporting',
            'weight_modifier': 1.2,
            'related_events': ['economic_crisis', 'market_crash'],
            'duration_hours': 24.0
        },
        'social_movement': {
            'name': 'Social Movement',
            'description': 'Popular movements and social change',
            'priority': 'background',
            'weight_modifier': 1.0,
            'related_events': ['social_unrest', 'protest'],
            'duration_hours': 12.0
        }
    }


@pytest.fixture
def sample_event_data():
    """Create sample event data for testing"""
    return {
        'economic_crisis': {
            'base_severity': 0.7,
            'duration_hours': 6.0,
            'pressure_impact': {
                'economic': 0.8,
                'political': 0.3,
                'social': 0.4
            },
            'narrative_weight': 1.5,
            'cascade_potential': 0.8
        },
        'political_upheaval': {
            'base_severity': 0.8,
            'duration_hours': 8.0,
            'pressure_impact': {
                'political': 0.9,
                'social': 0.5,
                'diplomatic': 0.6
            },
            'narrative_weight': 1.8,
            'cascade_potential': 0.7
        },
        'temporal_anomaly': {
            'base_severity': 0.6,
            'duration_hours': 2.0,
            'pressure_impact': {
                'temporal': 0.9,
                'environmental': 0.3
            },
            'narrative_weight': 2.0,
            'cascade_potential': 0.5
        }
    }


# Test markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "bible_compliance: mark test as Bible compliance test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Async test configuration
@pytest.fixture(autouse=True)
def setup_async_test_environment():
    """Set up async test environment"""
    # Ensure clean async environment for each test
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # Clean up any pending tasks
            pending = asyncio.all_tasks(loop)
            if pending:
                for task in pending:
                    if not task.done():
                        task.cancel()
    except RuntimeError:
        pass  # No running loop, which is fine
    
    yield
    
    # Cleanup after test
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # Clean up any pending tasks created during test
            pending = asyncio.all_tasks(loop)
            if pending:
                for task in pending:
                    if not task.done():
                        task.cancel()
    except RuntimeError:
        pass  # No running loop, which is fine


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary directory for test data"""
    data_dir = tmp_path / "chaos_test_data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def mock_file_system(temp_data_dir):
    """Create a mock file system for testing data persistence"""
    return {
        'config_file': temp_data_dir / "config.json",
        'pressure_data': temp_data_dir / "pressure_sources.json",
        'event_history': temp_data_dir / "event_history.json",
        'narrative_state': temp_data_dir / "narrative_state.json"
    }


# Helper functions available to all tests
class ChaosTestHelper:
    """Helper class for common chaos system test operations"""
    
    @staticmethod
    def create_mock_component(component_type: str):
        """Create a mock component with standard async methods"""
        mock = AsyncMock()
        mock.initialize = AsyncMock()
        mock.start = AsyncMock()
        mock.stop = AsyncMock()
        mock.pause = AsyncMock()
        mock.resume = AsyncMock()
        mock.get_system_status = AsyncMock(return_value={'status': 'running', 'component_type': component_type})
        mock.update_config = AsyncMock()
        return mock
    
    @staticmethod
    def assert_bible_compliance(system_status):
        """Assert that system meets Development Bible compliance requirements"""
        assert 'chaos_engine' in system_status['components']
        assert 'pressure_monitor' in system_status['components']
        assert 'warning_system' in system_status['components']
        assert 'narrative_moderator' in system_status['components']
        assert 'cascade_engine' in system_status['components']
    
    @staticmethod
    def assert_temporal_pressure_support(pressure_data):
        """Assert that temporal pressure is properly supported"""
        assert 'temporal' in pressure_data
        assert isinstance(pressure_data['temporal'], (int, float))
        assert 0.0 <= pressure_data['temporal'] <= 1.0
    
    @staticmethod
    def assert_three_tier_warnings(warning_sequence):
        """Assert that three-tier warning system is implemented"""
        phases = [w['phase'] for w in warning_sequence]
        assert 'rumor' in phases or 'RUMOR' in phases
        assert 'early_warning' in phases or 'EARLY_WARNING' in phases
        assert 'imminent' in phases or 'IMMINENT' in phases


@pytest.fixture
def chaos_test_helper():
    """Provide the test helper class"""
    return ChaosTestHelper


# Performance testing configuration
@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for testing"""
    return {
        'event_processing_max_seconds': 0.5,
        'health_check_max_seconds': 0.1,
        'status_update_max_seconds': 0.2,
        'narrative_update_max_seconds': 0.3,
        'cascade_processing_max_seconds': 1.0,
        'system_startup_max_seconds': 5.0,
        'system_shutdown_max_seconds': 2.0
    }


# Error simulation utilities
@pytest.fixture
def error_simulator():
    """Provide utilities for simulating various error conditions"""
    class ErrorSimulator:
        @staticmethod
        def create_connection_error():
            from backend.systems.chaos.core.exceptions import ComponentConnectionError
            return ComponentConnectionError("Simulated connection failure")
        
        @staticmethod
        def create_initialization_error():
            from backend.systems.chaos.core.exceptions import ChaosInitializationError
            return ChaosInitializationError("Simulated initialization failure")
        
        @staticmethod
        def create_system_error():
            from backend.systems.chaos.core.exceptions import ChaosSystemError
            return ChaosSystemError("Simulated system error")
        
        @staticmethod
        def create_intermittent_failure(success_count=2, failure_count=1):
            """Create a callable that fails intermittently"""
            call_count = 0
            
            def failing_method(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count % (success_count + failure_count) <= success_count:
                    return {"status": "success"}
                else:
                    raise Exception("Intermittent failure")
            
            return failing_method
    
    return ErrorSimulator 