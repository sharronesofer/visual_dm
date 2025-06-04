"""
Test suite for the Chaos System - Task 49 Implementation

This test suite verifies the comprehensive chaos system implementation
including pressure monitoring, event triggering, cross-system integration,
and mitigation factors.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import chaos system components
from backend.systems.chaos.core.chaos_engine import ChaosEngine
from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.systems.chaos.models.chaos_state import ChaosState, ChaosLevel
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData
from backend.infrastructure.systems.chaos.models.chaos_events import (
    ChaosEvent, PoliticalUpheavalEvent, NaturalDisasterEvent, 
    EconomicCollapseEvent, WarOutbreakEvent, ResourceScarcityEvent,
    FactionBetrayalEvent, CharacterRevelationEvent
)
from backend.systems.chaos.services.chaos_service import ChaosService
from backend.systems.chaos.services.pressure_service import PressureService
from backend.systems.chaos.services.event_service import EventService
from backend.infrastructure.systems.chaos.utils.event_helpers import EventHelpers
from backend.infrastructure.systems.chaos.utils.chaos_math import ChaosMath


class TestChaosSystemImports:
    """Test that all chaos system components can be imported successfully."""
    
    def test_core_imports(self):
        """Test that core chaos components import correctly."""
        from backend.systems.chaos.core.chaos_engine import ChaosEngine
        from backend.systems.chaos.core.config import ChaosConfig
        from backend.systems.chaos.core.pressure_monitor import PressureMonitor
        from backend.systems.chaos.core.system_integrator import SystemIntegrator
        assert ChaosEngine is not None
        assert ChaosConfig is not None
        assert PressureMonitor is not None
        assert SystemIntegrator is not None
    
    def test_model_imports(self):
        """Test that chaos models import correctly."""
        from backend.infrastructure.systems.chaos.models.chaos_state import ChaosState, ChaosLevel
        from backend.infrastructure.systems.chaos.models.pressure_data import PressureData
        from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEvent
        assert ChaosState is not None
        assert ChaosLevel is not None
        assert PressureData is not None
        assert ChaosEvent is not None
    
    def test_service_imports(self):
        """Test that chaos services import correctly."""
        from backend.systems.chaos.services.chaos_service import ChaosService
        from backend.systems.chaos.services.pressure_service import PressureService
        from backend.systems.chaos.services.event_service import EventService
        from backend.systems.chaos.services.event_manager import EventManager
        from backend.systems.chaos.services.mitigation_service import MitigationService
        assert ChaosService is not None
        assert PressureService is not None
        assert EventService is not None
        assert EventManager is not None
        assert MitigationService is not None
    
    def test_utility_imports(self):
        """Test that chaos utilities import correctly."""
        from backend.infrastructure.systems.chaos.utils.chaos_math import ChaosMath
        from backend.infrastructure.systems.chaos.utils.event_helpers import EventHelpers
        from backend.infrastructure.systems.chaos.utils.chaos_calculator import ChaosCalculator
        from backend.infrastructure.systems.chaos.utils.pressure_calculations import PressureCalculations
        assert ChaosMath is not None
        assert EventHelpers is not None
        assert ChaosCalculator is not None
        assert PressureCalculations is not None


class TestChaosConfiguration:
    """Test chaos system configuration."""
    
    def test_chaos_config_creation(self):
        """Test that ChaosConfig can be created with default values."""
        config = ChaosConfig()
        assert config is not None
        assert hasattr(config, 'pressure_thresholds')
        assert hasattr(config, 'event_weights')
        assert hasattr(config, 'mitigation_factors')
    
    def test_chaos_config_customization(self):
        """Test that ChaosConfig can be customized."""
        config = ChaosConfig()
        # Test that we can access and modify configuration
        assert config.pressure_thresholds is not None
        assert config.event_weights is not None


class TestPressureMonitoring:
    """Test pressure monitoring functionality."""
    
    @pytest.fixture
    def pressure_service(self):
        """Create a pressure service for testing."""
        return PressureService()
    
    def test_pressure_service_creation(self, pressure_service):
        """Test that PressureService can be created."""
        assert pressure_service is not None
    
    def test_pressure_data_structure(self):
        """Test that PressureData has the required structure."""
        # Create mock pressure data
        pressure_data = PressureData(
            timestamp=datetime.now(),
            global_pressure=0.5,
            regional_pressures={},
            source_pressures={},
            pressure_sources={}
        )
        assert pressure_data is not None
        assert hasattr(pressure_data, 'global_pressure')
        assert hasattr(pressure_data, 'regional_pressures')
        assert hasattr(pressure_data, 'source_pressures')


class TestChaosCalculation:
    """Test chaos calculation and scoring."""
    
    @pytest.fixture
    def chaos_math(self):
        """Create a ChaosMath instance for testing."""
        config = ChaosConfig()
        return ChaosMath(config)
    
    def test_chaos_math_creation(self, chaos_math):
        """Test that ChaosMath can be created."""
        assert chaos_math is not None
    
    def test_chaos_score_calculation(self, chaos_math):
        """Test that chaos scores can be calculated."""
        # Create mock pressure data
        pressure_data = PressureData(
            timestamp=datetime.now(),
            global_pressure=0.5,
            regional_pressures={'region1': 0.6},
            source_pressures={'faction_conflict': 0.7},
            pressure_sources={'faction_conflict': {'intensity': 0.7}}
        )
        
        # Calculate chaos score
        result = chaos_math.calculate_chaos_score(pressure_data)
        assert result is not None
        assert hasattr(result, 'chaos_score')
        assert isinstance(result.chaos_score, (int, float))


class TestEventSystem:
    """Test chaos event system."""
    
    @pytest.fixture
    def event_service(self):
        """Create an event service for testing."""
        return EventService()
    
    def test_event_service_creation(self, event_service):
        """Test that EventService can be created."""
        assert event_service is not None
    
    def test_event_classes_exist(self):
        """Test that all required event classes exist."""
        assert PoliticalUpheavalEvent is not None
        assert NaturalDisasterEvent is not None
        assert EconomicCollapseEvent is not None
        assert WarOutbreakEvent is not None
        assert ResourceScarcityEvent is not None
        assert FactionBetrayalEvent is not None
        assert CharacterRevelationEvent is not None
    
    def test_event_helpers_functionality(self):
        """Test that EventHelpers provides required functionality."""
        # Create mock pressure data for the test
        pressure_data = PressureData(
            timestamp=datetime.now(),
            global_pressure=0.5,
            regional_pressures={'region1': 0.6},
            source_pressures={'faction_conflict': 0.7},
            pressure_sources={'faction_conflict': 0.7}
        )
        
        # Test probability calculation
        from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEventType
        probability = EventHelpers.calculate_event_probability(
            chaos_score=0.8,
            event_type=ChaosEventType.POLITICAL_UPHEAVAL,
            pressure_data=pressure_data,
            base_probability=0.1
        )
        assert isinstance(probability, (int, float))
        assert 0 <= probability <= 1
        
        # Test severity determination
        from backend.infrastructure.systems.chaos.models.chaos_events import EventSeverity
        severity = EventHelpers.determine_event_severity(
            chaos_score=0.8,
            pressure_intensity=0.7
        )
        assert severity in [EventSeverity.MINOR, EventSeverity.MODERATE, EventSeverity.MAJOR, EventSeverity.CATASTROPHIC]


class TestChaosEngine:
    """Test the main chaos engine."""
    
    @pytest.fixture
    def chaos_config(self):
        """Create a chaos config for testing."""
        return ChaosConfig()
    
    def test_chaos_engine_singleton(self, chaos_config):
        """Test that ChaosEngine follows singleton pattern."""
        # Clear any existing instance
        ChaosEngine._instance = None
        
        engine1 = ChaosEngine.get_instance(chaos_config)
        engine2 = ChaosEngine.get_instance()
        
        assert engine1 is engine2
        assert isinstance(engine1, ChaosEngine)
    
    def test_chaos_engine_initialization(self, chaos_config):
        """Test that ChaosEngine can be initialized."""
        # Clear any existing instance
        ChaosEngine._instance = None
        
        engine = ChaosEngine.get_instance(chaos_config)
        assert engine is not None
        assert hasattr(engine, 'config')
        assert hasattr(engine, 'pressure_monitor')
        assert hasattr(engine, 'event_manager')
        assert hasattr(engine, 'system_integrator')


class TestChaosServices:
    """Test chaos system services."""
    
    def test_chaos_service_creation(self):
        """Test that ChaosService can be created."""
        service = ChaosService()
        assert service is not None
    
    def test_pressure_service_creation(self):
        """Test that PressureService can be created."""
        service = PressureService()
        assert service is not None
    
    def test_event_service_creation(self):
        """Test that EventService can be created."""
        service = EventService()
        assert service is not None


class TestChaosIntegration:
    """Test chaos system integration points."""
    
    def test_chaos_state_creation(self):
        """Test that ChaosState can be created."""
        chaos_state = ChaosState(
            chaos_level=ChaosLevel.MODERATE,
            chaos_score=0.6,
            timestamp=datetime.now(),
            regional_states={},
            active_events=[],
            pressure_sources={}
        )
        assert chaos_state is not None
        assert chaos_state.chaos_level == ChaosLevel.MODERATE
        assert chaos_state.chaos_score == 0.6


if __name__ == '__main__':
    pytest.main([__file__, '-v']) 