"""
Tests for Chaos System Utilities

Tests for utility functions and helper classes including:
- ChaosMath calculations and algorithms
- Event utilities and helpers
- Pressure calculations
- Cross-system integration utilities
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch

from backend.systems.chaos.utils.chaos_math import ChaosMath, ChaosCalculationResult
from backend.systems.chaos.utils.event_utils import EventUtils
from backend.systems.chaos.utils.event_helpers import EventHelpers
from backend.systems.chaos.utils.pressure_calculations import PressureCalculations
from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.models.chaos_state import ChaosState, ChaosLevel
from backend.systems.chaos.models.pressure_data import PressureData, PressureSource
from backend.systems.chaos.models.chaos_events import (
    ChaosEvent, ChaosEventType, EventSeverity, EventStatus
)


class TestChaosMath:
    """Test chaos mathematical calculations and algorithms"""
    
    @pytest.fixture
    def chaos_config(self):
        """Create test chaos configuration"""
        return ChaosConfig(
            chaos_threshold=0.7,
            pressure_weights={
                'political': 1.2,
                'economic': 1.0,
                'faction_tension': 1.1,
                'population_stress': 0.9,
                'military_buildup': 1.3,
                'environmental': 0.8
            }
        )
    
    @pytest.fixture
    def chaos_math(self, chaos_config):
        """Create ChaosMath instance for testing"""
        return ChaosMath(chaos_config)
    
    @pytest.fixture
    def sample_pressure_data(self):
        """Create sample pressure data for testing"""
        pressure_data = PressureData()
        pressure_data.pressure_sources = {
            'political': 0.6,
            'economic': 0.5,
            'faction_tension': 0.7,
            'population_stress': 0.4,
            'military_buildup': 0.3,
            'environmental': 0.2
        }
        pressure_data.global_pressure = 0.45
        return pressure_data
    
    def test_chaos_math_initialization(self, chaos_math):
        """Test ChaosMath initialization"""
        assert chaos_math.config is not None
        assert hasattr(chaos_math, 'pressure_weights')
    
    def test_calculate_chaos_score_basic(self, chaos_math, sample_pressure_data):
        """Test basic chaos score calculation"""
        result = chaos_math.calculate_chaos_score(sample_pressure_data)
        
        assert isinstance(result, ChaosCalculationResult)
        assert 0.0 <= result.chaos_score <= 1.0
        assert isinstance(result.chaos_level, ChaosLevel)
        assert isinstance(result.pressure_sources, dict)
        assert isinstance(result.weighted_factors, dict)
        assert isinstance(result.threshold_exceeded, bool)
    
    def test_weighted_pressure_calculation(self, chaos_math, sample_pressure_data):
        """Test that pressure weights are applied correctly"""
        result = chaos_math.calculate_chaos_score(sample_pressure_data)
        
        # Political pressure should be weighted higher (1.2x)
        political_weighted = result.weighted_factors.get('political', 0)
        political_raw = sample_pressure_data.pressure_sources['political']
        
        expected_weighted = political_raw * chaos_math.config.pressure_weights['political']
        assert abs(political_weighted - expected_weighted) < 0.01
    
    def test_chaos_level_determination(self, chaos_math):
        """Test chaos level determination from scores"""
        # Test different score ranges
        test_cases = [
            (0.1, ChaosLevel.DORMANT),
            (0.3, ChaosLevel.STABLE),
            (0.5, ChaosLevel.MODERATE),
            (0.7, ChaosLevel.HIGH),
            (0.85, ChaosLevel.CRITICAL),
            (0.95, ChaosLevel.CATASTROPHIC)
        ]
        
        for score, expected_level in test_cases:
            level = chaos_math._determine_chaos_level_from_score(score)
            assert level == expected_level
    
    def test_threshold_exceeded_detection(self, chaos_math):
        """Test threshold exceeded detection"""
        # High pressure data that should exceed threshold
        high_pressure_data = PressureData()
        high_pressure_data.pressure_sources = {
            'political': 0.9,
            'economic': 0.8,
            'faction_tension': 0.85,
            'population_stress': 0.7
        }
        high_pressure_data.global_pressure = 0.8
        
        result = chaos_math.calculate_chaos_score(high_pressure_data)
        assert result.threshold_exceeded
        assert result.chaos_score > chaos_math.config.chaos_threshold
        
        # Low pressure data that should not exceed threshold
        low_pressure_data = PressureData()
        low_pressure_data.pressure_sources = {
            'political': 0.2,
            'economic': 0.1,
            'faction_tension': 0.3
        }
        low_pressure_data.global_pressure = 0.2
        
        result = chaos_math.calculate_chaos_score(low_pressure_data)
        assert not result.threshold_exceeded
        assert result.chaos_score < chaos_math.config.chaos_threshold
    
    def test_recommended_events_generation(self, chaos_math):
        """Test generation of recommended events based on pressure sources"""
        # Create pressure data with high political pressure
        pressure_data = PressureData()
        pressure_data.pressure_sources = {
            'political': 0.9,
            'economic': 0.3,
            'faction_tension': 0.8
        }
        pressure_data.global_pressure = 0.7
        
        result = chaos_math.calculate_chaos_score(pressure_data)
        
        # Should recommend political events due to high political pressure
        assert len(result.recommended_events) > 0
        political_events = [e for e in result.recommended_events 
                          if 'political' in e or 'upheaval' in e]
        assert len(political_events) > 0
    
    def test_empty_pressure_data_handling(self, chaos_math):
        """Test handling of empty pressure data"""
        empty_pressure_data = PressureData()
        
        result = chaos_math.calculate_chaos_score(empty_pressure_data)
        
        assert result.chaos_score == 0.0
        assert result.chaos_level == ChaosLevel.DORMANT
        assert not result.threshold_exceeded
        assert len(result.recommended_events) == 0
    
    def test_extreme_values_handling(self, chaos_math):
        """Test handling of extreme pressure values"""
        # Test with maximum pressure values
        max_pressure_data = PressureData()
        max_pressure_data.pressure_sources = {
            source: 1.0 for source in ['political', 'economic', 'faction_tension']
        }
        max_pressure_data.global_pressure = 1.0
        
        result = chaos_math.calculate_chaos_score(max_pressure_data)
        assert result.chaos_score <= 1.0  # Should not exceed maximum
        assert result.chaos_level == ChaosLevel.CATASTROPHIC
        
        # Test with zero pressure values
        zero_pressure_data = PressureData()
        zero_pressure_data.pressure_sources = {
            source: 0.0 for source in ['political', 'economic', 'faction_tension']
        }
        zero_pressure_data.global_pressure = 0.0
        
        result = chaos_math.calculate_chaos_score(zero_pressure_data)
        assert result.chaos_score == 0.0
        assert result.chaos_level == ChaosLevel.DORMANT


class TestEventUtils:
    """Test event utility functions"""
    
    def test_create_event_from_type(self):
        """Test creating events from event types"""
        event_data = {
            'severity': EventSeverity.MODERATE,
            'affected_regions': ['region1'],
            'chaos_score_trigger': 0.7
        }
        
        event = EventUtils.create_event_from_type(
            ChaosEventType.POLITICAL_UPHEAVAL,
            event_data
        )
        
        assert event.event_type == ChaosEventType.POLITICAL_UPHEAVAL
        assert event.severity == EventSeverity.MODERATE
        assert event.affected_regions == ['region1']
        assert event.chaos_score_trigger == 0.7
    
    def test_validate_event_data(self):
        """Test event data validation"""
        valid_data = {
            'event_type': ChaosEventType.ECONOMIC_COLLAPSE,
            'severity': EventSeverity.MAJOR,
            'affected_regions': ['region1'],
            'chaos_score_trigger': 0.8
        }
        
        assert EventUtils.validate_event_data(valid_data)
        
        # Test invalid data
        invalid_data = {
            'event_type': 'invalid_type',
            'severity': EventSeverity.MAJOR
            # Missing required fields
        }
        
        assert not EventUtils.validate_event_data(invalid_data)
    
    def test_calculate_event_impact(self):
        """Test event impact calculation"""
        event = ChaosEvent(
            event_id='test_id',
            event_type=ChaosEventType.NATURAL_DISASTER,
            severity=EventSeverity.CRITICAL,
            status=EventStatus.ACTIVE,
            title='Test Disaster',
            description='Test disaster event',
            affected_regions=['region1', 'region2'],
            triggered_at=datetime.now(),
            chaos_score_trigger=0.9
        )
        
        impact = EventUtils.calculate_event_impact(event)
        
        assert isinstance(impact, dict)
        assert 'severity_multiplier' in impact
        assert 'regional_impact' in impact
        assert 'duration_factor' in impact
    
    def test_get_event_cooldown_duration(self):
        """Test event cooldown duration calculation"""
        duration = EventUtils.get_event_cooldown_duration(
            ChaosEventType.WAR_OUTBREAK,
            EventSeverity.CRITICAL
        )
        
        assert isinstance(duration, timedelta)
        assert duration.total_seconds() > 0
        
        # Critical events should have longer cooldowns
        critical_duration = EventUtils.get_event_cooldown_duration(
            ChaosEventType.WAR_OUTBREAK,
            EventSeverity.CRITICAL
        )
        
        minor_duration = EventUtils.get_event_cooldown_duration(
            ChaosEventType.WAR_OUTBREAK,
            EventSeverity.MINOR
        )
        
        assert critical_duration > minor_duration
    
    def test_format_event_description(self):
        """Test event description formatting"""
        event = ChaosEvent(
            event_id='test_id',
            event_type=ChaosEventType.FACTION_BETRAYAL,
            severity=EventSeverity.MAJOR,
            status=EventStatus.PENDING,
            title='Faction Betrayal',
            description='A faction has betrayed their allies',
            affected_regions=['region1'],
            triggered_at=datetime.now(),
            chaos_score_trigger=0.75
        )
        
        formatted = EventUtils.format_event_description(event)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert event.title in formatted
        assert str(event.severity.value) in formatted


class TestEventHelpers:
    """Test event helper functions"""
    
    def test_generate_event_title(self):
        """Test event title generation"""
        title = EventHelpers.generate_event_title(
            ChaosEventType.POLITICAL_UPHEAVAL,
            EventSeverity.MAJOR,
            {'government_type': 'monarchy'}
        )
        
        assert isinstance(title, str)
        assert len(title) > 0
    
    def test_determine_affected_regions(self):
        """Test determining affected regions for events"""
        pressure_data = PressureData()
        pressure_data.regional_pressures = {
            'region1': Mock(pressure_score=0.8),
            'region2': Mock(pressure_score=0.4),
            'region3': Mock(pressure_score=0.9)
        }
        
        affected_regions = EventHelpers.determine_affected_regions(
            ChaosEventType.ECONOMIC_COLLAPSE,
            EventSeverity.MAJOR,
            pressure_data
        )
        
        assert isinstance(affected_regions, list)
        assert len(affected_regions) > 0
        # High pressure regions should be included
        assert 'region3' in affected_regions
    
    def test_calculate_event_severity(self):
        """Test event severity calculation"""
        severity = EventHelpers.calculate_event_severity(
            chaos_score=0.85,
            pressure_sources={'political': 0.9, 'economic': 0.7}
        )
        
        assert isinstance(severity, EventSeverity)
        # High chaos score should result in high severity
        assert severity in [EventSeverity.MAJOR, EventSeverity.CRITICAL, EventSeverity.CATASTROPHIC]
    
    def test_generate_event_metadata(self):
        """Test event metadata generation"""
        metadata = EventHelpers.generate_event_metadata(
            ChaosEventType.NATURAL_DISASTER,
            EventSeverity.CRITICAL,
            {'disaster_type': 'earthquake', 'magnitude': 7.5}
        )
        
        assert isinstance(metadata, dict)
        assert 'disaster_type' in metadata
        assert 'magnitude' in metadata
        assert metadata['disaster_type'] == 'earthquake'
        assert metadata['magnitude'] == 7.5


class TestPressureCalculations:
    """Test pressure calculation utilities"""
    
    def test_calculate_weighted_pressure(self):
        """Test weighted pressure calculation"""
        pressure_sources = {
            'political': 0.7,
            'economic': 0.5,
            'faction_tension': 0.8
        }
        
        weights = {
            'political': 1.2,
            'economic': 1.0,
            'faction_tension': 1.1
        }
        
        weighted = PressureCalculations.calculate_weighted_pressure(
            pressure_sources, weights
        )
        
        assert isinstance(weighted, dict)
        assert 'political' in weighted
        assert weighted['political'] == 0.7 * 1.2
        assert weighted['economic'] == 0.5 * 1.0
        assert weighted['faction_tension'] == 0.8 * 1.1
    
    def test_aggregate_pressure_score(self):
        """Test pressure score aggregation"""
        weighted_pressures = {
            'political': 0.84,  # 0.7 * 1.2
            'economic': 0.5,    # 0.5 * 1.0
            'faction_tension': 0.88  # 0.8 * 1.1
        }
        
        aggregate = PressureCalculations.aggregate_pressure_score(weighted_pressures)
        
        assert isinstance(aggregate, float)
        assert 0.0 <= aggregate <= 1.0
        # Should be average of weighted pressures
        expected = sum(weighted_pressures.values()) / len(weighted_pressures)
        assert abs(aggregate - expected) < 0.01
    
    def test_calculate_pressure_trend(self):
        """Test pressure trend calculation"""
        historical_data = [
            {'timestamp': datetime.now() - timedelta(hours=3), 'pressure': 0.5},
            {'timestamp': datetime.now() - timedelta(hours=2), 'pressure': 0.6},
            {'timestamp': datetime.now() - timedelta(hours=1), 'pressure': 0.7},
            {'timestamp': datetime.now(), 'pressure': 0.8}
        ]
        
        trend = PressureCalculations.calculate_pressure_trend(historical_data)
        
        assert isinstance(trend, float)
        # Should be positive trend (increasing pressure)
        assert trend > 0
    
    def test_normalize_pressure_values(self):
        """Test pressure value normalization"""
        raw_values = {
            'source1': 150,  # Above normal range
            'source2': 0.5,  # Already normalized
            'source3': -10   # Below normal range
        }
        
        normalized = PressureCalculations.normalize_pressure_values(raw_values)
        
        assert isinstance(normalized, dict)
        for key, value in normalized.items():
            assert 0.0 <= value <= 1.0
    
    def test_detect_pressure_anomalies(self):
        """Test pressure anomaly detection"""
        pressure_data = {
            'political': 0.95,  # Anomalously high
            'economic': 0.5,    # Normal
            'faction_tension': 0.02  # Anomalously low
        }
        
        anomalies = PressureCalculations.detect_pressure_anomalies(
            pressure_data, threshold=0.8
        )
        
        assert isinstance(anomalies, dict)
        assert 'high_anomalies' in anomalies
        assert 'low_anomalies' in anomalies
        assert 'political' in anomalies['high_anomalies']


class TestUtilityIntegration:
    """Integration tests for utility functions"""
    
    def test_full_calculation_pipeline(self):
        """Test full calculation pipeline using utilities"""
        # Create test data
        raw_pressure_data = {
            'political': 0.7,
            'economic': 0.5,
            'faction_tension': 0.8,
            'population_stress': 0.4
        }
        
        weights = {
            'political': 1.2,
            'economic': 1.0,
            'faction_tension': 1.1,
            'population_stress': 0.9
        }
        
        # Step 1: Calculate weighted pressures
        weighted = PressureCalculations.calculate_weighted_pressure(
            raw_pressure_data, weights
        )
        
        # Step 2: Aggregate pressure score
        aggregate_score = PressureCalculations.aggregate_pressure_score(weighted)
        
        # Step 3: Create pressure data object
        pressure_data = PressureData()
        pressure_data.pressure_sources = raw_pressure_data
        pressure_data.global_pressure = aggregate_score
        
        # Step 4: Calculate chaos score
        config = ChaosConfig(pressure_weights=weights)
        chaos_math = ChaosMath(config)
        chaos_result = chaos_math.calculate_chaos_score(pressure_data)
        
        # Verify pipeline results
        assert isinstance(chaos_result, ChaosCalculationResult)
        assert chaos_result.chaos_score > 0
        assert len(chaos_result.pressure_sources) > 0
        assert len(chaos_result.weighted_factors) > 0
    
    def test_event_creation_pipeline(self):
        """Test event creation pipeline using utilities"""
        # Step 1: Determine event type based on pressure
        pressure_sources = {'political': 0.9, 'economic': 0.3}
        event_type = ChaosEventType.POLITICAL_UPHEAVAL  # Based on high political pressure
        
        # Step 2: Calculate severity
        severity = EventHelpers.calculate_event_severity(
            chaos_score=0.8,
            pressure_sources=pressure_sources
        )
        
        # Step 3: Determine affected regions
        pressure_data = PressureData()
        pressure_data.pressure_sources = pressure_sources
        affected_regions = EventHelpers.determine_affected_regions(
            event_type, severity, pressure_data
        )
        
        # Step 4: Create event
        event_data = {
            'severity': severity,
            'affected_regions': affected_regions,
            'chaos_score_trigger': 0.8
        }
        
        event = EventUtils.create_event_from_type(event_type, event_data)
        
        # Verify pipeline results
        assert isinstance(event, ChaosEvent)
        assert event.event_type == event_type
        assert event.severity == severity
        assert len(event.affected_regions) > 0
    
    def test_performance_with_large_datasets(self):
        """Test utility performance with large datasets"""
        # Create large pressure dataset
        large_pressure_data = {
            f'source_{i}': 0.5 for i in range(1000)
        }
        
        weights = {
            f'source_{i}': 1.0 for i in range(1000)
        }
        
        start_time = datetime.now()
        
        # Test weighted calculation performance
        weighted = PressureCalculations.calculate_weighted_pressure(
            large_pressure_data, weights
        )
        
        # Test aggregation performance
        aggregate = PressureCalculations.aggregate_pressure_score(weighted)
        
        end_time = datetime.now()
        calculation_time = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (< 1 second)
        assert calculation_time < 1.0
        assert isinstance(aggregate, float)
        assert 0.0 <= aggregate <= 1.0 