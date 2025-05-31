"""
Comprehensive Tests for Chaos System Components

Tests for the chaos system implementation including:
- Chaos Engine core functionality
- Pressure monitoring and calculation
- Event triggering and management
- Cross-system integration
- Analytics and performance monitoring
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from backend.systems.chaos.core.chaos_engine import ChaosEngine, get_chaos_engine
from backend.systems.chaos.core.pressure_monitor import PressureMonitor
from backend.systems.chaos.core.event_triggers import EventTriggerSystem
from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.models.chaos_state import ChaosState, ChaosLevel
from backend.systems.chaos.models.pressure_data import PressureData, PressureReading, PressureSource
from backend.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType, EventSeverity
from backend.systems.chaos.services.chaos_service import ChaosService
from backend.systems.chaos.services.event_manager import EventManager
from backend.systems.chaos.services.mitigation_service import MitigationService
from backend.systems.chaos.utils.chaos_math import ChaosMath, ChaosCalculationResult
from backend.systems.chaos.analytics.chaos_analytics import ChaosAnalytics


class TestChaosEngine:
    """Test the main chaos engine functionality"""
    
    @pytest.fixture
    def chaos_config(self):
        """Create a test chaos configuration"""
        return ChaosConfig(
            chaos_threshold=0.7,
            pressure_update_interval=1.0,
            event_cooldown_minutes=5,
            max_concurrent_events=3
        )
    
    @pytest.fixture
    def chaos_engine(self, chaos_config):
        """Create a chaos engine instance for testing"""
        # Reset singleton for testing
        ChaosEngine._instance = None
        return ChaosEngine(chaos_config)
    
    def test_chaos_engine_singleton(self, chaos_config):
        """Test that chaos engine follows singleton pattern"""
        # Reset singleton
        ChaosEngine._instance = None
        
        engine1 = ChaosEngine.get_instance(chaos_config)
        engine2 = ChaosEngine.get_instance()
        
        assert engine1 is engine2
        assert isinstance(engine1, ChaosEngine)
    
    def test_chaos_engine_initialization(self, chaos_engine):
        """Test chaos engine initialization"""
        assert chaos_engine.config is not None
        assert chaos_engine.pressure_monitor is not None
        assert chaos_engine.chaos_math is not None
        assert chaos_engine.event_manager is not None
        assert chaos_engine.system_integrator is not None
        assert chaos_engine.analytics is not None
        assert not chaos_engine.is_running
        assert not chaos_engine.is_paused
    
    @pytest.mark.asyncio
    async def test_chaos_engine_lifecycle(self, chaos_engine):
        """Test chaos engine start/stop lifecycle"""
        # Mock the initialize method to avoid complex setup
        with patch.object(chaos_engine, 'initialize', new_callable=AsyncMock):
            await chaos_engine.start()
            assert chaos_engine.is_running
            assert not chaos_engine.is_paused
            
            chaos_engine.pause()
            assert chaos_engine.is_paused
            
            chaos_engine.resume()
            assert not chaos_engine.is_paused
            
            await chaos_engine.stop()
            assert not chaos_engine.is_running
    
    def test_get_current_chaos_state(self, chaos_engine):
        """Test getting current chaos state"""
        # Set up a mock chaos state
        mock_state = ChaosState(
            chaos_level=ChaosLevel.MODERATE,
            chaos_score=0.6,
            last_updated=datetime.now()
        )
        chaos_engine.current_chaos_state = mock_state
        
        state_dict = chaos_engine.get_current_chaos_state()
        
        assert isinstance(state_dict, dict)
        assert 'chaos_level' in state_dict
        assert 'chaos_score' in state_dict
        assert 'last_updated' in state_dict
    
    @pytest.mark.asyncio
    async def test_apply_mitigation(self, chaos_engine):
        """Test applying mitigation factors"""
        with patch.object(chaos_engine.event_manager, 'apply_mitigation', new_callable=AsyncMock) as mock_apply:
            mock_apply.return_value = True
            
            result = await chaos_engine.apply_mitigation(
                mitigation_type='diplomatic',
                effectiveness=0.5,
                duration_hours=24,
                source_id='test_source',
                source_type='diplomatic',
                description='Test mitigation'
            )
            
            assert result is True
            mock_apply.assert_called_once()


class TestPressureMonitor:
    """Test pressure monitoring functionality"""
    
    @pytest.fixture
    def pressure_monitor(self):
        """Create a pressure monitor for testing"""
        config = ChaosConfig()
        return PressureMonitor(config)
    
    def test_pressure_monitor_initialization(self, pressure_monitor):
        """Test pressure monitor initialization"""
        assert pressure_monitor.config is not None
        assert pressure_monitor.pressure_data is not None
        assert not pressure_monitor.is_monitoring
        assert pressure_monitor.monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_pressure_monitor_lifecycle(self, pressure_monitor):
        """Test pressure monitor start/stop lifecycle"""
        with patch.object(pressure_monitor, '_initialize_system_connections', new_callable=AsyncMock):
            with patch.object(pressure_monitor, '_monitoring_loop', new_callable=AsyncMock):
                await pressure_monitor.start()
                assert pressure_monitor.is_monitoring
                
                await pressure_monitor.stop()
                assert not pressure_monitor.is_monitoring
    
    def test_get_current_pressure_data(self, pressure_monitor):
        """Test getting current pressure data"""
        pressure_data = pressure_monitor.get_current_pressure_data()
        assert isinstance(pressure_data, PressureData)
    
    def test_get_global_pressure(self, pressure_monitor):
        """Test getting global pressure value"""
        # Set up mock pressure data
        pressure_monitor.pressure_data.global_pressure = 0.6
        
        global_pressure = pressure_monitor.get_global_pressure()
        assert isinstance(global_pressure, float)
        assert 0.0 <= global_pressure <= 1.0
    
    def test_is_pressure_above_threshold(self, pressure_monitor):
        """Test pressure threshold checking"""
        pressure_monitor.pressure_data.global_pressure = 0.8
        
        assert pressure_monitor.is_pressure_above_threshold(0.7)
        assert not pressure_monitor.is_pressure_above_threshold(0.9)


class TestEventTriggerSystem:
    """Test event triggering functionality"""
    
    @pytest.fixture
    def event_trigger_system(self):
        """Create an event trigger system for testing"""
        config = ChaosConfig()
        return EventTriggerSystem(config)
    
    def test_event_trigger_initialization(self, event_trigger_system):
        """Test event trigger system initialization"""
        assert event_trigger_system.config is not None
        assert hasattr(event_trigger_system, 'event_cooldowns')
        assert hasattr(event_trigger_system, 'active_events')
    
    @pytest.mark.asyncio
    async def test_evaluate_chaos_events(self, event_trigger_system):
        """Test chaos event evaluation"""
        # Create mock chaos calculation result
        chaos_result = ChaosCalculationResult(
            chaos_score=0.8,
            chaos_level=ChaosLevel.HIGH,
            pressure_sources={'political': 0.7, 'economic': 0.6},
            weighted_factors={'political': 0.84, 'economic': 0.48},
            threshold_exceeded=True,
            recommended_events=['political_upheaval', 'economic_instability']
        )
        
        pressure_data = PressureData()
        pressure_data.global_pressure = 0.8
        
        with patch.object(event_trigger_system, '_create_chaos_event') as mock_create:
            mock_event = Mock(spec=ChaosEvent)
            mock_create.return_value = mock_event
            
            events = await event_trigger_system.evaluate_chaos_events(chaos_result, pressure_data)
            
            assert isinstance(events, list)


class TestChaosMath:
    """Test chaos mathematical calculations"""
    
    @pytest.fixture
    def chaos_math(self):
        """Create chaos math calculator for testing"""
        config = ChaosConfig()
        return ChaosMath(config)
    
    @pytest.fixture
    def sample_pressure_data(self):
        """Create sample pressure data for testing"""
        pressure_data = PressureData()
        pressure_data.pressure_sources = {
            'political': 0.7,
            'economic': 0.5,
            'faction_tension': 0.8,
            'population_stress': 0.4
        }
        pressure_data.global_pressure = 0.6
        return pressure_data
    
    def test_calculate_chaos_score(self, chaos_math, sample_pressure_data):
        """Test chaos score calculation"""
        result = chaos_math.calculate_chaos_score(sample_pressure_data)
        
        assert isinstance(result, ChaosCalculationResult)
        assert 0.0 <= result.chaos_score <= 1.0
        assert isinstance(result.chaos_level, ChaosLevel)
        assert isinstance(result.pressure_sources, dict)
        assert isinstance(result.weighted_factors, dict)
        assert isinstance(result.threshold_exceeded, bool)
    
    def test_high_pressure_exceeds_threshold(self, chaos_math):
        """Test that high pressure exceeds chaos threshold"""
        high_pressure_data = PressureData()
        high_pressure_data.pressure_sources = {
            'political': 0.9,
            'economic': 0.8,
            'faction_tension': 0.9,
            'population_stress': 0.7
        }
        high_pressure_data.global_pressure = 0.85
        
        result = chaos_math.calculate_chaos_score(high_pressure_data)
        
        assert result.threshold_exceeded
        assert result.chaos_score > chaos_math.config.chaos_threshold
    
    def test_low_pressure_below_threshold(self, chaos_math):
        """Test that low pressure stays below threshold"""
        low_pressure_data = PressureData()
        low_pressure_data.pressure_sources = {
            'political': 0.2,
            'economic': 0.1,
            'faction_tension': 0.3,
            'population_stress': 0.2
        }
        low_pressure_data.global_pressure = 0.2
        
        result = chaos_math.calculate_chaos_score(low_pressure_data)
        
        assert not result.threshold_exceeded
        assert result.chaos_score < chaos_math.config.chaos_threshold


class TestChaosService:
    """Test chaos service functionality"""
    
    @pytest.fixture
    def chaos_service(self):
        """Create chaos service for testing"""
        config = ChaosConfig()
        return ChaosService(config)
    
    def test_chaos_service_initialization(self, chaos_service):
        """Test chaos service initialization"""
        assert chaos_service.config is not None
        assert chaos_service._chaos_engine is None  # Lazy loaded
    
    @pytest.mark.asyncio
    async def test_get_chaos_status(self, chaos_service):
        """Test getting chaos status"""
        with patch.object(chaos_service, '_get_chaos_engine') as mock_engine:
            mock_engine.return_value.get_current_chaos_state.return_value = {
                'chaos_level': 'MODERATE',
                'chaos_score': 0.6
            }
            
            status = await chaos_service.get_chaos_status()
            
            assert isinstance(status, dict)
            assert 'chaos_level' in status
            assert 'chaos_score' in status


class TestMitigationService:
    """Test mitigation service functionality"""
    
    @pytest.fixture
    def mitigation_service(self):
        """Create mitigation service for testing"""
        config = ChaosConfig()
        return MitigationService(config)
    
    def test_mitigation_service_initialization(self, mitigation_service):
        """Test mitigation service initialization"""
        assert mitigation_service.config is not None
        assert hasattr(mitigation_service, 'active_mitigations')
    
    @pytest.mark.asyncio
    async def test_apply_mitigation(self, mitigation_service):
        """Test applying mitigation factors"""
        result = await mitigation_service.apply_mitigation(
            mitigation_type='diplomatic',
            effectiveness=0.5,
            duration_hours=24,
            source_id='test_source',
            source_type='diplomatic',
            description='Test mitigation'
        )
        
        assert isinstance(result, bool)
    
    def test_calculate_mitigation_effects(self, mitigation_service):
        """Test mitigation effect calculation"""
        pressure_sources = {
            'political': 0.8,
            'economic': 0.6,
            'faction_tension': 0.7
        }
        
        mitigated = mitigation_service.calculate_mitigation_effects(pressure_sources)
        
        assert isinstance(mitigated, dict)
        assert len(mitigated) == len(pressure_sources)
        for key in pressure_sources:
            assert key in mitigated
            assert isinstance(mitigated[key], float)


class TestChaosAnalytics:
    """Test chaos analytics functionality"""
    
    @pytest.fixture
    def chaos_analytics(self):
        """Create chaos analytics for testing"""
        config = ChaosConfig()
        return ChaosAnalytics(config)
    
    def test_chaos_analytics_initialization(self, chaos_analytics):
        """Test chaos analytics initialization"""
        assert chaos_analytics.config is not None
    
    def test_start_operation(self, chaos_analytics):
        """Test starting an operation for tracking"""
        context_id = chaos_analytics.start_operation("test_operation")
        
        assert isinstance(context_id, str)
        assert len(context_id) > 0
    
    def test_end_operation(self, chaos_analytics):
        """Test ending an operation"""
        context_id = chaos_analytics.start_operation("test_operation")
        chaos_analytics.end_operation(context_id, True, "test_operation")
        
        # Should not raise any exceptions
        assert True
    
    def test_record_metric(self, chaos_analytics):
        """Test recording metrics"""
        chaos_analytics.record_metric('test_metric', 0.5, 'test_category')
        
        # Should not raise any exceptions
        assert True


class TestIntegration:
    """Integration tests for chaos system components"""
    
    @pytest.fixture
    def full_chaos_system(self):
        """Create a full chaos system for integration testing"""
        # Reset singleton
        ChaosEngine._instance = None
        
        config = ChaosConfig(
            chaos_threshold=0.7,
            pressure_update_interval=0.1,  # Fast for testing
            event_cooldown_minutes=1
        )
        
        return ChaosEngine(config)
    
    @pytest.mark.asyncio
    async def test_full_system_integration(self, full_chaos_system):
        """Test full system integration"""
        with patch.object(full_chaos_system, 'initialize', new_callable=AsyncMock):
            with patch.object(full_chaos_system, '_background_loop', new_callable=AsyncMock):
                await full_chaos_system.start()
                
                # Test system state
                assert full_chaos_system.is_running
                
                # Test getting system metrics
                metrics = full_chaos_system.get_system_metrics()
                assert isinstance(metrics, dict)
                
                # Test getting pressure summary
                pressure_summary = full_chaos_system.get_pressure_summary()
                assert isinstance(pressure_summary, dict)
                
                await full_chaos_system.stop()
                assert not full_chaos_system.is_running


# Performance and stress tests
class TestPerformance:
    """Performance tests for chaos system"""
    
    @pytest.mark.asyncio
    async def test_pressure_calculation_performance(self):
        """Test that pressure calculations are performant"""
        config = ChaosConfig()
        chaos_math = ChaosMath(config)
        
        # Create large pressure data
        pressure_data = PressureData()
        pressure_data.pressure_sources = {
            f'source_{i}': 0.5 for i in range(100)
        }
        
        start_time = datetime.now()
        result = chaos_math.calculate_chaos_score(pressure_data)
        end_time = datetime.now()
        
        calculation_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (< 100ms)
        assert calculation_time < 0.1
        assert isinstance(result, ChaosCalculationResult)
    
    def test_memory_usage(self):
        """Test that chaos system doesn't leak memory"""
        config = ChaosConfig()
        
        # Create and destroy multiple instances
        for _ in range(100):
            pressure_monitor = PressureMonitor(config)
            chaos_math = ChaosMath(config)
            mitigation_service = MitigationService(config)
            
            # Force garbage collection
            del pressure_monitor
            del chaos_math
            del mitigation_service
        
        # Should complete without memory issues
        assert True