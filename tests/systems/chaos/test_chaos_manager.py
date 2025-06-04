"""
Unit tests for the Chaos Manager

Tests the consolidated ChaosManager that serves as the single coordination point 
for all chaos subsystems as required by the Development Bible.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from backend.systems.chaos.core.chaos_manager import (
    ChaosManager, SystemStatus, ChaosSystemStatus
)
from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.core.exceptions import (
    ChaosSystemError
)

# Define ComponentHealth constants for tests
class ComponentHealth:
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


@pytest.fixture
def chaos_config():
    """Create a test chaos configuration"""
    config = ChaosConfig()
    return config


@pytest.fixture
def chaos_manager(chaos_config):
    """Create a chaos manager for testing"""
    return ChaosManager(chaos_config)


@pytest.fixture
def mock_chaos_engine():
    """Create a mock chaos engine"""
    mock_engine = AsyncMock()
    mock_engine.initialize = AsyncMock()
    mock_engine.start = AsyncMock()
    mock_engine.stop = AsyncMock()
    mock_engine.pause = AsyncMock()
    mock_engine.resume = AsyncMock()
    mock_engine.get_system_status = AsyncMock(return_value={'status': 'running'})
    mock_engine.process_event = AsyncMock()
    return mock_engine


@pytest.fixture
def mock_pressure_monitor():
    """Create a mock pressure monitor"""
    mock_monitor = AsyncMock()
    mock_monitor.initialize = AsyncMock()
    mock_monitor.start = AsyncMock()
    mock_monitor.stop = AsyncMock()
    mock_monitor.pause = AsyncMock()
    mock_monitor.resume = AsyncMock()
    mock_monitor.get_current_pressures = AsyncMock(return_value={'political': 0.5})
    mock_monitor.get_system_status = AsyncMock(return_value={'status': 'monitoring'})
    return mock_monitor


@pytest.fixture
def mock_warning_system():
    """Create a mock warning system"""
    mock_warnings = AsyncMock()
    mock_warnings.initialize = AsyncMock()
    mock_warnings.start = AsyncMock()
    mock_warnings.stop = AsyncMock()
    mock_warnings.pause = AsyncMock()
    mock_warnings.resume = AsyncMock()
    mock_warnings.get_active_warnings = AsyncMock(return_value=[])
    mock_warnings.get_system_status = AsyncMock(return_value={'status': 'ready'})
    return mock_warnings


@pytest.fixture
def mock_narrative_moderator():
    """Create a mock narrative moderator"""
    mock_moderator = AsyncMock()
    mock_moderator.initialize = AsyncMock()
    mock_moderator.start = AsyncMock()
    mock_moderator.stop = AsyncMock()
    mock_moderator.pause = AsyncMock()
    mock_moderator.resume = AsyncMock()
    mock_moderator.get_narrative_status = AsyncMock(return_value={'tension': 0.5})
    return mock_moderator


@pytest.fixture
def mock_cascade_engine():
    """Create a mock cascade engine"""
    mock_cascade = AsyncMock()
    mock_cascade.initialize = AsyncMock()
    mock_cascade.start = AsyncMock()
    mock_cascade.stop = AsyncMock()
    mock_cascade.pause = AsyncMock()
    mock_cascade.resume = AsyncMock()
    mock_cascade.get_active_cascades = AsyncMock(return_value=[])
    return mock_cascade


class TestChaosManagerInitialization:
    """Test chaos manager initialization and configuration"""
    
    def test_chaos_manager_creation(self, chaos_config):
        """Test that chaos manager can be created with proper defaults"""
        manager = ChaosManager(chaos_config)
        
        assert manager.config is chaos_config
        assert manager.status == ChaosSystemStatus.STOPPED
        assert not manager._initialized
        assert manager.chaos_engine is None
        assert manager.pressure_monitor is None
        assert manager.warning_system is None
        assert manager.narrative_moderator is None
        assert manager.cascade_engine is None
        assert len(manager.error_history) == 0
        assert len(manager.performance_metrics) == 0
    
    @pytest.mark.asyncio
    async def test_initialization_creates_components(self, chaos_manager):
        """Test that initialization creates all required components"""
        await chaos_manager.initialize()
        
        assert chaos_manager._initialized
        assert chaos_manager.chaos_engine is not None
        assert chaos_manager.pressure_monitor is not None
        assert chaos_manager.warning_system is not None
        assert chaos_manager.narrative_moderator is not None
        assert chaos_manager.cascade_engine is not None
        
        # All components should be initialized
        assert hasattr(chaos_manager.chaos_engine, '_initialized')
        assert hasattr(chaos_manager.pressure_monitor, '_initialized')
        assert hasattr(chaos_manager.warning_system, '_initialized')
        assert hasattr(chaos_manager.narrative_moderator, '_initialized')
        assert hasattr(chaos_manager.cascade_engine, '_initialized')
    
    @pytest.mark.asyncio
    async def test_initialization_failure_cleanup(self, chaos_manager):
        """Test that initialization failure cleans up partially created components"""
        # Mock one component to fail initialization
        with patch('backend.systems.chaos.core.chaos_engine.ChaosEngine') as mock_engine_class:
            mock_engine_class.return_value.initialize.side_effect = ChaosSystemError("Test failure")
            
            with pytest.raises(ChaosSystemError):
                await chaos_manager.initialize()
            
            # Should not be marked as initialized
            assert not chaos_manager._initialized
            assert chaos_manager.status == ChaosSystemStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_double_initialization_prevention(self, chaos_manager):
        """Test that multiple initialization calls are handled gracefully"""
        await chaos_manager.initialize()
        assert chaos_manager._initialized
        
        # Second initialization should not cause issues
        await chaos_manager.initialize()
        assert chaos_manager._initialized


class TestChaosManagerLifecycle:
    """Test chaos manager lifecycle management"""
    
    @pytest.mark.asyncio
    async def test_start_system(self, chaos_manager):
        """Test starting the chaos system"""
        await chaos_manager.initialize()
        
        assert chaos_manager.status == ChaosSystemStatus.STOPPED
        
        await chaos_manager.start()
        
        assert chaos_manager.status == ChaosSystemStatus.RUNNING
        assert chaos_manager.start_time is not None
    
    @pytest.mark.asyncio
    async def test_stop_system(self, chaos_manager):
        """Test stopping the chaos system"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        assert chaos_manager.status == ChaosSystemStatus.RUNNING
        
        await chaos_manager.stop()
        
        assert chaos_manager.status == ChaosSystemStatus.STOPPED
        assert chaos_manager.start_time is None
    
    @pytest.mark.asyncio
    async def test_pause_resume_system(self, chaos_manager):
        """Test pausing and resuming the chaos system"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        assert chaos_manager.status == ChaosSystemStatus.RUNNING
        
        await chaos_manager.pause()
        assert chaos_manager.status == ChaosSystemStatus.PAUSED
        
        await chaos_manager.resume()
        assert chaos_manager.status == ChaosSystemStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_start_without_initialization_fails(self, chaos_manager):
        """Test that starting without initialization raises error"""
        with pytest.raises(ChaosSystemError):
            await chaos_manager.start()
    
    @pytest.mark.asyncio
    async def test_restart_system(self, chaos_manager):
        """Test restarting the chaos system"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        old_start_time = chaos_manager.start_time
        
        await chaos_manager.restart()
        
        assert chaos_manager.status == ChaosSystemStatus.RUNNING
        assert chaos_manager.start_time != old_start_time
    
    @pytest.mark.asyncio
    async def test_component_failure_handling(self, chaos_manager):
        """Test handling of component failures during lifecycle operations"""
        await chaos_manager.initialize()
        
        # Mock a component to fail during start
        chaos_manager.chaos_engine.start.side_effect = ChaosSystemError("Engine failed")
        
        with pytest.raises(ChaosSystemError):
            await chaos_manager.start()
        
        assert chaos_manager.status == ChaosSystemStatus.ERROR
        assert len(chaos_manager.error_history) > 0


class TestComponentHealthMonitoring:
    """Test component health monitoring"""
    
    @pytest.mark.asyncio
    async def test_get_component_health_all_healthy(self, chaos_manager):
        """Test getting component health when all components are healthy"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock all components as healthy
        with patch.object(chaos_manager, '_check_component_health') as mock_check:
            mock_check.return_value = ComponentHealth.HEALTHY
            
            health = await chaos_manager.get_component_health()
            
            assert health['chaos_engine'] == ComponentHealth.HEALTHY
            assert health['pressure_monitor'] == ComponentHealth.HEALTHY
            assert health['warning_system'] == ComponentHealth.HEALTHY
            assert health['narrative_moderator'] == ComponentHealth.HEALTHY
            assert health['cascade_engine'] == ComponentHealth.HEALTHY
            assert health['overall'] == ComponentHealth.HEALTHY
    
    @pytest.mark.asyncio
    async def test_get_component_health_with_degraded_component(self, chaos_manager):
        """Test getting component health with one degraded component"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock one component as degraded
        def mock_health_check(component):
            if component == chaos_manager.pressure_monitor:
                return ComponentHealth.DEGRADED
            return ComponentHealth.HEALTHY
        
        with patch.object(chaos_manager, '_check_component_health', side_effect=mock_health_check):
            health = await chaos_manager.get_component_health()
            
            assert health['pressure_monitor'] == ComponentHealth.DEGRADED
            assert health['overall'] == ComponentHealth.DEGRADED
    
    @pytest.mark.asyncio
    async def test_get_component_health_with_failed_component(self, chaos_manager):
        """Test getting component health with one failed component"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock one component as failed
        def mock_health_check(component):
            if component == chaos_manager.warning_system:
                return ComponentHealth.FAILED
            return ComponentHealth.HEALTHY
        
        with patch.object(chaos_manager, '_check_component_health', side_effect=mock_health_check):
            health = await chaos_manager.get_component_health()
            
            assert health['warning_system'] == ComponentHealth.FAILED
            assert health['overall'] == ComponentHealth.FAILED
    
    def test_check_component_health_healthy(self, chaos_manager):
        """Test checking health of a healthy component"""
        mock_component = Mock()
        mock_component.get_system_status.return_value = {'status': 'running', 'errors': []}
        
        health = chaos_manager._check_component_health(mock_component)
        assert health == ComponentHealth.HEALTHY
    
    def test_check_component_health_degraded(self, chaos_manager):
        """Test checking health of a degraded component"""
        mock_component = Mock()
        mock_component.get_system_status.return_value = {
            'status': 'running', 
            'errors': ['minor error'],
            'warnings': ['performance issue']
        }
        
        health = chaos_manager._check_component_health(mock_component)
        assert health == ComponentHealth.DEGRADED
    
    def test_check_component_health_failed(self, chaos_manager):
        """Test checking health of a failed component"""
        mock_component = Mock()
        mock_component.get_system_status.side_effect = Exception("Component failed")
        
        health = chaos_manager._check_component_health(mock_component)
        assert health == ComponentHealth.FAILED


class TestSystemStatus:
    """Test system status reporting"""
    
    @pytest.mark.asyncio
    async def test_get_system_status_stopped(self, chaos_manager):
        """Test getting system status when stopped"""
        status = await chaos_manager.get_system_status()
        
        assert status['status'] == ChaosSystemStatus.STOPPED
        assert status['initialized'] is False
        assert status['start_time'] is None
        assert status['uptime'] == 0
        assert 'components' in status
        assert 'metrics' in status
        assert 'recent_errors' in status
    
    @pytest.mark.asyncio
    async def test_get_system_status_running(self, chaos_manager):
        """Test getting system status when running"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        status = await chaos_manager.get_system_status()
        
        assert status['status'] == ChaosSystemStatus.RUNNING
        assert status['initialized'] is True
        assert status['start_time'] is not None
        assert status['uptime'] > 0
        assert 'component_health' in status
        
        # Check component statuses
        assert 'chaos_engine' in status['components']
        assert 'pressure_monitor' in status['components']
        assert 'warning_system' in status['components']
        assert 'narrative_moderator' in status['components']
        assert 'cascade_engine' in status['components']
    
    @pytest.mark.asyncio
    async def test_get_system_status_with_errors(self, chaos_manager):
        """Test getting system status with error history"""
        await chaos_manager.initialize()
        
        # Add some test errors
        test_error = ChaosSystemError("Test error")
        await chaos_manager._log_error("test_component", test_error)
        
        status = await chaos_manager.get_system_status()
        
        assert len(status['recent_errors']) > 0
        error_entry = status['recent_errors'][0]
        assert error_entry['component'] == "test_component"
        assert "Test error" in error_entry['error']
        assert 'timestamp' in error_entry


class TestEventProcessing:
    """Test event processing coordination"""
    
    @pytest.mark.asyncio
    async def test_trigger_event_success(self, chaos_manager):
        """Test successful event triggering"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock successful event processing
        chaos_manager.chaos_engine.process_event = AsyncMock(return_value={"status": "success"})
        
        result = await chaos_manager.trigger_event("economic_crisis", severity=0.7)
        
        assert result["status"] == "success"
        chaos_manager.chaos_engine.process_event.assert_called_once()
        
        # Should log performance metrics
        assert len(chaos_manager.performance_metrics) > 0
    
    @pytest.mark.asyncio
    async def test_trigger_event_system_not_running(self, chaos_manager):
        """Test event triggering when system is not running"""
        await chaos_manager.initialize()
        
        with pytest.raises(ChaosSystemError):
            await chaos_manager.trigger_event("economic_crisis")
    
    @pytest.mark.asyncio
    async def test_trigger_event_with_cascade(self, chaos_manager):
        """Test event triggering with cascade effects"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock cascade processing
        chaos_manager.cascade_engine.process_cascade = AsyncMock(
            return_value={"triggered_events": ["social_unrest"]}
        )
        
        result = await chaos_manager.trigger_event("economic_crisis", enable_cascades=True)
        
        chaos_manager.cascade_engine.process_cascade.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_trigger_event_error_handling(self, chaos_manager):
        """Test error handling during event processing"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock event processing to fail
        test_error = ChaosSystemError("Event processing failed")
        chaos_manager.chaos_engine.process_event.side_effect = test_error
        
        with pytest.raises(ChaosSystemError):
            await chaos_manager.trigger_event("economic_crisis")
        
        # Should log the error
        assert len(chaos_manager.error_history) > 0


class TestWarningManagement:
    """Test warning system coordination"""
    
    @pytest.mark.asyncio
    async def test_get_active_warnings(self, chaos_manager):
        """Test getting active warnings"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock warning system response
        mock_warnings = [
            {"id": "warning_1", "phase": "early", "event_type": "economic_crisis"}
        ]
        chaos_manager.warning_system.get_active_warnings.return_value = mock_warnings
        
        warnings = await chaos_manager.get_active_warnings()
        
        assert len(warnings) == 1
        assert warnings[0]["id"] == "warning_1"
        chaos_manager.warning_system.get_active_warnings.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_escalate_warning(self, chaos_manager):
        """Test warning escalation"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock successful escalation
        chaos_manager.warning_system.escalate_warning = AsyncMock(return_value=True)
        
        result = await chaos_manager.escalate_warning("warning_1")
        
        assert result is True
        chaos_manager.warning_system.escalate_warning.assert_called_once_with("warning_1")
    
    @pytest.mark.asyncio
    async def test_dismiss_warning(self, chaos_manager):
        """Test warning dismissal"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock successful dismissal
        chaos_manager.warning_system.dismiss_warning = AsyncMock(return_value=True)
        
        result = await chaos_manager.dismiss_warning("warning_1")
        
        assert result is True
        chaos_manager.warning_system.dismiss_warning.assert_called_once_with("warning_1")


class TestNarrativeCoordination:
    """Test narrative moderator coordination"""
    
    @pytest.mark.asyncio
    async def test_get_narrative_status(self, chaos_manager):
        """Test getting narrative status"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock narrative status
        mock_status = {
            "current_tension": 0.7,
            "current_engagement": 0.6,
            "active_themes": {"theme1": {"name": "Political Crisis"}}
        }
        chaos_manager.narrative_moderator.get_narrative_status.return_value = mock_status
        
        status = await chaos_manager.get_narrative_status()
        
        assert status["current_tension"] == 0.7
        assert "theme1" in status["active_themes"]
        chaos_manager.narrative_moderator.get_narrative_status.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_narrative_tension(self, chaos_manager):
        """Test updating narrative tension"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock successful update
        chaos_manager.narrative_moderator.update_tension_level = AsyncMock(return_value=True)
        
        result = await chaos_manager.update_narrative_tension(0.8)
        
        assert result is True
        chaos_manager.narrative_moderator.update_tension_level.assert_called_once_with(0.8)
    
    @pytest.mark.asyncio
    async def test_update_narrative_engagement(self, chaos_manager):
        """Test updating narrative engagement"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock successful update
        chaos_manager.narrative_moderator.update_engagement_level = AsyncMock(return_value=True)
        
        result = await chaos_manager.update_narrative_engagement(0.9)
        
        assert result is True
        chaos_manager.narrative_moderator.update_engagement_level.assert_called_once_with(0.9)
    
    @pytest.mark.asyncio
    async def test_add_narrative_theme(self, chaos_manager):
        """Test adding narrative theme"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock successful addition
        chaos_manager.narrative_moderator.add_narrative_theme = AsyncMock(return_value=True)
        
        result = await chaos_manager.add_narrative_theme(
            theme_id="test_theme",
            name="Test Theme",
            description="A test theme",
            priority="central",
            weight_modifier=1.5,
            related_events=["economic_crisis"]
        )
        
        assert result is True
        chaos_manager.narrative_moderator.add_narrative_theme.assert_called_once()


class TestPressureMonitoring:
    """Test pressure monitoring coordination"""
    
    @pytest.mark.asyncio
    async def test_get_current_pressures(self, chaos_manager):
        """Test getting current pressure levels"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock pressure data
        mock_pressures = {
            "economic": 0.7,
            "political": 0.6,
            "social": 0.4,
            "environmental": 0.3,
            "diplomatic": 0.5,
            "temporal": 0.2
        }
        chaos_manager.pressure_monitor.get_current_pressures.return_value = mock_pressures
        
        pressures = await chaos_manager.get_current_pressures()
        
        assert pressures["economic"] == 0.7
        assert pressures["temporal"] == 0.2
        assert len(pressures) == 6
        chaos_manager.pressure_monitor.get_current_pressures.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_pressure_trends(self, chaos_manager):
        """Test getting pressure trends"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock pressure trends
        chaos_manager.pressure_monitor.get_pressure_trends = AsyncMock(
            return_value={"economic": "increasing", "political": "stable"}
        )
        
        trends = await chaos_manager.get_pressure_trends()
        
        assert trends["economic"] == "increasing"
        assert trends["political"] == "stable"
        chaos_manager.pressure_monitor.get_pressure_trends.assert_called_once()


class TestCascadeManagement:
    """Test cascade effect coordination"""
    
    @pytest.mark.asyncio
    async def test_get_active_cascades(self, chaos_manager):
        """Test getting active cascade effects"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock cascade data
        mock_cascades = [
            {"id": "cascade_1", "trigger_event": "economic_crisis", "target_events": ["social_unrest"]}
        ]
        chaos_manager.cascade_engine.get_active_cascades.return_value = mock_cascades
        
        cascades = await chaos_manager.get_active_cascades()
        
        assert len(cascades) == 1
        assert cascades[0]["id"] == "cascade_1"
        chaos_manager.cascade_engine.get_active_cascades.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_trigger_cascade(self, chaos_manager):
        """Test triggering cascade effects"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Mock successful cascade trigger
        chaos_manager.cascade_engine.trigger_cascade = AsyncMock(
            return_value={"cascade_id": "cascade_1", "triggered_events": ["social_unrest"]}
        )
        
        result = await chaos_manager.trigger_cascade("economic_crisis", severity=0.8)
        
        assert result["cascade_id"] == "cascade_1"
        assert "social_unrest" in result["triggered_events"]
        chaos_manager.cascade_engine.trigger_cascade.assert_called_once()


class TestPerformanceMetrics:
    """Test performance metrics tracking"""
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics(self, chaos_manager):
        """Test getting performance metrics"""
        await chaos_manager.initialize()
        await chaos_manager.start()
        
        # Add some test metrics
        await chaos_manager._record_performance_metric("event_processing", 0.15)
        await chaos_manager._record_performance_metric("pressure_check", 0.05)
        
        metrics = chaos_manager.get_performance_metrics()
        
        assert len(metrics) >= 2
        
        # Find our test metrics
        event_metrics = [m for m in metrics if m['operation'] == 'event_processing']
        pressure_metrics = [m for m in metrics if m['operation'] == 'pressure_check']
        
        assert len(event_metrics) > 0
        assert len(pressure_metrics) > 0
        assert event_metrics[0]['duration'] == 0.15
        assert pressure_metrics[0]['duration'] == 0.05
    
    @pytest.mark.asyncio
    async def test_get_performance_metrics_by_operation(self, chaos_manager):
        """Test getting performance metrics filtered by operation"""
        await chaos_manager.initialize()
        
        # Add test metrics
        await chaos_manager._record_performance_metric("event_processing", 0.10)
        await chaos_manager._record_performance_metric("event_processing", 0.20)
        await chaos_manager._record_performance_metric("pressure_check", 0.05)
        
        metrics = chaos_manager.get_performance_metrics(operation="event_processing")
        
        assert len(metrics) == 2
        assert all(m['operation'] == 'event_processing' for m in metrics)
    
    def test_get_average_performance(self, chaos_manager):
        """Test getting average performance for operations"""
        # Manually add some metrics
        chaos_manager.performance_metrics = [
            {'operation': 'test_op', 'duration': 0.10, 'timestamp': datetime.now()},
            {'operation': 'test_op', 'duration': 0.20, 'timestamp': datetime.now()},
            {'operation': 'test_op', 'duration': 0.30, 'timestamp': datetime.now()},
            {'operation': 'other_op', 'duration': 0.50, 'timestamp': datetime.now()},
        ]
        
        avg = chaos_manager.get_average_performance("test_op")
        assert avg == 0.20  # (0.10 + 0.20 + 0.30) / 3
        
        avg_other = chaos_manager.get_average_performance("other_op")
        assert avg_other == 0.50
        
        avg_missing = chaos_manager.get_average_performance("missing_op")
        assert avg_missing == 0.0


class TestErrorHandling:
    """Test error handling and logging"""
    
    @pytest.mark.asyncio
    async def test_log_error(self, chaos_manager):
        """Test error logging"""
        test_error = ChaosSystemError("Test error message")
        
        await chaos_manager._log_error("test_component", test_error)
        
        assert len(chaos_manager.error_history) == 1
        error_entry = chaos_manager.error_history[0]
        assert error_entry['component'] == "test_component"
        assert "Test error message" in error_entry['error']
        assert 'timestamp' in error_entry
    
    def test_get_recent_errors(self, chaos_manager):
        """Test getting recent errors"""
        # Add test errors with timestamps
        now = datetime.now()
        chaos_manager.error_history = [
            {
                'component': 'comp1',
                'error': 'Error 1',
                'timestamp': now - timedelta(minutes=5)
            },
            {
                'component': 'comp2', 
                'error': 'Error 2',
                'timestamp': now - timedelta(minutes=2)
            },
            {
                'component': 'comp3',
                'error': 'Error 3', 
                'timestamp': now - timedelta(hours=2)
            }
        ]
        
        # Get errors from last hour
        recent_errors = chaos_manager.get_recent_errors(hours=1)
        
        assert len(recent_errors) == 2  # Only first two are within 1 hour
        assert recent_errors[0]['component'] == 'comp2'  # Most recent first
        assert recent_errors[1]['component'] == 'comp1'
    
    def test_error_history_cleanup(self, chaos_manager):
        """Test that error history is cleaned up when it gets too large"""
        # Fill error history beyond max size
        max_errors = chaos_manager.config.system_config.max_error_history
        
        for i in range(max_errors + 10):
            chaos_manager.error_history.append({
                'component': f'comp_{i}',
                'error': f'Error {i}',
                'timestamp': datetime.now()
            })
        
        chaos_manager._cleanup_old_errors()
        
        # Should be trimmed to max size
        assert len(chaos_manager.error_history) == max_errors
        
        # Should keep the most recent errors
        assert chaos_manager.error_history[-1]['component'] == f'comp_{max_errors + 9}'


class TestConfigurationManagement:
    """Test configuration updates and management"""
    
    @pytest.mark.asyncio
    async def test_update_config(self, chaos_manager):
        """Test updating configuration"""
        await chaos_manager.initialize()
        
        new_config = ChaosConfig()
        new_config.system_config.health_check_interval = 30.0
        
        await chaos_manager.update_config(new_config)
        
        assert chaos_manager.config.system_config.health_check_interval == 30.0
    
    @pytest.mark.asyncio
    async def test_update_config_propagates_to_components(self, chaos_manager):
        """Test that config updates propagate to all components"""
        await chaos_manager.initialize()
        
        # Mock component update_config methods
        for component in [chaos_manager.chaos_engine, chaos_manager.pressure_monitor,
                         chaos_manager.warning_system, chaos_manager.narrative_moderator,
                         chaos_manager.cascade_engine]:
            component.update_config = AsyncMock()
        
        new_config = ChaosConfig()
        await chaos_manager.update_config(new_config)
        
        # All components should have received config update
        for component in [chaos_manager.chaos_engine, chaos_manager.pressure_monitor,
                         chaos_manager.warning_system, chaos_manager.narrative_moderator,
                         chaos_manager.cascade_engine]:
            component.update_config.assert_called_once_with(new_config)


@pytest.mark.asyncio
async def test_integration_full_lifecycle():
    """Integration test for full chaos manager lifecycle"""
    config = ChaosConfig()
    manager = ChaosManager(config)
    
    # Full lifecycle test
    await manager.initialize()
    assert manager._initialized
    assert manager.status == ChaosSystemStatus.STOPPED
    
    await manager.start()
    assert manager.status == ChaosSystemStatus.RUNNING
    
    # Test basic operations
    status = await manager.get_system_status()
    assert status['status'] == ChaosSystemStatus.RUNNING
    
    health = await manager.get_component_health()
    assert 'overall' in health
    
    # Test pause/resume
    await manager.pause()
    assert manager.status == ChaosSystemStatus.PAUSED
    
    await manager.resume()
    assert manager.status == ChaosSystemStatus.RUNNING
    
    # Test stop
    await manager.stop()
    assert manager.status == ChaosSystemStatus.STOPPED


@pytest.mark.asyncio
async def test_integration_error_recovery():
    """Integration test for error recovery capabilities"""
    config = ChaosConfig()
    manager = ChaosManager(config)
    
    await manager.initialize()
    await manager.start()
    
    # Simulate component failure
    original_method = manager.pressure_monitor.get_current_pressures
    manager.pressure_monitor.get_current_pressures = Mock(side_effect=Exception("Simulated failure"))
    
    # Component should be marked as failed
    health = await manager.get_component_health()
    assert health['pressure_monitor'] == ComponentHealth.FAILED
    assert health['overall'] == ComponentHealth.FAILED
    
    # Restore component
    manager.pressure_monitor.get_current_pressures = original_method
    
    # Should recover
    health = await manager.get_component_health()
    assert health['pressure_monitor'] == ComponentHealth.HEALTHY
    
    await manager.stop() 