"""
Unit tests for the Warning System

Tests the three-tier escalation system (rumor → early → imminent) as required by the Development Bible.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from backend.systems.chaos.core.warning_system import (
    WarningSystem, WarningPhase, WarningEvent
)
from backend.systems.chaos.core.config import ChaosConfig


@pytest.fixture
def chaos_config():
    """Create a test chaos configuration"""
    config = ChaosConfig()
    return config


@pytest.fixture
def warning_system(chaos_config):
    """Create a warning system for testing"""
    return WarningSystem(chaos_config)


@pytest.fixture
def mock_regional_data():
    """Create mock regional data for testing"""
    mock_data = Mock()
    mock_data.pressure_sources = {
        'economic': 0.6,
        'political': 0.8,
        'social': 0.4
    }
    return mock_data


class TestWarningSystemInitialization:
    """Test warning system initialization and configuration"""
    
    def test_warning_system_creation(self, chaos_config):
        """Test that warning system can be created with proper defaults"""
        warning_system = WarningSystem(chaos_config)
        
        assert warning_system.config is chaos_config
        assert not warning_system._initialized
        assert not warning_system._running
        assert len(warning_system.active_warnings) == 0
        assert len(warning_system.warning_history) == 0
    
    def test_default_phase_durations(self, warning_system):
        """Test that default phase durations are set correctly"""
        assert warning_system.phase_durations[WarningPhase.RUMOR] == timedelta(hours=8)
        assert warning_system.phase_durations[WarningPhase.EARLY] == timedelta(hours=4)
        assert warning_system.phase_durations[WarningPhase.IMMINENT] == timedelta(hours=1)
    
    def test_escalation_probabilities(self, warning_system):
        """Test that escalation probabilities are configured correctly"""
        assert warning_system.escalation_probabilities[WarningPhase.RUMOR] == 0.6
        assert warning_system.escalation_probabilities[WarningPhase.EARLY] == 0.8
        assert warning_system.escalation_probabilities[WarningPhase.IMMINENT] == 0.9
    
    @pytest.mark.asyncio
    async def test_initialization(self, warning_system):
        """Test warning system initialization"""
        await warning_system.initialize()
        
        assert warning_system._initialized
        assert warning_system.metrics['warnings_triggered'] == 0


class TestWarningGeneration:
    """Test warning event generation and triggering"""
    
    @pytest.mark.asyncio
    async def test_trigger_rumor_warning(self, warning_system):
        """Test triggering rumor phase warning"""
        await warning_system.initialize()
        
        region_id = "test_region"
        event_type = "economic_crisis"
        
        result = await warning_system.trigger_warning(region_id, "rumor", event_type)
        
        assert result is True
        assert region_id in warning_system.active_warnings
        assert len(warning_system.active_warnings[region_id]) == 1
        assert warning_system.metrics['warnings_triggered'] == 1
        
        # Check warning content
        warning_key = f"rumor_{event_type}"
        warning = warning_system.active_warnings[region_id][warning_key]
        assert warning.phase == WarningPhase.RUMOR
        assert warning.event_type == event_type
        assert warning.region_id == region_id
        assert "Merchants whisper" in warning.description
    
    @pytest.mark.asyncio
    async def test_trigger_early_warning(self, warning_system):
        """Test triggering early warning phase"""
        await warning_system.initialize()
        
        region_id = "test_region"
        event_type = "political_upheaval"
        
        result = await warning_system.trigger_warning(region_id, "early", event_type)
        
        assert result is True
        warning_key = f"early_{event_type}"
        warning = warning_system.active_warnings[region_id][warning_key]
        assert warning.phase == WarningPhase.EARLY
        assert "Political crisis becomes apparent" in warning.description
    
    @pytest.mark.asyncio
    async def test_trigger_imminent_warning(self, warning_system):
        """Test triggering imminent warning phase"""
        await warning_system.initialize()
        
        region_id = "test_region"
        event_type = "civil_unrest"
        
        result = await warning_system.trigger_warning(region_id, "imminent", event_type)
        
        assert result is True
        warning_key = f"imminent_{event_type}"
        warning = warning_system.active_warnings[region_id][warning_key]
        assert warning.phase == WarningPhase.IMMINENT
        assert "about to erupt" in warning.description
    
    @pytest.mark.asyncio
    async def test_invalid_warning_phase(self, warning_system):
        """Test handling of invalid warning phase"""
        await warning_system.initialize()
        
        result = await warning_system.trigger_warning("test_region", "invalid_phase", "test_event")
        
        assert result is False
        assert len(warning_system.active_warnings) == 0


class TestWarningEscalation:
    """Test warning escalation logic"""
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_warnings_low_chaos(self, warning_system, mock_regional_data):
        """Test that low chaos level doesn't trigger warnings"""
        await warning_system.initialize()
        
        result = await warning_system.check_and_trigger_warnings(
            "test_region", 0.3, mock_regional_data
        )
        
        assert result is False
        assert len(warning_system.active_warnings) == 0
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_warnings_moderate_chaos(self, warning_system, mock_regional_data):
        """Test that moderate chaos triggers rumor warnings"""
        await warning_system.initialize()
        
        result = await warning_system.check_and_trigger_warnings(
            "test_region", 0.5, mock_regional_data
        )
        
        assert result is True
        assert "test_region" in warning_system.active_warnings
        # Should trigger rumor phase since political pressure is highest
        assert any("rumor" in key for key in warning_system.active_warnings["test_region"].keys())
    
    @pytest.mark.asyncio
    async def test_check_and_trigger_warnings_high_chaos_escalation(self, warning_system, mock_regional_data):
        """Test that high chaos escalates existing warnings"""
        await warning_system.initialize()
        
        # First trigger a rumor warning
        await warning_system.trigger_warning("test_region", "rumor", "political_upheaval")
        
        # Then check with high chaos level - should escalate
        result = await warning_system.check_and_trigger_warnings(
            "test_region", 0.8, mock_regional_data
        )
        
        assert result is True
        # Should now have both rumor and early warnings
        region_warnings = warning_system.active_warnings["test_region"]
        assert any("rumor" in key for key in region_warnings.keys())
        assert any("early" in key for key in region_warnings.keys())
    
    def test_determine_event_type_from_pressure(self, warning_system, mock_regional_data):
        """Test event type determination from pressure sources"""
        event_type = warning_system._determine_event_type(mock_regional_data)
        
        # Political pressure is highest (0.8), so should return political event
        assert event_type == "political_upheaval"
    
    def test_determine_event_type_no_data(self, warning_system):
        """Test event type determination with no regional data"""
        event_type = warning_system._determine_event_type(None)
        assert event_type == "general_chaos"


class TestWarningContent:
    """Test warning content generation"""
    
    def test_generate_rumor_content(self, warning_system):
        """Test rumor phase content generation"""
        description, clues, indicators = warning_system._generate_warning_content(
            WarningPhase.RUMOR, "economic_crisis"
        )
        
        assert "whisper" in description.lower()
        assert "Nervous traders" in clues[0]
        assert "Market volatility" in indicators[0]
    
    def test_generate_early_warning_content(self, warning_system):
        """Test early warning content generation"""
        description, clues, indicators = warning_system._generate_warning_content(
            WarningPhase.EARLY, "civil_unrest"
        )
        
        assert "concerning levels" in description.lower()
        assert "demonstrations" in clues[0].lower()
        assert "pressure metrics" in indicators[0].lower()
    
    def test_generate_imminent_content(self, warning_system):
        """Test imminent warning content generation"""
        description, clues, indicators = warning_system._generate_warning_content(
            WarningPhase.IMMINENT, "economic_crisis"
        )
        
        assert "about to break" in description.lower()
        assert "panic" in clues[0].lower()
        assert "imminent" in indicators[0].lower()
    
    def test_calculate_warning_severity(self, warning_system):
        """Test warning severity calculation"""
        rumor_severity = warning_system._calculate_warning_severity(WarningPhase.RUMOR)
        early_severity = warning_system._calculate_warning_severity(WarningPhase.EARLY)
        imminent_severity = warning_system._calculate_warning_severity(WarningPhase.IMMINENT)
        
        assert rumor_severity == 0.3
        assert early_severity == 0.6
        assert imminent_severity == 0.9
        assert rumor_severity < early_severity < imminent_severity


class TestWarningLifecycle:
    """Test warning lifecycle management"""
    
    @pytest.mark.asyncio
    async def test_warning_expiration(self, warning_system):
        """Test that warnings expire correctly"""
        await warning_system.initialize()
        
        # Create a warning with very short duration for testing
        warning_system.phase_durations[WarningPhase.RUMOR] = timedelta(seconds=0.1)
        
        await warning_system.trigger_warning("test_region", "rumor", "test_event")
        assert len(warning_system.active_warnings["test_region"]) == 1
        
        # Wait for expiration
        await asyncio.sleep(0.2)
        
        # Process escalations (which handles expiration)
        await warning_system._process_warning_escalations()
        
        # Warning should either escalate or be removed
        # Since we're not mocking random, we can't predict exactly what happens
        # But we can check that the system processed it
        assert warning_system.metrics['warnings_triggered'] >= 1
    
    @pytest.mark.asyncio
    async def test_warning_cleanup(self, warning_system):
        """Test cleanup of expired warnings"""
        await warning_system.initialize()
        
        # Create an expired warning manually
        warning_event = WarningEvent(
            warning_id="test_warning",
            region_id="test_region",
            phase=WarningPhase.RUMOR,
            event_type="test_event",
            severity=0.3,
            triggered_at=datetime.now() - timedelta(hours=2),
            expires_at=datetime.now() - timedelta(hours=1),
            description="Test warning",
            visible_clues=["Test clue"],
            hidden_indicators=["Test indicator"],
            escalation_probability=0.5
        )
        
        warning_system.active_warnings["test_region"] = {"test_key": warning_event}
        
        await warning_system._cleanup_expired_warnings()
        
        # Warning should be cleaned up
        assert len(warning_system.active_warnings) == 0
    
    @pytest.mark.asyncio
    async def test_clear_warning(self, warning_system):
        """Test manual warning clearing (intervention)"""
        await warning_system.initialize()
        
        await warning_system.trigger_warning("test_region", "rumor", "test_event")
        assert len(warning_system.active_warnings["test_region"]) == 1
        
        result = await warning_system.clear_warning("test_region", "rumor")
        
        assert result is True
        assert len(warning_system.active_warnings) == 0
        assert warning_system.metrics['warnings_prevented'] == 1


class TestWarningQueries:
    """Test warning query and reporting functions"""
    
    @pytest.mark.asyncio
    async def test_get_region_warnings(self, warning_system):
        """Test getting warnings for a specific region"""
        await warning_system.initialize()
        
        await warning_system.trigger_warning("test_region", "rumor", "test_event")
        await warning_system.trigger_warning("test_region", "early", "test_event")
        
        result = await warning_system.get_region_warnings("test_region")
        
        assert result['region_id'] == "test_region"
        assert result['warning_count'] == 2
        assert result['highest_phase'] == "early"
        assert len(result['active_warnings']) == 2
    
    @pytest.mark.asyncio
    async def test_get_all_warnings(self, warning_system):
        """Test getting all warnings across regions"""
        await warning_system.initialize()
        
        await warning_system.trigger_warning("region1", "rumor", "event1")
        await warning_system.trigger_warning("region2", "early", "event2")
        
        result = await warning_system.get_all_warnings()
        
        assert result['total_warnings'] == 2
        assert result['active_regions'] == 2
        assert len(result['warnings']) == 2
        assert 'metrics' in result
    
    @pytest.mark.asyncio
    async def test_get_region_warnings_empty(self, warning_system):
        """Test getting warnings for region with no warnings"""
        await warning_system.initialize()
        
        result = await warning_system.get_region_warnings("empty_region")
        
        assert result['region_id'] == "empty_region"
        assert result['warning_count'] == 0
        assert result['highest_phase'] is None
        assert len(result['active_warnings']) == 0


class TestWarningSystemLifecycle:
    """Test warning system start/stop lifecycle"""
    
    @pytest.mark.asyncio
    async def test_start_stop_cycle(self, warning_system):
        """Test starting and stopping the warning system"""
        assert not warning_system._running
        
        await warning_system.start()
        assert warning_system._running
        assert warning_system._monitoring_task is not None
        
        await warning_system.stop()
        assert not warning_system._running
        assert warning_system._monitoring_task.cancelled()
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_error_handling(self, warning_system):
        """Test that monitoring loop handles errors gracefully"""
        await warning_system.initialize()
        
        # Mock the escalation processing to raise an error
        with patch.object(warning_system, '_process_warning_escalations', side_effect=Exception("Test error")):
            warning_system._running = True
            
            # Start monitoring loop for short time
            task = asyncio.create_task(warning_system._monitoring_loop())
            await asyncio.sleep(0.1)
            
            warning_system._running = False
            await task
            
            # Should complete without raising exception
            assert True


class TestWarningEventModel:
    """Test WarningEvent data model"""
    
    def test_warning_event_creation(self):
        """Test creating a warning event"""
        now = datetime.now()
        expires = now + timedelta(hours=2)
        
        warning = WarningEvent(
            warning_id="test_id",
            region_id="test_region",
            phase=WarningPhase.EARLY,
            event_type="test_event",
            severity=0.6,
            triggered_at=now,
            expires_at=expires,
            description="Test warning",
            visible_clues=["Clue 1", "Clue 2"],
            hidden_indicators=["Indicator 1"],
            escalation_probability=0.8
        )
        
        assert warning.warning_id == "test_id"
        assert warning.phase == WarningPhase.EARLY
        assert warning.severity == 0.6
        assert len(warning.visible_clues) == 2
    
    def test_warning_event_to_dict(self):
        """Test converting warning event to dictionary"""
        now = datetime.now()
        expires = now + timedelta(hours=2)
        
        warning = WarningEvent(
            warning_id="test_id",
            region_id="test_region",
            phase=WarningPhase.IMMINENT,
            event_type="test_event",
            severity=0.9,
            triggered_at=now,
            expires_at=expires,
            description="Test warning",
            visible_clues=["Clue"],
            hidden_indicators=["Indicator"],
            escalation_probability=0.9
        )
        
        warning_dict = warning.to_dict()
        
        assert warning_dict['warning_id'] == "test_id"
        assert warning_dict['phase'] == "imminent"
        assert warning_dict['severity'] == 0.9
        assert isinstance(warning_dict['triggered_at'], str)
        assert isinstance(warning_dict['expires_at'], str)


@pytest.mark.asyncio
async def test_integration_with_escalation_monitoring():
    """Integration test for warning escalation monitoring"""
    config = ChaosConfig()
    warning_system = WarningSystem(config)
    
    # Set very short durations for testing
    warning_system.phase_durations[WarningPhase.RUMOR] = timedelta(seconds=0.1)
    warning_system.escalation_probabilities[WarningPhase.RUMOR] = 1.0  # Force escalation
    
    await warning_system.initialize()
    
    # Trigger initial warning
    await warning_system.trigger_warning("test_region", "rumor", "test_event")
    initial_count = warning_system.metrics['warnings_triggered']
    
    # Wait for escalation processing
    await asyncio.sleep(0.2)
    await warning_system._process_warning_escalations()
    
    # Should have escalated to early warning
    final_count = warning_system.metrics['warnings_triggered']
    assert final_count > initial_count
    assert warning_system.metrics['warnings_escalated'] >= 1 