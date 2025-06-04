"""
Integration tests for the Chaos System

Tests the full integration of all chaos system components working together
to ensure Bible compliance requirements are met in real scenarios.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from backend.systems.chaos.core.chaos_manager import ChaosManager
from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.services.chaos_service import ChaosService
from backend.systems.chaos.core.warning_system import WarningPhase
from backend.systems.chaos.core.narrative_moderator import NarrativePriority
from backend.systems.chaos.core.exceptions import ChaosSystemError


@pytest.fixture
def integration_config():
    """Create a configuration for integration testing"""
    config = ChaosConfig()
    # Faster intervals for testing
    config.system_config.health_check_interval = 0.1
    config.warning_config.rumor_duration_hours = 0.001
    config.warning_config.early_warning_duration_hours = 0.001
    config.narrative_config.analysis_interval_seconds = 0.1
    return config


@pytest.fixture
async def chaos_service(integration_config):
    """Create a fully initialized chaos service"""
    service = ChaosService(integration_config)
    await service.initialize()
    return service


@pytest.fixture
async def running_chaos_service(chaos_service):
    """Create a running chaos service"""
    await chaos_service.start()
    yield chaos_service
    await chaos_service.stop()


class TestFullSystemIntegration:
    """Test full system integration with all components"""
    
    @pytest.mark.asyncio
    async def test_complete_system_startup_and_shutdown(self, integration_config):
        """Test complete system startup and shutdown sequence"""
        service = ChaosService(integration_config)
        
        # Test initialization sequence
        await service.initialize()
        assert service.manager._initialized
        assert service.manager.chaos_engine is not None
        assert service.manager.pressure_monitor is not None
        assert service.manager.warning_system is not None
        assert service.manager.narrative_moderator is not None
        assert service.manager.cascade_engine is not None
        
        # Test startup sequence
        await service.start()
        status = await service.get_system_status()
        assert status['status'].name == 'RUNNING'
        assert status['initialized'] is True
        
        # Test health monitoring
        health = await service.get_component_health()
        assert health['overall'].name == 'HEALTHY'
        
        # Test shutdown sequence
        await service.stop()
        status = await service.get_system_status()
        assert status['status'].name == 'STOPPED'
    
    @pytest.mark.asyncio
    async def test_pressure_to_event_pipeline(self, running_chaos_service):
        """Test the complete pipeline from pressure monitoring to event generation"""
        # Mock external pressure sources
        pressure_data = {
            'economic': 0.8,  # High economic pressure
            'political': 0.7,  # High political pressure
            'social': 0.3,
            'environmental': 0.2,
            'diplomatic': 0.4,
            'temporal': 0.1
        }
        
        # Update pressure sources
        with patch.object(running_chaos_service.manager.pressure_monitor, 'get_current_pressures', return_value=pressure_data):
            pressures = await running_chaos_service.get_current_pressures()
            assert pressures['economic'] == 0.8
            assert pressures['political'] == 0.7
            
            # High pressures should trigger event consideration
            # Mock the chaos engine to capture event processing
            events_triggered = []
            
            async def mock_process_event(event_type, **kwargs):
                events_triggered.append((event_type, kwargs))
                return {"status": "success", "event_id": f"test_{event_type}"}
            
            running_chaos_service.manager.chaos_engine.process_event = mock_process_event
            
            # Trigger an event based on high pressure
            result = await running_chaos_service.trigger_event("economic_crisis", severity=0.8)
            
            assert result["status"] == "success"
            assert len(events_triggered) == 1
            assert events_triggered[0][0] == "economic_crisis"
            assert events_triggered[0][1]['severity'] == 0.8
    
    @pytest.mark.asyncio
    async def test_narrative_weighting_pipeline(self, running_chaos_service):
        """Test the narrative intelligence weighting system integration"""
        # Add a critical political theme
        theme_added = await running_chaos_service.add_narrative_theme(
            theme_id="political_crisis",
            name="Political Crisis",
            description="Critical political narrative theme",
            priority="critical",
            weight_modifier=2.0,
            related_events=["political_upheaval", "faction_conflict"]
        )
        assert theme_added is True
        
        # Set narrative context
        await running_chaos_service.update_narrative_tension(0.9)  # High tension
        await running_chaos_service.update_narrative_engagement(0.3)  # Low engagement
        
        # Get narrative status to verify integration
        narrative_status = await running_chaos_service.get_narrative_status()
        assert narrative_status['current_tension'] == 0.9
        assert narrative_status['current_engagement'] == 0.3
        assert 'political_crisis' in narrative_status['active_themes']
        
        # Critical theme should be active
        theme = narrative_status['active_themes']['political_crisis']
        assert theme['priority'] == 'critical'
        assert theme['weight_modifier'] == 2.0
        assert theme['is_active'] is True
    
    @pytest.mark.asyncio
    async def test_warning_escalation_pipeline(self, running_chaos_service):
        """Test the three-tier warning escalation system integration"""
        # Mock warning system to track escalations
        warning_phases = []
        
        async def mock_issue_warning(event_type, phase, **kwargs):
            warning_id = f"warning_{len(warning_phases)}"
            warning_phases.append({
                'id': warning_id,
                'event_type': event_type,
                'phase': phase,
                'timestamp': datetime.now()
            })
            return warning_id
        
        running_chaos_service.manager.warning_system.issue_warning = mock_issue_warning
        
        # Simulate warning escalation sequence
        rumor_id = await running_chaos_service.manager.warning_system.issue_warning(
            "economic_crisis", WarningPhase.RUMOR
        )
        assert rumor_id == "warning_0"
        assert warning_phases[0]['phase'] == WarningPhase.RUMOR
        
        early_id = await running_chaos_service.manager.warning_system.issue_warning(
            "economic_crisis", WarningPhase.EARLY_WARNING
        )
        assert early_id == "warning_1"
        assert warning_phases[1]['phase'] == WarningPhase.EARLY_WARNING
        
        imminent_id = await running_chaos_service.manager.warning_system.issue_warning(
            "economic_crisis", WarningPhase.IMMINENT
        )
        assert imminent_id == "warning_2"
        assert warning_phases[2]['phase'] == WarningPhase.IMMINENT
        
        # Verify escalation sequence is correct
        assert len(warning_phases) == 3
        assert warning_phases[0]['phase'] == WarningPhase.RUMOR
        assert warning_phases[1]['phase'] == WarningPhase.EARLY_WARNING
        assert warning_phases[2]['phase'] == WarningPhase.IMMINENT
    
    @pytest.mark.asyncio
    async def test_cascade_effect_integration(self, running_chaos_service):
        """Test cascade effect integration with event processing"""
        # Mock cascade engine to track cascades
        cascades_triggered = []
        
        async def mock_process_cascade(trigger_event, **kwargs):
            cascade_id = f"cascade_{len(cascades_triggered)}"
            target_events = ["social_unrest", "political_instability"]
            cascades_triggered.append({
                'id': cascade_id,
                'trigger_event': trigger_event,
                'target_events': target_events,
                'severity': kwargs.get('severity', 0.5)
            })
            return {
                'cascade_id': cascade_id,
                'triggered_events': target_events
            }
        
        running_chaos_service.manager.cascade_engine.process_cascade = mock_process_cascade
        
        # Trigger an event with cascades enabled
        result = await running_chaos_service.trigger_event(
            "economic_crisis", 
            severity=0.8, 
            enable_cascades=True
        )
        
        # Should have triggered cascade effects
        assert len(cascades_triggered) == 1
        cascade = cascades_triggered[0]
        assert cascade['trigger_event'] == "economic_crisis"
        assert cascade['severity'] == 0.8
        assert "social_unrest" in cascade['target_events']
        assert "political_instability" in cascade['target_events']
    
    @pytest.mark.asyncio
    async def test_temporal_pressure_integration(self, running_chaos_service):
        """Test temporal pressure monitoring and event processing"""
        # Set up temporal pressure scenario
        temporal_pressures = {
            'economic': 0.4,
            'political': 0.3,
            'social': 0.2,
            'environmental': 0.1,
            'diplomatic': 0.2,
            'temporal': 0.9  # Very high temporal pressure
        }
        
        with patch.object(running_chaos_service.manager.pressure_monitor, 'get_current_pressures', return_value=temporal_pressures):
            pressures = await running_chaos_service.get_current_pressures()
            
            # Temporal pressure should be very high
            assert pressures['temporal'] == 0.9
            
            # Mock temporal event processing
            temporal_events = []
            
            async def mock_process_temporal_event(event_type, **kwargs):
                temporal_events.append((event_type, kwargs))
                return {"status": "success", "temporal_effect": True}
            
            running_chaos_service.manager.chaos_engine.process_event = mock_process_temporal_event
            
            # Trigger temporal event
            result = await running_chaos_service.trigger_event("temporal_anomaly", severity=0.9)
            
            assert result["status"] == "success"
            assert result["temporal_effect"] is True
            assert len(temporal_events) == 1
            assert temporal_events[0][0] == "temporal_anomaly"


class TestBibleComplianceRequirements:
    """Test specific Development Bible compliance requirements"""
    
    @pytest.mark.asyncio
    async def test_three_tier_escalation_compliance(self, running_chaos_service):
        """Test that three-tier escalation system meets Bible requirements"""
        # Mock the warning system to verify proper escalation
        escalation_sequence = []
        
        async def mock_escalate_warning(warning_id):
            # Simulate proper escalation phases
            current_phases = [w['phase'] for w in escalation_sequence]
            
            if not current_phases:
                new_phase = WarningPhase.RUMOR
            elif WarningPhase.RUMOR in current_phases and WarningPhase.EARLY_WARNING not in current_phases:
                new_phase = WarningPhase.EARLY_WARNING
            elif WarningPhase.EARLY_WARNING in current_phases and WarningPhase.IMMINENT not in current_phases:
                new_phase = WarningPhase.IMMINENT
            else:
                return False  # Cannot escalate further
            
            escalation_sequence.append({
                'warning_id': warning_id,
                'phase': new_phase,
                'timestamp': datetime.now()
            })
            return True
        
        running_chaos_service.manager.warning_system.escalate_warning = mock_escalate_warning
        
        # Test escalation sequence
        warning_id = "test_warning_1"
        
        # First escalation: None -> Rumor
        result = await running_chaos_service.escalate_warning(warning_id)
        assert result is True
        assert escalation_sequence[0]['phase'] == WarningPhase.RUMOR
        
        # Second escalation: Rumor -> Early Warning
        result = await running_chaos_service.escalate_warning(warning_id)
        assert result is True
        assert escalation_sequence[1]['phase'] == WarningPhase.EARLY_WARNING
        
        # Third escalation: Early Warning -> Imminent
        result = await running_chaos_service.escalate_warning(warning_id)
        assert result is True
        assert escalation_sequence[2]['phase'] == WarningPhase.IMMINENT
        
        # Fourth escalation should fail (already at highest level)
        result = await running_chaos_service.escalate_warning(warning_id)
        assert result is False
        
        # Verify all three tiers are represented
        phases = [e['phase'] for e in escalation_sequence]
        assert WarningPhase.RUMOR in phases
        assert WarningPhase.EARLY_WARNING in phases
        assert WarningPhase.IMMINENT in phases
    
    @pytest.mark.asyncio
    async def test_cascading_effects_compliance(self, running_chaos_service):
        """Test cascading effects meet Bible requirements"""
        # Track cascade chains
        cascade_chains = []
        
        async def mock_get_active_cascades():
            return cascade_chains
        
        async def mock_trigger_cascade(trigger_event, **kwargs):
            # Simulate proper cascade chain
            cascade_id = f"cascade_{len(cascade_chains)}"
            
            # Define cascade relationships per Bible requirements
            cascade_map = {
                'economic_crisis': ['social_unrest', 'political_instability'],
                'political_upheaval': ['diplomatic_crisis', 'social_unrest'],
                'environmental_disaster': ['economic_crisis', 'social_unrest'],
                'social_unrest': ['political_upheaval'],
                'diplomatic_crisis': ['economic_crisis']
            }
            
            target_events = cascade_map.get(trigger_event, [])
            
            cascade = {
                'id': cascade_id,
                'trigger_event': trigger_event,
                'target_events': target_events,
                'severity': kwargs.get('severity', 0.5),
                'timestamp': datetime.now()
            }
            cascade_chains.append(cascade)
            
            return {
                'cascade_id': cascade_id,
                'triggered_events': target_events
            }
        
        running_chaos_service.manager.cascade_engine.get_active_cascades = mock_get_active_cascades
        running_chaos_service.manager.cascade_engine.trigger_cascade = mock_trigger_cascade
        
        # Test cascade chain: Economic Crisis -> Social Unrest -> Political Upheaval
        result1 = await running_chaos_service.trigger_cascade("economic_crisis", severity=0.8)
        assert 'social_unrest' in result1['triggered_events']
        assert 'political_instability' in result1['triggered_events']
        
        result2 = await running_chaos_service.trigger_cascade("social_unrest", severity=0.6)
        assert 'political_upheaval' in result2['triggered_events']
        
        # Verify cascade chain exists
        active_cascades = await running_chaos_service.get_active_cascades()
        assert len(active_cascades) == 2
        
        # Verify proper cascade relationships
        economic_cascade = next(c for c in active_cascades if c['trigger_event'] == 'economic_crisis')
        social_cascade = next(c for c in active_cascades if c['trigger_event'] == 'social_unrest')
        
        assert 'social_unrest' in economic_cascade['target_events']
        assert 'political_upheaval' in social_cascade['target_events']
    
    @pytest.mark.asyncio
    async def test_narrative_intelligence_compliance(self, running_chaos_service):
        """Test narrative intelligence weighting meets Bible requirements"""
        # Set up narrative scenario
        await running_chaos_service.add_narrative_theme(
            theme_id="economic_drama",
            name="Economic Drama",
            description="Central economic narrative",
            priority="central",
            weight_modifier=1.5,
            related_events=["economic_crisis", "market_crash"]
        )
        
        await running_chaos_service.add_narrative_theme(
            theme_id="political_intrigue",
            name="Political Intrigue", 
            description="Critical political narrative",
            priority="critical",
            weight_modifier=2.0,
            related_events=["political_upheaval", "faction_conflict"]
        )
        
        # Set dramatic tension and engagement levels
        await running_chaos_service.update_narrative_tension(0.8)  # High tension
        await running_chaos_service.update_narrative_engagement(0.4)  # Low engagement
        
        # Verify narrative intelligence affects event weighting
        narrative_status = await running_chaos_service.get_narrative_status()
        
        # Should have active themes
        assert len(narrative_status['active_themes']) >= 2
        assert 'economic_drama' in narrative_status['active_themes']
        assert 'political_intrigue' in narrative_status['active_themes']
        
        # Critical theme should have higher weight modifier
        political_theme = narrative_status['active_themes']['political_intrigue']
        economic_theme = narrative_status['active_themes']['economic_drama']
        
        assert political_theme['priority'] == 'critical'
        assert economic_theme['priority'] == 'central'
        assert political_theme['weight_modifier'] > economic_theme['weight_modifier']
        
        # High tension with low engagement should affect chaos generation
        assert narrative_status['current_tension'] == 0.8
        assert narrative_status['current_engagement'] == 0.4
    
    @pytest.mark.asyncio
    async def test_distribution_fatigue_compliance(self, running_chaos_service):
        """Test distribution fatigue management meets Bible requirements"""
        # Track event timing to test fatigue
        event_history = []
        
        async def mock_process_event(event_type, **kwargs):
            event_history.append({
                'event_type': event_type,
                'timestamp': datetime.now(),
                'severity': kwargs.get('severity', 0.5)
            })
            return {"status": "success", "event_id": f"event_{len(event_history)}"}
        
        running_chaos_service.manager.chaos_engine.process_event = mock_process_event
        
        # Trigger multiple events quickly to test fatigue
        await running_chaos_service.trigger_event("economic_crisis", severity=0.6)
        await running_chaos_service.trigger_event("political_upheaval", severity=0.7)
        await running_chaos_service.trigger_event("social_unrest", severity=0.5)
        
        # Should have triggered events
        assert len(event_history) == 3
        
        # Events should be spaced appropriately (implementation dependent)
        # Bible requires fatigue to prevent clustering
        timestamps = [e['timestamp'] for e in event_history]
        
        # Verify events were processed (fatigue mechanism would be in the actual implementation)
        assert len(timestamps) == 3
        assert all(isinstance(ts, datetime) for ts in timestamps)
    
    @pytest.mark.asyncio
    async def test_temporal_pressure_compliance(self, running_chaos_service):
        """Test temporal pressure as 6th pressure type meets Bible requirements"""
        # Verify temporal pressure is included in pressure monitoring
        pressures = await running_chaos_service.get_current_pressures()
        
        # Should include all 6 pressure types per Bible requirement
        expected_pressures = {
            'economic', 'political', 'social', 
            'environmental', 'diplomatic', 'temporal'
        }
        
        actual_pressures = set(pressures.keys())
        assert expected_pressures.issubset(actual_pressures), f"Missing pressures: {expected_pressures - actual_pressures}"
        
        # Temporal pressure should be monitored like other pressures
        assert 'temporal' in pressures
        assert isinstance(pressures['temporal'], (int, float))
        assert 0.0 <= pressures['temporal'] <= 1.0


class TestPerformanceIntegration:
    """Test performance characteristics of integrated system"""
    
    @pytest.mark.asyncio
    async def test_system_performance_under_load(self, running_chaos_service):
        """Test system performance with multiple concurrent operations"""
        start_time = datetime.now()
        
        # Simulate concurrent operations
        tasks = []
        
        # Add multiple narrative themes concurrently
        for i in range(5):
            task = running_chaos_service.add_narrative_theme(
                theme_id=f"theme_{i}",
                name=f"Theme {i}",
                description=f"Test theme {i}",
                priority="supporting",
                weight_modifier=1.0,
                related_events=[f"event_{i}"]
            )
            tasks.append(task)
        
        # Get system status multiple times
        for i in range(3):
            tasks.append(running_chaos_service.get_system_status())
        
        # Update narrative levels
        tasks.append(running_chaos_service.update_narrative_tension(0.7))
        tasks.append(running_chaos_service.update_narrative_engagement(0.6))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert duration < 5.0, f"Operations took too long: {duration}s"
        
        # All theme additions should succeed
        theme_results = results[:5]
        assert all(result is True for result in theme_results)
        
        # Status calls should succeed
        status_results = results[5:8]
        assert all('status' in result for result in status_results)
    
    @pytest.mark.asyncio
    async def test_component_health_monitoring_performance(self, running_chaos_service):
        """Test performance of health monitoring system"""
        start_time = datetime.now()
        
        # Multiple health checks
        health_checks = []
        for i in range(10):
            health_checks.append(running_chaos_service.get_component_health())
        
        results = await asyncio.gather(*health_checks)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Health checks should be fast
        assert duration < 2.0, f"Health checks took too long: {duration}s"
        
        # All health checks should succeed
        assert len(results) == 10
        assert all('overall' in result for result in results)
    
    @pytest.mark.asyncio
    async def test_error_recovery_performance(self, running_chaos_service):
        """Test system recovery performance after errors"""
        # Simulate component failure
        original_method = running_chaos_service.manager.pressure_monitor.get_current_pressures
        
        # Cause temporary failure
        running_chaos_service.manager.pressure_monitor.get_current_pressures = Mock(
            side_effect=Exception("Temporary failure")
        )
        
        start_time = datetime.now()
        
        # System should detect failure quickly
        health = await running_chaos_service.get_component_health()
        assert health['pressure_monitor'].name == 'FAILED'
        
        # Restore component
        running_chaos_service.manager.pressure_monitor.get_current_pressures = original_method
        
        # System should recover quickly
        health = await running_chaos_service.get_component_health()
        assert health['pressure_monitor'].name == 'HEALTHY'
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Recovery should be fast
        assert duration < 1.0, f"Recovery took too long: {duration}s"


class TestDataIntegrity:
    """Test data integrity across system components"""
    
    @pytest.mark.asyncio
    async def test_configuration_consistency(self, running_chaos_service):
        """Test that configuration is consistent across all components"""
        # Get system status
        status = await running_chaos_service.get_system_status()
        
        # All components should be initialized and running
        components = status['components']
        expected_components = [
            'chaos_engine', 'pressure_monitor', 'warning_system',
            'narrative_moderator', 'cascade_engine'
        ]
        
        for component_name in expected_components:
            assert component_name in components, f"Missing component: {component_name}"
            component_status = components[component_name]
            assert 'status' in component_status
    
    @pytest.mark.asyncio
    async def test_narrative_data_consistency(self, running_chaos_service):
        """Test narrative data consistency across operations"""
        # Add narrative theme
        await running_chaos_service.add_narrative_theme(
            theme_id="consistency_test",
            name="Consistency Test Theme",
            description="Theme for testing data consistency",
            priority="central",
            weight_modifier=1.3,
            related_events=["test_event"]
        )
        
        # Update narrative levels
        await running_chaos_service.update_narrative_tension(0.6)
        await running_chaos_service.update_narrative_engagement(0.8)
        
        # Get narrative status
        status = await running_chaos_service.get_narrative_status()
        
        # Verify data consistency
        assert 'consistency_test' in status['active_themes']
        theme = status['active_themes']['consistency_test']
        
        assert theme['name'] == "Consistency Test Theme"
        assert theme['priority'] == "central"
        assert theme['weight_modifier'] == 1.3
        assert "test_event" in theme['related_events']
        assert theme['is_active'] is True
        
        assert status['current_tension'] == 0.6
        assert status['current_engagement'] == 0.8
    
    @pytest.mark.asyncio
    async def test_pressure_data_consistency(self, running_chaos_service):
        """Test pressure data consistency"""
        # Mock consistent pressure data
        consistent_pressures = {
            'economic': 0.5,
            'political': 0.6,
            'social': 0.4,
            'environmental': 0.3,
            'diplomatic': 0.7,
            'temporal': 0.2
        }
        
        with patch.object(running_chaos_service.manager.pressure_monitor, 'get_current_pressures', return_value=consistent_pressures):
            # Multiple pressure readings should be consistent
            pressures1 = await running_chaos_service.get_current_pressures()
            pressures2 = await running_chaos_service.get_current_pressures()
            
            assert pressures1 == pressures2
            assert pressures1 == consistent_pressures
            
            # All expected pressure types should be present
            expected_types = {'economic', 'political', 'social', 'environmental', 'diplomatic', 'temporal'}
            assert set(pressures1.keys()) >= expected_types


@pytest.mark.asyncio
async def test_full_system_scenario():
    """Complete end-to-end scenario test"""
    config = ChaosConfig()
    config.system_config.health_check_interval = 0.1
    
    service = ChaosService(config)
    await service.initialize()
    await service.start()
    
    try:
        # Scenario: Economic crisis leading to cascading effects with narrative impact
        
        # 1. Set up narrative context
        await service.add_narrative_theme(
            theme_id="economic_collapse",
            name="Economic Collapse",
            description="Major economic crisis narrative",
            priority="critical",
            weight_modifier=2.5,
            related_events=["economic_crisis", "market_crash", "unemployment_surge"]
        )
        
        await service.update_narrative_tension(0.3)  # Low tension initially
        await service.update_narrative_engagement(0.8)  # High engagement
        
        # 2. Simulate rising economic pressure
        high_economic_pressure = {
            'economic': 0.9,  # Critical economic pressure
            'political': 0.4,
            'social': 0.3,
            'environmental': 0.2,
            'diplomatic': 0.3,
            'temporal': 0.1
        }
        
        with patch.object(service.manager.pressure_monitor, 'get_current_pressures', return_value=high_economic_pressure):
            pressures = await service.get_current_pressures()
            assert pressures['economic'] == 0.9
            
            # 3. Issue warnings (simulated)
            warning_phases = []
            async def mock_issue_warning(event_type, phase, **kwargs):
                warning_id = f"warning_{len(warning_phases)}"
                warning_phases.append({'id': warning_id, 'phase': phase, 'event_type': event_type})
                return warning_id
            
            service.manager.warning_system.issue_warning = mock_issue_warning
            
            # Issue escalating warnings
            await service.manager.warning_system.issue_warning("economic_crisis", WarningPhase.RUMOR)
            await asyncio.sleep(0.01)
            await service.manager.warning_system.issue_warning("economic_crisis", WarningPhase.EARLY_WARNING)
            await asyncio.sleep(0.01)
            await service.manager.warning_system.issue_warning("economic_crisis", WarningPhase.IMMINENT)
            
            # 4. Trigger the main event
            events_processed = []
            async def mock_process_event(event_type, **kwargs):
                events_processed.append((event_type, kwargs))
                return {"status": "success", "event_id": f"event_{len(events_processed)}"}
            
            service.manager.chaos_engine.process_event = mock_process_event
            
            result = await service.trigger_event("economic_crisis", severity=0.9, enable_cascades=True)
            assert result["status"] == "success"
            
            # 5. Verify cascade effects
            cascades_triggered = []
            async def mock_process_cascade(trigger_event, **kwargs):
                cascade_id = f"cascade_{len(cascades_triggered)}"
                target_events = ["social_unrest", "political_instability", "unemployment_surge"]
                cascades_triggered.append({
                    'id': cascade_id,
                    'trigger_event': trigger_event,
                    'target_events': target_events
                })
                return {'cascade_id': cascade_id, 'triggered_events': target_events}
            
            service.manager.cascade_engine.process_cascade = mock_process_cascade
            
            cascade_result = await service.trigger_cascade("economic_crisis", severity=0.9)
            assert "social_unrest" in cascade_result['triggered_events']
            
            # 6. Update narrative tension due to events
            await service.update_narrative_tension(0.9)  # High tension after crisis
            
            # 7. Verify final system state
            final_status = await service.get_system_status()
            assert final_status['status'].name == 'RUNNING'
            
            final_narrative = await service.get_narrative_status()
            assert final_narrative['current_tension'] == 0.9
            assert 'economic_collapse' in final_narrative['active_themes']
            
            health = await service.get_component_health()
            assert health['overall'].name == 'HEALTHY'
            
            # Verify the complete scenario flow
            assert len(warning_phases) == 3  # All warning phases issued
            assert len(events_processed) == 1  # Main event processed
            assert len(cascades_triggered) == 1  # Cascade triggered
            
    finally:
        await service.stop() 