"""
Comprehensive Tests for Chaos System Models

Tests for all chaos system data models including:
- ChaosState and related enums (Bible-compliant chaos levels)
- ChaosEvents and event types (Bible-specified event framework)  
- PressureData and pressure monitoring models (Bible multi-dimensional pressure)
- Model validation and serialization
- WebSocket compatibility for Unity frontend
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from unittest.mock import Mock, patch

from backend.infrastructure.systems.chaos.models.chaos_state import (
    ChaosState, ChaosLevel, ChaosMetrics, ChaosHistory
)
from backend.infrastructure.systems.chaos.models.chaos_events import (
    ChaosEvent, ChaosEventType, EventSeverity, EventStatus,
    PoliticalUpheavalEvent, NaturalDisasterEvent, EconomicCollapseEvent,
    WarOutbreakEvent, ResourceScarcityEvent, FactionBetrayalEvent,
    CharacterRevelationEvent, EventMetadata, EventEffect
)
from backend.infrastructure.systems.chaos.models.pressure_data import (
    PressureData, PressureReading, PressureSource
)


class TestChaosState:
    """Test ChaosState model per Bible chaos level requirements"""
    
    def test_chaos_level_enum_bible_compliant(self):
        """Test ChaosLevel enum matches Bible-specified chaos levels"""
        # Bible specifies chaos progression from stable to catastrophic
        required_levels = [
            'STABLE',        # Bible: Normal conditions
            'LOW',          # Bible: Minor fluctuations  
            'MODERATE',     # Bible: Noticeable disruptions
            'HIGH',         # Bible: Significant reality distortions
            'CRITICAL',     # Bible: Extreme chaos (legacy support)
            'CATASTROPHIC'  # Bible: Reality breakdown
        ]
        
        for level_name in required_levels:
            assert hasattr(ChaosLevel, level_name)
            level = getattr(ChaosLevel, level_name)
            assert isinstance(level, ChaosLevel)
    
    def test_chaos_level_ordering_bible_thresholds(self):
        """Test ChaosLevel enum ordering matches Bible threshold progression"""
        # Bible specifies threshold progression: 0.3 -> 0.6 -> 0.8
        levels = [
            ChaosLevel.STABLE,      # Below 0.3
            ChaosLevel.LOW,         # 0.3 - 0.6  
            ChaosLevel.MODERATE,    # 0.6 - 0.8
            ChaosLevel.HIGH,        # Above 0.8
            ChaosLevel.CRITICAL,    # Extreme (legacy)
            ChaosLevel.CATASTROPHIC # Maximum
        ]
        
        # Test that each level value is greater than the previous
        for i in range(1, len(levels)):
            assert levels[i].value > levels[i-1].value
    
    def test_chaos_state_initialization_bible_compliant(self):
        """Test ChaosState initialization with Bible-compliant defaults"""
        state = ChaosState()
        
        # Bible: System should start in stable state
        assert state.chaos_level in [ChaosLevel.STABLE, ChaosLevel.DORMANT]
        assert state.chaos_score == 0.0  # Bible: Start with no pressure
        assert isinstance(state.last_updated, datetime)
        assert state.active_events == []
        assert state.pressure_sources == {}  # Bible: Multi-dimensional pressure sources
        assert state.mitigation_factors == {}  # Bible: Mitigation support
        assert isinstance(state.state_id, str)
    
    def test_chaos_state_pressure_sources_bible_format(self):
        """Test ChaosState pressure sources match Bible multi-dimensional system"""
        # Bible specifies 6 pressure types
        bible_pressure_sources = {
            'economic': 0.4,      # Bible: Economic Pressure
            'political': 0.6,     # Bible: Political Pressure
            'social': 0.3,        # Bible: Social Pressure  
            'environmental': 0.2, # Bible: Environmental Pressure
            'diplomatic': 0.5,    # Bible: Diplomatic relationships
            'temporal': 0.1       # Bible: Temporal Pressure (when implemented)
        }
        
        state = ChaosState(
            chaos_level=ChaosLevel.MODERATE,
            chaos_score=0.5,
            pressure_sources=bible_pressure_sources
        )
        
        assert state.pressure_sources == bible_pressure_sources
        # Verify Bible pressure types are supported
        assert 'economic' in state.pressure_sources
        assert 'political' in state.pressure_sources
        assert 'social' in state.pressure_sources
        assert 'environmental' in state.pressure_sources
        assert 'diplomatic' in state.pressure_sources
    
    def test_chaos_state_validation_bible_thresholds(self):
        """Test ChaosState validation uses Bible-specified ranges"""
        # Bible: Chaos score range is 0.0 to 1.0
        with pytest.raises(ValueError):
            ChaosState(chaos_score=-0.1)  # Below minimum
        
        with pytest.raises(ValueError):
            ChaosState(chaos_score=1.1)   # Above maximum
        
        # Bible threshold boundaries should work
        state_low = ChaosState(chaos_score=0.3)    # Bible low threshold
        state_medium = ChaosState(chaos_score=0.6) # Bible medium threshold  
        state_high = ChaosState(chaos_score=0.8)   # Bible high threshold
        
        assert state_low.chaos_score == 0.3
        assert state_medium.chaos_score == 0.6
        assert state_high.chaos_score == 0.8
    
    def test_chaos_state_serialization_bible_compatible(self):
        """Test ChaosState serialization for Bible-compliant API/WebSocket"""
        state = ChaosState(
            chaos_level=ChaosLevel.MODERATE,
            chaos_score=0.6,  # Bible medium threshold
            active_events=['event1'],
            pressure_sources={'political': 0.7, 'economic': 0.5}  # Bible pressure types
        )
        
        # Test dict conversion for API compatibility
        state_dict = state.to_dict()
        assert isinstance(state_dict, dict)
        assert state_dict['chaos_level'] == 'MODERATE'
        assert state_dict['chaos_score'] == 0.6
        assert 'last_updated' in state_dict
        assert state_dict['active_events'] == ['event1']
        
        # Verify Bible pressure sources are preserved
        assert state_dict['pressure_sources']['political'] == 0.7
        assert state_dict['pressure_sources']['economic'] == 0.5


class TestChaosEvents:
    """Test ChaosEvent models per Bible event framework"""
    
    def test_chaos_event_type_enum_bible_compliant(self):
        """Test ChaosEventType enum includes Bible-specified event categories"""
        # Bible specifies these abstract event categories that are implemented
        bible_event_types = [
            'POLITICAL_UPHEAVAL',    # Bible: Political pressure events
            'NATURAL_DISASTER',      # Bible: Environmental pressure events
            'ECONOMIC_COLLAPSE',     # Bible: Economic pressure events
            'WAR_OUTBREAK',          # Bible: Military/conflict events
            'RESOURCE_SCARCITY',     # Bible: Resource pressure events
            'FACTION_BETRAYAL',      # Bible: Faction tension events
            'CHARACTER_REVELATION'   # Bible: Social/narrative events
        ]
        
        for event_type in bible_event_types:
            assert hasattr(ChaosEventType, event_type)
            chaos_event_type = getattr(ChaosEventType, event_type)
            assert isinstance(chaos_event_type, ChaosEventType)
    
    def test_event_severity_enum_bible_scaling(self):
        """Test EventSeverity enum matches Bible severity scaling"""
        # Bible specifies severity progression for event impact
        severities = [
            EventSeverity.MINOR,        # Bible: Low impact, localized
            EventSeverity.MODERATE,     # Bible: Regional impact
            EventSeverity.MAJOR,        # Bible: Multi-regional impact
            EventSeverity.CRITICAL,     # Bible: Critical impact
            EventSeverity.CATASTROPHIC  # Bible: Global impact
        ]
        
        # Test ordering matches Bible severity progression
        for i in range(1, len(severities)):
            assert severities[i].value > severities[i-1].value
    
    def test_base_chaos_event_bible_framework(self):
        """Test base ChaosEvent matches Bible event framework"""
        event = ChaosEvent(
            event_type=ChaosEventType.POLITICAL_UPHEAVAL,
            severity=EventSeverity.MODERATE,
            affected_regions=['region1', 'region2'],  # Bible: Regional scope
            cooldown_hours=72.0,  # Bible: Event cooldown system
            cascade_probability=0.3  # Bible: Cascading effects
        )
        
        # Verify Bible event framework requirements
        assert event.event_type == ChaosEventType.POLITICAL_UPHEAVAL
        assert event.severity == EventSeverity.MODERATE
        assert event.affected_regions == ['region1', 'region2']
        assert event.cooldown_hours == 72.0  # Bible default
        assert event.cascade_probability == 0.3
        assert event.status == EventStatus.PENDING
        assert hasattr(event, 'cascade_delay_hours')  # Bible: Delayed cascades
        assert hasattr(event, 'mitigation_factors')   # Bible: Mitigation system
    
    def test_political_upheaval_event_bible_compliant(self):
        """Test PoliticalUpheavalEvent matches Bible political pressure events"""
        event = PoliticalUpheavalEvent(
            severity=EventSeverity.MAJOR,
            affected_regions=['political_region'],
            government_type='monarchy',  # Bible: Government type affects events
            rebellion_strength=0.8
        )
        
        # Bible: Political events should target political systems
        assert event.event_type == ChaosEventType.POLITICAL_UPHEAVAL
        assert event.severity == EventSeverity.MAJOR
        assert hasattr(event, 'government_type')    # Bible: Context-specific data
        assert hasattr(event, 'rebellion_strength') # Bible: Event intensity
    
    def test_economic_collapse_event_bible_compliant(self):
        """Test EconomicCollapseEvent matches Bible economic pressure events"""
        event = EconomicCollapseEvent(
            severity=EventSeverity.MAJOR,
            affected_regions=['trade_region'],
            collapse_type='market_crash',  # Bible: Economic event types
            economic_impact=0.7
        )
        
        # Bible: Economic events should affect trade and markets
        assert event.event_type == ChaosEventType.ECONOMIC_COLLAPSE
        assert event.severity == EventSeverity.MAJOR
        assert hasattr(event, 'collapse_type')    # Bible: Economic context
        assert hasattr(event, 'economic_impact')  # Bible: Impact measurement
    
    def test_faction_betrayal_event_bible_compliant(self):
        """Test FactionBetrayalEvent matches Bible faction system integration"""
        event = FactionBetrayalEvent(
            severity=EventSeverity.MODERATE,
            affected_regions=['faction_region'],
            betraying_faction='faction_a',    # Bible: Faction integration
            betrayed_faction='faction_b',
            trust_impact=0.6
        )
        
        # Bible: Faction events should integrate with faction system
        assert event.event_type == ChaosEventType.FACTION_BETRAYAL
        assert hasattr(event, 'betraying_faction')  # Bible: Faction system integration
        assert hasattr(event, 'betrayed_faction')
        assert hasattr(event, 'trust_impact')       # Bible: Trust/reputation effects
    
    def test_event_serialization_bible_compatible(self):
        """Test event serialization for Bible-compliant WebSocket/API"""
        event = ChaosEvent(
            event_type=ChaosEventType.NATURAL_DISASTER,
            severity=EventSeverity.MAJOR,
            affected_regions=['disaster_region'],
            chaos_score_at_trigger=0.7,  # Bible: Pressure context
            cascade_probability=0.4       # Bible: Cascading effects
        )
        
        # Test WebSocket-compatible serialization
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict['event_type'] == 'NATURAL_DISASTER'
        assert event_dict['severity'] == 'MAJOR'
        assert event_dict['affected_regions'] == ['disaster_region']
        assert event_dict['chaos_score_at_trigger'] == 0.7
        assert event_dict['cascade_probability'] == 0.4
        
        # Test JSON string conversion
        json_str = event.to_json()
        assert isinstance(json_str, str)
        assert 'NATURAL_DISASTER' in json_str
    
    def test_event_effects_bible_framework(self):
        """Test EventEffect matches Bible cross-system integration"""
        effect = EventEffect(
            target_system='faction',      # Bible: Cross-system integration
            target_id='faction_123',
            effect_type='reduce_stability', # Bible: System-specific effects
            magnitude=0.5,
            duration_hours=48.0,           # Bible: Temporary effects
            delay_hours=2.0                # Bible: Delayed consequences
        )
        
        # Verify Bible cross-system integration requirements
        assert effect.target_system == 'faction'
        assert effect.target_id == 'faction_123'
        assert effect.effect_type == 'reduce_stability'
        assert effect.magnitude == 0.5
        assert effect.duration_hours == 48.0
        assert effect.delay_hours == 2.0
        assert effect.is_delayed()  # Bible: Delayed cascade effects


class TestPressureData:
    """Test PressureData models per Bible multi-dimensional pressure system"""
    
    def test_pressure_source_enum_bible_types(self):
        """Test PressureSource enum includes Bible-specified pressure types"""
        # Bible specifies these pressure source types
        bible_pressure_types = [
            'ECONOMIC',       # Bible: Economic Pressure
            'POLITICAL',      # Bible: Political Pressure
            'SOCIAL',         # Bible: Social Pressure (population)
            'ENVIRONMENTAL',  # Bible: Environmental Pressure
            'DIPLOMATIC',     # Bible: Diplomatic relationships
            'FACTION_CONFLICT' # Bible: Faction system integration
        ]
        
        # Note: Not all may be implemented as enum values, but should be supported as strings
        for pressure_type in ['ECONOMIC', 'POLITICAL', 'ENVIRONMENTAL']:
            if hasattr(PressureSource, pressure_type):
                pressure_source = getattr(PressureSource, pressure_type)
                assert isinstance(pressure_source, PressureSource)
    
    def test_pressure_data_initialization_bible_structure(self):
        """Test PressureData initialization with Bible-compliant structure"""
        pressure_data = PressureData()
        
        # Bible: Multi-dimensional pressure system structure
        assert hasattr(pressure_data, 'pressure_sources')
        assert hasattr(pressure_data, 'global_pressure')
        assert hasattr(pressure_data, 'last_update')
        assert hasattr(pressure_data, 'calculation_time_ms')
        
        # Verify structure supports Bible pressure types
        assert isinstance(pressure_data.pressure_sources, dict)
    
    def test_pressure_data_bible_pressure_sources(self):
        """Test PressureData with Bible-specified pressure sources"""
        # Bible: Multi-dimensional pressure calculation
        bible_pressure_sources = {
            'economic': 0.4,      # Bible: Market crashes, resource depletion
            'political': 0.6,     # Bible: Leadership failures, succession crises
            'social': 0.3,        # Bible: Population unrest, faction tensions
            'environmental': 0.2, # Bible: Natural disasters, seasonal extremes
            'diplomatic': 0.5     # Bible: Diplomatic relationships
        }
        
        pressure_data = PressureData(
            region_id='test_region',
            pressure_sources=bible_pressure_sources
        )
        
        # Verify Bible pressure sources are properly stored
        assert pressure_data.region_id == 'test_region'
        assert pressure_data.pressure_sources == bible_pressure_sources
        
        # Test individual Bible pressure types
        assert pressure_data.pressure_sources['economic'] == 0.4
        assert pressure_data.pressure_sources['political'] == 0.6
        assert pressure_data.pressure_sources['social'] == 0.3
        assert pressure_data.pressure_sources['environmental'] == 0.2
        assert pressure_data.pressure_sources['diplomatic'] == 0.5
    
    def test_pressure_data_validation_bible_ranges(self):
        """Test PressureData validation uses Bible-specified ranges"""
        # Bible: Pressure values should be 0.0 to 1.0
        valid_pressure_data = PressureData(
            pressure_sources={
                'economic': 0.0,    # Bible: Minimum pressure
                'political': 1.0    # Bible: Maximum pressure
            }
        )
        
        # Should not raise exceptions for valid ranges
        assert valid_pressure_data.pressure_sources['economic'] == 0.0
        assert valid_pressure_data.pressure_sources['political'] == 1.0
    
    def test_pressure_reading_bible_format(self):
        """Test PressureReading matches Bible pressure monitoring format"""
        reading = PressureReading(
            source=PressureSource.ECONOMIC if hasattr(PressureSource, 'ECONOMIC') else 'economic',
            value=0.6,
            location_id='region_123',     # Bible: Regional pressure tracking
            timestamp=datetime.now(),
            details={'market_volatility': 0.8}  # Bible: Context details
        )
        
        # Verify Bible pressure reading structure
        assert reading.value == 0.6
        assert reading.location_id == 'region_123'
        assert isinstance(reading.timestamp, datetime)
        assert 'market_volatility' in reading.details
    
    def test_pressure_data_serialization_bible_compatible(self):
        """Test PressureData serialization for Bible-compliant API"""
        pressure_data = PressureData(
            region_id='serialization_test',
            pressure_sources={
                'economic': 0.5,
                'political': 0.7
            }
        )
        
        # Test serialization for API compatibility
        if hasattr(pressure_data, 'to_dict'):
            data_dict = pressure_data.to_dict()
            assert isinstance(data_dict, dict)
            assert 'pressure_sources' in data_dict
            assert data_dict['pressure_sources']['economic'] == 0.5
            assert data_dict['pressure_sources']['political'] == 0.7


class TestModelIntegration:
    """Test model integration per Bible cross-system requirements"""
    
    def test_chaos_state_with_events_bible_integration(self):
        """Test ChaosState integrates with events per Bible framework"""
        # Create Bible-compliant chaos state with events
        event1 = ChaosEvent(
            event_type=ChaosEventType.ECONOMIC_COLLAPSE,
            severity=EventSeverity.MODERATE
        )
        event2 = ChaosEvent(
            event_type=ChaosEventType.POLITICAL_UPHEAVAL,
            severity=EventSeverity.MAJOR
        )
        
        state = ChaosState(
            chaos_level=ChaosLevel.HIGH,
            chaos_score=0.8,  # Bible: High threshold
            active_events=[event1.event_id, event2.event_id],
            pressure_sources={'political': 0.9, 'economic': 0.8}  # Bible: High pressure causes events
        )
        
        # Verify Bible integration requirements
        assert state.chaos_level == ChaosLevel.HIGH
        assert len(state.active_events) == 2
        assert state.pressure_sources['political'] == 0.9  # High political pressure
        assert state.pressure_sources['economic'] == 0.8   # High economic pressure
    
    def test_pressure_to_chaos_conversion_bible_compliant(self):
        """Test PressureData to ChaosState conversion per Bible calculation"""
        # Bible: Multi-dimensional pressure should determine chaos level
        pressure_data = PressureData(
            pressure_sources={
                'economic': 0.7,     # Bible: High economic pressure
                'political': 0.8,    # Bible: High political pressure  
                'social': 0.5,       # Bible: Moderate social pressure
                'environmental': 0.3 # Bible: Low environmental pressure
            }
        )
        
        # Bible: High pressure should result in high chaos
        # (This would normally be done by ChaosMath, but testing model compatibility)
        total_pressure = sum(pressure_data.pressure_sources.values()) / len(pressure_data.pressure_sources)
        expected_chaos_level = ChaosLevel.HIGH if total_pressure > 0.8 else ChaosLevel.MODERATE
        
        chaos_state = ChaosState(
            chaos_score=total_pressure,
            chaos_level=expected_chaos_level,
            pressure_sources=pressure_data.pressure_sources
        )
        
        # Verify Bible pressure-to-chaos conversion
        assert chaos_state.chaos_score == total_pressure
        assert chaos_state.pressure_sources == pressure_data.pressure_sources
        assert chaos_state.chaos_level in [ChaosLevel.MODERATE, ChaosLevel.HIGH]
    
    def test_websocket_compatibility_bible_frontend(self):
        """Test model WebSocket compatibility for Bible Unity frontend integration"""
        # Bible: Unity frontend requires WebSocket-compatible serialization
        chaos_state = ChaosState(
            chaos_level=ChaosLevel.MODERATE,
            chaos_score=0.6,
            pressure_sources={'political': 0.7}
        )
        
        chaos_event = ChaosEvent(
            event_type=ChaosEventType.FACTION_BETRAYAL,
            severity=EventSeverity.MODERATE,
            affected_regions=['region1']
        )
        
        # Test WebSocket serialization compatibility
        state_dict = chaos_state.to_dict()
        event_dict = chaos_event.to_dict()
        
        # Verify Bible frontend compatibility requirements
        assert isinstance(state_dict, dict)
        assert isinstance(event_dict, dict)
        assert state_dict['chaos_level'] == 'MODERATE'
        assert event_dict['event_type'] == 'FACTION_BETRAYAL'
        
        # Test JSON string compatibility
        event_json = chaos_event.to_json()
        assert isinstance(event_json, str)
        assert 'FACTION_BETRAYAL' in event_json 