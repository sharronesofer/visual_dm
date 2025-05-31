"""
Chaos Engine

Main engine that coordinates all chaos system operations.
This is the heart of the hidden narrative engine.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import random

from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.models.chaos_state import ChaosState, ChaosLevel
from backend.systems.chaos.models.pressure_data import PressureData
from backend.systems.chaos.models.chaos_events import ChaosEvent
from backend.systems.chaos.core.pressure_monitor import PressureMonitor
from backend.systems.chaos.services.event_manager import EventManager
from backend.systems.chaos.core.system_integrator import SystemIntegrator
from backend.systems.chaos.analytics.chaos_analytics import ChaosAnalytics
from backend.systems.chaos.utils.chaos_math import ChaosMath, ChaosCalculationResult

logger = logging.getLogger(__name__)

class ChaosEngine:
    """
    Main chaos engine responsible for coordinating the entire chaos system.
    
    This engine:
    - Monitors pressure across all game systems
    - Calculates chaos levels based on weighted factors  
    - Triggers chaos events when thresholds are exceeded
    - Handles event cascading and mitigation
    - Maintains narrative coherence
    - Remains completely hidden from players
    """
    
    _instance: Optional['ChaosEngine'] = None
    
    def __init__(self, config: Optional[ChaosConfig] = None):
        """Initialize the chaos engine with configuration."""
        if ChaosEngine._instance is not None:
            raise RuntimeError("ChaosEngine is a singleton. Use get_instance() instead.")
            
        self.config = config or ChaosConfig()
        
        # Initialize core components
        self.pressure_monitor = PressureMonitor(self.config)
        self.chaos_math = ChaosMath(self.config)
        self.event_manager = EventManager(self.config)
        self.system_integrator = SystemIntegrator(self.config)
        self.analytics = ChaosAnalytics(self.config)
        
        # State tracking
        self.current_chaos_state: Optional[ChaosState] = None
        self.current_pressure_data: Optional[PressureData] = None
        
        # Runtime flags
        self.is_running: bool = False
        self.is_paused: bool = False
        self.background_tasks: List[asyncio.Task] = []
        
        # Performance metrics
        self.last_calculation_time = datetime.now()
        self.calculation_count = 0
        
        ChaosEngine._instance = self
        logger.info("Chaos Engine initialized")
        
    @classmethod
    def get_instance(cls, config: Optional[ChaosConfig] = None) -> 'ChaosEngine':
        """Get the singleton chaos engine instance."""
        if cls._instance is None:
            if config is None:
                raise ValueError("Config required for first-time initialization")
            cls._instance = cls(config)
        return cls._instance
    
    async def initialize(self) -> None:
        """Initialize the chaos engine and all components."""
        try:
            logger.info("Initializing Chaos Engine...")
            
            # Initialize components
            await self.pressure_monitor.initialize()
            await self.event_manager.initialize()
            await self.system_integrator.initialize()
            await self.analytics.initialize()
            
            # Connect event manager to system integrator for event dispatching
            self.event_manager.set_event_dispatcher(self.system_integrator)
            self.system_integrator.set_chaos_engine(self)
            
            # Initialize chaos state
            initial_pressure = await self.pressure_monitor.collect_all_pressure()
            self.current_pressure_data = initial_pressure
            
            # Calculate initial chaos state
            chaos_result = self.chaos_math.calculate_chaos_score(initial_pressure)
            self.current_chaos_state = ChaosState.from_calculation_result(chaos_result)
            
            logger.info("Chaos Engine initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize Chaos Engine: {e}")
            raise
    
    async def start(self) -> None:
        """Start the chaos engine monitoring loop."""
        if self.is_running:
            logger.warning("Chaos engine is already running")
            return
            
        # Initialize if not already done
        if not hasattr(self, '_initialized'):
            await self.initialize()
            self._initialized = True
            
        self.is_running = True
        self.is_paused = False
        
        # Start the monitoring task
        background_task = asyncio.create_task(self._background_loop())
        self.background_tasks.append(background_task)
        
        logger.info("Chaos Engine started")
        
    async def stop(self) -> None:
        """Stop the chaos engine."""
        self.is_running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        # Stop components
        await self.pressure_monitor.stop()
        await self.system_integrator.shutdown()
                
        logger.info("Chaos Engine stopped")
        
    def pause(self) -> None:
        """Pause chaos monitoring without stopping the engine."""
        self.is_paused = True
        logger.info("Chaos Engine paused")
        
    def resume(self) -> None:
        """Resume chaos monitoring."""
        self.is_paused = False
        logger.info("Chaos Engine resumed")
        
    async def _background_loop(self) -> None:
        """Main background loop for chaos calculations and event processing"""
        try:
            while self.is_running:
                if not self.is_paused:
                    context_id = self.analytics.start_operation("chaos_calculation_cycle")
                    
                    try:
                        # Collect current pressure data
                        pressure_context = self.analytics.start_operation("pressure_collection")
                        try:
                            pressure_data = await self.pressure_monitor.collect_all_pressure()
                            self.current_pressure_data = pressure_data
                        finally:
                            self.analytics.end_operation(pressure_context, True, "pressure_collection")
                        
                        # Calculate chaos score and state
                        calc_context = self.analytics.start_operation("chaos_calculation")
                        try:
                            chaos_result = self.chaos_math.calculate_chaos_score(pressure_data)
                            self.current_chaos_state = ChaosState.from_calculation_result(chaos_result)
                        finally:
                            self.analytics.end_operation(calc_context, True, "chaos_calculation")
                        
                        # Process events based on current chaos state
                        event_context = self.analytics.start_operation("event_processing")
                        try:
                            await self.event_manager.process_chaos_state(
                                chaos_result, pressure_data, self.current_chaos_state
                            )
                        finally:
                            self.analytics.end_operation(event_context, True, "event_processing")
                        
                        # Update calculation metrics
                        self.calculation_count += 1
                        self.last_calculation_time = datetime.now()
                        
                        # Record performance metrics
                        self.analytics.record_metric(
                            'chaos_score', chaos_result.chaos_score, 'chaos_calculation'
                        )
                        
                    except Exception as e:
                        logger.error(f"Error in chaos calculation cycle: {e}")
                        self.analytics.end_operation(context_id, False, "chaos_calculation_cycle")
                    else:
                        self.analytics.end_operation(context_id, True, "chaos_calculation_cycle")
                
                # Wait for next calculation cycle
                await asyncio.sleep(self.config.chaos_calculation_interval)
                
        except asyncio.CancelledError:
            logger.info("Chaos Engine background loop cancelled")
        except Exception as e:
            logger.error(f"Error in Chaos Engine background loop: {e}")
            
    def _update_chaos_state(self, chaos_result: ChaosCalculationResult) -> None:
        """Update the current chaos state based on calculation results."""
        
        # Update basic metrics
        self.current_chaos_state.current_chaos_score = chaos_result.chaos_score
        
        # Check for level changes
        level_changed = self.current_chaos_state.update_chaos_level(chaos_result.chaos_level)
        
        # Update trends and velocity
        self.current_chaos_state.chaos_trend = chaos_result.temporal_factors.get('trend', 0.0)
        self.current_chaos_state.chaos_velocity = chaos_result.temporal_factors.get('velocity', 0.0)
        self.current_chaos_state.pressure_momentum = chaos_result.temporal_factors.get('momentum', 0.0)
        
        # Update regional breakdown
        if chaos_result.regional_scores:
            self.current_chaos_state.regional_chaos_scores = chaos_result.regional_scores
            # Map regional scores to chaos levels
            for region_id, score in chaos_result.regional_scores.items():
                regional_level = self._determine_chaos_level_from_score(score)
                self.current_chaos_state.regional_chaos_levels[region_id] = regional_level
        
        # Update source contributions
        if chaos_result.source_contributions:
            self.current_chaos_state.pressure_source_contributions = {
                source.value if hasattr(source, 'value') else str(source): contribution
                for source, contribution in chaos_result.source_contributions.items()
            }
            
            # Find dominant source
            if self.current_chaos_state.pressure_source_contributions:
                dominant_source = max(
                    self.current_chaos_state.pressure_source_contributions.items(),
                    key=lambda x: x[1]
                )[0]
                self.current_chaos_state.dominant_pressure_source = dominant_source
        
        # Update temporal factors
        self.current_chaos_state.temporal_adjustments = chaos_result.temporal_factors
        
        # Remove expired mitigations
        self.current_chaos_state.remove_expired_mitigations()
        
        # Update calculation timestamp
        self.current_chaos_state.calculation_timestamp = datetime.now()
        
        # Update score history
        self.current_chaos_state.update_score_history()
        
        # Calculate risk assessment
        self.current_chaos_state.calculate_risk_assessment()
        
        # Log level changes
        if level_changed:
            logger.info(f"Chaos level changed: {self.current_chaos_state.previous_chaos_level.value} -> "
                       f"{self.current_chaos_state.current_chaos_level.value} (score: {chaos_result.chaos_score:.3f})")
    
    def _determine_chaos_level_from_score(self, score: float) -> ChaosLevel:
        """Determine chaos level from a chaos score."""
        if score >= 0.9:
            return ChaosLevel.EXTREME
        elif score >= 0.7:
            return ChaosLevel.CRITICAL
        elif score >= 0.5:
            return ChaosLevel.HIGH
        elif score >= 0.3:
            return ChaosLevel.ELEVATED
        elif score >= 0.1:
            return ChaosLevel.STABLE
        else:
            return ChaosLevel.DORMANT
    
    async def _cleanup_expired_data(self) -> None:
        """Clean up expired data and maintain system health."""
        try:
            # Clean up old pressure readings
            removed_readings = self.current_pressure_data.cleanup_old_readings(
                max_age_hours=self.config.max_pressure_history_hours
            )
            
            if removed_readings > 0:
                logger.debug(f"Cleaned up {removed_readings} old pressure readings")
            
            # Clean up expired cooldowns
            self.current_chaos_state.clean_expired_cooldowns()
            
            # Update system health metrics
            self._update_system_health()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _update_system_health(self) -> None:
        """Update system health metrics."""
        try:
            # Calculate overall system health based on various factors
            health_factors = []
            
            # Monitor calculation timing
            if self.calculation_count > 0:
                average_calculation_time_ms = (datetime.now() - self.last_calculation_time).total_seconds() * 1000 / self.calculation_count
                if average_calculation_time_ms < 100:  # Under 100ms is good
                    health_factors.append(1.0)
                elif average_calculation_time_ms < 500:  # Under 500ms is okay
                    health_factors.append(0.7)
                else:
                    health_factors.append(0.3)  # Over 500ms is concerning
            
            # Monitor pressure data freshness
            time_since_last_reading = (datetime.now() - self.current_pressure_data.last_calculation).total_seconds()
            if time_since_last_reading < 60:  # Fresh data
                health_factors.append(1.0)
            elif time_since_last_reading < 300:  # Somewhat stale
                health_factors.append(0.6)
            else:
                health_factors.append(0.2)  # Very stale
            
            # Monitor error rate
            if self.current_pressure_data.errors_encountered == 0:
                health_factors.append(1.0)
            else:
                error_rate = self.current_pressure_data.errors_encountered / max(1, self.current_pressure_data.readings_processed)
                health_factors.append(max(0.0, 1.0 - error_rate * 5))  # Penalize errors
            
            # Calculate average health
            self.current_chaos_state.system_health = sum(health_factors) / len(health_factors)
            
            # Calculate pressure stability
            if len(self.current_chaos_state.score_history) >= 2:
                recent_scores = [score for _, score in self.current_chaos_state.score_history[-10:]]
                if len(recent_scores) >= 2:
                    variance = sum((score - sum(recent_scores)/len(recent_scores))**2 for score in recent_scores) / len(recent_scores)
                    # Lower variance = higher stability
                    self.current_chaos_state.pressure_stability = max(0.0, 1.0 - variance * 2)
                else:
                    self.current_chaos_state.pressure_stability = 1.0
            else:
                self.current_chaos_state.pressure_stability = 1.0
                
        except Exception as e:
            logger.error(f"Error updating system health: {e}")
            self.current_chaos_state.system_health = 0.5  # Default to moderate health
            self.current_chaos_state.pressure_stability = 0.5
    
    def _update_metrics(self, start_time: datetime, events_triggered: int) -> None:
        """Update performance metrics."""
        calculation_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        self.calculation_count += 1
        self.last_calculation_time = datetime.now()
        
        # Update pressure data metrics
        self.current_pressure_data.calculation_time_ms = calculation_time_ms
    
    def _log_chaos_state_changes(self, chaos_result: ChaosCalculationResult) -> None:
        """Log significant changes in chaos state."""
        try:
            # Log level changes (already logged in _update_chaos_state)
            
            # Log significant score changes
            if len(self.current_chaos_state.score_history) >= 2:
                previous_score = self.current_chaos_state.score_history[-2][1]
                current_score = chaos_result.chaos_score
                score_change = abs(current_score - previous_score)
                
                if score_change >= 0.1:  # 10% change threshold
                    direction = "increased" if current_score > previous_score else "decreased"
                    logger.info(f"Chaos score {direction} significantly: "
                               f"{previous_score:.3f} -> {current_score:.3f} "
                               f"(change: {score_change:.3f})")
            
            # Log dominant pressure source changes
            if (self.current_chaos_state.dominant_pressure_source and 
                chaos_result.source_contributions):
                
                current_dominant = max(
                    chaos_result.source_contributions.items(),
                    key=lambda x: x[1]
                )[0]
                
                current_dominant_str = current_dominant.value if hasattr(current_dominant, 'value') else str(current_dominant)
                
                if (self.current_chaos_state.dominant_pressure_source != current_dominant_str):
                    logger.info(f"Dominant pressure source changed: "
                               f"{self.current_chaos_state.dominant_pressure_source} -> {current_dominant_str}")
                               
        except Exception as e:
            logger.debug(f"Error logging chaos state changes: {e}")
    
    def _should_notify_pressure_change(self, chaos_result: ChaosCalculationResult) -> bool:
        """Determine if pressure changes are significant enough to notify other systems"""
        # Only notify on significant changes or level transitions
        if len(self.current_chaos_state.score_history) >= 2:
            previous_score = self.current_chaos_state.score_history[-2][1]
            score_change = abs(chaos_result.chaos_score - previous_score)
            
            # Notify on 5% change or level change
            if score_change >= 0.05 or self.current_chaos_state.chaos_level != self.current_chaos_state.previous_chaos_level:
                return True
        
        return False
    
    # Public API methods
    
    def get_current_chaos_state(self) -> Dict[str, Any]:
        """Get current chaos state for analytics"""
        if not self.current_chaos_state:
            return {}
        
        return {
            'current_chaos_score': self.current_chaos_state.current_chaos_score,
            'current_chaos_level': self.current_chaos_state.current_chaos_level.value,
            'calculation_timestamp': self.current_chaos_state.calculation_timestamp.isoformat(),
            'regional_chaos_scores': self.current_chaos_state.regional_chaos_scores,
            'system_health': self.current_chaos_state.system_health,
            'pressure_stability': self.current_chaos_state.pressure_stability
        }
    
    def get_regional_chaos_state(self, region_id: str) -> Dict[str, Any]:
        """Get chaos state for a specific region."""
        return self.current_chaos_state.get_regional_chaos_summary(region_id)
    
    def get_active_events(self) -> List[ChaosEvent]:
        """Get currently active chaos events"""
        return self.event_manager.get_active_events()
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event system statistics"""
        return self.event_manager.get_event_statistics()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'calculation_count': self.calculation_count,
            'last_calculation': self.last_calculation_time.isoformat(),
            'active_background_tasks': len([t for t in self.background_tasks if not t.done()]),
            'system_health': self.current_chaos_state.system_health if self.current_chaos_state else 0.0,
            'pressure_stability': self.current_chaos_state.pressure_stability if self.current_chaos_state else 0.0,
            'connected_systems': [name for name in getattr(self.system_integrator, 'system_connections', {}).keys()],
            'analytics_enabled': self.analytics.is_initialized
        }
    
    def get_pressure_summary(self) -> Dict[str, Any]:
        """Get current pressure summary for analytics"""
        if not self.current_pressure_data:
            return {}
        
        return {
            'overall_pressure': self.current_pressure_data.global_pressure.get_overall_pressure(),
            'source_breakdown': self.current_pressure_data.global_pressure.get_pressure_breakdown(),
            'regional_pressure': {
                str(region_id): pressure.get_overall_pressure()
                for region_id, pressure in self.current_pressure_data.regional_pressures.items()
            },
            'last_calculation': self.last_calculation_time.isoformat()
        }
    
    async def apply_mitigation(self, mitigation_type: str, effectiveness: float,
                             duration_hours: float, source_id: str, source_type: str,
                             description: str = "", affected_regions: List[str] = None,
                             affected_sources: List[str] = None) -> bool:
        """Apply a mitigation factor"""
        try:
            context_id = self.analytics.start_operation("mitigation_application")
            
            try:
                success = await self.event_manager.apply_mitigation(
                    mitigation_type, effectiveness, duration_hours, source_id, source_type,
                    description, affected_regions or [], affected_sources or []
                )
                
                if success:
                    logger.info(f"Applied mitigation: {mitigation_type} (effectiveness: {effectiveness})")
                
                return success
                
            finally:
                self.analytics.end_operation(context_id, success, "mitigation_application")
                
        except Exception as e:
            logger.error(f"Error applying mitigation: {e}")
            return False
    
    async def force_trigger_event(self, event_type: str, severity: str = "moderate",
                                regions: List[str] = None) -> bool:
        """Force trigger a chaos event (for testing/admin purposes)"""
        try:
            context_id = self.analytics.start_operation("force_trigger_event")
            
            try:
                success = await self.event_manager.force_trigger_event(event_type, severity, regions or [])
                
                if success:
                    logger.info(f"Force triggered event: {event_type} ({severity})")
                
                return success
                
            finally:
                self.analytics.end_operation(context_id, success, "force_trigger_event")
                
        except Exception as e:
            logger.error(f"Error force triggering event: {e}")
            return False
    
    def update_config(self, **kwargs) -> None:
        """Update chaos engine configuration."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.info(f"Updated config: {key} = {value}")
            else:
                logger.warning(f"Unknown config parameter: {key}")
    
    def set_event_dispatcher(self, event_dispatcher) -> None:
        """Set the event dispatcher for system integration."""
        self.event_manager.set_event_dispatcher(event_dispatcher)
        logger.info("Event dispatcher connected to chaos engine")
    
    def connect_system(self, system_name: str, system_handler) -> None:
        """Connect a game system to the chaos engine."""
        # This would be implemented to manually connect systems
        logger.info(f"Manual system connection request for {system_name}")
        
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        try:
            health_data = {
                'overall_health': 'good',
                'connected_systems': 0,
                'failed_systems': 0,
                'system_status': {},
                'integration_metrics': {},
                'last_check': datetime.now().isoformat()
            }
            
            # Get system integrator health
            if self.system_integrator:
                integrator_health = await self.system_integrator.get_system_health()
                health_data.update(integrator_health)
            
            # Add analytics health
            analytics_status = self.analytics.get_system_status()
            health_data['analytics_status'] = analytics_status
            
            # Determine overall health
            if self.is_running and not self.is_paused:
                if health_data['failed_systems'] == 0:
                    health_data['overall_health'] = 'excellent'
                elif health_data['failed_systems'] < health_data['connected_systems'] / 4:
                    health_data['overall_health'] = 'good'
                elif health_data['failed_systems'] < health_data['connected_systems'] / 2:
                    health_data['overall_health'] = 'fair'
                else:
                    health_data['overall_health'] = 'poor'
            else:
                health_data['overall_health'] = 'stopped'
            
            return health_data
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return {
                'overall_health': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

    async def shutdown(self) -> None:
        """Shutdown the chaos engine gracefully"""
        try:
            logger.info("Shutting down Chaos Engine...")
            
            self.is_running = False
            
            # Cancel background tasks
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Shutdown components
            await self.analytics.shutdown()
            await self.system_integrator.shutdown()
            await self.event_manager.shutdown()
            
            logger.info("Chaos Engine shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Chaos Engine shutdown: {e}")


def get_chaos_engine() -> ChaosEngine:
    """Get the global chaos engine instance."""
    return ChaosEngine.get_instance() 