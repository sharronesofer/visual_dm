"""
Test Complete Chaos System Integration

Test the complete chaos system with all components:
- Narrative Intelligence Weighting
- Warning System (3-tier escalation)
- Cascade Engine
- Full integration with existing chaos components

This validates Task 75: Backend - Implement Complete Chaos System
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from backend.systems.chaos.core.chaos_engine import ChaosEngine
from backend.systems.chaos.core.narrative_moderator import (
    NarrativeModerator, NarrativeGenre, NarrativePacing, NarrativeContext
)
from backend.systems.chaos.core.warning_system import (
    WarningSystem, WarningPhase, WarningEvent, WarningSequence
)
from backend.systems.chaos.core.cascade_engine import (
    CascadeEngine, CascadeType, CascadeRule, CascadeEvent
)
from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType, EventSeverity
from backend.infrastructure.systems.chaos.models.chaos_state import ChaosState, ChaosLevel
from backend.infrastructure.systems.chaos.models.pressure_data import PressureData, RegionalPressure
from backend.infrastructure.systems.chaos.utils.chaos_math import ChaosCalculationResult


# Module-level fixtures for shared use
@pytest.fixture
def chaos_config():
    """Create chaos configuration for testing"""
    return ChaosConfig()

@pytest.fixture
def sample_pressure_data():
    """Create sample pressure data for testing"""
    pressure_data = PressureData()
    pressure_data.economic_instability = 0.7
    pressure_data.faction_conflict = 0.6
    pressure_data.population_stress = 0.8
    pressure_data.environmental_pressure = 0.4
    pressure_data.military_buildup = 0.5
    pressure_data.diplomatic_tension = 0.6
    return pressure_data

@pytest.fixture
def sample_chaos_result():
    """Create sample chaos calculation result"""
    return ChaosCalculationResult(
        chaos_score=0.75,
        chaos_level=ChaosLevel.HIGH,
        regional_scores={'region1': 0.8, 'region2': 0.7},
        source_contributions={
            'economic_instability': 0.7,
            'faction_conflict': 0.6,
            'population_stress': 0.8
        },
        temporal_factors={'trend': 0.1, 'velocity': 0.05}
    )

@pytest.fixture
def sample_chaos_state():
    """Create sample chaos state"""
    return ChaosState(
        current_chaos_level=ChaosLevel.HIGH,
        current_chaos_score=0.75
    )

@pytest.fixture
def sample_chaos_event():
    """Create a sample chaos event"""
    return ChaosEvent(
        event_id="test-event-1",
        event_type=ChaosEventType.POLITICAL_UPHEAVAL,
        title="Political Crisis",
        description="A major political crisis unfolds",
        severity=EventSeverity.MAJOR,
        affected_regions=["region1"],
        trigger_probability=0.6
    )


class TestCompleteChaoSystem:
    """Test the complete integrated chaos system"""
    
    def test_chaos_config_creation(self, chaos_config):
        """Test that chaos config can be created"""
        assert chaos_config is not None
        assert hasattr(chaos_config, 'pressure_update_interval')


class TestNarrativeModerator:
    """Test narrative intelligence weighting system"""
    
    @pytest.fixture
    def narrative_moderator(self, chaos_config):
        """Create narrative moderator for testing"""
        return NarrativeModerator(chaos_config)
    
    def test_narrative_moderator_initialization(self, narrative_moderator):
        """Test narrative moderator initializes correctly"""
        assert narrative_moderator.config is not None
        assert narrative_moderator.narrative_context is not None
        assert isinstance(narrative_moderator.narrative_context.current_genre, NarrativeGenre)
        assert isinstance(narrative_moderator.narrative_context.current_pacing, NarrativePacing)
    
    def test_narrative_context_creation(self):
        """Test narrative context creation"""
        context = NarrativeContext(
            current_genre=NarrativeGenre.POLITICAL_INTRIGUE,
            current_pacing=NarrativePacing.BUILDUP,
            recent_event_density=0.3,
            player_involvement_level=0.7,
            story_momentum=0.6
        )
        
        assert context.current_genre == NarrativeGenre.POLITICAL_INTRIGUE
        assert context.current_pacing == NarrativePacing.BUILDUP
        assert context.recent_event_density == 0.3
        assert context.player_involvement_level == 0.7
        assert context.story_momentum == 0.6
    
    def test_apply_narrative_weights(self, narrative_moderator, sample_pressure_data):
        """Test narrative weight application"""
        # Create test events
        events = [
            ChaosEvent(
                event_id="event1",
                event_type=ChaosEventType.POLITICAL_UPHEAVAL,
                title="Political Crisis",
                trigger_probability=0.5,
                affected_regions=["region1"]
            ),
            ChaosEvent(
                event_id="event2", 
                event_type=ChaosEventType.ECONOMIC_COLLAPSE,
                title="Market Crash",
                trigger_probability=0.4,
                affected_regions=["region1"]
            )
        ]
        
        base_probabilities = {
            "political_upheaval": 0.5,
            "economic_collapse": 0.4
        }
        
        # Apply narrative weights
        weighted_probs = narrative_moderator.apply_narrative_weights(
            events, sample_pressure_data, base_probabilities
        )
        
        assert isinstance(weighted_probs, dict)
        assert "political_upheaval" in weighted_probs
        assert "economic_collapse" in weighted_probs
        assert all(0.0 <= prob <= 1.0 for prob in weighted_probs.values())
    
    def test_record_event(self, narrative_moderator, sample_chaos_event):
        """Test event recording for narrative tracking"""
        initial_count = len(narrative_moderator.event_history)
        
        narrative_moderator.record_event(sample_chaos_event)
        
        assert len(narrative_moderator.event_history) == initial_count + 1
        assert narrative_moderator.event_history[-1][1].event_id == sample_chaos_event.event_id
    
    def test_get_narrative_status(self, narrative_moderator):
        """Test narrative status reporting"""
        status = narrative_moderator.get_narrative_status()
        
        assert isinstance(status, dict)
        assert 'current_genre' in status
        assert 'current_pacing' in status
        assert 'story_momentum' in status
        assert 'event_history_length' in status
        assert 'narrative_tension' in status


class TestWarningSystem:
    """Test the 3-tier warning escalation system"""
    
    @pytest.fixture
    def warning_system(self, chaos_config):
        """Create warning system for testing"""
        return WarningSystem(chaos_config)
    
    def test_warning_system_initialization(self, warning_system):
        """Test warning system initializes correctly"""
        assert warning_system.config is not None
        assert hasattr(warning_system, 'active_sequences')
        assert hasattr(warning_system, 'warning_templates')
        assert hasattr(warning_system, 'environmental_signs')
    
    def test_should_generate_warnings(self, warning_system):
        """Test warning generation decision logic"""
        # High chaos score should generate warnings for major events
        should_warn = warning_system.should_generate_warnings(
            ChaosEventType.POLITICAL_UPHEAVAL,
            EventSeverity.MAJOR,
            0.8
        )
        assert should_warn
        
        # Low chaos score should not generate warnings for minor events
        should_warn = warning_system.should_generate_warnings(
            ChaosEventType.SOCIAL_UNREST,
            EventSeverity.MINOR,
            0.2
        )
        assert not should_warn
    
    def test_generate_warning_sequence(self, warning_system):
        """Test warning sequence generation"""
        target_time = datetime.now() + timedelta(hours=48)
        
        sequence = warning_system.generate_warning_sequence(
            ChaosEventType.ECONOMIC_COLLAPSE,
            EventSeverity.MAJOR,
            ["region1", "region2"],
            target_time
        )
        
        assert sequence is not None
        assert sequence.target_event_type == ChaosEventType.ECONOMIC_COLLAPSE
        assert sequence.target_event_severity == EventSeverity.MAJOR
        assert set(sequence.target_regions) == {"region1", "region2"}
        assert sequence.target_event_time == target_time
        
        # Should have warnings for at least some phases (timing dependent)
        total_warnings = (len(sequence.rumor_warnings) + 
                         len(sequence.omen_warnings) + 
                         len(sequence.crisis_warnings))
        assert total_warnings > 0
    
    def test_warning_phases(self, warning_system):
        """Test different warning phases"""
        # Test all warning phases exist
        assert WarningPhase.RUMOR.value == "rumor"
        assert WarningPhase.OMEN.value == "omen"
        assert WarningPhase.CRISIS.value == "crisis"
    
    def test_get_active_warnings(self, warning_system):
        """Test active warning retrieval"""
        # Initially should have no active warnings
        active_warnings = warning_system.get_active_warnings()
        assert isinstance(active_warnings, list)
        assert len(active_warnings) == 0
    
    def test_warning_statistics(self, warning_system):
        """Test warning statistics"""
        stats = warning_system.get_warning_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_sequences' in stats
        assert 'active_sequences' in stats
        assert 'completed_sequences' in stats
        assert 'mitigated_sequences' in stats


class TestCascadeEngine:
    """Test cascading effects system"""
    
    @pytest.fixture 
    def cascade_engine(self, chaos_config):
        """Create cascade engine for testing"""
        return CascadeEngine(chaos_config)
    
    def test_cascade_engine_initialization(self, cascade_engine):
        """Test cascade engine initializes correctly"""
        assert cascade_engine.config is not None
        assert hasattr(cascade_engine, 'cascade_rules')
        assert hasattr(cascade_engine, 'scheduled_cascades')
        assert len(cascade_engine.cascade_rules) > 0
    
    def test_cascade_types(self):
        """Test cascade type enumeration"""
        assert CascadeType.IMMEDIATE.value == "immediate"
        assert CascadeType.DELAYED.value == "delayed"
        assert CascadeType.CONDITIONAL.value == "conditional"
        assert CascadeType.AMPLIFYING.value == "amplifying"
        assert CascadeType.MITIGATING.value == "mitigating"
    
    def test_cascade_rule_probability_calculation(self, sample_chaos_event):
        """Test cascade rule probability calculation"""
        rule = CascadeRule(
            trigger_event_type=ChaosEventType.POLITICAL_UPHEAVAL,
            cascade_event_type=ChaosEventType.ECONOMIC_COLLAPSE,
            base_probability=0.4,
            cascade_type=CascadeType.DELAYED
        )
        
        world_context = {
            'economic_pressure': 0.7,
            'political_pressure': 0.8
        }
        
        probability = rule.calculate_cascade_probability(sample_chaos_event, world_context)
        
        assert isinstance(probability, float)
        assert 0.0 <= probability <= 1.0
    
    @pytest.mark.asyncio
    async def test_process_event_cascades(self, cascade_engine, sample_chaos_event):
        """Test cascade processing from events"""
        world_context = {
            'economic_pressure': 0.6,
            'political_pressure': 0.7,
            'chaos_score': 0.75
        }
        
        cascade_events = await cascade_engine.process_event_cascades(
            sample_chaos_event, world_context
        )
        
        assert isinstance(cascade_events, list)
        # May or may not have cascades depending on probability rolls
        for cascade in cascade_events:
            assert isinstance(cascade, CascadeEvent)
            assert cascade.trigger_event_id == sample_chaos_event.event_id
    
    @pytest.mark.asyncio 
    async def test_process_due_cascades(self, cascade_engine):
        """Test processing of due cascade events"""
        due_cascades = await cascade_engine.process_due_cascades()
        
        assert isinstance(due_cascades, list)
        # Initially should be empty
        assert len(due_cascades) == 0
    
    def test_get_cascade_statistics(self, cascade_engine):
        """Test cascade statistics"""
        stats = cascade_engine.get_cascade_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_completed_cascades' in stats
        assert 'total_scheduled_cascades' in stats
        assert 'cascade_type_distribution' in stats
        assert 'common_cascade_patterns' in stats
        assert 'average_cascade_delay' in stats


class TestIntegratedChaosSystem:
    """Test the complete integrated chaos system"""
    
    @pytest.fixture
    def mock_event_dispatcher(self):
        """Create mock event dispatcher"""
        dispatcher = Mock()
        dispatcher.publish = AsyncMock()
        return dispatcher
    
    @pytest.mark.asyncio
    async def test_chaos_engine_with_new_components(self, chaos_config, mock_event_dispatcher):
        """Test chaos engine with all new components integrated"""
        # Create chaos engine (will automatically include new components)
        with patch('backend.systems.chaos.core.system_integrator.SystemIntegrator') as mock_integrator:
            mock_integrator.return_value.initialize = AsyncMock()
            mock_integrator.return_value.dispatch_chaos_event = AsyncMock()
            mock_integrator.return_value.dispatch_warning_event = AsyncMock()
            
            engine = ChaosEngine(chaos_config)
            
            # Verify new components are initialized
            assert hasattr(engine, 'narrative_moderator')
            assert hasattr(engine, 'warning_system')
            assert hasattr(engine, 'cascade_engine')
            
            assert isinstance(engine.narrative_moderator, NarrativeModerator)
            assert isinstance(engine.warning_system, WarningSystem)
            assert isinstance(engine.cascade_engine, CascadeEngine)
    
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self, chaos_config):
        """Test complete workflow with all components"""
        # Create individual components
        narrative_moderator = NarrativeModerator(chaos_config)
        warning_system = WarningSystem(chaos_config)
        cascade_engine = CascadeEngine(chaos_config)
        
        # Create test data
        pressure_data = PressureData()
        pressure_data.economic_instability = 0.8
        pressure_data.faction_conflict = 0.7
        
        chaos_result = ChaosCalculationResult(
            chaos_score=0.8,
            chaos_level=ChaosLevel.CRITICAL,
            regional_scores={'region1': 0.9},
            source_contributions={'economic_instability': 0.8},
            temporal_factors={}
        )
        
        # Test narrative intelligence
        test_events = [
            ChaosEvent(
                event_id="test1",
                event_type=ChaosEventType.ECONOMIC_COLLAPSE,
                title="Market Crash",
                trigger_probability=0.7,
                affected_regions=["region1"]
            )
        ]
        
        base_probs = {"economic_collapse": 0.7}
        
        weighted_probs = narrative_moderator.apply_narrative_weights(
            test_events, pressure_data, base_probs
        )
        
        assert isinstance(weighted_probs, dict)
        assert "economic_collapse" in weighted_probs
        
        # Test warning generation
        should_warn = warning_system.should_generate_warnings(
            ChaosEventType.ECONOMIC_COLLAPSE,
            EventSeverity.MAJOR,
            chaos_result.chaos_score
        )
        
        assert should_warn  # High chaos score should trigger warnings
        
        # Test cascade processing
        world_context = {
            'economic_pressure': pressure_data.economic_instability,
            'chaos_score': chaos_result.chaos_score
        }
        
        cascades = await cascade_engine.process_event_cascades(
            test_events[0], world_context
        )
        
        assert isinstance(cascades, list)
    
    def test_component_statistics_integration(self, chaos_config):
        """Test that all components provide proper statistics"""
        narrative_moderator = NarrativeModerator(chaos_config)
        warning_system = WarningSystem(chaos_config)
        cascade_engine = CascadeEngine(chaos_config)
        
        # Test narrative statistics
        narrative_stats = narrative_moderator.get_narrative_status()
        assert isinstance(narrative_stats, dict)
        
        # Test warning statistics  
        warning_stats = warning_system.get_warning_statistics()
        assert isinstance(warning_stats, dict)
        
        # Test cascade statistics
        cascade_stats = cascade_engine.get_cascade_statistics()
        assert isinstance(cascade_stats, dict)


@pytest.mark.integration
class TestChaoSystemPerformance:
    """Test chaos system performance and reliability"""
    
    @pytest.mark.asyncio
    async def test_system_can_handle_high_load(self, chaos_config):
        """Test system handles multiple rapid events"""
        narrative_moderator = NarrativeModerator(chaos_config)
        
        # Create many test events
        events = []
        for i in range(100):
            event = ChaosEvent(
                event_id=f"event_{i}",
                event_type=ChaosEventType.SOCIAL_UNREST,
                title=f"Event {i}",
                trigger_probability=0.5,
                affected_regions=["region1"]
            )
            events.append(event)
        
        pressure_data = PressureData()
        pressure_data.population_stress = 0.8
        
        # Create base probabilities for each unique event type
        base_probs = {"social_unrest": 0.5}
        
        # Should handle large number of events without error
        weighted_probs = narrative_moderator.apply_narrative_weights(
            events, pressure_data, base_probs
        )
        
        # The narrative moderator groups by event type, so we expect 1 result for social_unrest
        assert len(weighted_probs) == 1
        assert "social_unrest" in weighted_probs
        assert isinstance(weighted_probs["social_unrest"], float)
    
    def test_memory_usage_reasonable(self, chaos_config):
        """Test that components don't consume excessive memory"""
        narrative_moderator = NarrativeModerator(chaos_config)
        warning_system = WarningSystem(chaos_config)
        cascade_engine = CascadeEngine(chaos_config)
        
        # Add many events and check memory usage remains reasonable
        for i in range(1000):
            event = ChaosEvent(
                event_id=f"event_{i}",
                event_type=ChaosEventType.SOCIAL_UNREST,
                title=f"Event {i}",
                affected_regions=["region1"]
            )
            narrative_moderator.record_event(event)
        
        # Should auto-cleanup old events (keeps last 100)
        assert len(narrative_moderator.event_history) <= 100 