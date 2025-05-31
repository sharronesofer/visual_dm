"""
Cross-System Integration - Handles integration with other game systems
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class CrossSystemIntegrator:
    """Manages integration between chaos system and other game systems"""
    
    def __init__(self):
        self.system_connections: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.pressure_collectors: Dict[str, Callable] = {}
        self.integration_health: Dict[str, bool] = {}
        
        # System integration configurations
        self.system_configs = {
            'economy': {
                'pressure_sources': ['market_volatility', 'resource_scarcity', 'trade_disruption'],
                'chaos_effects': ['market_crash', 'resource_shortage', 'trade_route_closure'],
                'health_check_interval': 300  # 5 minutes
            },
            'faction': {
                'pressure_sources': ['faction_tension', 'diplomatic_instability', 'succession_crisis'],
                'chaos_effects': ['faction_war', 'diplomatic_breakdown', 'leadership_crisis'],
                'health_check_interval': 180  # 3 minutes
            },
            'region': {
                'pressure_sources': ['population_unrest', 'infrastructure_decay', 'environmental_stress'],
                'chaos_effects': ['civil_unrest', 'infrastructure_failure', 'natural_disaster'],
                'health_check_interval': 240  # 4 minutes
            },
            'motif': {
                'pressure_sources': ['narrative_tension', 'thematic_pressure', 'story_acceleration'],
                'chaos_effects': ['narrative_twist', 'character_revelation', 'plot_acceleration'],
                'health_check_interval': 600  # 10 minutes
            }
        }
    
    async def initialize_system_connections(self):
        """Initialize connections to all integrated systems"""
        
        for system_name in self.system_configs.keys():
            try:
                await self._connect_system(system_name)
                self.integration_health[system_name] = True
                logger.info(f"Connected to {system_name} system")
                
            except Exception as e:
                logger.error(f"Failed to connect to {system_name} system: {e}")
                self.integration_health[system_name] = False
    
    async def _connect_system(self, system_name: str):
        """Connect to a specific system"""
        
        try:
            # Dynamic import of system modules
            system_module = await self._import_system_module(system_name)
            
            if system_module:
                self.system_connections[system_name] = system_module
                
                # Register pressure collector if available
                if hasattr(system_module, 'get_pressure_data'):
                    self.pressure_collectors[system_name] = system_module.get_pressure_data
                
                # Register event handlers if available
                if hasattr(system_module, 'handle_chaos_event'):
                    if system_name not in self.event_handlers:
                        self.event_handlers[system_name] = []
                    self.event_handlers[system_name].append(system_module.handle_chaos_event)
                    
        except Exception as e:
            logger.error(f"Error connecting to {system_name}: {e}")
            raise
    
    async def _import_system_module(self, system_name: str):
        """Dynamically import system module"""
        
        try:
            # Try to import the system's service module
            module_path = f"backend.systems.{system_name}.services.{system_name}_service"
            module = __import__(module_path, fromlist=[f"{system_name}_service"])
            
            # Look for service class
            service_class_name = f"{system_name.title()}Service"
            if hasattr(module, service_class_name):
                service_class = getattr(module, service_class_name)
                return service_class()
            
            return module
            
        except ImportError as e:
            logger.warning(f"Could not import {system_name} service: {e}")
            return None
    
    async def collect_all_system_pressure(self) -> Dict[str, float]:
        """Collect pressure data from all connected systems"""
        
        all_pressure = {}
        
        # Collect from each connected system
        for system_name, collector in self.pressure_collectors.items():
            try:
                pressure_data = await self._collect_system_pressure(system_name, collector)
                if pressure_data:
                    all_pressure.update(pressure_data)
                    
            except Exception as e:
                logger.error(f"Failed to collect pressure from {system_name}: {e}")
                self.integration_health[system_name] = False
        
        return all_pressure
    
    async def _collect_system_pressure(self, system_name: str, collector: Callable) -> Dict[str, float]:
        """Collect pressure data from a specific system"""
        
        try:
            # Call the system's pressure collector
            if asyncio.iscoroutinefunction(collector):
                pressure_data = await collector()
            else:
                pressure_data = collector()
            
            # Validate and normalize pressure data
            if isinstance(pressure_data, dict):
                normalized_data = {}
                for key, value in pressure_data.items():
                    if isinstance(value, (int, float)):
                        # Ensure pressure values are between 0.0 and 1.0
                        normalized_value = max(0.0, min(1.0, float(value)))
                        normalized_data[f"{system_name}_{key}"] = normalized_value
                
                return normalized_data
            
            return {}
            
        except Exception as e:
            logger.error(f"Error collecting pressure from {system_name}: {e}")
            return {}
    
    async def dispatch_chaos_event(self, event_type: str, event_data: Dict[str, Any],
                                 target_systems: List[str] = None):
        """Dispatch chaos event to target systems"""
        
        if target_systems is None:
            target_systems = list(self.event_handlers.keys())
        
        dispatch_results = {}
        
        for system_name in target_systems:
            if system_name in self.event_handlers:
                try:
                    result = await self._dispatch_to_system(system_name, event_type, event_data)
                    dispatch_results[system_name] = result
                    
                except Exception as e:
                    logger.error(f"Failed to dispatch event to {system_name}: {e}")
                    dispatch_results[system_name] = {'success': False, 'error': str(e)}
        
        return dispatch_results
    
    async def _dispatch_to_system(self, system_name: str, event_type: str, 
                                event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch event to a specific system"""
        
        handlers = self.event_handlers.get(system_name, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event_type, event_data)
                else:
                    result = handler(event_type, event_data)
                
                return {'success': True, 'result': result}
                
            except Exception as e:
                logger.error(f"Handler error in {system_name}: {e}")
                continue
        
        return {'success': False, 'error': 'No successful handlers'}
    
    async def health_check_all_systems(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all connected systems"""
        
        health_status = {}
        
        for system_name in self.system_configs.keys():
            health_status[system_name] = await self._health_check_system(system_name)
        
        return health_status
    
    async def _health_check_system(self, system_name: str) -> Dict[str, Any]:
        """Perform health check on a specific system"""
        
        status = {
            'connected': system_name in self.system_connections,
            'pressure_collector_available': system_name in self.pressure_collectors,
            'event_handlers_available': system_name in self.event_handlers,
            'last_health_check': datetime.now(),
            'integration_healthy': self.integration_health.get(system_name, False)
        }
        
        # Test pressure collection
        if system_name in self.pressure_collectors:
            try:
                test_pressure = await self._collect_system_pressure(
                    system_name, 
                    self.pressure_collectors[system_name]
                )
                status['pressure_collection_test'] = 'passed'
                status['pressure_sources_count'] = len(test_pressure)
                
            except Exception as e:
                status['pressure_collection_test'] = 'failed'
                status['pressure_collection_error'] = str(e)
        
        return status
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of all system integrations"""
        
        return {
            'total_systems': len(self.system_configs),
            'connected_systems': len(self.system_connections),
            'healthy_systems': sum(1 for healthy in self.integration_health.values() if healthy),
            'pressure_collectors': len(self.pressure_collectors),
            'event_handlers': {
                system: len(handlers) for system, handlers in self.event_handlers.items()
            },
            'system_health': self.integration_health.copy(),
            'last_updated': datetime.now()
        }
    
    async def reconnect_system(self, system_name: str) -> bool:
        """Attempt to reconnect to a system"""
        
        try:
            await self._connect_system(system_name)
            self.integration_health[system_name] = True
            logger.info(f"Successfully reconnected to {system_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reconnect to {system_name}: {e}")
            self.integration_health[system_name] = False
            return False
    
    def register_custom_handler(self, system_name: str, handler: Callable):
        """Register a custom event handler for a system"""
        
        if system_name not in self.event_handlers:
            self.event_handlers[system_name] = []
        
        self.event_handlers[system_name].append(handler)
        logger.info(f"Registered custom handler for {system_name}")
    
    def unregister_system(self, system_name: str):
        """Unregister a system from integration"""
        
        if system_name in self.system_connections:
            del self.system_connections[system_name]
        
        if system_name in self.pressure_collectors:
            del self.pressure_collectors[system_name]
        
        if system_name in self.event_handlers:
            del self.event_handlers[system_name]
        
        if system_name in self.integration_health:
            del self.integration_health[system_name]
        
        logger.info(f"Unregistered {system_name} from chaos system integration")