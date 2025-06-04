"""
Chaos Manager

Consolidated manager that serves as the single point of coordination for all chaos system components.
Implements the Development Bible requirement for unified chaos management.
"""

import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass

from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.core.chaos_engine import ChaosEngine
from backend.systems.chaos.core.pressure_monitor import PressureMonitor
from backend.systems.chaos.core.warning_system import WarningSystem
from backend.systems.chaos.core.narrative_moderator import NarrativeModerator
from backend.systems.chaos.core.cascade_engine import CascadeEngine
from backend.systems.chaos.services.llm_service import ChaosLLMService

# Status constants for the chaos system
class ChaosSystemStatus:
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class SystemStatus:
    """Status information for a chaos subsystem"""
    name: str
    initialized: bool
    running: bool
    healthy: bool
    last_activity: Optional[datetime]
    error_count: int
    
class ChaosManager:
    """
    Unified manager for the entire chaos system.
    
    This manager coordinates all chaos subsystems and provides a single interface
    for external systems to interact with the chaos functionality.
    
    Components managed:
    - ChaosEngine: Core event generation and processing
    - PressureMonitor: System pressure tracking and calculation
    - WarningSystem: Three-tier escalation warnings
    - NarrativeModerator: Narrative intelligence weighting
    - CascadeEngine: Event cascade processing
    - LLMService: AI-powered text generation and reasoning
    """
    
    def __init__(self, config: Optional[ChaosConfig] = None):
        self.config = config or ChaosConfig()
        
        # Core components
        self.chaos_engine: Optional[ChaosEngine] = None
        self.pressure_monitor: Optional[PressureMonitor] = None
        self.warning_system: Optional[WarningSystem] = None
        self.narrative_moderator: Optional[NarrativeModerator] = None
        self.cascade_engine: Optional[CascadeEngine] = None
        self.llm_service: Optional[ChaosLLMService] = None
        
        # Manager state
        self._initialized = False
        self._running = False
        self._paused = False
        self._shutdown_requested = False
        self._status = ChaosSystemStatus.STOPPED
        
        # Performance tracking
        self.startup_time: Optional[datetime] = None
        self.start_time: Optional[datetime] = None
        self.last_health_check: Optional[datetime] = None
        self.component_statuses: Dict[str, SystemStatus] = {}
        
        # Error tracking
        self.error_history: List[tuple] = []  # (timestamp, component, error)
        self.performance_metrics: List[dict] = []  # Performance metrics storage
        self.max_error_history = 100
        
        # Async coordination
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._coordinator_task: Optional[asyncio.Task] = None
        
        print("ChaosManager created - unified chaos system coordinator")
    
    @property
    def status(self) -> str:
        """Get current system status"""
        return self._status
    
    def _set_status(self, new_status: str) -> None:
        """Set system status"""
        self._status = new_status
    
    async def initialize(self) -> bool:
        """
        Initialize all chaos system components.
        
        Returns:
            True if all components initialized successfully
        """
        if self._initialized:
            print("ChaosManager already initialized")
            return True
        
        try:
            print("Initializing ChaosManager and all subsystems...")
            
            # Initialize components in dependency order
            success = True
            
            # 1. Initialize LLM service first (provides services to others)
            print("  Initializing LLMService...")
            self.llm_service = ChaosLLMService(self.config)
            await self.llm_service.initialize()
            self._update_component_status("llm_service", initialized=True)
            
            # 2. Initialize pressure monitor (provides data to others)
            print("  Initializing PressureMonitor...")
            self.pressure_monitor = PressureMonitor(self.config)
            await self.pressure_monitor.initialize()
            self._update_component_status("pressure_monitor", initialized=True)
            
            # 3. Initialize narrative moderator
            print("  Initializing NarrativeModerator...")
            self.narrative_moderator = NarrativeModerator(self.config)
            await self.narrative_moderator.initialize()
            self._update_component_status("narrative_moderator", initialized=True)
            
            # 4. Initialize warning system (can now use LLM service)
            print("  Initializing WarningSystem...")
            self.warning_system = WarningSystem(self.config)
            self.warning_system.set_llm_service(self.llm_service)  # Wire up LLM service
            await self.warning_system.initialize()
            self._update_component_status("warning_system", initialized=True)
            
            # 5. Initialize main chaos engine (depends on others)
            print("  Initializing ChaosEngine...")
            self.chaos_engine = ChaosEngine(
                config=self.config,
                pressure_monitor=self.pressure_monitor
            )
            await self.chaos_engine.initialize()
            self._update_component_status("chaos_engine", initialized=True)
            
            # 6. Initialize cascade engine (can now use LLM service)
            print("  Initializing CascadeEngine...")
            self.cascade_engine = CascadeEngine(self.config)
            self.cascade_engine.set_llm_service(self.llm_service)  # Wire up LLM service
            await self.cascade_engine.initialize()
            self._update_component_status("cascade_engine", initialized=True)
            
            # 7. Initialize mitigation service if available
            from backend.systems.chaos.services.mitigation_service import MitigationService
            print("  Initializing MitigationService...")
            self.mitigation_service = MitigationService(self.config)
            self.mitigation_service.set_llm_service(self.llm_service)  # Wire up LLM service
            self._update_component_status("mitigation_service", initialized=True)
            
            # Mark as initialized
            self._initialized = True
            self.startup_time = datetime.now()
            
            print("ChaosManager initialization complete - all subsystems ready")
            return True
            
        except Exception as e:
            print(f"Error during ChaosManager initialization: {e}")
            self._record_error("manager", e)
            self._set_status(ChaosSystemStatus.ERROR)
            await self._cleanup_failed_initialization()
            return False
    
    async def start(self) -> bool:
        """
        Start all chaos system components.
        
        Returns:
            True if all components started successfully
        """
        if not self._initialized:
            print("ChaosManager not initialized - calling initialize() first")
            if not await self.initialize():
                return False
        
        if self._running:
            print("ChaosManager already running")
            return True
        
        try:
            print("Starting ChaosManager and all subsystems...")
            
            # Start components in dependency order
            components_to_start = [
                ("llm_service", self.llm_service),
                ("pressure_monitor", self.pressure_monitor),
                ("narrative_moderator", self.narrative_moderator),
                ("warning_system", self.warning_system),
                ("chaos_engine", self.chaos_engine),
                ("cascade_engine", self.cascade_engine),
                ("mitigation_service", getattr(self, 'mitigation_service', None))
            ]
            
            for name, component in components_to_start:
                if component:
                    if hasattr(component, 'start'):
                        print(f"  Starting {name}...")
                        await component.start()
                        self._update_component_status(name, running=True)
                    else:
                        print(f"  {name} does not require starting")
                        self._update_component_status(name, running=True)
                else:
                    print(f"  Warning: {name} not initialized, skipping start")
            
            # Start manager coordination tasks
            self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
            self._coordinator_task = asyncio.create_task(self._coordination_loop())
            
            self._running = True
            self.start_time = datetime.now()
            self._set_status(ChaosSystemStatus.RUNNING)
            
            print("ChaosManager started successfully - all components running")
            return True
            
        except Exception as e:
            print(f"Error starting ChaosManager: {e}")
            self._record_error("manager", e)
            self._set_status(ChaosSystemStatus.ERROR)
            return False
    
    async def stop(self) -> None:
        """
        Stop all chaos system components.
        """
        if not self._running:
            print("ChaosManager not running")
            return
        
        print("Stopping ChaosManager and all subsystems...")
        
        self._shutdown_requested = True
        self._running = False
        self._paused = False
        
        # Stop coordination tasks first
        if self._coordinator_task:
            self._coordinator_task.cancel()
            try:
                await self._coordinator_task
            except asyncio.CancelledError:
                pass
        
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Stop components in reverse order
        components_to_stop = [
            ("mitigation_service", getattr(self, 'mitigation_service', None)),
            ("cascade_engine", self.cascade_engine),
            ("chaos_engine", self.chaos_engine),
            ("warning_system", self.warning_system),
            ("narrative_moderator", self.narrative_moderator),
            ("pressure_monitor", self.pressure_monitor),
            ("llm_service", self.llm_service)
        ]
        
        for name, component in components_to_stop:
            if component and hasattr(component, 'stop'):
                try:
                    print(f"  Stopping {name}...")
                    await component.stop()
                    self._update_component_status(name, running=False)
                except Exception as e:
                    print(f"Error stopping {name}: {e}")
                    self._record_error(name, e)
        
        self._set_status(ChaosSystemStatus.STOPPED)
        print("ChaosManager stopped")
    
    async def pause(self) -> None:
        """Pause chaos system operations without stopping."""
        if not self._running:
            print("ChaosManager not running - cannot pause")
            return
        
        if self._paused:
            print("ChaosManager already paused")
            return
        
        print("Pausing chaos system operations...")
        
        try:
            if self.chaos_engine:
                await self.chaos_engine.pause()
            if self.pressure_monitor:
                await self.pressure_monitor.pause()
            if self.warning_system:
                await self.warning_system.pause()
            if self.narrative_moderator:
                await self.narrative_moderator.pause()
            if self.cascade_engine:
                await self.cascade_engine.pause()
            
            self._paused = True
            self._set_status(ChaosSystemStatus.PAUSED)
            print("Chaos system paused")
            
        except Exception as e:
            print(f"Error pausing chaos system: {e}")
            self._record_error("manager", e)
    
    async def resume(self) -> None:
        """Resume chaos system operations after pause."""
        if not self._running:
            print("ChaosManager not running - cannot resume")
            return
        
        if not self._paused:
            print("ChaosManager not paused - already running")
            return
        
        print("Resuming chaos system operations...")
        
        try:
            if self.chaos_engine:
                await self.chaos_engine.resume()
            if self.pressure_monitor:
                await self.pressure_monitor.resume()
            if self.warning_system:
                await self.warning_system.resume()
            if self.narrative_moderator:
                await self.narrative_moderator.resume()
            if self.cascade_engine:
                await self.cascade_engine.resume()
            
            self._paused = False
            self._set_status(ChaosSystemStatus.RUNNING)
            print("Chaos system resumed")
            
        except Exception as e:
            print(f"Error resuming chaos system: {e}")
            self._record_error("manager", e)
    
    async def _health_monitor_loop(self) -> None:
        """Monitor health of all components."""
        while self._running and not self._shutdown_requested:
            try:
                await self._perform_health_check()
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in health monitor loop: {e}")
                self._record_error("health_monitor", e)
                await asyncio.sleep(120)  # Wait longer on error
    
    async def _coordination_loop(self) -> None:
        """Coordinate between components and handle cross-component logic."""
        while self._running and not self._shutdown_requested:
            try:
                await self._coordinate_components()
                await asyncio.sleep(30)  # Coordinate every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in coordination loop: {e}")
                self._record_error("coordinator", e)
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _perform_health_check(self) -> None:
        """Perform health check on all components."""
        self.last_health_check = datetime.now()
        
        components = [
            ("pressure_monitor", self.pressure_monitor),
            ("narrative_moderator", self.narrative_moderator),
            ("warning_system", self.warning_system),
            ("chaos_engine", self.chaos_engine),
            ("cascade_engine", self.cascade_engine)
        ]
        
        for name, component in components:
            if component:
                try:
                    # Check if component has health check method
                    if hasattr(component, 'get_health_status'):
                        health_status = await component.get_health_status()
                        is_healthy = health_status.get('status', 'unknown') == 'healthy'
                    else:
                        # Basic health check - component exists and appears functional
                        is_healthy = hasattr(component, '_running') and getattr(component, '_running', False)
                    
                    self._update_component_status(name, healthy=is_healthy)
                    
                except Exception as e:
                    print(f"Health check failed for {name}: {e}")
                    self._record_error(name, e)
                    self._update_component_status(name, healthy=False)
    
    async def _coordinate_components(self) -> None:
        """Coordinate between components for cross-component functionality."""
        if not all([self.chaos_engine, self.pressure_monitor, self.warning_system, self.narrative_moderator, self.cascade_engine]):
            return
        
        try:
            # Get current pressure data
            pressure_data = self.pressure_monitor.get_current_pressure_data()
            
            # Update narrative context based on pressure
            narrative_context = self.narrative_moderator.get_narrative_status()
            
            # Check if warnings should be triggered based on pressure and narrative state
            if pressure_data and hasattr(pressure_data, 'regional_data'):
                for region_id, regional_data in pressure_data.regional_data.items():
                    chaos_level = getattr(regional_data, 'chaos_level', 0.0)
                    
                    # Let warning system check if warnings should be triggered
                    await self.warning_system.check_and_trigger_warnings(
                        region_id, chaos_level, regional_data
                    )
            
            # Coordinate narrative weighting with chaos engine
            if hasattr(self.chaos_engine, 'update_narrative_weights'):
                narrative_weights = await self.narrative_moderator.get_event_weights(
                    narrative_context, pressure_data
                )
                await self.chaos_engine.update_narrative_weights(narrative_weights)
            
            # Coordinate cascade processing with chaos engine
            if hasattr(self.chaos_engine, 'update_cascade_weights'):
                cascade_weights = await self.cascade_engine.get_cascade_weights(
                    pressure_data
                )
                await self.chaos_engine.update_cascade_weights(cascade_weights)
            
        except Exception as e:
            print(f"Error in component coordination: {e}")
            self._record_error("coordinator", e)
    
    def _update_component_status(self, component_name: str, 
                               initialized: Optional[bool] = None,
                               running: Optional[bool] = None,
                               healthy: Optional[bool] = None) -> None:
        """Update status for a component."""
        if component_name not in self.component_statuses:
            self.component_statuses[component_name] = SystemStatus(
                name=component_name,
                initialized=False,
                running=False,
                healthy=False,
                last_activity=None,
                error_count=0
            )
        
        status = self.component_statuses[component_name]
        
        if initialized is not None:
            status.initialized = initialized
        if running is not None:
            status.running = running
        if healthy is not None:
            status.healthy = healthy
        
        status.last_activity = datetime.now()
    
    def _record_error(self, component: str, error: Exception) -> None:
        """Record an error for tracking."""
        timestamp = datetime.now()
        self.error_history.append((timestamp, component, str(error)))
        
        # Trim error history
        if len(self.error_history) > self.max_error_history:
            self.error_history = self.error_history[-self.max_error_history:]
        
        # Update component error count
        if component in self.component_statuses:
            self.component_statuses[component].error_count += 1
    
    async def _cleanup_failed_initialization(self) -> None:
        """Clean up after failed initialization."""
        components = [
            self.chaos_engine,
            self.warning_system,
            self.narrative_moderator,
            self.pressure_monitor,
            self.cascade_engine
        ]
        
        for component in components:
            if component and hasattr(component, 'stop'):
                try:
                    await component.stop()
                except Exception as e:
                    print(f"Error during cleanup: {e}")
    
    # Public Interface Methods
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'manager_status': {
                'initialized': self._initialized,
                'running': self._running,
                'startup_time': self.startup_time.isoformat() if self.startup_time else None,
                'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None
            },
            'component_statuses': {
                name: {
                    'initialized': status.initialized,
                    'running': status.running,
                    'healthy': status.healthy,
                    'last_activity': status.last_activity.isoformat() if status.last_activity else None,
                    'error_count': status.error_count
                }
                for name, status in self.component_statuses.items()
            },
            'recent_errors': [
                {
                    'timestamp': timestamp.isoformat(),
                    'component': component,
                    'error': error
                }
                for timestamp, component, error in self.error_history[-10:]  # Last 10 errors
            ],
            'overall_health': self._calculate_overall_health()
        }
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health."""
        if not self._initialized:
            return 'not_initialized'
        
        if not self._running:
            return 'stopped'
        
        healthy_components = sum(1 for status in self.component_statuses.values() if status.healthy)
        total_components = len(self.component_statuses)
        
        if total_components == 0:
            return 'unknown'
        
        health_ratio = healthy_components / total_components
        
        if health_ratio >= 1.0:
            return 'healthy'
        elif health_ratio >= 0.75:
            return 'degraded'
        elif health_ratio >= 0.5:
            return 'critical'
        else:
            return 'failing'
    
    async def get_chaos_state(self, region_id: Optional[str] = None) -> Dict[str, Any]:
        """Get current chaos state through the chaos engine."""
        if not self.chaos_engine:
            return {'error': 'ChaosEngine not initialized'}
        
        return self.chaos_engine.get_chaos_state(region_id)
    
    async def get_pressure_summary(self) -> Dict[str, Any]:
        """Get pressure summary through the pressure monitor."""
        if not self.pressure_monitor:
            return {'error': 'PressureMonitor not initialized'}
        
        return self.pressure_monitor.get_pressure_summary()
    
    async def get_warning_status(self) -> Dict[str, Any]:
        """Get warning system status."""
        if not self.warning_system:
            return {'error': 'WarningSystem not initialized'}
        
        return await self.warning_system.get_all_warnings()
    
    async def get_narrative_status(self) -> Dict[str, Any]:
        """Get narrative moderator status."""
        if not self.narrative_moderator:
            return {'error': 'NarrativeModerator not initialized'}
        
        return self.narrative_moderator.get_narrative_status()
    
    async def force_trigger_event(self, event_type: str, severity: str = "moderate", 
                                 regions: Optional[List[str]] = None) -> bool:
        """Force trigger a chaos event through the chaos engine."""
        if not self.chaos_engine:
            return False
        
        return await self.chaos_engine.force_trigger_event(event_type, severity, regions)
    
    async def apply_mitigation(self, mitigation_type: str, effectiveness: float,
                              duration_hours: float, source_id: str, source_type: str,
                              description: str = "", affected_regions: Optional[List[str]] = None,
                              affected_sources: Optional[List[str]] = None) -> bool:
        """Apply mitigation through the chaos engine."""
        if not self.chaos_engine:
            return False
        
        return await self.chaos_engine.apply_mitigation(
            mitigation_type, effectiveness, duration_hours, source_id, source_type,
            description, affected_regions, affected_sources
        )
    
    async def restart_component(self, component_name: str) -> bool:
        """Restart a specific component."""
        component_map = {
            'pressure_monitor': self.pressure_monitor,
            'narrative_moderator': self.narrative_moderator,
            'warning_system': self.warning_system,
            'chaos_engine': self.chaos_engine,
            'cascade_engine': self.cascade_engine
        }
        
        component = component_map.get(component_name)
        if not component:
            print(f"Unknown component: {component_name}")
            return False
        
        try:
            print(f"Restarting {component_name}...")
            await component.stop()
            await asyncio.sleep(1)  # Brief pause
            await component.start()
            
            self._update_component_status(component_name, running=True, healthy=True)
            print(f"Component {component_name} restarted successfully")
            return True
            
        except Exception as e:
            print(f"Error restarting {component_name}: {e}")
            self._record_error(component_name, e)
            return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from all components."""
        metrics = {}
        
        components = [
            ("pressure_monitor", self.pressure_monitor),
            ("narrative_moderator", self.narrative_moderator),
            ("warning_system", self.warning_system),
            ("chaos_engine", self.chaos_engine),
            ("cascade_engine", self.cascade_engine)
        ]
        
        for name, component in components:
            if component and hasattr(component, 'metrics'):
                metrics[name] = getattr(component, 'metrics', {})
        
        return metrics
    
    async def get_llm_metrics(self) -> Dict[str, Any]:
        """Get metrics about LLM usage across all components"""
        metrics = {}
        
        if self.llm_service:
            metrics['llm_service'] = {
                'enabled': self.llm_service.enabled,
                'initialized': self.llm_service._initialized,
                'model_preference': self.llm_service.model_preference,
                'has_openai': self.llm_service.openai_client is not None,
                'has_anthropic': self.llm_service.anthropic_client is not None
            }
        
        if self.warning_system:
            metrics['warning_system'] = {
                'llm_generated_warnings': self.warning_system.metrics.get('llm_generated_warnings', 0),
                'template_fallbacks': self.warning_system.metrics.get('template_fallbacks', 0)
            }
        
        if self.cascade_engine:
            metrics['cascade_engine'] = {
                'llm_analyzed_cascades': self.cascade_engine.metrics.get('llm_analyzed_cascades', 0),
                'rule_based_cascades': self.cascade_engine.metrics.get('rule_based_cascades', 0)
            }
        
        if hasattr(self, 'mitigation_service') and self.mitigation_service:
            metrics['mitigation_service'] = {
                'llm_suggestions_generated': self.mitigation_service.llm_suggestions_generated,
                'template_suggestions_generated': self.mitigation_service.template_suggestions_generated
            }
        
        return metrics
    
    async def generate_llm_enhanced_event(self, event_type: str, severity: str, 
                                        regions: Optional[List[str]] = None,
                                        context: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Generate a chaos event with LLM-enhanced descriptions"""
        if not self.chaos_engine:
            print("Chaos engine not initialized")
            return None
        
        try:
            # Import here to avoid circular imports
            from backend.infrastructure.systems.chaos.models.chaos_events import ChaosEventType, EventSeverity, EventTemplate
            
            # Convert string parameters to enums
            try:
                chaos_event_type = ChaosEventType(event_type.lower())
                event_severity = EventSeverity(severity.lower())
            except ValueError as e:
                print(f"Invalid event type or severity: {e}")
                return None
            
            # Create a basic template for LLM enhancement
            template = EventTemplate(
                event_type=chaos_event_type,
                base_severity=event_severity,
                base_duration_hours=24.0,
                base_cooldown_hours=168.0,
                title_template=f"{severity.title()} {event_type.replace('_', ' ').title()}",
                description_template=f"A {severity} {event_type.replace('_', ' ')} event occurs",
                flavor_text_template=f"{severity.title()} {event_type.replace('_', ' ')} affects the region",
                use_llm_generation=True
            )
            
            # Set LLM service reference
            template.set_llm_service(self.llm_service)
            
            # Generate event with enhanced context
            chaos_event = template.create_event(
                chaos_score=0.5,  # Default chaos score
                affected_regions=regions,
                context=context or {}
            )
            
            return chaos_event
            
        except Exception as e:
            print(f"Error generating LLM-enhanced event: {e}")
            self._record_error("manager", e)
            return None 