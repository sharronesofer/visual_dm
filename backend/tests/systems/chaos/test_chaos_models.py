"""
Comprehensive Tests for Chaos System Models

Tests for all chaos system data models including:
- ChaosState and related enums
- ChaosEvents and event types
- PressureData and pressure monitoring models
- Model validation and serialization
- WebSocket compatibility for Unity frontend
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from unittest.mock import Mock, patch

from backend.systems.chaos.models.chaos_state import (
    ChaosState, ChaosLevel, ChaosMetrics, ChaosHistory,
    ChaosConfiguration, ChaosThreshold
)
from backend.systems.chaos.models.chaos_events import (
    ChaosEvent, ChaosEventType, EventSeverity, EventStatus,
    PoliticalUpheavalEvent, NaturalDisasterEvent, EconomicCollapseEvent,
    WarOutbreakEvent, ResourceScarcityEvent, FactionBetrayalEvent,
    CharacterRevelationEvent, EventMetadata, EventEffect
)
from backend.systems.chaos.models.pressure_data import (
    PressureData, PressureReading, PressureSource, PressureMetrics,
    PressureHistory, PressureTrend
)


class TestChaosState:
    """Test ChaosState model and related classes"""
    
    def test_chaos_level_enum_values(self):
        """Test ChaosLevel enum has all required values"""
        expected_levels = [
            'DORMANT', 'STABLE', 'MODERATE', 'HIGH', 'CRITICAL', 'CATASTROPHIC'
        ]
        
        for level_name in expected_levels:
            assert hasattr(ChaosLevel, level_name)
            level = getattr(ChaosLevel, level_name)
            assert isinstance(level, ChaosLevel)
    
    def test_chaos_level_ordering(self):
        """Test ChaosLevel enum ordering from lowest to highest"""
        levels = [
            ChaosLevel.DORMANT,
            ChaosLevel.STABLE,
            ChaosLevel.MODERATE,
            ChaosLevel.HIGH,
            ChaosLevel.CRITICAL,
            ChaosLevel.CATASTROPHIC
        ]
        
        # Test that each level is greater than the previous
        for i in range(1, len(levels)):
            assert levels[i].value > levels[i-1].value
    
    def test_chaos_state_initialization(self):
        """Test ChaosState initialization with default values"""
        state = ChaosState()
        
        assert state.chaos_level == ChaosLevel.DORMANT
        assert state.chaos_score == 0.0
        assert isinstance(state.last_updated, datetime)
        assert state.active_events == []
        assert state.pressure_sources == {}
        assert state.mitigation_factors == {}
        assert isinstance(state.state_id, str)
    
    def test_chaos_state_with_custom_values(self):
        """Test ChaosState initialization with custom values"""
        custom_time = datetime.now() - timedelta(hours=1)
        custom_events = ['event1', 'event2']
        custom_pressure = {'political': 0.7, 'economic': 0.5}
        custom_mitigation = {'diplomatic': 0.3}
        
        state = ChaosState(
            chaos_level=ChaosLevel.HIGH,
            chaos_score=0.8,
            last_updated=custom_time,
            active_events=custom_events,
            pressure_sources=custom_pressure,
            mitigation_factors=custom_mitigation
        )
        
        assert state.chaos_level == ChaosLevel.HIGH
        assert state.chaos_score == 0.8
        assert state.last_updated == custom_time
        assert state.active_events == custom_events
        assert state.pressure_sources == custom_pressure
        assert state.mitigation_factors == custom_mitigation
    
    def test_chaos_state_validation(self):
        """Test ChaosState validation rules"""
        # Test chaos_score bounds
        with pytest.raises(ValueError):
            ChaosState(chaos_score=-0.1)  # Below minimum
        
        with pytest.raises(ValueError):
            ChaosState(chaos_score=1.1)   # Above maximum
        
        # Valid boundary values should work
        state_min = ChaosState(chaos_score=0.0)
        state_max = ChaosState(chaos_score=1.0)
        assert state_min.chaos_score == 0.0
        assert state_max.chaos_score == 1.0
    
    def test_chaos_state_serialization(self):
        """Test ChaosState serialization for API/WebSocket compatibility"""
        state = ChaosState(
            chaos_level=ChaosLevel.MODERATE,
            chaos_score=0.6,
            active_events=['event1'],
            pressure_sources={'political': 0.7}
        )
        
        # Test dict conversion
        state_dict = state.to_dict()
        assert isinstance(state_dict, dict)
        assert state_dict['chaos_level'] == 'MODERATE'
        assert state_dict['chaos_score'] == 0.6
        assert 'last_updated' in state_dict
        assert state_dict['active_events'] == ['event1']
        assert state_dict['pressure_sources'] == {'political': 0.7}
    
    def test_chaos_state_deserialization(self):
        """Test ChaosState deserialization from dict"""
        state_data = {
            'chaos_level': 'HIGH',
            'chaos_score': 0.75,
            'active_events': ['event1', 'event2'],
            'pressure_sources': {'economic': 0.8},
            'mitigation_factors': {'diplomatic': 0.2}
        }
        
        state = ChaosState.from_dict(state_data)
        assert state.chaos_level == ChaosLevel.HIGH
        assert state.chaos_score == 0.75
        assert state.active_events == ['event1', 'event2']
        assert state.pressure_sources == {'economic': 0.8}
        assert state.mitigation_factors == {'diplomatic': 0.2}
    
    def test_chaos_metrics_initialization(self):
        """Test ChaosMetrics model initialization"""
        metrics = ChaosMetrics()
        
        assert metrics.total_events_triggered == 0
        assert metrics.average_chaos_score == 0.0
        assert metrics.peak_chaos_score == 0.0
        assert metrics.time_in_high_chaos == timedelta(0)
        assert metrics.mitigation_effectiveness == 0.0
        assert isinstance(metrics.last_calculated, datetime)
    
    def test_chaos_history_tracking(self):
        """Test ChaosHistory model for tracking state changes"""
        history = ChaosHistory()
        
        # Add some history entries
        history.add_entry(ChaosLevel.STABLE, 0.3, datetime.now())
        history.add_entry(ChaosLevel.MODERATE, 0.5, datetime.now())
        
        assert len(history.entries) == 2
        assert history.entries[0].chaos_level == ChaosLevel.STABLE
        assert history.entries[1].chaos_level == ChaosLevel.MODERATE
        
        # Test history analysis
        trend = history.get_trend()
        assert trend in ['increasing', 'decreasing', 'stable']


class TestChaosEvents:
    """Test ChaosEvent models and event types"""
    
    def test_chaos_event_type_enum(self):
        """Test ChaosEventType enum has all required event types"""
        expected_types = [
            'POLITICAL_UPHEAVAL', 'NATURAL_DISASTER', 'ECONOMIC_COLLAPSE',
            'WAR_OUTBREAK', 'RESOURCE_SCARCITY', 'FACTION_BETRAYAL',
            'CHARACTER_REVELATION'
        ]
        
        for event_type in expected_types:
            assert hasattr(ChaosEventType, event_type)
    
    def test_event_severity_enum(self):
        """Test EventSeverity enum ordering"""
        severities = [
            EventSeverity.MINOR,
            EventSeverity.MODERATE,
            EventSeverity.MAJOR,
            EventSeverity.CRITICAL,
            EventSeverity.CATASTROPHIC
        ]
        
        # Test ordering
        for i in range(1, len(severities)):
            assert severities[i].value > severities[i-1].value
    
    def test_event_status_enum(self):
        """Test EventStatus enum values"""
        expected_statuses = ['PENDING', 'ACTIVE', 'RESOLVED', 'CANCELLED']
        
        for status in expected_statuses:
            assert hasattr(EventStatus, status)
    
    def test_base_chaos_event_initialization(self):
        """Test base ChaosEvent initialization"""
        event = ChaosEvent(
            event_type=ChaosEventType.POLITICAL_UPHEAVAL,
            severity=EventSeverity.MODERATE,
            affected_regions=['region1', 'region2'],
            description="Test political upheaval"
        )
        
        assert event.event_type == ChaosEventType.POLITICAL_UPHEAVAL
        assert event.severity == EventSeverity.MODERATE
        assert event.affected_regions == ['region1', 'region2']
        assert event.description == "Test political upheaval"
        assert event.status == EventStatus.PENDING
        assert isinstance(event.event_id, str)
        assert isinstance(event.triggered_at, datetime)
    
    def test_chaos_event_validation(self):
        """Test ChaosEvent validation rules"""
        # Test required fields
        with pytest.raises(ValueError):
            ChaosEvent(event_type=None)
        
        with pytest.raises(ValueError):
            ChaosEvent(
                event_type=ChaosEventType.POLITICAL_UPHEAVAL,
                affected_regions=[]  # Empty regions not allowed
            )
    
    def test_political_upheaval_event(self):
        """Test PoliticalUpheavalEvent specific functionality"""
        event = PoliticalUpheavalEvent(
            affected_regions=['capital_region'],
            severity=EventSeverity.MAJOR,
            government_type='monarchy',
            rebellion_strength=0.7,
            affected_factions=['nobles', 'commoners']
        )
        
        assert event.event_type == ChaosEventType.POLITICAL_UPHEAVAL
        assert event.government_type == 'monarchy'
        assert event.rebellion_strength == 0.7
        assert event.affected_factions == ['nobles', 'commoners']
        assert 'political' in event.description.lower()
    
    def test_natural_disaster_event(self):
        """Test NaturalDisasterEvent specific functionality"""
        event = NaturalDisasterEvent(
            affected_regions=['coastal_region'],
            severity=EventSeverity.CRITICAL,
            disaster_type='earthquake',
            magnitude=7.5,
            duration_hours=48
        )
        
        assert event.event_type == ChaosEventType.NATURAL_DISASTER
        assert event.disaster_type == 'earthquake'
        assert event.magnitude == 7.5
        assert event.duration_hours == 48
        assert 'earthquake' in event.description.lower()
    
    def test_economic_collapse_event(self):
        """Test EconomicCollapseEvent specific functionality"""
        event = EconomicCollapseEvent(
            affected_regions=['trade_hub'],
            severity=EventSeverity.MAJOR,
            collapse_type='market_crash',
            affected_resources=['gold', 'grain'],
            economic_impact=0.8
        )
        
        assert event.event_type == ChaosEventType.ECONOMIC_COLLAPSE
        assert event.collapse_type == 'market_crash'
        assert event.affected_resources == ['gold', 'grain']
        assert event.economic_impact == 0.8
    
    def test_war_outbreak_event(self):
        """Test WarOutbreakEvent specific functionality"""
        event = WarOutbreakEvent(
            affected_regions=['border_region'],
            severity=EventSeverity.CRITICAL,
            aggressor_faction='orcs',
            defender_faction='humans',
            war_type='territorial',
            estimated_duration_days=90
        )
        
        assert event.event_type == ChaosEventType.WAR_OUTBREAK
        assert event.aggressor_faction == 'orcs'
        assert event.defender_faction == 'humans'
        assert event.war_type == 'territorial'
        assert event.estimated_duration_days == 90
    
    def test_resource_scarcity_event(self):
        """Test ResourceScarcityEvent specific functionality"""
        event = ResourceScarcityEvent(
            affected_regions=['farming_region'],
            severity=EventSeverity.MODERATE,
            scarce_resources=['food', 'water'],
            scarcity_level=0.6,
            cause='drought'
        )
        
        assert event.event_type == ChaosEventType.RESOURCE_SCARCITY
        assert event.scarce_resources == ['food', 'water']
        assert event.scarcity_level == 0.6
        assert event.cause == 'drought'
    
    def test_faction_betrayal_event(self):
        """Test FactionBetrayalEvent specific functionality"""
        event = FactionBetrayalEvent(
            affected_regions=['political_center'],
            severity=EventSeverity.MAJOR,
            betraying_faction='nobles',
            betrayed_faction='crown',
            betrayal_type='political_coup',
            trust_impact=0.9
        )
        
        assert event.event_type == ChaosEventType.FACTION_BETRAYAL
        assert event.betraying_faction == 'nobles'
        assert event.betrayed_faction == 'crown'
        assert event.betrayal_type == 'political_coup'
        assert event.trust_impact == 0.9
    
    def test_character_revelation_event(self):
        """Test CharacterRevelationEvent specific functionality"""
        event = CharacterRevelationEvent(
            affected_regions=['story_region'],
            severity=EventSeverity.MODERATE,
            character_id='char_123',
            revelation_type='secret_identity',
            revelation_content='The merchant is actually a spy',
            narrative_impact=0.7
        )
        
        assert event.event_type == ChaosEventType.CHARACTER_REVELATION
        assert event.character_id == 'char_123'
        assert event.revelation_type == 'secret_identity'
        assert event.revelation_content == 'The merchant is actually a spy'
        assert event.narrative_impact == 0.7
    
    def test_event_serialization(self):
        """Test event serialization for WebSocket compatibility"""
        event = PoliticalUpheavalEvent(
            affected_regions=['test_region'],
            severity=EventSeverity.MODERATE,
            government_type='democracy',
            rebellion_strength=0.5
        )
        
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict['event_type'] == 'POLITICAL_UPHEAVAL'
        assert event_dict['severity'] == 'MODERATE'
        assert event_dict['government_type'] == 'democracy'
        assert 'event_id' in event_dict
        assert 'triggered_at' in event_dict
    
    def test_event_metadata(self):
        """Test EventMetadata model"""
        metadata = EventMetadata(
            source_system='chaos',
            trigger_reason='pressure_threshold_exceeded',
            related_events=['event1', 'event2'],
            custom_data={'key': 'value'}
        )
        
        assert metadata.source_system == 'chaos'
        assert metadata.trigger_reason == 'pressure_threshold_exceeded'
        assert metadata.related_events == ['event1', 'event2']
        assert metadata.custom_data == {'key': 'value'}
    
    def test_event_effects(self):
        """Test EventEffect model for tracking event consequences"""
        effect = EventEffect(
            effect_type='economic',
            target_system='economy',
            magnitude=0.7,
            duration_hours=24,
            description='Market instability'
        )
        
        assert effect.effect_type == 'economic'
        assert effect.target_system == 'economy'
        assert effect.magnitude == 0.7
        assert effect.duration_hours == 24
        assert effect.description == 'Market instability'


class TestPressureData:
    """Test PressureData models and pressure monitoring"""
    
    def test_pressure_source_enum(self):
        """Test PressureSource enum values"""
        expected_sources = [
            'POLITICAL', 'ECONOMIC', 'FACTION_TENSION', 'POPULATION_STRESS',
            'MILITARY_BUILDUP', 'ENVIRONMENTAL', 'DIPLOMATIC', 'RESOURCE'
        ]
        
        for source in expected_sources:
            assert hasattr(PressureSource, source)
    
    def test_pressure_data_initialization(self):
        """Test PressureData initialization"""
        pressure_data = PressureData()
        
        assert pressure_data.global_pressure == 0.0
        assert pressure_data.pressure_sources == {}
        assert pressure_data.regional_pressure == {}
        assert isinstance(pressure_data.last_updated, datetime)
        assert isinstance(pressure_data.data_id, str)
    
    def test_pressure_data_with_values(self):
        """Test PressureData with custom values"""
        pressure_sources = {
            'political': 0.7,
            'economic': 0.5,
            'faction_tension': 0.8
        }
        regional_pressure = {
            'region1': 0.6,
            'region2': 0.4
        }
        
        pressure_data = PressureData(
            global_pressure=0.6,
            pressure_sources=pressure_sources,
            regional_pressure=regional_pressure
        )
        
        assert pressure_data.global_pressure == 0.6
        assert pressure_data.pressure_sources == pressure_sources
        assert pressure_data.regional_pressure == regional_pressure
    
    def test_pressure_data_validation(self):
        """Test PressureData validation rules"""
        # Test pressure bounds
        with pytest.raises(ValueError):
            PressureData(global_pressure=-0.1)
        
        with pytest.raises(ValueError):
            PressureData(global_pressure=1.1)
        
        # Test pressure source bounds
        with pytest.raises(ValueError):
            PressureData(pressure_sources={'political': 1.5})
    
    def test_pressure_reading_model(self):
        """Test PressureReading model for individual readings"""
        reading = PressureReading(
            source=PressureSource.POLITICAL,
            value=0.7,
            region_id='test_region',
            timestamp=datetime.now(),
            metadata={'source_detail': 'election_tension'}
        )
        
        assert reading.source == PressureSource.POLITICAL
        assert reading.value == 0.7
        assert reading.region_id == 'test_region'
        assert reading.metadata == {'source_detail': 'election_tension'}
    
    def test_pressure_metrics_calculation(self):
        """Test PressureMetrics model for analytics"""
        metrics = PressureMetrics()
        
        # Add some sample readings
        readings = [
            PressureReading(PressureSource.POLITICAL, 0.5),
            PressureReading(PressureSource.POLITICAL, 0.7),
            PressureReading(PressureSource.POLITICAL, 0.6)
        ]
        
        metrics.calculate_from_readings(readings)
        
        assert metrics.average_pressure == 0.6
        assert metrics.peak_pressure == 0.7
        assert metrics.pressure_variance > 0
    
    def test_pressure_trend_analysis(self):
        """Test PressureTrend model for trend analysis"""
        trend = PressureTrend()
        
        # Add historical data points
        timestamps = [
            datetime.now() - timedelta(hours=3),
            datetime.now() - timedelta(hours=2),
            datetime.now() - timedelta(hours=1),
            datetime.now()
        ]
        values = [0.3, 0.5, 0.7, 0.8]
        
        for timestamp, value in zip(timestamps, values):
            trend.add_data_point(timestamp, value)
        
        trend_direction = trend.calculate_trend()
        assert trend_direction == 'increasing'
        
        slope = trend.get_slope()
        assert slope > 0  # Positive slope for increasing trend
    
    def test_pressure_history_tracking(self):
        """Test PressureHistory model for historical data"""
        history = PressureHistory()
        
        # Add historical pressure data
        for i in range(5):
            timestamp = datetime.now() - timedelta(hours=i)
            pressure_data = PressureData(
                global_pressure=0.5 + (i * 0.1),
                pressure_sources={'political': 0.4 + (i * 0.1)}
            )
            history.add_entry(timestamp, pressure_data)
        
        assert len(history.entries) == 5
        
        # Test historical analysis
        avg_pressure = history.get_average_pressure(hours=24)
        assert 0.5 <= avg_pressure <= 0.9
        
        peak_pressure = history.get_peak_pressure(hours=24)
        assert peak_pressure == 0.9
    
    def test_pressure_data_serialization(self):
        """Test PressureData serialization for WebSocket compatibility"""
        pressure_data = PressureData(
            global_pressure=0.6,
            pressure_sources={'political': 0.7, 'economic': 0.5},
            regional_pressure={'region1': 0.8}
        )
        
        data_dict = pressure_data.to_dict()
        assert isinstance(data_dict, dict)
        assert data_dict['global_pressure'] == 0.6
        assert data_dict['pressure_sources'] == {'political': 0.7, 'economic': 0.5}
        assert data_dict['regional_pressure'] == {'region1': 0.8}
        assert 'last_updated' in data_dict
        assert 'data_id' in data_dict
    
    def test_pressure_data_deserialization(self):
        """Test PressureData deserialization from dict"""
        data_dict = {
            'global_pressure': 0.75,
            'pressure_sources': {'faction_tension': 0.8},
            'regional_pressure': {'region2': 0.6}
        }
        
        pressure_data = PressureData.from_dict(data_dict)
        assert pressure_data.global_pressure == 0.75
        assert pressure_data.pressure_sources == {'faction_tension': 0.8}
        assert pressure_data.regional_pressure == {'region2': 0.6}


class TestModelIntegration:
    """Test integration between different model types"""
    
    def test_chaos_state_with_events(self):
        """Test ChaosState integration with ChaosEvents"""
        # Create some events
        event1 = PoliticalUpheavalEvent(
            affected_regions=['region1'],
            severity=EventSeverity.MODERATE
        )
        event2 = EconomicCollapseEvent(
            affected_regions=['region2'],
            severity=EventSeverity.MAJOR
        )
        
        # Create chaos state with events
        state = ChaosState(
            chaos_level=ChaosLevel.HIGH,
            chaos_score=0.8,
            active_events=[event1.event_id, event2.event_id]
        )
        
        assert len(state.active_events) == 2
        assert event1.event_id in state.active_events
        assert event2.event_id in state.active_events
    
    def test_pressure_data_to_chaos_state_conversion(self):
        """Test converting PressureData to ChaosState"""
        pressure_data = PressureData(
            global_pressure=0.8,
            pressure_sources={
                'political': 0.9,
                'economic': 0.7,
                'faction_tension': 0.8
            }
        )
        
        # Convert to chaos state (this would be done by chaos engine)
        chaos_state = ChaosState.from_pressure_data(pressure_data)
        
        assert chaos_state.chaos_score == pressure_data.global_pressure
        assert chaos_state.pressure_sources == pressure_data.pressure_sources
        assert chaos_state.chaos_level in [ChaosLevel.HIGH, ChaosLevel.CRITICAL]
    
    def test_websocket_compatibility(self):
        """Test that all models are WebSocket compatible for Unity frontend"""
        # Test ChaosState
        state = ChaosState(chaos_level=ChaosLevel.MODERATE, chaos_score=0.6)
        state_json = state.to_json()
        assert isinstance(state_json, str)
        
        # Test ChaosEvent
        event = PoliticalUpheavalEvent(
            affected_regions=['test'],
            severity=EventSeverity.MODERATE
        )
        event_json = event.to_json()
        assert isinstance(event_json, str)
        
        # Test PressureData
        pressure = PressureData(global_pressure=0.5)
        pressure_json = pressure.to_json()
        assert isinstance(pressure_json, str)
    
    def test_model_performance(self):
        """Test model performance for real-time gameplay"""
        import time
        
        # Test rapid state updates
        start_time = time.time()
        
        for i in range(1000):
            state = ChaosState(
                chaos_score=i / 1000.0,
                chaos_level=ChaosLevel.MODERATE
            )
            state_dict = state.to_dict()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 1000 operations in under 1 second
        assert duration < 1.0
        
        # Test event creation performance
        start_time = time.time()
        
        for i in range(100):
            event = PoliticalUpheavalEvent(
                affected_regions=[f'region_{i}'],
                severity=EventSeverity.MODERATE
            )
            event_dict = event.to_dict()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 event operations in under 0.5 seconds
        assert duration < 0.5 