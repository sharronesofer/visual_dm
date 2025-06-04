"""
Chaos Analytics - Business Logic

Business logic for chaos system analytics without infrastructure concerns.
Uses infrastructure analytics for all technical operations.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Business logic imports only
from backend.systems.chaos.core.config import ChaosConfig
from backend.infrastructure.analytics.chaos_analytics_complete import ChaosAnalyticsInfrastructure

class ChaosAnalytics:
    """
    Business logic for chaos system analytics.
    
    Provides high-level analytics operations while delegating all technical
    infrastructure concerns to the ChaosAnalyticsInfrastructure.
    """
    
    def __init__(self, config: ChaosConfig):
        self.config = config
        
        # Use infrastructure for all technical operations
        self.analytics_infrastructure = ChaosAnalyticsInfrastructure(config.to_dict())
        
        # Business logic state only
        self.is_initialized = False
        self.is_running = False
        
    async def initialize(self) -> None:
        """Initialize analytics with business logic validation"""
        try:
            # Validate business configuration
            if not self._validate_analytics_configuration():
                return False
            
            # Initialize infrastructure
            await self.analytics_infrastructure.initialize()
            
            self.is_initialized = True
            self.is_running = True
            
            return True
            
        except Exception as e:
            self.is_initialized = False
            return False
    
    def _validate_analytics_configuration(self) -> bool:
        """Validate analytics configuration from business perspective"""
        # Business logic validation
        if not self.config:
            return False
        
        # Ensure required business parameters are present
        required_params = ['update_interval_seconds', 'enabled']
        for param in required_params:
            if not hasattr(self.config, param):
                return False
        
        return True
    
    # Business Logic Event Tracking
    
    def track_event_created(self, chaos_event) -> None:
        """Track event creation from business perspective"""
        if not self.is_running:
            return
        
        # Extract business-relevant data
        event_data = {
            'event_id': chaos_event.event_id,
            'event_type': chaos_event.event_type.value if hasattr(chaos_event.event_type, 'value') else str(chaos_event.event_type),
            'severity': chaos_event.severity.value if hasattr(chaos_event.severity, 'value') else str(chaos_event.severity),
            'title': chaos_event.title,
            'description': chaos_event.description,
            'affected_regions': [str(r) for r in chaos_event.affected_regions],
            'global_event': chaos_event.global_event
        }
        
        # Delegate to infrastructure
        self.analytics_infrastructure.track_event_created(event_data)
    
    def track_event_triggered(self, chaos_event, chaos_state, pressure_data) -> None:
        """Track event triggering from business perspective"""
        if not self.is_running:
            return
        
        # Extract business-relevant data
        event_data = {
            'event_id': chaos_event.event_id,
            'affected_regions': [str(r) for r in chaos_event.affected_regions],
            'global_event': chaos_event.global_event
        }
        
        chaos_state_data = {
            'global_chaos_score': chaos_state.global_chaos_score,
            'regional_scores': {str(k): v for k, v in chaos_state.regional_chaos_scores.items()},
            'system_health': self._calculate_system_health(chaos_state)
        }
        
        pressure_data_dict = {
            'pressure_sources': pressure_data.pressure_sources,
            'stability_score': self._calculate_pressure_stability(pressure_data)
        }
        
        # Delegate to infrastructure
        self.analytics_infrastructure.track_event_triggered(event_data, chaos_state_data, pressure_data_dict)
    
    def track_event_resolved(self, event_id: str, resolution_type: str = "auto",
                           resolution_quality: float = 1.0, mitigation_applied: bool = False,
                           mitigation_effectiveness: float = 0.0) -> None:
        """Track event resolution with business logic validation"""
        if not self.is_running:
            return
        
        # Business logic validation
        resolution_quality = max(0.0, min(1.0, resolution_quality))  # Clamp to valid range
        mitigation_effectiveness = max(0.0, min(1.0, mitigation_effectiveness))
        
        # Delegate to infrastructure
        self.analytics_infrastructure.track_event_resolved(
            event_id, resolution_type, resolution_quality, 
            mitigation_applied, mitigation_effectiveness
        )
    
    def take_analytics_snapshot(self, chaos_state, pressure_data) -> None:
        """Take analytics snapshot with business context"""
        if not self.is_running:
            return
        
        # Extract business-relevant data
        chaos_state_data = {
            'global_chaos_score': chaos_state.global_chaos_score,
            'global_chaos_level': chaos_state.global_chaos_level.value if hasattr(chaos_state.global_chaos_level, 'value') else str(chaos_state.global_chaos_level),
            'regional_scores': {str(k): v for k, v in chaos_state.regional_chaos_scores.items()},
            'system_health': self._calculate_system_health(chaos_state)
        }
        
        pressure_data_dict = {
            'pressure_sources': pressure_data.pressure_sources,
            'stability_score': self._calculate_pressure_stability(pressure_data)
        }
        
        # Delegate to infrastructure
        self.analytics_infrastructure.take_analytics_snapshot(chaos_state_data, pressure_data_dict)
    
    # Business Logic Analysis
    
    async def analyze_event_patterns(self) -> Dict[str, Any]:
        """Analyze event patterns with business logic interpretation"""
        if not self.is_running:
            return {'error': 'Analytics not running'}
        
        # Get raw analysis from infrastructure
        raw_analysis = self.analytics_infrastructure.analyze_event_patterns()
        
        # Add business logic interpretation
        business_analysis = self._interpret_analysis_for_business(raw_analysis)
        
        return business_analysis
    
    def _interpret_analysis_for_business(self, raw_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret raw analytics for business use"""
        interpretation = {
            'raw_analysis': raw_analysis,
            'business_insights': {},
            'recommendations': []
        }
        
        # Business logic interpretation
        if 'event_frequency' in raw_analysis:
            freq_data = raw_analysis['event_frequency']
            total_events = freq_data.get('total_events', 0)
            avg_interval = freq_data.get('average_interval_hours', 0)
            
            if total_events > 0:
                if avg_interval < 6:  # Events happening very frequently
                    interpretation['business_insights']['event_frequency'] = 'high_stress'
                    interpretation['recommendations'].append('Consider pressure reduction measures')
                elif avg_interval > 48:  # Events rare
                    interpretation['business_insights']['event_frequency'] = 'stable'
                    interpretation['recommendations'].append('System appears stable')
                else:
                    interpretation['business_insights']['event_frequency'] = 'normal'
        
        if 'severity_distribution' in raw_analysis:
            severity_data = raw_analysis['severity_distribution']
            severity_percentages = severity_data.get('severity_percentages', {})
            
            high_severity_pct = severity_percentages.get('critical', 0) + severity_percentages.get('major', 0)
            if high_severity_pct > 30:  # More than 30% high severity
                interpretation['business_insights']['severity_trend'] = 'escalating'
                interpretation['recommendations'].append('Focus on mitigation strategies')
            else:
                interpretation['business_insights']['severity_trend'] = 'manageable'
        
        return interpretation
    
    # Business Logic Configuration
    
    async def get_configuration(self, path: Optional[str] = None) -> Any:
        """Get configuration with business logic validation"""
        if not self.is_running:
            return None
        
        return self.analytics_infrastructure.get_configuration(path)
    
    async def set_configuration(self, path: str, value: Any, changed_by: str = "system",
                              reason: str = "") -> bool:
        """Set configuration with business logic rules"""
        if not self.is_running:
            return False
        
        # Business logic validation
        if not self._validate_configuration_change_from_business_perspective(path, value):
            return False
        
        return await self.analytics_infrastructure.set_configuration(path, value, changed_by, reason)
    
    def _validate_configuration_change_from_business_perspective(self, path: str, value: Any) -> bool:
        """Validate configuration changes from business logic perspective"""
        # Business rules for configuration changes
        
        # Pressure weights must maintain balance
        if path.startswith('pressure_weights'):
            # Ensure no weight is too dominant
            if isinstance(value, (int, float)) and value > 1.5:
                return False  # Too high, could destabilize system
        
        # Chaos thresholds must be properly ordered
        if path.startswith('chaos_thresholds'):
            if isinstance(value, (int, float)):
                if value < 0.0 or value > 1.0:
                    return False  # Outside valid range
        
        return True
    
    # Utility Business Logic
    
    def _calculate_system_health(self, chaos_state) -> float:
        """Calculate system health from business perspective"""
        base_health = 1.0 - chaos_state.global_chaos_score
        
        # Adjust for regional imbalances
        regional_scores = list(chaos_state.regional_chaos_scores.values())
        if regional_scores:
            max_regional = max(regional_scores)
            min_regional = min(regional_scores)
            imbalance_penalty = (max_regional - min_regional) * 0.2
            base_health -= imbalance_penalty
        
        return max(0.0, min(1.0, base_health))
    
    def _calculate_pressure_stability(self, pressure_data) -> float:
        """Calculate pressure stability from business perspective"""
        pressure_values = list(pressure_data.pressure_sources.values())
        if not pressure_values:
            return 1.0
        
        # Stability is inverse of pressure variance
        avg_pressure = sum(pressure_values) / len(pressure_values)
        variance = sum((p - avg_pressure) ** 2 for p in pressure_values) / len(pressure_values)
        stability = 1.0 - min(variance, 1.0)  # Cap variance effect
        
        return max(0.0, min(1.0, stability))
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status from business perspective"""
        if not self.is_running:
            return {'status': 'not_running', 'analytics_enabled': False}
        
        infrastructure_status = self.analytics_infrastructure.get_system_status()
        
        # Add business logic status
        business_status = {
            'status': 'running',
            'analytics_enabled': True,
            'business_config_valid': self._validate_analytics_configuration(),
            'infrastructure_status': infrastructure_status
        }
        
        return business_status
    
    async def shutdown(self) -> None:
        """Shutdown analytics with business logic cleanup"""
        try:
            # Business logic cleanup
            self.is_running = False
            
            # Save final analytics data
            if self.analytics_infrastructure:
                await self.analytics_infrastructure.save_analytics_data()
            
            self.is_initialized = False
            
        except Exception:
            pass 